# Modelo de datos — monitoring-service

> Estado: 🟢 Estable | Última actualización: 2026-10-20
> Naming: entidades y atributos en inglés (HALT-DB-NAMING)
> Fuente de dominio: análisis M9 (Seguimiento y Analítica)

## Convenciones de modelado (transversales)

> **Estándar autoritativo:** [06-data/modeling-conventions.md](../../../06-data/modeling-conventions.md) (ratificado en ADR-004). Resumen aplicable:

- **Tres conceptos de estado (no confundir):** (1) *ciclo de vida del registro* (técnico) → `is_active` + soft delete (`deleted_at`); (2) *estado de negocio* (parametrizable) → FK `status_id` → catálogo `status`; (3) *enum técnico cerrado* (CC/CE, EMAIL/IN_APP…) → `VARCHAR` + `CHECK (... IN (...))`. **No se usa el tipo `ENUM` nativo de Postgres** (su `ALTER TYPE` bloquea migraciones independientes por servicio).
- **Estados de negocio parametrizables:** el servicio implementa `status_category` + `status` (+ `status_transition` si aplica) en su propia BD; los agregados con máquina de estados referencian `status_id`. Solo migran estados de **negocio**; los enums técnicos cerrados (`*_type`, `channel`…) permanecen como `VARCHAR + CHECK`. Los catálogos `kpi_status` y `risk_level` son una instancia de este patrón (categorías `KPI_STATUS` / `RISK_LEVEL`).
- **Auditoría (tablas transaccionales):** `created_at`/`created_by`, `updated_at`/`updated_by`, `deleted_at`/`deleted_by` (soft delete), `is_active` y `row_version`. Acciones del sistema usan `SYSTEM_ACTOR_ID = 00000000-0000-0000-0000-000000000000`. Catálogos: `created_*`/`updated_*` + `is_active` (sin soft delete). Append-only: solo el timestamp de inserción.
- **Acciones referenciales:** cada FK declara `ON UPDATE`/`ON DELETE`. Por defecto: catálogo/padre → `RESTRICT`; hijo de agregado (composición) → `CASCADE`; FK opcional → `SET NULL`.
- **Nomenclatura de constraints:** `pk_<tabla>`, `uq_<tabla>_<cols>`, `fk_<tabla>_<ref>`, `ck_<tabla>_<regla>`, `ix_<tabla>_<cols>`.

## Entidades propias

---

### Catálogos configurables

Los catálogos de tipos de alerta y niveles de riesgo son configurables en runtime por el
equipo pedagógico, sin necesidad de deploy. Esto permite ajustar umbrales y categorías
según normativa SENA vigente.

#### `kpi_type`

Catálogo de tipos de KPI medibles en el sistema. Configurable en runtime.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| id | UUID | No | PK |
| code | VARCHAR(50) | No | UNIQUE; ej: ATTENDANCE, CURRICULUM_PROGRESS, DROPOUT_RISK, PRODUCTIVE_STAGE_PROGRESS |
| name | VARCHAR(120) | No | Nombre descriptivo |
| description | TEXT | Sí | Qué mide este KPI |
| unit | VARCHAR(20) | No | PERCENTAGE, COUNT, HOURS, DAYS |
| is_active | BOOLEAN | No | DEFAULT true |

Seed con 4 KPI types: ATTENDANCE (%), CURRICULUM_PROGRESS (%), DROPOUT_RISK (COUNT), PRODUCTIVE_STAGE_PROGRESS (%).

---

#### `alert_type`

Catálogo de tipos de alerta configurables.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `code` | VARCHAR(50) | No | UNIQUE; ej: `LOW_ATTENDANCE`, `HIGH_DROPOUT_RISK`, `CURRICULUM_DELAY` |
| `name` | VARCHAR(120) | No | Nombre para visualización |
| `description` | TEXT | Sí | Cuándo se genera esta alerta |
| `default_threshold` | DECIMAL(10,4) | Sí | Valor umbral por defecto (ej: 0.80 = 80% asistencia mínima) |
| `threshold_unit` | VARCHAR(20) | Sí | `PERCENTAGE`, `COUNT`, `DAYS`, `HOURS` |
| `affects_ficha_status` | BOOLEAN | No | Si true, puede cambiar el overall_status de la ficha |
| `is_active` | BOOLEAN | No | DEFAULT true |

