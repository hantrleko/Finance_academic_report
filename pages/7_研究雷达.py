"""页面：研究雷达 - 从历史 digest 中提炼上升主题、方法信号与推荐阅读路径。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.express as px
import streamlit as st

from src.intelligence import (
    build_execution_playbook,
    build_gap_map,
    build_hypothesis_lab,
    build_research_radar,
    build_topic_workspace,
    execution_playbook_to_markdown,
    gap_map_to_markdown,
    hypothesis_lab_to_markdown,
    radar_to_markdown,
    topic_workspace_to_markdown,
)
from utils.data_loader import load_all_digests
from utils.safety import html_escape_text, safe_url

st.set_page_config(
    page_title="研究雷达 | 金融文献速递",
    page_icon="🧭",
    layout="wide",
)

st.title("🧭 研究雷达")
st.markdown(
    "从历史日报中自动提炼 **上升主题、方法趋势、来源结构和推荐关注论文**。"
    "该页面不调用外部 LLM，完全基于已提交的 digest 元数据生成，可用于快速制定阅读计划。"
)

with st.spinner("正在加载历史数据并构建研究雷达..."):
    all_digests = load_all_digests()

if not all_digests:
    st.warning("暂无历史数据，请等待自动抓取或先运行手动抓取。")
    st.stop()

col_cfg1, col_cfg2 = st.columns(2)
with col_cfg1:
    recent_issues = st.slider("近期窗口（期数）", min_value=3, max_value=30, value=14, step=1)
with col_cfg2:
    baseline_issues = st.slider("基准窗口（期数）", min_value=7, max_value=90, value=45, step=1)

radar = build_research_radar(all_digests, recent_issues=recent_issues, baseline_issues=baseline_issues)

st.markdown("---")
metric_cols = st.columns(5)
metric_cols[0].metric("覆盖期数", radar["issue_count"])
metric_cols[1].metric("近期窗口", radar["recent_issue_count"])
metric_cols[2].metric("近期论文", radar["recent_paper_count"])
metric_cols[3].metric("基准窗口", radar["baseline_issue_count"])
metric_cols[4].metric("最新日期", radar["latest_date"] or "N/A")

st.caption(
    f"近期窗口：{radar.get('earliest_recent_date') or 'N/A'} → {radar.get('latest_date') or 'N/A'}；"
    "上升主题按近期词频占比相对基准窗口的提升排序。"
)

st.download_button(
    "⬇️ 导出研究雷达 (Markdown)",
    data=radar_to_markdown(radar),
    file_name=f"research_radar_{radar.get('latest_date') or 'latest'}.md",
    mime="text/markdown",
)

st.markdown("---")

tab_topics, tab_methods, tab_sources, tab_papers, tab_gaps, tab_hypotheses, tab_execution, tab_workspace = st.tabs([
    "🚀 上升主题",
    "🔬 方法/领域信号",
    "🌐 来源结构",
    "⭐ 推荐关注论文",
    "🕳️ 缺口地图",
    "🧪 假设实验室",
    "复现执行",
    "🧩 专题工作台",
])

with tab_topics:
    st.subheader("🚀 上升主题雷达")
    emerging = radar.get("emerging_topics", [])
    if emerging:
        fig = px.bar(
            emerging[::-1],
            x="lift",
            y="term",
            orientation="h",
            color="recent_score",
            color_continuous_scale="Blues",
            labels={"lift": "相对基准提升（百分点）", "term": "主题", "recent_score": "近期强度"},
        )
        fig.update_layout(height=520, margin=dict(l=20, r=20, t=20, b=40), plot_bgcolor="white")
        fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(emerging, use_container_width=True, hide_index=True)
    else:
        st.info("当前窗口未检测到显著上升主题。可以调小近期窗口或等待更多数据积累。")

with tab_methods:
    left, right = st.columns(2)
    with left:
        st.subheader("🔬 方法信号")
        method_signals = radar.get("method_signals", [])
        if method_signals:
            st.dataframe(
                [{"方法": item["label"], "论文数": item["count"], "示例": item.get("example", "")} for item in method_signals],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("近期论文中尚未检测到明显方法标签。")
    with right:
        st.subheader("🏷️ 领域信号")
        domain_signals = radar.get("domain_signals", [])
        if domain_signals:
            st.dataframe(
                [{"领域": item["label"], "论文数": item["count"], "示例": item.get("example", "")} for item in domain_signals],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("近期论文中尚未检测到明显领域标签。")

with tab_sources:
    st.subheader("🌐 近期来源结构")
    source_data = radar.get("recent_source_mix", [])
    if source_data:
        col_chart, col_table = st.columns([1, 1])
        with col_chart:
            fig_source = px.pie(
                source_data,
                names="label",
                values="count",
                hole=0.42,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_source.update_traces(textposition="inside", textinfo="percent+label")
            fig_source.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_source, use_container_width=True)
        with col_table:
            st.dataframe(
                [{"来源": item["label"], "篇数": item["count"], "占比": f"{item['share']}%"} for item in source_data],
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("暂无来源数据。")

with tab_papers:
    st.subheader("⭐ 推荐关注论文")
    st.caption("关注度分数综合引用、顶级期刊、来源新鲜度、主题丰富度和发表年份，用于辅助排序，不代表论文质量定论。")
    notable = radar.get("notable_papers", [])
    if notable:
        for idx, paper in enumerate(notable, 1):
            doi_safe = safe_url(paper.get("doi_url", ""))
            openalex_safe = safe_url(paper.get("openalex_url", ""))
            link_html = ""
            if doi_safe:
                link_html += f'<a href="{doi_safe}" target="_blank" rel="noopener">DOI</a> '
            if openalex_safe:
                link_html += f'<a href="{openalex_safe}" target="_blank" rel="noopener">原文链接</a>'
            if not link_html:
                link_html = "N/A"

            st.markdown(
                f"""
                <div style="border:1px solid #dce8ff;border-radius:10px;padding:1rem;margin-bottom:0.8rem;background:#f8faff;">
                  <div style="font-weight:700;color:#1a3a6e;">{idx}. {html_escape_text(paper.get('title'))}</div>
                  <div style="color:#555;font-size:0.9rem;margin-top:0.35rem;">
                    <strong>来源：</strong>{html_escape_text(paper.get('source_label'))}
                    &nbsp;|&nbsp;<strong>期刊/来源：</strong>{html_escape_text(paper.get('venue') or 'N/A')}
                    &nbsp;|&nbsp;<strong>发表：</strong>{html_escape_text(paper.get('published_date') or 'N/A')}
                    &nbsp;|&nbsp;<strong>引用：</strong>{html_escape_text(paper.get('cited_by_count'))}
                    &nbsp;|&nbsp;<strong>关注度：</strong>{html_escape_text(paper.get('attention_score'))}
                  </div>
                  <div style="color:#555;font-size:0.9rem;margin-top:0.35rem;">{link_html}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("暂无可推荐论文。")

