"""Exportación CSV/JSON según /DOCS/data_contract.md §5-6."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path

from scraper.normalize import BookRecord

logger = logging.getLogger("scraper.export")

CSV_FIELDNAMES = [
    "title", "product_url", "price", "currency", "availability", "rating",
    "category", "scraped_at", "upc", "image_url", "price_excl_tax",
    "price_incl_tax", "tax", "stock_count", "reviews_count", "description",
]


def export_json(records: list[BookRecord], path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = [r.to_dict() for r in records]
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("exported_json path=%s records=%d", path, len(records))


def export_csv(records: list[BookRecord], path: str) -> None:
    """UTF-8 sin BOM, delimitador coma, QUOTE_MINIMAL (ver data_contract.md §6)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in records:
            writer.writerow(r.to_dict())
    logger.info("exported_csv path=%s records=%d", path, len(records))
