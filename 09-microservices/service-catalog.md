# Catálogo actualizado de microservicios

> Estado: 🟡 Revisión | Última actualización: 2026-10-07
> Autor: Kevin Andrey Culma (Arquitecto) | Equipo: Arquitectura.

> La tabla de implementación observada más abajo es el corte histórico registrado el 2026-10-07; sus commits y conteos no certifican el estado actual. Para la convención de rutas, estado por ambiente y responsables del corte 2026-10-30, véase el [baseline DS-001](../15-project-control/ds-001-architecture-baseline.md).

## Resumen ejecutivo

La topología backend vigente tiene 10 microservicios desplegables y 10 repositorios de datos/infra relacionados. Hay 9 módulos funcionales de producto; document-service, audit-service y notification-service son capacidades transversales.

| # | Microservicio | Módulo | Responsabilidad | App repo | DB repo | Stack | Deployables |
|---|---|---|---|---|---|---|---|
| 01 | `iam-service` | M1 | Identidad, autenticación, sesiones, RBAC, JWT/JWKS y auditoría de login. | `design-software-iam-service` | `design-software-iam-db` | Java / Spring Boot / Maven | iam-api |
| 02 | `reference-data-service` | M2 + M4 | Jerarquía institucional, centros de formación, unidades institucionales, catálogos y parámetros. | `design-software-reference-data-service` | `design-software-reference-data-db` | Go | reference-data-api |
| 03 | `academic-management-service` | M5 + M6 | Líneas/redes tecnológicas, programas, competencias, resultados de aprendizaje y fichas. | `design-software-academic-management-service` | `design-software-academic-management-db` | Java / Spring Boot / Maven | academic-management-api |
| 04 | `training-environment-service` | M3 | Ambientes de formación, tipos, inventario, reglas de disponibilidad, mantenimientos y reservas. | `design-software-training-environment-service` | `design-software-training-environment-db` | Go | training-environment-api |
| 05 | `scheduling-service` | M8 | Creación, validación, publicación, archivo y consulta de horarios y sesiones. | `design-software-scheduling-service` | `design-software-scheduling-db` | Java / Spring Boot / Maven | schedules-api, scheduling-engine, conflict-validator |
| 06 | `actors-service` | M7 | Instructores, aprendices, empresas, etapa productiva, asignación de competencias y planes de mejora. | `design-software-actors-service` | `design-software-actors-db` | Java / Spring Boot / Maven | actors-api |
| 07 | `document-service` | Transversal | Documentos, versiones, plantillas, variables de plantilla, renderizado PDF y ciclo de vida documental. | `design-software-document-service` | `design-software-document-db` | Python / FastAPI | document_api, template_api, pdf_renderer_worker, document_lifecycle_worker |
| 08 | `monitoring-service` | M9 | KPIs, seguimiento de fichas, sesiones de seguimiento, alertas generadas y planes de mejora. | `design-software-monitoring-service` | `design-software-monitoring-db` | Python / FastAPI | api, alert_worker |
| 09 | `audit-service` | Transversal | Registro append-only de auditoría y consulta de eventos auditables. | `design-software-audit-service` | `design-software-audit-db` | Go | audit-query-api, audit-worker |
| 10 | `notification-service` | Transversal | Envío, trazabilidad e idempotencia de notificaciones EMAIL e IN_APP. | `design-software-notification-service` | `design-software-notification-db` | Go | notification-api, notification-worker |

## Estado de implementación observado

| Microservicio | Rama app | Commit app | Endpoints detectados | Tablas principales | Estado |
|---|---|---:|---:|---:|---|
| `iam-service` | `develop` | `240b1d1` | 3 | 11 | Implementado con contrato OpenAPI y controladores que implementan interfaces generadas. |
| `reference-data-service` | `develop` | `2662107` | 3 | 9 | Implementado con API HTTP, seguridad JWT/JWKS y publicación AMQP opcional. |
| `academic-management-service` | `develop` | `437b092` | 32 | 7 | Implementado con arquitectura hexagonal y módulos academic-core, academic-adapters y academic-management-api. |
| `training-environment-service` | `develop` | `ccd2d95` | 24 | 7 | Implementado con API HTTP y middleware JWT. |
| `scheduling-service` | `develop` | `864a479` | 19 | 8 | Implementado con módulos contracts, scheduling-core, scheduling-adapters, schedules-api, scheduling-engine y conflict-validator. |
| `actors-service` | `develop` | `c160e05` | 50 | 15 | Implementado con módulos actors-core, actors-adapters y actors-api. |
| `document-service` | `develop` | `feda1e2` | 2 | 5 | Esqueleto hexagonal con APIs FastAPI y workers definidos. |
| `monitoring-service` | `develop` | `0e4a200` | 2 | 13 | Implementado parcialmente con API FastAPI, caso de uso RecordKpi y worker de alertas pendiente. |
| `audit-service` | `develop` | `9157f84` | 1 | 4 | Esqueleto Go con query API de health y worker pendiente. |
| `notification-service` | `develop` | `e237b4f` | 6 | 3 | Implementado con API HTTP, worker AMQP, outbox, templates y SMTP/MailHog para dev. |

## Notas de ownership

- Cada microservicio mantiene ownership de escritura sobre su repositorio de datos correspondiente.
- `notification-service` es el propietario vigente de entrega de notificaciones, templates, outbox de notificación y `sent_notification`.
- `monitoring-service` conserva KPIs y alertas. Si aparece `monitoring.sent_notification` en scripts SQL, tratarla como legado/remediación histórica y no como ownership vigente de entrega.
- `audit-service` debe recibir eventos de auditoría de forma asíncrona; ningún servicio debe escribir directamente en su base.
