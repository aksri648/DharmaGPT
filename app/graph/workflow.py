from langgraph.graph import StateGraph, START, END
from app.graph.state import GraphState
from app.graph.nodes.query_analyzer import query_analyzer_node
from app.graph.nodes.scripture_retrieval import scripture_retrieval_node
from app.graph.nodes.context_selection import context_selection_node
from app.graph.nodes.response_generation import response_generation_node
from app.graph.nodes.citation_validation import citation_validation_node


def create_graph() -> StateGraph:
    builder = StateGraph(GraphState)

    builder.add_node("query_analyzer", query_analyzer_node)
    builder.add_node("scripture_retrieval", scripture_retrieval_node)
    builder.add_node("context_selection", context_selection_node)
    builder.add_node("response_generation", response_generation_node)
    builder.add_node("citation_validation", citation_validation_node)

    builder.add_edge(START, "query_analyzer")
    builder.add_edge("query_analyzer", "scripture_retrieval")
    builder.add_edge("scripture_retrieval", "context_selection")
    builder.add_edge("context_selection", "response_generation")
    builder.add_edge("response_generation", "citation_validation")
    builder.add_edge("citation_validation", END)

    return builder.compile()


dharma_graph = create_graph()
