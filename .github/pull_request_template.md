## Resumen

<!-- Qué hace este PR en 1-3 frases. Qué problema resuelve o qué artefacto entrega. -->

## Cambios

<!-- Lista de cambios concretos. Ej: -->
- [ ]
- [ ]

## Cómo probar

<!-- Comando exacto para reproducir, dataset de salida esperado. Ej: -->
<!-- `pytest -v` y/o `python -m scraper.pipeline --pages 3 --with-detail` -->

## Riesgos

<!-- Ej: cambio de selector puede romper el extractor si el DOM del sitio cambia; -->
<!-- cambio de rate limit puede afectar tiempo total de la corrida. -->

## Checklist

- [ ] Los artefactos de `/DOCS` afectados están actualizados y consistentes entre sí
- [ ] El contrato de datos (`DOCS/data_contract.md`) no se rompió sin actualizar versión/changelog
- [ ] Se respetó la política de rate limit / User-Agent de `DOCS/onboarding_scraper.md`
- [ ] Se actualizó `DOCS/changelog.md` con la entrada correspondiente
- [ ] `pytest` en verde
- [ ] Sin secretos, tokens ni credenciales en el diff
- [ ] Documentación (`README`/`/DOCS`) actualizada si el comportamiento cambió
