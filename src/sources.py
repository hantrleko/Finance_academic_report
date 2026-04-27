"""Paper source fetchers."""
from __future__ import annotations

import datetime as dt
import json
import re
import time
import xml.etree.ElementTree as ET
from html import unescape
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

from .models import (
    ARXIV_API_URL,
    CONCEPT_ECONOMICS,
    CONCEPT_FINANCE,
    NBER_RSS_URL,
    OPENALEX_URL,
    S2_API_URL,
    Paper,
)

S2_MAX_RETRIES = 3
S2_BASE_BACKOFF_SECONDS = 2
_last_s2_request_ts = 0.0


def _sanitize_xml_text(xml_text: str) -> str:
    # Remove invalid control characters for XML 1.0 and escape bare ampersands.
    sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", xml_text)
    sanitized = re.sub(r"&(?!#?\w+;)", "&amp;", sanitized)
    return sanitized


def _parse_xml_with_recovery(xml_text: str) -> ET.Element | None:
    try:
        return ET.fromstring(xml_text)
    except ET.ParseError as first_error:
        recovered = _sanitize_xml_text(xml_text)
        try:
            return ET.fromstring(recovered)
        except ET.ParseError as second_error:
            print(f"[NBER] XML parse error: {first_error}")
            print(f"[NBER] XML recovery failed: {second_error}")
            return None


def _retry_after_seconds(err: HTTPError, attempt: int) -> int:
    retry_after = err.headers.get("Retry-After") if err.headers else None
    if retry_after and retry_after.isdigit():
        return max(1, int(retry_after))
    return S2_BASE_BACKOFF_SECONDS * (2 ** attempt)


def _respect_s2_rate_limit(min_interval_seconds: float) -> None:
    global _last_s2_request_ts
    now = time.time()
    wait = min_interval_seconds - (now - _last_s2_request_ts)
    if wait > 0:
        time.sleep(wait)
    _last_s2_request_ts = time.time()


def _request_s2(
    params: dict[str, Any],
    headers: dict[str, str],
    min_interval_seconds: float,
) -> list[dict[str, Any]] | None:
    req = Request(f"{S2_API_URL}?{urlencode(params)}", headers=headers)
    for attempt in range(S2_MAX_RETRIES):
        _respect_s2_rate_limit(min_interval_seconds)
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8")).get("data", [])
        except HTTPError as e:
            if e.code == 429 and attempt < S2_MAX_RETRIES - 1:
                wait_seconds = _retry_after_seconds(e, attempt)
                print(f"[S2] Rate limited (429), retrying in {wait_seconds}s...")
                time.sleep(wait_seconds)
                continue
            print(f"[S2] Fetch error: HTTP {e.code}")
            return None
        except (URLError, Exception) as e:
            print(f"[S2] Fetch error: {type(e).__name__}: {e}")
            return None
    return None


def _extract_xml_tag_text(block: str, tag: str) -> str:
    match = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", block, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    text = re.sub(r"<[^>]+>", "", match.group(1))
    return unescape(text).strip()


def _parse_pub_date(pub_date_str: str, date_from: dt.date) -> str:
    if not pub_date_str:
        return ""
    try:
        parsed = dt.datetime.strptime(pub_date_str[:16].strip().rstrip(","), "%a, %d %b %Y")
        if parsed.date() < date_from:
            return ""
        return parsed.date().isoformat()
    except ValueError:
        return pub_date_str[:10]


def _extract_nber_authors_from_title(title: str) -> tuple[str, list[str]]:
    """从 NBER 标题中提取作者（格式：'Paper Title -- by Author A, Author B'），
    返回清洗后的标题和作者列表。"""
    match = re.search(r"\s+--\s+by\s+(.+)$", title, re.IGNORECASE)
    if match:
        authors_str = match.group(1).strip()
        clean_title = title[: match.start()].strip()
        # 按逗号或分号分割，过滤空字符串
        authors = [a.strip() for a in re.split(r"[,;]", authors_str) if a.strip()]
        return clean_title, authors
    return title, []


