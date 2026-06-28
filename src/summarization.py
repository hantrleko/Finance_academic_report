"""Summarization and LLM post-processing."""
from __future__ import annotations

import json
import re
import time
from urllib.request import Request, urlopen

from .models import LLMConfig, Paper

_METHOD_SIGNALS = {
    # 因果识别
    "difference-in-differences": "双重差分",
    "diff-in-diff": "双重差分",
    "did estimat": "双重差分",
    "regression discontinuity": "断点回归",
    "rd design": "断点回归",
    "fuzzy rdd": "模糊断点回归",
    "instrumental variable": "工具变量",
    "two-stage least": "两阶段最小二乘",
    "2sls": "两阶段最小二乘",
    "natural experiment": "自然实验",
    "synthetic control": "合成控制法",
    "event study": "事件研究",
    "propensity score": "倾向得分匹配",
    "matching estimat": "匹配估计量",
    "causal inference": "因果推断",
    "local average treatment": "局部平均处理效应",
    # 面板与时序
    "panel data": "面板数据",
    "panel regression": "面板回归",
    "fixed effect": "固定效应",
    "random effect": "随机效应",
    "time series": "时间序列",
    "vector autoregression": "向量自回归",
    "var model": "向量自回归",
    "garch": "GARCH 波动率模型",
    "cointegration": "协整分析",
    "error correction": "误差修正模型",
    "local projection": "局部投影法",
    # 横截面与结构
    "cross-section": "横截面分析",
    "regression": "回归分析",
    "structural model": "结构模型",
    "structural estimation": "结构估计",
    "dsge": "DSGE 模型",
    "equilibrium model": "均衡模型",
    "gmm": "广义矩估计",
    "maximum likelihood": "最大似然估计",
    "bayesian": "贝叶斯方法",
    "monte carlo": "蒙特卡洛模拟",
    "simulation": "数值模拟",
    "calibrat": "模型校准",
    # 机器学习/AI
    "machine learning": "机器学习",
    "deep learning": "深度学习",
    "neural network": "神经网络",
    "random forest": "随机森林",
    "xgboost": "XGBoost",
    "gradient boost": "梯度提升",
    "lasso": "LASSO 正则化",
    "ridge regression": "岭回归",
    "principal component": "主成分分析",
    "large language model": "大语言模型",
    "transformer": "Transformer 模型",
    # 文本与情绪
    "nlp": "自然语言处理",
    "text analysis": "文本分析",
    "sentiment analysis": "情绪分析",
    "topic model": "主题模型",
    "word embedding": "词向量",
    # 实验与调查
    "randomized": "随机实验",
    "randomised": "随机实验",
    "experiment": "实验方法",
    "survey": "调查数据",
    "field experiment": "田野实验",
    # 资产定价
    "fama-macbeth": "Fama-MacBeth 回归",
    "portfolio sort": "组合排序",
    "factor model": "因子模型",
    "asset pricing test": "资产定价检验",
    # 其他
    "meta-analysis": "元分析",
    "stochastic": "随机过程",
    "optimization": "优化方法",
    "equilibrium": "均衡模型",
}

_FINDING_SIGNALS = [
    (r"we (?:show|find|demonstrate|document|establish|prove) that\s+(.{30,200}?)[.]", "核心发现"),
    (r"(?:results?|findings?) (?:show|indicate|suggest|reveal|demonstrate) that\s+(.{30,200}?)[.]", "研究结论"),
    (r"we (?:propose|develop|introduce|present)\s+(.{20,150}?)[.]", "主要贡献"),
    (r"(?:this|the) paper (?:examines?|investigates?|studies|analyzes?|explores?)\s+(.{20,200}?)[.]", "研究问题"),
    (r"(?:this|our) (?:study|analysis|paper|research)\s+(.{20,200}?)[.]", "研究内容"),
    (r"we (?:estimate|measure|quantify|identify)\s+(.{20,200}?)[.]", "量化结果"),
    (r"(?:our|the) (?:model|framework|approach|method)\s+(.{20,150}?)[.]", "方法要点"),
    (r"(?:consistent with|in line with|evidence (?:for|against))\s+(.{20,150}?)[.]", "理论检验"),
]

_last_llm_call: dict[str, float] = {}
LLM_CALL_INTERVAL = 1.5


