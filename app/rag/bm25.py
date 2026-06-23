import logging
import psycopg
from app.config import settings

logger = logging.getLogger(__name__)

_K = 1.2
_B = 0.75


def _get_conn() -> psycopg.Connection:
    return psycopg.connect(settings.database_url)


def bm25_search(
    collection: str,
    query: str,
    k: int = 10,
    metadata_filter: dict | None = None,
) -> list[dict]:
    """PostgreSQL full-text BM25 search against langchain_pg_embedding rows."""
    tsquery = _to_tsquery(query)
    if not tsquery:
        return []

    sql = """
        WITH stats AS (
            SELECT
                AVG(LENGTH(document)) AS avg_doc_len,
                COUNT(*) AS total_docs
            FROM langchain_pg_embedding e
            JOIN langchain_pg_collection c ON e.collection_id = c.id
            WHERE c.name = %s
        ),
        scored AS (
            SELECT
                e.id,
                e.document,
                e.cmetadata,
                ts_rank_cd(
                    to_tsvector('english', COALESCE(e.document, '')),
                    to_tsquery('english', %s),
                    32
                ) AS ts_rank,
                ts_length(to_tsvector('english', COALESCE(e.document, ''))) AS doc_len
            FROM langchain_pg_embedding e
            JOIN langchain_pg_collection c ON e.collection_id = c.id
            WHERE c.name = %s
              AND to_tsvector('english', COALESCE(e.document, ''))
                  @@ to_tsquery('english', %s)
        )
        SELECT
            s.id,
            s.document,
            s.cmetadata,
            s.ts_rank,
            s.doc_len,
            (s.ts_rank * (%s + 1)) / (s.ts_rank + %s * (1 - %s + %s * s.doc_len / st.avg_doc_len)) AS bm25_score
        FROM scored s, stats st
        ORDER BY bm25_score DESC
        LIMIT %s;
    """

    try:
        conn = _get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (
                    collection,
                    tsquery,
                    collection,
                    tsquery,
                    _K,
                    _B,
                    _B,
                    k,
                ))
                rows = cur.fetchall()
        finally:
            conn.close()
    except Exception:
        logger.exception("BM25 search failed for collection '%s'", collection)
        return []

    results = []
    for row in rows:
        doc_id, document, metadata, ts_rank, doc_len, bm25_score = row
        results.append({
            "id": str(doc_id),
            "document": document or "",
            "metadata": metadata or {},
            "bm25_score": float(bm25_score),
            "ts_rank": float(ts_rank),
        })
    return results


def _to_tsquery(query: str) -> str:
    """Convert free-text query to a PostgreSQL tsquery string."""
    words = query.lower().split()
    stop_words = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
        "you", "your", "yours", "yourself", "yourselves",
        "he", "him", "his", "himself", "she", "her", "hers", "herself",
        "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
        "what", "which", "who", "whom", "this", "that", "these", "those",
        "am", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "having", "do", "does", "did", "doing",
        "a", "an", "the", "and", "but", "if", "or", "because", "as",
        "until", "while", "of", "at", "by", "for", "with", "about",
        "against", "between", "through", "during", "before", "after",
        "above", "below", "to", "from", "up", "down", "in", "out",
        "on", "off", "over", "under", "again", "further", "then", "once",
        "here", "there", "when", "where", "why", "how", "all", "both",
        "each", "few", "more", "most", "other", "some", "such", "no",
        "nor", "not", "only", "own", "same", "so", "than", "too",
        "very", "s", "t", "can", "will", "just", "don", "should", "now",
        "feel", "feeling", "feels",
    }
    filtered = [w for w in words if w not in stop_words and len(w) > 1]
    if not filtered:
        filtered = [w for w in words if len(w) > 0]
    if not filtered:
        return ""
    return " & ".join(filtered)


def bm25_search_gita(query: str, k: int = 10, metadata_filter: dict | None = None) -> list[dict]:
    return bm25_search(settings.pgvector_collection_gita, query, k, metadata_filter)


def bm25_search_ramayana(query: str, k: int = 10, metadata_filter: dict | None = None) -> list[dict]:
    return bm25_search(settings.pgvector_collection_ramayana, query, k, metadata_filter)


def bm25_search_stories(query: str, k: int = 10, metadata_filter: dict | None = None) -> list[dict]:
    return bm25_search(settings.pgvector_collection_stories, query, k, metadata_filter)
