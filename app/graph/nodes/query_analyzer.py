import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.graph.state import GraphState
from app.graph.llm import build_llm
from app.knowledge_base.taxonomies import EMOTIONS, THEMES, CATEGORIES

logger = logging.getLogger(__name__)

ANALYZER_PROMPT = f"""You are a query analyzer for DharmaGPT. Your task is to analyze a user's life problem and classify it.

Extract exactly:
1. emotion — the PRIMARY emotion from: {', '.join(EMOTIONS)}
2. theme — the PRIMARY dharma theme from: {', '.join(THEMES)}
3. category — the life category from: {', '.join(CATEGORIES)}
4. sub_emotions — any secondary emotions (list)
5. confidence — how confident you are in your analysis (0.0 to 1.0)

Respond ONLY with a valid JSON object like this:
{{"emotion": "fear", "theme": "courage", "category": "career", "sub_emotions": ["anxiety", "confusion"], "confidence": 0.85}}

Do not include any other text."""


def query_analyzer_node(state: GraphState) -> dict:
    llm = build_llm(
        temperature=settings.query_analyzer_temperature,
        max_tokens=settings.query_analyzer_max_tokens,
        api_key_override=state.get("llm_api_key"),
        base_url_override=state.get("llm_base_url"),
    )

    messages = [
        SystemMessage(content=ANALYZER_PROMPT),
        HumanMessage(content=state.get("query", "")),
    ]

    try:
        response = llm.invoke(messages)
        return {"analysis_raw": response.content}
    except Exception:
        logger.exception("Query analyzer LLM call failed")
        return {"analysis_raw": None}
