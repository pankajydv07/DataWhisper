import hashlib
import time
from typing import Any

_cache: dict[str, dict[str, Any]] = {}


def normalise_question(question: str) -> str:
    return " ".join(question.lower().strip().split())


def make_key(*parts: object) -> str:
    raw_key = "|".join(str(part) for part in parts)
    return hashlib.md5(raw_key.encode("utf-8")).hexdigest()


def cache_get(key: str) -> Any | None:
    entry = _cache.get(key)
    if entry is None:
        return None

    if time.time() >= entry["expires"]:
        _cache.pop(key, None)
        return None

    return entry["value"]


def cache_set(key: str, value: Any, ttl_seconds: int) -> None:
    _cache[key] = {
        "value": value,
        "expires": time.time() + ttl_seconds,
    }
