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
from src.core.factory import OPENAI_MODELS, get_llm_provider
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


def extract_movies_from_trace(trace):
    """Extract movie data with images from trace observations."""
    movies = []
    seen_ids = set()
    if not trace:
        return movies
    for step in trace:
        obs_raw = step.get("observation")
        if not obs_raw:
            continue
        try:
            obs = json.loads(obs_raw)
        except (json.JSONDecodeError, TypeError):
            continue
        # Single movie detail
        if obs.get("poster_url") and obs.get("id") not in seen_ids:
            movies.append(obs)
            seen_ids.add(obs["id"])
        # List of movies (search, similar, trending, mood, compare)
        for key in ("movies", "comparison"):
            for m in obs.get(key, []):
                if isinstance(m, dict) and m.get("poster_url") and m.get("id") not in seen_ids:
                    movies.append(m)
                    seen_ids.add(m["id"])
    return movies


def render_movie_cards(movies, max_cols=4):
    """Render movie poster cards in a grid."""
    if not movies:
        return
    st.markdown("---")
    st.markdown("🎬 **Phim liên quan:**")
    cols = st.columns(min(len(movies), max_cols))
    for idx, movie in enumerate(movies[:max_cols * 2]):
        col = cols[idx % max_cols]
        with col:
            poster = movie.get("poster_url")
            if poster:
                st.image(poster, use_container_width=True)
            title = movie.get("title", "")
            year = movie.get("year", "")
            rating = movie.get("rating", "")
            genres = ", ".join(movie.get("genres", [])) if movie.get("genres") else ""
            st.markdown(f"**{title}** ({year})")
            if rating:
                st.caption(f"⭐ {rating}/10 · {genres}")


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
                    # Show banner image in trace if available
                    for key in ("movies", "comparison"):
                        for m in obs.get(key, []):
                            if isinstance(m, dict) and m.get("backdrop_url"):
                                st.image(m["backdrop_url"], caption=m.get("title", ""), use_container_width=True)
                                break
                        else:
                            continue
                        break
                    else:
                        if obs.get("backdrop_url"):
                            st.image(obs["backdrop_url"], caption=obs.get("title", ""), use_container_width=True)
                    st.json(obs)
                except json.JSONDecodeError:
                    st.code(step["observation"])
            if step.get("raw") and not step.get("action"):
                st.text(step["raw"])


def run_query(mode: str, user_input: str, model: str, max_steps: int):
    llm = get_llm_provider(model=model)

    if mode == "ReAct Agent":
        agent = ReActAgent(llm=llm, tools=TOOL_SPECS, max_steps=max_steps)
        return agent.run(user_input)

    chatbot = ChatbotBaseline(llm=llm)
    return chatbot.run(user_input)


init_session()

st.title("🎬 Movie Recommendation Demo")
st.caption(
    "So sánh Chatbot baseline vs ReAct Agent (OpenAI). "
    "Đổi model gpt-4o / gpt-4o-mini ở sidebar để so sánh chất lượng & tốc độ."
)

with st.sidebar:
    st.header("Cấu hình")
    mode = st.radio("Chế độ", ["ReAct Agent", "Chatbot Baseline"], index=0)
    model_options = list(OPENAI_MODELS)
    default_model = os.getenv("DEFAULT_MODEL", "gpt-4o")
    if default_model not in model_options:
        default_model = "gpt-4o"
    model = st.selectbox(
        "OpenAI Model",
        model_options,
        index=model_options.index(default_model),
    )
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("Thiếu `OPENAI_API_KEY` trong `.env`.")
    if not os.getenv("TMDB_API_KEY"):
        st.warning("Thiếu `TMDB_API_KEY` trong `.env` — tools phim sẽ không hoạt động.")
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
                    f"model: {msg['metrics'].get('model', '—')} · "
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
                    result = run_query(mode, user_input, model, max_steps)
                    answer = result["answer"]
                    st.markdown(answer)

                    metrics = {
                        "model": model,
                        "latency_ms": result.get("latency_ms"),
                        "usage": result.get("usage"),
                        "steps": result.get("steps"),
                        "mode": result.get("mode"),
                    }
                    st.caption(
                        f"⏱ {metrics.get('latency_ms', 0)} ms · "
                        f"model: {model} · "
                        f"mode: {metrics.get('mode')} · "
                        f"steps: {metrics.get('steps', '—')}"
                    )

                    st.session_state.last_trace = result.get("trace")
                    st.session_state.last_metrics = metrics
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer, "metrics": metrics}
                    )

                    # Display movie banners from trace
                    trace_movies = extract_movies_from_trace(result.get("trace"))
                    if trace_movies:
                        render_movie_cards(trace_movies)
                except Exception as exc:
                    st.error(f"Lỗi: {exc}")
                    st.info("Kiểm tra `OPENAI_API_KEY` trong `.env`.")

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
