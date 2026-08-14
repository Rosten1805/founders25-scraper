"""Checkpoint de reanudación — ver /DOCS/pagination_strategy.md §3."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("scraper.checkpoint")


@dataclass
class Checkpoint:
    last_page_completed: int = 0
    visited_detail_urls: list[str] = field(default_factory=list)
    total_records_so_far: int = 0
    updated_at: str | None = None

    @classmethod
    def load(cls, path: str) -> "Checkpoint":
        p = Path(path)
        if not p.exists():
            logger.info("checkpoint_not_found path=%s starting_fresh=true", path)
            return cls()
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            logger.info("checkpoint_loaded path=%s last_page_completed=%s", path, data.get("last_page_completed"))
            return cls(**data)
        except (json.JSONDecodeError, TypeError) as exc:
            logger.warning("checkpoint_corrupt path=%s error=%s starting_fresh=true", path, exc)
            return cls()

    def save(self, path: str) -> None:
        self.updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(
                {
                    "last_page_completed": self.last_page_completed,
                    "visited_detail_urls": self.visited_detail_urls,
                    "total_records_so_far": self.total_records_so_far,
                    "updated_at": self.updated_at,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        logger.debug("checkpoint_saved path=%s last_page_completed=%d", path, self.last_page_completed)
