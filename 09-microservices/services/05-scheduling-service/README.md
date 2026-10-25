# scheduling-service

> Estado: 🟡 Revisión | Última actualización: 2026-10-07
> Autor: Kevin Andrey Culma (Arquitecto) | Equipo: Arquitectura.

| Campo | Valor |
|---|---|
| Módulo | M8 |
| App repo | `design-software-scheduling-service` |
| DB repo | `design-software-scheduling-db` |
| Stack | Java / Spring Boot / Maven |
| Deployables | schedules-api, scheduling-engine, conflict-validator |
| Estado observado | Implementado con módulos contracts, scheduling-core, scheduling-adapters, schedules-api, scheduling-engine y conflict-validator. |

## Responsabilidad

Creación, validación, publicación, archivo y consulta de horarios y sesiones.

## Persistencia

- Esquemas: scheduling
- Tablas: scheduling.class_session, scheduling.environment_availability_projection, scheduling.ficha_training_center_projection, scheduling.instructor_availability_projection, scheduling.outbox, scheduling.schedule, scheduling.scheduling_conflict, scheduling.site_travel_time, scheduling.time_slot

## API detectada

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

## Configuración

- `OTEL_EXPORTER_OTLP_ENDPOINT`
- `OTEL_TRACES_ENABLED`
- `OTEL_TRACES_SAMPLER_PROBABILITY`
- `POSTGRES_DB`
- `POSTGRES_PASSWORD`
- `POSTGRES_USER`
- `SCHEDULING_DB_PASSWORD`
- `SCHEDULING_DB_URL`
- `SCHEDULING_DB_USERNAME`
- `SCHEDULING_JPA_DDL_AUTO`
- `SCHEDULING_JPA_SHOW_SQL`
- `SCHEDULING_RABBIT_HEALTH_ENABLED`
- `SCHEDULING_RABBIT_LISTENER_ENABLED`
- `SERVER_PORT`
- `SPRING_RABBITMQ_HOST`
- `SPRING_RABBITMQ_PASSWORD`
- `SPRING_RABBITMQ_PORT`
- `SPRING_RABBITMQ_USERNAME`

## Notas

Mantiene proyecciones locales de disponibilidad de instructores y ambientes.

## Rendimiento R2

La decisión está en [ADR-027](../../../05-architecture/decisions/records/ADR-027-scheduling-r2-performance.md) y los resultados en el [informe QA R2](../../../11-quality/qa-report-r2-scheduling-service.md).
