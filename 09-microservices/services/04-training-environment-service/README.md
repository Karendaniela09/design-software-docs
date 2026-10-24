# training-environment-service

> Estado: 🟡 Revisión | Última actualización: 2026-10-24
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

Las operaciones del contrato ([`training-environment.yaml`](../../../07-api/contracts/openapi/training-environment.yaml), `servers: /api/v1`) se sirven bajo `/api/v1`, como fija [ADR-022 §3](../../../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md); detrás del edge la ruta pública es `/training-environment/api/v1/<recurso>`. Las rutas sin prefijo (`/environment-types`, `/training-environments`, `/reservations`, `/reports/...`) responden `404`. `GET /health` se mantiene también en la raíz como sonda de infraestructura (el edge enruta los health que no cuelgan de `/api/` con una regla de ruta exacta, ADR-022 §1) y `/metrics`, que no forma parte del contrato, queda en la raíz.

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/api/v1/environment-types` | `.\design-software-training-environment-service\internal\adapter\in\http\handler.go` |
| POST | `/api/v1/environment-types` | `.\design-software-training-environment-service\internal\adapter\in\http\handler.go` |
| GET | `/api/v1/environment-types/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\handler.go` |
| GET | `/api/v1/health` | `.\design-software-training-environment-service\internal\adapter\in\http\router.go` |
| GET | `/health` | `.\design-software-training-environment-service\internal\adapter\in\http\router.go` |
| GET | `/metrics` | `.\design-software-training-environment-service\cmd\training-environment-api\main.go` |
| GET | `/api/v1/reports/environment-utilization` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_utilization_handler.go` |
| GET | `/api/v1/reservations` | `.\design-software-training-environment-service\internal\adapter\in\http\reservation_handler.go` |
| POST | `/api/v1/reservations` | `.\design-software-training-environment-service\internal\adapter\in\http\reservation_handler.go` |
| DELETE | `/api/v1/reservations/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\reservation_handler.go` |
| GET | `/api/v1/reservations/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\reservation_handler.go` |
| PATCH | `/api/v1/reservations/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\reservation_handler.go` |
| GET | `/api/v1/training-environments` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_handler.go` |
| POST | `/api/v1/training-environments` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_handler.go` |
| DELETE | `/api/v1/training-environments/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_handler.go` |
| GET | `/api/v1/training-environments/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_handler.go` |
| PATCH | `/api/v1/training-environments/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_handler.go` |
| PUT | `/api/v1/training-environments/{id}` | `.\design-software-training-environment-service\internal\adapter\in\http\environment_handler.go` |
| GET | `/api/v1/training-environments/{id}/availability-rules` | `.\design-software-training-environment-service\internal\adapter\in\http\availability_rule_handler.go` |
| POST | `/api/v1/training-environments/{id}/availability-rules` | `.\design-software-training-environment-service\internal\adapter\in\http\availability_rule_handler.go` |
| DELETE | `/api/v1/training-environments/{id}/availability-rules/{rule_id}` | `.\design-software-training-environment-service\internal\adapter\in\http\availability_rule_handler.go` |
| GET | `/api/v1/training-environments/{id}/availability-rules/{rule_id}` | `.\design-software-training-environment-service\internal\adapter\in\http\availability_rule_handler.go` |
| PUT | `/api/v1/training-environments/{id}/availability-rules/{rule_id}` | `.\design-software-training-environment-service\internal\adapter\in\http\availability_rule_handler.go` |
| GET | `/api/v1/training-environments/{id}/maintenance` | `.\design-software-training-environment-service\internal\adapter\in\http\maintenance_handler.go` |
| POST | `/api/v1/training-environments/{id}/maintenance` | `.\design-software-training-environment-service\internal\adapter\in\http\maintenance_handler.go` |
| GET | `/api/v1/training-environments/{id}/maintenance/{maintenance_id}` | `.\design-software-training-environment-service\internal\adapter\in\http\maintenance_handler.go` |

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

- **R3 observability technical report:** [qa-report-r3-training-enviroment-service.md](../../../11-quality/qa-report-r3-training-enviroment-service.md)
## R6 maintenance schema evolution

- [Migration report and validation scope](./r6-schema-evolution.md).
- [ADR-017: reason and reason_detail compatibility](../../../05-architecture/decisions/records/ADR-017-training-environment-r6-schema-evolution.md).
- [QA report](../../../11-quality/qa-report-r6-training-environment-db.md).
- [Implementación DB: PR #134](https://github.com/code-sena/design-software-training-environment-db/pull/134).
