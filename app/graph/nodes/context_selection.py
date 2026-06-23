from app.config import settings
from app.graph.state import GraphState
from app.knowledge_base.schemas import RetrievedVerse


def context_selection_node(state: GraphState) -> dict:
    all_verses = list(state.get("gita_verses", []))
    all_verses.extend(state.get("ramayana_verses", []))

    all_verses.sort(key=lambda v: v.score, reverse=True)
    all_stories = list(state.get("stories", []))
    all_stories.sort(key=lambda s: s.score, reverse=True)

    max_verses = settings.max_selected_verses
    max_stories = settings.max_selected_stories

    selected_verses: list[RetrievedVerse] = []
    seen = set()
    for v in all_verses:
        key = (v.source, v.chapter, v.verse)
        if key not in seen:
            selected_verses.append(v)
            seen.add(key)
        if len(selected_verses) >= max_verses:
            break

    if not selected_verses and all_verses:
        selected_verses = all_verses[:max_verses]

    selected_stories = all_stories[:max_stories]

    return {
        "selected_verses": selected_verses,
        "selected_stories": selected_stories,
    }
