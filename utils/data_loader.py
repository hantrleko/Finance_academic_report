"""Streamlit 数据加载工具：从 output/ 目录读取已生成的 digest JSON 文件。"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import streamlit as st

# 确保项目根目录在 sys.path 中，以便导入 src 模块
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

OUTPUT_DIR = _ROOT / "output"


@st.cache_data(ttl=300)
def get_available_dates() -> list[str]:
    """返回所有已生成日报的日期列表（降序）。结果缓存 5 分钟。"""
    if not OUTPUT_DIR.exists():
        return []
    dates = []
    for d in OUTPUT_DIR.iterdir():
        if d.is_dir() and d.name not in ("latest", "alerts"):
            json_file = d / "digest.json"
            if json_file.exists():
                dates.append(d.name)
    return sorted(dates, reverse=True)


@st.cache_data(ttl=300)
def load_digest(date: str) -> dict[str, Any] | None:
    """加载指定日期的 digest 数据。date 格式为 'YYYY-MM-DD' 或 'latest'。
    
    使用 safe_load_digest_json 进行容错读取：
    - 若文件不存在，返回 None
    - 若 JSON 损坏或含 Git 冲突标记，返回带 _error 标记的字典，供前端展示提示
    """
    from src.filtering import safe_load_digest_json

    path = OUTPUT_DIR / date / "digest.json"
    if not path.exists():
        return None

    result = safe_load_digest_json(path)
    if result is None:
        # 文件存在但无法解析，返回带错误标记的字典，让前端可以显示友好提示
        return {"_error": True, "date": date, "papers": [], "count": 0}
    return result


def load_latest_digest() -> dict[str, Any] | None:
    """加载最新一期 digest 数据。"""
    return load_digest("latest")


@st.cache_data(ttl=600)
def load_all_digests() -> list[dict[str, Any]]:
    """加载所有日期的 digest 数据（用于统计分析）。结果缓存 10 分钟。
    
    自动跳过损坏的文件，不影响统计页面的正常展示。
    """
    results = []
    for date in get_available_dates():
        data = load_digest(date)
        if data and not data.get("_error"):
            results.append(data)
    return results


@st.cache_data(ttl=300)
def get_alert_dates() -> list[str]:
    """返回所有告警日期列表。结果缓存 5 分钟。"""
    alerts_dir = OUTPUT_DIR / "alerts"
    if not alerts_dir.exists():
        return []
    return sorted(
        [f.stem for f in alerts_dir.glob("*.json")],
        reverse=True,
    )