**Alertas pre-configuradas (Circular 1-2014 SENA, Acuerdo 00003/2012):**

| Código | Umbral | Descripción |
|--------|--------|-------------|
| `LOW_ATTENDANCE` | 80% | Asistencia por debajo del mínimo reglamentario |
| `HIGH_DROPOUT_RISK` | 3 aprendices | Aprendices con riesgo de deserción en la ficha |
| `CURRICULUM_DELAY` | 70% avance | Ficha con avance curricular por debajo del esperado |
| `LEARNER_ABSENCE_CRITICAL` | 3 sesiones | Aprendiz con más de 3 sesiones sin asistir |
| `PRODUCTIVE_STAGE_DELAY` | 30 días | Etapa productiva sin registro de visita en >30 días |
| `INSTRUCTOR_OVERLOAD` | 40 h/sem | Instructor con más horas asignadas de su límite |

---

#### `risk_level`

Niveles de severidad de riesgo. Ordenados para mostrar alertas por criticidad.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `code` | VARCHAR(20) | No | UNIQUE; INFO / LOW / MEDIUM / HIGH / CRITICAL |
| `label` | VARCHAR(60) | No | Etiqueta de presentación (ej: "Riesgo Crítico") |
| `color_hex` | VARCHAR(7) | No | Color para UI (ej: `#E53E3E`) |
| `priority_order` | SMALLINT | No | Orden de presentación (1 = mayor urgencia) |

**Valores fijos:** INFO (5) → LOW (4) → MEDIUM (3) → HIGH (2) → CRITICAL (1)

---

### `ficha_tracking`

Estado de seguimiento consolidado de una ficha activa. Una ficha tiene exactamente un
registro de seguimiento mientras está en estado EXECUTION.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `ficha_id` | UUID | No | UNIQUE; Referencia externa → academic-management-service |
| `assigned_instructor_id` | UUID | No | Instructor responsable del seguimiento (referencia externa → actors-service) |
| `overall_status_id` | UUID | No | FK → kpi_status. Estado calculado con base en KPIs activos |
| `active_alert_count` | INT | No | DEFAULT 0; contador desnormalizado de alertas sin resolver |
| `last_tracking_date` | DATE | Sí | Última fecha con sesión de seguimiento registrada |
| `next_tracking_date` | DATE | Sí | Próxima sesión de seguimiento planificada |
| `created_at` | TIMESTAMPTZ | No | |
| `updated_at` | TIMESTAMPTZ | No | |

**overall_status_id**: antes era un ENUM inline (`ON_TRACK`/`AT_RISK`/`CRITICAL`) que duplicaba los códigos del catálogo `kpi_status`. Se unifica reutilizando ese catálogo vía FK → `kpi_status`, eliminando la doble fuente de verdad del estado.

**active_alert_count** es un contador desnormalizado mantenido por triggers al insertar/resolver alertas. Proporciona acceso O(1) al conteo de alertas activas para el dashboard, evitando un COUNT(*) costoso. Trade-off: requiere trigger de consistencia (ver decisions.md).

---

### `kpi_status`

Catálogo de estados de KPI.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `code` | VARCHAR(20) | No | UNIQUE; ON_TRACK / AT_RISK / CRITICAL |
| `description` | TEXT | Sí | Descripción del estado |
| `risk_level_id` | UUID | No | FK → risk_level |

---

### `kpi_tracking`

Medición puntual de un KPI para una ficha. Cada medición crea un nuevo registro;
el historial se mantiene para análisis de tendencia.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `ficha_tracking_id` | UUID | No | FK → ficha_tracking |
| `kpi_type_id` | UUID | No | FK → kpi_type |
| `current_value` | DECIMAL(10,4) | No | Valor medido |
| `threshold_value` | DECIMAL(10,4) | No | Umbral de la alerta relacionada |
| `kpi_status_id` | UUID | No | FK → kpi_status |
| `period_start` | DATE | No | Inicio del período que cubre esta medición |
| `period_end` | DATE | No | Fin del período |
| `measured_at` | TIMESTAMPTZ | No | Timestamp de la medición |

