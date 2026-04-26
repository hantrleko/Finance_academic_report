"""页面：手动抓取 - 手动触发文献抓取并实时查看进度"""
from __future__ import annotations

import contextlib
import datetime as dt
import sys
import threading
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="手动抓取 | 金融文献速递",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ 手动抓取")
st.markdown(
    """
    在此页面可手动触发文献抓取流程。抓取完成后，结果将保存到 `output/` 目录，
    并可在「今日速递」和「历史档案」页面中查看。

    > **注意：** 如需 LLM 摘要增强功能，请在下方填写 API Key。不填写则使用规则摘要。
    """
)

st.markdown("---")

# ---- 配置区 ----
st.subheader("🔧 抓取参数配置")

col1, col2 = st.columns(2)
with col1:
    run_date = st.date_input(
        "抓取日期",
        value=dt.date.today(),
        help="选择要抓取的目标日期（默认今天）",
    )
    max_papers = st.slider("最大文献数", min_value=5, max_value=30, value=12, step=1)
    lookback_days = st.slider("回溯天数", min_value=1, max_value=30, value=7, step=1)
    min_quality_score = st.slider("最低质量分", min_value=0, max_value=10, value=2, step=1)

with col2:
    openalex_mailto = st.text_input(
        "OpenAlex 联系邮箱（可选）",
        placeholder="your@email.com",
        help="填写后可提高 OpenAlex API 请求优先级",
    )
    s2_api_key = st.text_input(
        "Semantic Scholar API Key（可选）",
        type="password",
        help="填写后可提高 S2 请求速率",
    )

st.markdown("---")
st.subheader("🤖 LLM 配置（可选）")
st.info("不填写 LLM 配置时，将使用规则摘要（无 AI 增强）。")

col3, col4 = st.columns(2)
with col3:
    st.markdown("**翻译模型（用于英文摘要翻译）**")
    llm_api_base = st.text_input("API Base URL", value="https://api.siliconflow.cn/v1", key="llm_base")
    llm_api_key = st.text_input("API Key", type="password", key="llm_key")
    llm_model = st.text_input("模型名称", value="tencent/Hunyuan-MT-7B", key="llm_model")

with col4:
    st.markdown("**分析模型（用于摘要生成和洞察分析）**")
    analysis_api_base = st.text_input("API Base URL", value="https://open.bigmodel.cn/api/paas/v4", key="ana_base")
    analysis_api_key = st.text_input("API Key", type="password", key="ana_key")
    analysis_model = st.text_input("模型名称", value="glm-4.7-flash", key="ana_model")

st.markdown("---")

# ---- 执行区 ----
if "run_log" not in st.session_state:
    st.session_state.run_log = ""
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "run_result" not in st.session_state:
    st.session_state.run_result = None


def run_digest_task(params: dict) -> None:
    """在后台线程中运行抓取任务。
    
    直接从 params 字典构建配置对象，完全不修改全局 os.environ，
    避免多用户并发时的环境变量污染问题。
    """
    log_buffer = StringIO()
    try:
        with contextlib.redirect_stdout(log_buffer):
            from src.config import (
                build_digest_config_from_dict,
                build_translate_llm_config_from_dict,
                build_analysis_llm_config_from_dict,
            )
            from src.pipeline import build_digest

            # 直接从参数字典构建配置对象，不依赖 os.environ
            cfg = build_digest_config_from_dict(params)
            translate_cfg = build_translate_llm_config_from_dict(params)
            analysis_cfg = build_analysis_llm_config_from_dict(params)

            result = build_digest(
                config=cfg,
                translate_cfg=translate_cfg,
                analysis_cfg=analysis_cfg,
                run_date=params["run_date"],
            )
        st.session_state.run_result = result
        log_buffer.write(f"\n✅ 抓取完成！共获取 {result['count']} 篇文献。\n")
    except Exception as e:
        log_buffer.write(f"\n❌ 抓取失败：{type(e).__name__}: {e}\n")
        st.session_state.run_result = None
    finally:
        st.session_state.run_log = log_buffer.getvalue()
        st.session_state.is_running = False


col_btn1, col_btn2 = st.columns([1, 3])
with col_btn1:
    start_btn = st.button(
        "🚀 开始抓取",
        disabled=st.session_state.is_running,
        use_container_width=True,
        type="primary",
    )
with col_btn2:
    if st.session_state.is_running:
        st.info("⏳ 抓取进行中，请稍候（通常需要 1-3 分钟）...")

if start_btn and not st.session_state.is_running:
    st.session_state.is_running = True
    st.session_state.run_log = "正在初始化抓取任务...\n"
    st.session_state.run_result = None

    params = {
        "run_date": run_date,
        "max_papers": max_papers,
        "lookback_days": lookback_days,
        "min_quality_score": min_quality_score,
        "openalex_mailto": openalex_mailto,
        "s2_api_key": s2_api_key,
        "llm_api_base": llm_api_base,
        "llm_api_key": llm_api_key,
        "llm_model": llm_model,
        "analysis_api_base": analysis_api_base,
        "analysis_api_key": analysis_api_key,
        "analysis_model": analysis_model,
    }

    thread = threading.Thread(target=run_digest_task, args=(params,), daemon=True)
    thread.start()
    st.rerun()

# ---- 日志输出 ----
if st.session_state.run_log:
    st.subheader("📋 运行日志")
    st.code(st.session_state.run_log, language="text")

    if not st.session_state.is_running and st.session_state.run_result:
        result = st.session_state.run_result
        st.success(f"✅ 抓取完成！共获取 **{result['count']}** 篇文献，来源：{result.get('source_used', 'N/A')}")
        st.markdown("请前往「今日速递」或「历史档案」页面查看结果。")

    if st.session_state.is_running:
        st.button("🔄 刷新日志", on_click=st.rerun)
