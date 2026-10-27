# academic-management-service

> Estado: 🟡 Revisión | Última actualización: 2026-10-24
> Autor: Kevin Andrey Culma (Arquitecto) | Equipo: Arquitectura.

| Campo | Valor |
|---|---|
| Módulo | M5 + M6 |
| App repo | `design-software-academic-management-service` |
| DB repo | `design-software-academic-management-db` |
| Stack | Java / Spring Boot / Maven |
| Deployables | academic-management-api |
| Estado observado | Implementado con arquitectura hexagonal y módulos academic-core, academic-adapters y academic-management-api. |

## Responsabilidad

Líneas/redes tecnológicas, programas, competencias, resultados de aprendizaje y fichas.

## Persistencia

- Esquemas: academic_management
- Tablas: academic_management.competency, academic_management.enrollment_ficha, academic_management.knowledge_network, academic_management.learning_outcome, academic_management.outbox, academic_management.processed_event, academic_management.tech_line, academic_management.tech_network, academic_management.training_program

## API detectada

Todas las rutas del contrato (`servers: /api/v1`, ver [`academic-management.yaml`](../../../07-api/contracts/openapi/academic-management.yaml) y [contract.md](./components/academic-management-api/contract.md)) se sirven bajo `/api/v1`, también los catálogos (`tech-lines`, `tech-networks`, `knowledge-networks`, `training-programs`) y las competencias. Las rutas sin ese prefijo responden 404. Por el edge se publican como `/academic-management/api/v1/...` (ADR-022 §3).

Todos los listados responden con el envelope único del contrato: `{ "data": [...], "pagination": { "page", "page_size", "total_items", "total_pages" } }`, con `page` base 1 y `page_size` máximo 100 (`_shared.yaml`), y los campos de cada elemento en `snake_case` (`is_active`, `created_at`). Los errores usan `{ "error": { "code", "message", "details", "trace_id" } }`.

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/api/v1/competencies/{competencyId}/learning-outcomes` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\LearningOutcomeController.java` |
| POST | `/api/v1/competencies/{competencyId}/learning-outcomes` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\LearningOutcomeController.java` |
| GET | `/api/v1/fichas` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\FichaController.java` |
| POST | `/api/v1/fichas` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\FichaController.java` |
| GET | `/api/v1/fichas/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\FichaController.java` |
| DELETE | `/api/v1/learning-outcomes/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\LearningOutcomeController.java` |
| PUT | `/api/v1/learning-outcomes/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\LearningOutcomeController.java` |
| DELETE | `/api/v1/competencies/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\CompetencyController.java` |
| GET | `/api/v1/competencies/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\CompetencyController.java` |
| PUT | `/api/v1/competencies/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\CompetencyController.java` |
| GET | `/api/v1/knowledge-networks` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\KnowledgeNetworkController.java` |
| POST | `/api/v1/knowledge-networks` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\KnowledgeNetworkController.java` |
| DELETE | `/api/v1/knowledge-networks/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\KnowledgeNetworkController.java` |
| GET | `/api/v1/knowledge-networks/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\KnowledgeNetworkController.java` |
| PUT | `/api/v1/knowledge-networks/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\KnowledgeNetworkController.java` |
| GET | `/api/v1/tech-lines` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechLineController.java` |
| POST | `/api/v1/tech-lines` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechLineController.java` |
| DELETE | `/api/v1/tech-lines/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechLineController.java` |
| GET | `/api/v1/tech-lines/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechLineController.java` |
| PUT | `/api/v1/tech-lines/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechLineController.java` |
| GET | `/api/v1/tech-networks` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechNetworkController.java` |
| POST | `/api/v1/tech-networks` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechNetworkController.java` |
| DELETE | `/api/v1/tech-networks/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechNetworkController.java` |
| GET | `/api/v1/tech-networks/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechNetworkController.java` |
| PUT | `/api/v1/tech-networks/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TechNetworkController.java` |
| GET | `/api/v1/training-programs` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TrainingProgramController.java` |
| POST | `/api/v1/training-programs` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TrainingProgramController.java` |
| DELETE | `/api/v1/training-programs/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TrainingProgramController.java` |
| GET | `/api/v1/training-programs/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TrainingProgramController.java` |
| PUT | `/api/v1/training-programs/{id}` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\TrainingProgramController.java` |
| GET | `/api/v1/training-programs/{programId}/competencies` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\CompetencyController.java` |
| POST | `/api/v1/training-programs/{programId}/competencies` | `.\design-software-academic-management-service\academic-adapters\src\main\java\co\sena\academic\adapter\in\rest\CompetencyController.java` |

## Configuración

- `ACADEMIC_COMPETENCY_ROUTING_KEY`
- `ACADEMIC_EVENTS_EXCHANGE`
- `ACADEMIC_FICHA_ROUTING_KEY`
- `ACTORS_SERVICE_BASE_URL`
- `DB_PASSWORD`
- `DB_URL`
- `DB_USER`
- `IAM_JWKS_URL` (legacy alias: `IAM_JWKS_URI`)
- `OTEL_EXPORTER_OTLP_ENDPOINT`
- `OTEL_TRACES_SAMPLING`
- `RABBITMQ_HOST`
- `RABBITMQ_PASSWORD`
- `RABBITMQ_PORT`
- `RABBITMQ_USERNAME`
- `REFERENCE_DATA_BASE_URL`

## Notas

Consulta reference-data y actors; pública eventos de ficha/programa por RabbitMQ.
