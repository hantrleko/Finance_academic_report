"""Subscriber registry and email sending."""
from __future__ import annotations

import json
import os
import re
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


@dataclass
class SMTPConfig:
    host: str
    port: int
    user: str
    password: str

    @property
    def enabled(self) -> bool:
        return bool(self.host and self.user and self.password)


def load_smtp_config_from_env() -> SMTPConfig:
    return SMTPConfig(
        host=os.getenv("SMTP_HOST", "").strip(),
        port=int(os.getenv("SMTP_PORT", "587").strip() or "587"),
        user=os.getenv("SMTP_USER", "").strip(),
        password=os.getenv("SMTP_PASS", "").strip(),
    )


def normalize_email(email: str) -> str:
    return email.strip().lower()


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(normalize_email(email)))


def load_subscribers(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(raw, list):
        return []
    cleaned = sorted({normalize_email(e) for e in raw if isinstance(e, str) and is_valid_email(e)})
    return cleaned


def save_subscribers(path: Path, emails: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cleaned = sorted({normalize_email(e) for e in emails if is_valid_email(e)})
    path.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")


def add_subscriber(path: Path, email: str) -> tuple[bool, str]:
    normalized = normalize_email(email)
    if not is_valid_email(normalized):
        return False, "邮箱格式不正确"

    subscribers = load_subscribers(path)
    if normalized in subscribers:
        return False, "该邮箱已订阅"

    subscribers.append(normalized)
    save_subscribers(path, subscribers)
    return True, "订阅成功"


def remove_subscriber(path: Path, email: str) -> tuple[bool, str]:
    normalized = normalize_email(email)
    subscribers = load_subscribers(path)
    if normalized not in subscribers:
        return False, "该邮箱不在订阅列表"

    subscribers.remove(normalized)
    save_subscribers(path, subscribers)
    return True, "已取消订阅"


def send_digest_email(
    recipients: list[str],
    smtp_cfg: SMTPConfig,
    subject: str,
    markdown_body: str,
    html_body: str,
) -> int:
    if not recipients:
        return 0
    if not smtp_cfg.enabled:
        raise RuntimeError("SMTP 未配置完整，无法发送订阅邮件。")

    sent = 0
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_cfg.host, smtp_cfg.port, timeout=30) as server:
        server.starttls(context=context)
        server.login(smtp_cfg.user, smtp_cfg.password)
        for recipient in recipients:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = smtp_cfg.user
            msg["To"] = recipient
            msg.set_content(markdown_body)
            if html_body:
                msg.add_alternative(html_body, subtype="html")
            server.send_message(msg)
            sent += 1
    return sent
