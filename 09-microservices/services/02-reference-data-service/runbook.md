# Runbook — reference-data-service

> Estado: 🟢 Estable | Última actualización: 2026-10-24

---

## Healthcheck

| Endpoint | Método | Respuesta esperada | Umbral SLO |
|----------|--------|--------------------|------------|
| `/health` | GET | `200 { "status": "ok" }` | < 200 ms |
| `/health/db` | GET | `200 { "db": "ok" }` | < 500 ms |
| `/health/cache` | GET | `200 { "redis": "ok" }` | < 100 ms |

> **Actualización HU-REF-031 (2026-10-24).** El servicio Go implementado sirve el contrato bajo `/api/v1` y expone `GET /api/v1/health/live` (alias `GET /api/v1/health`) y `GET /api/v1/health/ready` (200 si PostgreSQL responde, 503 si no). Las mismas rutas siguen en la raíz (`/health`, `/health/live`, `/health/ready`) para sondas de contenedor; el edge no las enruta (solo `/reference-data/api/`). `/health/db` y `/health/cache` de la tabla de arriba no existen en la implementación actual: deuda de este runbook, que describe el diseño previsto (Redis, Kafka) y está pendiente de reescritura.

**SLO:** 99.5 % de disponibilidad en horario hábil (lunes–viernes 06:00–22:00 COT).

Verificación rápida desde terminal:

```bash
curl -s http://localhost:8002/health | jq .
# Respuesta esperada: { "status": "ok" }

curl -s http://localhost:8002/health/cache | jq .
# Respuesta esperada: { "redis": "ok" }
```

---

## Variables de entorno requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `PORT` | Puerto de escucha del servicio | `8002` |
| `DB_HOST` | Host de PostgreSQL (`ref_db`) | `postgres-ref.internal` |
| `DB_PORT` | Puerto PostgreSQL | `5432` |
| `DB_NAME` | Nombre de la base de datos | `ref_db` |
| `DB_USER` | Usuario de conexión | `ref_svc` |
| `DB_PASSWORD` | Contraseña del usuario de BD | *(secreto — no loguear)* |
| `DB_POOL_MIN` | Conexiones mínimas en el pool | `2` |
| `DB_POOL_MAX` | Conexiones máximas en el pool | `10` |
| `REDIS_HOST` | Host de Redis para caché de catálogos | `redis-ref.internal` |
| `REDIS_PORT` | Puerto Redis | `6379` |
| `REDIS_PASSWORD` | Contraseña Redis (si aplica) | *(secreto)* |
| `REDIS_TTL_CATALOGS` | TTL en segundos para entradas de catálogo | `86400` (24 h) |
| `REDIS_TTL_HIERARCHY` | TTL en segundos para jerarquía institucional | `86400` (24 h) |
| `IAM_SERVICE_URL` | URL base del IAM service para validar JWT | `http://iam-service:8001` |
| `JWT_AUDIENCE` | Audience esperado en el token | `sena-platform` |
| `LOG_LEVEL` | Nivel de log (`debug`/`info`/`warn`/`error`) | `info` |
| `EVENT_TOPIC` | Topic Kafka/Broker de salida | `reference-data-events` |
| `BROKER_URL` | URL del message broker | `kafka:9092` |
| `IAM_JWT_ISSUER` | Emisor (`iss`) esperado en el JWT de IAM (implementado; obligatorio) | `https://iam.example` |
| `IAM_JWKS_URL` | URL del JWKS de IAM (implementado; obligatorio). `https`, o `http` solo hacia loopback o un host de `REFERENCE_DATA_JWKS_HTTP_ALLOWED_HOSTS` | `http://iam-api:8080/api/v1/auth/.well-known/jwks.json` |
| `REFERENCE_DATA_JWKS_HTTP_ALLOWED_HOSTS` | Hosts exactos, separados por comas, que pueden servir el JWKS por `http` desde la red interna (sin esquema, puerto ni comodines). Vacía: solo `https` o loopback. No relaja firma, emisor ni expiración (HU-REF-031) | `iam-api` |

