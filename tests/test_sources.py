import datetime as dt
import io
from urllib.error import HTTPError

from src import sources


class DummyResponse:
    def __init__(self, body: str):
        self._body = body.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._body


def test_s2_retry_on_429(monkeypatch):
    calls = {"count": 0}

    def fake_urlopen(_req, timeout=30):
        calls["count"] += 1
        if calls["count"] == 1:
            raise HTTPError(url="https://example.com", code=429, msg="Too Many Requests", hdrs={"Retry-After": "1"}, fp=io.BytesIO())
        return DummyResponse('{"data": []}')

    monkeypatch.setattr(sources, "urlopen", fake_urlopen)
    monkeypatch.setattr(sources.time, "sleep", lambda _n: None)

    papers = sources.fetch_semantic_scholar_papers(dt.date(2026, 3, 1), dt.date(2026, 3, 2), mailto="")
    assert papers == []
    assert calls["count"] == 2


def test_nber_xml_recovery_on_bare_ampersand(monkeypatch):
    broken_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<rss>
  <channel>
    <item>
      <title>Test & Value</title>
      <link>https://nber.org/papers/w1</link>
      <description>Paper & abstract</description>
      <pubDate>Mon, 17 Mar 2026 00:00:00 -0400</pubDate>
    </item>
  </channel>
</rss>
"""

    monkeypatch.setattr(sources, "urlopen", lambda _req, timeout=30: DummyResponse(broken_xml))
    papers = sources.fetch_nber_papers(dt.date(2026, 3, 1), max_results=5)

    assert len(papers) == 1
    assert papers[0].title == "Test & Value"
    assert papers[0].abstract == "Paper & abstract"
