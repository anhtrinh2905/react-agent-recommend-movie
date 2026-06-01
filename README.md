# Lab 3: Chatbot vs ReAct Agent (Industry Edition)

Welcome to Phase 3 of the Agentic AI course! This lab focuses on moving from a simple LLM Chatbot to a sophisticated **ReAct Agent** with industry-standard monitoring.

## 🚀 Getting Started

### 1. Setup Environment
Copy the `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env   # Linux/Mac
copy .env.example .env  # Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run src/app.py
```

### 4. Directory Structure
- `src/tools/`: Extension point for your custom tools.

---

## 🤖 LLM Provider Setup

Dự án hỗ trợ 3 provider cloud + 1 local. Chọn 1 hoặc nhiều để test.

### Option A — OpenAI (mặc định)
1. Lấy API key tại https://platform.openai.com/api-keys
2. Thêm vào `.env`:
```env
OPENAI_API_KEY=sk-...
DEFAULT_MODEL=gpt-4o-mini   # rẻ hơn gpt-4o để test
```

### Option B — DeepSeek (rẻ, nhanh)
1. Lấy API key tại https://platform.deepseek.com/api_keys
2. Thêm vào `.env`:
```env
DEEPSEEK_API_KEY=sk-...
```
3. Chọn `deepseek/deepseek-chat` trong dropdown app.

### Option C — Ollama (chạy local, miễn phí, không cần API key)
1. Cài Ollama: https://ollama.com/download
2. Khởi động server và tải model:
```bash
ollama serve                    # khởi động server (chạy nền)
ollama pull llama3.2:3b         # ~2GB, chạy được trên CPU thường
# hoặc model nhỏ hơn:
ollama pull qwen2.5:3b          # ~2GB, tiếng Việt tốt hơn
# hoặc model mạnh hơn (cần RAM 8GB+):
ollama pull qwen2.5:7b          # ~4.7GB
```
3. Không cần chỉnh `.env` — app tự detect Ollama đang chạy và hiện trong dropdown.

> **Tip:** Dùng `ollama list` để xem các model đã tải.

### Option D — Local GGUF (llama-cpp, không cần internet sau khi tải)
1. Cài thêm dependencies:
```bash
pip install -r requirements-local.txt
```
2. Tải model GGUF (~2.2GB):
   - Link: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
   - File cần tải: `phi-3-mini-4k-instruct-q4.gguf`
3. Tạo thư mục và đặt file vào:
```bash
mkdir models
# Đặt file .gguf vào thư mục models/
```
4. Thêm vào `.env`:
```env
LOCAL_MODEL_PATH=./models/Phi-3-mini-4k-instruct-q4.gguf
```

---

## 🏠 Running with Local Models (CPU)

If you don't want to use OpenAI or Gemini, you can run open-source models (like Phi-3) directly on your CPU using `llama-cpp-python`.

### 1. Download the Model
Download the **Phi-3-mini-4k-instruct-q4.gguf** (approx 2.2GB) from Hugging Face:
- [Phi-3-mini-4k-instruct-GGUF](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf)
- Direct Download: [phi-3-mini-4k-instruct-q4.gguf](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf)

### 2. Place Model in Project
Create a `models/` folder in the root and move the downloaded `.gguf` file there.

### 3. Update `.env`
Change your `DEFAULT_PROVIDER` and set the path:
```env
DEFAULT_PROVIDER=local
LOCAL_MODEL_PATH=./models/Phi-3-mini-4k-instruct-q4.gguf
```

## 🎯 Lab Objectives

1.  **Baseline Chatbot**: Observe the limitations of a standard LLM when faced with multi-step reasoning.
2.  **ReAct Loop**: Implement the `Thought-Action-Observation` cycle in `src/agent/agent.py`.
3.  **Provider Switching**: Swap between OpenAI and Gemini seamlessly using the `LLMProvider` interface.
4.  **Failure Analysis**: Use the structured logs in `logs/` to identify why the agent fails (hallucinations, parsing errors).
5.  **Grading & Bonus**: Follow the [SCORING.md](file:///Users/tindt/personal/ai-thuc-chien/day03-lab-agent/SCORING.md) to maximize your points and explore bonus metrics.

## 🛠️ How to Use This Baseline
The code is designed as a **Production Prototype**. It includes:
- **Telemetry**: Every action is logged in JSON format for later analysis.
- **Robust Provider Pattern**: Easily extendable to any LLM API.
- **Clean Skeletons**: Focus on the logic that matters—the agent's reasoning process.

---

*Happy Coding! Let's build agents that actually work.*
# react-agent-recommend-movie
