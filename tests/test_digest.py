import datetime as dt
import json
from pathlib import Path

from src.models import DigestConfig, LLMConfig, Paper
from src.pipeline import build_digest
from src.sources import extract_abstract
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
    monkeypatch.setattr(p, "fetch_ssrn_papers", lambda *_args, **_kwargs: [])

    cfg = DigestConfig(output_dir=tmp_path / "out")
    result = build_digest(cfg, translate_cfg=LLMConfig(), analysis_cfg=LLMConfig(), run_date=dt.date(2024, 1, 2))

    assert result["json"].exists()
    assert result["markdown"].exists()
    assert result["html"].exists()
    assert result["count"] == 1
    assert result["latest_updated"] is True


def test_build_digest_survives_single_source_failure(monkeypatch, tmp_path: Path):
    """并行抓取回归测试：任一数据源抛异常时应被降级为空列表，
    不影响其它源，digest 仍能正常生成。"""
    from src import pipeline as p

    def mk(source: str, title: str) -> Paper:
        return Paper(
            title=title,
            authors=["A"],
            venue="NBER Working Papers",
            published_date="2024-01-01",
            doi_url="",
            openalex_url="https://openalex.org/" + title,
            cited_by_count=0,
            abstract="finance economics abstract",
            summary_zh="",
            topics=["Finance"],
            source=source,
        )

    def boom(*_args, **_kwargs):
        raise RuntimeError("source down")

    monkeypatch.setattr(p, "fetch_openalex_papers", lambda *_a, **_k: [mk("openalex", "P1")])
    monkeypatch.setattr(p, "fetch_arxiv_finance_econ_papers", boom)  # 故意失败
    monkeypatch.setattr(p, "fetch_semantic_scholar_papers", lambda *_a, **_k: [mk("semantic_scholar", "P2")])
    monkeypatch.setattr(p, "fetch_nber_papers", lambda *_a, **_k: [mk("nber", "P3")])
    monkeypatch.setattr(p, "fetch_ssrn_papers", lambda *_a, **_k: [mk("ssrn", "P4")])

    cfg = DigestConfig(output_dir=tmp_path / "out_fail", min_quality_score=0)
    result = build_digest(cfg, translate_cfg=LLMConfig(), analysis_cfg=LLMConfig(), run_date=dt.date(2024, 1, 3))

    # arxiv 源失败但不应抛出异常，其余 4 源正常
    assert result["count"] == 4
    assert "arxiv" not in result["source_used"]
    assert "openalex" in result["source_used"]


