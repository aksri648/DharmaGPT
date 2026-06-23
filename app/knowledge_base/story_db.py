import json
from pathlib import Path

_STORIES_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "stories.json"


def load_stories() -> list[dict]:
    if not _STORIES_FILE.exists():
        return []
    try:
        with open(_STORIES_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


STORIES: list[dict] = load_stories()