Variables ausentes al arrancar producen fallo inmediato con log `FATAL: missing required env var`.

---

## Alertas críticas

| Alerta | Condición de disparo | Severidad | Acción inmediata |
|--------|----------------------|-----------|------------------|
| **BD no responde** | Timeout a `ref_db` > 5 s durante 2 minutos | P0 | Verificar conectividad a PostgreSQL; si la BD está caída escalar a DBA. No reiniciar el servicio hasta confirmar que la BD acepta conexiones. |
| **Redis no responde** | Timeout a Redis > 2 s durante 3 minutos | P1 | El servicio continúa operando desde la BD (fallback automático). Revisar Redis. Si Redis vuelve, el caché se reconstruye solo. |
| **Tasa de error 5xx > 1 %** | Más de 1 % de respuestas 5xx en ventana de 5 min | P1 | Revisar logs por traza de error; verificar estado de BD y Redis. |
| **Catálogo no encontrado (404 masivo)** | Más de 10 errores 404 en `/catalogs/{code}` por minuto desde otros servicios | P1 | Verificar integridad de datos en tabla `catalog` y `catalog_detail`. Posible truncado accidental o migración fallida. |
| **DLQ con mensajes** | `reference-data-events.dlq` acumula > 0 mensajes en ventana de 5 min | P2 | Revisar mensajes en DLQ; identificar evento fallido y causa. Ver procedimiento de DLQ en Escenarios de falla. |
| **Pool de conexiones agotado** | `db_pool_waiting > 0` durante más de 1 minuto | P2 | Revisar si hay consultas lentas en `ref_db`. Considerar aumentar `DB_POOL_MAX` temporalmente. |
| **Latencia de respuesta > 500 ms (p99)** | p99 de latencia supera 500 ms durante 5 min | P2 | Verificar si Redis está respondiendo (caché miss masivo); revisar slow queries en PostgreSQL. |

---

## Procedimientos comunes

### Reinicio del servicio

El servicio es stateless (el estado está en PostgreSQL y Redis). El reinicio es seguro en cualquier momento.

```bash
# Con Docker Compose
docker compose restart reference-data-api

# Con Kubernetes
kubectl rollout restart deployment/reference-data-api -n sena-platform

# Verificar que levantó correctamente
kubectl rollout status deployment/reference-data-api -n sena-platform

# Confirmar healthcheck post-reinicio
curl -s http://localhost:8002/health | jq .
```

Esperar al menos 15 segundos antes de validar el healthcheck. El servicio calienta las primeras consultas desde la BD; Redis se llena gradualmente.

### Revision de logs

```bash
# Docker Compose — últimas 200 líneas
docker compose logs --tail=200 reference-data-api

# Docker Compose — seguimiento en tiempo real
docker compose logs -f reference-data-api

# Kubernetes — pod activo
kubectl logs -l app=reference-data-api -n sena-platform --tail=200

# Kubernetes — seguimiento
kubectl logs -f -l app=reference-data-api -n sena-platform

# Filtrar solo errores
kubectl logs -l app=reference-data-api -n sena-platform | grep '"level":"error"'

# Filtrar por correlation_id de una solicitud específica
kubectl logs -l app=reference-data-api -n sena-platform | grep '"correlation_id":"<uuid>"'
```

Campos relevantes en los logs estructurados (JSON):

| Campo | Descripción |
|-------|-------------|
| `level` | `info` / `warn` / `error` |
| `msg` | Mensaje descriptivo |
| `correlation_id` | ID de la solicitud HTTP de origen |
| `catalog_code` | Catálogo involucrado (si aplica) |
| `duration_ms` | Tiempo de respuesta de la operación |
| `cache_hit` | `true` si la respuesta vino de Redis |

### Invalidar caché de catálogos manualmente

Usar cuando se detecte que los consumidores están leyendo datos obsoletos de catálogos o cuando se actualice directamente la BD sin pasar por la API.

**Opción A — Invalidación total (FLUSHDB): solo en emergencias**

Elimina TODA la caché del servicio. Los consumidores experimentarán mayor latencia por algunos minutos mientras se reconstruye.