**Particionamiento/retención (decisión explícita)**: `kpi_tracking` es una serie temporal y se
particiona por `measured_at` mediante particionado RANGE mensual nativo de PostgreSQL. Esto
acota tamaño de índices, permite poda de particiones en consultas de tendencia y facilita el
archivado/purga por período. (Reemplaza la nota previa que dejaba TimescaleDB/particionado como
opción condicionada al volumen: se adopta como decisión de modelado.)

---

### `tracking_session`

Sesión de seguimiento periódico registrada por instructor o coordinador.
Normativa SENA: seguimiento mínimo mensual para fichas en Ejecución (Acuerdo 00003/2012).

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `ficha_tracking_id` | UUID | No | FK → ficha_tracking |
| `instructor_id` | UUID | No | Referencia externa → actors-service |
| `session_date` | DATE | No | |
| `session_type` | VARCHAR(20) | No | CHECK (`session_type` IN (`ACADEMIC`, `WELLNESS`, `PROJECT`, `PRODUCTIVE_STAGE`)). Tipo de seguimiento |
| `attendance_count` | INT | Sí | Número de aprendices presentes |
| `total_learners` | INT | Sí | Total de aprendices en la ficha |
| `attendance_percentage` | DECIMAL(5,2) GENERATED ALWAYS AS (CASE WHEN total_learners > 0 THEN ROUND(CAST(attendance_count AS DECIMAL(10,4)) / total_learners * 100, 2) ELSE NULL END) STORED | Sí | Calculado: attendance_count / total_learners |
| `curriculum_progress_percentage` | DECIMAL(5,2) | Sí | % de avance curricular al momento del registro |
| `observations` | TEXT | Sí | Observaciones del instructor |
| `requires_follow_up` | BOOLEAN | No | DEFAULT false; si true, se debe generar alerta |
| `created_at` | TIMESTAMPTZ | No | |

Tabla append-only: conserva únicamente su timestamp de inserción (`created_at`).

**attendance_percentage** es una columna generada (GENERATED ALWAYS AS ... STORED) — PostgreSQL la mantiene automáticamente. No se puede insertar/actualizar manualmente.

---

### `generated_alert`

Alerta generada cuando un KPI supera un umbral o el sistema detecta una condición crítica.
Las alertas son consumidas por el `alert-worker` al procesar eventos del bus de mensajes.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `ficha_tracking_id` | UUID | No | FK → ficha_tracking |
| `alert_type_id` | UUID | No | FK → alert_type |
| `risk_level_id` | UUID | No | FK → risk_level |
| `source_event_id` | UUID | No | event_id del evento que disparó la alerta |
| `affected_learner_id` | UUID | Sí | Aprendiz afectado (referencia externa → actors-service) |
| `affected_instructor_id` | UUID | Sí | Instructor afectado (referencia externa → actors-service) |
| `triggered_value` | DECIMAL(10,4) | Sí | Valor que superó el umbral |
| `threshold_value` | DECIMAL(10,4) | Sí | Umbral configurado al momento de la alerta |
| `description` | TEXT | No | Descripción legible de la alerta |
| `is_resolved` | BOOLEAN | No | DEFAULT false |
| `resolved_by` | UUID | Sí | Referencia externa → iam-service |
| `resolution_notes` | TEXT | Sí | |
| `generated_at` | TIMESTAMPTZ | No | |
| `resolved_at` | TIMESTAMPTZ | Sí | |
| `updated_at` | TIMESTAMPTZ | No | |

