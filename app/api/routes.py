import tempfile
import os
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from app.config import settings
from app.api.schemas import ChatRequest, ChatResponse, HealthResponse, IngestResponse
from app.graph.state import GraphState
from app.graph.workflow import dharma_graph
from app.rag.loaders import load_pdf
from app.rag.splitter import get_text_splitter
from app.rag.vectorstore import get_gita_store, get_ramayana_store
from app.knowledge_base.constants import (
    SOURCE_BHAGAVAD_GITA, SOURCE_RAMAYANA,
    META_SOURCE, META_PAGE, META_THEMES, META_EMOTIONS,
)

logger = logging.getLogger(__name__)

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(version=settings.app_version)


@router.post("/ingest/pdf", response_model=IngestResponse)
async def ingest_pdf(
    file: UploadFile = File(...),
    source: str = Form(...),
    speaker: str | None = Form(None),
    themes: str = Form(""),
    emotions: str = Form(""),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    if source not in ("gita", "ramayana"):
        raise HTTPException(status_code=400, detail="source must be 'gita' or 'ramayana'")

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")

    theme_list = [t.strip() for t in themes.split(",") if t.strip()]
    emotion_list = [e.strip() for e in emotions.split(",") if e.strip()]

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        pages = load_pdf(tmp_path)

        source_name = SOURCE_BHAGAVAD_GITA if source == "gita" else SOURCE_RAMAYANA
        docs = []
        for i, page in enumerate(pages):
            page.metadata.update({
                META_SOURCE: source_name,
                META_PAGE: i + 1,
                META_THEMES: theme_list,
                META_EMOTIONS: emotion_list,
            })
            if speaker:
                page.metadata["speaker"] = speaker
            docs.append(page)

        splitter = get_text_splitter()
        splits = splitter.split_documents(docs)

        store = get_gita_store() if source == "gita" else get_ramayana_store()
        ids = store.add_documents(splits)
        collection = settings.pgvector_collection_gita if source == "gita" else settings.pgvector_collection_ramayana

        return IngestResponse(
            status="ok",
            pages_loaded=len(pages),
            chunks_indexed=len(ids),
            source=source_name,
            collection=collection,
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception("PDF ingestion failed")
        raise HTTPException(status_code=500, detail="PDF ingestion failed")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, http_request: Request):
    try:
        llm_api_key = http_request.headers.get("x-llm-api-key", "") or settings.llm_api_key
        llm_base_url = http_request.headers.get("x-llm-base-url", "") or settings.llm_base_url

        initial_state: GraphState = {
            "messages": [],
            "query": body.message,
            "query_analysis": None,
            "analysis_raw": None,
            "gita_verses": [],
            "ramayana_verses": [],
            "stories": [],
            "selected_verses": [],
            "selected_stories": [],
            "context": "",
            "response": "",
            "citations": [],
            "validation_result": "",
            "final_response": "",
            "llm_api_key": llm_api_key,
            "llm_base_url": llm_base_url,
        }

        config = {
            "configurable": {"thread_id": body.thread_id},
            "recursion_limit": settings.graph_recursion_limit,
        }

        result = await dharma_graph.ainvoke(initial_state, config)

        return ChatResponse(
            response=result.get("final_response", result.get("response", "")),
            query_analysis=result.get("query_analysis"),
            verses_used=result.get("selected_verses", []),
            stories_used=result.get("selected_stories", []),
            citations=result.get("citations", []),
            validation_status=result.get("validation_result"),
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception("Chat request failed")
        raise HTTPException(status_code=500, detail="Chat request failed")
