"""Validación de calidad de datos — ver /DOCS/qa_checklist.md."""

from __future__ import annotations

import logging
from collections import Counter

from scraper import config
from scraper.normalize import BookRecord

logger = logging.getLogger("scraper.qa")

# Umbrales de nulos aceptables por campo (ver qa_checklist.md §3)
NULL_THRESHOLDS = {
    "title": 0.0,
    "product_url": 0.0,
    "price": 0.0,
    "availability": 0.0,
    "category": 0.0,
    "rating": 0.05,
    "description": 0.15,
}


def run_qa(records: list[BookRecord], expected_total: int | None = None) -> dict:
    """Devuelve un reporte de QA; no lanza excepción — el llamador decide
    si un reporte con `passed: False` bloquea la publicación del dataset.
    """
    total = len(records)
    report: dict = {"total_records": total, "checks": {}}

    # 1. Conteo
    if expected_total is not None:
        report["checks"]["count"] = {
            "expected": expected_total,
            "actual": total,
            "passed": total == expected_total,
        }

    # 2. Duplicados
    url_counts = Counter(r.product_url for r in records)
    duplicate_urls = {url: c for url, c in url_counts.items() if c > 1}
    report["checks"]["duplicates"] = {
        "duplicate_product_urls": len(duplicate_urls),
        "passed": len(duplicate_urls) == 0,
    }

    # 3. Nulos
    null_report = {}
    all_passed_nulls = True
    for field_name, threshold in NULL_THRESHOLDS.items():
        nulls = sum(1 for r in records if getattr(r, field_name, None) in (None, ""))
        ratio = nulls / total if total else 0.0
        passed = ratio <= threshold
        all_passed_nulls = all_passed_nulls and passed
        null_report[field_name] = {"null_ratio": round(ratio, 4), "threshold": threshold, "passed": passed}
    report["checks"]["nulls"] = null_report

    # 4. Rangos
    invalid_ratings = sum(1 for r in records if r.rating is not None and r.rating not in range(1, 6))
    invalid_prices = sum(1 for r in records if r.price < 0)
    invalid_currency = sum(1 for r in records if r.currency != "GBP")
    report["checks"]["ranges"] = {
        "invalid_ratings": invalid_ratings,
        "invalid_prices": invalid_prices,
        "invalid_currency": invalid_currency,
        "passed": invalid_ratings == 0 and invalid_prices == 0 and invalid_currency == 0,
    }

    report["passed"] = (
        report["checks"].get("count", {}).get("passed", True)
        and report["checks"]["duplicates"]["passed"]
        and all_passed_nulls
        and report["checks"]["ranges"]["passed"]
    )

    level = logging.INFO if report["passed"] else logging.WARNING
    logger.log(level, "qa_report total=%d passed=%s", total, report["passed"])
    return report
