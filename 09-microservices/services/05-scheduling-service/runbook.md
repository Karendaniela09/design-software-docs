# Runbook — scheduling-service

> Estado: 🟢 Estable | Última actualización: 2026-06-20

---

## Healthcheck

Este servicio tiene tres componentes desplegables independientes. Cada uno debe verificarse por separado.

### schedules-api (puerto 8005)

```bash
curl -s http://schedules-api:8005/health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "component": "schedules-api",
  "db": "ok",
  "redis": "ok",
  "outbox_relay": "ok",
  "timestamp": "2026-06-20T00:00:00Z"
}
```

| Endpoint | Respuesta esperada | SLO |
|----------|--------------------|-----|
| `GET /health` | `200 { "status": "ok" }` | < 200 ms |
| `GET /health/ready` | `200` cuando `scheduling_db`, Redis y dependencias son accesibles | < 500 ms |

### conflict-validator-worker

El worker no expone un puerto HTTP propio. Verificar su actividad mediante:

1. **Heartbeat en Redis:**
   ```bash
   redis-cli GET scheduling:worker:conflict-validator:heartbeat
   # Debe retornar un timestamp actualizado en los últimos 60 s
   ```
2. **Logs del pod:**
   ```bash
   kubectl logs <pod-conflict-validator-worker> --tail=50
   ```
3. **Alerta de silencio:** Si no hay procesamiento de mensajes en > 5 min, el worker se considera detenido (alerta P1).

### scheduling-engine-workflow

El orquestador de workflow no expone un endpoint HTTP. Verificar mediante:

1. **Estado de workflows activos** (a través de la interfaz del motor de workflow configurado):
   ```bash
   # Ejemplo con Temporal CLI:
   temporal workflow list --namespace scheduling --status Running
   ```
2. **Logs del pod:**
   ```bash
   kubectl logs <pod-scheduling-engine-workflow> --tail=50
   ```
3. **Workflows colgados:** Si un workflow permanece en estado `Running` > 10 min sin progreso, revisar logs para detectar bloqueos en llamadas a dependencias.

---

## Variables de entorno requeridas

### schedules-api

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `PORT` | Puerto de escucha | `8005` |
| `DATABASE_URL` | Cadena de conexión a `scheduling_db` (PostgreSQL) | `postgresql://user:pass@host:5432/scheduling_db` |
| `DATABASE_POOL_MIN` | Conexiones mínimas en pool | `2` |
| `DATABASE_POOL_MAX` | Conexiones máximas en pool | `20` |
| `REDIS_URL` | URL de Redis para read models (ADR-002) | `redis://redis-host:6379` |
| `REDIS_READ_MODEL_TTL_S` | TTL de las claves de read model en segundos | `30` |
| `IAM_SERVICE_URL` | URL base de `iam-service` | `http://iam-service:8001` |
| `IAM_JWKS_URI` | URI del endpoint JWKS | `http://iam-service:8001/.well-known/jwks.json` |
| `MESSAGE_BROKER_URL` | URL del broker para Outbox relay | `amqp://user:pass@broker:5672` |
| `SCHEDULING_EVENTS_TOPIC` | Topic de publicación de eventos | `scheduling-events` |
| `OUTBOX_POLL_INTERVAL_MS` | Intervalo de polling del relay de Outbox | `2000` |
| `OUTBOX_BATCH_SIZE` | Mensajes procesados por ciclo de polling | `20` |
| `LOG_LEVEL` | Nivel de logging | `info` |
| `NODE_ENV` / `APP_ENV` | Entorno de ejecución | `production` |

### conflict-validator-worker

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | Cadena de conexión a `scheduling_db` | `postgresql://user:pass@host:5432/scheduling_db` |
| `REDIS_URL` | URL de Redis para read models | `redis://redis-host:6379` |
| `MESSAGE_BROKER_URL` | URL del broker para consumir `environment-events` | `amqp://user:pass@broker:5672` |
| `ENVIRONMENT_EVENTS_TOPIC` | Topic de eventos consumidos | `environment-events` |
| `SCHEDULING_EVENTS_TOPIC` | Topic de eventos publicados (`conflict.detected`) | `scheduling-events` |
| `WORKER_HEARTBEAT_INTERVAL_S` | Intervalo de escritura del heartbeat en Redis | `30` |
| `LOG_LEVEL` | Nivel de logging | `info` |

