"""
Ingest scripture PDFs into PostgreSQL + pgvector.

Loads a PDF, splits into chunks, enriches with metadata, and indexes
into the appropriate pgvector collection.

Usage:
  # Bhagavad Gita PDF
  python scripts/ingest_pdf.py --pdf data/gita/gita.pdf --source gita

  # Ramayana PDF
  python scripts/ingest_pdf.py --pdf data/ramayana/ramayana.pdf --source ramayana

  # With custom metadata
  python scripts/ingest_pdf.py --pdf data/gita/gita.pdf --source gita \
    --speaker Krishna --themes duty detachment --emotions fear anxiety

  # Dry run (inspect chunks before indexing)
  python scripts/ingest_pdf.py --pdf data/gita/gita.pdf --source gita --dry-run

  # Custom chunk size
  python scripts/ingest_pdf.py --pdf data/gita/gita.pdf --source gita \
    --chunk-size 800 --chunk-overlap 150
"""

import argparse
import re
from langchain_core.documents import Document
from app.config import settings
from app.rag.vectorstore import get_gita_store, get_ramayana_store
from app.rag.splitter import get_text_splitter
from app.rag.loaders import load_pdf
from app.knowledge_base.constants import (
    SOURCE_BHAGAVAD_GITA, SOURCE_RAMAYANA,
    META_SOURCE, META_PAGE, META_THEMES, META_EMOTIONS,
    META_CHAPTER, META_VERSE, META_SPEAKER,
)

CHAPTER_RE = re.compile(r"(?:chapter| Chapter |\bCh\.?)\s*(\d+)")
VERSE_RE = re.compile(r"(?:verse| Verse |\bv\.?\s*|sloka\s*|śloka\s*)[:\s]*(\d+)", re.IGNORECASE)


def parse_chapter_verse(text: str) -> tuple[int | None, int | None]:
    match = CHAPTER_RE.search(text)
    chapter = int(match.group(1)) if match else None
    match = VERSE_RE.search(text)
    verse = int(match.group(1)) if match else None
    return chapter, verse


def build_documents(
    pages: list[Document],
    source: str,
    speaker: str | None,
    themes: list[str],
    emotions: list[str],
) -> list[Document]:
    source_name = SOURCE_BHAGAVAD_GITA if source == "gita" else SOURCE_RAMAYANA
    docs = []
    for i, page in enumerate(pages):
        chapter, verse = parse_chapter_verse(page.page_content)
        metadata: dict = {
            META_SOURCE: source_name,
            META_PAGE: i + 1,
            META_CHAPTER: chapter,
            META_VERSE: verse,
            META_SPEAKER: speaker,
            META_THEMES: themes,
            META_EMOTIONS: emotions,
        }
        docs.append(Document(page_content=page.page_content, metadata=metadata))
    return docs


def ingest(
    pdf_path: str,
    source: str,
    speaker: str | None = None,
    themes: list[str] | None = None,
    emotions: list[str] | None = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    dry_run: bool = False,
):
    print(f"Loading PDF: {pdf_path}")
    pages = load_pdf(pdf_path)
    print(f"  -> {len(pages)} pages loaded")

    docs = build_documents(
        pages, source, speaker, themes or [], emotions or [],
    )

    splitter = get_text_splitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splits = splitter.split_documents(docs)
    print(f"  -> {len(splits)} chunks after splitting")

    if dry_run:
        print("\n=== DRY RUN - first 3 chunks ===")
        for i, chunk in enumerate(splits[:3]):
            meta = chunk.metadata
            print(f"\n--- Chunk {i + 1} (page {meta.get(META_PAGE)}) ---")
            ch = meta.get(META_CHAPTER)
            vs = meta.get(META_VERSE)
            pieces = []
            if ch:
                pieces.append(f"Ch {ch}")
            if vs:
                pieces.append(f"V {vs}")
            ref = ", ".join(pieces)
            print(f"  Reference: {ref}" if ref else "  Reference: unknown")
            print(f"  Content: {chunk.page_content[:200]}...")
        print(f"\nTotal chunks that would be indexed: {len(splits)}")
        return

    store = get_gita_store() if source == "gita" else get_ramayana_store()
    ids = store.add_documents(splits)
    collection_name = settings.pgvector_collection_gita if source == "gita" else settings.pgvector_collection_ramayana
    print(f"  -> Ingested {len(ids)} chunks into pgvector collection '{collection_name}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest scripture PDF into pgvector")
    parser.add_argument("--pdf", required=True, help="Path to PDF file")
    parser.add_argument("--source", required=True, choices=["gita", "ramayana"], help="Scripture source")
    parser.add_argument("--speaker", help="Default speaker (e.g. Krishna)")
    parser.add_argument("--themes", nargs="*", default=[], help="Theme tags (e.g. duty courage detachment)")
    parser.add_argument("--emotions", nargs="*", default=[], help="Emotion tags (e.g. fear anxiety)")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Character chunk size")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="Chunk overlap")
    parser.add_argument("--dry-run", action="store_true", help="Print chunks without indexing")
    args = parser.parse_args()
    ingest(
        args.pdf, args.source, args.speaker,
        args.themes, args.emotions,
        args.chunk_size, args.chunk_overlap,
        args.dry_run,
    )