def infer_domain_zh(title: str, topics: list[str]) -> str:
    text = (title + " " + " ".join(topics)).lower()
    domain_map = [
        (["asset pricing", "capm", "fama", "factor", "return"], "资产定价"),
        (["corporate finance", "firm", "capital structure", "merger", "acquisition", "ipo"], "公司金融"),
        (["banking", "bank", "credit", "lending", "loan"], "银行与信贷"),
        (["monetary", "central bank", "interest rate", "inflation"], "货币政策与宏观经济"),
        (["risk", "volatility", "var", "hedging", "derivative"], "风险管理与衍生品"),
        (["behavioral", "prospect", "sentiment", "bias"], "行为金融"),
        (["fintech", "blockchain", "cryptocurrency", "digital"], "金融科技"),
        (["labor", "employment", "wage", "household"], "劳动经济学"),
        (["trade", "tariff", "export", "import", "globalization"], "国际贸易"),
        (["inequality", "poverty", "welfare", "redistribution"], "收入分配与福利"),
        (["climate", "carbon", "green", "esg", "sustainability"], "绿色金融与可持续发展"),
        (["insurance", "pension", "retirement"], "保险与养老"),
        (["real estate", "housing", "property"], "房地产金融"),
    ]
    for keywords, domain in domain_map:
        if any(kw in text for kw in keywords):
            return domain
    return "金融经济学"


def extract_findings(abstract: str) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for pattern, label in _FINDING_SIGNALS:
        matches = re.findall(pattern, abstract, re.IGNORECASE)
        for m in matches:
            clean = re.sub(r"\s+", " ", m.strip())
            if len(clean) > 20:
                findings.append((label, clean))
    return findings[:3]


def _contains_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def simple_zh_summary(title: str, abstract: str, topics: list[str]) -> str:
    topic_text = "、".join(topics[:3]) if topics else "金融经济学"
    domain = infer_domain_zh(title, topics)
    clean_abs = re.sub(r"\s+", " ", abstract.strip())
    if not clean_abs:
        return (
            f"本文属于「{domain}」领域，主题为：{title}。"
            f"涉及关键词：{topic_text}。"
            "原文未提供摘要，建议通过 DOI 链接查看全文以了解具体研究方法与结论。"
        )

    abstract_lower = clean_abs.lower()
    methods = [zh for key, zh in _METHOD_SIGNALS.items() if key in abstract_lower]
    method_text = "、".join(dict.fromkeys(methods)) if methods else ""

    if not _contains_chinese(clean_abs):
        parts = [
            f"【{domain}】",
            f"论文标题：{title}",
            f"摘要概述：该研究围绕「{topic_text}」相关议题展开，属于{domain}方向的研究。",
            "结论要点：已基于原文英文摘要提炼主题信息，建议结合原文获取精确结论与量化结果。",
        ]
        if method_text:
            parts.append(f"研究方法：{method_text}")
        return "。".join(parts) + "。"

    findings = extract_findings(clean_abs)
    parts: list[str] = [f"【{domain}】", f"论文标题：{title}"]

    if findings:
        for label, content in findings:
            parts.append(f"{label}：{content}")
    else:
        sentences = [s.strip(" .;") for s in re.split(r"(?<=[.!?])\s+", clean_abs) if s.strip()]
        core = "。".join(sentences[:2])
        if len(core) > 300:
            core = core[:297] + "..."
        parts.append(f"摘要概述：{core}")

    if method_text:
        parts.append(f"研究方法：{method_text}")

    return "。".join(parts) + "。"


# LLM 重试配置：最多重试 3 次，初始等待 2 秒，指数退避，上限 30 秒
_LLM_MAX_RETRIES = 3
_LLM_RETRY_BASE_WAIT = 2.0
_LLM_RETRY_MAX_WAIT = 30.0
# 触发重试的 HTTP 状态码：429 限流、502/503 服务不可用
_LLM_RETRYABLE_CODES = {429, 502, 503}


