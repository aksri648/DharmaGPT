"""
Ingest Bhagavad Gita verses into PostgreSQL + pgvector.

Expected data format: JSON array of objects with fields:
  chapter, verse, text, translation, speaker, commentary, themes, emotions, character, category

Usage:
  python scripts/ingest_gita.py --input data/gita/verses.json
  python scripts/ingest_gita.py --input data/gita/verses.json --chunk-size 500 --chunk-overlap 50
"""

import json
import argparse
from langchain_core.documents import Document
from app.config import settings
from app.rag.vectorstore import get_gita_store
from app.rag.splitter import get_text_splitter
from app.knowledge_base.constants import (
    SOURCE_BHAGAVAD_GITA,
    META_SOURCE, META_CHAPTER, META_VERSE,
    META_TEXT, META_TRANSLATION, META_SPEAKER,
    META_COMMENTARY, META_THEMES, META_EMOTIONS,
    META_CHARACTER, META_CATEGORY,
)


def load_gita_data(path: str) -> list[dict]:
    with open(path, "r") as f:
        return json.load(f)


def build_documents(verses: list[dict]) -> list[Document]:
    docs = []
    for v in verses:
        content = f"Chapter {v['chapter']}, Verse {v['verse']}: {v['translation']}"
        metadata = {
            META_SOURCE: SOURCE_BHAGAVAD_GITA,
            META_CHAPTER: v.get(META_CHAPTER),
            META_VERSE: v.get(META_VERSE),
            META_TEXT: v.get(META_TEXT, ""),
            META_TRANSLATION: v.get(META_TRANSLATION, ""),
            META_SPEAKER: v.get(META_SPEAKER, "Krishna"),
            META_COMMENTARY: v.get(META_COMMENTARY, ""),
            META_THEMES: v.get(META_THEMES, []),
            META_EMOTIONS: v.get(META_EMOTIONS, []),
            META_CHARACTER: v.get(META_CHARACTER),
            META_CATEGORY: v.get(META_CATEGORY),
        }
        docs.append(Document(page_content=content, metadata=metadata))
    return docs


def ingest(input_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    data = load_gita_data(input_path)
    docs = build_documents(data)
    splitter = get_text_splitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splits = splitter.split_documents(docs)
    store = get_gita_store()
    ids = store.add_documents(splits)
    collection = settings.pgvector_collection_gita
    print(f"Ingested {len(ids)} verses into pgvector collection '{collection}'")
    return ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Bhagavad Gita verses into pgvector")
    parser.add_argument("--input", required=True, help="Path to JSON file with verses")
    parser.add_argument("--chunk-size", type=int, default=500, help="Character chunk size")
    parser.add_argument("--chunk-overlap", type=int, default=50, help="Chunk overlap")
    args = parser.parse_args()
    ingest(args.input, args.chunk_size, args.chunk_overlap)
