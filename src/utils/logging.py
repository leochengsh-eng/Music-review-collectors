from __future__ import annotations
import logging
from pathlib import Path

def configure_logging(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler()])
    return logging.getLogger("album_review_digest")
