# Contrato de Datos — Dataset de Libros (books.toscrape.com)

## 1. Campos — requeridos

| Campo | Tipo | Descripción | Normalización |
|---|---|---|---|
| `title` | `string` | Título completo del libro | Trim, unescape de entidades HTML, colapsar espacios múltiples |
| `product_url` | `string (URL absoluta)` | URL canónica de la ficha de detalle | `urljoin` con la base de la página de origen |
| `price` | `float` | Precio en GBP | Quitar símbolo `£`, castear a `float`, redondear a 2 decimales |
| `currency` | `string` | Siempre `"GBP"` en este sitio | Constante fija |
| `availability` | `bool` | `true` si "In stock", `false` en otro caso | Mapeo de texto → booleano |
| `rating` | `int` (1–5) o `null` | Estrellas | Mapeo `One→1 … Five→5`; si no mapea, `null` |
| `category` | `string` | Categoría (3er nivel del breadcrumb) | Trim, Title Case |
| `scraped_at` | `string (ISO 8601 UTC)` | Timestamp de extracción | Generado por el pipeline, no por el sitio |

## 2. Campos — opcionales

| Campo | Tipo | Default si falta | Notas |
|---|---|---|---|
| `upc` | `string` | `null` | Solo disponible en página de detalle |
| `image_url` | `string (URL absoluta)` | `null` | `urljoin` con base |
| `price_excl_tax` | `float` | `null` | Solo detalle |
| `price_incl_tax` | `float` | `null` | Solo detalle |
| `tax` | `float` | `0.0` | Solo detalle |
| `stock_count` | `int` | `null` | Extraído por regex de `availability_detail` |
| `reviews_count` | `int` | `0` | Solo detalle |
| `description` | `string` | `null` | Puede no existir en el DOM; ausencia ≠ error |

## 3. Casos límite

| # | Caso | Respuesta esperada |
|---|---|---|
| 1 | Título con comillas, apóstrofes o acentos (ej. *"Sharp Objects"*, *Élite*) | Se conserva tal cual en UTF-8; no se debe producir mojibake (`Ã©` en vez de `é`) al exportar |
| 2 | Precio `£0.00` o ausente | Si el nodo no existe → registro se descarta (campo requerido); si es `0.00`, se acepta pero se marca `warning` en el log de QA |
| 3 | Clase de rating no reconocida (ej. sitio cambia a `"star-rating Zero"` o clase ausente) | `rating = null` + warning en log; el registro **no** se descarta (rating no es crítico para el negocio) |
| 4 | Producto sin bloque `#product_description` | `description = null`, sin error ni warning (es un caso normal documentado) |
| 5 | Disponibilidad con texto atípico (`"Out of stock"`, o `"In stock (0 available)"`) | `availability = false` si "Out of stock"; si "In stock (0 available)" → `availability = true`, `stock_count = 0` (edge case: en stock pero sin unidades, se reporta tal cual) |

## 4. Validaciones

- `title`, `product_url`, `price`, `availability`, `category`, `scraped_at` → **requeridos**, su
  ausencia descarta el registro.
- `price >= 0` (rechazar negativos como error de parseo).
- `rating` ∈ `{1,2,3,4,5, null}` — cualquier otro valor es un bug de mapeo, no un dato válido.
- `product_url` debe ser una URL absoluta válida (esquema + host).
- `currency` siempre `"GBP"` — cualquier otro valor indica un error de extracción.

## 5. Ejemplo — JSON

```json
{
  "title": "A Light in the Attic",
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "price": 51.77,
  "currency": "GBP",
  "availability": true,
  "rating": 3,
  "category": "Poetry",
  "scraped_at": "2026-08-14T10:32:05Z",
  "upc": "a897fe39b1053632",
  "image_url": "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
  "price_excl_tax": 51.77,
  "price_incl_tax": 51.77,
  "tax": 0.0,
  "stock_count": 22,
  "reviews_count": 0,
  "description": "It's hard to imagine a world without A Light in the Attic..."
}
```

## 6. Ejemplo — CSV

- **Encoding:** UTF-8 (sin BOM)
- **Delimitador:** coma (`,`)
- **Quoting:** `QUOTE_MINIMAL`, con comillas dobles envolviendo campos que contengan comas, saltos
  de línea o comillas (típicamente `description`)
- **Encabezado:** obligatorio, nombres de columna = nombres de campo del contrato

```csv
title,product_url,price,currency,availability,rating,category,scraped_at,upc,image_url,price_excl_tax,price_incl_tax,tax,stock_count,reviews_count,description
"A Light in the Attic",https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html,51.77,GBP,true,3,Poetry,2026-08-14T10:32:05Z,a897fe39b1053632,https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg,51.77,51.77,0.0,22,0,"It's hard to imagine a world without A Light in the Attic..."
```
