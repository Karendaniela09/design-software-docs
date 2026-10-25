<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: contrato de API (OpenAPI 3.1)
fase: diseño (api-first)
estado: accepted
dependencias_entrada: 09-microservices/services/08-monitoring-service/data-model.md, 07-api/guidelines.md, 07-api/contracts/openapi/_shared.yaml
consumidores_siguientes: backend monitoring-api, alert-worker, frontend, pruebas de contrato
tldr: Seguimiento de fichas (KPIs, alertas, sesiones y planes de mejoramiento) con catálogos configurables y reportes propios. La entrega de notificaciones pertenece a notification-service. La fuente de verdad es monitoring.yaml.
decisiones_clave: OpenAPI publicable en 07-api/contracts/openapi/monitoring.yaml; paginación por cursor en kpi-trackings/generated-alerts; reportes descentralizados — solo dominio propio de monitoring-service
halts_registrados: ninguno
-->

# Contrato — monitoring-api

> Estado: 🟢 Aceptado | Última actualización: 2026-08-26

> **Fuente de verdad (normativa):** el spec OpenAPI 3.1 en
> [`07-api/contracts/openapi/monitoring.yaml`](../../../../../07-api/contracts/openapi/monitoring.yaml).
> Este documento es la **narrativa** que lo explica; ante cualquier diferencia, **manda el
> `monitoring.yaml`**. Convenciones transversales en
> [07-api/guidelines.md](../../../../../07-api/guidelines.md).

## Base URL

`/api/v1`

## Autenticación

Bearer JWT emitido por `iam-service`, verificado localmente vía JWKS. Todos los
endpoints requieren el header `Authorization: Bearer <token>` salvo que se indique lo
contrario. RBAC por `feature` + `scope` (módulo `MOD_MONITORING` en
[rbac-design.md](../../../../../09-microservices/services/01-iam-service/rbac-design.md)):
un token inválido o expirado retorna `401`; un feature insuficiente retorna `403`.

## Catálogos propios — `kpi_type` / `alert_type` / `risk_level` / `kpi_status`

`kpi_type` y `alert_type` son **configurables en runtime** por el equipo pedagógico
(sin deploy); exponen CRUD completo. `risk_level` (valores fijos INFO…CRITICAL) y
`kpi_status` (ON_TRACK/AT_RISK/CRITICAL, unificado vía FK a `risk_level`) son de
**solo lectura**.

### `GET /kpi-types` · `POST /kpi-types` · `GET|PUT|DELETE /kpi-types/{id}`

CRUD del catálogo de tipos de KPI. `DELETE` es soft delete (`is_active = false`).

- **Feature requerido:** `MON_KPI_VIEW` (lectura) / `MON_CATALOG_MANAGE` (escritura).

### `GET /alert-types` · `POST /alert-types` · `GET|PUT|DELETE /alert-types/{id}`

CRUD del catálogo de tipos de alerta (umbral por defecto, unidad, si afecta el
`overall_status` de la ficha).

- **Feature requerido:** `MON_ALERT_VIEW` (lectura) / `MON_CATALOG_MANAGE` (escritura).

### `GET /risk-levels` · `GET /kpi-statuses`

Solo lectura. Responden la lista paginada estándar `{ data, pagination }` (`page`, `page_size`;
[`guidelines.md` §6](../../../../../07-api/guidelines.md)), igual que el resto de las colecciones.

- **Feature requerido:** `MON_ALERT_VIEW` y `MON_KPI_VIEW` respectivamente.

## Seguimiento de ficha — `ficha_tracking` / `tracking_session`

### `GET /ficha-trackings` · `GET /ficha-trackings/{id}`

Seguimiento consolidado por ficha (estado global, conteo de alertas activas, próximas
fechas). **Solo lectura**: `ficha_tracking` se recalcula por el `alert-worker` a partir
de eventos de dominio, no se crea ni actualiza por REST.

- **Feature requerido:** `MON_DASHBOARD_FULL` (lista) / `MON_DASHBOARD_OWN` (detalle;
  también cubre el scope `OWN_FICHAS` del instructor asignado).
- **Filtros de lista:** `ficha_id`, `assigned_instructor_id`, `overall_status`.

### `GET /ficha-trackings/{id}/tracking-sessions` · `POST .../tracking-sessions` · `GET .../tracking-sessions/{session_id}`

Sesiones de seguimiento periódico (append-only). Normativa SENA: mínimo mensual para
fichas en Ejecución (Acuerdo 00003/2012). `attendance_percentage` la calcula el
servidor (columna generada).

- **Feature requerido:** `MON_TRACKING_SESSION_VIEW` (lectura) /
  `MON_TRACKING_SESSION_CREATE` (creación).
- **Filtros de lista:** `session_type`, `from`, `to` (rango de `session_date`).

## KPIs — `kpi_tracking`

### `GET /kpi-trackings` · `GET /kpi-trackings/{id}`

Mediciones de KPI por ficha, **solo lectura** (producidas por el `alert-worker`;
`kpi_tracking` está particionada por `measured_at`). Paginación por **cursor**
(guidelines §6: colección de crecimiento continuo).

