"""📚 全局跨期知识库搜索页面 —— 使用 DuckDB 内存数据库实现高效全文检索。"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from utils.data_loader import get_available_dates, load_digest, OUTPUT_DIR
from src.models import VENUE_WHITELIST

st.set_page_config(page_title="知识库搜索", page_icon="📚", layout="wide")
st.title("📚 全局知识库搜索")
st.caption("跨越所有历史期刊，精准检索你关心的论文。")


# ─────────────────────────────────────────────
# 1. 构建 DuckDB 内存数据库（带缓存）
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner="正在构建知识库索引，请稍候…")
def build_knowledge_base():
    """将所有历史 digest.json 加载到 DuckDB 内存数据库，返回 connection。"""
    import duckdb

    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE papers (
            digest_date    TEXT,
            title          TEXT,
            authors        TEXT,
            venue          TEXT,
            published_date TEXT,
            doi_url        TEXT,
            cited_by_count INTEGER,
            abstract       TEXT,
            summary_zh     TEXT,
            topics         TEXT,
            source         TEXT,
            is_top_tier    BOOLEAN
        )
    """)

    dates = get_available_dates()
    rows = []
    for date in dates:
        data = load_digest(date)
        if not data or data.get("_error"):
            continue
        for p in data.get("papers", []):
            venue_lower = (p.get("venue") or "").lower()
            is_top = any(w in venue_lower for w in VENUE_WHITELIST)
            rows.append((
                date,
                p.get("title", ""),
                ", ".join(p.get("authors") or []),
                p.get("venue", ""),
                p.get("published_date", ""),
                p.get("doi_url", ""),
                int(p.get("cited_by_count") or 0),
                p.get("abstract", ""),
                p.get("summary_zh", ""),
                ", ".join(p.get("topics") or []),
                p.get("source", ""),
                is_top,
            ))

    if rows:
        con.executemany("INSERT INTO papers VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", rows)

    return con, len(rows)


con, total_papers = build_knowledge_base()

# 统计信息
dates_list = get_available_dates()
col1, col2, col3 = st.columns(3)
col1.metric("📄 论文总数", f"{total_papers:,}")
col2.metric("📅 覆盖期数", f"{len(dates_list)} 期")
col3.metric("🏆 顶级期刊论文", f"{con.execute('SELECT COUNT(*) FROM papers WHERE is_top_tier').fetchone()[0]:,}")

st.markdown("---")

# ─────────────────────────────────────────────
# 2. 搜索与筛选控件
# ─────────────────────────────────────────────
with st.form("search_form"):
    st.subheader("🔍 搜索条件")
    search_col1, search_col2 = st.columns([3, 1])

    with search_col1:
        keyword = st.text_input(
            "关键词（搜索标题、摘要、中文摘要、主题）",
            placeholder="例如：ESG, factor model, monetary policy…",
        )

    with search_col2:
        search_field = st.selectbox(
            "搜索范围",
            ["全文（标题+摘要+主题）", "仅标题", "仅摘要（英文）", "仅中文摘要"],
        )

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

    with filter_col1:
        # 来源筛选
        sources_raw = con.execute("SELECT DISTINCT source FROM papers ORDER BY source").fetchall()
        source_options = ["全部"] + [r[0] for r in sources_raw if r[0]]
        selected_source = st.selectbox("数据来源", source_options)

    with filter_col2:
        # 日期范围
        if dates_list:
            date_min = dates_list[-1]
            date_max = dates_list[0]
        else:
            date_min = date_max = ""
        date_from = st.text_input("起始日期 (YYYY-MM-DD)", value=date_min)
        date_to = st.text_input("截止日期 (YYYY-MM-DD)", value=date_max)

    with filter_col3:
        min_citations = st.number_input("最低引用数", min_value=0, value=0, step=5)
        only_top_tier = st.checkbox("仅显示顶级期刊", value=False)

    with filter_col4:
        sort_by = st.selectbox(
            "排序方式",
            ["发布日期（最新）", "引用数（最高）", "收录日期（最新）"],
        )
        max_results = st.selectbox("最多显示", [20, 50, 100, 200], index=0)

    submitted = st.form_submit_button("🔍 搜索", use_container_width=True, type="primary")

