from functools import lru_cache
from langchain_postgres import PGVector
from app.config import settings
from app.rag.embeddings import get_embeddings


def get_connection() -> str:
    return settings.database_url


@lru_cache(maxsize=4)
def get_vectorstore(collection_name: str) -> PGVector:
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=collection_name,
        connection=get_connection(),
        use_jsonb=True,
    )


def get_gita_store() -> PGVector:
    return get_vectorstore(settings.pgvector_collection_gita)


def get_ramayana_store() -> PGVector:
    return get_vectorstore(settings.pgvector_collection_ramayana)


def get_stories_store() -> PGVector:
    return get_vectorstore(settings.pgvector_collection_stories)