- **Feature requerido:** `MON_KPI_VIEW`.
- **Filtros:** `ficha_tracking_id`, `kpi_type` (código), `kpi_status` (código), `from`,
  `to` (rango de `measured_at`).

## Alertas — `generated_alert`

### `GET /generated-alerts` · `GET /generated-alerts/{id}`

Alertas generadas, **solo lectura** (producidas por el `alert-worker`; ver
[alert-worker/contract.md](../alert-worker/contract.md)). Paginación por **cursor**.

- **Feature requerido:** `MON_ALERT_VIEW`.
- **Filtros:** `ficha_tracking_id`, `alert_type` (código), `risk_level` (código),
  `is_resolved`, `from`, `to` (rango de `generated_at`).

### `PUT /generated-alerts/{id}/resolve`

Marca la alerta como resuelta (`is_resolved`, `resolved_by`, `resolution_notes`,
`resolved_at`).

- **Feature requerido:** `MON_ALERT_RESOLVE`.

## Planes de mejoramiento — `improvement_plan`

### `GET /improvement-plans` · `POST /improvement-plans` · `GET|PUT /improvement-plans/{id}`

CRUD de planes de mejoramiento a nivel de ficha (opcionalmente ligados a una
`generated_alert`; distinto del `actor_improvement_plan` por actor individual en
actors-service). `PUT` cubre avance y transición de estado
(`PENDING` → `IN_PROGRESS` → `COMPLETED` / `CANCELLED`); una transición inválida
retorna `409`.

- **Feature requerido:** `MON_IMPROVEMENT_PLAN_MANAGE` (no existe variante `_VIEW`
  separada en el catálogo RBAC actual; se reutiliza `MANAGE` también para lectura).
- **Filtros de lista:** `ficha_tracking_id`, `learner_id`, `instructor_id`, `status`.

## Límite con notification-service

`monitoring-api` no expone `/sent-notifications` ni persiste `sent_notification`. La entrega y consulta de notificaciones pertenece a [`notification-service`](../../../10-notification-service/README.md). Monitoring publica `monitoring.alert.triggered`; Notification decide y registra la entrega.

---

# Reportes (dominio propio)

Reportes **descentralizados** (guidelines §11): `monitoring-api` sólo publica
indicadores calculados sobre **sus propias tablas** (`kpi_tracking`, `ficha_tracking`,
`kpi_status`, `risk_level`); no agrega datos de otros servicios ni actúa como hub
central de reportes.

### `GET /reports/kpi-summary`

Última medición de cada KPI por ficha, con su estado y nivel de riesgo. Cruza
`kpi_tracking` con `kpi_type`, `kpi_status` y `risk_level`.

- **Feature requerido:** `MON_REPORT_VIEW`.
- **Filtros:** `ficha_tracking_id`, `kpi_type`, `status` (código de `kpi_status`),
  `from`, `to`.
- **Inventario:** Usuarios: coordinación académica, instructores de seguimiento,
  panel de monitoreo · Frecuencia: on-demand · Formato: JSON · Fuente:
  `monitoring_db.kpi_tracking`, `kpi_type`, `kpi_status`, `risk_level`.

### `GET /reports/indicators`

Indicadores agregados de salud de fichas: cantidad de fichas y promedio de
`active_alert_count` agrupados por `overall_status_id` (vía `kpi_status` → `risk_level`).
Vista de tablero, no de detalle por ficha.

- **Feature requerido:** `MON_REPORT_VIEW`.
- **Filtros:** `status` (código de `kpi_status`), `assigned_instructor_id`.
- **Inventario:** Usuarios: dirección de centro, coordinación académica · Frecuencia:
  on-demand · Formato: JSON · Fuente: `monitoring_db.ficha_tracking`, `kpi_status`,
  `risk_level`.

---

## Formato de error estándar

Aplica el **envelope estándar de la plataforma** ([guidelines §7](../../../../../07-api/guidelines.md) /
`_shared.yaml#/components/schemas/Error`):

```json
{
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "El plan de mejoramiento ya está COMPLETED.",
    "details": [ { "field": "status", "issue": "INVALID_STATE_TRANSITION" } ],
    "trace_id": "b3f1c2a4-..."
  }
}
```

## Códigos de error propios

| Código | HTTP | Descripción |
|--------|------|-------------|
| `INVALID_STATE_TRANSITION` | 409 | Transición de estado no permitida (ej. plan ya `COMPLETED`, alerta ya resuelta) |
| `CATALOG_CODE_CONFLICT` | 409 | `code` de `kpi_type`/`alert_type` ya existe |
| `EXCLUSIVE_ARC_VIOLATION` | 422 | `generated_alert` con `affected_learner_id` y `affected_instructor_id` poblados a la vez |

## Referencias

- Modelo de datos: [data-model.md](../../data-model.md)
- Eventos del servicio: [events.md](../../events.md)
- Contrato alert-worker: [alert-worker/contract.md](../alert-worker/contract.md)
- Servicio de notificaciones: [notification-service](../../../10-notification-service/README.md)
- ADR-001 (broker): [ADR-001](../../../../../05-architecture/decisions/records/ADR-001-message-broker.md)
- ADR-004 (estados y auditoría): [ADR-004](../../../../../05-architecture/decisions/records/ADR-004-status-parametrization-and-audit-standard.md)
