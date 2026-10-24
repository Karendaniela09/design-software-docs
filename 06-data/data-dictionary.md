# Diccionario de datos

> Estado: 🟡 En progreso | Última actualización: 2026-08-28
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Datos

Índice transversal del modelo de datos. **La fuente de verdad de cada tabla (columnas, tipos, PII, retención, índices, seeds) es el `data-model.md` de cada servicio.** Este documento no duplica esas definiciones: las referencia y fija las reglas comunes.

## Convenciones comunes (obligatorias)

Definidas en [modeling-conventions.md](./modeling-conventions.md):
- **PK** `UUID` en todas las tablas · **Timestamps** `TIMESTAMPTZ` (UTC).
- **Columnas de auditoría** estándar según tipo de tabla (transaccional / catálogo / append-only).
- **Estados de negocio** parametrizables (`status_category` / `status` / `status_transition`); enums técnicos cerrados como `VARCHAR + CHECK`.
- **Nomenclatura** de constraints: `pk_`, `uq_`, `fk_`, `ck_`, `ix_`.

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

## Datos de referencia compartidos

El servicio `reference-data-service` es el propietario de la jerarquía institucional y los catálogos base. Otros servicios **no duplican** esos catálogos: los referencian por `id` (o los consumen vía evento/contrato), según [service-catalog.md](../09-microservices/service-catalog.md).

## Actualización R1 de Reference Data — 2026-10-20

| Objeto | Tipo / columnas principales | Changeset | Propósito y fuente canónica |
|---|---|---|---|
| `parameterization.event_inbox` | PK VARCHAR(100)+UUID; SHA-256 CHAR(64); processed_at TIMESTAMPTZ | `r1-reference-inbox-projection-001` | Deduplicación por consumidor/evento; [modelo del servicio](../09-microservices/services/02-reference-data-service/data-model.md) |
| `parameterization.event_projection` | PK VARCHAR(80)+UUID; payload JSONB; fecha TIMESTAMPTZ; contador BIGINT positivo | `r1-reference-inbox-projection-001` | Efecto persistente operativo e inspección del consumo; mismo modelo canónico |
| Grants inbox/projection | Permisos de reference_writer/reference_reader | `r1-reference-inbox-projection-grants-001` | Mínimo privilegio sin DELETE del historial de deduplicación |

Estado: diseño documentado antes del código; ejecución y revisión del changeset en el macroproyecto pendientes. El índice global no duplica todos los campos: el modelo del servicio contiene la definición completa, rollback y límites de retención.
