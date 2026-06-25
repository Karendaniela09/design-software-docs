# Definition of Done

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

## Contexto

Este documento define los criterios que debe cumplir un documento para ser considerado **terminado (done)**. Un documento "done" es aquel que ha pasado por revisión, está aprobado y puede considerarse estable para su uso como referencia.

## Criterios de Done

Un documento está **done** cuando:

- [ ] Fue aprobado por al menos un revisor distinto al autor.
- [ ] Está enlazado desde el `README.md` de su sección.
- [ ] El estado del documento se cambió a 🟢 (Estable) en el encabezado.
- [ ] Los enlaces relativos dentro del documento funcionan correctamente.
- [ ] No contiene información sensible (credenciales, datos personales reales, etc.).
- [ ] El `CHANGELOG.md` fue actualizado si el cambio:
    - Modifica reglas de gobernanza (`00-governance/`).
    - Cambia la estructura de carpetas del repositorio.
    - Modifica un contrato compartido (API, modelo de datos, convenciones de Git).

## Notas

- Un documento puede permanecer en 🟡 (En progreso) durante el desarrollo y solo pasar a 🟢 cuando esté completamente validado.
- Si el documento es deprecado, seguir el proceso en [documentation-rules.md](./documentation-rules.md#estados).

## Referencias

- [documentation-rules.md](./documentation-rules.md)
- [definition-of-ready.md](./definition-of-ready.md)
- [CHANGELOG.md](../CHANGELOG.md)