# Runbook — training-environment-service

> Estado: 🟢 Estable | Última actualización: 2026-10-24

---

## Healthcheck

| Endpoint | Respuesta esperada | SLO |
|----------|--------------------|-----|
| `GET http://training-environment-api:8004/health` | `200 { "status": "ok" }` | < 200 ms |
| `GET http://training-environment-api:8004/health/ready` | `200` cuando `env_db` es accesible | < 500 ms |

> **Rutas.** La operación `health` del contrato (`training-environment.yaml`, `servers: /api/v1`) es `GET /api/v1/health` (por el edge, `/training-environment/api/v1/health`); `GET /health` en la raíz sigue siendo la sonda de infraestructura y responde lo mismo. El resto de las operaciones del servicio cuelgan de `/api/v1` y las rutas sin prefijo responden `404` (HU-ENV-020, ADR-022 §3).

Respuesta esperada de `/health`:

```json
{
  "status": "ok",
  "service": "training-environment-service",
  "version": "1.x.x",
  "db": "ok",
  "timestamp": "2026-06-20T00:00:00Z"
}
```

Si `db` es `"degraded"` o `"unreachable"`, el servicio no puede responder consultas de disponibilidad. Esto bloquea directamente la creación de horarios en `scheduling-service`. Tratar como P0.

---

## Variables de entorno requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `PORT` | Puerto de escucha del servicio | `8004` |
| `DATABASE_URL` | Cadena de conexión a `env_db` (PostgreSQL) | `postgresql://user:pass@host:5432/env_db` |
| `DATABASE_POOL_MIN` | Conexiones mínimas en pool | `2` |
| `DATABASE_POOL_MAX` | Conexiones máximas en pool | `10` |
| `IAM_SERVICE_URL` | URL base de `iam-service` para validación de JWT | `http://iam-service:8001` |
| `IAM_JWKS_URI` | URI del endpoint JWKS para verificación de tokens | `http://iam-service:8001/.well-known/jwks.json` |
| `REFERENCE_DATA_SERVICE_URL` | URL base de `reference-data-service` | `http://reference-data-service:8002` |
| `MESSAGE_BROKER_URL` | URL del broker para publicar eventos en `environment-events` | `amqp://user:pass@broker:5672` |
| `ENVIRONMENT_EVENTS_TOPIC` | Nombre del topic de eventos publicados | `environment-events` |
| `LOG_LEVEL` | Nivel de logging | `info` |
| `NODE_ENV` / `APP_ENV` | Entorno de ejecución | `production` |

Variables opcionales de rendimiento:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `AVAILABILITY_QUERY_TIMEOUT_MS` | Timeout máximo para consultas de disponibilidad | `300` |
| `HTTP_REQUEST_TIMEOUT_MS` | Timeout para llamadas salientes a dependencias | `5000` |

---

## Alertas críticas

| Alerta | Condición | Severidad | Acción inmediata |
|--------|-----------|-----------|------------------|
| `env_db` inaccesible | Timeout o error de conexión sostenido > 10 s | P0 | Ver procedimiento "Base de datos no responde" |
| Disponibilidad no consultable | `scheduling-service` reporta `503` al llamar a este servicio | P0 | Reiniciar el pod; revisar logs del healthcheck; verificar conectividad de red |
| Latencia de consulta de disponibilidad alta | p95 > 300 ms sostenido 2 min | P1 | Revisar EXPLAIN ANALYZE en las queries de `availability_rule` y `maintenance`; verificar índices |
| Error en publicación de eventos | Mensaje en `environment-events.dlq` | P1 | Ver procedimiento "Mensaje en DLQ" |
| Ventana de mantenimiento activa inesperada | Ambiente bloqueado sin mantenimiento registrado | P1 | Ver procedimiento "Forzar cierre de ventana de mantenimiento" |
| `iam-service` inaccesible | JWT no puede validarse; todas las requests fallan con `401`/`503` | P1 | Verificar conectividad a `iam-service`; revisar logs de red |
| `reference-data-service` inaccesible | No puede consultarse el catálogo de tipos de ambiente o sedes | P2 | El servicio puede operar en modo degradado con tipos ya cargados; escalar si supera 5 min |

---

## Procedimientos comunes

### Forzar cierre de una ventana de mantenimiento

Usar cuando un mantenimiento quedó registrado con `end_date` incorrecto o debe cerrarse antes de lo previsto, y el ambiente está bloqueado para el `scheduling-service`.

