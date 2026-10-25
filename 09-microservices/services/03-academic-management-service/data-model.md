# Modelo de datos — academic-management-service

> Estado: 🟢 Estable | Última actualización: 2026-06-20
> Naming: entidades y atributos en inglés (HALT-DB-NAMING)

## Convenciones de modelado (transversales)

> **Estándar autoritativo:** [06-data/modeling-conventions.md](../../../06-data/modeling-conventions.md) (ratificado en ADR-004). Resumen aplicable:

- **Tres conceptos de estado (no confundir):** (1) *ciclo de vida del registro* (técnico) → `is_active` + soft delete (`deleted_at`); (2) *estado de negocio* (parametrizable) → FK `status_id` → catálogo `status`; (3) *enum técnico cerrado* (CC/CE, EMAIL/IN_APP…) → `VARCHAR` + `CHECK (... IN (...))`. **No se usa el tipo `ENUM` nativo de Postgres** (su `ALTER TYPE` bloquea migraciones independientes por servicio).
- **Estados de negocio parametrizables:** el servicio implementa `status_category` + `status` (+ `status_transition` si aplica) en su propia BD; los agregados con máquina de estados referencian `status_id`. Solo migran estados de **negocio**; los enums técnicos cerrados (`*_type`, `channel`…) permanecen como `VARCHAR + CHECK`.
- **Auditoría (tablas transaccionales):** `created_at`/`created_by`, `updated_at`/`updated_by`, `deleted_at`/`deleted_by` (soft delete), `is_active` y `row_version`. Acciones del sistema usan `SYSTEM_ACTOR_ID = 00000000-0000-0000-0000-000000000000`. Catálogos: `created_*`/`updated_*` + `is_active` (sin soft delete). Append-only: solo el timestamp de inserción.
- **Acciones referenciales:** cada FK declara `ON UPDATE`/`ON DELETE`. Por defecto: catálogo/padre → `RESTRICT`; hijo de agregado (composición) → `CASCADE`; FK opcional → `SET NULL`.
- **Nomenclatura de constraints:** `pk_<tabla>`, `uq_<tabla>_<cols>`, `fk_<tabla>_<ref>`, `ck_<tabla>_<regla>`, `ix_<tabla>_<cols>`.

## Entidades propias

### Jerarquía curricular (M5)

`tech_line` → `tech_network` → `knowledge_network` → `training_program`
`training_program` ↔ `competency` (1:M directa; un programa tiene múltiples competencias)
`competency` 1──* `learning_outcome`

| Entidad | PK | Campos clave |
|---------|-----|-------------|
| `tech_line` | UUID | `name`, `code`, `is_active` |
| `tech_network` | UUID | `name`, `tech_line_id`, `is_active` |
| `knowledge_network` | UUID | `name`, `tech_network_id`, `is_active` |
| `training_program` | UUID | `name`, `program_code`, `training_level`, `total_hours`, `knowledge_network_id` |
| `competency` | UUID | `name`, `sena_code`, `hours`, `program_id` |
| `learning_outcome` | UUID | `description`, `code`, `competency_id` |

### `tech_line` — detalle

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `name` | VARCHAR(150) | No | |
| `code` | VARCHAR(20) | No | UNIQUE |
| `is_active` | BOOLEAN | No | DEFAULT true |
| `created_at` | TIMESTAMPTZ | No | |

### `tech_network` — detalle

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `tech_line_id` | UUID | No | FK → tech_line |
| `name` | VARCHAR(150) | No | |
| `code` | VARCHAR(20) | No | |
| `is_active` | BOOLEAN | No | |
| `created_at` | TIMESTAMPTZ | No | |

UNIQUE (`tech_line_id`, `code`).

### `knowledge_network` — detalle

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `tech_network_id` | UUID | No | FK → tech_network |
| `name` | VARCHAR(150) | No | |
| `code` | VARCHAR(20) | No | |
| `is_active` | BOOLEAN | No | |
| `created_at` | TIMESTAMPTZ | No | |

