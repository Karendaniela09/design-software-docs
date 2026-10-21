# Entrega Develop HU-MON-003 / HU-03-monitoring

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

Fecha: 2026-10-14

Desarrollador: Kevin Andrey Culma Gomez

## Repositorios y ramas revisadas

| Repositorio | Rama | Estado |
| --- | --- | --- |
| `design-software-monitoring-service` | `hu-03-dev` | Modificado para PR hacia `develop` |
| `design-software-docs` | `hu-06-dev` | Modificado para alinear contrato async del alert-worker |
| `design-software-monitoring-db` | `hu-09-dev` | Revisado como dependencia de HU-MON-001, sin cambios nuevos |

## Pull requests creados

| Repositorio | Rama origen | Rama destino | PR | Commit |
| --- | --- | --- | --- | --- |
| `design-software-monitoring-service` | `hu-03-dev` | `develop` | https://github.com/code-sena/design-software-monitoring-service/pull/4 | `d6fc3f1` |
| `design-software-docs` | `hu-06-dev` | `main` | https://github.com/code-sena/design-software-docs/pull/288 | `273e272` |

Antes de implementar se actualizaron las ramas padre del servicio:

- `develop`
- `qa`
- `staging`
- `main`

La rama `hu-03-dev` se creo desde `hu-02-dev`, porque HU-MON-003 depende de la API y persistencia ya implementadas en HU-MON-001 y HU-MON-002.

## Alcance implementado

La implementacion se realizo para HU-MON-003: construir el `alert-worker` de Monitoring.

El objetivo principal fue consumir eventos de dominio, evaluar KPIs y umbrales, persistir mediciones y alertas de forma idempotente, e insertar eventos `monitoring.alert.triggered` en `monitoring.outbox` dentro de la misma transaccion que `generated_alert`.

## Documentacion fuente revisada

- `design-software-docs/09-microservices/services/08-monitoring-service/components/alert-worker/contract.md`
- `design-software-docs/09-microservices/services/08-monitoring-service/events.md`
- `design-software-docs/09-microservices/event-catalog.md`
- `design-software-docs/05-architecture/decisions/records/ADR-001-message-broker.md`
- `design-software-docs/09-microservices/services/08-monitoring-service/data-model.md`

## Cambios realizados

### 1. Alert-worker real

Archivos:

- `design-software-monitoring-service/apps/alert_worker/main.py`
- `design-software-monitoring-service/src/monitoring/application/usecase/alert_worker.py`
- `design-software-monitoring-service/src/monitoring/domain/model/event.py`

Cambios:

- Se reemplazo el skeleton del worker.
- Se soportan eventos:
  - `academic.ficha.opened`
  - `academic.ficha.closed`
  - `scheduling.schedule.published`
  - `scheduling.class_session.cancelled`
  - `actors.company_visit.completed`
  - `monitoring.kpi.tick`
- Se mantiene correlacion con `correlation_id`.
- Se conserva trazabilidad con `event_id` y `source_event_id`.

### 2. Persistencia transaccional e idempotente

Archivo:

- `design-software-monitoring-service/src/monitoring/adapter/outbound/persistence/repo.py`

Cambios:

- Se agrego metadata SQLAlchemy para `monitoring.outbox`.
- Se agrego `SqlAlchemyAlertWorkerRepository`.
- El worker inserta KPI, alerta y outbox dentro de una misma transaccion.
- La idempotencia evita duplicar alertas por `source_event_id`.
- La medicion equivalente se evita por `ficha_tracking_id`, `kpi_type_id` y `measured_at`.

### 3. Relay Outbox

Archivos:

- `design-software-monitoring-service/src/monitoring/application/usecase/alert_worker.py`
- `design-software-monitoring-service/src/monitoring/adapter/outbound/messaging/amqp.py`

Cambios:

- El relay lee filas pendientes de `monitoring.outbox`.
- Publica al broker.
- Marca `published_at` solo despues de ack del publisher.

### 4. RabbitMQ / AMQP

Archivo:

- `design-software-monitoring-service/src/monitoring/adapter/outbound/messaging/amqp.py`

Cambios:

- Se agrego publisher AMQP con publisher confirms.
- Se agrego consumer con bindings a exchanges de Academic, Scheduling, Actors y Monitoring.
- Se agrego DLQ propia de Monitoring con routing key `monitoring.alert-worker.dlq`.
- Se agrego dependencia `pika`.

### 5. Contrato async de Docs

Archivo:

