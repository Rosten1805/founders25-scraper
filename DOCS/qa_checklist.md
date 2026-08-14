# QA Checklist — Dataset de Libros

Ejecutar esta checklist **antes** de considerar un dataset (CSV/JSON) listo para publicar o
consumir en análisis posteriores.

## 1. Conteo

- [ ] Nº total de registros == 1000 (± tolerancia si el sitio cambió desde la última verificación;
      documentar cualquier diferencia).
- [ ] Nº de páginas de listado procesadas == 50 (o coincide con la señal real de fin de
      paginación, ver [pagination_strategy.md](pagination_strategy.md)).
- [ ] Nº de registros descartados por campo requerido faltante — reportado y justificado, no solo
      silenciado.

## 2. Duplicados

- [ ] `product_url` es único en el dataset (clave natural — no debería haber dos filas con la
      misma URL de detalle).
- [ ] `upc` es único cuando no es `null`.
- [ ] Si se detectan duplicados, investigar si es un bug de paginación (misma página procesada
      dos veces) antes de simplemente deduplicar.

## 3. Nulos

| Campo | Umbral aceptable de `null` | Acción si se excede |
|---|---|---|
| `title`, `product_url`, `price`, `availability`, `category` | 0% (son requeridos) | Bloquear publicación del dataset |
| `rating` | hasta 5% | Investigar mapeo de clases CSS |
| `description` | hasta 15% (hay productos sin descripción, es normal) | Solo advertencia |
| `upc`, `image_url`, campos de detalle | 0% si se scrapeó fase de detalle; 100% si el MVP fue solo listado | Documentar el alcance de la corrida |

## 4. Tipos

- [ ] `price`, `price_excl_tax`, `price_incl_tax`, `tax` son `float`, no `string`.
- [ ] `rating`, `stock_count`, `reviews_count` son `int` o `null`, no `float` ni `string`.
- [ ] `availability` es `bool`, no `"true"`/`"false"` como string.
- [ ] `scraped_at` es parseable como fecha ISO 8601.

## 5. Rangos y valores fuera de rango

- [ ] `rating` ∈ `{1,2,3,4,5, null}` — cualquier otro valor es un bug.
- [ ] `price >= 0` para todos los registros.
- [ ] `stock_count >= 0` cuando no es `null`.
- [ ] `currency == "GBP"` en el 100% de los registros.

## 6. Codificación

- [ ] El archivo CSV/JSON abre correctamente en UTF-8 sin caracteres corruptos (mojibake) en
      títulos con tildes, apóstrofes o comillas tipográficas.
- [ ] El CSV no tiene BOM si el consumidor downstream no lo espera (documentar si se necesita).
- [ ] Campos con comas o saltos de línea (`description`) están correctamente escapados con
      comillas dobles.

## 7. Resumen de corrida (a adjuntar junto al dataset)

- [ ] Timestamp de inicio/fin de la corrida.
- [ ] Tasa de error (requests fallidos / requests totales).
- [ ] Lista de warnings agregados (ej. "N registros con rating no mapeable").
- [ ] Versión del scraper / tag de release que generó el dataset (ver [changelog.md](changelog.md)).
