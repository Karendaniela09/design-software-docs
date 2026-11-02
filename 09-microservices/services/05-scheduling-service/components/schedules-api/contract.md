<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: contrato de API (OpenAPI 3.1)
fase: diseño (api-first)
estado: accepted
dependencias_entrada: 09-microservices/services/05-scheduling-service/data-model.md, 07-api/guidelines.md, 07-api/contracts/openapi/_shared.yaml
consumidores_siguientes: backend scheduling-service, frontend, pruebas de contrato
tldr: CRUD de horarios (schedule) con máquina de estados DRAFT→UNDER_REVIEW→PUBLISHED→ARCHIVED, sesiones de clase (class_session), catálogo de franjas horarias (time_slot), detección/resolución de conflictos (scheduling_conflict) y 5 reportes propios. La fuente de verdad es scheduling.yaml.
decisiones_clave: OpenAPI publicable en 07-api/contracts/openapi/scheduling.yaml; bloqueo optimista por row_version en mutaciones del agregado schedule; reportes por servicio (guidelines §11); envelope de error estándar (guidelines §7)
halts_registrados: ninguno
-->

# Contrato — schedules-api

> Estado: 🟢 Aceptado | Última actualización: 2026-08-06
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Arquitectura

> **Fuente de verdad (normativa):** el spec OpenAPI 3.1 en
> [`07-api/contracts/openapi/scheduling.yaml`](../../../../../07-api/contracts/openapi/scheduling.yaml).
> Este documento es la **narrativa** que lo explica; ante cualquier diferencia, **manda el
> `scheduling.yaml`**. Convenciones transversales en
> [07-api/guidelines.md](../../../../../07-api/guidelines.md).

> **Diseño previsto — no implementado.** Contrato a nivel de protocolo REST/JSON. No hay código de ningún lenguaje: los ejemplos son JSON genérico. Recursos y campos derivados de las entidades reales del [modelo de datos](../../data-model.md): `schedule`, `time_slot`, `class_session`, `scheduling_conflict`.

---

## Autenticación y autorización

Bearer JWT emitido por `iam-service`. Todos los endpoints requieren:

```
Authorization: Bearer <token>
```

La autorización es por **feature + scope** (RBAC de tres dimensiones: módulo → feature → scope). El JWT lleva pre-calculada la lista `features` con el formato `FEATURE_CODE:SCOPE_TYPE` (ver [rbac-design.md](../../../01-iam-service/rbac-design.md)). Cada endpoint exige un feature del módulo `MOD_SCHEDULING`; el `scope_type` acompañante determina el filtro de datos que el servicio aplica:

| scope_type | Filtro que aplica `schedules-api` |
|-----------|-----------------------------------|
| `GLOBAL` | Sin filtro adicional |
| `TRAINING_CENTER` | Solo horarios cuya ficha pertenece a `jwt.training_center_id` |
| `OWN_SCHEDULE` | Solo `class_session` con `instructor_id = jwt.actor_id` |
| `OWN_FICHA_AS_LEARNER` | Solo el `schedule` de la ficha activa del aprendiz (`jwt.ficha_id`) |

Si falta el feature requerido → `403 FORBIDDEN`. Si el token es inválido o expiró → `401 UNAUTHORIZED`.

## Base URL

`/api/v1`

## Convenciones

- Formato de intercambio: JSON (`Content-Type: application/json`).
- Identificadores: UUID v4.
- Fechas y horas: `session_date` en `YYYY-MM-DD`; horas (`start_time`, `end_time`) en `HH:mm` (24 h); timestamps en ISO-8601 UTC.
- Concurrencia: el agregado `schedule` usa bloqueo optimista con `row_version`; las mutaciones envían el `row_version` esperado y reciben `409 CONFLICT` si no coincide.

---

## Endpoints — Horarios (`schedule`)

