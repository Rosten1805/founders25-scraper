"""Configuración centralizada del scraper.

Todos los valores aquí están respaldados por un artefacto en /DOCS — no hay
"números mágicos" sueltos en el resto del código. Si el sitio cambia de
estructura, este es el único archivo que debería tocarse (ver
/DOCS/selectors_map.md, sección "Riesgos generales de cambio de DOM").
"""

from __future__ import annotations

# --- Sitio objetivo (ver /DOCS/onboarding_scraper.md) ---------------------
BASE_URL = "https://books.toscrape.com/"
CATALOGUE_PAGE_URL_TMPL = BASE_URL + "catalogue/page-{n}.html"
TOTAL_PAGES_EXPECTED = 50  # confirmado en vivo 2026-08-14, ver pagination_strategy.md
RECORDS_EXPECTED = 1000

# Parser de BeautifulSoup. "lxml" es más rápido pero requiere compilar una
# extensión C; en Python 3.14 sobre Windows sin Visual Studio Build Tools no
# hay wheel precompilado disponible aún. "html.parser" es stdlib puro, sin
# dependencias nativas — decisión de portabilidad (ver /DOCS/dependencias.md).
HTML_PARSER = "html.parser"

# --- Identificación / cortesía (ver /DOCS/onboarding_scraper.md §5-6) -----
USER_AGENT = (
    "founders25-scraper/0.2 "
    "(+https://github.com/<org>/founders25-scraper; contacto: highhopes1805@gmail.com)"
)
CONNECT_TIMEOUT = 10  # segundos
READ_TIMEOUT = 15  # segundos
REQUEST_TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)

DELAY_MIN = 1.0  # segundos, cortesía entre requests
DELAY_MAX = 2.0
JITTER = 0.3

MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 2  # 2, 4, 8, 16, 32
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
CIRCUIT_BREAKER_MAX_CONSECUTIVE_FAILURES = 10

# --- Selectores CSS (ver /DOCS/selectors_map.md) ---------------------------
# Página de listado
SEL_PRODUCT_CARD = "article.product_pod"
SEL_TITLE_LINK = "h3 a"
SEL_PRICE = "p.price_color"
SEL_AVAILABILITY = "p.instock.availability"
SEL_RATING = "p.star-rating"
SEL_IMAGE = "div.image_container img"
SEL_NEXT_PAGE = "li.next > a"
SEL_PAGE_INDICATOR = "li.current"  # texto tipo "Page 1 of 50"

# Página de detalle
SEL_DETAIL_TABLE = "table.table.table-striped"
SEL_BREADCRUMB_ITEMS = "ul.breadcrumb li"
DESCRIPTION_ANCHOR_ID = "product_description"

# Mapeo de clases de rating -> entero (ver /DOCS/data_contract.md)
RATING_WORD_TO_INT = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

# Campos requeridos del contrato (ver /DOCS/data_contract.md §1)
REQUIRED_FIELDS = (
    "title",
    "product_url",
    "price",
    "currency",
    "availability",
    "category",
    "scraped_at",
)

# --- Salidas -----------------------------------------------------------
DEFAULT_OUTPUT_DIR = "data"
DEFAULT_CHECKPOINT_FILE = "data/.checkpoint.json"
