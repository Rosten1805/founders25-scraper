"""Logging estructurado para el scraper.

El repositorio de referencia usa `print()` crudo sin persistencia. Aquí se
usa el módulo estándar `logging`, con timestamp ISO 8601, nivel y logger
nombreado por módulo — ver /DOCS/scraping_plan.md §6 (Observabilidad) y
/DOCS/onboarding_scraper.md §6.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path


class _UTCFormatter(logging.Formatter):
    converter = __import__("time").gmtime  # timestamps en UTC, no hora local

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        return (
            f"{ct.tm_year:04d}-{ct.tm_mon:02d}-{ct.tm_mday:02d}T"
            f"{ct.tm_hour:02d}:{ct.tm_min:02d}:{ct.tm_sec:02d}Z"
        )


def setup_logging(log_file: str | None = None, level: int = logging.INFO) -> logging.Logger:
    """Configura el logger raíz del proyecto y devuelve el logger principal.

    Formato: ``<timestamp ISO8601> <LEVEL> <logger_name> <message>``.
    El request_id (cuando aplica) se incluye en el propio mensaje desde
    quien loguea (ver http_client.py), en vez de forzarlo aquí para no
    acoplar el formatter a un solo tipo de evento.
    """
    fmt = "%(asctime)s %(levelname)-8s %(name)s %(message)s"
    formatter = _UTCFormatter(fmt)

    root = logging.getLogger("scraper")
    root.setLevel(level)
    root.handlers.clear()

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    root.propagate = False
    return root