### scheduling-engine-workflow

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | Cadena de conexión a `scheduling_db` | `postgresql://user:pass@host:5432/scheduling_db` |
| `REDIS_URL` | URL de Redis para read models | `redis://redis-host:6379` |
| `ACTORS_SERVICE_URL` | URL base de `actors-service` | `http://actors-service:8006` |
| `TRAINING_ENVIRONMENT_SERVICE_URL` | URL base de `training-environment-service` | `http://training-environment-api:8004` |
| `ACADEMIC_MANAGEMENT_SERVICE_URL` | URL base de `academic-management-service` | `http://academic-management-service:8003` |
| `WORKFLOW_TASK_TIMEOUT_S` | Timeout por tarea individual del workflow | `30` |
| `WORKFLOW_TOTAL_TIMEOUT_S` | Timeout total del workflow de horario | `300` |
| `LOG_LEVEL` | Nivel de logging | `info` |

---

## Alertas críticas

| Alerta | Condición | Severidad | Acción inmediata |
|--------|-----------|-----------|------------------|
| `scheduling_db` inaccesible | Timeout o error de conexión sostenido > 10 s | P0 | Ver procedimiento "Base de datos no responde" |
| Redis inaccesible | Timeout a Redis > 5 s; read models no disponibles | P0 | El servicio no puede validar disponibilidad sin Redis; creación de horarios bloqueada. Ver procedimiento "Redis inaccesible" |
| Mensaje `schedule.published` en DLQ | Registro en `scheduling-events-dlq` con `event_type = scheduling.schedule.published` | P0 | Ver procedimiento "Forzar publicación de mensaje Outbox estancado" |
| Outbox estancado | Registros en tabla `outbox` con `status = PENDING` y `created_at` > 5 min | P0 | Ver procedimiento "Forzar publicación de mensaje Outbox estancado" |
| `conflict-validator-worker` detenido | Sin heartbeat en Redis > 5 min | P1 | Reiniciar el pod; revisar logs; inspeccionar `environment-events.dlq` |
| `scheduling-engine-workflow` colgado | Workflow en estado `Running` > 10 min sin progreso | P1 | Ver procedimiento "Workflow colgado" |
| `actors-service` inaccesible | Error `503` al verificar disponibilidad de instructor | P1 | El workflow usa el read model en Redis si está disponible; si Redis también falla, suspender creación de horarios |
| `training-environment-service` inaccesible | Error `503` al consultar disponibilidad de ambiente | P1 | Igual que el anterior; el read model en Redis es la primera línea de defensa |
| `academic-management-service` inaccesible | Error `503` al consultar ficha o competencias | P1 | Suspender creación de horarios; informar a coordinadores |
| Horario publicado con conflictos activos | `scheduling_db`: `schedule.status = PUBLISHED` con registros en `scheduling_conflict` donde `is_resolved = false` | P1 | Despublicar el horario (cambio manual de estado); re-ejecutar validación de conflictos; notificar coordinadores |
| Read models de Redis desactualizados | Diferencia entre Redis y fuente canónica > 60 s después de un evento de disponibilidad | P2 | Ver procedimiento "Limpiar read models obsoletos en Redis" |

---

## Procedimientos comunes

### Re-ejecutar la validación de conflictos para un horario

Usar cuando se sospecha que el `conflict-validator-worker` procesó un horario con un read model desactualizado, o cuando se quiere forzar la re-validación después de corregir datos.

**Verificar el horario existe y está en estado correcto:**

```sql
-- scheduling_db
SELECT id, ficha_id, period, status, created_at, published_at
FROM schedule
WHERE id = '<uuid-horario>';
```

Un horario en estado `PUBLISHED` es inmutable. Si hay conflictos detectados sobre un horario publicado, se debe crear una nueva versión en `DRAFT`.

**Ver conflictos activos registrados:**

```sql
SELECT sc.id, sc.conflict_type, sc.description, sc.is_resolved, sc.detected_at,
       cs_a.session_date, cs_a.start_time, cs_a.end_time
FROM scheduling_conflict sc
JOIN class_session cs_a ON cs_a.id = sc.session_a_id
WHERE sc.schedule_id = '<uuid-horario>'
  AND sc.is_resolved = false
ORDER BY sc.detected_at;
```

**Disparar re-validación:** Publicar un mensaje de comando al worker para que re-procese el horario:

```bash
# Publicar comando de revalidación al exchange del worker
rabbitmqadmin publish exchange=scheduling-commands routing_key=conflict.validate \
  payload='{"schedule_id": "<uuid-horario>", "requested_by": "<uuid-operador>", "reason": "manual_revalidation"}'
```

**Verificar que el worker procesó el comando:**

```bash
kubectl logs <pod-conflict-validator-worker> --tail=50 | grep '<uuid-horario>'
```

