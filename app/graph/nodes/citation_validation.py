import re
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.graph.state import GraphState
from app.graph.llm import build_llm
from app.knowledge_base.schemas import Citation
from app.knowledge_base.constants import SOURCE_BHAGAVAD_GITA, SOURCE_RAMAYANA

logger = logging.getLogger(__name__)

CITATION_SKIPPED = "Validation skipped — LLM unavailable"

VALIDATION_PROMPT = """You are a citation validator. Your task is to verify that every scripture citation in the response actually exists in the provided context.

Rules:
1. For each verse citation (e.g., "Bhagavad Gita 2.47"), check if that exact verse (chapter and verse number) appears in the retrieved verses context.
2. For each story reference, check if it matches a story in the context.
3. If a citation is found in the context, mark it as valid.
4. If a citation is NOT found in the context, mark it as invalid and flag it as a potential hallucination.

Output a JSON array of citations:
[
  {"source": "Bhagavad Gita", "chapter": 2, "verse": 47, "text": "...", "valid": true},
  {"source": "Ramayana", "chapter": null, "verse": null, "text": "...", "valid": true}
]

If everything is valid, just confirm: {"status": "all_valid"}
If any citation is invalid, list ALL citations with their validity."""

VERSE_CITATION_RE = re.compile(
    r"(Bhagavad[_\s]?Gita|Gita|Ramayana)\s*(\d+)[.:]\s*(\d+)",
    re.IGNORECASE,
)


def _normalize_source(raw: str) -> str:
    if re.search(r"Bhagavad[_\s]?Gita|^Gita$", raw, re.IGNORECASE):
        return SOURCE_BHAGAVAD_GITA
    return SOURCE_RAMAYANA


def citation_validation_node(state: GraphState) -> dict:
    response = state.get("response", "")
    context = state.get("context", "")

    matches = VERSE_CITATION_RE.findall(response)

    citations = []
    for source_raw, chapter, verse in matches:
        source = _normalize_source(source_raw)
        context_marker = f"Chapter {chapter}, Verse {verse}"
        found = context_marker in context
        citations.append(Citation(
            source=source,
            chapter=int(chapter),
            verse=int(verse),
            text="",
            valid=found,
        ))

    llm = build_llm(
        temperature=settings.citation_validator_temperature,
        max_tokens=settings.citation_validator_max_tokens,
        api_key_override=state.get("llm_api_key"),
        base_url_override=state.get("llm_base_url"),
    )

    validation_messages = [
        SystemMessage(content=VALIDATION_PROMPT),
        HumanMessage(content=f"Retrieved Context:\n{context}\n\nResponse to Validate:\n{response}"),
    ]

    try:
        validation_result = llm.invoke(validation_messages)
        validation_text = validation_result.content
    except Exception:
        logger.exception("Citation validation LLM call failed")
        validation_text = CITATION_SKIPPED

    return {
        "citations": citations,
        "validation_result": validation_text,
        "final_response": response,
    }
