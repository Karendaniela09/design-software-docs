# Diccionario de datos

> Estado: 🟡 En progreso | Última actualización: 2026-10-26
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Datos

Índice transversal del modelo de datos. **La fuente de verdad de cada tabla (columnas, tipos, PII, retención, índices, seeds) es el `data-model.md` de cada servicio.** Este documento no duplica esas definiciones: las referencia y fija las reglas comunes.

## Convenciones comunes (obligatorias)

Definidas en [modeling-conventions.md](./modeling-conventions.md):
- **PK** `UUID` en todas las tablas · **Timestamps** `TIMESTAMPTZ` (UTC).
- **Columnas de auditoría** estándar según tipo de tabla (transaccional / catálogo / append-only).
- **Estados de negocio** parametrizables (`status_category` / `status` / `status_transition`); enums técnicos cerrados como `VARCHAR + CHECK`.
- **Nomenclatura** de constraints: `pk_`, `uq_`, `fk_`, `ck_`, `ix_`.

## Actualización R1 de Academic Management — 2026-10-24

| Objeto | Tipo / columnas principales | Changeset | Propósito y fuente canónica |
|---|---|---|---|
| `academic_management.outbox` | PK UUID; `event_id` UUID único; `payload` JSONB; `next_attempt_at`, `published_at`, `dead_lettered_at` TIMESTAMPTZ; `retry_count` INT | `01_ddl/03_tables/008_create_table_outbox.sql` (ya en `develop`) | Outbox transaccional: el evento se confirma en la misma transacción que el cambio de negocio; [modelo del servicio](../09-microservices/services/03-academic-management-service/data-model.md) |
| `academic_management.processed_event` | PK UUID; `event_id` UUID; `consumer_name` VARCHAR(120); `processed_at` TIMESTAMPTZ; único `(consumer_name, event_id)` | `01_ddl/03_tables/009_create_table_processed_event.sql` ([academic-management-db#134](https://github.com/code-sena/design-software-academic-management-db/pull/134), abierto) | Recibo durable del consumidor e idempotencia; mismo modelo canónico |

Estado: `outbox` ya existe en `develop`; `processed_event` está en el PR citado de `academic-management-db`, pendiente de revisión y merge. El índice global no duplica las definiciones: el modelo del servicio contiene los campos, los índices y los límites de retención. Decisión asociada: [ADR-025](../05-architecture/decisions/records/ADR-025-academic-resilient-messaging.md) (PROPOSED).

## Mapa de servicios → schema → modelo

| Servicio | Schema(s) previstos | Repo | Modelo de datos |
|----------|--------------------|------|-----------------|
| iam-service | `identity`, `identity_audit`, `rbac`, `rbac_catalog`, `session` | `design-software-iam-db` | [data-model](../09-microservices/services/01-iam-service/data-model.md) |
| reference-data-service | `institutional_structure`, `parameterization` | `design-software-reference-data-db` | [data-model](../09-microservices/services/02-reference-data-service/data-model.md) |
| academic-management-service | `academic_management` | `design-software-academic-management-db` | [data-model](../09-microservices/services/03-academic-management-service/data-model.md) |
| training-environment-service | `training_environment` | `design-software-training-environment-db` | [data-model](../09-microservices/services/04-training-environment-service/data-model.md) |
| scheduling-service | `scheduling` | `design-software-scheduling-db` | [data-model](../09-microservices/services/05-scheduling-service/data-model.md) |
| actors-service | `actors_parameterization` | `design-software-actors-db` | [data-model](../09-microservices/services/06-actors-service/data-model.md) |
| document-service | `document` | `design-software-document-db` | [data-model](../09-microservices/services/07-document-service/data-model.md) |
| monitoring-service | `monitoring` | `design-software-monitoring-db` | [data-model](../09-microservices/services/08-monitoring-service/data-model.md) |
| audit-service | `audit` | `design-software-audit-db` | [data-model](../09-microservices/services/09-audit-service/data-model.md) |
| notification-service | `notification` | `design-software-notification-db` | [data-model](../09-microservices/services/10-notification-service/data-model.md) |

> **Regla de aislamiento:** cada servicio debe crear y usar su propio schema; ninguna tabla debe quedar en `public`. Verificar este punto en la revisión de cada `data-model.md` antes de marcarlo 🟢.

## Actualización HU-ACAD-11 de Academic Management — 2026-10-24

| Objeto | Tipo / columnas principales | Changeset | Propósito y fuente canónica |
|---|---|---|---|
| `academic_management.enrollment_ficha`: `cancellation_notes`, `cancellation_at`, `cancellation_by` | VARCHAR(500) NULL; TIMESTAMPTZ NULL; UUID NULL | `hu-acad-11-cancellation-notes-970` | Justificación interna de la cancelación de una ficha y su auditoría (momento y actor); [modelo del servicio](../09-microservices/services/03-academic-management-service/data-model.md) |
| `academic_management.enrollment_ficha`: constraints de cancelación | `ck_enrollment_ficha_cancellation_notes_length` (nota nula o de 10 a 500 caracteres tras `btrim`); `ck_enrollment_ficha_cancellation_audit` (las tres columnas nulas o las tres pobladas) | `hu-acad-11-cancellation-notes-970` | Coherencia de la cancelación aplicada en la base de datos; mismo modelo canónico |

Estado: changeset publicado en `design-software-academic-management-db` [PR #135](https://github.com/code-sena/design-software-academic-management-db/pull/135), pendiente de revisión y merge a develop. El índice global no duplica las definiciones: el modelo del servicio contiene el detalle, el SQL y el rollback.

## Actualización HU-ACT-033 de Actors — asignación instructor → ficha — 2026-11-03

| Objeto | Tipo / columnas principales | Changeset | Propósito y fuente canónica |
|---|---|---|---|
| `actors_instructors.instructor_ficha_assignment` | `instructor_id`, `ficha_id` (UUID sin FK entre BD), `competency_id` (UUID opcional sin FK) y auditoría ADR-004 con borrado lógico | `hu-act-033-instructor-ficha-assignment-table-001` (03_tables) | Asignación administrativa del instructor a una ficha que gestiona el coordinador; [modelo del servicio](../09-microservices/services/06-actors-service/data-model.md) |
| `actors_instructors.instructor_ficha_assignment`: constraints | PK; FK `instructor_id` → `instructor` con `ON DELETE RESTRICT` | `hu-act-033-instructor-ficha-assignment-constraints-001` (04_alter) | Borrado lógico, sin cascada; `ficha_id` y `competency_id` no llevan FK (otro servicio) |
| `actors_instructors.instructor_ficha_assignment`: índices | `uq_instructor_ficha_assignment_active` (único parcial), `ix_instructor_ficha_assignment_ficha`, `ix_instructor_ficha_assignment_instructor` | `hu-act-033-instructor-ficha-assignment-indexes-001` (10_indexes) | Una asignación activa por instructor, ficha y competencia; consultas por ficha y por instructor |
| Semilla sintética (`dev,qa`) | fila `5e000000-...-0000000000f5`: instructor `...00b1` en ficha `...00c6` | `hu-act-033-seed-synthetic-instructor-ficha-assignment-001` (02_dml/04_patches) | Dato de prueba; no va a staging ni a main |
| `rbac_catalog.feature` `ACT_INSTRUCTOR_FICHA_ASSIGN` + grants | feature WRITE de `MOD_ACTORS`; SYSTEM_ADMIN GLOBAL, CENTER_DIRECTOR y COORDINATOR TRAINING_CENTER; LEARNER recibe `ACT_INSTRUCTOR_VIEW` `OWN_FICHA_AS_LEARNER` | `hu-act-033-instructor-ficha-assignment-016` (iam-db 02_dml/00_inserts) | [rbac-design.md](../09-microservices/services/01-iam-service/rbac-design.md) |

## Actualización HU-ACAD-11 de Actors — juicio evaluativo por RAP — 2026-10-24

| Objeto | Tipo / columnas principales | Changeset | Propósito y fuente canónica |
|---|---|---|---|
| `actors_learners.learner_rap_assessment` | `learner_id`, `ficha_id`, `learning_outcome_id` (UUID sin FK entre BD), `result` (`APPROVED` / `NOT_APPROVED`), `assessed_by`, `assessed_at` y auditoría ADR-004 | `hu-act-029-learner-rap-assessment-table-001` (03_tables) | Juicio evaluativo de un aprendiz sobre un RAP de su ficha; evidencia de la regla de cierre RN-ACAD-07 (100 % de los RAP activos del programa aprobados por cada aprendiz activo). No hay nota numérica; [modelo del servicio](../09-microservices/services/06-actors-service/data-model.md) |
| `actors_learners.learner_rap_assessment`: constraints | PK; `UNIQUE (learner_id, ficha_id, learning_outcome_id)`; FK compuesta a `learner_ficha_enrollment (learner_id, ficha_id)` con `ON DELETE RESTRICT` | `hu-act-029-learner-rap-assessment-constraints-001` (04_alter) | Un juicio vigente por aprendiz, ficha y RAP; borrado lógico, sin cascada; mismo modelo canónico |
| `actors_learners.learner_rap_assessment`: índice | `ix_learner_rap_assessment_ficha_result` (parcial sobre filas activas) | `hu-act-029-learner-rap-assessment-indexes-001` (10_indexes) | Conteo de cobertura por ficha; mismo modelo canónico |

Estado: changesets publicados en `design-software-actors-db` [PR #71](https://github.com/code-sena/design-software-actors-db/pull/71), pendientes de revisión y merge a develop. Sustituyen a la tabla `learner_final_grade` del primer borrador del PR, retirada por decisión del dueño (no hay nota numérica).

## Datos de referencia compartidos

El servicio `reference-data-service` es el propietario de la jerarquía institucional y los catálogos base. Otros servicios **no duplican** esos catálogos: los referencian por `id` (o los consumen vía evento/contrato), según [service-catalog.md](../09-microservices/service-catalog.md).

## Actualización R1 de Reference Data — 2026-10-20

| Objeto | Tipo / columnas principales | Changeset | Propósito y fuente canónica |
|---|---|---|---|
| `parameterization.event_inbox` | PK VARCHAR(100)+UUID; SHA-256 CHAR(64); processed_at TIMESTAMPTZ | `r1-reference-inbox-projection-001` | Deduplicación por consumidor/evento; [modelo del servicio](../09-microservices/services/02-reference-data-service/data-model.md) |
| `parameterization.event_projection` | PK VARCHAR(80)+UUID; payload JSONB; fecha TIMESTAMPTZ; contador BIGINT positivo | `r1-reference-inbox-projection-001` | Efecto persistente operativo e inspección del consumo; mismo modelo canónico |
| Grants inbox/projection | Permisos de reference_writer/reference_reader | `r1-reference-inbox-projection-grants-001` | Mínimo privilegio sin DELETE del historial de deduplicación |
| Revoke inbox/projection | Permisos sobrantes de reference_writer/reference_reader | `r1-reference-inbox-projection-grants-002` | Quita los privilegios heredados de los grants globales para que lo efectivo sea lo documentado |

Estado: diseño documentado antes del código; ejecución y revisión del changeset en el macroproyecto pendientes. El índice global no duplica todos los campos: el modelo del servicio contiene la definición completa, rollback y límites de retención.

## Actualización Document — HU-DOC-002 a HU-DOC-004 y mensajería R1

Los cambios de esquema de Document entre los changesets 970 y 975 se reflejan en el modelo canónico del servicio. Esta tabla identifica las entregas y sus objetos; columnas, constraints, índices y relaciones están detallados en [`07-document-service/data-model.md`](../09-microservices/services/07-document-service/data-model.md).

| Changeset | Objetos | Cambio documentado | Historia |
|---|---|---|---|
| `refinamiento-document-d9-template-versions-970` | `document_template_version`, `document_template_variable`, `document.template_version_id` | Versiones de plantilla, catálogo de variables y vínculo de la versión usada por cada documento | D-9 |
| `hu-doc-002-document-generating-nullable-storage-972` | `document.storage_key`, `document.mime_type` | Permite persistir el estado `GENERATING`; `ck_document_storage_when_available` exige ambos valores al completar la generación | HU-DOC-002 |
| `hu-doc-003-document-access-and-filters-973` | `document.training_center_id` | Alcance de acceso por centro y sus índices de consulta | HU-DOC-003 |
| `hu-doc-004-version-idempotency-974` | `document_version.correlation_id` | Evita crear dos versiones para el mismo mensaje de generación | HU-DOC-004 |
| `document-r1-outbox-inbox-975` | `document.event_outbox`, `document.message_inbox` | Publicación transaccional de eventos, reintentos y deduplicación de mensajes procesados | R1 |

Los cambios 970 y 972–975 están registrados en los changelogs de `design-software-document-db`; el modelo del servicio es la fuente de detalle de esquema y no se replica aquí.
