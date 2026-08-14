<!--
Plantilla de Pull Request — founders25-scraper
Copia de referencia. La copia funcional que GitHub usa realmente está en
.github/pull_request_template.md — si cambias una, cambia la otra.
-->

## Resumen

<!-- Qué hace este PR en 1-3 frases. Qué problema resuelve o qué artefacto entrega. -->

## Cambios

<!-- Lista de cambios concretos. Ej: -->
- [ ]
- [ ]

## Cómo probar (conceptual)

<!-- Mientras no haya código ejecutable: qué artefacto de /DOCS revisar, qué checklist validar. -->
<!-- Cuando haya código: comando exacto para reproducir, dataset de salida esperado. -->

## Riesgos

<!-- Ej: cambio de selector puede romper el extractor si el DOM del sitio cambia; -->
<!-- cambio de rate limit puede afectar tiempo total de la corrida. -->

## Checklist

- [ ] Los artefactos de `/DOCS` afectados están actualizados y consistentes entre sí
- [ ] El contrato de datos (`data_contract.md`) no se rompió sin actualizar versión/changelog
- [ ] Se respetó la política de rate limit / User-Agent de `onboarding_scraper.md`
- [ ] Se actualizó `changelog.md` con la entrada correspondiente
- [ ] Sin secretos, tokens ni credenciales en el diff
- [ ] Documentación (`README`/`/DOCS`) actualizada si el comportamiento cambió