**Verificar el estado actual del mantenimiento:**

```sql
-- Conectarse a env_db
SELECT id, environment_id, start_date, end_date, description, created_by
FROM maintenance
WHERE environment_id = '<uuid-ambiente>'
  AND end_date >= CURRENT_DATE
ORDER BY start_date;
```

**Identificar si hay sesiones de `scheduling-service` afectadas** (consulta de referencia cruzada, ejecutar en `scheduling_db`):

```sql
SELECT cs.id, cs.schedule_id, cs.session_date, cs.start_time, cs.end_time
FROM class_session cs
WHERE cs.environment_id = '<uuid-ambiente>'
  AND cs.session_date BETWEEN '<start_date>' AND '<end_date>'
  AND cs.status = 'ACTIVE';
```

**Cerrar el mantenimiento anticipadamente** (ajustar `end_date` al día de hoy):

```sql
-- env_db
UPDATE maintenance
SET end_date = CURRENT_DATE
WHERE id = '<uuid-mantenimiento>';
```

**Verificar que el ambiente vuelve a aparecer como disponible:**

```bash
curl -s -H "Authorization: Bearer <TOKEN>" \
  "http://training-environment-api:8004/environments/<uuid-ambiente>/availability?date=<YYYY-MM-DD>"
```

**Notificar a `scheduling-service`:** El cambio de disponibilidad debe notificarse manualmente si el evento `environment.availability.changed` no se publicó automáticamente. Publicar el evento al topic `environment-events` con `change_type: RULE_MODIFIED`.

---

### Cancelar una reserva conflictiva

Usar cuando una reserva en estado `CONFIRMED` bloquea un ambiente que el coordinador necesita para programar clases.

**Identificar la reserva:**

```sql
-- env_db
SELECT id, environment_id, reservation_date, start_time, end_time,
       status, requester_id, reason, created_at
FROM reservation
WHERE environment_id = '<uuid-ambiente>'
  AND reservation_date = '<YYYY-MM-DD>'
  AND status = 'CONFIRMED';
```

**Confirmar que no existe una sesión de clase sobre el mismo bloque** (verificación cruzada en `scheduling_db`):

```sql
SELECT id, schedule_id, session_date, start_time, end_time, status
FROM class_session
WHERE environment_id = '<uuid-ambiente>'
  AND session_date = '<YYYY-MM-DD>'
  AND status = 'ACTIVE'
  AND start_time < '<end_time_reserva>'
  AND end_time > '<start_time_reserva>';
```

**Cancelar la reserva:**

```sql
-- env_db
UPDATE reservation
SET status = 'CANCELLED',
    updated_at = now()
WHERE id = '<uuid-reserva>'
  AND status = 'CONFIRMED';
```

**Registrar la acción en el log de operaciones** con el `id` de la reserva, motivo y operador que ejecutó el cambio.

---

### Mensaje en la DLQ `environment-events.dlq`

**Inspeccionar el mensaje:**

```bash
# Con CLI del broker (ejemplo RabbitMQ)
rabbitmqadmin get queue=environment-events.dlq count=10
```

**Revisar el payload del mensaje** para determinar el `event_type` y el `event_id`.

**Si el fallo es transitorio** (broker momentáneamente caído, timeout de red): reencolar el mensaje hacia `environment-events`. Los consumidores aplican deduplicación por `event_id`.

```bash
rabbitmqadmin publish exchange=environment-events routing_key=environment-events \
  payload='<payload-del-mensaje>'
```

**Si el fallo es estructural** (payload malformado, schema incorrecto): corregir el payload manualmente y reencolar. Abrir ticket de bug con el payload original y el stacktrace del consumidor.

**Retención en DLQ**: 7 días. Los mensajes no reencolados en ese plazo se pierden permanentemente.

---

## Escenarios de falla

### Base de datos no responde

**Síntomas:** `/health` retorna `500` o `{ "db": "unreachable" }`; `scheduling-service` recibe `503` al consultar disponibilidad.

**Pasos:**

1. Verificar estado del pod de la base de datos:
   ```bash
   kubectl get pods -n <namespace> | grep env-db
   kubectl logs <pod-env-db> --tail=50
   ```
2. Verificar que la `DATABASE_URL` es correcta y el host es alcanzable desde el pod de la API:
   ```bash
   kubectl exec -it <pod-training-environment-api> -- nc -zv <db-host> 5432
   ```
