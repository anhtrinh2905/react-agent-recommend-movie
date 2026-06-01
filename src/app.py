"""
Streamlit demo: Chatbot vs ReAct Movie Recommendation Agent.

Run from project root:
    streamlit run src/app.py
"""

import json
import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from src.agent.agent import ReActAgent
from src.agent.chatbot import ChatbotBaseline
from src.core.factory import get_llm_provider, is_local_provider_available
from src.tools.registry import TOOL_SPECS

st.set_page_config(
    page_title="Movie ReAct Agent Demo",
    page_icon="🎬",
    layout="wide",
)

EXAMPLE_PROMPTS = [
    "Tôi vừa xem Inception, gợi ý phim tương tự có trên Netflix.",
    "Phim trending tuần này ở VN thể loại Sci-Fi là gì?",
    "Tôi buồn, muốn xem phim nhẹ nhàng — gợi ý 3 phim.",
    "So sánh Inception, Interstellar và The Prestige.",
    "Phim Get Out có trên Netflix VN không?",
]


def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_trace" not in st.session_state:
        st.session_state.last_trace = None
    if "last_metrics" not in st.session_state:
        st.session_state.last_metrics = None


def render_trace(trace):
    if not trace:
        st.info("Chưa có trace ReAct. Hãy gửi câu hỏi ở chế độ ReAct Agent.")
        return

    for step in trace:
        with st.expander(f"Bước {step['step']}", expanded=False):
            if step.get("thought"):
                st.markdown(f"**Thought:** {step['thought']}")
            if step.get("action"):
                st.markdown(f"**Action:** `{step['action']}`")
            if step.get("observation"):
                try:
                    obs = json.loads(step["observation"])
                    st.json(obs)
                except json.JSONDecodeError:
                    st.code(step["observation"])
            if step.get("raw") and not step.get("action"):
                st.text(step["raw"])


def run_query(mode: str, user_input: str, provider: str, model: str, max_steps: int):
    llm = get_llm_provider(provider=provider, model=model)

    if mode == "ReAct Agent":
        agent = ReActAgent(llm=llm, tools=TOOL_SPECS, max_steps=max_steps)
        return agent.run(user_input)

    chatbot = ChatbotBaseline(llm=llm)
    return chatbot.run(user_input)


init_session()

st.title("🎬 Movie Recommendation Demo")
st.caption("So sánh Chatbot baseline vs ReAct Agent với 7 movie tools (TMDB API).")

with st.sidebar:
    st.header("Cấu hình")
    mode = st.radio("Chế độ", ["ReAct Agent", "Chatbot Baseline"], index=0)
    provider_options = ["openai", "google"]
    if is_local_provider_available():
        provider_options.append("local")

    default_provider = os.getenv("DEFAULT_PROVIDER", "openai").lower()
    if default_provider not in provider_options:
        default_provider = "openai"

    provider = st.selectbox(
        "LLM Provider",
        provider_options,
        index=provider_options.index(default_provider),
    )
    if not is_local_provider_available():
        st.caption("Local model: cài thêm từ `requirements-local.txt` nếu cần.")
    if not os.getenv("TMDB_API_KEY"):
        st.warning("Thiếu `TMDB_API_KEY` trong `.env` — tools phim sẽ không hoạt động.")
    default_model = os.getenv("DEFAULT_MODEL", "gpt-4o")
    if provider == "google":
        default_model = "gemini-1.5-flash"
    elif provider == "local":
        default_model = "Phi-3-mini (local)"
    model = st.text_input("Model", value=default_model)
    max_steps = st.slider("Max ReAct steps", 2, 8, 5)

    st.divider()
    st.subheader("Tools (7)")
    for tool in TOOL_SPECS:
        st.markdown(f"**`{tool['name']}`** — {tool['description'][:80]}...")

    st.divider()
    st.subheader("Gợi ý câu hỏi")
    for prompt in EXAMPLE_PROMPTS:
        if st.button(prompt, key=f"ex_{abs(hash(prompt))}"):
            st.session_state.pending_prompt = prompt

col_chat, col_trace = st.columns([1.2, 1])

with col_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("metrics"):
                st.caption(
                    f"⏱ {msg['metrics'].get('latency_ms', 0)} ms · "
                    f"steps: {msg['metrics'].get('steps', '—')} · "
                    f"tokens: {msg['metrics'].get('usage', {}).get('total_tokens', '—')}"
                )

    pending = st.session_state.pop("pending_prompt", None)
    user_input = st.chat_input("Hỏi về phim...") or pending

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Đang suy luận..."):
                try:
                    result = run_query(mode, user_input, provider, model, max_steps)
                    answer = result["answer"]
                    st.markdown(answer)

                    metrics = {
                        "latency_ms": result.get("latency_ms"),
                        "usage": result.get("usage"),
                        "steps": result.get("steps"),
                        "mode": result.get("mode"),
                    }
                    st.caption(
                        f"⏱ {metrics.get('latency_ms', 0)} ms · "
                        f"mode: {metrics.get('mode')} · "
                        f"steps: {metrics.get('steps', '—')}"
                    )

                    st.session_state.last_trace = result.get("trace")
                    st.session_state.last_metrics = metrics
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer, "metrics": metrics}
                    )
                except Exception as exc:
                    st.error(f"Lỗi: {exc}")
                    st.info("Kiểm tra API key trong `.env` hoặc chọn provider `local` nếu đã tải model GGUF.")

with col_trace:
    st.subheader("ReAct Trace")
    if mode == "ReAct Agent":
        render_trace(st.session_state.last_trace)
    else:
        st.info("Chuyển sang **ReAct Agent** để xem Thought / Action / Observation.")

    if st.session_state.last_metrics:
        st.subheader("Metrics")
        st.json(st.session_state.last_metrics)

    if st.button("Xóa lịch sử chat"):
        st.session_state.messages = []
        st.session_state.last_trace = None
        st.session_state.last_metrics = None
        st.rerun()
