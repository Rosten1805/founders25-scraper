# Promptpack — Scraper con IA (books.toscrape.com)

Prompts listos para usar, ya adaptados al sitio y tema de este proyecto. Úsalos en sesiones
posteriores con la IA para generar/revisar los artefactos o, en el prompt 8, para generar el
código Python real.

## 1) Descubrimiento del sitio y robots

**Rol:** Legal & Data Ethics + Crawler Designer

> Analiza el dominio `books.toscrape.com`. Resume `robots.txt` y términos de uso; indica lo
> permitido, límites de rate y páginas sensibles. Propón un alcance ético del scraping y una
> política de User-Agent/Rate Limit/Backoff. Formato: tabla + checklist.

*Ya ejecutado para este proyecto → ver [onboarding_scraper.md](onboarding_scraper.md).*

## 2) Target de datos y contrato

**Rol:** Data Architect

> Define el contrato de datos (JSON y CSV) para el dataset de catálogo de libros de
> `books.toscrape.com`. Especifica campos requeridos/opcionales, tipos, defaults, normalizaciones
> y validaciones. Incluye 5 casos límite y respuestas esperadas.

*Ya ejecutado para este proyecto → ver [data_contract.md](data_contract.md).*

## 3) Mapa de selectores CSS

**Rol:** DOM Analyst

> Sobre `books.toscrape.com/catalogue/page-1.html` y una ficha de detalle de producto, inspecciona
> el DOM y propone un mapa de selectores estable (id/class/paths) para título, precio,
> disponibilidad, rating, imagen, UPC, categoría y descripción. Identifica riesgos de cambios en
> el DOM y alternativas de fallback.

*Ya ejecutado para este proyecto → ver [selectors_map.md](selectors_map.md).*

## 4) Paginación y cobertura

**Rol:** Crawler Planner

> Diseña la estrategia de paginación de `books.toscrape.com` (patrón `catalogue/page-{n}.html`).
> Incluye: detección del fin de páginas, timeouts, politeness, reanudación (checkpoint) y conteo
> esperado de registros.

*Ya ejecutado para este proyecto → ver [pagination_strategy.md](pagination_strategy.md).*

## 5) Errores, retries y logs

**Rol:** Reliability Engineer

> Propón políticas de error handling (timeouts, 4xx/5xx) con retries exponenciales, backoff y
> circuit breaker conceptual para el scraper de `books.toscrape.com`. Define formato de logs
> (nivel, timestamp, request id) y artefactos de observabilidad.

*Base definida en [onboarding_scraper.md](onboarding_scraper.md) §6 y
[scraping_plan.md](scraping_plan.md) §6-7 — usar este prompt para profundizar el diseño del logger
en la próxima sesión.*

## 6) Export a CSV/JSON y QA de datos

**Rol:** Data Steward

> Describe el proceso de exportación a CSV/JSON (encoding, delimitador, encabezados) del dataset
> de libros y un checklist de QA: conteo, duplicados, nulos, tipos, valores fuera de rango.

*Ya ejecutado para este proyecto → ver [data_contract.md](data_contract.md) §6 y
[qa_checklist.md](qa_checklist.md).*

## 7) Plan de commits, tags y release (P1)

**Rol:** Release Manager

> Crea el plan de commits atómicos y puntos de tag para el P1 del scraper de books.toscrape.com.
> Tabla con 10 commits estimados, tags `v0.1.0` (plan), `v0.2.0` (selectores/paginación), `v0.3.0`
> (QA/export). Añade criterios de semver y checklist de release notes.

*Ya ejecutado para este proyecto → ver [changelog.md](changelog.md).*

## 8) Generación de código (próxima sesión)

**Rol:** Pair Programmer IA

> Con los artefactos de `/DOCS` adjuntos (onboarding_scraper.md, scraping_plan.md,
> selectors_map.md, pagination_strategy.md, data_contract.md, qa_checklist.md), genera código
> Python con `requests` + `BeautifulSoup` (parser `lxml`) para scrapear
> `books.toscrape.com/catalogue/page-{n}.html` y sus fichas de detalle, con logging básico según
> la política definida, normalización según el contrato, y export a CSV/JSON. Incluye pruebas
> mínimas (pytest) y docstrings. **No ejecutar ahora** — solo generar el código para revisión.

**Cuándo usarlo:** en la sesión siguiente, una vez validados todos los artefactos de `/DOCS` y
creado el repositorio `founders25-scraper`.
