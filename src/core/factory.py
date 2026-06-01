import os
from typing import Optional

from src.core.gemini_provider import GeminiProvider
from src.core.llm_provider import LLMProvider
from src.core.openai_provider import OpenAIProvider


def is_local_provider_available() -> bool:
    try:
        import llama_cpp  # noqa: F401

        return True
    except ImportError:
        return False


def get_llm_provider(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> LLMProvider:
    selected = (provider or os.getenv("DEFAULT_PROVIDER", "openai")).lower()
    selected_model = model or os.getenv("DEFAULT_MODEL", "gpt-4o")

    if selected == "openai":
        return OpenAIProvider(
            model_name=selected_model,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    if selected in {"google", "gemini"}:
        gemini_model = selected_model if selected_model.startswith("gemini") else "gemini-1.5-flash"
        return GeminiProvider(
            model_name=gemini_model,
            api_key=os.getenv("GEMINI_API_KEY"),
        )
    if selected == "local":
        if not is_local_provider_available():
            raise ImportError(
                "llama-cpp-python chưa được cài. Chạy: "
                "pip install llama-cpp-python --extra-index-url "
                "https://abetlen.github.io/llama-cpp-python/whl/metal "
                "(xem requirements-local.txt)."
            )
        from src.core.local_provider import LocalProvider

        model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        return LocalProvider(model_path=model_path)

    raise ValueError(f"Unsupported provider: {selected}")
