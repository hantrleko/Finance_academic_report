# Finance & Economics Daily Digest

这个项目会每天自动抓取公开金融/经济学文献，并生成类似 AI Digest 风格的日更内容（JSON + Markdown + HTML）。

## 当前能力

- 多源抓取：OpenAlex + arXiv + Semantic Scholar + NBER
- 中文摘要：规则摘要 + 可选 LLM 增强摘要
- 质量闸门：当日空结果时保留 `output/latest`
- 质量筛选：关键词白名单/黑名单 + 质量分 + 去重
- 告警落盘：空结果写入 `output/alerts/YYYY-MM-DD.json`
- 订阅推送：支持邮箱订阅列表，日报生成后自动群发
- 自动化：GitHub Actions 每天定时运行并提交 `output/` 结果

## 快速开始

```bash
python -m src.digest
```

查看输出：

- `output/latest/digest.md`
- `output/latest/index.html`
- `output/YYYY-MM-DD/digest.json`

## 订阅功能

订阅文件默认在 `data/subscribers.json`。

新增订阅：

```bash
python -m src.digest subscribe --email your_email@example.com
```

也可以不带参数交互填写邮箱：

```bash
python -m src.digest subscribe
```

取消订阅：

```bash
python -m src.digest unsubscribe --email your_email@example.com
```

查看订阅列表：

```bash
python -m src.digest list-subscribers
```

手动发送最新日报给订阅者：

```bash
python -m src.digest send-emails --subscribers-file data/subscribers.json
```

## 环境变量

### 抓取与筛选

- `DIGEST_MAX_PAPERS`：每期最多论文数（默认 12）
- `DIGEST_SOURCE_MIN_PAPERS`：多源保底篇数（默认 2）
- `DIGEST_MIN_CITATIONS`：最小引用门槛（默认 0）
- `DIGEST_OUTPUT_DIR`：输出目录（默认 `output`）
- `DIGEST_KEEP_LATEST_WHEN_EMPTY`：空结果是否保留 latest（`1`/`0`，默认 `1`）
- `DIGEST_LOOKBACK_DAYS`：回溯天数（默认 7）
- `DIGEST_TOPIC_WHITELIST`：关键词白名单（逗号分隔）
- `DIGEST_TOPIC_BLACKLIST`：关键词黑名单（逗号分隔）
- `DIGEST_MIN_QUALITY_SCORE`：最低质量分（默认 2）
- `OPENALEX_MAILTO`：OpenAlex/Crossref 请求的联系邮箱

### LLM（可选）

- `LLM_API_BASE`（默认 `https://api.siliconflow.cn/v1`）
- `LLM_API_KEY`
- `LLM_MODEL`（默认 `tencent/Hunyuan-MT-7B`）
- `LLM_TIMEOUT_SECONDS`（默认 30）
- `ANALYSIS_LLM_API_BASE`（默认 `https://open.bigmodel.cn/api/paas/v4`）
- `ANALYSIS_LLM_API_KEY`
- `ANALYSIS_LLM_MODEL`（默认 `glm-4.7-flash`）
- `ANALYSIS_LLM_TIMEOUT_SECONDS`（默认 60）

推荐双模型配置：

- 翻译模型（SiliconFlow）负责英文摘要到中文的高质量翻译
- 分析模型（GLM）负责文献筛选、结构化摘要与“今日洞察”

GitHub Actions Secrets 示例：

- `LLM_API_KEY=<你的硅基流动 key>`
- `ANALYSIS_LLM_API_KEY=<你的智谱 key>`
- 可选覆盖默认值：
  - `LLM_API_BASE=https://api.siliconflow.cn/v1`
  - `LLM_MODEL=tencent/Hunyuan-MT-7B`
  - `ANALYSIS_LLM_API_BASE=https://open.bigmodel.cn/api/paas/v4`
  - `ANALYSIS_LLM_MODEL=glm-4.7-flash`

Semantic Scholar（可选，建议配置）：

- `S2_API_KEY=<你的 Semantic Scholar API key>`
- `S2_MIN_INTERVAL_SECONDS=1.1`（建议保持 >1.0，满足 1 req/s 限制）

### 邮件推送（SMTP）

- `SMTP_HOST`
- `SMTP_PORT`（可选，默认 587）
- `SMTP_USER`
- `SMTP_PASS`

> 未配置 SMTP 时，发送步骤会自动跳过；建议在 CI 中通过 Secrets 配置。