**Entidad afectada (arco exclusivo)**: antes se modelaba con una FK polimórfica
(`affected_entity_type` / `affected_entity_id`) que impide integridad referencial. Se sustituye por
un arco exclusivo con FKs lógicas a actors-service (`affected_learner_id`, `affected_instructor_id`).
Arco exclusivo: como máximo una poblada; valida la aplicación (`CHECK (affected_learner_id IS NULL OR affected_instructor_id IS NULL)`). Son referencias externas (otro servicio), por lo que la FK no se aplica en BD.

---

### `outbox`

Tabla técnica para publicar de forma confiable los eventos producidos por Monitoring. Se inserta
en la misma transacción que modifica `generated_alert`; el relay publica las filas pendientes y
marca `published_at` únicamente después del `ack` del broker.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK. |
| `event_id` | UUID | No | Identificador canónico del evento; único para deduplicación. |
| `event_type` | VARCHAR(150) | No | `monitoring.alert.triggered` u otro evento de Monitoring. |
| `payload` | JSONB | No | Envelope completo del evento de integración. |
| `created_at` | TIMESTAMPTZ | No | Momento de inserción transaccional. |
| `published_at` | TIMESTAMPTZ | Sí | Null mientras está pendiente. |

Índice mínimo: (`published_at`, `created_at`) con filtro `published_at IS NULL` para el relay.

---

### `improvement_plan`

