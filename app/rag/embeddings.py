from functools import lru_cache
from langchain_openai import OpenAIEmbeddings
from app.config import settings


@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_base=settings.llm_base_url,
        openai_api_key=settings.llm_api_key or "sk-placeholder",
    )
