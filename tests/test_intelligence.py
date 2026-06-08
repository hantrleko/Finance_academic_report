from __future__ import annotations

from src.intelligence import (
    build_digest_brief,
    build_research_radar,
    citation_bucket,
    classify_taxonomy,
    extract_topic_terms,
    paper_attention_score,
    radar_to_markdown,
)


def _paper(title: str, **overrides):
    data = {
        "title": title,
        "authors": ["A. Author"],
        "venue": "Journal of Finance",
        "published_date": "2026-01-01",
        "doi_url": "https://doi.org/10.0000/example",
        "openalex_url": "https://openalex.org/W1",
        "cited_by_count": 10,
        "abstract": "This paper studies monetary policy with causal identification and machine learning.",
        "summary_zh": "研究问题：货币政策。研究方法：因果识别。",
        "topics": ["Monetary Policy", "Machine Learning"],
        "source": "openalex",
    }
    data.update(overrides)
    return data


def test_citation_bucket_labels_are_stable():
    assert citation_bucket(0) == "新近/待观察"
    assert citation_bucket(3) == "早期引用"
    assert citation_bucket(30) == "已有关注"
    assert citation_bucket(150) == "高影响"
    assert citation_bucket(600) == "经典高引"


def test_attention_score_rewards_top_tier_and_citations():
    base = _paper("Base paper", venue="Working Paper", cited_by_count=0, topics=[])
    strong = _paper("Strong paper", venue="Journal of Finance", cited_by_count=200)
    assert paper_attention_score(strong, reference_year=2026) > paper_attention_score(base, reference_year=2026)


def test_extract_topic_terms_uses_topics_and_title_words():
    terms = extract_topic_terms([
        _paper("Inflation Expectations and Monetary Policy", topics=["Inflation"]),
        _paper("Inflation Risk in Bond Markets", topics=["Inflation"]),
    ])
    assert terms[0]["term"] == "inflation"
    assert terms[0]["score"] >= 6


def test_classify_taxonomy_detects_method_keywords():
    result = classify_taxonomy([_paper("Causal Machine Learning for Credit")], {
        "AI": ("machine learning",),
        "Causal": ("causal",),
    })
    labels = {item["label"] for item in result}
    assert labels == {"AI", "Causal"}


def test_build_digest_brief_returns_reading_path_and_narrative():
    digest = {
        "date": "2026-06-01",
        "papers": [
            _paper("Monetary Policy and Inflation"),
            _paper("Climate Finance Working Paper", source="ssrn", venue="SSRN", topics=["Climate Finance"], cited_by_count=0),
        ],
    }
    brief = build_digest_brief(digest)
    assert brief["paper_count"] == 2
    assert brief["top_tier_count"] == 1
    assert brief["source_mix"]
    assert brief["reading_path"]
    assert "本期" in brief["narrative"]


def test_build_research_radar_finds_emerging_topics_and_notable_papers():
    digests = [
        {"date": "2026-06-03", "papers": [_paper("Climate Risk and Bank Lending", topics=["Climate Risk"], source="ssrn")]},
        {"date": "2026-06-02", "papers": [_paper("Climate Policy and Asset Pricing", topics=["Climate Risk"], source="arxiv")]},
        {"date": "2026-05-01", "papers": [_paper("Old Monetary Policy Study", topics=["Monetary Policy"])]},
    ]
    radar = build_research_radar(digests, recent_issues=2, baseline_issues=1)
    terms = {item["term"] for item in radar["emerging_topics"]}
    assert "climate risk" in terms
    assert radar["recent_paper_count"] == 2
    assert radar["notable_papers"]


def test_radar_to_markdown_contains_core_sections():
    radar = build_research_radar([
        {"date": "2026-06-03", "papers": [_paper("Climate Risk and Bank Lending", topics=["Climate Risk"])]}
    ])
    markdown = radar_to_markdown(radar)
    assert "# 研究雷达" in markdown
    assert "## 上升主题" in markdown
    assert "## 推荐关注论文" in markdown
