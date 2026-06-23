import re
from pydantic import BaseModel, Field
from app.config import settings
from app.knowledge_base.schemas import QueryAnalysis, RetrievedVerse, RetrievedStory, Citation

_THREAD_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=settings.chat_message_max_length,
    )
    thread_id: str = Field(
        default="default",
        max_length=settings.thread_id_max_length,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )


class ChatResponse(BaseModel):
    response: str
    query_analysis: QueryAnalysis | None = None
    verses_used: list[RetrievedVerse] = Field(default_factory=list)
    stories_used: list[RetrievedStory] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    validation_status: str | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = ""


class IngestResponse(BaseModel):
    status: str
    pages_loaded: int
    chunks_indexed: int
    source: str
    collection: str