def _parse_nber_items_fallback(xml_text: str, date_from: dt.date, max_results: int) -> list[Paper]:
    print("[NBER] Falling back to regex parser")
    papers: list[Paper] = []
    for block in re.findall(r"<item\b[^>]*>.*?</item>", xml_text, flags=re.IGNORECASE | re.DOTALL):
        if len(papers) >= max_results:
            break
        raw_title = _extract_xml_tag_text(block, "title")
        if not raw_title:
            continue
        clean_title, authors = _extract_nber_authors_from_title(raw_title)
        link = _extract_xml_tag_text(block, "link")
        description = _extract_xml_tag_text(block, "description")
        pub_date_str = _extract_xml_tag_text(block, "pubDate")
        pub_date = _parse_pub_date(pub_date_str, date_from)
        # 日期解析失败时回退到今日日期，而非丢弃该条目
        if pub_date_str and not pub_date:
            pub_date = date_from.isoformat()
        papers.append(
            Paper(
                title=clean_title,
                authors=authors,
                venue="NBER Working Papers",
                published_date=pub_date,
                doi_url="",
                openalex_url=link,
                cited_by_count=0,
                abstract=description,
                summary_zh="",
                topics=["Economics", "Finance"],
                source="nber",
            )
        )
    return papers


def extract_abstract(indexed_abstract: dict[str, Any] | None) -> str:
    if not indexed_abstract:
        return ""
    inverted = indexed_abstract.get("InvertedIndex", {})
    if not inverted:
        return ""

    max_pos = -1
    words: list[str | None] = []
    for word, positions in inverted.items():
        for pos in positions:
            if pos > max_pos:
                max_pos = pos
                words.extend([None] * (max_pos - len(words) + 1))
            words[pos] = word
    return " ".join([w for w in words if w])


def topic_names(concepts: list[dict[str, Any]]) -> list[str]:
    return [c.get("display_name") for c in concepts[:5] if c.get("display_name")]


def fetch_openalex_papers(date_from: dt.date, date_to: dt.date, mailto: str, per_page: int = 50) -> list[Paper]:
    filters = [
        f"from_publication_date:{date_from.isoformat()}",
        f"to_publication_date:{date_to.isoformat()}",
        f"concepts.id:{CONCEPT_ECONOMICS}|{CONCEPT_FINANCE}",
        "type:article",
        "has_abstract:true",
    ]
    params = {
        "filter": ",".join(filters),
        "sort": "publication_date:desc",
        "per-page": per_page,
    }
    if mailto:
        params["mailto"] = mailto

    try:
        with urlopen(f"{OPENALEX_URL}?{urlencode(params)}", timeout=30) as response:
            data = json.loads(response.read().decode("utf-8")).get("results", [])
    except URLError:
        return []

    papers: list[Paper] = []
    for item in data:
        doi = item.get("doi") or ""
        primary_location = item.get("primary_location") or {}
        if not isinstance(primary_location, dict):
            primary_location = {}
        source = primary_location.get("source") or {}
        if not isinstance(source, dict):
            source = {}

        authorships = item.get("authorships") or []
        if not isinstance(authorships, list):
            authorships = []

        papers.append(
            Paper(
                title=item.get("title") or "Untitled",
                authors=[
                    a.get("author", {}).get("display_name", "")
                    for a in authorships[:5]
                    if isinstance(a, dict) and a.get("author", {}).get("display_name")
                ],
                venue=unescape(source.get("display_name") or "Unknown"),
                published_date=item.get("publication_date") or "",
                doi_url=doi if doi.startswith("http") else (f"https://doi.org/{doi}" if doi else ""),
                openalex_url=item.get("id", ""),
                cited_by_count=item.get("cited_by_count", 0),
                abstract=extract_abstract(item.get("abstract_inverted_index")),
                summary_zh="",
                topics=topic_names(item.get("concepts", [])),
                source="openalex",
            )
        )
    return papers


