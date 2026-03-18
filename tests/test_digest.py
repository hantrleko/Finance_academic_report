import datetime as dt
import json
from pathlib import Path

from src.models import DigestConfig, LLMConfig, Paper
from src.pipeline import build_digest
from src.sources import extract_abstract
from src.subscribers import add_subscriber, load_subscribers, remove_subscriber
from src.summarization import simple_zh_summary


def test_extract_abstract_rebuilds_word_order():
    indexed = {"InvertedIndex": {"hello": [0], "world": [1], "finance": [2]}}
    assert extract_abstract(indexed) == "hello world finance"


def test_simple_summary_contains_title():
    text = simple_zh_summary("Asset Pricing", "This paper studies risk premiums.", ["Economics", "Finance"])
    assert "Asset Pricing" in text
    assert "摘要概述" in text
    assert "结论要点" in text
    assert "This paper studies risk premiums." not in text


def test_build_digest_writes_files(monkeypatch, tmp_path: Path):
    from src import pipeline as p

    dummy = Paper(
        title="A",
        authors=["B"],
        venue="C",
        published_date="2024-01-01",
        doi_url="",
        openalex_url="https://openalex.org/W123",
        cited_by_count=1,
        abstract="x",
        summary_zh="",
        topics=["Economics"],
        source="openalex",
    )

    monkeypatch.setattr(p, "fetch_openalex_papers", lambda *_args, **_kwargs: [dummy])
    monkeypatch.setattr(p, "fetch_arxiv_finance_econ_papers", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(p, "fetch_semantic_scholar_papers", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(p, "fetch_nber_papers", lambda *_args, **_kwargs: [])

    cfg = DigestConfig(output_dir=tmp_path / "out")
    result = build_digest(cfg, translate_cfg=LLMConfig(), analysis_cfg=LLMConfig(), run_date=dt.date(2024, 1, 2))

    assert result["json"].exists()
    assert result["markdown"].exists()
    assert result["html"].exists()
    assert result["count"] == 1
    assert result["latest_updated"] is True


def test_keep_latest_when_empty(monkeypatch, tmp_path: Path):
    from src import pipeline as p

    monkeypatch.setattr(p, "fetch_openalex_papers", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(p, "fetch_arxiv_finance_econ_papers", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(p, "fetch_semantic_scholar_papers", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(p, "fetch_nber_papers", lambda *_args, **_kwargs: [])

    out = tmp_path / "out"
    latest = out / "latest"
    latest.mkdir(parents=True)
    (latest / "digest.json").write_text(json.dumps({"count": 3}, ensure_ascii=False), encoding="utf-8")
    (latest / "digest.md").write_text("old", encoding="utf-8")

    cfg = DigestConfig(output_dir=out, keep_latest_when_empty=True)
    result = build_digest(cfg, translate_cfg=LLMConfig(), analysis_cfg=LLMConfig(), run_date=dt.date(2024, 1, 3))

    assert result["count"] == 0
    assert result["latest_updated"] is False
    assert (latest / "digest.md").read_text(encoding="utf-8") == "old"
    assert (out / "alerts" / "2024-01-03.json").exists()


def test_subscriber_crud(tmp_path: Path):
    file = tmp_path / "subscribers.json"

    ok, _ = add_subscriber(file, "alice@example.com")
    assert ok is True

    ok, msg = add_subscriber(file, "alice@example.com")
    assert ok is False
    assert "已订阅" in msg

    ok, _ = add_subscriber(file, "bob@example.com")
    assert ok is True

    subscribers = load_subscribers(file)
    assert subscribers == ["alice@example.com", "bob@example.com"]

    ok, _ = remove_subscriber(file, "alice@example.com")
    assert ok is True
    assert load_subscribers(file) == ["bob@example.com"]


def test_build_digest_keeps_multi_source_floor(monkeypatch, tmp_path: Path):
    from src import pipeline as p

    def make_paper(source: str, idx: int) -> Paper:
        return Paper(
            title=f"{source} paper {idx}",
            authors=["A"],
            venue="Journal of Finance",
            published_date="2026-03-18",
            doi_url="",
            openalex_url=f"https://example.com/{source}/{idx}",
            cited_by_count=1,
            abstract="finance market risk study with panel regression",
            summary_zh="",
            topics=["Economics", "Finance"],
            source=source,
        )

    monkeypatch.setattr(p, "fetch_openalex_papers", lambda *_args, **_kwargs: [make_paper("openalex", i) for i in range(1, 9)])
    monkeypatch.setattr(p, "fetch_arxiv_finance_econ_papers", lambda *_args, **_kwargs: [make_paper("arxiv", i) for i in range(1, 6)])
    monkeypatch.setattr(p, "fetch_semantic_scholar_papers", lambda *_args, **_kwargs: [make_paper("semantic_scholar", i) for i in range(1, 4)])
    monkeypatch.setattr(p, "fetch_nber_papers", lambda *_args, **_kwargs: [make_paper("nber", i) for i in range(1, 3)])

    cfg = DigestConfig(
        output_dir=tmp_path / "out_multi",
        max_papers=8,
        source_min_papers=1,
        min_quality_score=0,
    )
    result = build_digest(cfg, translate_cfg=LLMConfig(), analysis_cfg=LLMConfig(), run_date=dt.date(2026, 3, 18))
    metadata = json.loads(result["json"].read_text(encoding="utf-8"))
    sources = {item["source"] for item in metadata["papers"]}

    assert "openalex" in sources
    assert "arxiv" in sources
    assert "semantic_scholar" in sources
    assert "nber" in sources


def test_build_digest_respects_source_max_share(monkeypatch, tmp_path: Path):
    from src import pipeline as p

    def make_paper(source: str, idx: int) -> Paper:
        return Paper(
            title=f"{source} cap paper {idx}",
            authors=["A"],
            venue="Journal of Finance",
            published_date="2026-03-18",
            doi_url="",
            openalex_url=f"https://example.com/{source}/cap/{idx}",
            cited_by_count=1,
            abstract="finance market risk study with panel regression",
            summary_zh="",
            topics=["Economics", "Finance"],
            source=source,
        )

    monkeypatch.setattr(p, "fetch_openalex_papers", lambda *_args, **_kwargs: [make_paper("openalex", i) for i in range(1, 25)])
    monkeypatch.setattr(p, "fetch_arxiv_finance_econ_papers", lambda *_args, **_kwargs: [make_paper("arxiv", i) for i in range(1, 5)])
    monkeypatch.setattr(p, "fetch_semantic_scholar_papers", lambda *_args, **_kwargs: [make_paper("semantic_scholar", i) for i in range(1, 5)])
    monkeypatch.setattr(p, "fetch_nber_papers", lambda *_args, **_kwargs: [make_paper("nber", i) for i in range(1, 5)])

    cfg = DigestConfig(
        output_dir=tmp_path / "out_cap",
        max_papers=10,
        source_min_papers=1,
        source_max_share=0.4,
        min_quality_score=0,
    )
    result = build_digest(cfg, translate_cfg=LLMConfig(), analysis_cfg=LLMConfig(), run_date=dt.date(2026, 3, 18))
    metadata = json.loads(result["json"].read_text(encoding="utf-8"))
    source_counts: dict[str, int] = {}
    for item in metadata["papers"]:
        source_counts[item["source"]] = source_counts.get(item["source"], 0) + 1

    assert source_counts.get("openalex", 0) <= 4
