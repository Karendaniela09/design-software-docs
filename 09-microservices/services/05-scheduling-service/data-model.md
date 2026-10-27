# Modelo de datos — scheduling-service

> Estado: 🟢 Estable | Última actualización: 2026-10-26
> Naming: entidades y atributos en inglés (HALT-DB-NAMING)

## Convenciones de modelado (transversales)

> **Estándar autoritativo:** [06-data/modeling-conventions.md](../../../06-data/modeling-conventions.md) (ratificado en ADR-004). Resumen aplicable:

- **Tres conceptos de estado (no confundir):** (1) *ciclo de vida del registro* (técnico) → `is_active` + soft delete (`deleted_at`); (2) *estado de negocio* (parametrizable) → FK `status_id` → catálogo `status`; (3) *enum técnico cerrado* (CC/CE, EMAIL/IN_APP…) → `VARCHAR` + `CHECK (... IN (...))`. **No se usa el tipo `ENUM` nativo de Postgres** (su `ALTER TYPE` bloquea migraciones independientes por servicio).
- **Estados de negocio parametrizables:** el servicio implementa `status_category` + `status` (+ `status_transition` si aplica) en su propia BD; los agregados con máquina de estados referencian `status_id`. Solo migran estados de **negocio**; los enums técnicos cerrados (`*_type`, `channel`…) permanecen como `VARCHAR + CHECK`.
- **Auditoría (tablas transaccionales):** `created_at`/`created_by`, `updated_at`/`updated_by`, `deleted_at`/`deleted_by` (soft delete), `is_active` y `row_version`. Acciones del sistema usan `SYSTEM_ACTOR_ID = 00000000-0000-0000-0000-000000000000`. Catálogos: `created_*`/`updated_*` + `is_active` (sin soft delete). Append-only: solo el timestamp de inserción.
- **Acciones referenciales:** cada FK declara `ON UPDATE`/`ON DELETE`. Por defecto: catálogo/padre → `RESTRICT`; hijo de agregado (composición) → `CASCADE`; FK opcional → `SET NULL`.
- **Nomenclatura de constraints:** `pk_<tabla>`, `uq_<tabla>_<cols>`, `fk_<tabla>_<ref>`, `ck_<tabla>_<regla>`, `ix_<tabla>_<cols>`.

## Entidades propias

### `schedule`

Agregado raíz. Contiene el conjunto de sesiones de clase para una ficha en un período.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `ficha_id` | UUID | No | Referencia externa → academic-management-service |
| `period` | VARCHAR(10) | No | Ej: `2026-1` |
| `name` | VARCHAR(200) | Sí | Nombre descriptivo del horario |
| `status` | VARCHAR(30) | No | DRAFT / UNDER_REVIEW / PUBLISHED / ARCHIVED — `CHECK (status IN ('DRAFT','UNDER_REVIEW','PUBLISHED','ARCHIVED'))` |
| `published_at` | TIMESTAMPTZ | Sí | Null hasta publicación |
| `published_by` | UUID | Sí | ID de usuario que publicó |
| `row_version` | INT | No | Bloqueo optimista, `DEFAULT 0` (agregado raíz editable) |
| `created_by` | UUID | No | ID de usuario (iam-service) |
| `created_at` | TIMESTAMPTZ | No | |
| `updated_at` | TIMESTAMPTZ | No | |

**Invariante**: Una vez `status = PUBLISHED`, el registro es inmutable. Los cambios generan un nuevo `schedule` en estado `DRAFT`.

**Enforcement de inmutabilidad:** la inmutabilidad de un `schedule` en estado `PUBLISHED` se garantiza a nivel BD con un trigger `BEFORE UPDATE/DELETE` que rechaza cualquier cambio cuando `status = 'PUBLISHED'`, salvo la transición `status → ARCHIVED`.

### `time_slot`

Franja horaria reutilizable (ej: `Mañana 07:00–10:00`).

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `name` | VARCHAR(50) | No | Etiqueta (ej: `Morning 07:00-10:00`) |
| `day_of_week` | SMALLINT | No | 1=lunes … 7=domingo |
| `start_time` | TIME | No | |
| `end_time` | TIME | No | |
| `shift` | VARCHAR(20) | No | DAY / NIGHT / MIXED — `CHECK (shift IN ('DAY','NIGHT','MIXED'))` |

### `class_session`

Instancia de una clase: vincula ficha → instructor → ambiente → franja.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `schedule_id` | UUID | No | FK → schedule |
| `competency_id` | UUID | No | Referencia externa → academic-management-service |
| `environment_id` | UUID | No | Referencia externa → training-environment-service |
| `instructor_id` | UUID | No | Referencia externa → actors-service |
| `time_slot_id` | UUID | No | FK → time_slot |
| `start_time` | TIME | No | Copia desnormalizada de time_slot.start_time (inmutable tras creación) |
| `end_time` | TIME | No | Copia desnormalizada de time_slot.end_time (inmutable tras creación) |
| `day_of_week` | SMALLINT | No | Copia desnormalizada de time_slot.day_of_week (inmutable tras creación) |
| `session_date` | DATE | No | Fecha concreta de la sesión |
| `status` | VARCHAR(20) | No | ACTIVE / CANCELLED — `CHECK (status IN ('ACTIVE','CANCELLED'))` |
| `notes` | TEXT | Sí | |
| `updated_at` | TIMESTAMPTZ | No | |