def test_build_digest_overview_in_json(monkeypatch, tmp_path: Path):
    """验证 overview 字段被正确写入 digest.json（修复漏写 Bug 的回归测试）。"""
    from src import pipeline as p

    dummy = Paper(
        title="Asset Pricing and Risk",
        authors=["C. D. Author"],
        venue="Journal of Finance",
        published_date="2024-01-01",
        doi_url="",
        openalex_url="https://openalex.org/W999",
        cited_by_count=5,
        abstract="This paper studies asset pricing and risk premiums.",
        summary_zh="",
        topics=["Finance", "Economics"],
        source="openalex",
    )

    monkeypatch.setattr(p, "fetch_openalex_papers", lambda *_args, **_kwargs: [dummy])
    monkeypatch.setattr(p, "fetch_arxiv_finance_econ_papers", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(p, "fetch_semantic_scholar_papers", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(p, "fetch_nber_papers", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(p, "fetch_ssrn_papers", lambda *_args, **_kwargs: [])

    cfg = DigestConfig(output_dir=tmp_path / "out_overview")
    result = build_digest(cfg, translate_cfg=LLMConfig(), analysis_cfg=LLMConfig(), run_date=dt.date(2024, 1, 5))

    metadata = json.loads(result["json"].read_text(encoding="utf-8"))
    # overview 字段必须存在（即使 LLM 未配置时为空字符串，也不能是 KeyError）
    assert "overview" in metadata


def test_keep_latest_when_empty(monkeypatch, tmp_path: Path):
    from src import pipeline as p

    monkeypatch.setattr(p, "fetch_openalex_papers", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(p, "fetch_arxiv_finance_econ_papers", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(p, "fetch_semantic_scholar_papers", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(p, "fetch_nber_papers", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(p, "fetch_ssrn_papers", lambda *_args, **_kwargs: [])

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
    monkeypatch.setattr(p, "fetch_ssrn_papers", lambda *_args, **_kwargs: [])

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
    monkeypatch.setattr(p, "fetch_ssrn_papers", lambda *_args, **_kwargs: [])

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


# ---- 新增：中优先级覆盖率补充测试 ----

def test_safe_load_digest_json_valid(tmp_path: Path):
    """正常 JSON 文件应被正确解析。"""
    from src.filtering import safe_load_digest_json

    valid = tmp_path / "digest.json"
    valid.write_text(json.dumps({"count": 5, "papers": []}), encoding="utf-8")
    result = safe_load_digest_json(valid)
    assert result is not None
    assert result["count"] == 5


def test_safe_load_digest_json_git_conflict(tmp_path: Path):
    """含 Git 冲突标记的文件应返回 None。"""
    from src.filtering import safe_load_digest_json

    broken = tmp_path / "broken.json"
    broken.write_text(
        "<<<<<<< HEAD\n{\"count\": 1}\n=======\n{\"count\": 2}\n>>>>>>> branch\n",
        encoding="utf-8",
    )
    assert safe_load_digest_json(broken) is None


def test_safe_load_digest_json_invalid_json(tmp_path: Path):
    """格式错误的 JSON 文件应返回 None。"""
    from src.filtering import safe_load_digest_json

    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json}", encoding="utf-8")
    assert safe_load_digest_json(bad) is None


def test_safe_load_digest_json_missing_file(tmp_path: Path):
    """不存在的文件应返回 None。"""
    from src.filtering import safe_load_digest_json

    assert safe_load_digest_json(tmp_path / "nonexistent.json") is None


def test_extract_json_from_llm_response_plain():
    """纯 JSON 字符串应被直接解析。"""
    from src.summarization import _extract_json_from_llm_response

    raw = '{"themes": "asset pricing", "methods": "regression"}'
    result = _extract_json_from_llm_response(raw)
    assert result is not None
    assert result["themes"] == "asset pricing"


def test_extract_json_from_llm_response_with_markdown():
    """带 markdown 代码块的 JSON 应被正确提取。"""
    from src.summarization import _extract_json_from_llm_response

    raw = '```json\n{"relevant": true, "score": 8, "reason": "高质量金融研究"}\n```'
    result = _extract_json_from_llm_response(raw)
    assert result is not None
    assert result["score"] == 8


def test_extract_json_from_llm_response_embedded():
    """JSON 嵌入在其他文字中时应被正确提取。"""
    from src.summarization import _extract_json_from_llm_response

    raw = '以下是我的分析结果：\n{"themes": "货币政策", "methods": "VAR模型"}\n希望对你有帮助。'
    result = _extract_json_from_llm_response(raw)
    assert result is not None
    assert result["themes"] == "货币政策"


def test_extract_json_from_llm_response_invalid():
    """无法提取 JSON 时应返回 None。"""
    from src.summarization import _extract_json_from_llm_response

    assert _extract_json_from_llm_response("这不是 JSON 内容") is None
    assert _extract_json_from_llm_response("") is None


def test_dedupe_and_filter_removes_duplicates():
    """重复标题的论文应只保留第一篇。"""
    from src.filtering import dedupe_and_filter

    p1 = Paper(
        title="Asset Pricing and Risk",
        authors=["A"],
        venue="Journal of Finance",
        published_date="2024-01-01",
        doi_url="https://doi.org/10.1234/test",
        openalex_url="",
        cited_by_count=10,
        abstract="This paper studies asset pricing and risk premiums using regression.",
        summary_zh="",
        topics=["Finance", "Economics"],
        source="openalex",
    )
    p2 = Paper(
        title="Asset  Pricing and Risk",  # 多余空格，归一化后与 p1 相同
        authors=["B"],
        venue="Journal of Finance",
        published_date="2024-01-02",
        doi_url="",
        openalex_url="",
        cited_by_count=5,
        abstract="Duplicate paper.",
        summary_zh="",
        topics=["Finance"],
        source="openalex",
    )
    result = dedupe_and_filter(
        [p1, p2],
        topic_whitelist={"finance", "risk"},
        topic_blacklist=set(),
        min_quality_score=0,
    )
    assert len(result) == 1
    assert result[0].authors == ["A"]


def test_dedupe_and_filter_blacklist():
    """黑名单关键词命中的论文应被过滤。"""
    from src.filtering import dedupe_and_filter
    from src.models import VENUE_BLACKLIST

    bl_venue = next(iter(VENUE_BLACKLIST)) if VENUE_BLACKLIST else "predatory journal xyz"
    p = Paper(
        title="Some Paper",
        authors=["A"],
        venue=bl_venue,
        published_date="2024-01-01",
        doi_url="",
        openalex_url="",
        cited_by_count=0,
        abstract="content",
        summary_zh="",
        topics=["Finance"],
        source="openalex",
    )
    result = dedupe_and_filter(
        [p],
        topic_whitelist={"finance"},
        topic_blacklist=set(),
        min_quality_score=1,
    )
    assert len(result) == 0


def test_dedupe_and_filter_applies_quality_rules_to_ssrn():
    """SSRN 论文应与 OpenAlex/S2 一样经过黑名单和质量过滤。"""
    from src.filtering import dedupe_and_filter

    ssrn_paper = Paper(
        title="Unrelated Teaching Note",
        authors=["A"],
        venue="SSRN",
        published_date="2026-05-01",
        doi_url="",
        openalex_url="https://openalex.org/W-ssrn",
        cited_by_count=0,
        abstract="This note is about teaching material and classroom pedagogy.",
        summary_zh="",
        topics=["Education"],
        source="ssrn",
    )

    result = dedupe_and_filter(
        [ssrn_paper],
        topic_whitelist={"finance"},
        topic_blacklist={"pedagogy"},
        min_quality_score=1,
    )

    assert result == []


def test_legacy_send_emails_command_is_noop(capsys):
    """旧 workflow 中的 send-emails 命令应兼容为成功 no-op。"""
    from src.digest import make_parser, run_legacy_email_command

    args = make_parser().parse_args([
        "send-emails",
        "--subscribers-file",
        "data/subscribers.json",
        "--fallback-to",
        "test@example.com",
    ])
    assert args.command == "send-emails"

    assert run_legacy_email_command() == 0
    captured = capsys.readouterr()
    assert "skipping legacy send-emails" in captured.out


def test_render_markdown_includes_overview():
    """render_markdown 应在输出中包含 overview 内容。"""
    from src.rendering import render_markdown

    md = render_markdown(
        date="2024-01-01",
        papers=[],
        overview="今日文献聚焦于资产定价研究。",
    )
    assert "今日文献聚焦于资产定价研究" in md
    assert "今日综述" in md


def test_render_markdown_no_overview():
    """overview 为空时不应出现综述区块。"""
    from src.rendering import render_markdown

    md = render_markdown(date="2024-01-01", papers=[], overview="")
    assert "今日综述" not in md
