# training-environment-service

> Estado: 🟡 Revisión | Última actualización: 2026-10-07
> Autor: Kevin Andrey Culma (Arquitecto) | Equipo: Arquitectura.

| Campo | Valor |
|---|---|
| Módulo | M3 |
| App repo | `design-software-training-environment-service` |
| DB repo | `design-software-training-environment-db` |
| Stack | Go |
| Deployables | training-environment-api |
| Estado observado | Implementado con API HTTP y middleware JWT. |

## Responsabilidad

Ambientes de formación, tipos, inventario, reglas de disponibilidad, mantenimientos y reservas.

## Persistencia

- Esquemas: training_environment
- Tablas: training_environment.availability_rule, training_environment.environment, training_environment.environment_type, training_environment.inventory_item, training_environment.item_type, training_environment.maintenance, training_environment.reservation

## API detectada

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/environment-types` | `.\design-software-training-environment-service\internal\adapter\in\http\handler.go` |
| POST | `/environment-types` | `.\design-software-training-environment-service\internal\adapter\in\http\handler.go` |
| GET | `/environment-types/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\handler.go` |
| GET | `/health` | `.\design-software-training-environment-service\cmd\training-environment-api\main.go` |
| GET | `/metrics` | `.\design-software-training-environment-service\cmd\training-environment-api\main.go` |
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

## Configuración

- `APP_ENV`
- `DATABASE_URL`
- `ENV`
- `ENVIRONMENT`
- `ID`
- `JWKS_JSON`
- `JWKS_URL`
- `JWT_PUBLIC_KEY`
- `JWT_SECRET`
- `PERF_DATE`
- `PERF_SAMPLES`
- `PORT`
- `REQUIRE_POSTGRES_INTEGRATION`
- `TEST_DATABASE_URL`

## Notas

Usa DATABASE_URL y JWT/JWKS; expone reportes de utilización e implementa observabilidad integral conforme a [ADR-012](../../../05-architecture/decisions/records/ADR-012-training-environment-r3-observability.md) (OpenTelemetry W3C, métricas RED en /metrics, logs JSON correlacionados y alertas Grafana).

- **Informe técnico de observabilidad (Reto R3):** [informe-tecnico-r3.md](./informe-tecnico-r3.md)