| Método | Path | Descripción | Feature requerido |
|--------|------|-------------|-------------------|
| `GET` | `/schedules` | Listar horarios (paginado, filtros) | `SCH_VIEW_ALL` / `SCH_VIEW_OWN` |
| `POST` | `/schedules` | Crear borrador (`DRAFT`) para una ficha y período | `SCH_CREATE` |
| `GET` | `/schedules/{id}` | Obtener un horario con sus sesiones | `SCH_VIEW_ALL` / `SCH_VIEW_OWN` |
| `PUT` | `/schedules/{id}` | Editar metadatos del borrador (`name`) | `SCH_EDIT` |
| `DELETE` | `/schedules/{id}` | Eliminar borrador (solo `DRAFT`) | `SCH_DELETE_DRAFT` |
| `POST` | `/schedules/{id}/validate` | Validar (verificación síncrona final) y pasar a `UNDER_REVIEW` | `SCH_EDIT` |
| `POST` | `/schedules/{id}/publish` | Publicar (`UNDER_REVIEW → PUBLISHED`); emite `scheduling.schedule.published` vía Outbox | `SCH_PUBLISH` |
| `POST` | `/schedules/{id}/archive` | Archivar (`PUBLISHED → ARCHIVED`) | `SCH_ARCHIVE` |

Filtros de `GET /schedules`: `ficha_id`, `period`, `status` (`DRAFT|UNDER_REVIEW|PUBLISHED|ARCHIVED`).

**Ejemplo — `POST /schedules`**

Request:
```json
{
  "ficha_id": "b7c1e2a0-0000-4000-8000-000000000001",
  "period": "2026-1",
  "name": "Horario ADSO 2026-1 jornada mañana"
}
```

Response `201`:
```json
{
  "id": "f0a1b2c3-0000-4000-8000-0000000000aa",
  "ficha_id": "b7c1e2a0-0000-4000-8000-000000000001",
  "period": "2026-1",
  "name": "Horario ADSO 2026-1 jornada mañana",
  "status": "DRAFT",
  "published_at": null,
  "published_by": null,
  "row_version": 0,
  "created_by": "a1a1a1a1-0000-4000-8000-000000000000",
  "created_at": "2026-08-01T14:00:00Z",
  "updated_at": "2026-08-01T14:00:00Z"
}
```

> **Invariante de inmutabilidad:** un `schedule` en `PUBLISHED` no admite `PUT`/`DELETE` (solo la transición a `ARCHIVED`). La API responde `409 CONFLICT` con `error.code: SCHEDULE_IMMUTABLE`; todo cambio debe hacerse creando un nuevo borrador. `DELETE` requiere además el `row_version` vigente (query param), igual que las demás mutaciones del agregado.

---

## Endpoints — Sesiones de clase (`class_session`)

| Método | Path | Descripción | Feature requerido |
|--------|------|-------------|-------------------|
| `GET` | `/schedules/{id}/sessions` | Listar sesiones del horario (paginado) | `SCH_VIEW_ALL` / `SCH_VIEW_OWN` |
| `POST` | `/schedules/{id}/sessions` | Agregar una sesión al borrador | `SCH_EDIT` |
| `GET` | `/sessions` | Listar sesiones (todas las que el scope permita, paginado, filtros) | `SCH_VIEW_ALL` / `SCH_VIEW_OWN` |
| `GET` | `/sessions/{sessionId}` | Obtener una sesión | `SCH_VIEW_ALL` / `SCH_VIEW_OWN` |
| `PUT` | `/sessions/{sessionId}` | Editar una sesión del borrador (`notes`, reasignaciones) | `SCH_EDIT` |
| `DELETE` | `/sessions/{sessionId}` | Eliminar (soft delete) una sesión del borrador | `SCH_EDIT` |
| `POST` | `/sessions/{sessionId}/cancel` | Cancelar sesión (`ACTIVE → CANCELLED`); emite `scheduling.class_session.cancelled` | `SCH_EDIT` |

Filtros de `GET /sessions`: `schedule_id`, `instructor_id`, `environment_id`, `status` (`ACTIVE|CANCELLED`), `from`/`to` (rango de `session_date`).

**Ejemplo — `POST /schedules/{id}/sessions`**

Request:
```json
{
  "competency_id": "c0000000-0000-4000-8000-000000000010",
  "environment_id": "e0000000-0000-4000-8000-000000000020",
  "instructor_id": "d0000000-0000-4000-8000-000000000030",
  "time_slot_id": "70000000-0000-4000-8000-000000000040",
  "session_date": "2026-07-07",
  "notes": null
}
```

