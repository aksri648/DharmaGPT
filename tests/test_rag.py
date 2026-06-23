"""Tests for RAG pipeline components."""

from app.knowledge_base.taxonomies import EMOTIONS, THEMES, CATEGORIES
from app.knowledge_base.schemas import VerseMetadata, StoryMetadata, QueryAnalysis, RetrievedVerse, RetrievedStory
from app.knowledge_base.story_db import STORIES
from app.templates.response import SYSTEM_PROMPT


def test_taxonomies_not_empty():
    assert len(EMOTIONS) > 0
    assert len(THEMES) > 0
    assert len(CATEGORIES) > 0


def test_verse_metadata():
    meta = VerseMetadata(
        source="Bhagavad Gita",
        chapter=2,
        verse=47,
        speaker="Krishna",
        themes=["duty", "action"],
        emotions=["fear"],
    )
    assert meta.source == "Bhagavad Gita"
    assert meta.chapter == 2
    assert meta.verse == 47


def test_story_metadata():
    meta = StoryMetadata(
        title="Test Story",
        source="Ramayana",
        themes=["courage"],
        emotions=["fear"],
        characters=["Rama"],
    )
    assert meta.title == "Test Story"


def test_query_analysis():
    analysis = QueryAnalysis(
        emotion="fear",
        theme="courage",
        category="career",
        confidence=0.85,
    )
    assert analysis.emotion == "fear"
    assert analysis.theme == "courage"


def test_story_db_not_empty():
    assert len(STORIES) > 0
    for story in STORIES:
        assert "title" in story
        assert "summary" in story
        assert "themes" in story
        assert "emotions" in story


def test_story_db_themes_valid():
    for story in STORIES:
        for theme in story["themes"]:
            assert theme in THEMES, f"Invalid theme '{theme}' in story '{story['title']}'"


def test_story_db_emotions_valid():
    for story in STORIES:
        for emotion in story["emotions"]:
            assert emotion in EMOTIONS, f"Invalid emotion '{emotion}' in story '{story['title']}'"


def test_system_prompt_includes_key_sections():
    assert "Dharma Reflection" in SYSTEM_PROMPT
    assert "Core Teaching" in SYSTEM_PROMPT
    assert "Inspirational Verse" in SYSTEM_PROMPT
    assert "Action Steps" in SYSTEM_PROMPT
    assert "Sources" in SYSTEM_PROMPT


def test_constants_import():
    from app.knowledge_base.constants import (
        SOURCE_BHAGAVAD_GITA, SOURCE_RAMAYANA,
        META_SOURCE, META_CHAPTER, META_VERSE,
    )
    assert SOURCE_BHAGAVAD_GITA == "Bhagavad Gita"
    assert SOURCE_RAMAYANA == "Ramayana"
    assert META_SOURCE == "source"
    assert META_CHAPTER == "chapter"
    assert META_VERSE == "verse"


def test_config_reads_version():
    from app.config import settings
    assert settings.app_version != ""


def test_config_has_empty_secrets():
    from app.config import settings
    assert settings.llm_api_key == ""
    assert settings.database_url == ""


def test_retrieved_story_has_source():
    story = RetrievedStory(
        title="Test",
        summary="summary",
        teaching="teaching",
        source="Ramayana",
    )
    assert story.source == "Ramayana"


def test_retrieved_verse_has_source():
    verse = RetrievedVerse(
        text="text",
        translation="trans",
        chapter=2,
        verse=47,
        source="Bhagavad Gita",
    )
    assert verse.source == "Bhagavad Gita"


def test_rrf_fusion_basic():
    from app.rag.rrf import RankedItem, reciprocal_rank_fusion

    list_a = [
        RankedItem(id="1", document="doc1", metadata={}, source="gita"),
        RankedItem(id="2", document="doc2", metadata={}, source="gita"),
        RankedItem(id="3", document="doc3", metadata={}, source="gita"),
    ]
    list_b = [
        RankedItem(id="2", document="doc2", metadata={}, source="bm25"),
        RankedItem(id="1", document="doc1", metadata={}, source="bm25"),
        RankedItem(id="4", document="doc4", metadata={}, source="bm25"),
    ]

    fused = reciprocal_rank_fusion([list_a, list_b])
    assert len(fused) == 4
    ids = [item.id for item in fused]
    assert ids[0] == "1" or ids[0] == "2"
    for item in fused:
        assert item.score > 0


def test_rrf_fusion_single_list():
    from app.rag.rrf import RankedItem, reciprocal_rank_fusion

    items = [
        RankedItem(id="a", document="doc_a", metadata={}),
        RankedItem(id="b", document="doc_b", metadata={}),
    ]
    fused = reciprocal_rank_fusion([items])
    assert len(fused) == 2
    assert fused[0].id == "a"
    assert fused[0].score > fused[1].score


def test_rrf_fusion_empty():
    from app.rag.rrf import reciprocal_rank_fusion

    fused = reciprocal_rank_fusion([[], []])
    assert len(fused) == 0


def test_bm25_tsquery_basic():
    from app.rag.bm25 import _to_tsquery

    result = _to_tsquery("I feel fear about my career")
    assert "fear" in result
    assert "career" in result
    assert "feel" not in result
    assert "&" in result


def test_bm25_tsquery_sanskrit():
    from app.rag.bm25 import _to_tsquery

    result = _to_tsquery("nishkama karma yoga")
    assert "nishkama" in result
    assert "karma" in result
    assert "yoga" in result


def test_bm25_tsquery_empty():
    from app.rag.bm25 import _to_tsquery

    result = _to_tsquery("   ")
    assert result == ""


def test_config_has_hybrid_settings():
    from app.config import settings
    assert settings.hybrid_bm25_k == 10
    assert settings.rrf_k == 60