def _call_llm(messages: list[dict], cfg: LLMConfig, temperature: float = 0.3, max_tokens: int = 2048) -> str:
    """调用 LLM API，内置指数退避重试机制。

    对 429（限流）、502/503（服务不可用）和超时错误自动重试，
    最多重试 _LLM_MAX_RETRIES 次，等待时间按指数增长。
    """
    import urllib.error

    if not cfg.enabled:
        return ""

    now = time.time()
    last = _last_llm_call.get(cfg.api_base, 0)
    wait = LLM_CALL_INTERVAL - (now - last)
    if wait > 0:
        time.sleep(wait)
    _last_llm_call[cfg.api_base] = time.time()

    payload = {
        "model": cfg.model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    url = f"{cfg.api_base.rstrip('/')}/chat/completions"
    data_bytes = json.dumps(payload).encode("utf-8")

    last_exc: Exception | None = None
    for attempt in range(1, _LLM_MAX_RETRIES + 1):
        req = Request(
            url=url,
            data=data_bytes,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {cfg.api_key}",
            },
        )
        try:
            with urlopen(req, timeout=cfg.timeout_seconds) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except urllib.error.HTTPError as e:
            last_exc = e
            if e.code in _LLM_RETRYABLE_CODES:
                retry_wait = min(_LLM_RETRY_BASE_WAIT * (2 ** (attempt - 1)), _LLM_RETRY_MAX_WAIT)
                print(f"  [LLM RETRY] HTTP {e.code}, attempt {attempt}/{_LLM_MAX_RETRIES}, waiting {retry_wait:.1f}s...")
                time.sleep(retry_wait)
            else:
                print(f"  [LLM ERROR] HTTP {e.code}: {e.reason}")
                return ""
        except TimeoutError as e:
            last_exc = e
            retry_wait = min(_LLM_RETRY_BASE_WAIT * (2 ** (attempt - 1)), _LLM_RETRY_MAX_WAIT)
            print(f"  [LLM RETRY] Timeout, attempt {attempt}/{_LLM_MAX_RETRIES}, waiting {retry_wait:.1f}s...")
            time.sleep(retry_wait)
        except Exception as e:
            print(f"  [LLM ERROR] {type(e).__name__}: {e}")
            return ""

    print(f"  [LLM ERROR] All {_LLM_MAX_RETRIES} retries exhausted. Last error: {last_exc}")
    return ""


def _llm_translate(text: str, cfg: LLMConfig) -> str:
    if not cfg.enabled or not text.strip():
        return ""
    messages = [{"role": "user", "content": f"请将以下学术论文摘要翻译为中文，保持学术用语准确，译文简洁流畅：\n\n{text[:3000]}"}]
    return _call_llm(messages, cfg, temperature=0.1, max_tokens=1024)


def _is_structured_output_complete(text: str) -> bool:
    labels = ["📌 研究问题：", "🔬 研究方法：", "📊 核心发现：", "💡 应用价值："]
    if not all(label in text for label in labels):
        return False
    for label in labels:
        _, _, tail = text.partition(label)
        segment = tail.split("\n", 1)[0].strip()
        if len(segment) < 12:
            return False
    return True


