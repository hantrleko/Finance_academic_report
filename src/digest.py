"""CLI entry point for the digest pipeline."""
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
    parser.add_argument(
        "command",
        nargs="?",
        choices=["send-emails"],
        help="Legacy no-op command kept for backward-compatible workflows.",
    )
    parser.add_argument("--subscribers-file", default="", help=argparse.SUPPRESS)
    parser.add_argument("--fallback-to", default="", help=argparse.SUPPRESS)
    return parser


def run_legacy_email_command() -> int:
    """Keep removed email workflow steps non-fatal while deployments transition.

    Email delivery was removed from the project, but older GitHub Actions
    workflows may still invoke ``python -m src.digest send-emails``. Treat that
    command as a successful no-op so digest generation and commit steps can
    continue instead of failing on an unknown argument.
    """
    print("Email delivery has been removed; skipping legacy send-emails command.")
    return 0


def main() -> None:
    args = make_parser().parse_args()
    if args.command == "send-emails":
        raise SystemExit(run_legacy_email_command())
    raise SystemExit(run_digest())


if __name__ == "__main__":
    main()
