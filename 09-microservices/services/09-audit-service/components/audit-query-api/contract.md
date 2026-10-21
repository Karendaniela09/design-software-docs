<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: contrato del API de solo lectura de auditoría (cierra B1)
fase: diseño (contratos) — preliminar
estado: draft
dependencias_entrada: audit-service/data-model.md (audit_record); iam rbac (MOD_AUDIT); 07-api/contracts/openapi/audit.yaml
consumidores_siguientes: frontend (pantalla de auditoría), backend audit-query-api cuando se construya
tldr: API REST solo lectura sobre el event-store append-only audit_record. Consulta por cursor con filtros por índice + exportación. Sin escritura (exclusiva del audit-worker).
decisiones_clave: solo lectura; cursor por received_at desc; RBAC AUDIT_LOG_VIEW/AUDIT_EXPORT; sin correlation_id físico
halts_registrados: ninguno
-->

# Contrato — audit-query-api

API REST de **solo lectura** sobre `audit_record` (schema `audit`). Fuente máquina:
[`07-api/contracts/openapi/audit.yaml`](../../../../../07-api/contracts/openapi/audit.yaml).

## Endpoints

| Método | Ruta | Descripción | Feature RBAC |
|---|---|---|---|
| `GET` | `/audit-records` | Lista **por cursor** con filtros (actor, servicio, tipo de evento, entidad, rango temporal) | `AUDIT_LOG_VIEW` |
| `GET` | `/audit-records/{id}` | Un registro con su `payload` completo | `AUDIT_LOG_VIEW` |
| `GET` | `/audit-records/export` | Exporta el resultado filtrado (CSV/JSON) | `AUDIT_EXPORT` |

## Reglas

- **Solo lectura** (`SELECT`). Sin `INSERT`/`UPDATE`/`DELETE`: la escritura es exclusiva del
  `audit-worker` (append-only por eventos).
- **Paginación por cursor** (`received_at` descendente); colección grande y continua
  (no offset). `limit` máx 100.
- **Filtros respaldados por índices** de `audit_record`: `event_type`, `source_service`,
  `actor_id`, `entity_id`, más rango sobre `received_at`. `entity_type` acompaña a `entity_id`.
- **RBAC**: `AUDIT_LOG_VIEW` para consultar, `AUDIT_EXPORT` para exportar; scope `GLOBAL`
  (`SYSTEM_ADMIN`) o `TRAINING_CENTER` (`CENTER_DIRECTOR`). Sin estos features → `403`.
- **PII**: el `payload` puede contener datos personales; el acceso queda acotado por
  feature+scope y la propia consulta puede auditarse. No se exponen internals en errores.
- **Correlación**: `audit_record` no lleva `correlation_id` físico; se correlaciona por
  `event_id` y por el `trace_id` del envelope de error transversal (`_shared.yaml`).
