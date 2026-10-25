# academic-management-service

> Estado: 🟡 Revisión | Última actualización: 2026-10-07
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

## Configuración

- `ACADEMIC_COMPETENCY_ROUTING_KEY`
- `ACADEMIC_EVENTS_EXCHANGE`
- `ACADEMIC_FICHA_ROUTING_KEY`
- `ACTORS_SERVICE_BASE_URL`
- `DB_PASSWORD`
- `DB_URL`
- `DB_USER`
- `IAM_JWKS_URI`
- `OTEL_EXPORTER_OTLP_ENDPOINT`
- `OTEL_TRACES_SAMPLING`
- `RABBITMQ_HOST`
- `RABBITMQ_PASSWORD`
- `RABBITMQ_PORT`
- `RABBITMQ_USERNAME`
- `REFERENCE_DATA_BASE_URL`

## Notas

Consulta reference-data y actors; pública eventos de ficha/programa por RabbitMQ.
