"""CLI entry point for the digest pipeline (email push removed)."""
from __future__ import annotations

import argparse
from pathlib import Path

from .config import (
    load_analysis_llm_config_from_env,
    load_digest_config_from_env,
    load_translate_llm_config_from_env,
)
from .pipeline import build_digest


def run_digest() -> int:
    config = load_digest_config_from_env()
    translate_cfg = load_translate_llm_config_from_env()
    analysis_cfg = load_analysis_llm_config_from_env()

    result = build_digest(config, translate_cfg=translate_cfg, analysis_cfg=analysis_cfg)
    if result["count"] == 0:
        print("::warning::No papers generated for today.")
    print(
        f"Generated digest: {result['markdown']} | count={result['count']} | "
        f"source={result['source_used']} | latest_updated={result['latest_updated']}"
    )
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Finance & Economics daily digest tool")
    return parser


def main() -> None:
    make_parser().parse_args()
    raise SystemExit(run_digest())


if __name__ == "__main__":
    main()
