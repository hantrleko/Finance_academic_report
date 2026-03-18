"""Renderers for digest output."""
from __future__ import annotations

import html

from .models import Paper


def render_markdown(
    date: str,
    papers: list[Paper],
    note: str = "",
    overview: str = "",
    insights: dict[str, str] | None = None,
) -> str:
    insights = insights or {}
    lines = [f"# 金融经济学每日文献速递（{date}）", "", f"共筛选到 **{len(papers)}** 篇文献。", ""]
    if overview:
        lines.extend(["> 📢 **今日综述**", ">", *[f"> {line}" for line in overview.splitlines()], ""])
    if insights:
        lines.extend(
            [
                "## 今日洞察（LLM）",
                f"- 主题趋势：{insights.get('themes', 'N/A')}",
                f"- 方法趋势：{insights.get('methods', 'N/A')}",
                f"- 启示与应用：{insights.get('implications', 'N/A')}",
                f"- 后续观察：{insights.get('watchlist', 'N/A')}",
                "",
            ]
        )
    if note:
        lines.extend([f"> {note}", ""])

    for idx, p in enumerate(papers, start=1):
        links: list[str] = []
        if p.doi_url:
            links.append(f"[DOI]({p.doi_url})")
        if p.openalex_url:
            links.append(f"[链接]({p.openalex_url})")
        lines.extend(
            [
                f"## {idx}. {p.title}",
                f"- 来源：{p.source}",
                f"- 作者：{', '.join(p.authors) if p.authors else 'N/A'}",
                f"- 期刊/来源：{p.venue}",
                f"- 发表日期：{p.published_date}",
                f"- 引用数：{p.cited_by_count}",
                f"- 主题：{', '.join(p.topics) if p.topics else 'N/A'}",
                f"- 链接：{' '.join(links) if links else 'N/A'}",
                "",
                f"**中文摘要（自动生成）**：{p.summary_zh}",
                "",
            ]
        )
    return "\n".join(lines)


def render_html(
    date: str,
    papers: list[Paper],
    note: str = "",
    overview: str = "",
    insights: dict[str, str] | None = None,
) -> str:
    insights = insights or {}
    cards: list[str] = []
    for idx, p in enumerate(papers, start=1):
        doi_link = f'<a href="{html.escape(p.doi_url)}" target="_blank" rel="noopener noreferrer">DOI</a>' if p.doi_url else ""
        ext_link = f'<a href="{html.escape(p.openalex_url)}" target="_blank" rel="noopener noreferrer">链接</a>' if p.openalex_url else ""
        sep = " | " if doi_link and ext_link else ""
        cards.append(
            f"""
  <article class=\"card\">
    <h2>{idx}. {html.escape(p.title)}</h2>
    <p class=\"meta\">来源：{html.escape(p.source)}｜作者：{html.escape(', '.join(p.authors) if p.authors else 'N/A')}</p>
    <p class=\"meta\">期刊/来源：{html.escape(p.venue)}｜发表：{html.escape(p.published_date)}｜引用数：{p.cited_by_count}</p>
    <p class=\"meta\">主题：{html.escape(', '.join(p.topics) if p.topics else 'N/A')}</p>
    <p>{doi_link}{sep}{ext_link}</p>
    <p class=\"summary\"><strong>中文摘要（自动生成）:</strong> {html.escape(p.summary_zh)}</p>
  </article>
            """.strip()
        )

    note_html = f'<p class="note">{html.escape(note)}</p>' if note else ""
    overview_html = f'<div class="overview"><h2>📢 今日综述</h2><p>{html.escape(overview)}</p></div>' if overview else ""
    insights_html = ""
    if insights:
        insights_html = (
            '<div class="insights"><h2>🧭 今日洞察（LLM）</h2>'
            f'<p><strong>主题趋势：</strong>{html.escape(insights.get("themes", "N/A"))}</p>'
            f'<p><strong>方法趋势：</strong>{html.escape(insights.get("methods", "N/A"))}</p>'
            f'<p><strong>启示与应用：</strong>{html.escape(insights.get("implications", "N/A"))}</p>'
            f'<p><strong>后续观察：</strong>{html.escape(insights.get("watchlist", "N/A"))}</p>'
            "</div>"
        )
    cards_html = "\n".join(cards)

    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>金融经济学每日文献速递 - {html.escape(date)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem auto; max-width: 900px; line-height: 1.6; color: #111; padding: 0 1rem; }}
    .card {{ border: 1px solid #e6e6e6; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; }}
    .meta {{ color: #666; font-size: 0.95rem; }}
    .summary {{ background: #f8f8f8; padding: 0.8rem; border-radius: 8px; }}
    .note {{ color: #a15d00; background: #fff7e6; border: 1px solid #ffdf99; padding: 0.75rem; border-radius: 8px; }}
    .overview {{ background: #e8f4fd; border: 1px solid #b3d9f2; padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem; }}
    .insights {{ background: #f0f9f2; border: 1px solid #ccead2; padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem; }}
  </style>
</head>
<body>
  <h1>金融经济学每日文献速递</h1>
  <p class=\"meta\">日期：{html.escape(date)}｜篇数：{len(papers)}</p>
  {overview_html}
  {insights_html}
  {note_html}
  {cards_html}
</body>
</html>
"""
