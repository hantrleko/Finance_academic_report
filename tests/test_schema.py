from src.schema import normalize_digest, normalize_paper, validate_digest


def test_normalize_paper_fills_defaults_and_coerces_lists():
    paper = normalize_paper({"title": "A", "authors": "Alice, Bob", "topics": None, "cited_by_count": "3", "source": "ssrn"})
    assert paper["authors"] == ["Alice", "Bob"]
    assert paper["topics"] == []
    assert paper["cited_by_count"] == 3
    assert paper["source"] == "ssrn"


def test_normalize_paper_preserves_extra_fields():
    paper = normalize_paper({"title": "A", "source": "openalex", "relevance_score": 87})
    assert paper["relevance_score"] == 87


def test_normalize_digest_adds_optional_fields():
    digest = normalize_digest({"date": "2026-05-01", "papers": []})
    assert digest["count"] == 0
    assert digest["source_used"] == ""
    assert digest["overview"] == ""
    assert digest["insights"] == {}


def test_validate_digest_rejects_unknown_source_and_count_mismatch():
    ok, errors = validate_digest({
        "date": "2026-05-01",
        "count": 2,
        "papers": [{"title": "Paper", "source": "unknown_source"}],
    })
    assert not ok
    assert any("count" in err for err in errors)
    assert any("source" in err for err in errors)


def test_validate_digest_accepts_valid_minimal_digest():
    ok, errors = validate_digest({
        "date": "2026-05-01",
        "count": 1,
        "papers": [{"title": "Paper", "source": "openalex"}],
    })
    assert ok
    assert errors == []
