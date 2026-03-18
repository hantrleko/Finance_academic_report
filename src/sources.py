"""Paper source fetchers."""
from __future__ import annotations

import datetime as dt
import json
import re
import xml.etree.ElementTree as ET
from typing import Any
from urllib.error import URLError
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
                venue=source.get("display_name") or "Unknown",
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


def fetch_semantic_scholar_papers(date_from: dt.date, date_to: dt.date, mailto: str, max_results: int = 15) -> list[Paper]:
    fields = "title,authors,abstract,venue,year,externalIds,citationCount,publicationDate,s2FieldsOfStudy"
    params = urlencode({
        "query": "finance economics",
        "fields": fields,
        "limit": max_results,
        "publicationDateOrYear": f"{date_from.isoformat()}:{date_to.isoformat()}",
        "fieldsOfStudy": "Economics",
    })
    headers = {"User-Agent": "FinanceDigest/1.0"}
    if mailto:
        headers["User-Agent"] = f"FinanceDigest/1.0 (mailto:{mailto})"
    req = Request(f"{S2_API_URL}?{params}", headers=headers)
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8")).get("data", [])
    except (URLError, Exception) as e:
        print(f"[S2] Fetch error: {type(e).__name__}: {e}")
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
                venue=item.get("venue") or "Unknown",
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

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"[NBER] XML parse error: {e}")
        return []

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

        pub_date = ""
        if pub_date_str:
            try:
                parsed = dt.datetime.strptime(pub_date_str[:16].strip().rstrip(","), "%a, %d %b %Y")
                if parsed.date() < date_from:
                    continue
                pub_date = parsed.date().isoformat()
            except ValueError:
                pub_date = pub_date_str[:10]

        abstract = re.sub(r"<[^>]+>", "", description).strip()
        if not title:
            continue

        papers.append(
            Paper(
                title=title,
                authors=[],
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
