# audit-service

> Estado: 🟡 Revisión | Última actualización: 2026-10-07
> Autor: Kevin Andrey Culma (Arquitecto) | Equipo: Arquitectura.

| Campo | Valor |
|---|---|
| Módulo | Transversal |
| App repo | `design-software-audit-service` |
| DB repo | `design-software-audit-db` |
| Stack | Go |
| Deployables | audit-query-api, audit-worker |
| Estado observado | Query API de solo lectura y worker AMQP operativos; historial append-only con deduplicación. |

## Responsabilidad

Registro append-only de auditoría y consulta de eventos auditables.

## Persistencia

- Esquemas: audit
- Tablas: audit.audit_event_seen, audit.audit_record, audit.audit_record_2026_08, audit.audit_record_default

## API detectada

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/api/v1/health` | `design-software-audit-service/internal/adapter/in/httpapi/query.go` |
| GET | `/api/v1/audit-records` | `design-software-audit-service/internal/adapter/in/httpapi/query.go` |
| GET | `/api/v1/audit-records/{id}` | `design-software-audit-service/internal/adapter/in/httpapi/query.go` |
| GET | `/api/v1/audit-records/export` | `design-software-audit-service/internal/adapter/in/httpapi/query.go` |

## Configuración

- `DATABASE_URL`, `IAM_JWKS_URL`, `IAM_JWT_ISSUER`, `AUDIT_CURSOR_SECRET` (query API)
- `MESSAGE_BROKER_URL`, `BROKER_CONSUMER_GROUP`, `AUDIT_EVENTS_EXCHANGE` (worker)

## Notas

El contrato OpenAPI canónico está en `design-software-audit-service/api/openapi/audit.yaml`.
El worker consume AMQP y persiste auditoría idempotente.
