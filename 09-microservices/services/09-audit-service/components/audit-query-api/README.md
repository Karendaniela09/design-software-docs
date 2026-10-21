# audit-query-api

> Estado: 🟡 En progreso | Última actualización: 2026-08-13
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Arquitectura

> **Diseño previsto — no implementado.** Agnóstico de lenguaje.

## Tipo de componente
`-api` — API REST síncrona de **solo lectura**.

## Responsabilidad
Exponer **consulta y exportación** del event-store append-only `audit_record` para la
pantalla de auditoría. **No escribe** (los eventos entran únicamente por el `audit-worker`).
Gated por RBAC (`MOD_AUDIT`); resuelve el bloqueante B1 (pantalla de auditoría no construible
por falta de contrato de lectura).

## Tecnologías
| Capa | Tecnología |
|------|-----------|
| Runtime | Agnóstico — cualquier backend (a definir) |
| Framework | A definir |
| Persistencia | PostgreSQL 16 · schema `audit` (solo `SELECT`) |
| Transporte | HTTP/REST |

## Contrato
Ver [contract.md](./contract.md) y la fuente máquina
[`07-api/contracts/openapi/audit.yaml`](../../../../../07-api/contracts/openapi/audit.yaml).