def _is_summary_complete(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < 50:
        return False
    if _is_structured_output_complete(stripped):
        return True
    if stripped.endswith(("。", ".", "！", "?", "？")) and "..." not in stripped:
        return True
    return False


def _extract_json_from_llm_response(raw: str) -> dict | None:
    """从 LLM 返回文本中健壮地提取第一个 JSON 对象。
    支持带 markdown 代码块、前后有其他文字的情况。"""
    if not raw:
        return None
    # 先尝试去除 markdown 代码块
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    # 尝试直接解析
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # 尝试提取第一个 { ... } 块
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def llm_screen_relevance(papers: list[Paper], cfg: LLMConfig) -> list[Paper]:
    if not cfg.enabled or not papers:
        return papers

    filtered: list[Paper] = []
    for i, p in enumerate(papers, 1):
        print(f"  [SCREEN] [{i}/{len(papers)}] {p.title[:60]}...")
        prompt = (
            "你是金融经济学文献筛选专家。请判断以下论文是否属于金融、经济学或相关领域的高质量学术研究。\n\n"
            f"论文标题：{p.title}\n"
            f"期刊/来源：{p.venue}\n"
            f"主题标签：{', '.join(p.topics)}\n"
            f"摘要：{p.abstract[:500]}\n\n"
            '请仅返回一个JSON对象：{"relevant": true/false, "score": 1-10, "reason": "一句话理由"}'
        )
        raw = _call_llm([{"role": "user", "content": prompt}], cfg, temperature=0.1, max_tokens=256)
        if not raw:
            filtered.append(p)
            continue

        result = _extract_json_from_llm_response(raw)
        if result is None:
            print(f"    [SCREEN WARN] Could not parse response, keeping paper")
            filtered.append(p)
            continue
        try:
            score = int(result.get("score", 0))
            if score >= 6:
                filtered.append(p)
            else:
                print(f"    [FILTERED OUT] score {score} < 6")
        except (ValueError, TypeError):
            print(f"    [SCREEN WARN] Invalid score value, keeping paper")
            filtered.append(p)

    print(f"  [SCREEN] {len(filtered)}/{len(papers)} papers passed relevance screening")
    return filtered


def llm_zh_summary(title: str, abstract: str, topics: list[str], analysis_cfg: LLMConfig, translate_cfg: LLMConfig) -> str:
    if not abstract.strip():
        return simple_zh_summary(title, abstract, topics)

    topic_text = ", ".join(topics) if topics else "N/A"
    if analysis_cfg.enabled:
        prompt = (
            "你是金融经济学研究助手。请基于以下论文信息，生成结构化的中文摘要。\n\n"
            f"标题：{title}\n"
            f"主题：{topic_text}\n"
            f"摘要：{abstract}\n\n"
            "请用以下格式输出（每项1-2句话，不要编造）：\n"
            "📌 研究问题：...\n"
            "🔬 研究方法：...\n"
            "📊 核心发现：...\n"
            "💡 应用价值：..."
        )
        result = _call_llm([{"role": "user", "content": prompt}], analysis_cfg, temperature=0.3, max_tokens=1024)
        if result and _is_summary_complete(result):
            return result

    if translate_cfg.enabled:
        domain = infer_domain_zh(title, topics)
        translated = _llm_translate(abstract, translate_cfg)
        if translated and _is_summary_complete(translated):
            abstract_lower = abstract.lower()
            methods = [zh for key, zh in _METHOD_SIGNALS.items() if key in abstract_lower]
            method_text = "、".join(dict.fromkeys(methods)) if methods else ""
            if len(translated) > 500:
                translated = translated[:497] + "..."
            parts = [f"【{domain}】{translated}"]
            if method_text:
                parts.append(f"研究方法：{method_text}")
            return "。".join(parts) + "。"

    return simple_zh_summary(title, abstract, topics)


def apply_summaries(papers: list[Paper], analysis_cfg: LLMConfig, translate_cfg: LLMConfig) -> list[Paper]:
    print(f"[SUMMARY] analysis_llm={analysis_cfg.model}, translate_llm={translate_cfg.model}")
    for i, p in enumerate(papers, 1):
        print(f"  [SUMMARY] [{i}/{len(papers)}] {p.title[:50]}... (abstract={'yes' if p.abstract.strip() else 'no'})")
        p.summary_zh = llm_zh_summary(p.title, p.abstract, p.topics, analysis_cfg, translate_cfg)
    return papers


def generate_digest_overview(papers: list[Paper], cfg: LLMConfig) -> str:
    if not cfg.enabled or not papers:
        return ""

    paper_lines = [f"- {p.title}：{p.summary_zh[:100]}" for p in papers]
    papers_text = "\n".join(paper_lines)
    prompt = (
        "你是金融经济学研究综述专家。以下是今日筛选出的学术论文列表及其摘要。\n"
        "请用3-5句话生成一段中文综述，概括今日文献的主要主题和研究趋势，语言精炼、专业。\n\n"
        f"{papers_text}"
    )
    print("[OVERVIEW] Generating daily overview...")
    result = _call_llm([{"role": "user", "content": prompt}], cfg, temperature=0.5, max_tokens=512)
    if result:
        print(f"[OVERVIEW] Generated ({len(result)} chars)")
    return result


def score_papers_by_preference(
    papers: list[dict],
    preference: str,
    cfg: LLMConfig,
    batch_size: int = 5,
) -> list[dict]:
    """根据用户研究偏好，让 LLM 为每篇论文打出 relevance_score（0-100）。

    采用批量处理模式，每次将 batch_size 篇论文一起发给 LLM，减少 API 调用次数。
    如果 LLM 未启用或调用失败，所有论文的 relevance_score 设为 -1（表示未评分）。
    """
    if not cfg.enabled or not preference.strip() or not papers:
        for p in papers:
            p["relevance_score"] = -1
        return papers

    # 初始化所有论文的 relevance_score 为 -1
    for p in papers:
        p["relevance_score"] = -1

    # 构建论文索引映射，方便批量处理后回写结果
    paper_index = {i: p for i, p in enumerate(papers)}

    for batch_start in range(0, len(papers), batch_size):
        batch = [(i, papers[i]) for i in range(batch_start, min(batch_start + batch_size, len(papers)))]

        paper_list_text = ""
        for local_idx, (global_idx, p) in enumerate(batch, 1):
            paper_list_text += (
                f"[{local_idx}] 标题：{p.get('title', '')[:100]}\n"
                f"    期刊：{p.get('venue', 'N/A')}\n"
                f"    主题：{', '.join((p.get('topics') or [])[:4])}\n"
                f"    摘要：{(p.get('abstract') or '')[:200]}\n\n"
            )

        prompt = (
            f"用户的研究偏好：{preference}\n\n"
            f"请为以下 {len(batch)} 篇论文评估与用户研究偏好的相关性，"
            f"评分范围 0-100（100 = 完全匹配，0 = 完全不相关）。\n"
            f"只返回 JSON 数组，格式为：[{{\"id\": 1, \"score\": 85}}, {{\"id\": 2, \"score\": 30}}, ...]\n"
            f"不要添加任何其他文字。\n\n"
            f"{paper_list_text}"
        )

        raw = _call_llm([{"role": "user", "content": prompt}], cfg, temperature=0.1, max_tokens=512)
        if not raw:
            print(f"  [RELEVANCE] Batch {batch_start//batch_size + 1}: LLM call failed, skipping batch")
            continue

        # 解析 LLM 返回的 JSON 数组
        try:
            cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            scores_list = json.loads(cleaned)
            if not isinstance(scores_list, list):
                raise ValueError("Expected a JSON array")
            for item in scores_list:
                local_id = int(item.get("id", 0)) - 1  # 转为 0-indexed
                score = int(item.get("score", -1))
                if 0 <= local_id < len(batch):
                    global_idx = batch[local_id][0]
                    paper_index[global_idx]["relevance_score"] = max(0, min(100, score))
        except Exception as e:
            print(f"  [RELEVANCE] Batch parse error: {e}, raw={raw[:200]}")
            continue

        print(f"  [RELEVANCE] Batch {batch_start//batch_size + 1}/{(len(papers) + batch_size - 1)//batch_size} scored")

    scored = sum(1 for p in papers if p.get("relevance_score", -1) >= 0)
    print(f"[RELEVANCE] {scored}/{len(papers)} papers scored by preference")
    return papers


def score_papers_by_preference_local(papers: list[dict], preference: str) -> list[dict]:
    """TF-IDF cosine similarity scoring when LLM is unavailable.

    Converts the user preference string and each paper's text into TF-IDF
    vectors and computes cosine similarity as a 0-100 relevance score.
    Falls back to keyword overlap count if scikit-learn is not installed.
    """
    import math

    def _tokenize(text: str) -> list[str]:
        tokens = re.findall(r"[a-zA-Z\u4e00-\u9fff]{2,}", text.lower())
        stopwords = {
            "the", "and", "for", "with", "from", "that", "this", "into", "using",
            "paper", "study", "analysis", "evidence", "model", "data", "based",
        }
        return [t for t in tokens if t not in stopwords]

    pref_tokens = _tokenize(preference)
    if not pref_tokens:
        for p in papers:
            p["relevance_score"] = -1
        return papers

    pref_set = set(pref_tokens)

    # Try scikit-learn TF-IDF first
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        corpus = [preference]
        for p in papers:
            text = " ".join([
                p.get("title", ""),
                p.get("abstract", ""),
                " ".join(p.get("topics") or []),
                p.get("venue", ""),
            ])
            corpus.append(text)

        vectorizer = TfidfVectorizer(min_df=1, ngram_range=(1, 2))
        tfidf = vectorizer.fit_transform(corpus)
        sims = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        for i, p in enumerate(papers):
            p["relevance_score"] = int(round(float(sims[i]) * 100))
        return papers
    except ImportError:
        pass

    # Fallback: Jaccard-style keyword overlap scored 0-100
    for p in papers:
        text_tokens = set(_tokenize(" ".join([
            p.get("title", ""),
            p.get("abstract", ""),
            " ".join(p.get("topics") or []),
        ])))
        overlap = len(pref_set & text_tokens)
        # Normalize: treat 5+ overlapping terms as full match
        score = min(int(overlap / max(len(pref_set), 1) * 100), 100)
        p["relevance_score"] = score

    return papers


def generate_template_overview(papers: list[Paper]) -> str:
    """Generate a statistics-driven overview without any LLM calls.

    Summarizes domain distribution, method signals, source mix, and top-tier
    coverage based solely on local paper metadata.
    """
    if not papers:
        return ""

    from collections import Counter

    total = len(papers)

    # Domain counts using infer_domain_zh
    domain_counter: Counter[str] = Counter()
    for p in papers:
        domain = infer_domain_zh(p.title, p.topics)
        domain_counter[domain] += 1

    top_domains = domain_counter.most_common(3)

    # Method signals
    method_counter: Counter[str] = Counter()
    for p in papers:
        abstract_lower = p.abstract.lower()
        methods = [zh for key, zh in _METHOD_SIGNALS.items() if key in abstract_lower]
        for m in dict.fromkeys(methods):
            method_counter[m] += 1
    top_methods = method_counter.most_common(2)

    # Source mix
    source_labels = {
        "arxiv": "arXiv",
        "openalex": "OpenAlex",
        "semantic_scholar": "Semantic Scholar",
        "nber": "NBER",
        "ssrn": "SSRN",
    }
    source_counter: Counter[str] = Counter(p.source for p in papers)
    top_sources = source_counter.most_common(3)

    # Top-tier count
    from .models import VENUE_WHITELIST
    top_tier_count = sum(
        1 for p in papers if any(wl in p.venue.lower() for wl in VENUE_WHITELIST)
    )

    parts = [f"本期共收录 {total} 篇论文。"]

    if top_domains:
        domain_text = "、".join(f"{d}（{n} 篇）" for d, n in top_domains)
        parts.append(f"研究方向主要集中在{domain_text}。")

    if top_methods:
        method_text = "、".join(m for m, _ in top_methods)
        parts.append(f"方法上以{method_text}为主。")

    if top_sources:
        src_text = "、".join(f"{source_labels.get(s, s)}（{n} 篇）" for s, n in top_sources)
        parts.append(f"来源分布：{src_text}。")

    if top_tier_count:
        parts.append(f"其中 {top_tier_count} 篇命中顶级期刊白名单。")

    return "".join(parts)


def generate_digest_insights(papers: list[Paper], cfg: LLMConfig) -> dict[str, str]:
    if not cfg.enabled or not papers:
        return {}

    paper_lines = [
        f"{idx}. {p.title} | source={p.source} | topics={', '.join(p.topics[:3])} | summary={p.summary_zh[:140]}"
        for idx, p in enumerate(papers, 1)
    ]
    prompt = (
        "你是金融经济学研究编辑。请根据以下文献列表生成中文结构化洞察，并只输出JSON：\n"
        '{\"themes\":\"...\",\"methods\":\"...\",\"implications\":\"...\",\"watchlist\":\"...\"}\n'
        "要求：\n"
        "1. 每个字段1-2句，简洁具体，不要使用Markdown。\n"
        "2. 【重要】JSON的键名必须严格使用英文（themes/methods/implications/watchlist），绝对不能翻译为中文键名。\n"
        "3. 只输出JSON对象本身，不要有任何前缀或后缀文字。\n\n"
        + "\n".join(paper_lines)
    )
    raw = _call_llm([{"role": "user", "content": prompt}], cfg, temperature=0.2, max_tokens=700)
    if not raw:
        return {}

    obj = _extract_json_from_llm_response(raw)
    if obj is None:
        return {}

    fields = ["themes", "methods", "implications", "watchlist"]
    result: dict[str, str] = {}
    for field in fields:
        val = obj.get(field, "")
        if isinstance(val, str) and val.strip():
            result[field] = val.strip()
    return result