```bash
# Conectar al Redis del reference-data-service
redis-cli -h redis-ref.internal -p 6379 -a "$REDIS_PASSWORD"

# Dentro de redis-cli — borrar toda la base de datos
127.0.0.1:6379> FLUSHDB
OK

# Verificar que quedó vacía
127.0.0.1:6379> DBSIZE
(integer) 0
```

**Opcion B — Invalidación quirúrgica por catálogo (recomendada)**

Elimina solo el catálogo afectado. El patrón de clave es `catalog:<CATALOG_CODE>`.

```bash
redis-cli -h redis-ref.internal -p 6379 -a "$REDIS_PASSWORD"

# Invalidar catálogo de modalidades
127.0.0.1:6379> DEL catalog:MODALITY
(integer) 1

# Invalidar catálogo de jornadas
127.0.0.1:6379> DEL catalog:SHIFT
(integer) 1

# Invalidar un parámetro del sistema
127.0.0.1:6379> DEL parameter:MAX_HOURS_PER_WEEK
(integer) 1

# Listar todas las claves activas de catálogos (para diagnóstico)
127.0.0.1:6379> KEYS catalog:*
```

**Opcion C — Invalidación de jerarquía institucional**

```bash
redis-cli -h redis-ref.internal -p 6379 -a "$REDIS_PASSWORD"

# Invalidar un centro de formación específico por su center_code
127.0.0.1:6379> DEL training_center:CT-BOG-042

# Invalidar toda la jerarquía
127.0.0.1:6379> KEYS hierarchy:*
# Borrar cada clave encontrada o usar:
127.0.0.1:6379> EVAL "return redis.call('del', unpack(redis.call('keys', 'hierarchy:*')))" 0
```

Después de invalidar, la próxima consulta a ese catálogo recargará el valor desde PostgreSQL y lo almacenará en Redis con TTL de 24 h.

---

## Escenarios de falla y recuperacion

### Escenario 1: PostgreSQL no disponible

**Síntoma:** Errores 503 en todas las rutas; log muestra `Connection refused` o `ECONNREFUSED` hacia `ref_db`.

**Impacto:** Los catálogos que ya están en Redis siguen sirviéndose (TTL 24 h). Las rutas de escritura y las rutas que no estén en caché fallan.

**Pasos de recuperación:**

1. Confirmar que PostgreSQL está caído:
   ```bash
   psql -h postgres-ref.internal -U ref_svc -d ref_db -c "SELECT 1;"
   ```
2. Si la BD está caída, escalar al equipo de infraestructura / DBA.
3. No reiniciar el servicio mientras la BD esté caída — el servicio ya está atendiendo desde Redis.
4. Una vez que la BD recupera, el pool de conexiones se restablece automáticamente. Verificar:
   ```bash
   curl -s http://localhost:8002/health/db | jq .
   ```
5. Si el reconexión automática no ocurre en 2 minutos, reiniciar el servicio.

### Escenario 2: Redis no disponible

**Síntoma:** Log muestra `Redis connection error`; métricas indican `cache_hit = false` en el 100 % de solicitudes. Latencia aumenta a > 200 ms porque todo va a PostgreSQL.

**Impacto:** Degradación de rendimiento pero no interrupción del servicio. Los otros microservicios que leen catálogos sí pueden ver impacto si ellos también usan Redis.

**Pasos de recuperación:**

1. Verificar Redis:
   ```bash
   redis-cli -h redis-ref.internal -p 6379 ping
   # Esperado: PONG
   ```
2. Si Redis está caído, escalar al equipo de infraestructura.
3. El servicio sigue operando desde PostgreSQL en modo degradado. No es necesario reiniciar.
4. Cuando Redis recupera, el caché se reconstruye automáticamente con las consultas subsiguientes.
5. Si se necesita acelerar el calentamiento del caché, invocar manualmente los endpoints de catálogos más usados:
   ```bash
   curl -s http://localhost:8002/catalogs/MODALITY
   curl -s http://localhost:8002/catalogs/SHIFT
   ```

