"""Digest JSON schema normalization and validation helpers."""
from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

ALLOWED_PAPER_SOURCES = {"openalex", "arxiv", "semantic_scholar", "nber", "ssrn"}
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_PAPER_DEFAULTS: dict[str, Any] = {
    "title": "",
    "authors": [],
    "venue": "",
    "published_date": "",
    "doi_url": "",
    "openalex_url": "",
    "cited_by_count": 0,
    "abstract": "",
    "summary_zh": "",
    "topics": [],
    "source": "unknown",
}


def _as_text(value: Any) -> str:
    return "" if value is None else str(value)


def _as_text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_as_text(v) for v in value if _as_text(v)]
    if isinstance(value, tuple):
        return [_as_text(v) for v in value if _as_text(v)]
    if isinstance(value, str) and value.strip():
        return [part.strip() for part in value.split(",") if part.strip()]
    return []


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_paper(paper: Any) -> dict[str, Any]:
    """Return a paper dictionary with stable keys and safe primitive types."""
    src = paper if isinstance(paper, dict) else {}
    normalized = dict(src) if isinstance(src, dict) else {}
    for key, default in deepcopy(_PAPER_DEFAULTS).items():
        normalized.setdefault(key, default)
    normalized["title"] = _as_text(normalized["title"])
    normalized["authors"] = _as_text_list(normalized["authors"])
    normalized["venue"] = _as_text(normalized["venue"])
    normalized["published_date"] = _as_text(normalized["published_date"])
    normalized["doi_url"] = _as_text(normalized["doi_url"])
    normalized["openalex_url"] = _as_text(normalized["openalex_url"])
    normalized["cited_by_count"] = _as_int(normalized["cited_by_count"])
    normalized["abstract"] = _as_text(normalized["abstract"])
    normalized["summary_zh"] = _as_text(normalized["summary_zh"])
    normalized["topics"] = _as_text_list(normalized["topics"])
    normalized["source"] = _as_text(normalized["source"] or "unknown")
    return normalized


def normalize_digest(data: Any) -> dict[str, Any]:
    """Normalize digest JSON into a shape Streamlit pages can safely consume."""
    src = data if isinstance(data, dict) else {}
    papers = src.get("papers", [])
    if not isinstance(papers, list):
        papers = []
    normalized_papers = [normalize_paper(p) for p in papers]

    insights = src.get("insights", {})
    if not isinstance(insights, dict):
        insights = {}

    latest_updated = src.get("latest_updated", True)
    if not isinstance(latest_updated, bool):
        latest_updated = bool(latest_updated)

    normalized = dict(src) if isinstance(src, dict) else {}
    normalized.update({
        "date": _as_text(src.get("date", "")),
        "count": _as_int(src.get("count", len(normalized_papers)), len(normalized_papers)),
        "source_used": _as_text(src.get("source_used", "")),
        "latest_updated": latest_updated,
        "overview": _as_text(src.get("overview", "")),
        "insights": insights,
        "papers": normalized_papers,
    })
    return normalized


def validate_digest(data: Any) -> tuple[bool, list[str]]:
    """Validate normalized or raw digest data and return (ok, errors)."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return False, ["digest must be an object"]

    normalized = normalize_digest(data)
    date_value = normalized["date"]
    if not date_value:
        errors.append("date is required")
    elif not _DATE_RE.match(date_value):
        errors.append(f"date must use YYYY-MM-DD format: {date_value}")

    if normalized["count"] != len(normalized["papers"]):
        errors.append(f"count ({normalized['count']}) does not match papers length ({len(normalized['papers'])})")

    for idx, paper in enumerate(normalized["papers"], 1):
        if not paper["title"].strip():
            errors.append(f"papers[{idx}].title is required")
        if paper["source"] not in ALLOWED_PAPER_SOURCES:
            errors.append(f"papers[{idx}].source is not allowed: {paper['source']}")
        if paper["cited_by_count"] < 0:
            errors.append(f"papers[{idx}].cited_by_count must be non-negative")

    return not errors, errors
