"""页面：历史档案 - 按日期浏览历史文献速递"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from utils.data_loader import get_available_dates, load_digest, get_alert_dates
from src.models import VENUE_WHITELIST

st.set_page_config(
    page_title="历史档案 | 金融文献速递",
    page_icon="📅",
    layout="wide",
)

st.markdown(
    """
    <style>
    .paper-card {
        background: #f8faff;
        border: 1px solid #dce8ff;
        border-radius: 10px;
        padding: 1rem 1.3rem;
        margin-bottom: 0.8rem;
    }
    .paper-title { font-size: 1rem; font-weight: 700; color: #1a3a6e; }
    .paper-meta { color: #555; font-size: 0.86rem; margin: 0.25rem 0; }
    .summary-box {
        background: #eef4ff;
        border-left: 4px solid #1a56db;
        border-radius: 6px;
        padding: 0.7rem 0.9rem;
        margin-top: 0.5rem;
        font-size: 0.91rem;
        line-height: 1.7;
    }
    .source-badge {
        display: inline-block;
        padding: 2px 9px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 600;
        margin-right: 5px;
    }
    .badge-arxiv { background: #fff3cd; color: #856404; }
    .badge-openalex { background: #d1e7dd; color: #0f5132; }
    .badge-semantic_scholar { background: #cff4fc; color: #055160; }
    .badge-nber { background: #f8d7da; color: #842029; }
    .badge-top-tier {
        display: inline-block;
        padding: 2px 9px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
        background: #fff8e1;
        color: #b45309;
        border: 1px solid #f59e0b;
        margin-left: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📅 历史档案")

available_dates = get_available_dates()
alert_dates = set(get_alert_dates())

if not available_dates:
    st.warning("暂无历史数据。请等待 GitHub Actions 自动更新或手动运行抓取。")
    st.stop()

# ---- 日期选择 ----
col1, col2 = st.columns([2, 2])
with col1:
    selected_date = st.selectbox(
        "选择日期",
        options=available_dates,
        index=0,
        help="选择要查看的历史日期",
    )
with col2:
    st.markdown(f"**共 {len(available_dates)} 期历史记录**")
    if selected_date in alert_dates:
        st.warning(f"⚠️ {selected_date} 当日抓取结果为空（已记录告警）")

# ---- 加载并展示 ----
data = load_digest(selected_date)
if data is None:
    st.error(f"无法加载 {selected_date} 的数据。")
    st.stop()

if data.get("_error"):
    st.warning(
        f"⚠️ **{selected_date}** 的数据文件已损坏（可能含有 Git 冲突标记），无法解析。"
        " 请前往 GitHub 仓库手动修复该文件。"
    )
    st.stop()

papers = data.get("papers", [])
count = data.get("count", 0)
source_used = data.get("source_used", "N/A")
insights = data.get("insights", {})
overview = data.get("overview", "")

# 统计栏
st.markdown(f"### 📅 {selected_date} 速递")
c1, c2, c3 = st.columns(3)
c1.metric("文献总数", count)
c2.metric("数据来源", source_used[:40] + "..." if len(source_used) > 40 else source_used)
c3.metric("LLM 洞察", "有" if insights else "无")

if overview:
    with st.expander("📢 今日综述", expanded=False):
        st.markdown(overview)

if insights:
    with st.expander("🧭 今日洞察", expanded=False):
        for key, label in [("themes", "主题趋势"), ("methods", "方法趋势"),
                           ("implications", "启示与应用"), ("watchlist", "后续观察")]:
            val = insights.get(key, "")
            if val:
                st.markdown(f"**{label}：** {val}")

st.markdown("---")

# ---- 辅助函数 ----
def is_top_tier(venue: str) -> bool:
    venue_lower = venue.lower()
    return any(wl in venue_lower for wl in VENUE_WHITELIST)


def paper_to_markdown(idx: int, p: dict) -> str:
    title = p.get("title", "无标题")
    authors = p.get("authors") or []
    authors_str = ", ".join(authors[:5]) + (" et al." if len(authors) > 5 else "") if authors else "N/A"
    venue = p.get("venue", "N/A")
    pub_date = p.get("published_date", "N/A") or "N/A"
    cited = p.get("cited_by_count", 0)
    doi_url = p.get("doi_url", "")
    openalex_url = p.get("openalex_url", "")
    summary = p.get("summary_zh", "")
    source = p.get("source", "unknown")
    source_label = {"arxiv": "arXiv", "openalex": "OpenAlex", "semantic_scholar": "Semantic Scholar", "nber": "NBER"}.get(source, source)
    tier_tag = " 🏆 Top Tier" if is_top_tier(venue) else ""
    link = doi_url or openalex_url or ""
    title_md = f"[{title}]({link})" if link else title
    lines = [
        f"### {idx}. {title_md}",
        f"**来源：** {source_label}{tier_tag}  |  **期刊：** {venue}  |  **发表：** {pub_date}  |  **引用：** {cited}",
        f"**作者：** {authors_str}",
        "",
        summary,
        "",
    ]
    return "\n".join(lines)


def digest_to_markdown(date_str: str, papers: list, overview: str, insights: dict) -> str:
    lines = [f"# 金融经济学文献速递 — {date_str}", ""]
    if overview:
        lines += ["## 今日综述", "", overview, ""]
    if insights:
        lines += ["## 今日洞察", ""]
        for key, label in [("themes", "主题趋势"), ("methods", "方法趋势"),
                            ("implications", "启示与应用"), ("watchlist", "后续观察")]:
            val = insights.get(key, "")
            if val:
                lines.append(f"**{label}：** {val}")
        lines.append("")
    lines += ["## 文献列表", ""]
    for idx, p in enumerate(papers, 1):
        lines.append(paper_to_markdown(idx, p))
    return "\n".join(lines)


# ---- 筛选 ----
col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1, 1, 1])
with col_f1:
    search_kw = st.text_input("🔍 搜索关键词", placeholder="标题、摘要或主题")
with col_f2:
    source_filter = st.multiselect(
        "来源筛选",
        options=["arxiv", "openalex", "semantic_scholar", "nber"],
        default=[],
        placeholder="全部来源",
    )
with col_f3:
    top_tier_only = st.checkbox("🏆 仅显示顶级期刊", value=False)
with col_f4:
    sort_by_relevance = st.checkbox(
        "🎯 按相关性排序",
        value=False,
        help="需要在侧边栏填写「我的研究偏好」并配置 LLM API",
    )

# ---- 个性化相关性评分 ----
user_preference = st.session_state.get("user_preference", "").strip()
pref_api_base = st.session_state.get("preference_llm_api_base", "").strip()
pref_api_key = st.session_state.get("preference_llm_api_key", "").strip()
pref_model = st.session_state.get("preference_llm_model", "gpt-4o-mini").strip()

_cache_key = f"relevance_hist_{selected_date}_{user_preference[:50]}_{len(papers)}"

if sort_by_relevance and user_preference and papers:
    if not pref_api_key or not pref_api_base:
        st.warning("⚠️ 请在侧边栏「相关性评分 LLM 配置」中填写 API Base URL 和 API Key。")
    elif _cache_key not in st.session_state:
        with st.spinner(f"🎯 正在为 {len(papers)} 篇论文评估相关性，请稍候..."):
            try:
                from src.models import LLMConfig
                from src.summarization import score_papers_by_preference
                import copy

                pref_cfg = LLMConfig(
                    enabled=True,
                    api_base=pref_api_base,
                    api_key=pref_api_key,
                    model=pref_model,
                    timeout_seconds=30,
                )
                papers_copy = copy.deepcopy(papers)
                papers_copy = score_papers_by_preference(papers_copy, user_preference, pref_cfg)
                st.session_state[_cache_key] = papers_copy
                st.success(f"✅ 相关性评分完成！")
            except Exception as e:
                st.error(f"❌ 相关性评分失败：{e}")
                st.session_state[_cache_key] = None
    else:
        if st.session_state[_cache_key] is not None:
            st.info(f"🎯 已使用缓存的相关性评分结果")

    if _cache_key in st.session_state and st.session_state[_cache_key] is not None:
        papers = st.session_state[_cache_key]
        papers = sorted(papers, key=lambda p: p.get("relevance_score", -1), reverse=True)
elif sort_by_relevance and not user_preference:
    st.warning("⚠️ 请先在左侧侧边栏填写「我的研究偏好」，然后再开启相关性排序。")

filtered = papers
if source_filter:
    filtered = [p for p in filtered if p.get("source") in source_filter]
if search_kw:
    kw = search_kw.lower()
    filtered = [
        p for p in filtered
        if kw in p.get("title", "").lower()
        or kw in p.get("abstract", "").lower()
        or kw in p.get("summary_zh", "").lower()
    ]
if top_tier_only:
    filtered = [p for p in filtered if is_top_tier(p.get("venue", ""))]

# ---- 导出按钮 ----
if papers:
    full_md = digest_to_markdown(selected_date, papers, overview, insights)
    st.download_button(
        label="⬇️ 导出本期日报 (Markdown)",
        data=full_md,
        file_name=f"finance_digest_{selected_date}.md",
        mime="text/markdown",
        help="将本期所有文献导出为 Markdown 文件",
    )

BADGE_CLASS = {
    "arxiv": "badge-arxiv",
    "openalex": "badge-openalex",
    "semantic_scholar": "badge-semantic_scholar",
    "nber": "badge-nber",
}
SOURCE_LABEL = {
    "arxiv": "arXiv",
    "openalex": "OpenAlex",
    "semantic_scholar": "Semantic Scholar",
    "nber": "NBER",
}

st.caption(f"显示 {len(filtered)} / {count} 篇文献")

for idx, p in enumerate(filtered, 1):
    src = p.get("source", "unknown")
    badge_cls = BADGE_CLASS.get(src, "badge-openalex")
    src_label = SOURCE_LABEL.get(src, src)

    authors = p.get("authors") or []
    if len(authors) > 5:
        authors_str = ", ".join(authors[:5]) + " et al."
    elif authors:
        authors_str = ", ".join(authors)
    else:
        authors_str = "N/A"

    doi_url = p.get("doi_url", "")
    openalex_url = p.get("openalex_url", "")
    links_html = ""
    if doi_url:
        links_html += f'<a href="{doi_url}" target="_blank">DOI</a> '
    if openalex_url:
        links_html += f'<a href="{openalex_url}" target="_blank">原文链接</a>'

    topics = p.get("topics") or []
    topics_str = " · ".join(topics[:5]) if topics else "N/A"

    summary_raw = p.get("summary_zh", "")
    summary_html = summary_raw.replace("📌 研究问题：", "<br><strong>📌 研究问题：</strong>")
    summary_html = summary_html.replace("🔬 研究方法：", "<br><strong>🔬 研究方法：</strong>")
    summary_html = summary_html.replace("📊 核心发现：", "<br><strong>📊 核心发现：</strong>")
    summary_html = summary_html.replace("💡 应用价值：", "<br><strong>💡 应用价值：</strong>")

    venue = p.get("venue", "N/A")
    pub_date = p.get("published_date", "N/A") or "N/A"
    cited = p.get("cited_by_count", 0)

    # 顶级期刊徽章
    top_tier_badge = ""
    if is_top_tier(venue):
        top_tier_badge = '<span class="badge-top-tier">🏆 Top Tier</span>'

    # 相关性分数条
    relevance_score = p.get("relevance_score", -1)
    relevance_html = ""
    if relevance_score >= 0:
        bar_width = relevance_score
        if relevance_score >= 70:
            bar_color = "linear-gradient(90deg, #3b82f6, #10b981)"
        elif relevance_score >= 40:
            bar_color = "linear-gradient(90deg, #f59e0b, #3b82f6)"
        else:
            bar_color = "linear-gradient(90deg, #ef4444, #f59e0b)"
        relevance_html = f"""
        <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
            <span style="font-size:0.82rem;color:#555;min-width:80px;">🎯 相关性</span>
            <div style="flex:1;background:#e5e7eb;border-radius:6px;height:8px;overflow:hidden;">
                <div style="width:{bar_width}%;height:8px;border-radius:6px;background:{bar_color};"></div>
            </div>
            <span style="font-size:0.82rem;font-weight:700;color:#1d4ed8;min-width:36px;">{relevance_score}/100</span>
        </div>
        """

    st.markdown(
        f"""
        <div class="paper-card">
          <div class="paper-title">{idx}. {p.get("title", "无标题")}</div>
          <div class="paper-meta">
            <span class="source-badge {badge_cls}">{src_label}</span>
            {top_tier_badge}
            <strong>期刊：</strong>{venue}
            &nbsp;|&nbsp; <strong>发表：</strong>{pub_date}
            &nbsp;|&nbsp; <strong>引用：</strong>{cited}
          </div>
          <div class="paper-meta"><strong>作者：</strong>{authors_str}</div>
          <div class="paper-meta"><strong>主题：</strong>{topics_str}</div>
          {relevance_html}
          <div class="paper-meta">{links_html}</div>
          <div class="summary-box">{summary_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 单篇复制按钮
    paper_md = paper_to_markdown(idx, p)
    st.download_button(
        label="📋 复制此篇 (Markdown)",
        data=paper_md,
        file_name=f"paper_{idx}_{selected_date}.md",
        mime="text/markdown",
        key=f"copy_hist_{idx}_{selected_date}",
        help="下载此篇论文的 Markdown 格式摘要",
    )