- `design-software-docs/09-microservices/services/08-monitoring-service/components/alert-worker/contract.md`

Cambios:

- Se alinearon los eventos consumidos con `events.md` y la HU.
- Se documento la idempotencia por `source_event_id` y medicion equivalente.
- Se aclaro que `monitoring.alert.triggered` es el evento principal del worker.

## Criterios de aceptacion revisados

### AC-001 Eventos consumidos

Estado: IMPLEMENTADO.

Evidencia:

- `SUPPORTED_EVENT_TYPES` en `alert_worker.py`.
- Bindings AMQP en `amqp.py`.

### AC-002 Inicializar `ficha_tracking` con `academic.ficha.opened`

Estado: IMPLEMENTADO.

Evidencia:

- `initialize_ficha_tracking()` en `SqlAlchemyAlertWorkerRepository`.
- `test_ficha_opened_initializes_tracking_generates_alert_and_outbox_once`.

### AC-003 Registrar mediciones KPI

Estado: IMPLEMENTADO.

Evidencia:

- `record_kpi_evaluations()` inserta en `monitoring.kpi_tracking`.
- Soporta asistencia, avance curricular, riesgo de desercion y etapa productiva cuando hay datos suficientes.

### AC-004 Persistir alerta al cruzar umbral

Estado: IMPLEMENTADO.

Evidencia:

- `_create_alert_and_outbox()` inserta `generated_alert`.
- Usa `alert_type.default_threshold` y `risk_level`.

### AC-005 Idempotencia ante redelivery

Estado: IMPLEMENTADO.

Evidencia:

- Deduplicacion por `source_event_id` + `alert_type_id`.
- Prueba de redelivery en `tests/test_alert_worker.py`.

### AC-006 Outbox en la misma transaccion

Estado: IMPLEMENTADO.

Evidencia:

- `_create_alert_and_outbox()` inserta `generated_alert` y `outbox` dentro del mismo `session.begin()`.

### AC-007 Relay publica y marca tras ack

Estado: IMPLEMENTADO.

Evidencia:

- `OutboxRelay.publish_pending_once()`.
- Prueba `test_outbox_relay_marks_published_only_after_ack`.

### AC-008 Sin llamada directa a Notification

Estado: IMPLEMENTADO.

Evidencia:

- El worker solo publica `monitoring.alert.triggered` por outbox/AMQP.
- No hay cliente HTTP ni persistencia de entrega de notificaciones.

### AC-009 Backoff y DLQ

Estado: IMPLEMENTADO.

Evidencia:

- `RetryingEventConsumer`.
- `RabbitMqDeadLetterPublisher`.
- Prueba `test_persistent_consumer_failure_goes_to_monitoring_dlq`.

### AC-010 Pruebas

Estado: IMPLEMENTADO.

Evidencia:

- `tests/test_alert_worker.py`.

## Verificaciones ejecutadas

### Pruebas automatizadas

Comando:

```powershell
python -m pytest -q
```

Resultado:

```text
10 passed, 3 skipped
```

Observacion:

- Las 3 pruebas omitidas son integraciones PostgreSQL existentes que requieren `MONITORING_TEST_DATABASE_URL`.

### Compilacion Python

Comando:

```powershell
python -m compileall apps src tests
```

Resultado:

```text
PASS
```

### Validacion de whitespace

Comando:

```powershell
git diff --check
```

Resultado:

```text
PASS
```

## Dependencias bloqueantes verificadas

En `design-software-monitoring-db` existen las tablas requeridas:

- `monitoring.generated_alert`
- `monitoring.kpi_tracking`
- `monitoring.outbox`

No se requirieron migraciones nuevas para HU-MON-003.

## Nota de contrato

`monitoring.kpi.threshold_breached` permanece documentado en `events.md` y en el catalogo global, pero el contrato especifico del `alert-worker` define como evento producido principal `monitoring.alert.triggered`. Por eso esta entrega publica `monitoring.alert.triggered`.

## Pendientes para QA

- Ejecutar pruebas de integracion con PostgreSQL real usando `MONITORING_TEST_DATABASE_URL`.
- Probar consumer y relay con RabbitMQ real usando `AMQP_URL`.
- Validar routing keys y DLQ en ambiente QA.
- Validar que Notification y Audit consuman `monitoring.alert.triggered`.

## Resultado QA sugerido

Estado: LISTO PARA PR Y VALIDACION TECNICA.

Ramas:

- `design-software-monitoring-service` -> `hu-03-dev`
- `design-software-docs` -> `hu-06-dev`
