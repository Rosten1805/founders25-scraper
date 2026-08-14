# Dependencias (conceptual) — P1

> Documentación únicamente. **No se instala nada en esta sesión** — es material de referencia
> para la sesión de generación de código.

## 1. Dependencias propuestas

| Paquete | Versión sugerida (rango) | Rol en el pipeline |
|---|---|---|
| `requests` | `>=2.31,<3.0` | Cliente HTTP: descarga de páginas de listado y detalle |
| `beautifulsoup4` | `>=4.12,<5.0` | Parseo del DOM y aplicación del mapa de selectores |
| `pytest` | `>=8.0,<9.0` | Tests unitarios de normalización y extracción |

> **Decisiones de implementación (v0.2.0):**
> - `pandas` y `python-dotenv`, previstos originalmente, no se incorporaron. El export a
>   CSV/JSON usa los módulos estándar `csv`/`json` — cubren el contrato de datos
>   ([data_contract.md](data_contract.md) §5-6) sin añadir una dependencia pesada solo para
>   escribir un archivo tabular, y evitan ambigüedad de tipos por inferencia automática de
>   pandas. `python-dotenv` no fue necesario porque la configuración (`scraper/config.py`) no
>   requiere secretos ni variables de entorno en este proyecto.
> - `lxml`, también previsto originalmente como parser backend de BeautifulSoup, tampoco se
>   incorporó: en Python 3.14 sobre Windows sin Visual Studio Build Tools no hay wheel
>   precompilado disponible y falla al compilar desde código fuente. Se usa `html.parser` de la
>   librería estándar (`scraper/config.py: HTML_PARSER`) — más lento en datasets muy grandes,
>   pero sin dependencias nativas y suficiente para el volumen de este proyecto (~1000 registros).
>
> Ver [changelog.md](changelog.md) `[Unreleased]`.

## 2. Riesgos

### CVEs / seguridad
- `requests` y su dependencia transitiva `urllib3` han tenido CVEs históricos relacionados con
  manejo de redirecciones y proxies — revisar el advisory de GitHub del proyecto antes de fijar
  versión exacta en `requirements.txt`.
- `lxml` depende de `libxml2`/`libxslt` a nivel de sistema — revisar CVEs de esas librerías C si
  se despliega en un entorno con superficie de ataque relevante (no crítico para uso local de
  scraping educativo).

### Compatibilidad
- `lxml` requiere wheels precompilados por versión de Python/SO; verificar compatibilidad con la
  versión de Python del entorno antes de fijar la versión.
- `pandas 2.x` cambió el backend de tipos (`pyarrow` opcional) — si se usa export CSV simple, no
  hay impacto; si se planea análisis posterior, considerar fijar el backend explícitamente.

### Licencias
- `requests` (Apache 2.0), `beautifulsoup4` (MIT), `lxml` (BSD), `pandas` (BSD-3), `python-dotenv`
  (BSD-3) — todas permisivas, compatibles con uso comercial y sin obligación de copyleft.

## 3. Política de actualización

- Revisión mensual de versiones y advisories (o vía Dependabot/GitHub Security Alerts una vez
  creado el repo).
- Fijar rangos compatibles (`>=x,<y`) en `requirements.txt`, no versiones exactas sin razón —
  salvo que un CVE fuerce un pin específico.
- Cualquier bump de versión mayor (ej. `pandas 2.x → 3.x`) requiere una entrada en
  [changelog.md](changelog.md) bajo `Changed` y validación manual del pipeline antes de mergear.