Response `201` (`start_time`, `end_time` y `day_of_week` se copian de `time_slot` y son inmutables tras la creación):
```json
{
  "id": "51000000-0000-4000-8000-0000000000f1",
  "schedule_id": "f0a1b2c3-0000-4000-8000-0000000000aa",
  "competency_id": "c0000000-0000-4000-8000-000000000010",
  "environment_id": "e0000000-0000-4000-8000-000000000020",
  "instructor_id": "d0000000-0000-4000-8000-000000000030",
  "time_slot_id": "70000000-0000-4000-8000-000000000040",
  "session_date": "2026-07-07",
  "day_of_week": 2,
  "start_time": "07:00",
  "end_time": "10:00",
  "status": "ACTIVE",
  "notes": null,
  "updated_at": "2026-08-01T14:05:00Z"
}
```

---

## Endpoints — Franjas horarias (`time_slot`, catálogo)

| Método | Path | Descripción | Feature requerido |
|--------|------|-------------|-------------------|
| `GET` | `/time-slots` | Listar franjas (paginado) | `SCH_VIEW_ALL` |
| `POST` | `/time-slots` | Crear franja | `SCH_CREATE` |
| `GET` | `/time-slots/{id}` | Obtener franja | `SCH_VIEW_ALL` |
| `PUT` | `/time-slots/{id}` | Editar franja | `SCH_EDIT` |
| `DELETE` | `/time-slots/{id}` | Eliminar (soft delete) franja no referenciada por sesiones activas | `SCH_EDIT` |

Campos de `time_slot`: `name`, `day_of_week` (1=lunes … 7=domingo), `start_time`, `end_time`, `shift` (`DAY|NIGHT|MIXED`).

---

## Endpoints — Conflictos (`scheduling_conflict`)

| Método | Path | Descripción | Feature requerido |
|--------|------|-------------|-------------------|
| `GET` | `/schedules/{id}/conflicts` | Listar conflictos detectados en el borrador (paginado) | `SCH_CONFLICT_VIEW` |
| `POST` | `/conflicts/{conflictId}/resolve` | Marcar conflicto como resuelto (`is_resolved = true`) | `SCH_CONFLICT_RESOLVE` |

**Ejemplo — item de conflicto**
```json
{
  "id": "90000000-0000-4000-8000-0000000000c1",
  "schedule_id": "f0a1b2c3-0000-4000-8000-0000000000aa",
  "session_a_id": "51000000-0000-4000-8000-0000000000f1",
  "session_b_id": "51000000-0000-4000-8000-0000000000f2",
  "conflict_type": "INSTRUCTOR_DOUBLE_BOOKED",
  "description": "El instructor ya tiene una sesión el 2026-07-07 de 07:00 a 10:00",
  "is_resolved": false,
  "detected_at": "2026-08-01T14:06:00Z"
}
```

Valores de `conflict_type`: `INSTRUCTOR_DOUBLE_BOOKED`, `ENVIRONMENT_DOUBLE_BOOKED`, `SESSIONS_OVERLAP`.

> No se puede publicar (`POST /schedules/{id}/publish`) un horario con conflictos sin resolver: la API responde `409 CONFLICT` con `error.code: UNRESOLVED_CONFLICTS`.

---

## Paginación

Todos los listados usan paginación por offset con parámetros de query:

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `page` | Número de página (base 1) | `1` |
| `page_size` | Tamaño de página (máx. 100) | `20` |
| `sort` | Campo y dirección, ej. `created_at:desc` | según recurso |

Respuesta paginada (offset), envelope estándar (`_shared.yaml#/components/schemas/Pagination`):
```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 137,
    "total_pages": 7
  }
}
```

Para colecciones grandes/continuas (ej. `GET /reports/schedule-conflicts`) se usa paginación por
**cursor** (`_shared.yaml#/components/schemas/CursorPagination`): `?cursor=<opaco>&limit=50`,
respuesta con `pagination: { next_cursor, limit, has_more }`.

---

## Reportes (dominio propio)

Reportes propios del dominio scheduling (guidelines §11). **Solo lectura**; nunca mutan estado.

### `GET /reports/schedule-by-instructor`

Carga de sesiones agregada por instructor.

