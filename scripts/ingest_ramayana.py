"""
Ingest Ramayana passages into PostgreSQL + pgvector.

Expected data format: JSON array of objects with fields:
  book, chapter, text, translation, themes, emotions, character, category

Usage:
  python scripts/ingest_ramayana.py --input data/ramayana/passages.json
  python scripts/ingest_ramayana.py --input data/ramayana/passages.json --chunk-size 500
"""

import json
import argparse
from langchain_core.documents import Document
from app.config import settings
from app.rag.vectorstore import get_ramayana_store
from app.rag.splitter import get_text_splitter
from app.knowledge_base.constants import (
    SOURCE_RAMAYANA,
    META_SOURCE, META_BOOK, META_CHAPTER,
    META_TEXT, META_TRANSLATION, META_THEMES,
    META_EMOTIONS, META_CHARACTER, META_CATEGORY,
)


def load_ramayana_data(path: str) -> list[dict]:
    with open(path, "r") as f:
        return json.load(f)


def build_documents(passages: list[dict]) -> list[Document]:
    docs = []
    for p in passages:
        book = p.get(META_BOOK, "")
        chapter = p.get(META_CHAPTER, 0)
        content = f"{book}, Chapter {chapter}: {p.get(META_TEXT, '')}"
        metadata = {
            META_SOURCE: SOURCE_RAMAYANA,
            META_BOOK: book,
            META_CHAPTER: chapter,
            META_TEXT: p.get(META_TEXT, ""),
            META_TRANSLATION: p.get(META_TRANSLATION, ""),
            META_THEMES: p.get(META_THEMES, []),
            META_EMOTIONS: p.get(META_EMOTIONS, []),
            META_CHARACTER: p.get(META_CHARACTER),
            META_CATEGORY: p.get(META_CATEGORY),
        }
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


def ingest(input_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    data = load_ramayana_data(input_path)
    docs = build_documents(data)
    splitter = get_text_splitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splits = splitter.split_documents(docs)
    store = get_ramayana_store()
    ids = store.add_documents(splits)
    collection = settings.pgvector_collection_ramayana
    print(f"Ingested {len(ids)} passages into pgvector collection '{collection}'")
    return ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Ramayana passages into pgvector")
    parser.add_argument("--input", required=True, help="Path to JSON file with passages")
    parser.add_argument("--chunk-size", type=int, default=500, help="Character chunk size")
    parser.add_argument("--chunk-overlap", type=int, default=50, help="Chunk overlap")
    args = parser.parse_args()
    ingest(args.input, args.chunk_size, args.chunk_overlap)