UNIQUE (`tech_network_id`, `code`).

### `training_program` — detalle

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `knowledge_network_id` | UUID | No | FK → knowledge_network |
| `program_code` | VARCHAR(20) | No | Código SENA del programa |
| `name` | VARCHAR(200) | No | |
| `training_level` | VARCHAR(20) | No | CHECK: `training_level IN ('AUXILIARY','OPERATOR','TECHNICIAN','TECHNOLOGIST')`. Valores permitidos por el SENA. |
| `total_hours` | INT | No | Duración total en horas. CHECK: `total_hours >= 0`. |
| `version` | INT | No | Versión del programa |
| `is_active` | BOOLEAN | No | |
| `created_at` | TIMESTAMPTZ | No | |
| `updated_at` | TIMESTAMPTZ | No | |

### `competency` — detalle

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `program_id` | UUID | No | FK → training_program |
| `name` | VARCHAR(200) | No | |
| `sena_code` | VARCHAR(20) | No | |
| `hours` | INT | No | CHECK: `hours >= 0`. |
| `is_active` | BOOLEAN | No | |
| `created_at` | TIMESTAMPTZ | No | |

UNIQUE (`program_id`, `sena_code`).

### `learning_outcome` — detalle

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `competency_id` | UUID | No | FK → competency |
| `code` | VARCHAR(20) | No | |
| `description` | TEXT | No | |
| `is_active` | BOOLEAN | No | |
| `created_at` | TIMESTAMPTZ | No | |

UNIQUE (`competency_id`, `code`).

### Versionado de programa (dimensión temporal)

**Problema:** `training_program.version` representa la definición curricular vigente, pero las
definiciones evolucionan en el tiempo (cambios de competencias, horas, resultados de aprendizaje).
Una ficha (`enrollment_ficha`) abierta bajo una versión dada debe regirse por esa versión durante
toda su vida, aun cuando el programa se actualice posteriormente. Sin modelar esta dimensión
temporal, una actualización de programa alteraría retroactivamente la definición de fichas ya en
ejecución, rompiendo la integridad académica.

**Solución:** la ficha congela (snapshot) la versión del programa al momento de abrirse mediante la
columna `enrollment_ficha.program_version INT NOT NULL`, copiada de `training_program.version`.

> La ficha congela la versión del programa vigente al abrirse; cambios posteriores de versión no la
> afectan. Para historial de versiones de programa se recomienda tabla
> `training_program_version (program_id, version, effective_from, ...)` si el negocio requiere
> consultar definiciones históricas.

### Fichas y oferta (M6)

### `enrollment_ficha`

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `ficha_number` | VARCHAR(20) | No | Número de ficha SENA; único |
| `program_id` | UUID | No | FK → training_program |
| `program_version` | INT | No | Snapshot de `training_program.version` al abrir la ficha. Congela la versión del programa vigente; cambios posteriores no la afectan. |
| `training_center_id` | UUID | No | Referencia externa → reference-data-service |
| `status` | VARCHAR(30) | No | CHECK: `status IN ('INDUCTION','EXECUTION','PRODUCTIVE_STAGE','COMPLETED','CANCELLED')` |
| `start_date` | DATE | No | |
| `expected_end_date` | DATE | Sí | |
| `actual_end_date` | DATE | Sí | Fecha real de cierre de la ficha |
| `training_shift` | VARCHAR(20) | No | CHECK: `training_shift IN ('DAY','NIGHT','MIXED')`. Valores locales — el catálogo de referencia está en reference-data-service. Se usan valores locales para integridad sin dependencia síncrona. |
| `training_modality` | VARCHAR(20) | No | CHECK: `training_modality IN ('IN_PERSON','VIRTUAL','HYBRID')`. Valores locales — el catálogo de referencia está en reference-data-service. Se usan valores locales para integridad sin dependencia síncrona. |
| `max_capacity` | INT | No | Número máximo de aprendices |
| `created_at` | TIMESTAMPTZ | No | |
| `updated_at` | TIMESTAMPTZ | No | |

