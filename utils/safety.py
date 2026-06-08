"""Safety helpers for rendering externally sourced paper metadata in Streamlit."""
from __future__ import annotations

from html import escape
from typing import Any, Iterable
from urllib.parse import urlparse

_ALLOWED_URL_SCHEMES = {"http", "https"}
_STRUCTURED_SUMMARY_LABELS = [
    "📌 研究问题：",
    "🔬 研究方法：",
    "📊 核心发现：",
    "💡 应用价值：",
]


def html_escape_text(value: Any) -> str:
    """Return a string escaped for safe insertion into HTML text/attributes."""
    if value is None:
        return ""
    return escape(str(value), quote=True)


def html_escape_join(values: Iterable[Any], sep: str = ", ") -> str:
    """Escape and join a list-like value for HTML rendering."""
    return html_escape_text(sep.join(str(v) for v in values if v is not None and str(v)))


def safe_url(value: Any) -> str:
    """Return an escaped http(s) URL or an empty string for unsafe/invalid URLs."""
    if value is None:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""
    parsed = urlparse(raw)
    if parsed.scheme.lower() not in _ALLOWED_URL_SCHEMES or not parsed.netloc:
        return ""
    return html_escape_text(raw)


def format_summary_html(summary: Any) -> str:
    """Escape a summary and add lightweight formatting for known summary labels."""
    escaped = html_escape_text(summary).replace("\n", "<br>")
    for label in _STRUCTURED_SUMMARY_LABELS:
        escaped = escaped.replace(label, f"<br><strong>{label}</strong>")
    return escaped
