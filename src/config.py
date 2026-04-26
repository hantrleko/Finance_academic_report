"""Configuration loader for digest pipeline."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .models import DigestConfig, FINANCE_KEYWORDS, LLMConfig, SPAM_TERMS


def _csv_set(value: str, fallback: set[str]) -> set[str]:
    parsed = {x.strip().lower() for x in value.split(",") if x.strip()}
    return parsed or set(fallback)


def load_digest_config_from_env() -> DigestConfig:
    return DigestConfig(
        max_papers=int(os.getenv("DIGEST_MAX_PAPERS", "12")),
        source_min_papers=int(os.getenv("DIGEST_SOURCE_MIN_PAPERS", "2")),
        source_max_share=float(os.getenv("DIGEST_SOURCE_MAX_SHARE", "0.6")),
        min_citations=int(os.getenv("DIGEST_MIN_CITATIONS", "0")),
        output_dir=Path(os.getenv("DIGEST_OUTPUT_DIR", "output")),
        keep_latest_when_empty=os.getenv("DIGEST_KEEP_LATEST_WHEN_EMPTY", "1") == "1",
        lookback_days=int(os.getenv("DIGEST_LOOKBACK_DAYS", "7")),
        topic_whitelist=_csv_set(os.getenv("DIGEST_TOPIC_WHITELIST", ""), FINANCE_KEYWORDS),
        topic_blacklist=_csv_set(os.getenv("DIGEST_TOPIC_BLACKLIST", ""), SPAM_TERMS),
        min_quality_score=int(os.getenv("DIGEST_MIN_QUALITY_SCORE", "2")),
        openalex_mailto=os.getenv("OPENALEX_MAILTO", ""),
        s2_api_key=os.getenv("S2_API_KEY", ""),
        s2_min_interval_seconds=float(os.getenv("S2_MIN_INTERVAL_SECONDS", "1.1")),
    )


def load_translate_llm_config_from_env() -> LLMConfig:
    return LLMConfig(
        api_base=os.getenv("LLM_API_BASE", "https://api.siliconflow.cn/v1"),
        api_key=os.getenv("LLM_API_KEY", ""),
        model=os.getenv("LLM_MODEL", "tencent/Hunyuan-MT-7B"),
        timeout_seconds=int(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
    )


def load_analysis_llm_config_from_env() -> LLMConfig:
    return LLMConfig(
        api_base=os.getenv("ANALYSIS_LLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4"),
        api_key=os.getenv("ANALYSIS_LLM_API_KEY", ""),
        model=os.getenv("ANALYSIS_LLM_MODEL", "glm-4.7-flash"),
        timeout_seconds=int(os.getenv("ANALYSIS_LLM_TIMEOUT_SECONDS", "60")),
    )


def build_digest_config_from_dict(params: dict[str, Any]) -> DigestConfig:
    """从字典直接构建 DigestConfig，用于 Streamlit 前端直接传参，避免污染全局 os.environ。"""
    return DigestConfig(
        max_papers=int(params.get("max_papers", 12)),
        source_min_papers=int(params.get("source_min_papers", 2)),
        source_max_share=float(params.get("source_max_share", 0.6)),
        min_citations=int(params.get("min_citations", 0)),
        output_dir=Path(params.get("output_dir", "output")),
        keep_latest_when_empty=bool(params.get("keep_latest_when_empty", True)),
        lookback_days=int(params.get("lookback_days", 7)),
        topic_whitelist=set(FINANCE_KEYWORDS),
        topic_blacklist=set(SPAM_TERMS),
        min_quality_score=int(params.get("min_quality_score", 2)),
        openalex_mailto=str(params.get("openalex_mailto", "")),
        s2_api_key=str(params.get("s2_api_key", "")),
        s2_min_interval_seconds=float(params.get("s2_min_interval_seconds", 1.5)),
    )


def build_translate_llm_config_from_dict(params: dict[str, Any]) -> LLMConfig:
    """从字典直接构建翻译 LLMConfig，避免污染全局 os.environ。"""
    return LLMConfig(
        api_base=str(params.get("llm_api_base", "https://api.siliconflow.cn/v1")),
        api_key=str(params.get("llm_api_key", "")),
        model=str(params.get("llm_model", "tencent/Hunyuan-MT-7B")),
        timeout_seconds=int(params.get("llm_timeout_seconds", 30)),
    )


def build_analysis_llm_config_from_dict(params: dict[str, Any]) -> LLMConfig:
    """从字典直接构建分析 LLMConfig，避免污染全局 os.environ。"""
    return LLMConfig(
        api_base=str(params.get("analysis_api_base", "https://open.bigmodel.cn/api/paas/v4")),
        api_key=str(params.get("analysis_api_key", "")),
        model=str(params.get("analysis_model", "glm-4.7-flash")),
        timeout_seconds=int(params.get("analysis_timeout_seconds", 60)),
    )