# ─────────────────────────────────────────────
# 3. 执行查询
# ─────────────────────────────────────────────
if submitted or keyword:
    # 构建 WHERE 子句
    conditions = []
    params: list = []

    # 关键词搜索
    if keyword.strip():
        kw = f"%{keyword.strip().lower()}%"
        field_map = {
            "全文（标题+摘要+主题）": "(LOWER(title) LIKE ? OR LOWER(abstract) LIKE ? OR LOWER(summary_zh) LIKE ? OR LOWER(topics) LIKE ?)",
            "仅标题": "LOWER(title) LIKE ?",
            "仅摘要（英文）": "LOWER(abstract) LIKE ?",
            "仅中文摘要": "LOWER(summary_zh) LIKE ?",
        }
        cond = field_map[search_field]
        conditions.append(cond)
        # 参数数量与占位符数量匹配
        param_count = cond.count("?")
        params.extend([kw] * param_count)

    # 来源筛选
    if selected_source != "全部":
        conditions.append("source = ?")
        params.append(selected_source)

    # 日期范围
    if date_from:
        conditions.append("digest_date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("digest_date <= ?")
        params.append(date_to)

    # 引用数
    if min_citations > 0:
        conditions.append("cited_by_count >= ?")
        params.append(min_citations)

    # 顶级期刊
    if only_top_tier:
        conditions.append("is_top_tier = TRUE")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    # 排序
    order_map = {
        "发布日期（最新）": "published_date DESC",
        "引用数（最高）": "cited_by_count DESC",
        "收录日期（最新）": "digest_date DESC",
    }
    order_clause = f"ORDER BY {order_map[sort_by]}"

    sql = f"""
        SELECT title, authors, venue, published_date, digest_date,
               doi_url, cited_by_count, abstract, summary_zh, topics, source, is_top_tier
        FROM papers
        {where_clause}
        {order_clause}
        LIMIT {max_results}
    """

    try:
        rows = con.execute(sql, params).fetchall()
    except Exception as e:
        st.error(f"查询出错：{e}")
        rows = []

    # 统计命中数（不加 LIMIT）
    count_sql = f"SELECT COUNT(*) FROM papers {where_clause}"
    total_hits = con.execute(count_sql, params).fetchone()[0]

    st.markdown("---")
    if not rows:
        st.info("未找到符合条件的论文，请尝试调整搜索关键词或筛选条件。")
    else:
        st.markdown(f"**共找到 {total_hits:,} 篇论文**，显示前 {len(rows)} 篇：")

        # ── 导出按钮 ──
        md_lines = [f"# 知识库搜索结果\n\n**关键词：** {keyword or '（无）'}  \n**共 {total_hits} 篇，显示 {len(rows)} 篇**\n\n---\n"]
        for i, row in enumerate(rows, 1):
            (title, authors, venue, pub_date, dig_date,
             doi_url, cited, abstract, summary_zh, topics, source, is_top) in row
            md_lines.append(f"## {i}. {title}\n")
            md_lines.append(f"**作者：** {authors}  \n**期刊：** {venue}  \n**发表日期：** {pub_date}  \n**引用数：** {cited}\n\n")
            if summary_zh:
                md_lines.append(f"**中文摘要：** {summary_zh}\n\n")
            if doi_url:
                md_lines.append(f"**链接：** {doi_url}\n\n")
            md_lines.append("---\n")

        st.download_button(
            "⬇️ 导出搜索结果 (Markdown)",
            data="\n".join(md_lines),
            file_name=f"search_{keyword or 'all'}_{date_from}_{date_to}.md",
            mime="text/markdown",
        )

        # ── 渲染结果卡片 ──
        for i, row in enumerate(rows):
            (title, authors, venue, pub_date, dig_date,
             doi_url, cited, abstract, summary_zh, topics, source, is_top) in row

            top_badge = " 🏆" if is_top else ""
            source_badge = {"openalex": "🔵", "arxiv": "🟢", "s2": "🟠", "nber": "🔴", "ssrn": "🟣"}.get(source, "⚪")

            with st.expander(f"{source_badge} {title}{top_badge}", expanded=False):
                meta_col1, meta_col2, meta_col3 = st.columns([3, 2, 1])
                with meta_col1:
                    st.markdown(f"**作者：** {authors or '—'}")
                    st.markdown(f"**期刊：** {venue or '—'}")
                with meta_col2:
                    st.markdown(f"**发表日期：** {pub_date or '—'}")
                    st.markdown(f"**收录日期：** {dig_date}")
                with meta_col3:
                    st.markdown(f"**引用数：** {cited:,}")
                    if doi_url:
                        st.markdown(f"[🔗 原文链接]({doi_url})")

                if summary_zh:
                    st.markdown("**中文摘要：**")
                    st.markdown(f"> {summary_zh}")
                elif abstract:
                    st.markdown("**英文摘要（节选）：**")
                    st.markdown(f"> {abstract[:300]}{'…' if len(abstract) > 300 else ''}")

                if topics:
                    st.markdown(f"**主题标签：** `{'` `'.join(topics.split(', ')[:6])}`")

                # 收藏按钮（与收藏夹功能联动）
                paper_id = doi_url or title
                bm_key = f"bm_{i}_{hash(paper_id) % 100000}"
                if st.button("⭐ 收藏此论文", key=bm_key):
                    from utils.bookmarks import add_bookmark
                    add_bookmark({
                        "title": title, "authors": authors, "venue": venue,
                        "published_date": pub_date, "doi_url": doi_url,
                        "cited_by_count": cited, "abstract": abstract,
                        "summary_zh": summary_zh, "source": source,
                    })
                    st.success("已收藏！前往「我的收藏」页面查看。")

else:
    st.info("👆 在上方输入关键词或设置筛选条件后，点击「搜索」按钮开始检索。")
    st.markdown("""
    **使用提示：**
    - 支持英文和中文关键词（中文搜索中文摘要，英文搜索原文摘要和标题）
    - 可组合使用日期范围、来源筛选、引用数门槛进行精准检索
    - 勾选「仅显示顶级期刊」可快速聚焦高质量文献
    - 搜索结果支持一键导出为 Markdown 格式
    """)
