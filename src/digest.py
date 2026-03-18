"""Finance digest command-line entrypoint."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import (
    load_analysis_llm_config_from_env,
    load_digest_config_from_env,
    load_translate_llm_config_from_env,
)
from .pipeline import build_digest
from .sources import extract_abstract as _extract_abstract
from .subscribers import (
    add_subscriber,
    load_smtp_config_from_env,
    load_subscribers,
    remove_subscriber,
    send_digest_email,
)
from .summarization import simple_zh_summary as _simple_zh_summary

DEFAULT_SUBSCRIBERS_FILE = Path("data/subscribers.json")


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


def cmd_subscribe(email: str | None, subscribers_file: Path) -> int:
    input_email = email or input("请输入要订阅的邮箱: ").strip()
    ok, message = add_subscriber(subscribers_file, input_email)
    print(message)
    return 0 if ok else 1


def cmd_unsubscribe(email: str, subscribers_file: Path) -> int:
    ok, message = remove_subscriber(subscribers_file, email)
    print(message)
    return 0 if ok else 1


def cmd_list_subscribers(subscribers_file: Path) -> int:
    subscribers = load_subscribers(subscribers_file)
    print(json.dumps(subscribers, ensure_ascii=False, indent=2))
    return 0


def cmd_send_emails(subscribers_file: Path, fallback_to: str) -> int:
    subscribers = load_subscribers(subscribers_file)
    if fallback_to.strip():
        for addr in [x.strip().lower() for x in fallback_to.split(",") if x.strip()]:
            if addr not in subscribers:
                subscribers.append(addr)

    if not subscribers:
        print("No subscribers found, skip sending email.")
        return 0

    latest_md = Path("output/latest/digest.md")
    latest_html = Path("output/latest/index.html")
    markdown_body = latest_md.read_text(encoding="utf-8") if latest_md.exists() else "Digest markdown not found."
    html_body = latest_html.read_text(encoding="utf-8") if latest_html.exists() else ""

    smtp_cfg = load_smtp_config_from_env()
    if not smtp_cfg.enabled:
        print("SMTP not fully configured, skip sending email.")
        return 0
    sent = send_digest_email(
        recipients=sorted(set(subscribers)),
        smtp_cfg=smtp_cfg,
        subject="Finance & Economics Daily Digest",
        markdown_body=markdown_body,
        html_body=html_body,
    )
    print(f"Sent digest email to {sent} subscribers")
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Finance & Economics daily digest tool")
    subparsers = parser.add_subparsers(dest="command")

    subscribe = subparsers.add_parser("subscribe", help="Add an email subscriber")
    subscribe.add_argument("--email", type=str, default="", help="Subscriber email")
    subscribe.add_argument("--subscribers-file", type=Path, default=DEFAULT_SUBSCRIBERS_FILE)

    unsubscribe = subparsers.add_parser("unsubscribe", help="Remove an email subscriber")
    unsubscribe.add_argument("--email", required=True)
    unsubscribe.add_argument("--subscribers-file", type=Path, default=DEFAULT_SUBSCRIBERS_FILE)

    list_subs = subparsers.add_parser("list-subscribers", help="List all subscribers")
    list_subs.add_argument("--subscribers-file", type=Path, default=DEFAULT_SUBSCRIBERS_FILE)

    send_emails = subparsers.add_parser("send-emails", help="Send latest digest email to all subscribers")
    send_emails.add_argument("--subscribers-file", type=Path, default=DEFAULT_SUBSCRIBERS_FILE)
    send_emails.add_argument("--fallback-to", type=str, default="")

    return parser


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()

    if args.command == "subscribe":
        raise SystemExit(cmd_subscribe(email=args.email, subscribers_file=args.subscribers_file))
    if args.command == "unsubscribe":
        raise SystemExit(cmd_unsubscribe(email=args.email, subscribers_file=args.subscribers_file))
    if args.command == "list-subscribers":
        raise SystemExit(cmd_list_subscribers(subscribers_file=args.subscribers_file))
    if args.command == "send-emails":
        raise SystemExit(cmd_send_emails(subscribers_file=args.subscribers_file, fallback_to=args.fallback_to))

    raise SystemExit(run_digest())


if __name__ == "__main__":
    main()
