# Mapa de superficie API

> Generado desde anotaciones/controladores y rutas detectadas el 2026-10-07. Los endpoints implementados mediante interfaces OpenAPI generadas pueden requerir validar el contrato YAML para detalle completo.

## iam-service

- Repo: `design-software-iam-service`
- Stack: Java / Spring Boot / Maven
- Deployables: iam-api

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/api/v1/auth/.well-known/jwks.json` | `.\design-software-iam-service\iam-adapters\src\main\java\co\sena\iam\adapter\in\rest\JwksController.java` |
| GET | `/health` | `.\design-software-iam-service\iam-adapters\src\main\java\co\sena\iam\adapter\in\rest\HealthController.java` |
| GET | `/ready` | `.\design-software-iam-service\iam-adapters\src\main\java\co\sena\iam\adapter\in\rest\HealthController.java` |

Nota IAM: los controladores principales implementan interfaces generadas desde `contracts/openapi/iam.yaml`. Ademas de `/health`, `/ready` y JWKS, el contrato incluye `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me`, password reset, `/users`, `/roles`, `/modules` y reportes de login.

## reference-data-service

- Repo: `design-software-reference-data-service`
- Stack: Go
- Deployables: reference-data-api

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/health` | `.\design-software-reference-data-service\cmd\reference-data-api\main.go` |
| GET | `/health/live` | `.\design-software-reference-data-service\cmd\reference-data-api\main.go` |
| GET | `/health/ready` | `.\design-software-reference-data-service\cmd\reference-data-api\main.go` |

## academic-management-service

- Repo: `design-software-academic-management-service`
- Stack: Java / Spring Boot / Maven
- Deployables: academic-management-api

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/api/v1/competencies/{competencyId}/learning-outcomes` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\LearningOutcomeController.java` |
| POST | `/api/v1/competencies/{competencyId}/learning-outcomes` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\LearningOutcomeController.java` |
| GET | `/api/v1/fichas` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\FichaController.java` |
| POST | `/api/v1/fichas` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\FichaController.java` |
| GET | `/api/v1/fichas/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\FichaController.java` |
| DELETE | `/api/v1/learning-outcomes/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\LearningOutcomeController.java` |
| PUT | `/api/v1/learning-outcomes/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\LearningOutcomeController.java` |
| DELETE | `/competencies/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\CompetencyController.java` |
| GET | `/competencies/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\CompetencyController.java` |
| PUT | `/competencies/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\CompetencyController.java` |
| GET | `/knowledge-networks` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\KnowledgeNetworkController.java` |
| POST | `/knowledge-networks` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\KnowledgeNetworkController.java` |
| DELETE | `/knowledge-networks/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\KnowledgeNetworkController.java` |
| GET | `/knowledge-networks/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\KnowledgeNetworkController.java` |
| PUT | `/knowledge-networks/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\KnowledgeNetworkController.java` |
| GET | `/tech-lines` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechLineController.java` |
| POST | `/tech-lines` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechLineController.java` |
| DELETE | `/tech-lines/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechLineController.java` |
| GET | `/tech-lines/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechLineController.java` |
| PUT | `/tech-lines/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechLineController.java` |
| GET | `/tech-networks` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechNetworkController.java` |
| POST | `/tech-networks` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechNetworkController.java` |
| DELETE | `/tech-networks/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechNetworkController.java` |
| GET | `/tech-networks/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechNetworkController.java` |
| PUT | `/tech-networks/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechNetworkController.java` |
| GET | `/training-programs` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TrainingProgramController.java` |
| POST | `/training-programs` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TrainingProgramController.java` |
| DELETE | `/training-programs/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TrainingProgramController.java` |
| GET | `/training-programs/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TrainingProgramController.java` |
| PUT | `/training-programs/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TrainingProgramController.java` |
| GET | `/training-programs/{programId}/competencies` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\CompetencyController.java` |
| POST | `/training-programs/{programId}/competencies` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\CompetencyController.java` |

## training-environment-service

- Repo: `design-software-training-environment-service`
- Stack: Go
- Deployables: training-environment-api

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/environment-types` | `.\design-software-training-environment-service\internal\adapter\in\http\handler.go` |
| POST | `/environment-types` | `.\design-software-training-environment-service\internal\adapter\in\http\handler.go` |
| GET | `/environment-types/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\handler.go` |
| GET | `/health` | `.\design-software-training-environment-service\cmd\training-environment-api\main.go` |
| GET | `/reports/environment-utilization` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_utilization_handler.go` |
| GET | `/reservations` | `.\design-software-training-environment-service\internal\adapter\in\http\reservation_handler.go` |
| POST | `/reservations` | `.\design-software-training-environment-service\internal\adapter\in\http\reservation_handler.go` |
| DELETE | `/reservations/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\reservation_handler.go` |
| GET | `/reservations/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\reservation_handler.go` |
| PATCH | `/reservations/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\reservation_handler.go` |
| GET | `/training-environments` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_handler.go` |
| POST | `/training-environments` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_handler.go` |
| DELETE | `/training-environments/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_handler.go` |
| GET | `/training-environments/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_handler.go` |
| PATCH | `/training-environments/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_handler.go` |
| PUT | `/training-environments/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_handler.go` |
| GET | `/training-environments/{id}/availability-rules` | `.\design-software-training-environment-service\internal\adapter\in\http\availability_rule_handler.go` |
| POST | `/training-environments/{id}/availability-rules` | `.\design-software-training-environment-service\internal\adapter\in\http\availability_rule_handler.go` |
| DELETE | `/training-environments/{id}/availability-rules/{rule_id}` | `.\design-software-training-environment-service\internal\adapter\in\http\availability_rule_handler.go` |
| GET | `/training-environments/{id}/availability-rules/{rule_id}` | `.\design-software-training-environment-service\internal\adapter\in\http\availability_rule_handler.go` |
| PUT | `/training-environments/{id}/availability-rules/{rule_id}` | `.\design-software-training-environment-service\internal\adapter\in\http\availability_rule_handler.go` |
| GET | `/training-environments/{id}/maintenance` | `.\design-software-training-environment-service\internal\adapter\in\http\maintenance_handler.go` |
| POST | `/training-environments/{id}/maintenance` | `.\design-software-training-environment-service\internal\adapter\in\http\maintenance_handler.go` |
| GET | `/training-environments/{id}/maintenance/{maintenance_id}` | `.\design-software-training-environment-service\internal\adapter\in\http\maintenance_handler.go` |

## scheduling-service

- Repo: `design-software-scheduling-service`
- Stack: Java / Spring Boot / Maven
- Deployables: schedules-api, scheduling-engine, conflict-validator

| Metodo | Ruta | Fuente |
|---|---|---|
| POST | `/api/v1/conflicts/{id}/resolve` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\ConflictController.java` |
| GET | `/api/v1/health` | `.\design-software-scheduling-service\schedules-api\src\main\java\co\sena\scheduling\api\HealthController.java` |
| GET | `/api/v1/ready` | `.\design-software-scheduling-service\schedules-api\src\main\java\co\sena\scheduling\api\HealthController.java` |
| GET | `/api/v1/schedules` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\ScheduleController.java` |
| POST | `/api/v1/schedules` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\ScheduleController.java` |
| DELETE | `/api/v1/schedules/{id}` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\ScheduleController.java` |
| GET | `/api/v1/schedules/{id}` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\ScheduleController.java` |
| PUT | `/api/v1/schedules/{id}` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\ScheduleController.java` |
| POST | `/api/v1/schedules/{id}/archive` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\ScheduleController.java` |
| GET | `/api/v1/schedules/{id}/conflicts` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\ScheduleController.java` |
| POST | `/api/v1/schedules/{id}/publish` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\ScheduleController.java` |
| GET | `/api/v1/schedules/{id}/sessions` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\SessionController.java` |
| POST | `/api/v1/schedules/{id}/sessions` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\SessionController.java` |
| POST | `/api/v1/schedules/{id}/validate` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\ScheduleController.java` |
| GET | `/api/v1/sessions` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\SessionController.java` |
| DELETE | `/api/v1/sessions/{id}` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\SessionController.java` |
| GET | `/api/v1/sessions/{id}` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\SessionController.java` |
| PUT | `/api/v1/sessions/{id}` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\SessionController.java` |
| POST | `/api/v1/sessions/{id}/cancel` | `.\design-software-scheduling-service\scheduling-adapters\src\main\java\co\sena\scheduling\adapter\in\rest\SessionController.java` |

## actors-service

- Repo: `design-software-actors-service`
- Stack: Java / Spring Boot / Maven
- Deployables: actors-api

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

## document-service

- Repo: `design-software-document-service`
- Stack: Python / FastAPI
- Deployables: document_api, template_api, pdf_renderer_worker, document_lifecycle_worker

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/health` | `.\design-software-document-service\apps\template_api\main.py` |
| GET | `/health` | `.\design-software-document-service\apps\document_api\main.py` |

