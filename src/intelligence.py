"""Deterministic research-intelligence helpers for digest content innovation.

The functions in this module intentionally avoid network/LLM calls so they can
be used in Streamlit pages, tests, and scheduled workflows without extra cost.
They turn existing digest metadata into higher-level reading guidance: topic
radar, method signals, source-diversity notes, and recommended reading paths.
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from datetime import date, datetime
from typing import Any, Iterable

from .models import VENUE_WHITELIST

SOURCE_LABELS = {
    "arxiv": "arXiv",
    "openalex": "OpenAlex",
    "semantic_scholar": "Semantic Scholar",
    "nber": "NBER",
    "ssrn": "SSRN",
}

METHOD_TAXONOMY: dict[str, tuple[str, ...]] = {
    "因果识别": (
        "causal", "identification", "instrument", "iv ", "difference-in-differences",
        "diff-in-diff", "did", "regression discontinuity", "rd design", "natural experiment",
    ),
    "机器学习/AI": (
        "machine learning", "deep learning", "artificial intelligence", "neural",
        "transformer", "llm", "large language model", "random forest", "xgboost",
    ),
    "结构模型": ("structural", "equilibrium", "dynamic model", "dsge", "calibration"),
    "文本/情绪分析": ("text", "sentiment", "nlp", "news", "disclosure", "tone"),
    "实验/调查": ("experiment", "randomized", "rct", "survey", "field experiment"),
    "资产定价/实证金融": ("asset pricing", "factor", "portfolio", "return predictability", "anomaly"),
}

DOMAIN_TAXONOMY: dict[str, tuple[str, ...]] = {
    "货币政策与通胀": ("monetary", "inflation", "central bank", "interest rate", "fed", "ecb"),
    "银行与金融中介": ("bank", "lending", "credit", "financial intermediary", "deposit"),
    "资产定价与投资": ("asset pricing", "portfolio", "factor", "stock", "bond", "return"),
    "企业金融与治理": ("corporate", "governance", "firm", "investment", "capital structure"),
    "宏观金融风险": ("macro", "recession", "systemic", "risk", "financial stability", "crisis"),
    "可持续金融": ("climate", "carbon", "green", "esg", "sustainable"),
    "金融科技与数据": ("fintech", "crypto", "blockchain", "digital", "payment", "data"),
}

_STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "into", "using", "use", "new",
    "paper", "papers", "study", "studies", "analysis", "evidence", "effect", "effects",
    "model", "models", "data", "based", "between", "through", "over", "under", "across",
    "finance", "financial", "economic", "economics", "market", "markets", "journal",
}
_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z\-]{2,}")


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def _paper_text(paper: dict[str, Any]) -> str:
    parts = [
        paper.get("title", ""),
        paper.get("abstract", ""),
        paper.get("summary_zh", ""),
        paper.get("venue", ""),
        " ".join(paper.get("topics") or []),
    ]
    return " ".join(_text(part) for part in parts).lower()


def _parse_year(value: Any) -> int | None:
    match = re.search(r"(19|20)\d{2}", _text(value))
    return int(match.group(0)) if match else None


def is_top_tier_venue(venue: Any) -> bool:
    """Return True when a venue matches the configured top-tier whitelist."""
    venue_lower = _text(venue).lower()
    return any(item in venue_lower for item in VENUE_WHITELIST)


def citation_bucket(citations: Any) -> str:
    """Translate a citation count into a reader-friendly impact bucket."""
    try:
        count = int(citations)
    except (TypeError, ValueError):
        count = 0
    if count >= 500:
        return "经典高引"
    if count >= 100:
        return "高影响"
    if count >= 20:
        return "已有关注"
    if count > 0:
        return "早期引用"
    return "新近/待观察"


def paper_attention_score(paper: dict[str, Any], reference_year: int | None = None) -> float:
    """Score a paper for UI ranking without relying on external services.

    The score combines citation momentum, top-tier venue signal, source freshness,
    topic richness, and recency. It is not a quality judgment; it is a deterministic
    attention heuristic for browsing large digest archives.
    """
    try:
        citations = max(int(paper.get("cited_by_count", 0) or 0), 0)
    except (TypeError, ValueError):
        citations = 0

    score = math.log1p(citations) * 12
    if is_top_tier_venue(paper.get("venue")):
        score += 18
    if paper.get("source") in {"nber", "ssrn", "arxiv"}:
        score += 6
    if paper.get("summary_zh"):
        score += 4
    score += min(len(paper.get("topics") or []), 5) * 1.5

    year = _parse_year(paper.get("published_date"))
    ref_year = reference_year or date.today().year
    if year:
        age = max(ref_year - year, 0)
        score += max(0, 10 - age * 2)

    return round(score, 1)


def extract_topic_terms(papers: Iterable[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    """Extract normalized topic terms from paper topics and titles."""
    counter: Counter[str] = Counter()
    examples: dict[str, str] = {}
    for paper in papers:
        title = _text(paper.get("title", ""))
        for topic in paper.get("topics") or []:
            term = _text(topic).strip().lower()
            if term:
                counter[term] += 3
                examples.setdefault(term, title)
        for word in _WORD_RE.findall(title.lower()):
            word = word.strip("-")
            if word not in _STOPWORDS and len(word) >= 4:
                counter[word] += 1
                examples.setdefault(word, title)

    return [
        {"term": term, "score": score, "example": examples.get(term, "")}
        for term, score in counter.most_common(limit)
    ]


def classify_taxonomy(papers: Iterable[dict[str, Any]], taxonomy: dict[str, tuple[str, ...]]) -> list[dict[str, Any]]:
    """Count papers matching a keyword taxonomy."""
    counts: dict[str, int] = defaultdict(int)
    examples: dict[str, str] = {}
    for paper in papers:
        text = _paper_text(paper)
        for label, keywords in taxonomy.items():
            if any(keyword in text for keyword in keywords):
                counts[label] += 1
                examples.setdefault(label, _text(paper.get("title", "")))

    return [
        {"label": label, "count": count, "example": examples.get(label, "")}
        for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def source_mix(papers: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return source counts with display labels."""
    counter = Counter(_text(p.get("source", "unknown")) or "unknown" for p in papers)
    total = sum(counter.values()) or 1
    return [
        {
            "source": source,
            "label": SOURCE_LABELS.get(source, source),
            "count": count,
            "share": round(count / total * 100, 1),
        }
        for source, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def recommended_reading_path(papers: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    """Build a concise reading path with distinct reasons."""
    if not papers:
        return []

    reference_years = [_parse_year(p.get("published_date")) for p in papers]
    reference_year = max((year for year in reference_years if year), default=date.today().year)

    candidates: list[tuple[str, dict[str, Any], str]] = []
    by_score = sorted(papers, key=lambda p: paper_attention_score(p, reference_year), reverse=True)
    if by_score:
        p = by_score[0]
        candidates.append(("先读：高信息密度", p, f"综合关注度 {paper_attention_score(p, reference_year)}，{citation_bucket(p.get('cited_by_count'))}"))

    frontier = [p for p in papers if p.get("source") in {"arxiv", "ssrn", "nber"}]
    if frontier:
        p = sorted(frontier, key=lambda item: paper_attention_score(item, reference_year), reverse=True)[0]
        candidates.append(("前沿：新问题/工作论文", p, f"来自 {SOURCE_LABELS.get(p.get('source'), p.get('source'))}，适合追踪最新议题"))

    top_tier = [p for p in papers if is_top_tier_venue(p.get("venue"))]
    if top_tier:
        p = sorted(top_tier, key=lambda item: item.get("cited_by_count", 0) or 0, reverse=True)[0]
        candidates.append(("经典：顶刊/高可信基准", p, "命中顶级期刊白名单，可作为文献综述锚点"))

    method_papers = [p for p in papers if classify_taxonomy([p], METHOD_TAXONOMY)]
    if method_papers:
        p = sorted(method_papers, key=lambda item: paper_attention_score(item, reference_year), reverse=True)[0]
        method = classify_taxonomy([p], METHOD_TAXONOMY)[0]["label"]
        candidates.append(("方法：可复用识别/建模", p, f"检测到方法信号：{method}"))

    policy_papers = [p for p in papers if classify_taxonomy([p], DOMAIN_TAXONOMY)]
    if policy_papers:
        p = sorted(policy_papers, key=lambda item: paper_attention_score(item, reference_year), reverse=True)[0]
        domain = classify_taxonomy([p], DOMAIN_TAXONOMY)[0]["label"]
        candidates.append(("应用：政策/市场含义", p, f"关联领域：{domain}"))

    seen_titles: set[str] = set()
    path: list[dict[str, Any]] = []
    for role, paper, reason in candidates:
        title = _text(paper.get("title", ""))
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)
        path.append({
            "role": role,
            "title": title,
            "source": _text(paper.get("source", "unknown")),
            "source_label": SOURCE_LABELS.get(_text(paper.get("source", "unknown")), _text(paper.get("source", "unknown"))),
            "venue": _text(paper.get("venue", "")),
            "reason": reason,
            "attention_score": paper_attention_score(paper, reference_year),
            "doi_url": _text(paper.get("doi_url", "")),
            "openalex_url": _text(paper.get("openalex_url", "")),
        })
        if len(path) >= limit:
            break
    return path


def build_digest_brief(digest: dict[str, Any]) -> dict[str, Any]:
    """Build single-issue intelligence for daily/history pages."""
    papers = digest.get("papers", []) if isinstance(digest, dict) else []
    if not isinstance(papers, list):
        papers = []

    citations = [int(p.get("cited_by_count", 0) or 0) for p in papers if isinstance(p, dict)]
    top_tier_count = sum(1 for p in papers if isinstance(p, dict) and is_top_tier_venue(p.get("venue")))
    topic_terms = extract_topic_terms([p for p in papers if isinstance(p, dict)], limit=8)
    method_signals = classify_taxonomy([p for p in papers if isinstance(p, dict)], METHOD_TAXONOMY)
    domain_signals = classify_taxonomy([p for p in papers if isinstance(p, dict)], DOMAIN_TAXONOMY)

    lead_terms = [item["term"] for item in topic_terms[:3]]
    if lead_terms:
        narrative = "本期主要围绕 " + "、".join(lead_terms) + " 展开。"
    else:
        narrative = "本期主题信号较分散，建议结合来源与引用指标筛选阅读。"
    if method_signals:
        narrative += " 方法上可重点关注 " + "、".join(item["label"] for item in method_signals[:2]) + "。"
    if top_tier_count:
        narrative += f" 其中 {top_tier_count} 篇命中顶级期刊/高质量来源。"

    return {
        "date": digest.get("date", "") if isinstance(digest, dict) else "",
        "paper_count": len(papers),
        "avg_citations": round(sum(citations) / len(citations), 1) if citations else 0,
        "top_tier_count": top_tier_count,
        "source_mix": source_mix([p for p in papers if isinstance(p, dict)]),
        "topic_terms": topic_terms,
        "method_signals": method_signals,
        "domain_signals": domain_signals,
        "reading_path": recommended_reading_path([p for p in papers if isinstance(p, dict)]),
        "narrative": narrative,
    }


def _parse_digest_date(digest: dict[str, Any]) -> datetime:
    try:
        return datetime.strptime(_text(digest.get("date", "")), "%Y-%m-%d")
    except ValueError:
        return datetime.min


def build_research_radar(digests: list[dict[str, Any]], recent_issues: int = 14, baseline_issues: int = 45) -> dict[str, Any]:
    """Build cross-issue research radar from historical digests."""
    valid = [d for d in digests if isinstance(d, dict)]
    valid = sorted(valid, key=_parse_digest_date, reverse=True)
    recent = valid[:recent_issues]
    baseline = valid[recent_issues:recent_issues + baseline_issues]

    recent_papers = [p for d in recent for p in d.get("papers", []) if isinstance(p, dict)]
    baseline_papers = [p for d in baseline for p in d.get("papers", []) if isinstance(p, dict)]

    recent_topics = Counter({item["term"]: item["score"] for item in extract_topic_terms(recent_papers, limit=100)})
    baseline_topics = Counter({item["term"]: item["score"] for item in extract_topic_terms(baseline_papers, limit=100)})
    recent_total = sum(recent_topics.values()) or 1
    baseline_total = sum(baseline_topics.values()) or 1

    emerging: list[dict[str, Any]] = []
    for term, score in recent_topics.items():
        recent_share = score / recent_total
        baseline_share = baseline_topics.get(term, 0) / baseline_total
        lift = recent_share - baseline_share
        if score >= 2 and lift > 0:
            emerging.append({
                "term": term,
                "recent_score": score,
                "baseline_score": baseline_topics.get(term, 0),
                "lift": round(lift * 100, 2),
            })
    emerging = sorted(emerging, key=lambda item: (-item["lift"], -item["recent_score"], item["term"]))[:12]

    reference_year = max((_parse_year(p.get("published_date")) for p in recent_papers if _parse_year(p.get("published_date"))), default=date.today().year)
    notable = sorted(
        recent_papers,
        key=lambda p: paper_attention_score(p, reference_year),
        reverse=True,
    )[:10]

    return {
        "issue_count": len(valid),
        "recent_issue_count": len(recent),
        "baseline_issue_count": len(baseline),
        "recent_paper_count": len(recent_papers),
        "baseline_paper_count": len(baseline_papers),
        "latest_date": valid[0].get("date", "") if valid else "",
        "earliest_recent_date": recent[-1].get("date", "") if recent else "",
        "emerging_topics": emerging,
        "recent_source_mix": source_mix(recent_papers),
        "method_signals": classify_taxonomy(recent_papers, METHOD_TAXONOMY),
        "domain_signals": classify_taxonomy(recent_papers, DOMAIN_TAXONOMY),
        "notable_papers": [
            {
                "title": _text(p.get("title", "")),
                "source": _text(p.get("source", "unknown")),
                "source_label": SOURCE_LABELS.get(_text(p.get("source", "unknown")), _text(p.get("source", "unknown"))),
                "venue": _text(p.get("venue", "")),
                "published_date": _text(p.get("published_date", "")),
                "cited_by_count": int(p.get("cited_by_count", 0) or 0),
                "attention_score": paper_attention_score(p, reference_year),
                "doi_url": _text(p.get("doi_url", "")),
                "openalex_url": _text(p.get("openalex_url", "")),
            }
            for p in notable
        ],
    }


def radar_to_markdown(radar: dict[str, Any]) -> str:
    """Render research radar as portable Markdown."""
    lines = [
        f"# 研究雷达 — {radar.get('latest_date', 'N/A')}",
        "",
        f"- 覆盖期数：{radar.get('issue_count', 0)}",
        f"- 近期窗口：{radar.get('recent_issue_count', 0)} 期 / {radar.get('recent_paper_count', 0)} 篇",
        f"- 基准窗口：{radar.get('baseline_issue_count', 0)} 期 / {radar.get('baseline_paper_count', 0)} 篇",
        "",
        "## 上升主题",
    ]
    for item in radar.get("emerging_topics", []):
        lines.append(f"- {item['term']}：近期分数 {item['recent_score']}，较基准提升 {item['lift']}pp")
    lines.extend(["", "## 方法信号"])
    for item in radar.get("method_signals", []):
        lines.append(f"- {item['label']}：{item['count']} 篇")
    lines.extend(["", "## 推荐关注论文"])
    for idx, paper in enumerate(radar.get("notable_papers", []), 1):
        lines.append(f"{idx}. {paper['title']} — {paper['source_label']}，关注度 {paper['attention_score']}")
    return "\n".join(lines) + "\n"
