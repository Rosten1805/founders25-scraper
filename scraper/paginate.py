"""Recorrido de las páginas de listado con detección de fin y checkpoint.

Ver /DOCS/pagination_strategy.md. La señal real de fin es la ausencia de
`li.next`; el rango `1..max_pages` es solo un límite de seguridad para
evitar un loop infinito si el sitio cambiara de comportamiento — nunca la
única fuente de verdad (§7 del doc).
"""

from __future__ import annotations

import logging
from typing import Iterator

from scraper import config
from scraper.extract_listing import has_next_page, read_page_indicator
from scraper.http_client import HttpClient

logger = logging.getLogger("scraper.paginate")


def iterate_listing_pages(
    client: HttpClient,
    start_page: int = 1,
    max_pages: int = config.TOTAL_PAGES_EXPECTED,
) -> Iterator[tuple[int, str, str]]:
    """Genera tuplas (page_num, page_url, html) hasta que no haya más páginas.

    `max_pages` es un límite de seguridad, no la condición de corte real.
    """
    page_num = start_page
    while page_num <= max_pages:
        page_url = config.CATALOGUE_PAGE_URL_TMPL.format(n=page_num)
        response = client.get(page_url)
        html_text = response.text

        yield page_num, page_url, html_text

        indicator = read_page_indicator(html_text)
        next_exists = has_next_page(html_text)

        if indicator and f"of {max_pages}" not in indicator and page_num == 1:
            logger.warning(
                "page_indicator_mismatch expected_total=%d indicator=%r",
                max_pages, indicator,
            )

        if not next_exists:
            logger.info(
                "pagination_end_detected last_page=%d indicator=%r", page_num, indicator
            )
            break

        page_num += 1
