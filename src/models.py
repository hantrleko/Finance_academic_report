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

# 顶级金融/经济学期刊白名单（命中则质量评分加成）
VENUE_WHITELIST = {
    "journal of finance",
    "journal of financial economics",
    "review of financial studies",
    "american economic review",
    "quarterly journal of economics",
    "journal of political economy",
    "review of economic studies",
    "econometrica",
    "journal of monetary economics",
    "nber working papers",
    "journal of economic perspectives",
    "journal of economic literature",
    "journal of accounting and economics",
    "management science",
    "review of economics and statistics",
    "journal of financial and quantitative analysis",
    "journal of banking & finance",
    "journal of international economics",
    "rand journal of economics",
    "economic journal",
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
    source_max_share: float = 0.6
    min_citations: int = 0
    output_dir: Path = Path("output")
    keep_latest_when_empty: bool = True
    lookback_days: int = 7
    topic_whitelist: set[str] = field(default_factory=lambda: set(FINANCE_KEYWORDS))
    topic_blacklist: set[str] = field(default_factory=lambda: set(SPAM_TERMS))
    min_quality_score: int = 2
    openalex_mailto: str = ""
    s2_api_key: str = ""
    s2_min_interval_seconds: float = 1.5


@dataclass
class LLMConfig:
    api_base: str = ""
    api_key: str = ""
    model: str = ""
    timeout_seconds: int = 30

    @property
    def enabled(self) -> bool:
        return bool(self.api_base and self.api_key and self.model)
