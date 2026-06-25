# Definition of Ready

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

## Contexto

Este documento define los criterios que debe cumplir un documento para ser considerado **listo para revisión** (Pull Request). Estos criterios aseguran que las revisiones sean eficientes y que los documentos tengan un nivel mínimo de calidad antes de ser evaluados por otros miembros del equipo.

## Criterios de Ready

Un documento está **listo para revisión** cuando:

- [ ] Tiene título, estado, fecha y autor o equipo responsable.
- [ ] Explica su contexto y propósito (sección `## Contexto` con texto sustancial).
- [ ] El documento tiene al menos las secciones `## Contexto` y `## Contenido` con texto real (no vacías, no solo comentarios).
- [ ] Está enlazado desde el `README.md` de su sección correspondiente.
- [ ] Los diagramas referenciados existen en `08-uml/` con fuente editable y exportación.
- [ ] No contiene credenciales, tokens, datos personales reales ni información sensible (ver [security-rules.md](./security-rules.md)).
- [ ] Ha sido revisado por el autor antes de abrir el PR (autoevaluación).

## Notas

- Si el documento requiere aprobación de arquitectura, debe indicarlo en el PR.
- Los documentos que no cumplan estos criterios serán devueltos para completar.

## Referencias

- [security-rules.md](./security-rules.md)
- [documentation-rules.md](./documentation-rules.md)
- [definition-of-done.md](./definition-of-done.md)