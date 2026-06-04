# Movie ReAct Agent — Monorepo

Demo gợi ý phim với Chatbot baseline và ReAct Agent (TMDB tools), tách thành 3 phần:

| Thư mục | Mô tả |
|---------|--------|
| [`backend/`](backend/) | FastAPI — logic agent, tools, LLM providers |
| [`frontend-user/`](frontend-user/) | Next.js — giao diện người dùng (scaffold) |
| [`frontend-admin/`](frontend-admin/) | Next.js — dashboard admin / so sánh models (scaffold) |

## Chạy nhanh

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # điền OPENAI_API_KEY, TMDB_API_KEY, ...
uvicorn src.api.main:app --reload --port 8000
```

Chi tiết LLM providers (OpenAI, DeepSeek, Ollama, local GGUF): xem [backend/README.md](backend/README.md).

### 2. Frontend User

```bash
cd frontend-user && npm install && npm run dev
```

→ http://localhost:3000

### 3. Frontend Admin

```bash
cd frontend-admin && npm install && npm run dev -- -p 3001
```

→ http://localhost:3001

## Tài liệu lab (gốc)

- [SCORING.md](SCORING.md) · [EVALUATION.md](EVALUATION.md) · [INSTRUCTOR_GUIDE.md](INSTRUCTOR_GUIDE.md)
- Báo cáo nhóm: `report/`

## Thay đổi so với bản Streamlit

- UI Streamlit đã được thay bằng FastAPI + 2 app Next.js (chưa implement UI, chỉ scaffold).
- Logic agent (`src/agent`, `src/core`, `src/tools`) nằm trong `backend/`.
