# Entrega Develop HU-MON-004 / HU-04-monitoring

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

Fecha: 2026-10-14

Desarrollador: Kevin Andrey Culma Gomez

## Repositorios y ramas revisadas

| Repositorio | Rama | Estado |
| --- | --- | --- |
| `design-software-monitoring-service` | `hu-04-dev` | Modificado para PR hacia `develop` |
| `design-software-docs` | `hu-07-dev` | Modificado para contrato `/ready` y runbook |
| `design-software-monitoring-db` | `hu-09-dev` | Revisado como dependencia, sin cambios nuevos |

Antes de implementar se actualizaron las ramas padre del servicio:

- `develop`
- `qa`
- `staging`
- `main`

`develop` ya contenia HU-MON-003, por lo que HU-MON-004 se implemento encima del estado integrado mas reciente.

## Alcance implementado

HU-MON-004 cierra operabilidad, seguridad y calidad end-to-end para `monitoring-service`.

Se implemento:

- `/health` como liveness;
- `/ready` como readiness para BD y RabbitMQ;
- logs JSON estructurados con `trace_id`, `correlation_id` y `event_id`;
- configuracion centralizada por variables de entorno;
- instrumentacion OpenTelemetry alineada con ADR-008;
- metricas basicas de worker;
- CI con lint, compilacion y pruebas;
- README real del servicio;
- runbook operativo actualizado;
- prueba E2E minima del flujo evento -> alerta -> API -> resolucion -> plan.

## Pull requests creados

Pendiente de llenar tras crear PRs:

| Repositorio | Rama origen | Rama destino | PR | Commit |
| --- | --- | --- | --- | --- |
| `design-software-monitoring-service` | `hu-04-dev` | `develop` | https://github.com/code-sena/design-software-monitoring-service/pull/5 | `ddb9c52` |
| `design-software-docs` | `hu-07-dev` | `main` | https://github.com/code-sena/design-software-docs/pull/289 | `687b7d5` |

Nota: `design-software-docs` no tiene `origin/develop`; por eso el PR de Docs va hacia `main`, consistente con el flujo usado en Docs.

## Cambios realizados

### 1. Health y readiness

Archivos:

- `design-software-monitoring-service/src/monitoring/adapter/inbound/http/router.py`
- `design-software-monitoring-service/src/monitoring/readiness.py`
- `design-software-docs/07-api/contracts/openapi/monitoring.yaml`

Cambios:

- `GET /api/v1/health` queda como liveness publico.
- `GET /api/v1/ready` valida conectividad con base de datos y RabbitMQ.
- El contrato OpenAPI documenta `/ready` y su respuesta `503`.

### 2. Configuracion por entorno

Archivo:

- `design-software-monitoring-service/src/monitoring/config.py`

Variables cubiertas:

- `DATABASE_URL`
- `AMQP_URL`
- `JWKS_URL`
- `API_HOST`
- `API_PORT`
- `REQUEST_TIMEOUT_SECONDS`
- `READINESS_TIMEOUT_SECONDS`
- `OTEL_ENABLED`
- `OTEL_SERVICE_NAME`
- `OTEL_EXPORTER_OTLP_ENDPOINT`
- `DEPLOYMENT_ENVIRONMENT`
- `LOG_LEVEL`
- `ALERT_WORKER_MODE`

### 3. Observabilidad

Archivos:

- `design-software-monitoring-service/src/monitoring/observability.py`
- `design-software-monitoring-service/apps/api/main.py`
- `design-software-monitoring-service/apps/alert_worker/main.py`
- `design-software-monitoring-service/src/monitoring/application/usecase/alert_worker.py`

Cambios:

- Logs JSON con `trace_id`, `correlation_id` y `event_id`.
- Middleware de logging HTTP.
- Configuracion OpenTelemetry para FastAPI y SQLAlchemy.
- Contadores basicos para eventos procesados y alertas creadas.
- Logs de eventos del worker, relay outbox y DLQ.

### 4. CI/CD

Archivo:

- `design-software-monitoring-service/.github/workflows/ci.yml`

Pipeline:

- instala dependencias;
- ejecuta `ruff`;
- ejecuta `compileall`;
- ejecuta `pytest`;
- levanta servicios PostgreSQL y RabbitMQ disponibles para futuras pruebas de integracion.

### 5. README

Archivo:

- `design-software-monitoring-service/README.md`

Incluye:

- componentes runtime;
- endpoints disponibles;
- variables de entorno;
- comandos locales;
- calidad;
- observabilidad;
- retiro de `POST /api/v1/kpis`.

### 6. Runbook

Archivo:

- `design-software-docs/09-microservices/services/08-monitoring-service/runbook.md`

Incluye:

- arranque local;
- variables operativas;
- migraciones;
- verificacion de readiness;
- troubleshooting de BD;
- DLQ de Monitoring;
- replay de Outbox.

## Criterios de aceptacion

| AC | Estado | Evidencia |
| --- | --- | --- |
| AC-001 `/health` y `/ready` | Implementado | `router.py`, `readiness.py`, `test_monitoring_http_contract.py`, `monitoring.yaml` |
| AC-002 logs estructurados | Implementado | `observability.py`, `test_operability.py` |
| AC-003 OpenTelemetry | Implementado | `observability.py`, `apps/api/main.py`, `apps/alert_worker/main.py` |
| AC-004 configuracion por env | Implementado | `config.py`, README, runbook |
| AC-005 runbook actualizado | Implementado | `runbook.md` |
| AC-006 CI | Implementado | `.github/workflows/ci.yml` |
| AC-007 E2E minimo | Implementado | `test_monitoring_e2e.py` |
| AC-008 compatibilidad `/kpis` | Implementado | README indica retiro; contrato final usa `/kpi-trackings` |
| AC-009 README real | Implementado | `README.md` |
| AC-010 sin TODOs bloqueantes | Verificado | busqueda `TODO/FIXME` sin resultados en rutas principales |

## Verificaciones ejecutadas

```powershell
python -m ruff check apps src tests
```

Resultado:

```text
All checks passed!
```

```powershell
python -m compileall apps src tests
```

Resultado:

```text
PASS
```

```powershell
python -m pytest -q
```

Resultado:

```text
16 passed, 3 skipped
```

Observacion:

- Las 3 pruebas omitidas son integraciones PostgreSQL existentes que requieren `MONITORING_TEST_DATABASE_URL`.

```powershell
git diff --check
```

Resultado:

```text
PASS
```

## Supuestos

- Monitoring no implementa logica de canales de notificacion; solo publica alertas.
- `POST /api/v1/kpis` queda retirado. El contrato final usa `POST /api/v1/kpi-trackings`.
- El PR de Docs va hacia `main` porque el repositorio `design-software-docs` no tiene rama remota `develop`.

## Resultado QA sugerido

Estado: LISTO PARA PR Y VALIDACION TECNICA.

QA y arquitectura deben validar:

- `/api/v1/ready` con BD y broker reales;
- logs JSON en ambiente QA;
- exportacion OTLP al Collector;
- pipeline CI;
- replay de Outbox;
- DLQ de Monitoring;
- flujo E2E con base y broker reales.
