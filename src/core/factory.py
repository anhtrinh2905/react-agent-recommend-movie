import os
from typing import Optional

from src.core.llm_provider import LLMProvider
from src.core.openai_provider import OpenAIProvider

OPENAI_MODELS = ("gpt-4o", "gpt-4o-mini")


def get_llm_provider(model: Optional[str] = None) -> LLMProvider:
    selected_model = model or os.getenv("DEFAULT_MODEL", "gpt-4o")
    return OpenAIProvider(
        model_name=selected_model,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
