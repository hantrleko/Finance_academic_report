# Finance & Economics Daily Digest

每日自动抓取公开金融/经济学文献，生成结构化日报，并通过 **Streamlit** 在线网站进行交互式展示。

## 功能特性

- **多源抓取：** OpenAlex + arXiv + Semantic Scholar + NBER
- **智能过滤：** 关键词白名单/黑名单 + 引用数加分 + 顶级期刊加分 + 质量分门槛
- **AI 摘要：** 双模型架构（翻译模型 + 分析模型），支持结构化中文摘要
- **LLM 洞察：** 每日主题趋势、方法趋势、应用启示、后续观察
- **质量保障：** 空结果保留 `output/latest`，异常写入 `output/alerts/`
- **自动化：** GitHub Actions 每天定时运行并提交 `output/` 结果
- **在线展示：** Streamlit 多页面网站，支持搜索、筛选、统计可视化

## 快速开始

### 本地运行 Streamlit 网站

```bash
pip install -r requirements.txt
streamlit run app.py
```

访问 `http://localhost:8501` 即可查看网站。

### 手动触发文献抓取

```bash
python -m src.digest
```

或在 Streamlit 网站的「⚙️ 手动抓取」页面中操作。

## 部署到 Streamlit Cloud

1. Fork 本仓库到你的 GitHub 账号
2. 前往 [streamlit.io/cloud](https://streamlit.io/cloud) 创建新应用
3. 选择仓库，主文件设置为 `app.py`
4. 在 Streamlit Cloud 的 Secrets 中配置环境变量（可选）

## 页面说明

| 页面 | 功能 |
|------|------|
| 🏠 今日速递 | 最新一期文献日报，含 AI 综述、洞察和论文卡片 |
| 📅 历史档案 | 按日期浏览所有历史期刊 |
| 📈 数据统计 | 来源分布、主题分布、引用数等可视化统计 |
| ⚙️ 手动抓取 | 手动触发抓取，支持自定义参数和 LLM 配置 |

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
- **翻译模型**（SiliconFlow）：负责英文摘要到中文的高质量翻译
- **分析模型**（GLM）：负责文献筛选、结构化摘要与"今日洞察"

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

## 项目结构

```
Finance_academic_report/
├── app.py                  # Streamlit 主入口
├── pages/
│   ├── 1_今日速递.py        # 今日速递页面
│   ├── 2_历史档案.py        # 历史档案页面
│   ├── 3_数据统计.py        # 数据统计页面
│   └── 4_手动抓取.py        # 手动抓取页面
├── utils/
│   └── data_loader.py      # 数据加载工具
├── src/
│   ├── config.py           # 配置加载
│   ├── models.py           # 数据模型与常量
│   ├── sources.py          # 数据源抓取
│   ├── filtering.py        # 质量过滤
│   ├── summarization.py    # LLM 摘要生成
│   ├── pipeline.py         # 主流程编排
│   ├── rendering.py        # HTML/Markdown 渲染
│   └── digest.py           # CLI 入口
├── output/                 # 自动生成的日报数据
│   ├── latest/             # 最新一期
│   ├── YYYY-MM-DD/         # 历史日期
│   └── alerts/             # 空结果告警
├── tests/                  # 单元测试
├── .github/workflows/      # GitHub Actions
├── .streamlit/config.toml  # Streamlit 主题配置
└── requirements.txt
```
