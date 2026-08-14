# Onboarding del Scraper — P1

**Proyecto:** founders25-scraper
**Sitio objetivo:** `books.toscrape.com`
**Fecha de verificación:** 2026-08-14

## 1. Naturaleza del sitio

`books.toscrape.com` es un sandbox público mantenido por el equipo de Zyte/Scrapinghub, creado
explícitamente para practicar web scraping. El propio sitio lo declara en su aviso de pie de página:

> "This is a demo website for web scraping purposes. Prices and ratings here were randomly
> assigned and have no real meaning."

Esto es relevante para el análisis ético: los datos no representan un catálogo comercial real,
y el sitio autoriza implícita y explícitamente su uso para scraping.

## 2. robots.txt — verificado en vivo

| Verificación | Resultado |
|---|---|
| `http://books.toscrape.com/robots.txt` | **404 Not Found** |
| `https://books.toscrape.com/robots.txt` | **404 Not Found** |
| Fecha de chequeo | 2026-08-14 |

**No existe archivo `robots.txt`.** No hay reglas de exclusión explícitas (`Disallow`), ni
`Crawl-delay`, ni sitemap declarado.

> ⚠️ Nota de buena práctica (aplicable a cualquier sitio, no solo este): la **ausencia** de
> `robots.txt` no debe interpretarse por defecto como "todo permitido" en un sitio de producción
> real. Aquí sí es razonable tratarlo como scraping permitido porque el propio sitio declara ese
> propósito en su contenido visible. En un proyecto contra un sitio real, la ausencia de
> `robots.txt` debe ir acompañada de una revisión manual de Términos de Servicio antes de asumir
> permiso.

## 3. Términos de uso

No se detectan Términos y Condiciones formales ni licencia de datos publicada. El aviso del
footer citado arriba funciona como autorización de uso para fines de práctica/aprendizaje.

## 4. Alcance ético propuesto

- **Incluido:** páginas de catálogo (`/index.html`, `/catalogue/page-N.html`) y páginas de
  detalle de producto (`/catalogue/<slug>_<id>/index.html`). Todo es contenido público, sin
  autenticación.
- **Excluido:** no aplica (no hay login, carritos ni datos de usuario en este sitio).
- **Sin PII:** el dataset no contiene datos personales de terceros.
- **Sin sobrecarga:** aunque es un sandbox sin límites impuestos, se aplican las mismas
  políticas de cortesía que se usarían contra un sitio real (ver abajo), como ejercicio
  formativo para el resto de proyectos del curso.

## 5. Política de User-Agent

```
User-Agent: founders25-scraper/0.1 (+https://github.com/<org>/founders25-scraper; contacto: highhopes1805@gmail.com)
```

- Identifica el proyecto, su repositorio y un contacto — buena práctica estándar para que el
  operador del sitio pueda contactarnos si algo falla.
- No se suplanta el User-Agent de un navegador real.

## 6. Rate limit y backoff

| Parámetro | Valor propuesto | Justificación |
|---|---|---|
| Delay entre requests | 1–2 s (aleatorizado, jitter ±0.3s) | Cortesía estándar aunque el sitio no lo exige |
| Requests concurrentes | 1 (secuencial) | Evita ráfagas; el volumen (≤1050 requests) no requiere paralelismo |
| Timeout por request | 10 s conexión / 15 s lectura | Evita procesos colgados |
| Reintentos | Máx. 5, backoff exponencial (2s, 4s, 8s, 16s, 32s) + jitter | Tolerar fallos transitorios sin martillar el servidor |
| Circuit breaker | Abortar si 10 fallos consecutivos | Señal de bloqueo o caída del sitio |

## 7. Horario de cortesía

No aplica de forma estricta (sandbox sin tráfico real que proteger), pero se documenta como si
aplicara, para que el hábito se traslade a proyectos futuros: evitar lanzar corridas masivas en
horas pico del sitio objetivo cuando el target sea un sitio de producción real.

## ✅ Checklist de onboarding

- [x] robots.txt revisado (no existe — verificado en vivo, dos protocolos)
- [x] Términos/avisos revisados (aviso de sandbox de scraping encontrado)
- [x] Alcance ético definido (solo catálogo público, sin PII)
- [x] User-Agent definido con contacto e identificación del proyecto
- [x] Rate limit, timeouts, reintentos y backoff definidos
- [ ] Repo GitHub `founders25-scraper` creado con carpeta `/scraper` y `/DOCS`
- [ ] Perfil VS Code "Founders-Data" configurado y sincronizado
