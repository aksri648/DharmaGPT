import logging
from concurrent.futures import ThreadPoolExecutor
from langchain_postgres import PGVector
from langchain_core.documents import Document
from app.config import settings
from app.knowledge_base.constants import META_EMOTIONS, META_THEMES, META_CATEGORY
from app.rag.bm25 import bm25_search_gita, bm25_search_ramayana, bm25_search_stories
from app.rag.rrf import RankedItem, reciprocal_rank_fusion

logger = logging.getLogger(__name__)


def similarity_search(
    store: PGVector,
    query: str,
    metadata_filter: dict | None = None,
    k: int | None = None,
) -> list[Document]:
    k = k or settings.retriever_k
    return store.similarity_search(
        query=query,
        k=k,
        filter=metadata_filter,
        score_threshold=settings.retriever_score_threshold,
    )


def _doc_to_ranked(doc: Document, source: str) -> RankedItem:
    return RankedItem(
        id=doc.metadata.get("id", doc.page_content[:64]),
        document=doc.page_content,
        metadata=doc.metadata,
        source=source,
    )


def _bm25_to_ranked(item: dict, source: str) -> RankedItem:
    return RankedItem(
        id=item["id"],
        document=item["document"],
        metadata=item["metadata"],
        source=source,
    )


def hybrid_search_gita(
    query: str,
    metadata_filter: dict | None = None,
    k: int | None = None,
) -> list[RankedItem]:
    k = k or settings.retriever_k

    from app.rag.vectorstore import get_gita_store

    semantic_docs = similarity_search(get_gita_store(), query, metadata_filter, k)
    bm25_items = bm25_search_gita(query, k=k, metadata_filter=metadata_filter)

    semantic_ranked = [_doc_to_ranked(d, "gita") for d in semantic_docs]
    bm25_ranked = [_bm25_to_ranked(i, "gita") for i in bm25_items]

    return reciprocal_rank_fusion([semantic_ranked, bm25_ranked])


def hybrid_search_ramayana(
    query: str,
    metadata_filter: dict | None = None,
    k: int | None = None,
) -> list[RankedItem]:
    k = k or settings.retriever_k

    from app.rag.vectorstore import get_ramayana_store

    semantic_docs = similarity_search(get_ramayana_store(), query, metadata_filter, k)
    bm25_items = bm25_search_ramayana(query, k=k, metadata_filter=metadata_filter)

    semantic_ranked = [_doc_to_ranked(d, "ramayana") for d in semantic_docs]
    bm25_ranked = [_bm25_to_ranked(i, "ramayana") for i in bm25_items]

    return reciprocal_rank_fusion([semantic_ranked, bm25_ranked])


def hybrid_search_stories(
    query: str,
    metadata_filter: dict | None = None,
    k: int | None = None,
) -> list[RankedItem]:
    k = k or settings.retriever_k

    from app.rag.vectorstore import get_stories_store

    semantic_docs = similarity_search(get_stories_store(), query, metadata_filter, k)
    bm25_items = bm25_search_stories(query, k=k, metadata_filter=metadata_filter)

    semantic_ranked = [_doc_to_ranked(d, "stories") for d in semantic_docs]
    bm25_ranked = [_bm25_to_ranked(i, "stories") for i in bm25_items]

    return reciprocal_rank_fusion([semantic_ranked, bm25_ranked])


def _build_filter(
    emotion: str | None,
    theme: str | None,
    category: str | None,
) -> dict | None:
    parts = []
    if emotion:
        parts.append({META_EMOTIONS: {"$contains": emotion}})
    if theme:
        parts.append({META_THEMES: {"$contains": theme}})
    if category:
        parts.append({META_CATEGORY: category})
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    return {"$and": parts}


def combined_search(
    query: str,
    emotion: str | None = None,
    theme: str | None = None,
    category: str | None = None,
) -> tuple[list[RankedItem], list[RankedItem], list[RankedItem]]:
    metadata_filter = _build_filter(emotion, theme, category)

    with ThreadPoolExecutor(max_workers=3) as executor:
        gita_future = executor.submit(hybrid_search_gita, query, metadata_filter)
        ramayana_future = executor.submit(hybrid_search_ramayana, query, metadata_filter)
        story_future = executor.submit(hybrid_search_stories, query, metadata_filter)

        gita_results = gita_future.result()
        ramayana_results = ramayana_future.result()
        story_results = story_future.result()

    return gita_results, ramayana_results, story_results
