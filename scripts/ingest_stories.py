"""
Ingest story database into PostgreSQL + pgvector.

Loads stories from data/stories.json and indexes into pgvector.

Usage:
  python scripts/ingest_stories.py
"""

from langchain_core.documents import Document
from app.config import settings
from app.rag.vectorstore import get_stories_store
from app.rag.splitter import get_text_splitter
from app.knowledge_base.story_db import STORIES
from app.knowledge_base.constants import (
    META_SOURCE, META_TITLE, META_BOOK, META_CHAPTER,
    META_SUMMARY, META_TEACHING, META_THEMES,
    META_EMOTIONS, META_CHARACTERS, META_CATEGORY,
)


def build_documents() -> list[Document]:
    docs = []
    for s in STORIES:
        content = f"{s['title']}: {s['summary']}\n\nTeaching: {s['teaching']}"
        metadata = {
            META_SOURCE: s.get(META_SOURCE, "Ramayana"),
            META_TITLE: s.get(META_TITLE, ""),
            META_BOOK: s.get(META_BOOK, ""),
            META_CHAPTER: s.get(META_CHAPTER),
            META_SUMMARY: s.get(META_SUMMARY, ""),
            META_TEACHING: s.get(META_TEACHING, ""),
            META_THEMES: s.get(META_THEMES, []),
            META_EMOTIONS: s.get(META_EMOTIONS, []),
            META_CHARACTERS: s.get(META_CHARACTERS, []),
            META_CATEGORY: s.get(META_CATEGORY),
        }
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


def ingest():
    docs = build_documents()
    splitter = get_text_splitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)
    store = get_stories_store()
    ids = store.add_documents(splits)
    collection = settings.pgvector_collection_stories
    print(f"Ingested {len(ids)} story chunks into pgvector collection '{collection}'")
    return ids


if __name__ == "__main__":
    ingest()
