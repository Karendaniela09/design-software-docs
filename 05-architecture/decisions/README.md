# Architecture Decision Records (ADR)

## Contexto

Este directorio contiene el registro de decisiones de arquitectura del proyecto **Horarios SENA**. Los ADRs documentan decisiones significativas sobre la arquitectura del sistema, incluyendo el contexto, la decisión tomada, las consecuencias y las alternativas consideradas.

## Convenciones

- **Formato:** `ADR-NNN-titulo-corto.md`
- **Estado:** `PROPOSED` | `ACCEPTED` | `SUPERSEDED` | `DEPRECATED`
- **Numeración:** Secuencial desde ADR-001.
- **Nunca se eliminan:** Los ADRs deprecados permanecen en `records/` con estado `DEPRECATED`.

## Plantilla

Usar el archivo `_template-adr.md` para crear nuevos ADRs.

## Registro de ADRs

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-001 | Clean Architecture para el backend | ACCEPTED |
| ADR-002 | Autenticación con JWT y Spring Security | ACCEPTED |
| ADR-003 | Validación de conflictos en tiempo real | ACCEPTED |
| ADR-004 | Auditoría append-only | ACCEPTED |
| ADR-005 | Microservicios con base de datos por servicio | ACCEPTED |
| ADR-006 | Sistema de notificaciones por email | ACCEPTED |
| ADR-007 | Generación de reportes asíncronos con workers | ACCEPTED |

## Referencias

- [../overview.md](../overview.md)
- [../cross-cutting.md](../cross-cutting.md)
- [../deployment.md](../deployment.md)
- [04-requirements/traceability-matrix.md](../../04-requirements/traceability-matrix.md)