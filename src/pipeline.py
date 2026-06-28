"""Digest pipeline orchestration."""
from __future__ import annotations

import dataclasses
import datetime as dt
import json
from pathlib import Path
from typing import Any

from .filtering import backfill_abstracts, dedupe_and_filter, normalize_title
from .models import DigestConfig, LLMConfig
from .rendering import render_html, render_markdown
from .sources import (
    fetch_arxiv_finance_econ_papers,
    fetch_nber_papers,
    fetch_openalex_papers,
    fetch_semantic_scholar_papers,
    fetch_ssrn_papers,
)
from .summarization import apply_summaries, generate_digest_insights, generate_digest_overview, generate_template_overview, llm_screen_relevance

SOURCE_PRIORITY = ["openalex", "ssrn", "arxiv", "semantic_scholar", "nber"]


def _load_seen_titles(output_dir: Path, run_date: dt.date, lookback_days: int) -> set[str]:
    """从过去 lookback_days 天的 digest.json 中加载已出现的论文标题（归一化后），
    用于全局跨期去重，避免同一篇论文在不同日期的日报中重复出现。
    """
    seen: set[str] = set()
    for offset in range(1, lookback_days + 1):
        past_date = run_date - dt.timedelta(days=offset)
        path = output_dir / past_date.isoformat() / "digest.json"
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for p in data.get("papers", []):
                title = p.get("title", "")
                norm = normalize_title(title)
                if norm:
                    seen.add(norm)
        except Exception:
            pass
    return seen


def _cross_period_dedup(papers: list, seen_titles: set[str]) -> list:
    """过滤掉在过去几期中已经出现过的论文（全局跨期去重）。"""
    result = []
    for paper in papers:
        norm = normalize_title(paper.title)
        if norm and norm in seen_titles:
            continue
        result.append(paper)
    return result


def _load_latest_count(latest_json_path: Path) -> int:
    if not latest_json_path.exists():
        return 0
    try:
        return int(json.loads(latest_json_path.read_text(encoding="utf-8")).get("count", 0))
    except Exception:
        return 0


def _source_balanced_select(
    papers: list,
    max_items: int,
    source_min_items: int,
    source_max_share: float,
) -> list:
    if max_items <= 0 or not papers:
        return []
    if source_min_items <= 0 and source_max_share >= 1:
        return papers[:max_items]

    selected: list = []
    selected_keys: set[str] = set()
    selected_count_by_source: dict[str, int] = {}
    by_source: dict[str, list] = {}
    for p in papers:
        by_source.setdefault(p.source, []).append(p)

    source_order = [s for s in SOURCE_PRIORITY if s in by_source]
    source_order.extend([s for s in by_source.keys() if s not in source_order])
    max_per_source = max_items
    if 0 < source_max_share < 1:
        max_per_source = max(1, int(max_items * source_max_share))
        max_per_source = max(max_per_source, source_min_items)

    # Pass 1: reserve up to source_min_items for each available source.
    for source in source_order:
        taken = 0
        for paper in by_source[source]:
            key = paper.openalex_url or f"{paper.source}:{paper.title}:{paper.published_date}"
            if key in selected_keys:
                continue
            if selected_count_by_source.get(source, 0) >= max_per_source:
                continue
            selected.append(paper)
            selected_keys.add(key)
            selected_count_by_source[source] = selected_count_by_source.get(source, 0) + 1
            taken += 1
            if len(selected) >= max_items or taken >= source_min_items:
                break
        if len(selected) >= max_items:
            return selected

    # Pass 2: fill remaining slots by original ranking order.
    for paper in papers:
        key = paper.openalex_url or f"{paper.source}:{paper.title}:{paper.published_date}"
        if key in selected_keys:
            continue
        if selected_count_by_source.get(paper.source, 0) >= max_per_source:
            continue
        selected.append(paper)
        selected_keys.add(key)
        selected_count_by_source[paper.source] = selected_count_by_source.get(paper.source, 0) + 1
        if len(selected) >= max_items:
            break
    if len(selected) >= max_items:
        return selected

    # Pass 3: if strict cap blocks filling, relax cap to avoid under-filled digest.
    for paper in papers:
        key = paper.openalex_url or f"{paper.source}:{paper.title}:{paper.published_date}"
        if key in selected_keys:
            continue
        selected.append(paper)
        selected_keys.add(key)
        if len(selected) >= max_items:
            break
    return selected


