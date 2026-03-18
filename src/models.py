"""Core data models and constants for finance digest."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

OPENALEX_URL = "https://api.openalex.org/works"
ARXIV_API_URL = "https://export.arxiv.org/api/query"
CROSSREF_API_URL = "https://api.crossref.org/works"
S2_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
NBER_RSS_URL = "https://www.nber.org/rss/new.xml"

CONCEPT_ECONOMICS = "C162324750"
CONCEPT_FINANCE = "C154945302"

FINANCE_KEYWORDS = {
    "finance", "financial", "asset", "asset pricing", "bank", "banking", "stock", "bond",
    "portfolio", "investment", "pricing", "risk", "credit", "macro", "macroeconomic",
    "microeconomic", "economics", "economic", "econometric", "econometrics", "market",
    "monetary", "inflation", "fiscal", "trade", "household", "firm", "labor", "employment",
    "inequality", "derivative", "hedging", "volatility", "interest rate", "exchange rate",
    "central bank", "capital", "equity", "debt", "leverage", "corporate finance",
    "behavioral finance", "fintech", "cryptocurrency", "blockchain", "insurance", "pension",
    "mutual fund", "venture capital", "private equity", "real estate", "commodity", "option",
    "futures", "yield", "dividend", "valuation", "capm", "fama", "sharpe",
}

SPAM_TERMS = {
    "free dice", "monopoly go", "video", "enlace", "miss pacman", "telegram", "casino", "betting",
    "gift code", "daily rewards", "robotic", "weeding", "surgery", "medical imaging", "antenna",
    "phylogenetic",
}

VENUE_BLACKLIST = {
    "zenodo", "figshare", "dépôt institutionnel", "institutional repository", "preprints.org",
    "mdpi preprints", "research square", "authorea", "techrxiv", "engrxiv", "africarxiv",
    "eartharxiv", "medrxiv", "biorxiv",
}


@dataclass
class Paper:
    title: str
    authors: list[str]
    venue: str
    published_date: str
    doi_url: str
    openalex_url: str
    cited_by_count: int
    abstract: str
    summary_zh: str
    topics: list[str]
    source: str = "openalex"


@dataclass
class DigestConfig:
    max_papers: int = 12
    source_min_papers: int = 2
    min_citations: int = 0
    output_dir: Path = Path("output")
    keep_latest_when_empty: bool = True
    lookback_days: int = 7
    topic_whitelist: set[str] = field(default_factory=lambda: set(FINANCE_KEYWORDS))
    topic_blacklist: set[str] = field(default_factory=lambda: set(SPAM_TERMS))
    min_quality_score: int = 2
    openalex_mailto: str = ""
    s2_api_key: str = ""
    s2_min_interval_seconds: float = 1.1


@dataclass
class LLMConfig:
    api_base: str = ""
    api_key: str = ""
    model: str = ""
    timeout_seconds: int = 30

    @property
    def enabled(self) -> bool:
        return bool(self.api_base and self.api_key and self.model)