**Desnormalización intencional (3FN exception):** start_time, end_time y day_of_week son copias inmutables de time_slot. Se duplican aquí para que la detección de conflictos pueda usar índices directos en class_session sin JOINs, cumpliendo el SLO de < 2 s para validación de horario completo.

### `scheduling_conflict`

Conflicto detectado durante la validación del horario en estado DRAFT.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `schedule_id` | UUID | No | FK → schedule |
| `session_a_id` | UUID | No | FK → class_session |
| `session_b_id` | UUID | Sí | FK → class_session (null si conflicto simple) |
| `conflict_type` | VARCHAR(50) | No | 6 valores — `CHECK (conflict_type IN ('INSTRUCTOR_DOUBLE_BOOKED','ENVIRONMENT_DOUBLE_BOOKED','SESSIONS_OVERLAP','ENVIRONMENT_MAINTENANCE','INSTRUCTOR_UNAVAILABLE','INSTRUCTOR_TRAVEL_CONFLICT'))` |
| `description` | TEXT | No | Detalle legible del conflicto |
| `is_resolved` | BOOLEAN | No | false = pendiente de corrección |
| `detected_at` | TIMESTAMPTZ | No | |
| `severity` | VARCHAR(10) | No | LOW/MEDIUM/HIGH/CRITICAL (default MEDIUM) — *(refinamiento G1)* |
| `resolved_by` | UUID | Sí | actor que resolvió — *(G1)* |
| `resolved_at` | TIMESTAMPTZ | Sí | *(G1)* |
| `resolution_reason` | TEXT | Sí | justificación obligatoria al resolver — *(G1)* |
| `is_blocking_publication` | BOOLEAN | No | si bloquea publicar (default true) — *(G1)* |

**`class_session`** añade `execution_status` VARCHAR(15) `CHECK (PENDING/EXECUTED/NOT_EXECUTED/CANCELLED)` (default PENDING) — hecho de ejecución, distinto de `status` de programación *(D-4; asistencia individual = V2)*.



### `environment_availability_projection`

Read model local de disponibilidad de ambientes usado por la validación de horarios (HU-SCH-004 / ADR-002). `environment_id` es una referencia lógica al servicio de Training Environment; no tiene FK física entre servicios.

| Campo | Tipo | Nullable | Descripción |
|---|---|---|---|
| `id` | UUID | No | PK |
| `environment_id` | UUID | No | Ambiente proyectado; único |
| `available` | BOOLEAN | No | Disponibilidad efectiva |
| `effective_from` | TIMESTAMPTZ | Sí | Inicio de vigencia conocido |
| `reason` | TEXT | Sí | Motivo de indisponibilidad |
| `last_event_id` | UUID | No | Último evento aplicado; único para deduplicar la proyección |
| `updated_at` | TIMESTAMPTZ | No | Actualización, default `now()` |

### `instructor_availability_projection`

Read model local de disponibilidad de instructores por competencia (HU-SCH-004 / ADR-002). `instructor_id` y `competency_id` son referencias lógicas, sin FK física a Actors o Academic Management.

| Campo | Tipo | Nullable | Descripción |
|---|---|---|---|
| `id` | UUID | No | PK |
| `instructor_id` | UUID | No | Instructor proyectado |
| `competency_id` | UUID | Sí | Competencia; null cuando la disponibilidad no se limita a una competencia |
| `available` | BOOLEAN | No | Disponibilidad efectiva |
| `last_event_id` | UUID | No | Último evento aplicado; único para deduplicar la proyección |
| `updated_at` | TIMESTAMPTZ | No | Actualización, default `now()` |

Tiene una restricción única en `(instructor_id, competency_id)`.

### `outbox`

Staging transaccional del evento `scheduling.class_session.cancelled` (HU-SCH-003). Esta tabla guarda el evento de dominio en la misma transacción que el cambio; el relay/broker está fuera de este changeset y pertenece al alcance posterior de HU-SCH-007.

| Campo | Tipo | Nullable | Descripción |
|---|---|---|---|
| `id` | UUID | No | PK |
| `event_id` | UUID | No | Identidad única del evento |
| `event_type` | VARCHAR(128) | No | Tipo del evento |
| `payload` | JSONB | No | Payload del evento |
| `status` | VARCHAR(16) | No | `PENDING`, `PUBLISHED` o `FAILED` |
| `created_at` | TIMESTAMPTZ | No | Alta del evento |
| `published_at` | TIMESTAMPTZ | Sí | Momento de publicación |

`event_id` tiene restricción única; `ck_outbox_status` limita los estados permitidos.

### `site_travel_time`

Matriz de tiempos de traslado entre sedes, usada para detectar `INSTRUCTOR_TRAVEL_CONFLICT` (D-11).

