"""页面：数据统计 - 文献来源、主题分布等可视化统计"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import get_available_dates, load_all_digests

st.set_page_config(
    page_title="数据统计 | 金融文献速递",
    page_icon="📈",
    layout="wide",
)

st.title("📈 数据统计")
st.markdown("基于所有历史期刊数据的综合统计分析。")

# ---- 加载数据 ----
with st.spinner("正在加载历史数据..."):
    all_digests = load_all_digests()

if not all_digests:
    st.warning("暂无历史数据，请等待 GitHub Actions 自动更新。")
    st.stop()

# 展平所有论文
all_papers = []
daily_counts = []
for digest in all_digests:
    papers = digest.get("papers", [])
    all_papers.extend(papers)
    daily_counts.append({"date": digest.get("date", ""), "count": digest.get("count", 0)})

total_papers = len(all_papers)
total_days = len(all_digests)
avg_per_day = round(total_papers / total_days, 1) if total_days > 0 else 0

# ---- 顶部总览 ----
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("📄 累计文献数", total_papers)
c2.metric("📅 覆盖天数", total_days)
c3.metric("📊 日均文献数", avg_per_day)
c4.metric("⚠️ 空结果天数", sum(1 for d in all_digests if d.get("count", 0) == 0))

st.markdown("---")

# ---- 图表区 ----
tab1, tab2, tab3, tab4 = st.tabs(["📅 每日文献数量", "🌐 来源分布", "🏷️ 主题分布", "📚 期刊分布"])

# Tab 1: 每日文献数量趋势
with tab1:
    st.subheader("每日文献数量趋势")
    if daily_counts:
        daily_counts_sorted = sorted(daily_counts, key=lambda x: x["date"])
        dates = [d["date"] for d in daily_counts_sorted]
        counts = [d["count"] for d in daily_counts_sorted]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=counts,
            mode="lines+markers",
            name="文献数量",
            line=dict(color="#1a56db", width=2),
            marker=dict(size=5),
            fill="tozeroy",
            fillcolor="rgba(26, 86, 219, 0.08)",
        ))
        fig.update_layout(
            xaxis_title="日期",
            yaxis_title="文献数量",
            hovermode="x unified",
            height=380,
            margin=dict(l=40, r=20, t=20, b=40),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
        fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
        st.plotly_chart(fig, use_container_width=True)

        # 统计摘要
        non_zero = [c for c in counts if c > 0]
        if non_zero:
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("最高单日", max(non_zero))
            col_b.metric("最低单日（非零）", min(non_zero))
            col_c.metric("有效天数", len(non_zero))

# Tab 2: 来源分布
with tab2:
    st.subheader("文献来源分布")
    source_counter = Counter(p.get("source", "unknown") for p in all_papers)
    source_labels = {
        "arxiv": "arXiv",
        "openalex": "OpenAlex",
        "semantic_scholar": "Semantic Scholar",
        "nber": "NBER",
    }
    sources = list(source_counter.keys())
    source_display = [source_labels.get(s, s) for s in sources]
    source_values = [source_counter[s] for s in sources]

    col_pie, col_bar = st.columns(2)
    with col_pie:
        fig_pie = px.pie(
            names=source_display,
            values=source_values,
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        fig_bar = px.bar(
            x=source_display,
            y=source_values,
            color=source_display,
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"x": "来源", "y": "文献数量"},
        )
        fig_bar.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=40, r=20, t=20, b=40),
            plot_bgcolor="white",
        )
        fig_bar.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
        st.plotly_chart(fig_bar, use_container_width=True)

    # 数据表格
    st.markdown("**来源统计详情**")
    source_table = [
        {"来源": source_labels.get(s, s), "文献数量": c, "占比": f"{c/total_papers*100:.1f}%"}
        for s, c in sorted(source_counter.items(), key=lambda x: -x[1])
    ]
    st.dataframe(source_table, use_container_width=True, hide_index=True)

# Tab 3: 主题分布
with tab3:
    st.subheader("文献主题分布（Top 20）")
    topic_counter: Counter = Counter()
    for p in all_papers:
        for t in (p.get("topics") or []):
            topic_counter[t] += 1

    top_topics = topic_counter.most_common(20)
    if top_topics:
        topic_names = [t[0] for t in top_topics]
        topic_counts = [t[1] for t in top_topics]

        fig_topics = px.bar(
            x=topic_counts[::-1],
            y=topic_names[::-1],
            orientation="h",
            color=topic_counts[::-1],
            color_continuous_scale="Blues",
            labels={"x": "文献数量", "y": "主题"},
        )
        fig_topics.update_layout(
            height=520,
            margin=dict(l=20, r=20, t=20, b=40),
            plot_bgcolor="white",
            coloraxis_showscale=False,
        )
        fig_topics.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
        st.plotly_chart(fig_topics, use_container_width=True)
    else:
        st.info("暂无主题数据。")

# Tab 4: 期刊分布
with tab4:
    st.subheader("文献期刊/来源分布（Top 20）")
    venue_counter: Counter = Counter()
    for p in all_papers:
        venue = (p.get("venue") or "").strip()
        if venue and venue.lower() not in ("n/a", "", "arxiv"):
            venue_counter[venue] += 1

    top_venues = venue_counter.most_common(20)
    if top_venues:
        venue_names = [v[0] for v in top_venues]
        venue_counts = [v[1] for v in top_venues]

        fig_venues = px.bar(
            x=venue_counts[::-1],
            y=venue_names[::-1],
            orientation="h",
            color=venue_counts[::-1],
            color_continuous_scale="Greens",
            labels={"x": "文献数量", "y": "期刊/来源"},
        )
        fig_venues.update_layout(
            height=560,
            margin=dict(l=20, r=20, t=20, b=40),
            plot_bgcolor="white",
            coloraxis_showscale=False,
        )
        fig_venues.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
        st.plotly_chart(fig_venues, use_container_width=True)
    else:
        st.info("暂无期刊数据。")

    # 引用数分布
    st.markdown("---")
    st.subheader("引用数分布")
    citation_counts = [p.get("cited_by_count", 0) for p in all_papers if p.get("cited_by_count", 0) > 0]
    if citation_counts:
        fig_hist = px.histogram(
            x=citation_counts,
            nbins=30,
            labels={"x": "引用数", "y": "文献数量"},
            color_discrete_sequence=["#1a56db"],
        )
        fig_hist.update_layout(
            height=320,
            margin=dict(l=40, r=20, t=20, b=40),
            plot_bgcolor="white",
        )
        fig_hist.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
        st.plotly_chart(fig_hist, use_container_width=True)

        col_x, col_y, col_z = st.columns(3)
        col_x.metric("平均引用数", round(sum(citation_counts) / len(citation_counts), 1))
        col_y.metric("最高引用数", max(citation_counts))
        col_z.metric("有引用数文献", len(citation_counts))
    else:
        st.info("暂无引用数数据。")
