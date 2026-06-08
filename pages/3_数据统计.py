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

# ---- 加载顶级期刊白名单 ----
try:
    from src.models import VENUE_WHITELIST
except ImportError:
    VENUE_WHITELIST = set()

# ---- 展平所有论文，构建每日统计 ----
all_papers = []
daily_stats = []  # [{date, count, top_tier_count}]

for digest in all_digests:
    papers = digest.get("papers", [])
    all_papers.extend(papers)
    top_tier_count = sum(
        1 for p in papers
        if any(wl in (p.get("venue") or "").lower() for wl in VENUE_WHITELIST)
    )
    daily_stats.append({
        "date": digest.get("date", ""),
        "count": digest.get("count", len(papers)),
        "top_tier_count": top_tier_count,
    })

daily_stats_sorted = sorted(daily_stats, key=lambda x: x["date"])
total_papers = len(all_papers)
total_days = len(all_digests)
avg_per_day = round(total_papers / total_days, 1) if total_days > 0 else 0
total_top_tier = sum(d["top_tier_count"] for d in daily_stats)

# ---- 顶部总览 ----
st.markdown("---")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📄 累计文献数", total_papers)
c2.metric("📅 覆盖天数", total_days)
c3.metric("📊 日均文献数", avg_per_day)
c4.metric("🏆 顶级期刊文献", total_top_tier)
c5.metric("⚠️ 空结果天数", sum(1 for d in all_digests if d.get("count", 0) == 0))

st.markdown("---")

# ---- 图表区 ----
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 每日趋势",
    "🏆 顶级期刊趋势",
    "🌐 来源分布",
    "🏷️ 主题分布",
    "📚 期刊分布",
])

