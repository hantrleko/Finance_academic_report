"""Finance Academic Digest - Streamlit 主入口"""
import streamlit as st

# ---- 版本信息 ----
APP_VERSION = "v1.2"
APP_VERSION_DATE = "2026-04-30"

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
st.sidebar.caption(f"由 GitHub Actions 每日自动更新\n\n版本：{APP_VERSION}（{APP_VERSION_DATE}）")

# ---- 主页内容 ----
st.title("📊 金融经济学每日文献速递")
st.markdown(
    """
    欢迎使用金融经济学每日文献速递系统。本系统每日自动从多个学术数据库抓取最新金融与经济学文献，
    经过质量筛选和 AI 摘要生成后，以结构化方式呈现。

    **请通过左侧导航栏选择页面：**

    | 页面 | 功能 |
    |------|------|
    | 🏠 今日速递 | 查看最新一期文献速递，含 AI 综述与洞察、顶级期刊打标、一键导出 |
    | 📅 历史档案 | 按日期浏览历史期刊，支持导出和复制 |
    | 📈 数据统计 | 文献来源、主题分布等可视化统计 |
    | ⚙️ 手动抓取 | 手动触发文献抓取（需配置 API Key） |
    """
)

st.markdown("---")

# ---- 版本更新日志 ----
with st.expander(f"📋 版本更新日志（当前：{APP_VERSION}）", expanded=False):
    st.markdown(
        f"""
        ### {APP_VERSION} — {APP_VERSION_DATE}
        **新增 / 优化**
        - 全局跨期去重：抓取时自动过滤过去 7 天已出现的论文，保证每日日报 100% 新鲜
        - 顶级期刊打标：命中 VENUE_WHITELIST 的论文在卡片上显示 🏆 Top Tier 金色徽章
        - 新增「仅显示顶级期刊」筛选开关，快速聚焦高质量文献
        - 一键导出全期日报为 Markdown 文件（兼容 Notion、Obsidian 等笔记软件）
        - 单篇论文一键下载 Markdown 格式摘要
        - 历史档案页面同步支持以上所有新功能

        ### v1.1 — 2026-04-28
        **新增 / 优化**
        - 统计页面增加空数据保护，全新部署时不再崩溃
        - 期刊名称（Venue）HTML 实体自动解码（如 `&amp;` → `&`）
        - arXiv / NBER 来源引入基础质量过滤，过滤明显不相关预印本
        - LLM 洞察 Prompt 增加英文键名强制约束，防止解析失败
        - 新增 `.streamlit/secrets.toml.example` 部署配置模板
        - 测试用例从 11 个扩充至 23 个，覆盖关键鲁棒性函数

        ### v1.0 — 2026-04-24
        **重构**
        - 完整重构为 Streamlit 多页面网站（今日速递 / 历史档案 / 数据统计 / 手动抓取）
        - 移除邮件推送功能，删除 subscribers.py 及相关 workflow 步骤
        - 修复 `overview` 字段漏写到 `digest.json` 的 Bug
        - 修复手动抓取页面 `os.environ` 全局污染问题
        - LLM 调用增加指数退避重试（最多 3 次，支持 429/502/503）
        - 无摘要论文惩罚分从 -5 调整为 -25，确保被完全过滤
        - 损坏的 `digest.json` 文件在页面上显示友好警告而非白屏
        - 引入顶级期刊白名单加分（+5）和引用数加分（最高 +5）
        - 修复 NBER 作者提取和日期回退逻辑
        - 为 `data_loader.py` 添加 `@st.cache_data` 缓存
        """
    )