Plan de mejoramiento a nivel de ficha. Generado por coordinador o instructor a partir de
una alerta activa. Diferente del `actor_improvement_plan` en actors-service, que es por actor individual.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `ficha_tracking_id` | UUID | No | FK → ficha_tracking |
| `generated_alert_id` | UUID | Sí | FK → generated_alert (null si plan preventivo) |
| `learner_id` | UUID | Sí | Referencia externa → actors-service (null si aplica a toda la ficha) |
| `instructor_id` | UUID | Sí | Referencia externa |
| `title` | VARCHAR(200) | No | Título del plan |
| `description` | TEXT | No | Descripción del plan de mejoramiento |
| `specific_actions` | TEXT | No | Acciones concretas con responsables y fechas; durante R6 conserva el contrato HTTP textual |
| `due_date` | DATE | No | |
| `status` | VARCHAR(20) | No | CHECK (`status` IN (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`)) |
| `completion_notes` | TEXT | Sí | Notas al cerrar el plan |
| `created_by` | UUID | No | Referencia externa → iam-service |
| `created_at` | TIMESTAMPTZ | No | |
| `updated_at` | TIMESTAMPTZ | No | |

---

> **Ownership actualizado (ADR-005):** `sent_notification` ya no pertenece a este modelo. La entidad y su persistencia viven en [`notification-service`](../10-notification-service/data-model.md).

### Evolución R6 de `specific_actions`

La entidad atraviesa tres estados de esquema. El estado documentado como final no implica que CONTRACT forme parte del arranque automático del servicio.

| Fase | Definición efectiva | Lectura/escritura |
|---|---|---|
| Antes de EXPAND | `specific_actions TEXT NOT NULL` | El servicio lee y escribe TEXT. |
| EXPAND/BACKFILL | `specific_actions TEXT NOT NULL` y `specific_actions_v2 JSONB NULL` | Coexisten ambas columnas; el adaptador de persistencia detecta `specific_actions_v2`, conserva el contrato HTTP `string` y sincroniza las escrituras nuevas. |
| Después de CONTRACT | `specific_actions JSONB NOT NULL` | El adaptador detecta que la columna principal es JSONB; el HTTP sigue recibiendo y devolviendo `string`. |

La representación JSONB real de R6 es:

```json
{
  "version": 1,
  "actions": [
    { "text": "texto original exacto" }
  ]
}
```

`version` identifica la forma del documento y `actions` es un arreglo preparado para evolución, pero la implementación actual solo genera y revierte de forma segura un único elemento `actions[0].text`. BACKFILL conserva el texto original, incluidos Unicode, saltos de línea y caracteres especiales, mediante `jsonb_build_object`/`jsonb_build_array`; no separa el texto en múltiples acciones.

EXPAND agrega `specific_actions_v2` nullable y no cambia la nulabilidad de la columna original. BACKFILL solo actualiza filas donde `specific_actions_v2 IS NULL`. Antes de CONTRACT, la precondición de Liquibase exige que todas las filas tengan el documento esperado y que `actions[0].text` sea equivalente a `specific_actions`; CONTRACT elimina la columna TEXT, renombra la v2 y establece `NOT NULL`. La operación se mantiene en un changelog separado y requiere autorización operativa.

El rollback de BACKFILL reconstruye `specific_actions` desde `actions[0].text`; el rollback de EXPAND elimina la columna v2. El rollback de CONTRACT recrea TEXT en `specific_actions`, conserva la JSONB renombrada como `specific_actions_v2` y debe dejarla nullable. No es seguro asumir pérdida cero si el documento contiene múltiples acciones, otra versión o una estructura futura. Las evidencias que muestran `specific_actions_v2 NOT NULL` después del rollback requieren reconciliación. Véase [ADR-013](../../../05-architecture/decisions/records/ADR-013-monitoring-r6-text-jsonb-migration.md).

---

## Referencias externas

| Campo | Referencia lógica | Servicio propietario |
|-------|-------------------|----------------------|
| `ficha_id` en ficha_tracking | `enrollment_ficha.id` | `academic-management-service` |
| `assigned_instructor_id` | `instructor.id` | `actors-service` |
| `instructor_id` (tracking_session) | `instructor.id` | `actors-service` |
| `affected_learner_id` (generated_alert) | `learner.id` | `actors-service` |
| `affected_instructor_id` (generated_alert) | `instructor.id` | `actors-service` |
| `learner_id` (improvement_plan) | `learner.id` | `actors-service` |
| `resolved_by` | `user.id` | `iam-service` |
| `created_by` | `user.id` | `iam-service` |

---

## Índices relevantes

| Tabla | Campos indexados | Tipo | Motivo |
|-------|-----------------|------|--------|
| `ficha_tracking` | `ficha_id` | UNIQUE | Un tracking por ficha |
| `ficha_tracking` | `overall_status_id` | B-Tree | Filtrar fichas AT_RISK / CRITICAL |
| `ficha_tracking` | `assigned_instructor_id` | B-Tree | Fichas de un instructor |
| `kpi_type` | `code` | UNIQUE | Lookup por código de tipo de KPI |
| `kpi_tracking` | `(kpi_type_id, ficha_tracking_id, measured_at)` | B-Tree | Tendencias por tipo de KPI |
| `tracking_session` | `(ficha_tracking_id, session_date)` | B-Tree | Sesiones cronológicas por ficha |
| `generated_alert` | `(ficha_tracking_id, is_resolved)` | B-Tree | Alertas activas por ficha |
| `generated_alert` | `(alert_type_id, risk_level_id, generated_at)` | B-Tree | Reportes por tipo y severidad |
| `outbox` | (`published_at`, `created_at`) WHERE `published_at IS NULL` | B-Tree | Eventos pendientes para el relay |

---

## Seeds / Pre-cargados

### `kpi_type` (4 registros)

| code | name | unit |
|------|------|------|
| `ATTENDANCE` | Asistencia | PERCENTAGE |
| `CURRICULUM_PROGRESS` | Avance curricular | PERCENTAGE |
| `DROPOUT_RISK` | Riesgo de deserción | COUNT |
| `PRODUCTIVE_STAGE_PROGRESS` | Avance etapa productiva | PERCENTAGE |

## Remediación de congruencia — R3 (2026-08-06)

- **`remediation-monitoring-960`:** 5 columnas estaban como **ENUM nativo** (viola ADR-004) →
  convertidas a `VARCHAR + CHECK` conservando los valores: `alert_type.threshold_unit`,
  `tracking_session.session_type` e `improvement_plan.status`. Las columnas históricas de
  `sent_notification` se excluyen de Monitoring desde ADR-005 y pasan a `notification_db`.
- **`remediation-monitoring-961`:** `kpi_tracking` se implementa como tabla **particionada por
  RANGE mensual de `measured_at`** (antes se declaraba particionada en docs sin estarlo). La PK
  pasa a incluir la clave de partición.
