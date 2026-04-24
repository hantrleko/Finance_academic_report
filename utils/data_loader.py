"""Streamlit 数据加载工具：从 output/ 目录读取已生成的 digest JSON 文件。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def get_available_dates() -> list[str]:
    """返回所有已生成日报的日期列表（降序）。"""
    dates = []
    for d in OUTPUT_DIR.iterdir():
        if d.is_dir() and d.name not in ("latest", "alerts"):
            json_file = d / "digest.json"
            if json_file.exists():
                dates.append(d.name)
    return sorted(dates, reverse=True)


def load_digest(date: str) -> dict[str, Any] | None:
    """加载指定日期的 digest 数据。date 格式为 'YYYY-MM-DD' 或 'latest'。"""
    path = OUTPUT_DIR / date / "digest.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def load_latest_digest() -> dict[str, Any] | None:
    """加载最新一期 digest 数据。"""
    return load_digest("latest")


def load_all_digests() -> list[dict[str, Any]]:
    """加载所有日期的 digest 数据（用于统计分析）。"""
    results = []
    for date in get_available_dates():
        data = load_digest(date)
        if data:
            results.append(data)
    return results


def get_alert_dates() -> list[str]:
    """返回所有告警日期列表。"""
    alerts_dir = OUTPUT_DIR / "alerts"
    if not alerts_dir.exists():
        return []
    return sorted(
        [f.stem for f in alerts_dir.glob("*.json")],
        reverse=True,
    )