3. Si la base de datos está caída, seguir el runbook de recuperación de PostgreSQL del equipo de infraestructura.
4. Una vez restaurada la conexión, reiniciar el pod de la API para forzar reconexión del pool:
   ```bash
   kubectl rollout restart deployment/training-environment-api
   ```
5. Verificar el healthcheck:
   ```bash
   curl -s http://training-environment-api:8004/health
   ```

---

### Latencia alta en consultas de disponibilidad

**Síntomas:** `scheduling-service` reporta timeouts o p95 > 300 ms al llamar a `GET /environments/:id/availability`.

**Pasos:**

1. Verificar el plan de ejecución de la query de disponibilidad:
   ```sql
   -- env_db
   EXPLAIN ANALYZE
   SELECT * FROM availability_rule
   WHERE environment_id = '<uuid>'
     AND day_of_week = 2;
   ```
2. Verificar que los índices existen:
   ```sql
   SELECT indexname, indexdef
   FROM pg_indexes
   WHERE tablename IN ('availability_rule', 'maintenance', 'reservation');
   ```
3. Si los índices no existen, crearlos:
   ```sql
   CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_avail_rule_env_dow
     ON availability_rule (environment_id, day_of_week);

   CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_maintenance_env_dates
     ON maintenance (environment_id, start_date, end_date);

   CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_reservation_env_date
     ON reservation (environment_id, reservation_date);
   ```
4. Verificar si hay table bloat o necesidad de `VACUUM ANALYZE`:
   ```sql
   VACUUM ANALYZE availability_rule;
   VACUUM ANALYZE maintenance;
   VACUUM ANALYZE reservation;
   ```

---

### Evento no publicado al broker

**Síntomas:** Operación registrada exitosamente en `env_db` pero `scheduling-service` no actualizó su read model; no hay mensaje en el topic `environment-events`.

**Pasos:**

1. Verificar conectividad al broker desde el pod de la API:
   ```bash
   kubectl exec -it <pod-training-environment-api> -- nc -zv <broker-host> 5672
   ```
2. Revisar logs del publicador de eventos:
   ```bash
   kubectl logs <pod-training-environment-api> --tail=100 | grep "environment-events"
   ```
3. Publicar el evento manualmente si el hecho de negocio ya ocurrió pero el evento no se emitió. Construir el payload con los datos de `env_db` y publicarlo al topic `environment-events`. Los consumidores aplican idempotencia por `event_id`.
4. Informar a `scheduling-service` para que fuerce una resincronización de su read model (ver runbook de scheduling-service, procedimiento "Limpiar read models obsoletos en Redis").

---

### Ambiente reportado como disponible cuando debería estar bloqueado

**Síntomas:** `scheduling-service` asigna un ambiente que está en mantenimiento o tiene una reserva activa.

**Diagnóstico:**

```sql
-- env_db: verificar mantenimientos vigentes
SELECT * FROM maintenance
WHERE environment_id = '<uuid>'
  AND start_date <= CURRENT_DATE
  AND end_date >= CURRENT_DATE;

-- Verificar reservas activas en el mismo bloque
SELECT * FROM reservation
WHERE environment_id = '<uuid>'
  AND reservation_date = '<YYYY-MM-DD>'
  AND status IN ('PENDING', 'CONFIRMED')
  AND start_time < '<end_time>'
  AND end_time > '<start_time>';
```

Si el bloqueo existe en `env_db` pero `scheduling-service` lo ignoró, el read model de Redis en `scheduling-service` está desactualizado. Ejecutar el procedimiento "Limpiar read models obsoletos en Redis" del runbook de scheduling-service.

---

## Escalamiento

| Condición | Tiempo máximo antes de escalar | Paso siguiente | Contacto |
|-----------|-------------------------------|----------------|----------|
| `env_db` inaccesible y no restaurada | 10 min | Escalar a infraestructura y tech lead | @infra-oncall |
| Servicio no responde y afecta creación de horarios | 5 min | Escalar a tech lead; considerar modo de mantenimiento en `scheduling-service` | @tech-lead |
| Evento en DLQ sin causa clara | 30 min | Escalar a equipo de plataforma | @platform-team |
| Ambiente bloqueado erróneamente con fichas activas | Inmediato | Escalar a coordinador académico + tech lead | @coordinador-academico, @tech-lead |
