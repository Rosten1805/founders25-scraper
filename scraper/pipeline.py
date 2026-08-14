"""CLI del scraper — orquesta HTTP -> extract -> normalize -> export -> QA.

Uso:
    python -m scraper.pipeline --pages 50
    python -m scraper.pipeline --pages 5 --with-detail --output data/sample
"""

from __future__ import annotations

import argparse
import json
import logging
import time

from scraper import config
from scraper.checkpoint import Checkpoint
from scraper.exceptions import CircuitBreakerOpenError, NonRetryableHTTPError, RequiredFieldMissingError, ScraperError
from scraper.export import export_csv, export_json
from scraper.extract_detail import parse_detail_page
from scraper.extract_listing import parse_listing_page
from scraper.http_client import HttpClient
from scraper.logging_config import setup_logging
from scraper.normalize import build_record
from scraper.paginate import iterate_listing_pages
from scraper.qa import run_qa

logger = logging.getLogger("scraper.pipeline")


def run(
    pages: int,
    with_detail: bool,
    output_prefix: str,
    checkpoint_path: str,
    resume: bool,
) -> dict:
    checkpoint = Checkpoint.load(checkpoint_path) if resume else Checkpoint()
    start_page = checkpoint.last_page_completed + 1 if resume else 1

    records = []
    dropped = 0
    warnings_count = 0
    run_start = time.monotonic()

    with HttpClient() as client:
        try:
            for page_num, page_url, html_text in iterate_listing_pages(
                client, start_page=start_page, max_pages=pages
            ):
                listing_records = parse_listing_page(html_text, page_url)
                logger.info("page_processed page_num=%d cards=%d", page_num, len(listing_records))

                for raw in listing_records:
                    detail_raw = None
                    if with_detail and raw.get("product_url"):
                        try:
                            detail_html = client.get(raw["product_url"]).text
                            detail_raw = parse_detail_page(detail_html, raw["product_url"])
                            checkpoint.visited_detail_urls.append(raw["product_url"])
                        except NonRetryableHTTPError as exc:
                            logger.error("detail_fetch_failed url=%s error=%s", raw["product_url"], exc)
                            warnings_count += 1

                    try:
                        record = build_record(raw, detail_raw)
                        records.append(record)
                    except RequiredFieldMissingError as exc:
                        logger.warning("record_dropped reason=%s", exc)
                        dropped += 1

                checkpoint.last_page_completed = page_num
                checkpoint.total_records_so_far = len(records)
                checkpoint.save(checkpoint_path)

        except CircuitBreakerOpenError as exc:
            logger.error("run_aborted_circuit_breaker %s", exc)

    duration_s = round(time.monotonic() - run_start, 1)

    export_json(records, f"{output_prefix}.json")
    export_csv(records, f"{output_prefix}.csv")

    expected = None if with_detail and pages < config.TOTAL_PAGES_EXPECTED else None
    qa_report = run_qa(records, expected_total=expected)
    with open(f"{output_prefix}_qa_report.json", "w", encoding="utf-8") as f:
        json.dump(qa_report, f, ensure_ascii=False, indent=2)

    summary = {
        "pages_requested": pages,
        "records_extracted": len(records),
        "records_dropped": dropped,
        "warnings": warnings_count,
        "duration_seconds": duration_s,
        "with_detail": with_detail,
        "qa_passed": qa_report["passed"],
    }
    logger.info("run_summary %s", json.dumps(summary))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Scraper de books.toscrape.com (P1)")
    parser.add_argument("--pages", type=int, default=config.TOTAL_PAGES_EXPECTED, help="Número de páginas de listado a recorrer")
    parser.add_argument("--with-detail", action="store_true", help="Enriquecer cada registro con la ficha de detalle")
    parser.add_argument("--output", default=f"{config.DEFAULT_OUTPUT_DIR}/books", help="Prefijo de ruta de salida (sin extensión)")
    parser.add_argument("--checkpoint", default=config.DEFAULT_CHECKPOINT_FILE, help="Ruta del archivo de checkpoint")
    parser.add_argument("--resume", action="store_true", help="Reanudar desde el último checkpoint guardado")
    parser.add_argument("--log-file", default=None, help="Ruta opcional de archivo de log")
    args = parser.parse_args()

    setup_logging(log_file=args.log_file)
    logger.info(
        "run_start pages=%d with_detail=%s output=%s resume=%s",
        args.pages, args.with_detail, args.output, args.resume,
    )

    try:
        run(args.pages, args.with_detail, args.output, args.checkpoint, args.resume)
    except ScraperError as exc:
        logger.error("run_failed error=%s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
