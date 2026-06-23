from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from app.knowledge_base.schemas import (
    QueryAnalysis,
    RetrievedVerse,
    RetrievedStory,
    Citation,
)


class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    query: str

    query_analysis: QueryAnalysis | None
    analysis_raw: str | None

    gita_verses: list[RetrievedVerse]
    ramayana_verses: list[RetrievedVerse]
    stories: list[RetrievedStory]

    selected_verses: list[RetrievedVerse]
    selected_stories: list[RetrievedStory]

    context: str
    response: str
    citations: list[Citation]
    validation_result: str
    final_response: str

    llm_api_key: str
    llm_base_url: str
