import tomllib
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings


def _get_project_version() -> str:
    try:
        pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
        with open(pyproject, "rb") as f:
            return tomllib.load(f)["project"]["version"]
    except Exception:
        return "0.0.0"


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # LLM
    llm_model: str = "qwen3:8b"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = ""
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2048

    # Embeddings
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # Vector Store (PostgreSQL + pgvector)
    database_url: str = ""
    pgvector_collection_gita: str = "dharma_gita"
    pgvector_collection_ramayana: str = "dharma_ramayana"
    pgvector_collection_stories: str = "dharma_stories"

    # Retrieval
    retriever_k: int = 5
    retriever_score_threshold: float = 0.5
    hybrid_bm25_k: int = 10
    rrf_k: int = 60

    # Graph node config
    query_analyzer_temperature: float = 0.1
    query_analyzer_max_tokens: int = 256
    citation_validator_temperature: float = 0.0
    citation_validator_max_tokens: int = 512
    max_selected_verses: int = 3
    max_selected_stories: int = 2
    graph_recursion_limit: int = 25

    # API
    api_prefix: str = "/api/v1"
    chat_message_max_length: int = 2000
    thread_id_max_length: int = 100
    cors_origins: list[str] = ["*"]

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: Literal["debug", "info", "warning", "error"] = "info"
    app_title: str = "DharmaGPT"
    app_description: str = "AI-powered Dharma guide with Bhagavad Gita & Ramayana wisdom"
    app_version: str = ""


settings = Settings()
if not settings.app_version:
    settings.app_version = _get_project_version()