def build_digest(
    config: DigestConfig,
    translate_cfg: LLMConfig,
    analysis_cfg: LLMConfig,
    run_date: dt.date | None = None,
) -> dict[str, Any]:
    run_date = run_date or dt.date.today()
    date_from = run_date - dt.timedelta(days=config.lookback_days)

    print(f"[FETCH] Fetching from all sources (lookback={config.lookback_days}d)...")
    openalex_papers = fetch_openalex_papers(date_from, run_date, mailto=config.openalex_mailto, per_page=15)
    arxiv_papers = fetch_arxiv_finance_econ_papers(date_from, run_date, max_results=15)
    s2_papers = fetch_semantic_scholar_papers(
        date_from,
        run_date,
        mailto=config.openalex_mailto,
        max_results=15,
        api_key=config.s2_api_key,
        min_interval_seconds=config.s2_min_interval_seconds,
    )
    nber_papers = fetch_nber_papers(date_from, max_results=5)
    ssrn_papers = fetch_ssrn_papers(date_from, run_date, mailto=config.openalex_mailto, per_page=15)

    combined = openalex_papers + ssrn_papers + arxiv_papers + s2_papers + nber_papers
    sources = []
    for name, lst in [
        ("openalex", openalex_papers),
        ("ssrn", ssrn_papers),
        ("arxiv", arxiv_papers),
        ("semantic_scholar", s2_papers),
        ("nber", nber_papers),
    ]:
        if lst:
            sources.append(f"{name}({len(lst)})")
    source_used = "+".join(sources) if sources else "none"
    print(f"[FETCH] Total: {len(combined)} papers from {source_used}")

    papers = [p for p in combined if p.source in ("arxiv", "semantic_scholar", "nber") or p.cited_by_count >= config.min_citations]
    papers = backfill_abstracts(papers, mailto=config.openalex_mailto)

    # 全局跨期去重：过滤过去 lookback_days 天已出现过的论文
    seen_titles = _load_seen_titles(config.output_dir, run_date, config.lookback_days)
    before_dedup = len(papers)
    papers = _cross_period_dedup(papers, seen_titles)
    deduped_count = before_dedup - len(papers)
    if deduped_count > 0:
        print(f"[DEDUP] Removed {deduped_count} cross-period duplicate(s) (seen in past {config.lookback_days}d).")

    papers = dedupe_and_filter(
        papers,
        topic_whitelist=config.topic_whitelist,
        topic_blacklist=config.topic_blacklist,
        min_quality_score=config.min_quality_score,
    )

    papers = _source_balanced_select(
        papers,
        max_items=config.max_papers * 3,
        source_min_items=config.source_min_papers,
        source_max_share=config.source_max_share,
    )
    papers = llm_screen_relevance(papers, analysis_cfg)
    papers = _source_balanced_select(
        papers,
        max_items=config.max_papers,
        source_min_items=config.source_min_papers,
        source_max_share=config.source_max_share,
    )
    papers = apply_summaries(papers, analysis_cfg, translate_cfg)
    overview = generate_digest_overview(papers, analysis_cfg)
    if not overview:
        overview = generate_template_overview(papers)
    insights = generate_digest_insights(papers, analysis_cfg)

    config.output_dir.mkdir(parents=True, exist_ok=True)
    daily_dir = config.output_dir / run_date.isoformat()
    daily_dir.mkdir(parents=True, exist_ok=True)

    latest_json_path = config.output_dir / "latest" / "digest.json"
    latest_count = _load_latest_count(latest_json_path)
    skip_latest_update = config.keep_latest_when_empty and len(papers) == 0 and latest_count > 0
    note = "今日抓取结果为空，已保留上一期 latest 内容，避免覆盖有效日报。" if skip_latest_update else ""

    metadata = {
        "date": run_date.isoformat(),
        "count": len(papers),
        "source_used": source_used,
        "latest_updated": not skip_latest_update,
        "overview": overview,
        "insights": insights,
        "papers": [dataclasses.asdict(p) for p in papers],
    }

    json_path = daily_dir / "digest.json"
    md_path = daily_dir / "digest.md"
    html_path = daily_dir / "index.html"

    json_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(
        render_markdown(run_date.isoformat(), papers, note=note, overview=overview, insights=insights),
        encoding="utf-8",
    )
    html_path.write_text(
        render_html(run_date.isoformat(), papers, note=note, overview=overview, insights=insights),
        encoding="utf-8",
    )

    latest_updated = False
    latest_dir = config.output_dir / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)
    if not skip_latest_update:
        (latest_dir / "digest.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        (latest_dir / "digest.md").write_text(
            render_markdown(run_date.isoformat(), papers, overview=overview, insights=insights),
            encoding="utf-8",
        )
        (latest_dir / "index.html").write_text(
            render_html(run_date.isoformat(), papers, overview=overview, insights=insights),
            encoding="utf-8",
        )
        latest_updated = True

    if len(papers) == 0:
        alerts_dir = config.output_dir / "alerts"
        alerts_dir.mkdir(parents=True, exist_ok=True)
        alert = {
            "date": run_date.isoformat(),
            "level": "warning",
            "message": "No papers fetched for this run. latest preserved if previous digest exists.",
            "source_used": source_used,
        }
        (alerts_dir / f"{run_date.isoformat()}.json").write_text(json.dumps(alert, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "json": json_path,
        "markdown": md_path,
        "html": html_path,
        "count": len(papers),
        "latest_updated": latest_updated,
        "source_used": source_used,
    }