### Escenario 3: Catálogos devuelven datos obsoletos

**Síntoma:** Otros servicios reportan que los valores de catálogo no coinciden con lo actualizado vía API. `monitoring-service` o `scheduling-service` usan valores que ya no existen.

**Causa probable:** La API fue actualizada directamente en la BD (sin pasar por el endpoint REST) o el evento `reference.catalog.updated` no fue procesado por los consumidores.

**Pasos de recuperación:**

1. Confirmar el estado en BD:
   ```bash
   psql -h postgres-ref.internal -U ref_svc -d ref_db \
     -c "SELECT code, label, is_active FROM catalog_detail WHERE catalog_id = (SELECT id FROM catalog WHERE code = 'MODALITY');"
   ```
2. Invalidar el catálogo afectado en Redis (ver procedimiento B de invalidación arriba).
3. Verificar que los consumidores (`scheduling-service`, `actors-service`) también invaliden su propia caché al recibir el evento. Si no lo hicieron, escalar a los equipos de esos servicios para que ejecuten su propio procedimiento de invalidación.

### Escenario 4: Mensajes en DLQ (reference-data-events.dlq)

**Síntoma:** Alerta de DLQ con mensajes pendientes.

**Pasos de recuperación:**

1. Inspeccionar los mensajes en la DLQ:
   ```bash
   # Con Kafka CLI
   kafka-console-consumer.sh \
     --bootstrap-server kafka:9092 \
     --topic reference-data-events.dlq \
     --from-beginning \
     --max-messages 10
   ```
2. Identificar el `event_type` y el error de procesamiento.
3. Si el error es transitorio (consumidor temporalmente caído), el consumidor puede reprocesar el mensaje al recuperarse.
4. Si el error es permanente (payload malformado), registrar en el sistema de incidencias y marcar el mensaje para descarte manual.
5. Retención máxima en DLQ: 7 días.

### Escenario 5: Degradacion lenta — pool de conexiones agotado

**Síntoma:** Latencia en aumento progresivo. Log muestra `db pool exhausted` o `connection timeout`.

**Pasos de recuperación:**

1. Revisar conexiones activas en PostgreSQL:
   ```bash
   psql -h postgres-ref.internal -U ref_svc -d ref_db \
     -c "SELECT count(*), state FROM pg_stat_activity WHERE datname='ref_db' GROUP BY state;"
   ```
2. Identificar consultas lentas:
   ```bash
   psql -h postgres-ref.internal -U ref_svc -d ref_db \
     -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state \
         FROM pg_stat_activity WHERE datname='ref_db' AND state != 'idle' \
         ORDER BY duration DESC LIMIT 10;"
   ```
3. Si hay consultas colgadas (> 30 s), terminarlas:
   ```bash
   psql -h postgres-ref.internal -U ref_svc -d ref_db \
     -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity \
         WHERE datname='ref_db' AND state = 'active' \
         AND now() - query_start > interval '30 seconds';"
   ```
4. Aumentar `DB_POOL_MAX` temporalmente si el volumen de tráfico lo justifica y reiniciar el servicio.

---

## Escalamiento

| Nivel | Condición | Receptor | Medio |
|-------|-----------|----------|-------|
| L1 — Operaciones | Alerta P2 / síntoma contenido | Equipo de plataforma | Slack `#ops-alerts` |
| L2 — Backend | Alerta P1 / error en catálogos afecta otros servicios | Tech lead de reference-data | Slack + llamada directa |
| L3 — Infraestructura | P0 / PostgreSQL o Redis caídos | Equipo de infraestructura / DBA | PagerDuty |
| L4 — Producto | Datos institucionales corruptos o pérdida de datos | Product owner del módulo M2/M4 | Correo + reunión urgente |

**Información a incluir en el escalamiento:**

- Timestamp del primer síntoma
- Texto del log de error con `correlation_id`
- Resultado de `/health`, `/health/db`, `/health/cache`
- Catálogo(s) afectados si aplica
- Servicios consumidores impactados (los que leen de este servicio: todos los demás)
