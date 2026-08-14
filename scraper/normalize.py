"""Normalización según /DOCS/data_contract.md.

Cada función maneja explícitamente los 5 casos límite documentados en el
contrato (precio ausente/cero, rating no mapeable, descripción ausente,
disponibilidad con texto atípico, título con caracteres especiales) en
lugar de dejar que una excepción genérica tumbe todo el registro.
"""

from __future__ import annotations

import html
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from scraper import config
from scraper.exceptions import RequiredFieldMissingError

logger = logging.getLogger("scraper.normalize")

_STOCK_COUNT_RE = re.compile(r"\((\d+)\s+available\)")
_PRICE_RE = re.compile(r"[\d.]+")


@dataclass
class BookRecord:
    """Registro normalizado — refleja 1:1 /DOCS/data_contract.md."""

    title: str
    product_url: str
    price: float
    currency: str
    availability: bool
    rating: int | None
    category: str
    scraped_at: str
    upc: str | None = None
    image_url: str | None = None
    price_excl_tax: float | None = None
    price_incl_tax: float | None = None
    tax: float | None = 0.0
    stock_count: int | None = None
    reviews_count: int = 0
    description: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_text(raw: str | None) -> str | None:
    if raw is None:
        return None
    # Caso límite #1: títulos con comillas/acentos -> unescape de entidades
    # HTML + colapsar espacios, preservando UTF-8 (nada de recodificar).
    text = html.unescape(raw)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def normalize_price(raw: str | None) -> float | None:
    """'£51.77' -> 51.77. Caso límite #2: ausente o '£0.00'."""
    if raw is None:
        return None
    match = _PRICE_RE.search(raw.replace(",", ""))  # tolera separador de miles
    if not match:
        logger.warning("price_parse_failed raw=%r", raw)
        return None
    value = round(float(match.group()), 2)
    if value == 0:
        logger.warning("price_is_zero raw=%r", raw)
    return value


def normalize_availability(raw: str | None) -> bool:
    """Caso límite #5: texto atípico ('Out of stock', 'In stock (0 available)')."""
    if raw is None:
        return False
    return "in stock" in raw.strip().lower()


def parse_stock_count(raw: str | None) -> int | None:
    if raw is None:
        return None
    match = _STOCK_COUNT_RE.search(raw)
    return int(match.group(1)) if match else None


def map_rating(rating_class: str | None) -> int | None:
    """Caso límite #3: clase de rating no reconocida -> None + warning, sin descartar."""
    if rating_class is None:
        return None
    value = config.RATING_WORD_TO_INT.get(rating_class)
    if value is None:
        logger.warning("rating_class_unmapped class=%r", rating_class)
    return value


def build_record(listing_raw: dict, detail_raw: dict | None = None) -> BookRecord:
    """Combina datos crudos de listado (+ detalle opcional) en un BookRecord válido.

    Lanza RequiredFieldMissingError si algún campo requerido del contrato
    (/DOCS/data_contract.md §1) no puede completarse — el llamador decide
    si descarta el registro y sigue, o aborta la corrida.
    """
    title = normalize_text(listing_raw.get("title"))
    if not title:
        raise RequiredFieldMissingError("title", listing_raw.get("product_url", "unknown"))

    product_url = listing_raw.get("product_url")
    if not product_url:
        raise RequiredFieldMissingError("product_url", title)

    price = normalize_price(listing_raw.get("price_raw"))
    if price is None:
        raise RequiredFieldMissingError("price", product_url)

    availability = normalize_availability(listing_raw.get("availability_raw"))
    rating = map_rating(listing_raw.get("rating_raw"))

    detail_raw = detail_raw or {}
    category = normalize_text(detail_raw.get("category")) or "Unknown"
    if "category" not in detail_raw:
        # Sin fase de detalle no hay breadcrumb; se documenta el alcance
        # reducido en vez de fallar (ver /DOCS/pagination_strategy.md §6, MVP).
        logger.debug("category_unavailable_without_detail_phase product_url=%s", product_url)

    record = BookRecord(
        title=title,
        product_url=product_url,
        price=price,
        currency="GBP",
        availability=availability,
        rating=rating,
        category=category,
        scraped_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        upc=detail_raw.get("upc"),
        image_url=listing_raw.get("image_url"),
        price_excl_tax=normalize_price(detail_raw.get("price_excl_tax_raw")),
        price_incl_tax=normalize_price(detail_raw.get("price_incl_tax_raw")),
        tax=normalize_price(detail_raw.get("tax_raw")) or 0.0,
        stock_count=parse_stock_count(detail_raw.get("availability_detail_raw")),
        reviews_count=int(detail_raw.get("reviews_count_raw") or 0),
        description=normalize_text(detail_raw.get("description")),  # caso límite #4: puede ser None
    )
    return record
