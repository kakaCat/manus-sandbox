from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from app.core.config import get_settings


def create_llm() -> BaseChatModel:
    settings = get_settings()

    return ChatOpenAI(
        model=settings.model_name,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        openai_api_key=settings.openai_api_key,
        openai_api_base=settings.openai_api_base,
        streaming=True
    )
