"""Extracción de la página de detalle de producto.

Mejora deliberada sobre un parseo posicional (`tr:nth-child(n)`): la tabla
se lee construyendo un diccionario {texto del <th>: texto del <td>}, así que
si el sitio reordena filas el parseo no se rompe — ver
/DOCS/selectors_map.md §2 ("preferir siempre el selector por etiqueta").
"""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup

from scraper import config

logger = logging.getLogger("scraper.extract_detail")

_TABLE_KEYS = (
    "UPC",
    "Product Type",
    "Price (excl. tax)",
    "Price (incl. tax)",
    "Tax",
    "Availability",
    "Number of reviews",
)


def parse_detail_page(html: str, url: str) -> dict:
    """Extrae los datos crudos de la ficha de detalle de un producto."""
    soup = BeautifulSoup(html, config.HTML_PARSER)

    table_data: dict[str, str | None] = {}
    table = soup.select_one(config.SEL_DETAIL_TABLE)
    if table:
        for row in table.find_all("tr"):
            th, td = row.find("th"), row.find("td")
            if th and td:
                table_data[th.get_text(strip=True)] = td.get_text(strip=True)
    else:
        logger.warning("detail_table_not_found url=%s", url)

    missing_keys = [k for k in _TABLE_KEYS if k not in table_data]
    if missing_keys:
        logger.warning("detail_table_missing_keys url=%s missing=%s", url, missing_keys)

    breadcrumb_items = soup.select(config.SEL_BREADCRUMB_ITEMS)
    category = None
    if len(breadcrumb_items) >= 3:
        category = breadcrumb_items[2].get_text(strip=True)
    else:
        logger.warning("detail_breadcrumb_unexpected_length url=%s len=%d", url, len(breadcrumb_items))

    description = None
    desc_anchor = soup.find(id=config.DESCRIPTION_ANCHOR_ID)
    if desc_anchor:
        desc_p = desc_anchor.find_next_sibling("p")
        description = desc_p.get_text(strip=True) if desc_p else None
    # Ausencia de descripción es un caso normal documentado (ver
    # /DOCS/data_contract.md, caso límite #4) — no se loguea como warning.

    return {
        "upc": table_data.get("UPC"),
        "product_type": table_data.get("Product Type"),
        "price_excl_tax_raw": table_data.get("Price (excl. tax)"),
        "price_incl_tax_raw": table_data.get("Price (incl. tax)"),
        "tax_raw": table_data.get("Tax"),
        "availability_detail_raw": table_data.get("Availability"),
        "reviews_count_raw": table_data.get("Number of reviews"),
        "category": category,
        "description": description,
    }
