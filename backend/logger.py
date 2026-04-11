import logging
import os
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("datawhisper")
logger.setLevel(logging.INFO)

handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
handler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
)

if not logger.handlers:
    logger.addHandler(handler)


def is_debug_enabled() -> bool:
    return os.getenv("DEBUG", "false").lower() == "true"