- **Feature requerido:** `SCH_REPORT_VIEW` (cualquier instructor) **o** `SCH_VIEW_OWN` con scope `OWN_SCHEDULE`.
  Sin `SCH_REPORT_VIEW`, `instructor_id` es obligatorio y debe ser igual al claim `actor_id` del JWT; si no, `403 FORBIDDEN`
  (lo usa "Mi horario" del instructor para su resumen semanal). Los demás reportes siguen exigiendo `SCH_REPORT_VIEW`.
- **Filtros:** `instructor_id`, `from`, `to` (rango de `session_date`).
- **Inventario:** Usuarios: coordinadores académicos y jefes de área · Frecuencia: on-demand/semanal · Formato: JSON · Fuente: `class_session`.

### `GET /reports/schedule-by-ficha`

Estado y resumen de sesiones del horario por ficha.

- **Feature requerido:** `SCH_REPORT_VIEW`.
- **Filtros:** `ficha_id`, `period`, `status`, `from`, `to` (rango de `created_at` del horario).
- **Inventario:** Usuarios: coordinadores académicos y bienestar · Frecuencia: on-demand/diaria · Formato: JSON · Fuente: `schedule` + `class_session`.

### `GET /reports/schedule-by-environment`

Carga de sesiones agregada por ambiente de formación.

- **Feature requerido:** `SCH_REPORT_VIEW`.
- **Filtros:** `environment_id`, `from`, `to` (rango de `session_date`).
- **Inventario:** Usuarios: gestores de ambientes y coordinadores académicos · Frecuencia: on-demand/semanal · Formato: JSON · Fuente: `class_session`.

### `GET /reports/schedule-conflicts`

Conflictos de horario detectados en toda la plataforma. **Paginación por cursor** (colección
grande/continua, guidelines §6) a diferencia de `GET /schedules/{id}/conflicts` (por horario,
offset).

- **Feature requerido:** `SCH_REPORT_VIEW`.
- **Filtros:** `schedule_id`, `conflict_type`, `is_resolved`, `from`, `to` (rango de `detected_at`).
- **Inventario:** Usuarios: arquitectura y soporte de plataforma · Frecuencia: on-demand · Formato: JSON · Fuente: `scheduling_conflict`.

### `GET /reports/environment-occupancy`

Tasa de ocupación de ambientes (`occupied_slots` / `total_slots`) en un rango de fechas, cruzando
`class_session` contra el catálogo `time_slot`.

- **Feature requerido:** `SCH_REPORT_VIEW`.
- **Filtros:** `environment_id`, `from`, `to` (rango de `session_date`).
- **Inventario:** Usuarios: gestores de ambientes y subdirectores de centro · Frecuencia: on-demand/mensual · Formato: JSON · Fuente: `class_session` + `time_slot`.

---

## Formato de error estándar

Aplica el **envelope estándar de la plataforma** ([guidelines §7](../../../../../07-api/guidelines.md) /
`_shared.yaml#/components/schemas/Error`):

```json
{
  "error": {
    "code": "SCHEDULE_NOT_FOUND",
    "message": "El horario solicitado no existe",
    "trace_id": "b3f1c2a4-9e21-4d3a-8f0c-1a2b3c4d5e6f"
  }
}
```

Errores de validación agregan el detalle por campo en `error.details`:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "La solicitud contiene campos inválidos",
    "details": [
      { "field": "period", "issue": "formato inválido, se espera YYYY-N" }
    ],
    "trace_id": "b3f1c2a4-9e21-4d3a-8f0c-1a2b3c4d5e6f"
  }
}
```

| HTTP | `error.code` (ejemplos) | Situación |
|------|--------------------------|-----------|
| `400` | `VALIDATION_ERROR` | Payload o parámetros inválidos |
| `401` | `UNAUTHORIZED` | JWT ausente, inválido o expirado |
| `403` | `FORBIDDEN` | Falta el feature o el scope no cubre el recurso |
| `404` | `SCHEDULE_NOT_FOUND`, `SESSION_NOT_FOUND` | Recurso inexistente |
| `409` | `SCHEDULE_IMMUTABLE`, `UNRESOLVED_CONFLICTS`, `ROW_VERSION_MISMATCH` | Conflicto de estado o concurrencia |
| `429` | `TOO_MANY_REQUESTS` | Límite de tasa superado (`POST .../validate`, reportes) |
