"""我的收藏页面：管理收藏的论文，支持 BibTeX 导出。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from utils.bookmarks import export_bibtex, is_bookmarked, load_bookmarks, remove_bookmark, _paper_id
from utils.safety import format_summary_html, html_escape_text, safe_url
from src.models import VENUE_WHITELIST

st.set_page_config(
    page_title="我的收藏 | 金融文献速递",
    page_icon="⭐",
    layout="wide",
)

st.markdown(
    """
    <style>
    .bm-card {
        background: #fffdf0;
        border: 1px solid #f0d060;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .bm-title { font-size: 1.05rem; font-weight: 700; color: #1a3a6e; }
    .bm-meta { color: #555; font-size: 0.88rem; margin: 0.3rem 0; }
    .summary-box {
        background: #eef4ff;
        border-left: 4px solid #1a56db;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        margin-top: 0.6rem;
        font-size: 0.93rem;
        line-height: 1.7;
    }
    .badge-top-tier {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        background: #fff8e1;
        color: #b45309;
        border: 1px solid #f59e0b;
        margin-left: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⭐ 我的收藏")
st.caption("在「今日速递」或「知识库搜索」页面点击「⭐ 收藏」按钮，论文将保存到这里。")

# ---- 加载收藏夹 ----
bookmarks = load_bookmarks()

if not bookmarks:
    st.info("收藏夹为空。请前往「今日速递」或「📚 知识库搜索」页面，点击论文卡片上的「⭐ 收藏」按钮。")
    st.stop()

# ---- 顶部统计与导出 ----
col1, col2, col3 = st.columns([1, 1, 4])
col1.metric("⭐ 收藏总数", len(bookmarks))

top_tier_count = sum(
    1 for b in bookmarks
    if any(wl in (b.get("venue") or "").lower() for wl in VENUE_WHITELIST)
)
col2.metric("🏆 顶级期刊", top_tier_count)

st.markdown("---")

# ---- 导出按钮 ----
export_col1, export_col2, _ = st.columns([1, 1, 4])
with export_col1:
    bibtex_str = export_bibtex(bookmarks)
    st.download_button(
        label="📥 导出 BibTeX (.bib)",
        data=bibtex_str,
        file_name="finance_bookmarks.bib",
        mime="text/plain",
        help="导出为 BibTeX 格式，可直接导入 Zotero、EndNote、Mendeley 等文献管理软件",
    )

with export_col2:
    # 导出为 Markdown
    md_lines = ["# 我的收藏 — 金融文献速递", ""]
    for i, b in enumerate(bookmarks, 1):
        title = b.get("title", "无标题")
        authors = b.get("authors", "N/A")
        venue = b.get("venue", "N/A")
        pub_date = b.get("published_date", "N/A") or "N/A"
        doi_url = b.get("doi_url", "")
        summary = b.get("summary_zh", "")
        link = f"[{title}]({doi_url})" if doi_url else title
        md_lines.append(f"## {i}. {link}")
        md_lines.append(f"**作者：** {authors}  |  **期刊：** {venue}  |  **发表：** {pub_date}")
        if summary:
            md_lines.append(f"\n{summary}")
        md_lines.append("")
    md_str = "\n".join(md_lines)
    st.download_button(
        label="📄 导出 Markdown (.md)",
        data=md_str,
        file_name="finance_bookmarks.md",
        mime="text/markdown",
        help="导出为 Markdown 格式，可粘贴到 Notion、Obsidian 等笔记软件",
    )

st.markdown("---")

# ---- 搜索与筛选 ----
st.markdown("### 📋 收藏列表")
col_s1, col_s2 = st.columns([3, 1])
with col_s1:
    search_kw = st.text_input("🔍 搜索收藏", placeholder="输入标题、作者、期刊关键词")
with col_s2:
    top_tier_only = st.checkbox("🏆 仅显示顶级期刊", value=False)

# 过滤
filtered = bookmarks
if search_kw:
    kw = search_kw.lower()
    filtered = [
        b for b in filtered
        if kw in (b.get("title") or "").lower()
        or kw in (b.get("authors") or "").lower()
        or kw in (b.get("venue") or "").lower()
        or kw in (b.get("abstract") or "").lower()
        or kw in (b.get("summary_zh") or "").lower()
    ]
if top_tier_only:
    filtered = [
        b for b in filtered
        if any(wl in (b.get("venue") or "").lower() for wl in VENUE_WHITELIST)
    ]

st.caption(f"共 {len(filtered)} / {len(bookmarks)} 篇收藏")

# ---- 论文卡片 ----
if not filtered:
    st.info("没有符合条件的收藏。")
else:
    for idx, b in enumerate(filtered, 1):
        title = b.get("title", "无标题")
        authors = b.get("authors", "N/A")
        venue = b.get("venue", "N/A")
        pub_date = b.get("published_date", "N/A") or "N/A"
        doi_url = b.get("doi_url", "")
        openalex_url = b.get("openalex_url", "")
        cited = b.get("cited_by_count", 0)
        source = b.get("source", "unknown")
        digest_date = b.get("digest_date", "")
        summary_raw = b.get("summary_zh", "")

        # 格式化摘要（先转义外部数据，再添加允许的结构化标签）
        summary_html = format_summary_html(summary_raw)

        # 顶级期刊徽章
        top_tier_badge = ""
        if any(wl in venue.lower() for wl in VENUE_WHITELIST):
            top_tier_badge = '<span class="badge-top-tier">🏆 Top Tier</span>'

        # 链接
        links_html = ""
        doi_safe = safe_url(doi_url)
        openalex_safe = safe_url(openalex_url)
        if doi_safe:
            links_html += f'<a href="{doi_safe}" target="_blank" rel="noopener">DOI</a> '
        if openalex_safe:
            links_html += f'<a href="{openalex_safe}" target="_blank" rel="noopener">原文链接</a>'

        source_label = {
            "arxiv": "arXiv", "openalex": "OpenAlex",
            "semantic_scholar": "Semantic Scholar", "nber": "NBER", "ssrn": "SSRN",
        }.get(source, source)

        title_html = html_escape_text(title)
        authors_html = html_escape_text(authors)
        venue_html = html_escape_text(venue)
        pub_date_html = html_escape_text(pub_date)
        cited_html = html_escape_text(cited)
        source_label_html = html_escape_text(source_label)
        from_date_str = f"  |  <strong>收录于：</strong>{html_escape_text(digest_date)}" if digest_date else ""

        st.markdown(
            f"""
            <div class="bm-card">
              <div class="bm-title">{idx}. {title_html}</div>
              <div class="bm-meta">
                {top_tier_badge}
                <strong>来源：</strong>{source_label_html}
                &nbsp;|&nbsp; <strong>期刊：</strong>{venue_html}
                &nbsp;|&nbsp; <strong>发表：</strong>{pub_date_html}
                &nbsp;|&nbsp; <strong>引用数：</strong>{cited_html}
                {from_date_str}
              </div>
              <div class="bm-meta"><strong>作者：</strong>{authors_html}</div>
              <div class="bm-meta">{links_html}</div>
              {"<div class='summary-box'>" + summary_html + "</div>" if summary_html else ""}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 操作按钮
        btn_c1, btn_c2, _ = st.columns([1, 1, 4])
        with btn_c1:
            # 单篇 BibTeX 导出
            single_bib = export_bibtex([b])
            st.download_button(
                label="📥 BibTeX",
                data=single_bib,
                file_name=f"paper_{idx}.bib",
                mime="text/plain",
                key=f"bib_{idx}",
                help="导出此篇的 BibTeX 引用格式",
            )
        with btn_c2:
            if st.button("🗑️ 取消收藏", key=f"rm_{idx}", help="从收藏夹中移除此论文"):
                pid = _paper_id(b)
                remove_bookmark(pid)
                st.success(f"已从收藏夹移除：{title[:40]}...")
                st.rerun()