with tab_gaps:
    st.subheader("🕳️ 研究缺口地图")
    st.caption("把近期论文映射到「研究领域 × 方法路线」矩阵，发现领域和方法都活跃、但组合尚少的潜在选题。该结果是选题启发，不代表严格学术空白。")
    gap_map = build_gap_map(all_digests, recent_issues=recent_issues)

    g1, g2, g3 = st.columns(3)
    g1.metric("分析期数", gap_map["recent_issue_count"])
    g2.metric("分析论文", gap_map["paper_count"])
    g3.metric("潜在机会", len(gap_map["opportunities"]))

    st.download_button(
        "⬇️ 导出研究缺口地图 (Markdown)",
        data=gap_map_to_markdown(gap_map),
        file_name=f"gap_map_{gap_map.get('latest_date') or 'latest'}.md",
        mime="text/markdown",
        disabled=not gap_map["opportunities"],
    )

    col_domain, col_method = st.columns(2)
    with col_domain:
        st.markdown("**近期活跃领域**")
        if gap_map["domain_counts"]:
            st.dataframe(gap_map["domain_counts"], use_container_width=True, hide_index=True)
        else:
            st.info("未检测到领域信号。")
    with col_method:
        st.markdown("**近期活跃方法**")
        if gap_map["method_counts"]:
            st.dataframe(gap_map["method_counts"], use_container_width=True, hide_index=True)
        else:
            st.info("未检测到方法信号。")

    st.markdown("**领域 × 方法矩阵**")
    matrix_rows = [
        {"领域": item["domain"], "方法": item["method"], "篇数": item["count"], "示例": item.get("example", "")}
        for item in gap_map["matrix"]
    ]
    st.dataframe(matrix_rows, use_container_width=True, hide_index=True)

    st.markdown("**潜在选题机会**")
    if gap_map["opportunities"]:
        for idx, item in enumerate(gap_map["opportunities"], 1):
            st.markdown(
                f"""
                <div style="border:1px solid #f4d7a1;border-radius:10px;padding:1rem;margin-bottom:0.8rem;background:#fffaf0;">
                  <div style="font-weight:700;color:#92400e;">{idx}. {html_escape_text(item['domain'])} × {html_escape_text(item['method'])}</div>
                  <div style="margin-top:0.35rem;"><strong>研究问题：</strong>{html_escape_text(item['question'])}</div>
                  <div style="color:#555;font-size:0.9rem;margin-top:0.35rem;">
                    <strong>证据强度：</strong>领域 {html_escape_text(item['domain_count'])} 篇，方法 {html_escape_text(item['method_count'])} 篇
                  </div>
                  <div style="color:#555;font-size:0.9rem;margin-top:0.35rem;">{html_escape_text(item['data_hint'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("当前窗口内没有发现可提示的领域×方法空白组合。可以扩大近期窗口或等待更多 digest 数据。")

    if gap_map["strong_pairs"]:
        st.markdown("**已有强组合（可作为基准文献路径）**")
        st.dataframe(
            [{"领域": item["domain"], "方法": item["method"], "篇数": item["count"], "示例": item.get("example", "")} for item in gap_map["strong_pairs"]],
            use_container_width=True,
            hide_index=True,
        )

with tab_hypotheses:
    st.subheader("🧪 研究假设实验室")
    st.caption("把缺口地图中的潜在选题进一步转化为可检验假设卡：处理变量、结果变量、机制、识别方案、稳健性和证伪测试。")
    lab = build_hypothesis_lab(all_digests, recent_issues=recent_issues)

    h1, h2, h3 = st.columns(3)
    h1.metric("分析期数", lab["recent_issue_count"])
    h2.metric("分析论文", lab["paper_count"])
    h3.metric("假设卡", len(lab["cards"]))

    st.download_button(
        "⬇️ 导出假设实验室 (Markdown)",
        data=hypothesis_lab_to_markdown(lab),
        file_name=f"hypothesis_lab_{lab.get('latest_date') or 'latest'}.md",
        mime="text/markdown",
        disabled=not lab["cards"],
    )

    if not lab["cards"]:
        st.info("当前窗口尚未形成足够的领域×方法缺口，暂无法生成假设卡。")
    else:
        method_options = sorted({card["method"] for card in lab["cards"]})
        selected_methods = st.multiselect("按方法筛选假设卡", options=method_options, default=[])
        cards = [card for card in lab["cards"] if not selected_methods or card["method"] in selected_methods]
        for card in cards:
            st.markdown(
                f"""
                <div style="border:1px solid #c7d2fe;border-radius:12px;padding:1rem;margin-bottom:1rem;background:#f8faff;">
                  <div style="font-weight:800;color:#3730a3;font-size:1.02rem;">{html_escape_text(card['id'])} · {html_escape_text(card['title'])}</div>
                  <div style="margin-top:0.45rem;"><strong>可检验假设：</strong>{html_escape_text(card['hypothesis'])}</div>
                  <div style="margin-top:0.35rem;"><strong>机制：</strong>{html_escape_text(card['mechanism'])}</div>
                  <div style="color:#555;font-size:0.9rem;margin-top:0.35rem;">
                    <strong>处理变量：</strong>{html_escape_text(card['treatment_variable'])}<br>
                    <strong>结果变量：</strong>{html_escape_text(card['outcome_variable'])}<br>
                    <strong>识别方案：</strong>{html_escape_text(card['identification_plan'])}<br>
                    <strong>优先级：</strong>{html_escape_text(card['priority_score'])}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander(f"{card['id']} 稳健性 / 证伪 / 数据计划", expanded=False):
                st.markdown(f"**数据计划：** {card['data_plan']}")
                st.markdown("**稳健性检查**")
                for item in card["robustness_checks"]:
                    st.markdown(f"- {item}")
                st.markdown("**证伪测试**")
                for item in card["falsification_tests"]:
                    st.markdown(f"- {item}")
                st.markdown(f"**潜在贡献：** {card['contribution']}")

with tab_execution:
    st.subheader("复现执行计划")
    st.caption("把假设卡进一步拆解为可执行研究计划：数据包、里程碑、复现清单、预期产物和风险控制，帮助从选题进入可落地项目管理。")
    playbook = build_execution_playbook(all_digests, recent_issues=recent_issues)

    e1, e2, e3, e4 = st.columns(4)
    e1.metric("分析期数", playbook["recent_issue_count"])
    e2.metric("分析论文", playbook["paper_count"])
    e3.metric("项目计划", playbook["project_count"])
    e4.metric("平均就绪度", playbook["avg_readiness_score"])

    st.download_button(
        "下载复现执行计划 (Markdown)",
        data=execution_playbook_to_markdown(playbook),
        file_name=f"execution_playbook_{playbook.get('latest_date') or 'latest'}.md",
        mime="text/markdown",
        disabled=not playbook["projects"],
    )

    if not playbook["projects"]:
        st.info("当前窗口尚未形成可执行项目计划。可先扩大近期窗口或查看假设实验室是否已有假设卡。")
    else:
        for project in playbook["projects"]:
            st.markdown(
                f"""
                <div style="border:1px solid #bbf7d0;border-radius:12px;padding:1rem;margin-bottom:1rem;background:#f7fff9;">
                  <div style="font-weight:800;color:#166534;font-size:1.02rem;">{html_escape_text(project['id'])} · {html_escape_text(project['title'])}</div>
                  <div style="color:#555;font-size:0.9rem;margin-top:0.35rem;">
                    <strong>对应假设：</strong>{html_escape_text(project['hypothesis_id'])}
                    &nbsp;|&nbsp;<strong>方法：</strong>{html_escape_text(project['method'])}
                    &nbsp;|&nbsp;<strong>就绪度：</strong>{html_escape_text(project['readiness_score'])}
                    &nbsp;|&nbsp;<strong>执行难度：</strong>{html_escape_text(project['difficulty'])}/5
                  </div>
                  <div style="margin-top:0.45rem;"><strong>数据包：</strong>{html_escape_text(project['data_package'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander(f"{project['id']} 里程碑 / 复现清单 / 风险控制", expanded=False):
                st.markdown("**四周里程碑**")
                for milestone in project["milestones"]:
                    st.markdown(f"- **{milestone['week']}：** {milestone['task']}")
                st.markdown("**复现清单**")
                for item in project["reproducibility_checklist"]:
                    st.checkbox(item, value=False, key=f"{project['id']}_{item}")
                st.markdown("**预期产物**")
                for item in project["expected_artifacts"]:
                    st.markdown(f"- {item}")
                st.markdown("**风险控制**")
                for item in project["risk_controls"]:
                    st.markdown(f"- {item}")


with tab_workspace:
    st.subheader("🧩 专题工作台")
    st.caption("输入英文关键词或短语，系统会在历史 digest 中构建一个专题文献综述草稿：时间线、延展词、方法/领域信号和推荐论文。")
    topic_query = st.text_input(
        "专题关键词",
        value="inflation",
        placeholder="例如：inflation、asset pricing、climate risk、machine learning",
        help="建议使用英文关键词；多个词会按 AND 逻辑匹配标题、摘要、主题和摘要字段。",
    ).strip()

    if not topic_query:
        st.info("请输入专题关键词以生成工作台。")
    else:
        workspace = build_topic_workspace(all_digests, topic_query)
        st.markdown(workspace["narrative"])

        w1, w2, w3, w4 = st.columns(4)
        w1.metric("命中文献", workspace["paper_count"])
        w2.metric("首次出现", workspace["first_date"] or "N/A")
        w3.metric("最近出现", workspace["latest_date"] or "N/A")
        w4.metric("相关延展词", len(workspace["related_terms"]))

        st.download_button(
            "⬇️ 导出专题综述草稿 (Markdown)",
            data=topic_workspace_to_markdown(workspace),
            file_name=f"topic_workspace_{topic_query.replace(' ', '_')}.md",
            mime="text/markdown",
            disabled=workspace["paper_count"] == 0,
        )

        if workspace["paper_count"] == 0:
            st.warning("未找到匹配论文。可尝试更短的英文关键词，如 `inflation` 而不是完整句子。")
        else:
            col_timeline, col_terms = st.columns([1, 1])
            with col_timeline:
                st.markdown("**出现时间线**")
                if workspace["timeline"]:
                    fig_timeline = px.line(
                        workspace["timeline"],
                        x="date",
                        y="count",
                        markers=True,
                        labels={"date": "日期", "count": "命中文献数"},
                    )
                    fig_timeline.update_layout(height=320, margin=dict(l=30, r=20, t=20, b=40), plot_bgcolor="white")
                    fig_timeline.update_yaxes(dtick=1, showgrid=True, gridcolor="#f0f0f0")
                    st.plotly_chart(fig_timeline, use_container_width=True)
            with col_terms:
                st.markdown("**相关延展词**")
                if workspace["related_terms"]:
                    st.dataframe(
                        [{"延展词": item["term"], "强度": item["score"], "示例": item.get("example", "")} for item in workspace["related_terms"]],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("暂无足够延展词。")

            st.markdown("**文献综述提纲**")
            for line in workspace["review_outline"]:
                st.markdown(f"- {line}")

            col_method, col_domain = st.columns(2)
            with col_method:
                st.markdown("**方法信号**")
                if workspace["method_signals"]:
                    st.dataframe(
                        [{"方法": item["label"], "论文数": item["count"], "示例": item.get("example", "")} for item in workspace["method_signals"]],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("未检测到明确方法信号。")
            with col_domain:
                st.markdown("**领域信号**")
                if workspace["domain_signals"]:
                    st.dataframe(
                        [{"领域": item["label"], "论文数": item["count"], "示例": item.get("example", "")} for item in workspace["domain_signals"]],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("未检测到明确领域信号。")

            st.markdown("**推荐纳入综述的论文**")
            for idx, paper in enumerate(workspace["top_papers"], 1):
                doi_safe = safe_url(paper.get("doi_url", ""))
                openalex_safe = safe_url(paper.get("openalex_url", ""))
                link_html = ""
                if doi_safe:
                    link_html += f'<a href="{doi_safe}" target="_blank" rel="noopener">DOI</a> '
                if openalex_safe:
                    link_html += f'<a href="{openalex_safe}" target="_blank" rel="noopener">原文链接</a>'
                if not link_html:
                    link_html = "N/A"
                summary_preview = paper.get("summary_zh", "")[:180]
                st.markdown(
                    f"""
                    <div style="border:1px solid #e6e6e6;border-radius:10px;padding:1rem;margin-bottom:0.8rem;background:#ffffff;">
                      <div style="font-weight:700;color:#1a3a6e;">{idx}. {html_escape_text(paper.get('title'))}</div>
                      <div style="color:#555;font-size:0.9rem;margin-top:0.35rem;">
                        <strong>来源：</strong>{html_escape_text(paper.get('source_label'))}
                        &nbsp;|&nbsp;<strong>期刊/来源：</strong>{html_escape_text(paper.get('venue') or 'N/A')}
                        &nbsp;|&nbsp;<strong>引用层级：</strong>{html_escape_text(paper.get('citation_bucket'))}
                        &nbsp;|&nbsp;<strong>关注度：</strong>{html_escape_text(paper.get('attention_score'))}
                      </div>
                      <div style="color:#555;font-size:0.9rem;margin-top:0.35rem;">{html_escape_text(summary_preview)}{'...' if summary_preview else ''}</div>
                      <div style="color:#555;font-size:0.9rem;margin-top:0.35rem;">{link_html}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
