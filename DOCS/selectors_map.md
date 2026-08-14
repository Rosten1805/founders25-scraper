# Mapa de Selectores CSS — books.toscrape.com

**Estado de verificación:** los selectores marcados ✅ fueron confirmados contra el HTML en vivo
el 2026-08-14; los marcados 🟡 se documentan a partir de la estructura pública y estable de este
sitio (ampliamente usado como sandbox de referencia), pero deben confirmarse manualmente con
DevTools (F12 → Inspeccionar) antes de implementar el extractor, siguiendo la política del curso
de no dar por verificado lo que no se ha inspeccionado.

## 1. Página de listado (`/catalogue/page-{n}.html`)

Contenedor de cada tarjeta: `article.product_pod` ✅

| Campo | Selector primario | Ubicación del dato | Fallback | Riesgo de fragilidad |
|---|---|---|---|---|
| `title` | `h3 > a` | atributo `title` del `<a>` (texto completo) ✅ | texto visible del `<a>` (puede venir truncado con "…") 🟡 | Bajo — atributo `title` es estable en este template |
| `product_url` | `h3 > a` | atributo `href` (relativo) ✅ | — | Requiere `urljoin(base_url, href)`; sin fallback si falta |
| `price` | `p.price_color` 🟡 | texto, formato `£51.77` | — | Medio — si cambia el símbolo de moneda, romperá el parseo numérico |
| `availability` | `p.instock.availability` 🟡 | texto `"In stock"` con espacios/saltos de línea | ausencia del nodo → `false` | Bajo |
| `rating` | `p.star-rating` 🟡 | segunda clase del atributo `class` (`One`/`Two`/`Three`/`Four`/`Five`) | si clase no mapeable → `null` + warning | Medio — depende de mantener el diccionario de mapeo actualizado |
| `image_url` | `div.image_container img` 🟡 | atributo `src` (relativo) | — | Requiere `urljoin`; sin fallback si falta |

## 2. Página de detalle (`/catalogue/<slug>_<id>/index.html`)

| Campo | Selector primario (robusto) | Selector fallback (posicional) | Notas |
|---|---|---|---|
| `upc` | fila de `table.table.table-striped` cuyo `<th>` == "UPC" → `<td>` | `tr:nth-child(1) td` 🟡 | **Preferir siempre el selector por etiqueta `<th>`**, no por posición: si el sitio reordena filas de la tabla, el posicional rompe silenciosamente y el basado en texto no |
| `product_type` | `<th>` == "Product Type" → `<td>` | `tr:nth-child(2) td` 🟡 | ídem |
| `price_excl_tax` | `<th>` == "Price (excl. tax)" → `<td>` | `tr:nth-child(3) td` 🟡 | ídem |
| `price_incl_tax` | `<th>` == "Price (incl. tax)" → `<td>` | `tr:nth-child(4) td` 🟡 | ídem |
| `tax` | `<th>` == "Tax" → `<td>` | `tr:nth-child(5) td` 🟡 | ídem |
| `availability_detail` | `<th>` == "Availability" → `<td>` | `tr:nth-child(6) td` 🟡 | texto tipo `"In stock (22 available)"` — requiere regex `\((\d+) available\)` para extraer `stock_count` |
| `reviews_count` | `<th>` == "Number of reviews" → `<td>` | `tr:nth-child(7) td` 🟡 | castear a `int`, default `0` |
| `category` | `ul.breadcrumb li:nth-child(3) a` 🟡 | texto del breadcrumb, 3er nivel | Bajo — breadcrumb tiene estructura fija: Home / Books / *Categoría* / *Título* |
| `description` | `div#product_description` + siguiente `<p>` hermano 🟡 | ausencia → `description = null` | El nodo `#product_description` puede no existir en algunos productos; no debe tratarse como error |

## 3. Paginación (referencia cruzada)

Ver detalle completo en [pagination_strategy.md](pagination_strategy.md). Selector clave:
`li.next > a` ✅ (confirmado en vivo — apunta a `catalogue/page-2.html` desde la portada).

## 4. Pruebas manuales recomendadas (antes de implementar)

1. Abrir `books.toscrape.com` en el navegador → DevTools (F12) → pestaña Elements.
2. Usar el inspector de selección (icono de flecha) sobre una tarjeta de producto → confirmar
   clase `product_pod` y estructura interna.
3. En la consola, ejecutar `document.querySelectorAll('article.product_pod').length` → debe
   devolver `20` en cualquier página de listado excepto la última (puede ser menor).
4. Abrir un producto de detalle → confirmar en consola:
   `document.querySelector('table.table-striped').rows.length` → debe devolver `7`.
5. Repetir el paso 3 en `catalogue/page-50.html` → confirmar ausencia de `li.next`.

## 5. Riesgos generales de cambio de DOM

- Si el sitio migra de plantilla (poco probable en un sandbox estable, pero posible), todos los
  selectores basados en clase (`price_color`, `star-rating`, `instock`) son los más frágiles.
- Mitigación: centralizar los selectores en un único módulo de configuración (no hardcodeados
  dispersos en el código) para que un cambio de DOM requiera editar un solo archivo.
- Cualquier cambio de selector debe registrarse en [changelog.md](changelog.md) bajo `Changed`.
