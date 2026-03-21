import os
import pickle
from typing import List, Tuple

HISTORY_PATH = "chat_history.pkl"
MAX_HISTORY_ITEMS = 200


def _normalize_history(raw_history) -> List[Tuple[str, str]]:
    """Keep only valid (question, answer) string tuples."""
    normalized = []
    if not isinstance(raw_history, list):
        return normalized

    for item in raw_history:
        if isinstance(item, tuple) and len(item) == 2:
            question, answer = item
            if isinstance(question, str) and isinstance(answer, str):
                normalized.append((question, answer))
    return normalized


def load_chat_history() -> List[Tuple[str, str]]:
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "rb") as f:
                return _normalize_history(pickle.load(f))[-MAX_HISTORY_ITEMS:]
        except Exception:
            # Corrupted history should not break app startup.
            return []
    return []


def save_chat_history(history) -> None:
    trimmed_history = history[-MAX_HISTORY_ITEMS:]
    with open(HISTORY_PATH, "wb") as f:
        pickle.dump(trimmed_history, f)