## monitoring-service

- Repo: `design-software-monitoring-service`
- Stack: Python / FastAPI
- Deployables: api, alert_worker

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/health` | `.\design-software-monitoring-service\src\monitoring\adapter\inbound\http\router.py` |
| POST | `/kpis` | `.\design-software-monitoring-service\src\monitoring\adapter\inbound\http\router.py` |

## audit-service

- Repo: `design-software-audit-service`
- Stack: Go
- Deployables: audit-query-api, audit-worker

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/api/v1/health` | `design-software-audit-service/internal/adapter/in/httpapi/query.go` |
| GET | `/api/v1/audit-records` | `design-software-audit-service/internal/adapter/in/httpapi/query.go` |
| GET | `/api/v1/audit-records/{id}` | `design-software-audit-service/internal/adapter/in/httpapi/query.go` |
| GET | `/api/v1/audit-records/export` | `design-software-audit-service/internal/adapter/in/httpapi/query.go` |

## notification-service

- Repo: `design-software-notification-service`
- Stack: Go
- Deployables: notification-api, notification-worker

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/health` | `.\design-software-notification-service\internal\adapter\in\http\handler.go` |
| GET | `/health` | `.\design-software-notification-service\cmd\notification-worker\main.go` |
| POST | `/notifications` | `.\design-software-notification-service\internal\adapter\in\http\handler.go` |
| GET | `/notifications/{id}` | `.\design-software-notification-service\internal\adapter\in\http\handler.go` |
| GET | `/ready` | `.\design-software-notification-service\cmd\notification-worker\main.go` |
| GET | `/ready` | `.\design-software-notification-service\internal\adapter\in\http\handler.go` |
