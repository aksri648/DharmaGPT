import asyncio
import json
from app.graph.state import GraphState
from app.rag.retriever import combined_search
from app.knowledge_base.schemas import RetrievedVerse, RetrievedStory, QueryAnalysis
from app.knowledge_base.constants import (
    META_TEXT, META_TRANSLATION, META_CHAPTER, META_VERSE,
    META_SPEAKER, META_THEMES, META_SOURCE,
    META_TITLE, META_SUMMARY, META_TEACHING,
)

JSON_FENCE_OPEN = "```json"
JSON_FENCE_CLOSE = "```"
LEN_FENCE_OPEN = len(JSON_FENCE_OPEN)
LEN_FENCE_CLOSE = len(JSON_FENCE_CLOSE)


def parse_analysis(analysis_raw: str | None) -> QueryAnalysis | None:
    if not analysis_raw:
        return None
    try:
        cleaned = analysis_raw.strip()
        if cleaned.startswith(JSON_FENCE_OPEN):
            cleaned = cleaned[LEN_FENCE_OPEN:]
        if cleaned.endswith(JSON_FENCE_CLOSE):
            cleaned = cleaned[:-LEN_FENCE_CLOSE]
        cleaned = cleaned.strip()
        data = json.loads(cleaned)
        return QueryAnalysis(**data)
    except (json.JSONDecodeError, Exception):
        return None


def _build_verse(item) -> RetrievedVerse:
    meta = item.metadata
    return RetrievedVerse(
        text=meta.get(META_TEXT, item.document),
        translation=meta.get(META_TRANSLATION, ""),
        chapter=int(meta.get(META_CHAPTER, 0)),
        verse=int(meta.get(META_VERSE, 0)),
        source=meta.get(META_SOURCE, item.source),
        speaker=meta.get(META_SPEAKER),
        score=item.score,
        themes=meta.get(META_THEMES, []),
    )


def _build_story(item) -> RetrievedStory:
    meta = item.metadata
    return RetrievedStory(
        title=meta.get(META_TITLE, ""),
        summary=meta.get(META_SUMMARY, item.document),
        teaching=meta.get(META_TEACHING, ""),
        source=meta.get(META_SOURCE, item.source),
        score=item.score,
        themes=meta.get(META_THEMES, []),
    )


def scripture_retrieval_node(state: GraphState) -> dict:
    query = state.get("query", "")
    analysis_raw = state.get("analysis_raw")
    analysis = parse_analysis(analysis_raw)

    emotion = analysis.emotion if analysis else None
    theme = analysis.theme if analysis else None
    category = analysis.category if analysis else None

    gita_results, ramayana_results, story_results = asyncio.get_event_loop().run_in_executor(
        None,
        lambda: combined_search(query=query, emotion=emotion, theme=theme, category=category),
    )

    gita_verses = [_build_verse(doc) for doc in gita_results]
    ramayana_verses_raw = [_build_verse(doc) for doc in ramayana_results]
    stories = [_build_story(doc) for doc in story_results]

    return {
        "query_analysis": analysis,
        "gita_verses": gita_verses,
        "ramayana_verses": ramayana_verses_raw,
        "stories": stories,
    }
