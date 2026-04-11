from collections import defaultdict, deque
from typing import Deque

MAX_TURNS = 3

_histories: dict[str, Deque[tuple[str, str]]] = defaultdict(
    lambda: deque(maxlen=MAX_TURNS)
)


def get_history_text(user_id: str, session_id: str) -> str:
    history_key = f"{user_id}:{session_id}"
    turns = _histories[history_key]

    if not turns:
        return "No prior turns."

    return "\n".join(f"User: {question}\nSQL: {sql}" for question, sql in turns)


def add_turn(user_id: str, session_id: str, question: str, sql: str) -> None:
    history_key = f"{user_id}:{session_id}"
    _histories[history_key].append((question, sql))