#### Máquina de estados de `status`

Estado inicial: `INDUCTION`. Transiciones válidas:

- `INDUCTION` → `EXECUTION` | `CANCELLED`
- `EXECUTION` → `PRODUCTIVE_STAGE` | `CANCELLED`
- `PRODUCTIVE_STAGE` → `COMPLETED` | `CANCELLED`
- `COMPLETED` → (terminal)
- `CANCELLED` → (terminal)

`COMPLETED` y `CANCELLED` son estados terminales; no admiten transiciones de salida.

## Referencias externas

| Campo | Referencia lógica | Servicio propietario |
|-------|-------------------|----------------------|
| `training_center_id` | `training_center.id` | `reference-data-service` |

## Tablas de integración resiliente

### `outbox`

La operación de negocio y su evento se confirman en la misma transacción. El relay publica posteriormente y conserva los reintentos.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK técnica |
| `event_id` | UUID | No | Identificador único del evento |
| `event_type` | VARCHAR(120) | No | Tipo canónico |
| `topic` | VARCHAR(120) | No | Exchange de destino |
| `routing_key` | VARCHAR(120) | No | Clave de enrutamiento |
| `payload` | JSONB | No | Envelope serializado |
| `created_at` | TIMESTAMPTZ | No | Momento de creación |
| `next_attempt_at` | TIMESTAMPTZ | No | Próximo intento |
| `retry_count` | INT | No | Intentos fallidos, mayor o igual a cero |
| `published_at` | TIMESTAMPTZ | Sí | Confirmación positiva del broker |
| `dead_lettered_at` | TIMESTAMPTZ | Sí | Envío agotado a DLQ |
| `last_error` | TEXT | Sí | Último error observado |

La unicidad de `event_id` evita dos filas para el mismo evento. El índice parcial `ix_academic_outbox_pending` cubre eventos no publicados ni enviados a DLQ.

### `processed_event`

Registra la recepción durable del consumidor y actúa como frontera de idempotencia.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK técnica |
| `event_id` | UUID | No | ID conservado desde RabbitMQ |
| `event_type` | VARCHAR(120) | No | Tipo recibido |
| `consumer_name` | VARCHAR(120) | No | Consumidor que registró el evento |
| `processed_at` | TIMESTAMPTZ | No | Momento de primera recepción |

La restricción única `(consumer_name, event_id)` hace que una segunda entrega no cree otro recibo. El índice `ix_academic_processed_event_processed_at` soporta consultas operativas y futura retención.

## Índices relevantes

| Tabla | Campos | Tipo | Motivo |
|-------|--------|------|--------|
| `training_program` | `program_code` | UNIQUE | Búsqueda por código de programa |
| `enrollment_ficha` | `ficha_number` | UNIQUE | Referencia desde scheduling-service |
| `enrollment_ficha` | `status` | B-Tree | Filtro por estado activo (frecuente) |
| `enrollment_ficha` | `training_center_id` | B-Tree | Fichas activas por centro |
| `enrollment_ficha` | `(training_center_id, status)` | B-Tree | Consultas de dashboard por centro y estado |
| `outbox` | `(next_attempt_at, created_at)` pendiente | B-Tree parcial | Relay de eventos publicables |
| `processed_event` | `processed_at` | B-Tree | Operación y retención de recibos |

## Remediación de congruencia — R3 (2026-08-06)

El CHECK de `enrollment_ficha.status` ya estaba documentado pero **faltaba en el DDL real**
(la columna aceptaba cualquier string). Se implementa vía changeset nuevo
`remediation-academic-960` (no se modifica ningún changeset corrido):
`CHECK (status IN ('INDUCTION','EXECUTION','PRODUCTIVE_STAGE','COMPLETED','CANCELLED'))`.
Además, el contrato se ajustó en R1 a `max_capacity ≥ 1` (calzar con el `CHECK max_capacity > 0` real).
