"""Finance Academic Digest - Streamlit 主入口"""
import streamlit as st

st.set_page_config(
    page_title="金融经济学每日文献速递",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- 侧边栏导航 ----
st.sidebar.title("📊 金融文献速递")
st.sidebar.markdown("---")

pages = {
    "🏠 今日速递": "pages/1_今日速递.py",
    "📅 历史档案": "pages/2_历史档案.py",
    "📈 数据统计": "pages/3_数据统计.py",
    "⚙️ 手动抓取": "pages/4_手动抓取.py",
}

st.sidebar.markdown("### 导航")
for name in pages:
    st.sidebar.markdown(f"- {name}")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**数据来源**\n\n"
    "- [OpenAlex](https://openalex.org)\n"
    "- [arXiv](https://arxiv.org)\n"
    "- [Semantic Scholar](https://www.semanticscholar.org)\n"
    "- [NBER](https://www.nber.org)\n"
)
st.sidebar.markdown("---")
st.sidebar.caption("由 GitHub Actions 每日自动更新")

# ---- 主页内容（重定向提示）----
st.title("📊 金融经济学每日文献速递")
st.markdown(
    """
    欢迎使用金融经济学每日文献速递系统。本系统每日自动从多个学术数据库抓取最新金融与经济学文献，
    经过质量筛选和 AI 摘要生成后，以结构化方式呈现。

    **请通过左侧导航栏选择页面：**

    | 页面 | 功能 |
    |------|------|
    | 🏠 今日速递 | 查看最新一期文献速递，含 AI 综述与洞察 |
    | 📅 历史档案 | 按日期浏览历史期刊 |
    | 📈 数据统计 | 文献来源、主题分布等可视化统计 |
    | ⚙️ 手动抓取 | 手动触发文献抓取（需配置 API Key） |
    """
)