**Si el worker no puede recibir comandos directos**, ejecutar la validación mediante SQL forzando la re-evaluación:

```sql
-- Marcar conflictos anteriores como resueltos para forzar re-detección limpia
UPDATE scheduling_conflict
SET is_resolved = true
WHERE schedule_id = '<uuid-horario>'
  AND is_resolved = false;
```

A continuación reiniciar el worker para que re-consuma el estado actual.

---

### Forzar publicación de un mensaje Outbox estancado

Usar cuando un horario fue publicado (estado `PUBLISHED` en `scheduling_db`) pero el evento `scheduling.schedule.published` no llegó a los consumidores. El relay de Outbox puede estar detenido o haber fallado silenciosamente.

**Identificar registros estancados en la tabla `outbox`:**

```sql
-- scheduling_db
SELECT id, event_id, event_type, status, created_at, published_at,
       now() - created_at AS age
FROM outbox
WHERE status IN ('PENDING', 'FAILED')
ORDER BY created_at ASC;
```

**Verificar el estado del relay** (proceso interno de `schedules-api`):

```bash
kubectl logs <pod-schedules-api> --tail=100 | grep -i "outbox"
```

**Si el relay está activo pero los mensajes siguen estancados** (status `FAILED`):

1. Revisar el payload del registro de `outbox` para descartar malformación:
   ```sql
   SELECT payload FROM outbox WHERE id = '<uuid-outbox>';
   ```
2. Si el payload es válido, restablecer el status a `PENDING` para que el relay lo reintente:
   ```sql
   UPDATE outbox
   SET status = 'PENDING', published_at = NULL
   WHERE id = '<uuid-outbox>'
     AND status = 'FAILED';
   ```

**Si el relay está detenido** (no hay actividad en logs > 2 min):

1. Reiniciar el pod de `schedules-api`:
   ```bash
   kubectl rollout restart deployment/schedules-api
   ```
2. El relay retoma el polling automáticamente al arrancar y procesa todos los registros `PENDING`.
3. Verificar en los logs que el mensaje fue publicado:
   ```bash
   kubectl logs <pod-schedules-api> --tail=50 | grep "outbox.*published"
   ```
4. Confirmar en la tabla `outbox`:
   ```sql
   SELECT status, published_at FROM outbox WHERE event_id = '<event-id>';
   -- Debe mostrar status = 'PUBLISHED' y published_at con timestamp
   ```

**Publicación manual de emergencia** (solo si el relay no puede recuperarse):

```bash
# Extraer el payload del registro de outbox
# Publicar directamente al topic scheduling-events
rabbitmqadmin publish exchange=scheduling-events routing_key=scheduling-events \
  payload='<payload-json-del-outbox>'
```

Marcar el registro como publicado manualmente:

```sql
UPDATE outbox
SET status = 'PUBLISHED', published_at = now()
WHERE id = '<uuid-outbox>';
```

Los consumidores aplican deduplicación por `event_id`, por lo que un reenvío no produce efectos duplicados.

---

### Limpiar read models obsoletos en Redis

Usar cuando el read model de disponibilidad de ambientes o instructores en Redis contiene datos desactualizados respecto a las fuentes canónicas (`training-environment-service`, `actors-service`).

**Identificar las claves afectadas:**

```bash
# Patrón de claves de read model de ambientes
redis-cli KEYS "scheduling:readmodel:environment:*"

# Patrón de claves de read model de instructores
redis-cli KEYS "scheduling:readmodel:instructor:*"
```

**Inspeccionar una clave específica:**

```bash
redis-cli GET "scheduling:readmodel:environment:<uuid-ambiente>"
# Comparar con la respuesta de la API de training-environment-service
curl -s -H "Authorization: Bearer <TOKEN>" \
  "http://training-environment-api:8004/environments/<uuid-ambiente>/availability?date=<YYYY-MM-DD>"
```

**Limpiar las claves de un ambiente específico** (el worker las regenerará al próximo evento o consulta):

```bash
redis-cli DEL "scheduling:readmodel:environment:<uuid-ambiente>"
```

**Limpiar todos los read models de ambientes** (operación de alto impacto — ejecutar solo en ventana de mantenimiento):

```bash
# Con redis-cli y pipeline
redis-cli KEYS "scheduling:readmodel:environment:*" | xargs redis-cli DEL
```

**Forzar repoblado desde snapshot de `training-environment-service`:**

El endpoint de snapshot reconstruye el read model completo para todos los ambientes activos. Llamarlo desde el pod del worker:

```bash
kubectl exec -it <pod-conflict-validator-worker> -- \
  curl -s -H "Authorization: Bearer <TOKEN>" \
  -X POST "http://training-environment-api:8004/internal/snapshot/environments"
```

**Verificar que las claves fueron reconstruidas:**

```bash
redis-cli TTL "scheduling:readmodel:environment:<uuid-ambiente>"
# Debe retornar un valor positivo (TTL en segundos, configurado en REDIS_READ_MODEL_TTL_S)
```

---

## Escenarios de falla

### Base de datos no responde

**Síntomas:** `GET /health` retorna `500` o `{ "db": "unreachable" }`; toda creación y consulta de horarios falla.

**Pasos:**

1. Verificar estado del pod de la base de datos:
   ```bash
   kubectl get pods -n <namespace> | grep scheduling-db
   kubectl logs <pod-scheduling-db> --tail=50
   ```
2. Verificar conectividad desde los pods del servicio:
   ```bash
   kubectl exec -it <pod-schedules-api> -- nc -zv <db-host> 5432
   ```
3. Si la base de datos está caída, seguir el runbook de recuperación de PostgreSQL del equipo de infraestructura. `scheduling_db` requiere consistencia fuerte — no operar en modo degradado sin base de datos.
4. Orden de reinicio una vez restaurada la base de datos:
   ```bash
   kubectl rollout restart deployment/schedules-api
   kubectl rollout restart deployment/conflict-validator-worker
   kubectl rollout restart deployment/scheduling-engine-workflow
   ```
5. Verificar que los registros en `outbox` con `status = PENDING` son procesados por el relay tras el reinicio.

---

### Redis inaccesible

**Síntomas:** `GET /health` retorna `{ "redis": "unreachable" }`; el workflow no puede consultar read models; las validaciones de disponibilidad fallan.

**Pasos:**

1. Verificar estado del pod de Redis:
   ```bash
   kubectl get pods -n <namespace> | grep redis
   redis-cli -h <redis-host> ping
   ```
2. Si Redis está caído, los read models se pierden. El servicio no puede crear horarios de forma confiable en este estado.
3. Una vez Redis esté disponible, forzar repoblado de read models:
   ```bash
   # Desde el pod del worker, llamar al snapshot de training-environment-service
   kubectl exec -it <pod-conflict-validator-worker> -- \
     curl -X POST "http://training-environment-api:8004/internal/snapshot/environments" \
     -H "Authorization: Bearer <TOKEN>"
   ```
4. Reiniciar los pods del servicio para restablecer las conexiones al pool de Redis:
   ```bash
   kubectl rollout restart deployment/schedules-api
   kubectl rollout restart deployment/conflict-validator-worker
   ```

---

### conflict-validator-worker detenido

**Síntomas:** Sin heartbeat en Redis (`scheduling:worker:conflict-validator:heartbeat`) > 5 min; mensajes de `environment-events` no se procesan; read models no se actualizan.

**Pasos:**

1. Revisar logs del pod:
   ```bash
   kubectl logs <pod-conflict-validator-worker> --tail=100
   ```
2. Verificar si hay mensajes acumulados en `environment-events` sin procesar:
   ```bash
   rabbitmqadmin list queues name messages consumers | grep environment-events
   ```
3. Reiniciar el pod:
   ```bash
   kubectl rollout restart deployment/conflict-validator-worker
   ```
4. Confirmar que el heartbeat se restablece:
   ```bash
   redis-cli GET scheduling:worker:conflict-validator:heartbeat
   ```
5. Verificar que los mensajes acumulados en `environment-events` se procesan:
   ```bash
   kubectl logs <pod-conflict-validator-worker> --tail=100 | grep "environment.availability\|environment.maintenance"
   ```
6. Inspeccionar `environment-events.dlq` por si el worker falló al procesar algún mensaje:
   ```bash
   rabbitmqadmin get queue=environment-events.dlq count=10
   ```

---

### Workflow colgado

**Síntomas:** Un workflow de creación de horario permanece en estado `Running` > 10 min; el coordinador reporta que la creación de horario no termina.

**Pasos:**

1. Identificar el workflow bloqueado:
   ```bash
   temporal workflow list --namespace scheduling --status Running
   ```
2. Ver el historial del workflow para identificar la tarea que no avanza:
   ```bash
   temporal workflow show --workflow-id <workflow-id> --namespace scheduling
   ```
3. Verificar si la tarea bloqueada es una llamada a una dependencia (actors-service, training-environment-service, academic-management-service):
   ```bash
   kubectl logs <pod-scheduling-engine-workflow> --tail=200 | grep '<workflow-id>'
   ```