def fetch_arxiv_finance_econ_papers(date_from: dt.date, date_to: dt.date | None = None, max_results: int = 50) -> list[Paper]:
    date_to = date_to or date_from
    query = quote_plus("cat:q-fin.* OR cat:econ.*")
    params = f"search_query={query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    try:
        with urlopen(f"{ARXIV_API_URL}?{params}", timeout=30) as response:
            xml_text = response.read().decode("utf-8")
    except URLError:
        return []

    root = ET.fromstring(xml_text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    papers: list[Paper] = []
    for entry in root.findall("atom:entry", ns):
        published = (entry.findtext("atom:published", default="", namespaces=ns) or "")[:10]
        try:
            pub_date = dt.date.fromisoformat(published)
        except ValueError:
            continue
        if pub_date < date_from or pub_date > date_to:
            continue
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip().replace("\n", " ")
        abstract = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip().replace("\n", " ")
        authors = [
            author.findtext("atom:name", default="", namespaces=ns) or ""
            for author in entry.findall("atom:author", ns)
        ]
        papers.append(
            Paper(
                title=title or "Untitled",
                authors=[a for a in authors if a][:5],
                venue="arXiv",
                published_date=published,
                doi_url="",
                openalex_url=entry.findtext("atom:id", default="", namespaces=ns) or "",
                cited_by_count=0,
                abstract=abstract,
                summary_zh="",
                topics=["Economics", "Finance"],
                source="arxiv",
            )
        )
    return papers


def fetch_semantic_scholar_papers(
    date_from: dt.date,
    date_to: dt.date,
    mailto: str = "",
    max_results: int = 15,
    api_key: str = "",
    min_interval_seconds: float = 1.1,
) -> list[Paper]:
    fields = "title,authors,abstract,venue,year,externalIds,citationCount,publicationDate,s2FieldsOfStudy"
    params = {
        "query": "finance economics",
        "fields": fields,
        "limit": max_results,
        "publicationDateOrYear": f"{date_from.isoformat()}:{date_to.isoformat()}",
        "fieldsOfStudy": "Economics",
    }
    headers = {"User-Agent": "FinanceDigest/1.0"}
    if mailto:
        headers["User-Agent"] = f"FinanceDigest/1.0 (mailto:{mailto})"
    if api_key:
        headers["x-api-key"] = api_key
    data = _request_s2(params, headers, min_interval_seconds=min_interval_seconds)
    if data is None:
        return []
    if not data:
        fallback_params = {
            "query": "finance economics",
            "fields": fields,
            "limit": max_results,
            "fieldsOfStudy": "Economics",
        }
        print("[S2] No results with date filter, retrying without date filter")
        data = _request_s2(fallback_params, headers, min_interval_seconds=min_interval_seconds)
        if data is None:
            return []

    papers: list[Paper] = []
    for item in data:
        if not item:
            continue
        external_ids = item.get("externalIds") or {}
        doi = external_ids.get("DOI", "")
        s2_fields = item.get("s2FieldsOfStudy") or []
        topics = [f.get("category", "") for f in s2_fields if f.get("category")][:5]
        authors_raw = item.get("authors") or []
        papers.append(
            Paper(
                title=item.get("title") or "Untitled",
                authors=[a.get("name", "") for a in authors_raw[:5] if a.get("name")],
                venue=unescape(item.get("venue") or "Unknown"),
                published_date=item.get("publicationDate") or "",
                doi_url=f"https://doi.org/{doi}" if doi else "",
                openalex_url=f"https://api.semanticscholar.org/CorpusID:{external_ids.get('CorpusId', '')}" if external_ids.get("CorpusId") else "",
                cited_by_count=item.get("citationCount") or 0,
                abstract=(item.get("abstract") or "").strip(),
                summary_zh="",
                topics=topics or ["Economics", "Finance"],
                source="semantic_scholar",
            )
        )
    print(f"[S2] Fetched {len(papers)} papers")
    return papers


def fetch_nber_papers(date_from: dt.date, max_results: int = 5) -> list[Paper]:
    req = Request(NBER_RSS_URL, headers={"User-Agent": "FinanceDigest/1.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            xml_text = resp.read().decode("utf-8")
    except (URLError, Exception) as e:
        print(f"[NBER] Fetch error: {type(e).__name__}: {e}")
        return []

    root = _parse_xml_with_recovery(xml_text)
    if root is None:
        return _parse_nber_items_fallback(xml_text, date_from, max_results)

    papers: list[Paper] = []
    channel = root.find("channel")
    if channel is None:
        print("[NBER] No channel found in RSS")
        return []

    for item in channel.findall("item"):
        if len(papers) >= max_results:
            break

        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        pub_date_str = (item.findtext("pubDate") or "").strip()

        pub_date = _parse_pub_date(pub_date_str, date_from)
        # 日期解析失败时回退到 date_from，而非丢弃该条目
        if pub_date_str and not pub_date:
            pub_date = date_from.isoformat()

        abstract = re.sub(r"<[^>]+>", "", description).strip()
        if not title:
            continue
        clean_title, authors = _extract_nber_authors_from_title(title)
        papers.append(
            Paper(
                title=clean_title,
                authors=authors,
                venue="NBER Working Papers",
                published_date=pub_date,
                doi_url="",
                openalex_url=link,
                cited_by_count=0,
                abstract=abstract,
                summary_zh="",
                topics=["Economics", "Finance"],
                source="nber",
            )
        )
    print(f"[NBER] Fetched {len(papers)} papers")
    return papers
