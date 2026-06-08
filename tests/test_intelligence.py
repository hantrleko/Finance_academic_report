from __future__ import annotations

from src.intelligence import (
    build_digest_brief,
    build_gap_map,
    build_research_radar,
    build_topic_workspace,
    citation_bucket,
    classify_taxonomy,
    gap_map_to_markdown,
    extract_topic_terms,
    paper_attention_score,
    radar_to_markdown,
    topic_workspace_to_markdown,
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


def test_build_topic_workspace_filters_by_all_query_terms():
    digests = [
        {"date": "2026-06-03", "papers": [
            _paper("Climate Risk and Bank Lending", topics=["Climate Risk"], source="ssrn"),
            _paper("Climate Preferences", topics=["Climate"], abstract="Investor preferences."),
        ]},
    ]
    workspace = build_topic_workspace(digests, "climate risk")
    assert workspace["paper_count"] == 1
    assert workspace["top_papers"][0]["title"] == "Climate Risk and Bank Lending"


def test_build_topic_workspace_returns_timeline_related_terms_and_outline():
    digests = [
        {"date": "2026-06-01", "papers": [_paper("Inflation Expectations", topics=["Inflation", "Expectations"])]},
        {"date": "2026-06-02", "papers": [_paper("Inflation and Central Bank Communication", topics=["Inflation", "Communication"])]},
    ]
    workspace = build_topic_workspace(digests, "inflation")
    assert workspace["paper_count"] == 2
    assert workspace["first_date"] == "2026-06-01"
    assert workspace["latest_date"] == "2026-06-02"
    assert workspace["timeline"] == [{"date": "2026-06-01", "count": 1}, {"date": "2026-06-02", "count": 1}]
    assert workspace["related_terms"]
    assert workspace["review_outline"]


def test_build_topic_workspace_empty_query_or_no_match_is_safe():
    workspace = build_topic_workspace([{"date": "2026-06-01", "papers": [_paper("Inflation Expectations")]}], "")
    assert workspace["paper_count"] == 0
    assert workspace["top_papers"] == []
    no_match = build_topic_workspace([{"date": "2026-06-01", "papers": [_paper("Inflation Expectations")]}], "crypto")
    assert no_match["paper_count"] == 0
    assert "暂未命中" in no_match["narrative"]


def test_topic_workspace_to_markdown_contains_literature_review_sections():
    workspace = build_topic_workspace([
        {"date": "2026-06-01", "papers": [_paper("Inflation Expectations", topics=["Inflation", "Expectations"])]}
    ], "inflation")
    markdown = topic_workspace_to_markdown(workspace)
    assert "# 专题工作台" in markdown
    assert "## 文献综述提纲" in markdown
    assert "## 推荐论文" in markdown


def test_topic_workspace_top_papers_include_citation_bucket():
    workspace = build_topic_workspace([
        {"date": "2026-06-01", "papers": [_paper("High Impact Inflation", topics=["Inflation"], cited_by_count=120)]}
    ], "inflation")
    assert workspace["top_papers"][0]["citation_bucket"] == "高影响"


def test_build_gap_map_creates_domain_method_matrix():
    digests = [
        {"date": "2026-06-03", "papers": [
            _paper("Inflation and Causal Identification", abstract="Monetary policy with causal identification.", topics=["Inflation"]),
            _paper("Bank Lending with Machine Learning", abstract="Bank lending and credit risk using machine learning.", topics=["Credit"]),
        ]},
    ]
    gap_map = build_gap_map(digests, recent_issues=1)
    assert gap_map["paper_count"] == 2
    matrix_pairs = {(item["domain"], item["method"]): item["count"] for item in gap_map["matrix"]}
    assert matrix_pairs[("货币政策与通胀", "因果识别")] == 1
    assert matrix_pairs[("银行与金融中介", "机器学习/AI")] == 1


def test_build_gap_map_identifies_missing_active_combinations():
    digests = [
        {"date": "2026-06-03", "papers": [
            _paper("Inflation and Causal Identification", abstract="Monetary policy with causal identification.", topics=["Inflation"]),
            _paper("Bank Lending with Machine Learning", abstract="Bank lending and credit risk using machine learning.", topics=["Credit"]),
        ]},
    ]
    gap_map = build_gap_map(digests, recent_issues=1)
    opportunity_pairs = {(item["domain"], item["method"]) for item in gap_map["opportunities"]}
    assert ("货币政策与通胀", "机器学习/AI") in opportunity_pairs
    assert ("银行与金融中介", "因果识别") in opportunity_pairs


def test_gap_map_to_markdown_contains_opportunities_and_strong_pairs():
    gap_map = build_gap_map([
        {"date": "2026-06-03", "papers": [
            _paper("Inflation and Causal Identification", abstract="Monetary policy with causal identification.", topics=["Inflation"]),
            _paper("Bank Lending with Machine Learning", abstract="Bank lending and credit risk using machine learning.", topics=["Credit"]),
        ]},
    ], recent_issues=1)
    markdown = gap_map_to_markdown(gap_map)
    assert "# 研究缺口地图" in markdown
    assert "## 潜在选题机会" in markdown
    assert "## 已有强组合" in markdown


def test_build_gap_map_empty_input_is_safe():
    gap_map = build_gap_map([], recent_issues=5)
    assert gap_map["paper_count"] == 0
    assert gap_map["opportunities"] == []
    assert gap_map["matrix"]