| Campo | Tipo | Nullable | Descripción |
|---|---|---|---|
| `id` | UUID | No | PK; default `gen_random_uuid()` |
| `origin_site_id` | UUID | No | Referencia lógica a la sede de origen |
| `destination_site_id` | UUID | No | Referencia lógica a la sede de destino |
| `travel_minutes` | INT | No | Tiempo de traslado; no puede ser negativo |
| `is_active` | BOOLEAN | No | Default `true` |
| `created_at`, `updated_at` | TIMESTAMPTZ | No | Defaults `now()` |

La pareja origen/destino es única (`uq_site_travel_time`); `ck_site_travel_time_minutes` exige `travel_minutes >= 0`.

### `ficha_training_center_projection`

Proyección local de `ficha_id` a `training_center_id` para filtrar lecturas con scope `TRAINING_CENTER` (HU-SCH-008). Academic Management es dueño de la relación de negocio; la integración debe sincronizar la proyección. No hay FK física entre bases.

| Campo | Tipo | Nullable | Descripción |
|---|---|---|---|
| `ficha_id` | UUID | No | PK; ficha proyectada |
| `training_center_id` | UUID | No | Centro de formación asociado |
| `updated_at` | TIMESTAMPTZ | No | Actualización, default `now()` |

El índice `idx_ficha_training_center_projection_center` cubre `(training_center_id, ficha_id)`.

## Referencias externas

| Campo | Referencia lógica | Servicio propietario |
|-------|-------------------|----------------------|
| `ficha_id` | `enrollment_ficha.id` | `academic-management-service` |
| `competency_id` | `competency.id` | `academic-management-service` |
| `environment_id` | `environment.id` | `training-environment-service` |
| `instructor_id` | `instructor.id` | `actors-service` |

## Índices relevantes

| Tabla | Campos | Tipo | Motivo |
|-------|--------|------|--------|
| `schedule` | `(ficha_id, period) WHERE status = 'PUBLISHED'` | UNIQUE parcial | Solo un horario PUBLISHED por ficha/período; permite múltiples DRAFT/ARCHIVED |
| `schedule` | `status` | B-Tree | Filtro por DRAFT / PUBLISHED |
| `class_session` | `(instructor_id, session_date, start_time, end_time)` | B-Tree | Detección de conflictos de instructor |
| `class_session` | `(environment_id, session_date, start_time, end_time)` | B-Tree | Detección de conflictos de ambiente |
| `class_session` | `schedule_id` | B-Tree | Carga de sesiones por horario |
| `schedule` | `ix_schedule_active_created_at` sobre `(created_at) WHERE is_active = true` | B-Tree parcial (R2) | Listado paginado de horarios activos ordenado por fecha de creación, sin Sort ([ADR-027](../../../05-architecture/decisions/records/ADR-027-scheduling-r2-performance.md)) |
| `class_session` | `ix_class_session_active_schedule_date` sobre `(schedule_id, session_date) WHERE is_active = true` | B-Tree parcial (R2) | Sesiones activas de un horario ordenadas por fecha, sin Sort; su beneficio aparece desde unos cien registros por horario ([informe QA R2](../../../11-quality/qa-report-r2-scheduling-service.md)) |

> **Nota (UNIQUE parcial sobre `schedule`):** un `UNIQUE (ficha_id, period)` total impediría crear un nuevo DRAFT cuando ya existe un PUBLISHED para la misma ficha+período, lo que contradice la invariante de inmutabilidad (los cambios deben generar un nuevo `schedule` en DRAFT). El índice parcial con `WHERE status = 'PUBLISHED'` garantiza un único horario publicado por ficha/período a la vez que permite coexistir borradores y versiones archivadas.

## Prevención de doble-asignación (exclusion constraints)

Como red de seguridad a nivel de BD, **además** del `conflict-validator-worker`, se aplican `EXCLUDE USING gist` sobre `class_session` para impedir el doble-booking de instructor y de ambiente cuando los rangos horarios se solapan (solo sobre sesiones `ACTIVE`):

```sql
-- requiere extensión btree_gist
ALTER TABLE class_session ADD CONSTRAINT ex_session_instructor
  EXCLUDE USING gist (instructor_id WITH =,
    tsrange((session_date + start_time),(session_date + end_time)) WITH &&)
  WHERE (status = 'ACTIVE');
ALTER TABLE class_session ADD CONSTRAINT ex_session_environment
  EXCLUDE USING gist (environment_id WITH =,
    tsrange((session_date + start_time),(session_date + end_time)) WITH &&)
  WHERE (status = 'ACTIVE');
```

## Remediación de congruencia — R3 (2026-08-06)

El contrato promete **soft delete** (`DELETE` lógico) en `schedule`, `class_session` y
`time_slot`, pero las tablas no tenían columnas que lo respalden. Se agregan vía changeset
nuevo `remediation-scheduling-960` (no se modifica ningún changeset corrido):
`is_active BOOLEAN NOT NULL DEFAULT true`, `deleted_at TIMESTAMPTZ`, `deleted_by UUID` en las
tres tablas. `scheduling_conflict` no se toca (es de solo lectura, sin `DELETE` en el contrato).
