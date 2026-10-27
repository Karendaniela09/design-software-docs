# Runbook — actors-service

> Estado: 🟢 Estable | Última actualización: 2026-06-20

Servicio fuente de verdad sobre instructores, aprendices y empresas del proceso formativo SENA. Gestiona contratos, competencias, disponibilidad, etapas productivas y visitas empresariales.

---

## Healthcheck

| Endpoint | Respuesta esperada | SLO |
|----------|--------------------|-----|
| `GET /health` | `200 { "status": "ok" }` | < 200 ms |
| `GET /health/db` | `200` cuando `actors_db` (PostgreSQL) acepta conexiones | < 500 ms |

**Verificación manual:**

```bash
curl -sf http://actors-service:8006/health | jq .
curl -sf http://actors-service:8006/health/db | jq .
```

**SLO de disponibilidad:** 99% mensual (máximo ~7.3 h de downtime/mes).

**Nota operativa:** `scheduling-service` consulta instructores síncronamente al crear sesiones. Una degradación de este servicio bloquea la creación de horarios en tiempo real.

---

## Variables de entorno requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | Cadena de conexión PostgreSQL a `actors_db` | `postgresql://user:pass@host:5432/actors_db` |
| `DATABASE_POOL_MIN` | Conexiones mínimas en el pool | `2` |
| `DATABASE_POOL_MAX` | Conexiones máximas en el pool | `10` |
| `IAM_SERVICE_URL` | URL base de `iam-service` para validación de JWT | `http://iam-service:8001` |
| `ACADEMIC_MANAGEMENT_SERVICE_URL` | URL base de `academic-management-service` | `http://academic-management-service:8003` |
| `REFERENCE_DATA_SERVICE_URL` | URL base de `reference-data-service` | `http://reference-data-service:8002` |
| `SPRING_RABBITMQ_HOST` | Host de RabbitMQ (ADR-001) | `rabbitmq` |
| `SPRING_RABBITMQ_USERNAME` / `SPRING_RABBITMQ_PASSWORD` | Credenciales de RabbitMQ | (secreto) |
| `ACTORS_OUTBOX_ENABLED` | Activa el despachador del outbox hacia RabbitMQ. Por defecto `false`: los eventos se guardan igual y se entregan al activarlo. Mismo valor funcional en los 4 ambientes una vez que la tabla tiene las columnas de HU-ACT-022 | `false` |
| `ACTORS_EVENTS_EXCHANGE` | Exchange topic de los eventos propios | `actors-events` |
| `ACTORS_IAM_CONSUMER_ENABLED` | Activa el consumidor de eventos de IAM | `false` |
| `IAM_EVENTS_EXCHANGE` | Exchange de eventos de IAM a consumir | `iam-events` |
| `ACTORS_IAM_QUEUE` / `ACTORS_IAM_DLX` / `ACTORS_IAM_DLQ` | Cola de entrada, exchange de mensajes fallidos y cola de mensajes fallidos del consumidor de IAM | `actors-service.iam` / `actors-iam-dlx` / `actors-events.dlq` |
| `JWT_SECRET` | Clave de verificación de tokens JWT | (secreto) |
| `PORT` | Puerto de escucha del servicio | `8006` |
| `LOG_LEVEL` | Nivel de logging | `info` |
| `ALERT_WEBHOOK_URL` | Webhook para alertas operativas | `https://hooks.slack.com/...` |

**Variables no requeridas:** Redis no es utilizado por este servicio.

---

## Alertas críticas

