# Estrategia de Paginación — books.toscrape.com

## 1. Tipo de paginación

Paginación por **URL numérica secuencial** (no scroll infinito, no cursor/token):

```
https://books.toscrape.com/catalogue/page-1.html
https://books.toscrape.com/catalogue/page-2.html
...
https://books.toscrape.com/catalogue/page-50.html
```

La portada (`/index.html`) equivale al contenido de `page-1.html`.

## 2. Señales de fin de paginación

Confirmado en vivo (2026-08-14):

- **Señal primaria:** ausencia del nodo `li.next > a` en la página actual. La página 50 no
  contiene este enlace.
- **Señal secundaria (cruce de validación):** el indicador textual `"Page {n} of 50"` visible en
  el listado. Si `n == 50`, se espera que no exista `li.next` — si ambas señales no coinciden,
  se registra una advertencia (posible cambio de estructura del sitio).
- **No usar** el status HTTP como señal de fin: pedir `page-51.html` devuelve `404`, pero
  depender de eso como mecanismo normal de corte es una mala práctica (genera una request
  fallida innecesaria y confunde las métricas de error reales).

## 3. Checkpoint y reanudación

- Al procesar cada página de listado exitosamente, persistir `last_page_completed = n` en un
  archivo de estado (`.checkpoint.json`) junto con `timestamp` y `total_records_so_far`.
- Si el proceso se interrumpe (error no recuperable, corte manual), la siguiente ejecución lee
  el checkpoint y reanuda desde `last_page_completed + 1`, evitando reprocesar páginas ya
  extraídas.
- El checkpoint de la fase de detalle es independiente: se guarda la lista de `product_url` ya
  visitadas (o su hash) para no repetir requests de detalle si se reanuda a mitad del scraping.

## 4. Timeouts y politeness

| Parámetro | Valor |
|---|---|
| Timeout conexión | 10 s |
| Timeout lectura | 15 s |
| Delay entre requests de listado | 1–2 s con jitter |
| Delay entre requests de detalle | 1–2 s con jitter |
| Reintentos por página | hasta 5, backoff exponencial (ver [onboarding_scraper.md](onboarding_scraper.md)) |

## 5. Conteo esperado de registros

Confirmado en vivo:

- **Total de productos:** 1000
- **Productos por página de listado:** 20
- **Páginas de listado:** 50 (`1000 / 20`)
- **Páginas de detalle (si se scrapea ficha completa):** hasta 1000, una por producto

## 6. Estimación de tiempo

| Alcance | Nº de requests | Tiempo estimado (a 1.5 s/req promedio) |
|---|---|---|
| Solo listado (título, precio, disponibilidad, rating, imagen) | 50 | ~75 s (~1.3 min) |
| Listado + detalle completo (UPC, impuestos, stock, reviews, descripción) | ~1050 | ~26 min |

**Recomendación para el MVP del P1:** empezar por *solo listado* (rápido, cubre el contrato
mínimo) y añadir el enriquecimiento con detalle como iteración siguiente (tag `v0.2.0`, ver
[changelog.md](changelog.md)).

## 7. Riesgos de paginación

- Si el sitio cambia el tamaño de página (de 20 a otro número), el conteo esperado de páginas
  cambia — el checkpoint debe recalcularse en base a la señal de fin (`li.next`), nunca hardcodear
  `range(1, 51)` como única fuente de verdad.
- Recomendación: usar `range(1, 51)` solo como límite de seguridad (evitar loop infinito), pero
  cortar siempre por la señal real de fin de paginación.
