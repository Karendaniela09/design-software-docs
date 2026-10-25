# actors-service

> Estado: 🟡 Revisión | Última actualización: 2026-10-07
> Autor: Kevin Andrey Culma (Arquitecto) | Equipo: Arquitectura.

| Campo | Valor |
|---|---|
| Módulo | M7 |
| App repo | `design-software-actors-service` |
| DB repo | `design-software-actors-db` |
| Stack | Java / Spring Boot / Maven |
| Deployables | actors-api |
| Estado observado | Implementado con módulos actors-core, actors-adapters y actors-api. |

## Responsabilidad

Instructores, aprendices, empresas, etapa productiva, asignación de competencias y planes de mejora.

## Persistencia

- Esquemas: actors_companies, actors_instructors, actors_learners, actors_parameterization, actors_tracking
- Tablas: actors_companies.company, actors_companies.company_visit, actors_companies.productive_stage, actors_instructors.competency_assignment, actors_instructors.instructor, actors_instructors.instructor_area, actors_instructors.instructor_availability_exception, actors_instructors.instructor_contract, actors_learners.learner, actors_learners.learner_ficha_enrollment, actors_parameterization.status, actors_parameterization.status_category, actors_parameterization.status_transition, actors_tracking.activity_log, actors_tracking.actor_improvement_plan

## API detectada

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/api/v1/catalogs` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\CatalogController.java` |
| GET | `/api/v1/catalogs/{catalog_id}/details` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\CatalogController.java` |
| GET | `/api/v1/companies` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\CompanyController.java` |
| POST | `/api/v1/companies` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\CompanyController.java` |
| DELETE | `/api/v1/companies/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\CompanyController.java` |
| GET | `/api/v1/companies/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\CompanyController.java` |
| PATCH | `/api/v1/companies/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\CompanyController.java` |
| PUT | `/api/v1/companies/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\CompanyController.java` |
| GET | `/api/v1/improvement-plans` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\ImprovementPlanController.java` |
| POST | `/api/v1/improvement-plans` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\ImprovementPlanController.java` |
| GET | `/api/v1/improvement-plans/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\ImprovementPlanController.java` |
| PUT | `/api/v1/improvement-plans/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\ImprovementPlanController.java` |
| GET | `/api/v1/instructors` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorController.java` |
| POST | `/api/v1/instructors` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorController.java` |
| DELETE | `/api/v1/instructors/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorController.java` |
| GET | `/api/v1/instructors/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorController.java` |
| PATCH | `/api/v1/instructors/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorController.java` |
| PUT | `/api/v1/instructors/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorController.java` |
| GET | `/api/v1/instructors/{id}/activity-log` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorController.java` |
| GET | `/api/v1/instructors/{id}/availability-exceptions` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorAvailabilityExceptionController.java` |
| POST | `/api/v1/instructors/{id}/availability-exceptions` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorAvailabilityExceptionController.java` |
| DELETE | `/api/v1/instructors/{id}/availability-exceptions/{exception_id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorAvailabilityExceptionController.java` |
| GET | `/api/v1/instructors/{instructorId}/areas` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorAreaController.java` |
| POST | `/api/v1/instructors/{instructorId}/areas` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorAreaController.java` |
| DELETE | `/api/v1/instructors/{instructorId}/areas/{areaId}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorAreaController.java` |
| GET | `/api/v1/instructors/{instructorId}/competencies` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\CompetencyAssignmentController.java` |
| POST | `/api/v1/instructors/{instructorId}/competencies` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\CompetencyAssignmentController.java` |
| DELETE | `/api/v1/instructors/{instructorId}/competencies/{assignmentId}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\CompetencyAssignmentController.java` |
| GET | `/api/v1/instructors/{instructorId}/contracts` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorContractController.java` |
| POST | `/api/v1/instructors/{instructorId}/contracts` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorContractController.java` |
| GET | `/api/v1/instructors/{instructorId}/contracts/{contractId}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorContractController.java` |
| PUT | `/api/v1/instructors/{instructorId}/contracts/{contractId}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InstructorContractController.java` |
| GET | `/api/v1/learners` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\LearnerController.java` |
| POST | `/api/v1/learners` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\LearnerController.java` |
| DELETE | `/api/v1/learners/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\LearnerController.java` |
| GET | `/api/v1/learners/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\LearnerController.java` |
| PATCH | `/api/v1/learners/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\LearnerController.java` |
| PUT | `/api/v1/learners/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\LearnerController.java` |
| GET | `/api/v1/learners/{id}/activity-log` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\LearnerController.java` |
| GET | `/api/v1/learners/{id}/ficha-enrollments` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\LearnerController.java` |
| POST | `/api/v1/learners/{id}/ficha-enrollments` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\LearnerController.java` |
| GET | `/api/v1/productive-stages` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\ProductiveStageController.java` |
| POST | `/api/v1/productive-stages` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\ProductiveStageController.java` |
| GET | `/api/v1/productive-stages/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\ProductiveStageController.java` |
| PUT | `/api/v1/productive-stages/{id}` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\ProductiveStageController.java` |
| POST | `/api/v1/productive-stages/{id}/visits` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\ProductiveStageController.java` |
| GET | `/api/v1/reports/active-catalog` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\CatalogController.java` |
| GET | `/api/v1/reports/instructor-load` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\ReportsController.java` |
| GET | `/api/v1/reports/learner-tracking` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\ReportsController.java` |
| GET | `/internal/fichas/{fichaId}/active-learners/count` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InternalFichaLearnerController.java` |
| GET | `/internal/learners/by-user/{userId}/active-ficha` | `.\design-software-actors-service\actors-adapters\src\main\java\co\sena\actors\adapter\in\rest\InternalLearnerFichaController.java` |

## Configuración

- `ACADEMIC_MANAGEMENT_BASE_URL`
- `ACTORS_DB_PASSWORD`
- `ACTORS_DB_URL`
- `ACTORS_DB_USER`
- `IAM_JWKS_URI`
- `IAM_JWT_ISSUER`
- `ACTORS_EVENTS_EXCHANGE`
- `ACTORS_OUTBOX_ENABLED`
- `SPRING_RABBITMQ_HOST`
- `SPRING_RABBITMQ_PASSWORD`
- `SPRING_RABBITMQ_USERNAME`
- `OTEL_EXPORTER_OTLP_ENDPOINT`

## Documentación técnica

- [Data Model](./data-model.md)
- [Decisiones](./decisions.md)
- [Eventos](./events.md)
- [Runbook](./runbook.md)
- [Seguridad y STRIDE (R4)](./security.md)
- [Decisión Arquitectónica (ADR-019)](../../../05-architecture/decisions/records/ADR-019-actors-security-hardening.md)
- [Reporte QA de Seguridad R4](../../../11-quality/qa-report-r4-security-actors.md)

## Notas

Integra con academic-management para información de fichas/competencias.