| Alerta | Condición | Severidad | Acción inmediata |
|--------|-----------|-----------|------------------|
| BD no responde | Timeout en `actors_db` > 5 s o `/health/db` retorna 5xx | P0 | Ver [Falla de base de datos](#falla-de-base-de-datos) |
| Instructores no encontrados masivamente | Error 404 masivo desde `scheduling-service` al consultar instructores activos | P1 | Verificar integridad: `SELECT COUNT(*) FROM instructor WHERE is_active = true` |
| Mensaje en DLQ de actors-events | Mensaje en `actors-events.dlq` sin procesar > 5 min | P1 | Revisar DLQ; ver [Mensajes en Dead Letter Queue](#mensajes-en-dead-letter-queue) |
| Desincronización con iam-service | Evento `iam.user.created` no procesado; actor sin registro en actors-service | P1 | Verificar la cola `ACTORS_IAM_QUEUE` y la DLQ en RabbitMQ (consumidor activo, mensajes sin reconocer) |
| Competencias marcadas `requires_review` en masa | Lote de `competency_assignment.requires_review = true` sin atender > 24 h | P2 | Notificar coordinadores para revisión manual |
| Latencia alta en `/instructors/available` | P95 > 300 ms | P2 | Verificar índice `competency_id WHERE is_active = true`; ver [Consulta de disponibilidad lenta](#consulta-de-disponibilidad-lenta) |
| Servicio no responde | `/health` retorna 5xx o sin respuesta > 1 min | P0 | Reiniciar pod/contenedor; revisar logs de arranque |
| `ActorsHighErrorRate` | Respuestas 4xx/5xx de actors-service por encima del 5 % durante 2 minutos (sin contar `/actuator`) | P2 | Ver [Tasa de error alta en actors-service](#tasa-de-error-alta-en-actors-service) |

---

## Procedimientos comunes

### Transferir manualmente un aprendiz a una ficha diferente

Usar cuando el aprendiz fue matriculado en la ficha incorrecta o cuando se aprueba un traslado formal.

**Precondición:** Confirmar que existe la ficha destino en `academic-management-service`.

```sql
-- 1. Identificar el registro de inscripción activo del aprendiz
SELECT id, learner_id, ficha_id, stage, enrollment_date, is_current
FROM learner_ficha_enrollment
WHERE learner_id = '<LEARNER_UUID>'
  AND is_current = true;

-- 2. Cerrar la inscripción actual (dentro de una transacción)
BEGIN;

UPDATE learner_ficha_enrollment
SET
    is_current      = false,
    completion_date = CURRENT_DATE,
    transfer_reason = 'Traslado manual por operaciones — <MOTIVO>'
WHERE learner_id   = '<LEARNER_UUID>'
  AND is_current   = true;

-- 3. Crear la nueva inscripción en la ficha destino
INSERT INTO learner_ficha_enrollment
    (id, learner_id, ficha_id, stage, enrollment_date, is_current, transfer_reason, created_at)
VALUES
    (gen_random_uuid(),
     '<LEARNER_UUID>',
     '<FICHA_DESTINO_UUID>',
     'LECTURE',        -- ajustar a INDUCTION o PRODUCTIVE según corresponda
     CURRENT_DATE,
     true,
     'Traslado desde ficha <FICHA_ORIGEN_UUID>',
     NOW());

-- 4. Registrar en bitácora de actividad
INSERT INTO activity_log
    (id, actor_type, actor_id, event_type, description, previous_value, new_value, recorded_by, recorded_at)
VALUES
    (gen_random_uuid(),
     'LEARNER',
     '<LEARNER_UUID>',
     'FICHA_TRANSFERRED',
     'Traslado manual de ficha por operaciones',
     '<FICHA_ORIGEN_UUID>',
     '<FICHA_DESTINO_UUID>',
     NULL,   -- NULL = evento del sistema; reemplazar por UUID del operador si disponible
     NOW());

COMMIT;
```

**Verificar resultado:**

```sql
SELECT id, ficha_id, stage, enrollment_date, is_current
FROM learner_ficha_enrollment
WHERE learner_id = '<LEARNER_UUID>'
ORDER BY created_at DESC
LIMIT 3;
```

**Post-acción:** Notificar a `scheduling-service` si el aprendiz tenía sesiones programadas en la ficha anterior. Publicar el evento `actors.learner.enrolled` manualmente si el sistema no lo dispara automáticamente.

---

### Reactivar un instructor desactivado

Usar cuando un instructor fue marcado inactivo por error o cuando regresa al servicio activo tras una ausencia.

**Precondición:** Verificar con el área de talento humano que la reactivación está autorizada y que existe un contrato vigente o nuevo contrato a crear.

```sql
-- 1. Verificar estado actual del instructor
SELECT id, full_name, is_active, updated_at
FROM instructor
WHERE id = '<INSTRUCTOR_UUID>';

-- 2. Verificar contratos existentes
SELECT id, contract_type, start_date, end_date, is_current
FROM instructor_contract
WHERE instructor_id = '<INSTRUCTOR_UUID>'
ORDER BY start_date DESC;

-- 3. Reactivar instructor y marcar contrato como vigente (transacción)
BEGIN;

UPDATE instructor
SET
    is_active  = true,
    updated_at = NOW()
WHERE id = '<INSTRUCTOR_UUID>';

-- Si el contrato anterior sigue vigente, reactivarlo
UPDATE instructor_contract
SET is_current = true
WHERE instructor_id = '<INSTRUCTOR_UUID>'
  AND id = '<CONTRACT_UUID>';
-- Si se debe crear un contrato nuevo, usar INSERT en lugar del UPDATE anterior.

-- Reactivar asignaciones de competencia que quedaron en SUSPENDIDA
-- (las asignaciones se suspenden automáticamente al procesar iam.user.deactivated)
UPDATE competency_assignment
SET is_active = true
WHERE instructor_id = '<INSTRUCTOR_UUID>'
  AND is_active = false;
-- ATENCIÓN: revisar que solo se reactiven las competencias válidas; excluir las revocadas.

-- Registrar en bitácora
INSERT INTO activity_log
    (id, actor_type, actor_id, event_type, description, previous_value, new_value, recorded_by, recorded_at)
VALUES
    (gen_random_uuid(),
     'INSTRUCTOR',
     '<INSTRUCTOR_UUID>',
     'STATUS_CHANGED',
     'Reactivación manual por operaciones',
     'is_active=false',
     'is_active=true',
     NULL,
     NOW());

COMMIT;
```

**Verificar resultado:**

```sql
SELECT i.id, i.full_name, i.is_active,
       COUNT(ca.id) FILTER (WHERE ca.is_active = true) AS competencias_activas
FROM instructor i
LEFT JOIN competency_assignment ca ON ca.instructor_id = i.id
WHERE i.id = '<INSTRUCTOR_UUID>'
GROUP BY i.id, i.full_name, i.is_active;
```

**Post-acción:** Confirmar con `iam-service` que el usuario correspondiente también fue reactivado (`is_active = true` en `iam-service`). Si no, la reactivación en actors-service no tendrá efecto funcional porque el JWT seguirá siendo rechazado.

---

## Escenarios de falla

### Falla de base de datos

**Síntoma:** `/health/db` retorna 503; todas las peticiones al API retornan 500; logs muestran `connection timeout` o `too many connections`.

**Diagnóstico:**

```bash
# Verificar conectividad desde el pod del servicio
psql "$DATABASE_URL" -c "SELECT 1;"

# Revisar conexiones activas en la BD
psql "$DATABASE_URL" -c "
  SELECT count(*), state
  FROM pg_stat_activity
  WHERE datname = 'actors_db'
  GROUP BY state;"
```

**Acciones:**

1. Si el problema es agotamiento de conexiones (`too many connections`): reducir `DATABASE_POOL_MAX` y reiniciar el servicio. Verificar si hay conexiones zombies con `pg_terminate_backend`.
2. Si PostgreSQL no responde: escalar a DBA de guardia. El servicio puede reiniciarse pero no recuperará hasta que la BD esté disponible.
3. Si la BD está disponible pero el servicio no conecta: verificar `DATABASE_URL` en las variables de entorno del pod.

---

### Mensajes en Dead Letter Queue

**Síntoma:** Alerta de mensaje en `actors-events.dlq`; actor no fue creado tras evento `iam.user.created`; o cambio de estado de competencia no se reflejó.

**Diagnóstico:**

```bash
# Ver cuántos mensajes hay en la DLQ y leer uno sin consumirlo (consola de gestión de RabbitMQ)
rabbitmqctl list_queues name messages_ready | grep actors-events.dlq
# Cola > Get messages (Ack mode: Reject requeue true), o con la API de gestión:
curl -s -u "$RABBITMQ_USER:$RABBITMQ_PASSWORD" -X POST "http://rabbitmq:15672/api/queues/%2F/actors-events.dlq/get" \
  -H 'content-type: application/json' -d '{"count":1,"ackmode":"ack_requeue_true","encoding":"auto"}'
```

**Acciones:**

1. Identificar el `event_type` y `event_id` del mensaje fallido.
2. Determinar la causa: payload malformado, BD no disponible en el momento del procesamiento, referencia externa inválida.
3. Si fue un fallo transitorio (BD no disponible): reproducir el mensaje con `POST /api/v1/ops/actors/iam-dlq/replay-one` (un mensaje por llamada; requiere `ACT_INSTRUCTOR_MANAGE`). La lógica de idempotencia usa `event_id` para evitar duplicados.
4. Si el payload es inválido: corregir manualmente el estado en la BD según el procedimiento correspondiente y descartar el mensaje de la DLQ.

---

### Eventos de actors pendientes o muertos en el outbox

**Síntoma:** un consumidor (audit, monitoring, scheduling) no recibe eventos de actors; o hay filas `DEAD` en `actors_tracking.company_visit_outbox`.

**Diagnóstico:**

```bash
# Conteo por estado (pending, sending, published, dead)
curl -s -H "Authorization: Bearer $TOKEN" http://actors-api:8080/api/v1/ops/actors/outbox/status
```

```sql
SELECT status, count(*), min(created_at) FROM actors_tracking.company_visit_outbox
 WHERE published_at IS NULL GROUP BY status;
SELECT event_id, event_type, attempts, last_error FROM actors_tracking.company_visit_outbox
 WHERE status = 'DEAD' ORDER BY created_at;
```

**Acciones:**

1. Si crece `pending` y nada se publica, comprobar que `ACTORS_OUTBOX_ENABLED=true`, que RabbitMQ responde y que el exchange `actors-events` existe con un binding hacia los consumidores. Con el interruptor en `false` las filas se acumulan sin perderse.
2. Un mensaje sin binding se devuelve como "no enrutable" y la fila se reintenta; corregir el binding y esperar el siguiente reintento.
3. Para una fila `DEAD`, corregir la causa (`last_error`) y reactivarla con `POST /api/v1/ops/actors/outbox/{eventId}/replay`. Los consumidores deduplican por `event_id`.

---

### Tasa de error alta en actors-service

**Síntoma:** se dispara la alerta `ActorsHighErrorRate` (Prometheus y regla de Grafana `actors-r3-errors`): más del 5 % de las respuestas son 4xx o 5xx durante 2 minutos.

**Dónde mirar (HU-ACT-024):**

- **Métricas RED.** `actors-api` expone `/actuator/prometheus` en el puerto de gestión **8081**, sin mTLS y solo dentro de la red de Docker (no se publica ni pasa por el edge; el negocio sigue en 8080 con mTLS). Prometheus lo lee con el job `actors-service`. Las series son `http_server_requests_seconds_count` y `_bucket`, etiquetadas por `application`, `uri` (plantilla de la ruta, nunca el id real), `method` y `status`.
- **Tablero.** `Actors R3 · Alta de aprendiz (RED)` en Grafana (`observability/grafana/dashboards/actors-r3.json` de `docker-infra`): tasa, errores y p95 por ruta, y las tres rutas más usadas.
- **Trazas.** Tempo, con el `traceId` de la petición; las consultas JDBC aparecen como spans dentro de la traza.
- **Logs.** Una línea JSON por evento con `timestamp`, `level`, `logger`, `message`, `service`, `correlation_id` (el trace id W3C, el mismo que llega desde el MFE en `traceparent`), `span_id` y `stack_trace`. Filtrar por `correlation_id` en Loki une las capas de una misma petición. Nunca se registran tokens ni documentos.

**Acciones:**

1. En el tablero, ver qué ruta concentra los errores y si son 4xx (clientes: token vencido o sin permiso, validación) o 5xx (servicio o base de datos).
2. Con un `correlation_id` de una petición fallida, abrir su traza en Tempo y filtrar los logs por ese valor.
3. 401/403 en bloque: revisar `IAM_JWKS_URL` (o el alias compatible `IAM_JWKS_URI`), `IAM_JWT_ISSUER` y que iam-service responda. 5xx en bloque: ver [Falla de base de datos](#falla-de-base-de-datos) y los eventos del outbox si el fallo es al guardar un evento.
4. Si el aviso es por pruebas con entradas inválidas a propósito, la alerta vuelve a normal sola cuando el ratio baja del 5 %.

---

### Consulta de disponibilidad lenta

**Síntoma:** `GET /instructors/available?competency_id=<UUID>` supera 300 ms P95; scheduling-service reporta timeouts al crear sesiones.

**Diagnóstico:**

```sql
-- Verificar que el índice parcial está siendo usado
EXPLAIN ANALYZE
SELECT i.id, i.full_name
FROM instructor i
JOIN competency_assignment ca ON ca.instructor_id = i.id
WHERE ca.competency_id = '<COMPETENCY_UUID>'
  AND ca.is_active = true
  AND i.is_active = true;
```

**Acciones:**

1. Si el índice no está siendo usado: ejecutar `ANALYZE competency_assignment;` y `ANALYZE instructor;`.
2. Si el índice está corrompido: `REINDEX INDEX CONCURRENTLY idx_competency_assignment_active;`
3. Si la tabla tiene millones de filas sin vaciar: ejecutar `VACUUM ANALYZE competency_assignment;`

---

### Desincronización de actor con iam-service

**Síntoma:** Usuario existe en `iam-service` pero no tiene registro en `instructor` ni en `learner`; el API retorna 404 al intentar acceder por `user_id`.

**Causa probable:** El evento `iam.user.created` no fue procesado (fallo transitorio, servicio caído al momento del evento, mensaje expiró en la DLQ).

**Acción:** Crear el registro de actor manualmente a partir de los datos disponibles en `iam-service`, luego registrar el evento en `activity_log` con `event_type = 'MANUAL_SYNC'`. No reinventar el `user_id`; usar exactamente el UUID que proviene de `iam-service`.

---

## Escalamiento

| Nivel | Condición para escalar | A quién |
|-------|------------------------|---------|
| **L1 — Operaciones** | Servicio caído; latencia alta; mensajes en DLQ; fallo en healthcheck | Equipo de guardia de plataforma |
| **L2 — Ingeniería backend** | Corrupción de datos en `instructor` o `learner`; fallo en migración de BD; comportamiento inesperado tras deploy | Equipo backend responsable del servicio |
| **L3 — DBA** | Problemas de rendimiento en PostgreSQL; corrupción de índices; necesidad de `pg_terminate_backend` masivo; fallo en replicación | DBA de guardia |
| **L4 — Dominio** | Decisiones sobre reglas de negocio: si se puede o no reactivar un instructor, si un traslado de ficha es válido, conflictos de competencias | Coordinador académico o área de talento humano |

**Canal de alertas:** Configurar `ALERT_WEBHOOK_URL` con el webhook del canal de operaciones en Slack/Teams.

**Retención de PII:** Datos de `instructor` y `learner` deben eliminarse 5 años después de su desvinculación o graduación. Coordinar con el equipo de privacidad antes de cualquier borrado masivo.
