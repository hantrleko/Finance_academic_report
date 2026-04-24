"""页面：今日速递 - 展示最新一期文献日报"""
from __future__ import annotations

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from utils.data_loader import get_available_dates, load_latest_digest, load_digest

st.set_page_config(
    page_title="今日速递 | 金融文献速递",
    page_icon="🏠",
    layout="wide",
)

# ---- 样式 ----
st.markdown(
    """
    <style>
    .paper-card {
        background: #f8faff;
        border: 1px solid #dce8ff;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .paper-title { font-size: 1.05rem; font-weight: 700; color: #1a3a6e; }
    .paper-meta { color: #555; font-size: 0.88rem; margin: 0.3rem 0; }
    .summary-box {
        background: #eef4ff;
        border-left: 4px solid #1a56db;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        margin-top: 0.6rem;
        font-size: 0.93rem;
        line-height: 1.7;
    }
    .source-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-arxiv { background: #fff3cd; color: #856404; }
    .badge-openalex { background: #d1e7dd; color: #0f5132; }
    .badge-semantic_scholar { background: #cff4fc; color: #055160; }
    .badge-nber { background: #f8d7da; color: #842029; }
    .insight-box {
        background: #f0f9f2;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .overview-box {
        background: #e8f4fd;
        border: 1px solid #b3d9f2;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 1.5rem;
        font-size: 0.97rem;
        line-height: 1.8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- 标题区 ----
st.title("🏠 今日速递")

# 日期选择器
available_dates = get_available_dates()
col_title, col_date = st.columns([3, 1])
with col_date:
    if available_dates:
        selected_date = st.selectbox(
            "选择日期",
            options=["latest"] + available_dates,
            format_func=lambda x: "最新一期" if x == "latest" else x,
            key="date_selector",
        )
    else:
        selected_date = "latest"

# 加载数据
data = load_digest(selected_date)

if data is None:
    st.error("暂无数据，请先运行文献抓取或等待 GitHub Actions 自动更新。")
    st.stop()

date_str = data.get("date", "未知日期")
count = data.get("count", 0)
source_used = data.get("source_used", "N/A")
papers = data.get("papers", [])
insights = data.get("insights", {})
overview = data.get("overview", "")

# ---- 顶部统计栏 ----
st.markdown(f"### 📅 {date_str} 文献速递")
col1, col2, col3, col4 = st.columns(4)
col1.metric("📄 文献总数", count)

source_counts: dict[str, int] = {}
for p in papers:
    src = p.get("source", "unknown")
    source_counts[src] = source_counts.get(src, 0) + 1

col2.metric("🔬 arXiv", source_counts.get("arxiv", 0))
col3.metric("🌐 OpenAlex", source_counts.get("openalex", 0))
col4.metric("📚 S2 + NBER", source_counts.get("semantic_scholar", 0) + source_counts.get("nber", 0))

st.markdown("---")

# ---- 今日综述 ----
if overview:
    st.markdown(
        f'<div class="overview-box">📢 <strong>今日综述</strong><br><br>{overview}</div>',
        unsafe_allow_html=True,
    )

# ---- 今日洞察 ----
if insights:
    with st.expander("🧭 今日洞察（LLM 分析）", expanded=True):
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        insight_labels = {
            "themes": "📌 主题趋势",
            "methods": "🔬 方法趋势",
            "implications": "💡 启示与应用",
            "watchlist": "👀 后续观察",
        }
        for key, label in insight_labels.items():
            val = insights.get(key, "")
            if val:
                st.markdown(f"**{label}：** {val}")
        st.markdown("</div>", unsafe_allow_html=True)

# ---- 筛选控件 ----
st.markdown("### 📋 文献列表")
col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    search_kw = st.text_input("🔍 搜索标题/摘要关键词", placeholder="例如：inflation、machine learning")
with col_f2:
    source_filter = st.multiselect(
        "来源筛选",
        options=["arxiv", "openalex", "semantic_scholar", "nber"],
        default=[],
        placeholder="全部来源",
    )

# ---- 论文卡片展示 ----
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

filtered_papers = papers
if source_filter:
    filtered_papers = [p for p in filtered_papers if p.get("source") in source_filter]
if search_kw:
    kw_lower = search_kw.lower()
    filtered_papers = [
        p for p in filtered_papers
        if kw_lower in p.get("title", "").lower()
        or kw_lower in p.get("abstract", "").lower()
        or kw_lower in p.get("summary_zh", "").lower()
    ]

if not filtered_papers:
    st.info("没有符合条件的文献。")
else:
    st.caption(f"共显示 {len(filtered_papers)} / {count} 篇文献")
    for idx, p in enumerate(filtered_papers, 1):
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
            links_html += f'<a href="{doi_url}" target="_blank" rel="noopener">DOI</a> '
        if openalex_url:
            links_html += f'<a href="{openalex_url}" target="_blank" rel="noopener">原文链接</a>'

        topics = p.get("topics") or []
        topics_str = " · ".join(topics[:5]) if topics else "N/A"

        summary_raw = p.get("summary_zh", "")
        # 将结构化摘要中的 emoji 标签转为换行格式
        summary_html = summary_raw.replace("📌 研究问题：", "<br><strong>📌 研究问题：</strong>")
        summary_html = summary_html.replace("🔬 研究方法：", "<br><strong>🔬 研究方法：</strong>")
        summary_html = summary_html.replace("📊 核心发现：", "<br><strong>📊 核心发现：</strong>")
        summary_html = summary_html.replace("💡 应用价值：", "<br><strong>💡 应用价值：</strong>")

        venue = p.get("venue", "N/A")
        pub_date = p.get("published_date", "N/A") or "N/A"
        cited = p.get("cited_by_count", 0)

        st.markdown(
            f"""
            <div class="paper-card">
              <div class="paper-title">{idx}. {p.get("title", "无标题")}</div>
              <div class="paper-meta">
                <span class="source-badge {badge_cls}">{src_label}</span>
                <strong>期刊/来源：</strong>{venue}
                &nbsp;|&nbsp; <strong>发表：</strong>{pub_date}
                &nbsp;|&nbsp; <strong>引用数：</strong>{cited}
              </div>
              <div class="paper-meta"><strong>作者：</strong>{authors_str}</div>
              <div class="paper-meta"><strong>主题：</strong>{topics_str}</div>
              <div class="paper-meta">{links_html}</div>
              <div class="summary-box">{summary_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
