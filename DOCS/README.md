# /DOCS — P1 Scraper (books.toscrape.com)

Artefactos de diseño del scraper, producidos sin escribir código, siguiendo la sesión
"Prompting efectivo aplicado a scraping". Sitio objetivo: **books.toscrape.com** (sandbox público
de práctica de scraping, verificado el 2026-08-14 — sin `robots.txt`, con aviso explícito de uso
autorizado para scraping).

## Artefactos

| # | Archivo | Contenido |
|---|---|---|
| 1 | [onboarding_scraper.md](onboarding_scraper.md) | Alcance ético, robots.txt/términos, User-Agent, rate limit, backoff |
| 2 | [scraping_plan.md](scraping_plan.md) | Objetivo, fuentes, pipeline (Mermaid), responsabilidades, observabilidad |
| 3 | [selectors_map.md](selectors_map.md) | Selectores CSS por campo (listado y detalle), fallbacks, riesgos |
| 4 | [pagination_strategy.md](pagination_strategy.md) | Tipo de paginación, señales de fin, checkpoint, estimaciones |
| 5 | [data_contract.md](data_contract.md) | Campos requeridos/opcionales, tipos, defaults, 5 casos límite, ejemplos JSON/CSV |
| 6 | [qa_checklist.md](qa_checklist.md) | Duplicados, nulos, rangos, conteos, codificación |
| 7 | [dependencias.md](dependencias.md) | requests/bs4/lxml/pandas/dotenv (conceptual), riesgos, política de actualización |
| 8 | [pr_template.md](pr_template.md) | Plantilla de Pull Request |
| 9 | [changelog.md](changelog.md) | Formato de changelog + plan de tags/releases + 10 commits estimados |
| — | [promptpack.md](promptpack.md) | 8 prompts profesionales listos para usar en próximas sesiones |

## ✅ Checklist rápido

- [x] `/DOCS/onboarding_scraper.md`
- [x] `/DOCS/scraping_plan.md`
- [x] `/DOCS/selectors_map.md`
- [x] `/DOCS/pagination_strategy.md`
- [x] `/DOCS/data_contract.md`
- [x] `/DOCS/qa_checklist.md`
- [x] `/DOCS/dependencias.md`
- [x] `/DOCS/pr_template.md`
- [x] `/DOCS/changelog.md`

## Próximos pasos (fuera de esta sesión)

1. Crear repositorio `founders25-scraper` (o monorepo con carpeta `/scraper`) en GitHub.
2. Configurar Projects (Kanban) y milestones del P1; activar protección de `main` y mover
   [pr_template.md](pr_template.md) a `.github/pull_request_template.md`.
3. Configurar perfil de VS Code "Founders-Data" (extensiones: GitHub Copilot, GitHub Pull
   Requests & Issues, GitLens, Python, Pylance, Markdown All in One, REST Client/Thunder Client).
4. Abrir issues a partir de la tabla de commits de [changelog.md](changelog.md).
5. Usar el prompt 8 de [promptpack.md](promptpack.md) para generar el código Python del scraper.

## Notas de verificación

Antes de escribir estos artefactos se comprobó en vivo (2026-08-14):

- `http://books.toscrape.com/robots.txt` → **404** (no existe)
- `https://books.toscrape.com/robots.txt` → **404** (no existe)
- Estructura confirmada: `article.product_pod`, `li.next` → `catalogue/page-2.html`, indicador
  "Page 1 of 50", 1000 resultados totales (20 por página → 50 páginas)
- Aviso del sitio: *"This is a demo website for web scraping purposes. Prices and ratings here
  were randomly assigned and have no real meaning."*

Los selectores marcados 🟡 en [selectors_map.md](selectors_map.md) están documentados a partir de
la estructura pública y conocida de este sitio de referencia, pero **deben confirmarse
manualmente con DevTools** antes de implementar el extractor — ninguna herramienta automática de
esta sesión pudo leer el HTML crudo directamente.
