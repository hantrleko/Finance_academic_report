"""Digest pipeline orchestration."""
from __future__ import annotations

import dataclasses
import datetime as dt
import json
from pathlib import Path
from typing import Any

from .filtering import backfill_abstracts, dedupe_and_filter
from .models import DigestConfig, LLMConfig
from .rendering import render_html, render_markdown
from .sources import (
    fetch_arxiv_finance_econ_papers,
    fetch_nber_papers,
    fetch_openalex_papers,
    fetch_semantic_scholar_papers,
)
from .summarization import apply_summaries, generate_digest_insights, generate_digest_overview, llm_screen_relevance

SOURCE_PRIORITY = ["openalex", "arxiv", "semantic_scholar", "nber"]


def _load_latest_count(latest_json_path: Path) -> int:
    if not latest_json_path.exists():
        return 0
    try:
        return int(json.loads(latest_json_path.read_text(encoding="utf-8")).get("count", 0))
    except Exception:
        return 0


def _source_balanced_select(papers: list, max_items: int, source_min_items: int) -> list:
    if max_items <= 0 or not papers:
        return []
    if source_min_items <= 0:
        return papers[:max_items]

    selected: list = []
    selected_keys: set[str] = set()
    by_source: dict[str, list] = {}
    for p in papers:
        by_source.setdefault(p.source, []).append(p)

    source_order = [s for s in SOURCE_PRIORITY if s in by_source]
    source_order.extend([s for s in by_source.keys() if s not in source_order])

    # Pass 1: reserve up to source_min_items for each available source.
    for source in source_order:
        taken = 0
        for paper in by_source[source]:
            key = paper.openalex_url or f"{paper.source}:{paper.title}:{paper.published_date}"
            if key in selected_keys:
                continue
            selected.append(paper)
            selected_keys.add(key)
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

    combined = openalex_papers + arxiv_papers + s2_papers + nber_papers
    sources = []
    for name, lst in [
        ("openalex", openalex_papers),
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
    )
    papers = llm_screen_relevance(papers, analysis_cfg)
    papers = _source_balanced_select(
        papers,
        max_items=config.max_papers,
        source_min_items=config.source_min_papers,
    )
    papers = apply_summaries(papers, analysis_cfg, translate_cfg)
    overview = generate_digest_overview(papers, analysis_cfg)
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
