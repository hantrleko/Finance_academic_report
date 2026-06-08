# Finance & Economics Daily Digest

[![Version](https://img.shields.io/badge/version-v1.6-blue)](https://github.com/hantrleko/Finance_academic_report/releases)
[![Tests](https://img.shields.io/badge/tests-42%20passed-brightgreen)](https://github.com/hantrleko/Finance_academic_report/actions)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

每日自动抓取公开金融/经济学文献，生成结构化日报，并通过 **Streamlit** 在线网站进行交互式展示。

## 功能特性

- **多源抓取：** OpenAlex + arXiv + Semantic Scholar + NBER + SSRN
- **智能过滤：** 关键词白名单/黑名单 + 引用数加分 + 顶级期刊加分 + 质量分门槛 + arXiv/NBER 基础过滤
- **AI 摘要：** 双模型架构（翻译模型 + 分析模型），支持结构化中文摘要
- **LLM 洞察：** 每日主题趋势、方法趋势、应用启示、后续观察
- **研究雷达：** 无需外部 LLM，基于历史 digest 自动发现上升主题、方法/领域信号、来源结构和推荐关注论文
- **智能导读：** 今日速递内置本地规则生成的关键词信号、阅读路径、引用/来源/顶刊概览
- **质量保障：** 空结果保留 `output/latest`，异常写入 `output/alerts/`，digest JSON 结构校验，损坏文件友好提示
- **高可靠性：** LLM 调用指数退避重试、S2 限流自动重试、JSON 解析三级容错
- **自动化：** GitHub Actions 每天定时运行并提交 `output/` 结果（含 pip 缓存加速）
- **在线展示：** Streamlit 多页面网站，支持可点击导航、搜索、筛选、统计可视化、研究雷达、DuckDB 跨期知识库搜索和收藏夹导出

## 快速开始

### 本地运行 Streamlit 网站

```bash
pip install -r requirements.txt
streamlit run app.py
```

访问 `http://localhost:8501` 即可查看网站。

### 配置 API Key（可选）

复制 `.streamlit/secrets.toml.example` 为 `.streamlit/secrets.toml`，填入你的 API Key：

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# 编辑 .streamlit/secrets.toml，填入真实的 API Key
```

### 手动触发文献抓取

```bash
python -m src.digest
```

或在 Streamlit 网站的「⚙️ 手动抓取」页面中操作。

### 运行测试

```bash
pytest -v
```

## 部署到 Streamlit Cloud

1. Fork 本仓库到你的 GitHub 账号
2. 前往 [streamlit.io/cloud](https://streamlit.io/cloud) 创建新应用
3. 选择仓库，主文件设置为 `app.py`
4. 在 Streamlit Cloud 的 **App Settings → Secrets** 中，将 `.streamlit/secrets.toml.example` 的内容粘贴进去并填入真实值

## 页面说明

| 页面 | 功能 |
|------|------|
| 🏠 今日速递 | 最新一期文献日报，含 AI 综述、洞察和论文卡片 |
| 📅 历史档案 | 按日期浏览所有历史期刊 |
| 📈 数据统计 | 来源分布、主题分布、引用数等可视化统计 |
| ⚙️ 手动抓取 | 手动触发抓取，支持自定义参数和 LLM 配置 |
| 📚 知识库搜索 | 基于 DuckDB 跨期检索历史文献，支持多条件筛选和 Markdown 导出 |
| ⭐ 我的收藏 | 管理收藏论文，支持 BibTeX / Markdown 导出 |
| 🧭 研究雷达 | 从历史 digest 提炼上升主题、方法/领域信号、来源结构和推荐关注论文 |

## 数据质量与安全

- 前端对来自外部数据源的标题、作者、期刊、摘要和链接进行 HTML 转义与 URL 白名单校验，避免外部元数据破坏页面结构。
- `src/schema.py` 会标准化并校验 digest JSON，页面加载时会对异常字段给出提示。
- `src/intelligence.py` 只使用本地元数据生成研究雷达和智能导读，不额外发送论文标题/摘要到第三方服务。
- 测试套件会扫描 `output/*/digest.json`，确保提交的历史数据不含 Git 冲突标记、JSON 可解析且 source 字段合法。

## 环境变量

### 抓取与筛选

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DIGEST_MAX_PAPERS` | 每期最多论文数 | 12 |
| `DIGEST_SOURCE_MIN_PAPERS` | 多源保底篇数 | 2 |
| `DIGEST_SOURCE_MAX_SHARE` | 单一来源最大占比 | 0.6 |
| `DIGEST_MIN_CITATIONS` | 最小引用门槛 | 0 |
| `DIGEST_OUTPUT_DIR` | 输出目录 | output |
| `DIGEST_KEEP_LATEST_WHEN_EMPTY` | 空结果是否保留 latest | 1 |
| `DIGEST_LOOKBACK_DAYS` | 回溯天数 | 7 |
| `DIGEST_TOPIC_WHITELIST` | 关键词白名单（逗号分隔） | — |
| `DIGEST_TOPIC_BLACKLIST` | 关键词黑名单（逗号分隔） | — |
| `DIGEST_MIN_QUALITY_SCORE` | 最低质量分 | 2 |
| `OPENALEX_MAILTO` | OpenAlex/Crossref 联系邮箱 | — |

### LLM（可选）

推荐双模型配置：
- **翻译模型**（如 SiliconFlow）：负责英文摘要到中文的高质量翻译
- **分析模型**（如 GLM / GPT-4o）：负责文献筛选、结构化摘要与"今日洞察"

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_API_BASE` | 翻译模型 API 地址 | https://api.siliconflow.cn/v1 |
| `LLM_API_KEY` | 翻译模型 API Key | — |
| `LLM_MODEL` | 翻译模型名称 | tencent/Hunyuan-MT-7B |
| `ANALYSIS_LLM_API_BASE` | 分析模型 API 地址 | https://open.bigmodel.cn/api/paas/v4 |
| `ANALYSIS_LLM_API_KEY` | 分析模型 API Key | — |
| `ANALYSIS_LLM_MODEL` | 分析模型名称 | glm-4.7-flash |
| `S2_API_KEY` | Semantic Scholar API Key | — |
| `S2_MIN_INTERVAL_SECONDS` | S2 请求间隔（秒） | 1.5 |

### 本地依赖说明

「📚 知识库搜索」页面使用 DuckDB 构建内存索引；请确保已通过 `pip install -r requirements.txt` 安装 `duckdb`。

> **提示：** 本地开发时可将上述变量写入 `.streamlit/secrets.toml`（参考 `.streamlit/secrets.toml.example`）；Streamlit Cloud 部署时在 App Settings → Secrets 中配置。

## 项目结构

```
Finance_academic_report/
├── app.py                          # Streamlit 主入口（含版本号与更新日志）
├── pages/
│   ├── 1_今日速递.py               # 今日速递页面
│   ├── 2_历史档案.py               # 历史档案页面
│   ├── 3_数据统计.py               # 数据统计页面
│   ├── 4_手动抓取.py               # 手动抓取页面
│   ├── 5_知识库搜索.py             # DuckDB 跨期知识库搜索
│   ├── 6_我的收藏.py               # 收藏夹管理与导出
│   └── 7_研究雷达.py               # 上升主题、方法信号与推荐阅读路径
├── utils/
│   ├── data_loader.py              # 数据加载工具（含缓存、标准化与容错）
│   ├── bookmarks.py                # 收藏夹读写与 BibTeX 导出
│   └── safety.py                   # 前端 HTML/URL 安全渲染工具
├── src/
│   ├── config.py                   # 配置加载（支持 dict 直接构建）
│   ├── models.py                   # 数据模型与常量（含期刊白/黑名单）
│   ├── sources.py                  # 数据源抓取（含 S2 重试、NBER 修复）
│   ├── filtering.py                # 质量过滤（含 safe_load_digest_json）
│   ├── summarization.py            # LLM 摘要生成（含指数退避重试）
│   ├── pipeline.py                 # 主流程编排
│   ├── rendering.py                # HTML/Markdown 渲染
│   ├── schema.py                   # digest JSON 标准化与结构校验
│   ├── intelligence.py             # 本地研究雷达与智能导读
│   └── digest.py                   # CLI 入口
├── output/                         # 自动生成的日报数据
│   ├── latest/                     # 最新一期
│   ├── YYYY-MM-DD/                 # 历史日期
│   └── alerts/                     # 空结果告警
├── tests/                          # 单元测试与数据健康检查（42 个用例）
├── .github/workflows/              # GitHub Actions 定时任务
├── .streamlit/
│   ├── config.toml                 # Streamlit 主题配置
│   └── secrets.toml.example        # API Key 配置模板
└── requirements.txt
```

## 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| v1.6 | 2026-06-08 | 新增研究雷达与智能导读：本地提炼上升主题、方法/领域信号、来源结构和推荐关注论文；测试扩充至 42 个 |
| v1.5 | 2026-05-02 | 新增 DuckDB 知识库搜索、SSRN 数据源、收藏夹与导出功能；修复自动化兼容、依赖和历史数据一致性 |
| v1.4 | 2026-05-01 | 扩充期刊黑名单、优化手动抓取关键词配置和统计页面 |
| v1.3 | 2026-04-30 | 新增研究偏好、AI 个性化相关性评分和跨页面偏好共享 |
| v1.2 | 2026-04-30 | 新增跨期去重、顶级期刊打标和 Markdown 导出 |
| v1.1 | 2026-04-28 | 版本标识、空数据保护、HTML 实体解码、arXiv 过滤、Prompt 约束、测试扩充 |
| v1.0 | 2026-04-24 | Streamlit 重构、移除邮件推送、overview Bug 修复、LLM 重试、线程安全修复 |