# ---- Tab 1: 每日文献数量趋势 ----
with tab1:
    st.subheader("每日文献数量趋势")
    dates = [d["date"] for d in daily_stats_sorted]
    counts = [d["count"] for d in daily_stats_sorted]

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
        hovertemplate="%{x}<br>文献数：%{y} 篇<extra></extra>",
    ))

    # 7 日移动平均线
    if len(counts) >= 7:
        ma7 = []
        for i in range(len(counts)):
            window = counts[max(0, i - 6): i + 1]
            ma7.append(round(sum(window) / len(window), 1))
        fig.add_trace(go.Scatter(
            x=dates,
            y=ma7,
            mode="lines",
            name="7 日均线",
            line=dict(color="#e3a008", width=2, dash="dash"),
            hovertemplate="%{x}<br>7日均线：%{y:.1f} 篇<extra></extra>",
        ))

    fig.update_layout(
        xaxis_title="日期",
        yaxis_title="文献数量",
        hovermode="x unified",
        height=400,
        margin=dict(l=40, r=20, t=20, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
    st.plotly_chart(fig, use_container_width=True)

    non_zero = [c for c in counts if c > 0]
    if non_zero:
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("最高单日", max(non_zero))
        col_b.metric("最低单日（非零）", min(non_zero))
        col_c.metric("有效天数", len(non_zero))
        col_d.metric("7 日均线（最新）", ma7[-1] if len(counts) >= 7 else "N/A")

# ---- Tab 2: 顶级期刊趋势 ----
with tab2:
    st.subheader("🏆 顶级期刊文献占比趋势")
    st.caption("命中 VENUE_WHITELIST（Journal of Finance、AER 等 20 个顶级期刊）的文献占每日总量的百分比。")

    top_tier_counts = [d["top_tier_count"] for d in daily_stats_sorted]
    top_tier_pct = [
        round(d["top_tier_count"] / d["count"] * 100, 1) if d["count"] > 0 else 0
        for d in daily_stats_sorted
    ]

    fig2 = go.Figure()
    # 顶级期刊数量柱状图（背景）
    fig2.add_trace(go.Bar(
        x=dates,
        y=top_tier_counts,
        name="顶级期刊篇数",
        marker_color="rgba(255, 193, 7, 0.5)",
        yaxis="y",
        hovertemplate="%{x}<br>顶级期刊：%{y} 篇<extra></extra>",
    ))
    # 占比折线图（前景）
    fig2.add_trace(go.Scatter(
        x=dates,
        y=top_tier_pct,
        mode="lines+markers",
        name="占比 %",
        line=dict(color="#d03801", width=2),
        marker=dict(size=5),
        yaxis="y2",
        hovertemplate="%{x}<br>占比：%{y:.1f}%<extra></extra>",
    ))

    fig2.update_layout(
        xaxis_title="日期",
        yaxis=dict(title="顶级期刊篇数", showgrid=True, gridcolor="#f0f0f0"),
        yaxis2=dict(title="占比 (%)", overlaying="y", side="right", showgrid=False, range=[0, 100]),
        hovermode="x unified",
        height=400,
        margin=dict(l=40, r=60, t=20, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 顶级期刊命中统计
    top_tier_papers = [
        p for p in all_papers
        if any(wl in (p.get("venue") or "").lower() for wl in VENUE_WHITELIST)
    ]
    if top_tier_papers:
        top_venue_counter = Counter(p.get("venue", "N/A") for p in top_tier_papers)
        st.markdown("**各顶级期刊命中次数（Top 10）**")
        top_venue_data = [
            {"期刊": v, "命中次数": c}
            for v, c in top_venue_counter.most_common(10)
        ]
        st.dataframe(top_venue_data, use_container_width=True, hide_index=True)
    else:
        st.info("暂无顶级期刊文献数据。")

# ---- Tab 3: 来源分布 ----
with tab3:
    st.subheader("文献来源分布")
    source_counter = Counter(p.get("source", "unknown") for p in all_papers)
    source_labels = {
        "arxiv": "arXiv",
        "openalex": "OpenAlex",
        "semantic_scholar": "Semantic Scholar",
        "nber": "NBER",
        "ssrn": "SSRN",
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
        # 各来源平均引用数对比
        source_cited: dict[str, list[int]] = {}
        for p in all_papers:
            s = source_labels.get(p.get("source", "unknown"), p.get("source", "unknown"))
            c = p.get("cited_by_count", 0) or 0
            source_cited.setdefault(s, []).append(c)
        avg_cited_by_source = {
            s: round(sum(v) / len(v), 1) for s, v in source_cited.items() if v
        }
        fig_cited = px.bar(
            x=list(avg_cited_by_source.keys()),
            y=list(avg_cited_by_source.values()),
            color=list(avg_cited_by_source.keys()),
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"x": "来源", "y": "平均引用数"},
            title="各来源平均引用数",
        )
        fig_cited.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=40, r=20, t=40, b=40),
            plot_bgcolor="white",
        )
        fig_cited.update_yaxes(showgrid=True, gridcolor="#f0f0f0")
        st.plotly_chart(fig_cited, use_container_width=True)

    st.markdown("**来源统计详情**")
    source_table = [
        {"来源": source_labels.get(s, s), "文献数量": c, "占比": f"{c/total_papers*100:.1f}%",
         "平均引用数": avg_cited_by_source.get(source_labels.get(s, s), 0)}
        for s, c in sorted(source_counter.items(), key=lambda x: -x[1])
    ]
    st.dataframe(source_table, use_container_width=True, hide_index=True)

# ---- Tab 4: 主题分布 ----
with tab4:
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

# ---- Tab 5: 期刊分布 ----
with tab5:
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

        # 标记顶级期刊
        colors = [
            "#f6ad55" if any(wl in vn.lower() for wl in VENUE_WHITELIST) else "#4299e1"
            for vn in venue_names
        ]

        fig_venues = go.Figure(go.Bar(
            x=venue_counts[::-1],
            y=venue_names[::-1],
            orientation="h",
            marker_color=colors[::-1],
            hovertemplate="%{y}<br>文献数：%{x}<extra></extra>",
        ))
        fig_venues.update_layout(
            height=560,
            margin=dict(l=20, r=20, t=30, b=40),
            plot_bgcolor="white",
            title="🟡 金色 = 顶级期刊，🔵 蓝色 = 普通期刊",
            title_font_size=12,
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
