"""页面：今日速递 - 展示最新一期文献日报"""
from __future__ import annotations

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from utils.data_loader import get_available_dates, load_digest
from utils.safety import format_summary_html, html_escape_text, safe_url
from src.intelligence import build_digest_brief
from src.models import VENUE_WHITELIST

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
    .badge-ssrn { background: #eadcff; color: #5a189a; }
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
    .relevance-bar-wrap {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 4px 0;
    }
    .relevance-label { font-size: 0.82rem; color: #555; min-width: 80px; }
    .relevance-bar-bg {
        flex: 1;
        background: #e5e7eb;
        border-radius: 6px;
        height: 8px;
        overflow: hidden;
    }
    .relevance-bar-fill {
        height: 8px;
        border-radius: 6px;
        background: linear-gradient(90deg, #3b82f6, #10b981);
    }
    .relevance-score-num { font-size: 0.82rem; font-weight: 700; color: #1d4ed8; min-width: 36px; }
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

if data.get("_error"):
    st.warning(
        f"⚠️ **{selected_date}** 的数据文件已损坏（可能含有 Git 冲突标记），无法解析。"
        " 请前往 GitHub 仓库手动修复 `output/{selected_date}/digest.json` 文件。"
    )
    st.stop()

date_str = data.get("date", "未知日期")
count = data.get("count", 0)
source_used = data.get("source_used", "N/A")
papers = data.get("papers", [])
insights = data.get("insights", {})
overview = data.get("overview", "")
warnings = data.get("_warnings", [])

if warnings:
    with st.expander("⚠️ 数据格式提示", expanded=False):
        for warning in warnings:
            st.warning(warning)

# ---- 顶部统计栏 ----
st.markdown(f"### 📅 {date_str} 文献速递")
col1, col2, col3, col4 = st.columns(4)
col1.metric("📄 文献总数", count)

source_counts: dict[str, int] = {}
for p in papers:
    src = p.get("source", "unknown")
    source_counts[src] = source_counts.get(src, 0) + 1

col2.metric("🔬 arXiv", source_counts.get("arxiv", 0))
col3.metric("🌐 OpenAlex + SSRN", source_counts.get("openalex", 0) + source_counts.get("ssrn", 0))
col4.metric("📚 S2 + NBER", source_counts.get("semantic_scholar", 0) + source_counts.get("nber", 0))

st.markdown("---")

# ---- 今日综述 ----
if overview:
    overview_html = html_escape_text(overview).replace("\n", "<br>")
    st.markdown(
        f'<div class="overview-box">📢 <strong>今日综述</strong><br><br>{overview_html}</div>',
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
else:
    st.info(
        "💡 未配置 LLM，今日洞察不可用。"
        " **研究雷达、缺口图、假设实验室**等本地智能分析功能无需 LLM，"
        " 可前往 **「研究雷达」** 页面查看跨期选题分析。",
        icon=None,
    )

# ---- 智能导读 ----
brief = build_digest_brief(data)
with st.expander("🧠 智能导读（本地规则生成）", expanded=not bool(insights)):
    st.markdown(brief["narrative"])
    b1, b2, b3 = st.columns(3)
    b1.metric("平均引用", brief["avg_citations"])
    b2.metric("顶级期刊/来源", brief["top_tier_count"])
    b3.metric("来源数", len(brief["source_mix"]))

    if brief["topic_terms"]:
        st.markdown("**本期关键词信号**")
        st.dataframe(
            [{"主题": item["term"], "强度": item["score"], "示例论文": item.get("example", "")} for item in brief["topic_terms"][:6]],
            use_container_width=True,
            hide_index=True,
        )

    if brief["reading_path"]:
        st.markdown("**推荐阅读路径**")
        for item in brief["reading_path"]:
            link = safe_url(item.get("doi_url")) or safe_url(item.get("openalex_url"))
            title = item["title"]
            if link:
                st.markdown(f"- **{item['role']}**：[{title}]({link}) — {item['reason']}")
            else:
                st.markdown(f"- **{item['role']}**：{title} — {item['reason']}")

# ---- 筛选控件 ----
st.markdown("### 📋 文献列表")
col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1, 1, 1])
with col_f1:
    search_kw = st.text_input("🔍 搜索标题/摘要关键词", placeholder="例如：inflation、machine learning")
with col_f2:
    source_filter = st.multiselect(
        "来源筛选",
        options=["arxiv", "openalex", "semantic_scholar", "nber", "ssrn"],
        default=[],
        placeholder="全部来源",
    )
with col_f3:
    top_tier_only = st.checkbox("🏆 仅显示顶级期刊", value=False)
with col_f4:
    sort_by_relevance = st.checkbox(
        "🎯 按相关性排序",
        value=False,
        help="填写侧边栏「我的研究偏好」后生效；有 LLM API 时使用语义评分，否则使用关键词相似度",
    )

# ---- 辅助函数 ----
def _contains_chinese_in_abstract(text: str) -> bool:
    import re
    return bool(re.search(r"[\u4e00-\u9fff]", text))


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
    source_label = {"arxiv": "arXiv", "openalex": "OpenAlex", "semantic_scholar": "Semantic Scholar", "nber": "NBER", "ssrn": "SSRN"}.get(source, source)
    tier_tag = " 🏆 Top Tier" if is_top_tier(venue) else ""
    relevance = p.get("relevance_score", -1)
    relevance_str = f"  |  **相关性：** {relevance}/100" if relevance >= 0 else ""

    link = doi_url or openalex_url or ""
    title_md = f"[{title}]({link})" if link else title

    lines = [
        f"### {idx}. {title_md}",
        f"**来源：** {source_label}{tier_tag}  |  **期刊：** {venue}  |  **发表：** {pub_date}  |  **引用：** {cited}{relevance_str}",
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
        labels = {"themes": "主题趋势", "methods": "方法趋势", "implications": "启示与应用", "watchlist": "后续观察"}
        for key, label in labels.items():
            val = insights.get(key, "")
            if val:
                lines.append(f"**{label}：** {val}")
        lines.append("")
    lines += ["## 文献列表", ""]
    for idx, p in enumerate(papers, 1):
        lines.append(paper_to_markdown(idx, p))
    return "\n".join(lines)


# ---- 个性化相关性评分 ----
user_preference = st.session_state.get("user_preference", "").strip()
pref_api_base = st.session_state.get("preference_llm_api_base", "").strip()
pref_api_key = st.session_state.get("preference_llm_api_key", "").strip()
pref_model = st.session_state.get("preference_llm_model", "gpt-4o-mini").strip()

# 缓存键：偏好 + 日期 + 论文数量，避免重复调用
_cache_key = f"relevance_{selected_date}_{user_preference[:50]}_{len(papers)}"

if sort_by_relevance and user_preference and papers:
    has_llm = bool(pref_api_key and pref_api_base)

    if _cache_key not in st.session_state:
        if has_llm:
            # LLM 语义评分
            with st.spinner(f"🎯 正在为 {len(papers)} 篇论文评估与「{user_preference[:30]}...」的相关性，请稍候..."):
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
                    st.success(f"✅ LLM 相关性评分完成，已按与「{user_preference[:30]}」的相关性排序。")
                except Exception as e:
                    st.error(f"❌ LLM 相关性评分失败：{e}")
                    st.session_state[_cache_key] = None
        else:
            # 本地 TF-IDF / 关键词相似度评分（无需 API）
            import copy
            from src.summarization import score_papers_by_preference_local
            papers_copy = copy.deepcopy(papers)
            papers_copy = score_papers_by_preference_local(papers_copy, user_preference)
            st.session_state[_cache_key] = papers_copy
            st.info(f"🎯 已使用本地关键词相似度评分（偏好：「{user_preference[:40]}」）。如需语义评分，请在侧边栏配置 LLM API。")
    else:
        if st.session_state[_cache_key] is not None:
            mode = "LLM 语义" if has_llm else "本地关键词"
            st.info(f"🎯 已使用缓存的{mode}评分结果（偏好：「{user_preference[:40]}」）")

    # 使用评分后的论文列表
    if _cache_key in st.session_state and st.session_state[_cache_key] is not None:
        papers = st.session_state[_cache_key]
        papers = sorted(papers, key=lambda p: p.get("relevance_score", -1), reverse=True)

elif sort_by_relevance and not user_preference:
    st.warning("⚠️ 请先在左侧侧边栏填写「我的研究偏好」，然后再开启相关性排序。")

# ---- 过滤论文 ----
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
if top_tier_only:
    filtered_papers = [p for p in filtered_papers if is_top_tier(p.get("venue", ""))]

# ---- 导出全期日报按钮 ----
if papers:
    full_md = digest_to_markdown(date_str, papers, overview, insights)
    col_export1, col_export2, _ = st.columns([1, 1, 4])
    with col_export1:
        st.download_button(
            label="⬇️ 导出全期日报 (Markdown)",
            data=full_md,
            file_name=f"finance_digest_{date_str}.md",
            mime="text/markdown",
            help="将本期所有文献导出为 Markdown 文件，可直接粘贴到 Notion、Obsidian 等笔记软件",
        )

# ---- 论文卡片展示 ----
BADGE_CLASS = {
    "arxiv": "badge-arxiv",
    "openalex": "badge-openalex",
    "semantic_scholar": "badge-semantic_scholar",
    "nber": "badge-nber",
    "ssrn": "badge-ssrn",
}
SOURCE_LABEL = {
    "arxiv": "arXiv",
    "openalex": "OpenAlex",
    "semantic_scholar": "Semantic Scholar",
    "nber": "NBER",
    "ssrn": "SSRN",
}

if not filtered_papers:
    st.info("没有符合条件的文献。")
else:
    sort_label = "（按相关性排序）" if sort_by_relevance and user_preference else ""
    st.caption(f"共显示 {len(filtered_papers)} / {count} 篇文献{sort_label}")

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
        doi_safe = safe_url(doi_url)
        openalex_safe = safe_url(openalex_url)
        if doi_safe:
            links_html += f'<a href="{doi_safe}" target="_blank" rel="noopener">DOI</a> '
        if openalex_safe:
            links_html += f'<a href="{openalex_safe}" target="_blank" rel="noopener">原文链接</a>'

        topics = p.get("topics") or []
        topics_str = " · ".join(topics[:5]) if topics else "N/A"

        summary_raw = p.get("summary_zh", "")
        abstract_raw = p.get("abstract", "")

        # Detect whether the summary is a structured LLM output or local fallback
        is_structured = summary_raw and any(
            label in summary_raw for label in ["📌 研究问题", "🔬 研究方法", "📊 核心发现", "💡 应用价值"]
        )
        is_local_fallback = summary_raw and not is_structured and not _contains_chinese_in_abstract(abstract_raw)

        summary_html = format_summary_html(summary_raw) if summary_raw else ""

        venue = p.get("venue", "N/A")
        pub_date = p.get("published_date", "N/A") or "N/A"
        cited = p.get("cited_by_count", 0)
        title_html = html_escape_text(p.get("title", "无标题"))
        venue_html = html_escape_text(venue)
        pub_date_html = html_escape_text(pub_date)
        cited_html = html_escape_text(cited)
        authors_html = html_escape_text(authors_str)
        topics_html = html_escape_text(topics_str)
        src_label_html = html_escape_text(src_label)

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
            <div class="relevance-bar-wrap">
                <span class="relevance-label">🎯 相关性</span>
                <div class="relevance-bar-bg">
                    <div class="relevance-bar-fill" style="width:{bar_width}%; background:{bar_color};"></div>
                </div>
                <span class="relevance-score-num">{relevance_score}/100</span>
            </div>
            """

        # 摘要展示：本地降级时补充说明
        fallback_note = ""
        if is_local_fallback:
            fallback_note = '<div style="font-size:0.78rem;color:#888;margin-bottom:4px;">📝 本地信号提取（无 LLM，建议查阅原文摘要）</div>'

        st.markdown(
            f"""
            <div class="paper-card">
              <div class="paper-title">{idx}. {title_html}</div>
              <div class="paper-meta">
                <span class="source-badge {badge_cls}">{src_label_html}</span>
                {top_tier_badge}
                <strong>期刊/来源：</strong>{venue_html}
                &nbsp;|&nbsp; <strong>发表：</strong>{pub_date_html}
                &nbsp;|&nbsp; <strong>引用数：</strong>{cited_html}
              </div>
              <div class="paper-meta"><strong>作者：</strong>{authors_html}</div>
              <div class="paper-meta"><strong>主题：</strong>{topics_html}</div>
              {relevance_html}
              <div class="paper-meta">{links_html}</div>
              {fallback_note}
              <div class="summary-box">{summary_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 原文摘要展开（仅当有摘要且非结构化中文摘要时显示）
        if abstract_raw and not is_structured:
            with st.expander("📄 原文摘要（英文）", expanded=False):
                st.caption(abstract_raw)

        paper_md = paper_to_markdown(idx, p)
        btn_col1, btn_col2, _ = st.columns([1, 1, 4])
        with btn_col1:
            st.download_button(
                label="📋 复制此篇 (Markdown)",
                data=paper_md,
                file_name=f"paper_{idx}_{date_str}.md",
                mime="text/markdown",
                key=f"copy_{idx}_{date_str}",
                help="下载此篇论文的 Markdown 格式摘要",
            )
        with btn_col2:
            try:
                from utils.bookmarks import add_bookmark, is_bookmarked
                authors_list = p.get("authors") or []
                paper_for_bm = {
                    "title": p.get("title", ""),
                    "authors": ", ".join(authors_list),
                    "venue": p.get("venue", ""),
                    "published_date": p.get("published_date", ""),
                    "doi_url": p.get("doi_url", ""),
                    "openalex_url": p.get("openalex_url", ""),
                    "cited_by_count": p.get("cited_by_count", 0),
                    "abstract": p.get("abstract", ""),
                    "summary_zh": p.get("summary_zh", ""),
                    "source": p.get("source", ""),
                    "digest_date": date_str,
                }
                already = is_bookmarked(paper_for_bm)
                bm_label = "✅ 已收藏" if already else "⭐ 收藏"
                if st.button(bm_label, key=f"bm_{idx}_{date_str}", help="收藏此论文到「我的收藏」"):
                    if not already:
                        add_bookmark(paper_for_bm)
                        st.success("已添加到收藏夹！")
                        st.rerun()
                    else:
                        st.info("该论文已在收藏夹中。")
            except Exception:
                pass
