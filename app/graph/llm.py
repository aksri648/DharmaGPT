from langchain_openai import ChatOpenAI
from app.config import settings


def build_llm(
    temperature: float | None = None,
    max_tokens: int | None = None,
    api_key_override: str | None = None,
    base_url_override: str | None = None,
) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.llm_model,
        openai_api_base=base_url_override or settings.llm_base_url,
        openai_api_key=api_key_override or settings.llm_api_key,
        temperature=temperature if temperature is not None else settings.llm_temperature,
        max_tokens=max_tokens if max_tokens is not None else settings.llm_max_tokens,
    )
