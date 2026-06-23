import json
import logging
from app.graph.state import GraphState
from app.graph.llm import build_llm
from app.templates.response import build_rag_context, build_prompt

logger = logging.getLogger(__name__)


def response_generation_node(state: GraphState) -> dict:
    query = state.get("query", "")
    verses = state.get("selected_verses", [])
    stories = state.get("selected_stories", [])
    analysis = state.get("query_analysis")

    context = build_rag_context(verses, stories)

    analysis_str = ""
    if analysis:
        analysis_str = json.dumps(analysis.model_dump(), indent=2)

    prompt = build_prompt(query, context, analysis_str)

    llm = build_llm(
        api_key_override=state.get("llm_api_key"),
        base_url_override=state.get("llm_base_url"),
    )

    try:
        response = llm.invoke(prompt)
        return {
            "context": context,
            "response": response.content,
        }
    except Exception:
        logger.exception("Response generation LLM call failed")
        return {
            "context": context,
            "response": "I apologize, but I'm unable to generate a response at this time. Please try again later.",
        }
