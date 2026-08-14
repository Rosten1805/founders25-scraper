"""Extracción de la página de listado (/catalogue/page-{n}.html).

Devuelve datos crudos (strings tal cual aparecen en el DOM); la limpieza y
el tipado viven en normalize.py — separación deliberada para poder testear
cada capa por separado (ver /DOCS/selectors_map.md §1).
"""

from __future__ import annotations

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper import config

logger = logging.getLogger("scraper.extract_listing")


def parse_listing_page(html: str, page_url: str) -> list[dict]:
    """Extrae los datos crudos de cada tarjeta de producto de una página de listado.

    Un campo faltante en una tarjeta puntual no aborta el parseo de la
    página completa: se registra un warning y el campo queda como ``None``
    (normalize.py decide después si eso descarta el registro).
    """
    soup = BeautifulSoup(html, config.HTML_PARSER)
    cards = soup.select(config.SEL_PRODUCT_CARD)
    records: list[dict] = []

    for card in cards:
        title_link = card.select_one(config.SEL_TITLE_LINK)
        title = title_link.get("title") if title_link else None
        if not title and title_link:
            title = title_link.get_text(strip=True)
        href = title_link.get("href") if title_link else None
        product_url = urljoin(page_url, href) if href else None

        price_node = card.select_one(config.SEL_PRICE)
        price_raw = price_node.get_text(strip=True) if price_node else None

        availability_node = card.select_one(config.SEL_AVAILABILITY)
        availability_raw = availability_node.get_text(strip=True) if availability_node else None

        rating_node = card.select_one(config.SEL_RATING)
        rating_raw = None
        if rating_node:
            classes = rating_node.get("class", [])
            rating_raw = next((c for c in classes if c != "star-rating"), None)

        image_node = card.select_one(config.SEL_IMAGE)
        image_src = image_node.get("src") if image_node else None
        image_url = urljoin(page_url, image_src) if image_src else None

        if not title or not product_url:
            logger.warning(
                "listing_card_missing_required_field page_url=%s title=%s product_url=%s",
                page_url, bool(title), bool(product_url),
            )

        records.append(
            {
                "title": title,
                "product_url": product_url,
                "price_raw": price_raw,
                "availability_raw": availability_raw,
                "rating_raw": rating_raw,
                "image_url": image_url,
            }
        )

    if not cards:
        logger.warning("listing_page_no_product_cards page_url=%s", page_url)

    return records


def has_next_page(html: str) -> bool:
    """True si existe el enlace 'next' — señal primaria de fin de paginación."""
    soup = BeautifulSoup(html, config.HTML_PARSER)
    return soup.select_one(config.SEL_NEXT_PAGE) is not None


def read_page_indicator(html: str) -> str | None:
    """Devuelve el texto tipo 'Page 1 of 50' — señal secundaria de cruce."""
    soup = BeautifulSoup(html, config.HTML_PARSER)
    node = soup.select_one(config.SEL_PAGE_INDICATOR)
    return node.get_text(strip=True) if node else None