4. Si la dependencia está caída, restaurarla primero. El workflow reintentará automáticamente según su política de reintentos.
5. Si el workflow no puede completarse (dependencia irrecuperable), terminarlo y notificar al coordinador para que reintente la creación:
   ```bash
   temporal workflow terminate --workflow-id <workflow-id> --namespace scheduling \
     --reason "Dependencia irrecuperable — reintento manual requerido"
   ```
6. Verificar que el registro de `schedule` en `scheduling_db` no quedó en estado inconsistente:
   ```sql
   SELECT id, status, updated_at FROM schedule
   WHERE id = '<uuid-horario>';
   -- Si el status es DRAFT, es seguro. Si está en un estado intermedio no estándar, corregirlo a DRAFT.
   ```

---

### Horario publicado con conflictos sin resolver

**Síntomas:** Un horario en estado `PUBLISHED` tiene registros en `scheduling_conflict` con `is_resolved = false`; instructores o coordinadores reportan solapamientos.

**Pasos:**

1. Confirmar el estado del horario y los conflictos:
   ```sql
   -- scheduling_db
   SELECT s.id, s.ficha_id, s.period, s.status, s.published_at,
          COUNT(sc.id) AS conflictos_activos
   FROM schedule s
   JOIN scheduling_conflict sc ON sc.schedule_id = s.id
   WHERE s.id = '<uuid-horario>'
     AND sc.is_resolved = false
   GROUP BY s.id;
   ```
2. Despublicar el horario (retroceder a `UNDER_REVIEW`):
   ```sql
   UPDATE schedule
   SET status = 'UNDER_REVIEW',
       published_at = NULL,
       published_by = NULL,
       updated_at = now()
   WHERE id = '<uuid-horario>'
     AND status = 'PUBLISHED';
   ```
3. Notificar a los consumidores del evento `schedule.published` (document-service, actors-service) que el horario fue despublicado. Publicar un evento de compensación si el sistema lo soporta.
4. Informar a los coordinadores académicos afectados.
5. Ejecutar el procedimiento "Re-ejecutar la validación de conflictos para un horario".
6. Una vez resueltos los conflictos, el coordinador puede republicar el horario a través de la API.

---

## Escalamiento

| Condición | Tiempo máximo antes de escalar | Paso siguiente | Contacto |
|-----------|-------------------------------|----------------|----------|
| `scheduling_db` inaccesible y no restaurada | 10 min | Escalar a infraestructura y tech lead | @infra-oncall |
| Redis inaccesible y no restaurado | 10 min | Escalar a infraestructura; suspender creación de horarios | @infra-oncall |
| Mensaje `schedule.published` en DLQ sin resolución | 15 min | Escalar a tech lead; ejecutar publicación manual de emergencia | @tech-lead |
| Horario publicado con conflictos activos | Inmediato | Despublicar; escalar a coordinador académico + tech lead | @coordinador-academico, @tech-lead |
| Worker detenido y no se recupera con reinicio | 20 min | Escalar a tech lead; revisar si hay corrupción en el read model de Redis | @tech-lead |
| Workflow colgado con impacto en periodo de matrícula | Inmediato | Escalar a tech lead; evaluar terminación manual del workflow | @tech-lead |
| Cualquier componente no resuelto en 30 min | — | Escalar a responsable del proyecto | @project-owner |

---

## Security Verification & Negative Integration Tests (R4 Hardening)

### Health & Cryptographic Endpoint Probing
Verify service health and cryptographic key availability through the Traefik Edge Gateway:

```bash
# 1. Verify Scheduling service health
curl -s http://localhost:18080/scheduling/actuator/health
# Expected: {"status":"UP","groups":["liveness","readiness"]}

# 2. Verify IAM RSA public keys (JWKS)
curl -s http://localhost:18080/iam/api/v1/auth/.well-known/jwks.json
# Expected: JSON Web Key Set with "kid": "iam-rsa-1"
```

### Running Automated Security Negative Integration Tests
Execute the 17 automated negative authentication and authorization tests in `schedules-api`:

```bash
mvn test -Dtest=SecurityNegativeAuthIT -Dsurefire.failIfNoSpecifiedTests=false
```

Expected output:
```text
[INFO] Tests run: 17, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

Key vectors tested:
- Unsigned tokens (`alg: none`) and invalid signatures rejected with HTTP 401.
- Expired tokens and foreign issuers rejected with HTTP 401.
- Missing `SCH_*` features rejected with HTTP 403.
- Foreign training center and instructor IDOR queries rejected with HTTP 404.
- Malformed or unsupported scopes rejected fail-closed with HTTP 403.
