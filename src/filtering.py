"""Filtering and data quality helpers."""
from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from .models import CROSSREF_API_URL, VENUE_BLACKLIST, VENUE_WHITELIST, Paper


def normalize_title(text: str) -> str:
    return re.sub(r"\W+", "", text).lower()


def quality_score(paper: Paper, topic_whitelist: set[str]) -> int:
    text = " ".join([paper.title, paper.abstract, paper.venue, " ".join(paper.topics)]).lower()
    title_text = paper.title.lower()
    topic_text = " ".join(paper.topics).lower()
    venue_lower = paper.venue.lower()

    score = 0

    # 关键词匹配评分
    for keyword in topic_whitelist:
        if keyword in title_text:
            score += 3
        elif keyword in topic_text:
            score += 2
        elif keyword in text:
            score += 1

    # 无摘要扣分
    if not paper.abstract.strip():
        score -= 5

    # 期刊黑名单扣分
    if any(bl in venue_lower for bl in VENUE_BLACKLIST):
        score -= 10

    # 顶级期刊白名单加分
    if any(wl in venue_lower for wl in VENUE_WHITELIST):
        score += 5

    # DOI 存在加分
    if paper.doi_url:
        score += 1

    # 引用数加分（每 10 次引用加 1 分，上限 5 分）
    citation_bonus = min(paper.cited_by_count // 10, 5)
    score += citation_bonus

    return score


def is_relevant_openalex_paper(
    paper: Paper,
    topic_whitelist: set[str],
    topic_blacklist: set[str],
    min_quality_score: int,
) -> bool:
    text = " ".join([paper.title, paper.abstract, paper.venue, " ".join(paper.topics)]).lower()
    if any(term in text for term in topic_blacklist):
        return False

    venue_lower = paper.venue.lower()
    if any(bl in venue_lower for bl in VENUE_BLACKLIST):
        return False

    return quality_score(paper, topic_whitelist) >= min_quality_score


def dedupe_and_filter(
    papers: list[Paper],
    topic_whitelist: set[str],
    topic_blacklist: set[str],
    min_quality_score: int,
) -> list[Paper]:
    unique: list[Paper] = []
    seen_titles: set[str] = set()

    for paper in papers:
        normalized = normalize_title(paper.title)
        if normalized and normalized in seen_titles:
            continue

        if paper.source in ("openalex", "semantic_scholar") and not is_relevant_openalex_paper(
            paper,
            topic_whitelist=topic_whitelist,
            topic_blacklist=topic_blacklist,
            min_quality_score=min_quality_score,
        ):
            continue

        if normalized:
            seen_titles.add(normalized)
        unique.append(paper)

    return unique


def fetch_crossref_abstract(doi: str, mailto: str = "") -> str:
    if not doi:
        return ""
    clean_doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    url = f"{CROSSREF_API_URL}/{quote_plus(clean_doi)}"
    ua = "FinanceDigest/1.0"
    if mailto:
        ua = f"FinanceDigest/1.0 (mailto:{mailto})"
    req = Request(url, headers={"Accept": "application/json", "User-Agent": ua})
    try:
        with urlopen(req, timeout=15) as resp:
            data: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
        abstract = data.get("message", {}).get("abstract", "")
        if abstract:
            return re.sub(r"<[^>]+>", "", abstract).strip()
    except Exception:
        return ""
    return ""


def backfill_abstracts(papers: list[Paper], mailto: str = "") -> list[Paper]:
    for p in papers:
        if not p.abstract and p.doi_url:
            p.abstract = fetch_crossref_abstract(p.doi_url, mailto=mailto)
    return papers
