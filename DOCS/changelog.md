# Changelog — founders25-scraper (P1)

Formato basado en [Keep a Changelog](https://keepachangelog.com/) y versionado
[SemVer](https://semver.org/): `MAJOR.MINOR.PATCH`.

- **MAJOR**: cambio incompatible en el contrato de datos (ej. se elimina o renombra un campo
  requerido).
- **MINOR**: nueva funcionalidad compatible hacia atrás (ej. nuevos campos opcionales, nueva
  fuente de datos).
- **PATCH**: correcciones sin cambiar el contrato (ej. fix de un selector, ajuste de rate limit).

Categorías por release: `Added`, `Changed`, `Fixed`, `Deprecated`, `Removed`, `Security`.

## [Unreleased]

### Added
- Artefactos iniciales de `/DOCS`: onboarding, plan de scraping, mapa de selectores, estrategia
  de paginación, contrato de datos, QA checklist, dependencias, PR template, changelog.
- Implementación completa de `scraper/` (http_client con retries/backoff/circuit breaker,
  extractores de listado y detalle, normalizador, paginación con checkpoint, export CSV/JSON,
  QA automatizado, pipeline CLI) y suite de tests `pytest` con fixtures HTML reales.

### Changed
- Selectores de `selectors_map.md` confirmados 1:1 contra HTML real descargado el 2026-08-14
  (antes marcados 🟡 "a confirmar"; ahora ✅ verificados por los tests de `tests/test_extract.py`).
- Export de datos: se usa `csv`/`json` de la librería estándar en vez de `pandas` — ver
  [dependencias.md](dependencias.md).

### Fixed
- **Encoding (UTF-8) en `http_client.py`:** `books.toscrape.com` declara `charset=UTF-8` en un
  `<meta>` HTML, no en la cabecera HTTP `Content-Type`. `requests` solo detecta encoding desde la
  cabecera HTTP y, sin ella, cae a ISO-8859-1 por defecto (RFC 2616), corrompiendo cualquier
  caracter no-ASCII (`£`, comillas tipográficas, espacios de no separación) al leer
  `response.text` — se manifestó como `Â£0.00` en vez de `£0.00` y texto corrupto en
  `description` durante la primera corrida real contra el sitio (2026-08-14). Fix: forzar
  `response.encoding = "utf-8"` explícitamente en `HttpClient.get()`. Verificado: 0 caracteres
  corruptos tras el fix en `data/books_detail_sample.json`.

## Plan de releases del P1

| Tag | Alcance | Contenido |
|---|---|---|
| `v0.1.0` | Plan | Artefactos de `/DOCS` completos: onboarding, scraping_plan, data_contract (sin código aún) |
| `v0.2.0` | Selectores/paginación | Extractor funcional (listado + detalle), mapa de selectores validado en código, paginación con checkpoint |
| `v0.3.0` | QA/export | Normalizador, export CSV/JSON, QA checklist automatizado, logging de corrida |

## Plan de commits atómicos estimados (10)

| # | Commit (mensaje sugerido) | Artefacto/código afectado |
|---|---|---|
| 1 | `docs: add onboarding_scraper.md with robots.txt and rate-limit policy` | `/DOCS/onboarding_scraper.md` |
| 2 | `docs: add scraping_plan.md with pipeline diagram` | `/DOCS/scraping_plan.md` |
| 3 | `docs: add data_contract.md with JSON/CSV schema` | `/DOCS/data_contract.md` |
| 4 | `docs: add selectors_map.md for listing and detail pages` | `/DOCS/selectors_map.md` |
| 5 | `docs: add pagination_strategy.md with checkpoint plan` | `/DOCS/pagination_strategy.md` |
| 6 | `feat: implement HTTP client with retries and rate limit` | `scraper/http_client.py` |
| 7 | `feat: implement listing extractor with selectors map` | `scraper/extract_listing.py` |
| 8 | `feat: implement detail extractor and normalizer` | `scraper/extract_detail.py`, `scraper/normalize.py` |
| 9 | `feat: implement CSV/JSON export and QA report` | `scraper/export.py`, `scraper/qa.py` |
| 10 | `chore: add requirements.txt, logging config and README run instructions` | `requirements.txt`, `scraper/logging_config.py` |

## Criterios de SemVer para este proyecto

- Cambiar un selector sin afectar el contrato de datos → `PATCH`.
- Agregar un campo opcional nuevo al contrato → `MINOR`.
- Eliminar/renombrar un campo requerido, o cambiar el tipo de un campo existente → `MAJOR`.

## ✅ Checklist de release notes

- [ ] Versión y fecha
- [ ] Resumen de 1-2 frases del alcance del release
- [ ] Lista de artefactos `/DOCS` nuevos o modificados
- [ ] Cambios en el contrato de datos, si los hubo (con nota de compatibilidad)
- [ ] Resultado del QA checklist de la última corrida generada con este release
- [ ] Enlace al PR o PRs incluidos
