# Runbook — academic-management-service

> Estado: 🟢 Estable | Última actualización: 2026-10-24

---

## Healthcheck

| Endpoint | Método | Respuesta esperada | Umbral SLO |
|----------|--------|--------------------|------------|
| `/health` | GET | `200 { "status": "ok" }` | < 200 ms |
| `/health/db` | GET | `200 { "db": "ok" }` | < 500 ms |

**SLO:** 99 % de disponibilidad continua (sin ventana de mantenimiento diferenciada por horario).

Verificación rápida desde terminal:

```bash
curl -s http://localhost:8003/health | jq .
# Respuesta esperada: { "status": "ok" }

curl -s http://localhost:8003/health/db | jq .
# Respuesta esperada: { "db": "ok" }
```

---

## Variables de entorno requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `PORT` | Puerto de escucha del servicio | `8003` |
| `DB_HOST` | Host de PostgreSQL (`academic_db`) | `postgres-academic.internal` |
| `DB_PORT` | Puerto PostgreSQL | `5432` |
| `DB_NAME` | Nombre de la base de datos | `academic_db` |
| `DB_USER` | Usuario de conexión | `academic_svc` |
| `DB_PASSWORD` | Contraseña del usuario de BD | *(secreto — no loguear)* |
| `DB_POOL_MIN` | Conexiones mínimas en el pool | `2` |
| `DB_POOL_MAX` | Conexiones máximas en el pool | `10` |
| `IAM_SERVICE_URL` | URL base del IAM service para validar JWT | `http://iam-service:8001` |
| `REFERENCE_DATA_SERVICE_URL` | URL base del reference-data-service | `http://reference-data-service:8002` |
| `JWT_AUDIENCE` | Audience esperado en el token | `sena-platform` |
| `LOG_LEVEL` | Nivel de log (`debug`/`info`/`warn`/`error`) | `info` |
| `EVENT_TOPIC` | Topic Kafka/Broker de salida | `academic-events` |
| `BROKER_URL` | URL del message broker | `kafka:9092` |

**Nota:** Este servicio no usa Redis. No hay variables de caché. El rendimiento depende directamente de la disponibilidad de `academic_db` y de la latencia hacia `reference-data-service` (consultado en modo síncrono para validar `training_center_id` al abrir fichas).

Variables ausentes al arrancar producen fallo inmediato con log `FATAL: missing required env var`.

---

## Imagen de despliegue

> HU-ACAD-019 ([docs#361](https://github.com/code-sena/design-software-docs/issues/361)), escenario 3.

El servicio se empaqueta con `deploy/Dockerfile.api` (convención de [ADR-006](../../../05-architecture/decisions/records/ADR-006-polyglot-stack-strategy.md)). Se construye desde la raíz del repo `design-software-academic-management-service`:

```bash
docker build -f deploy/Dockerfile.api -t academic-management-service:local .
```

- **Build multi-etapa.** Maven 3.9 con Temurin 17 compila los tres módulos (`academic-core`, `academic-adapters`, `academic-management-api`) y genera el jar ejecutable de Spring Boot. La imagen final es `eclipse-temurin:17-jre` y corre con el usuario sin privilegios `10001`.
- **Puerto interno 8080** ([ADR-007](../../../05-architecture/decisions/records/ADR-007-edge-gateway-and-port-convention.md)). La imagen fija `SERVER_PORT=8080`, que sobrescribe el `server.port: 8003` de `application.yml`. El `8003` es el puerto al correr el jar sin contenedor, como en los ejemplos de este runbook; detrás del edge el servicio se alcanza por el puerto 8080 de su contenedor.
- **Misma imagen en los cuatro ambientes** ([ADR-022](../../../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md) §6). La imagen no lleva secretos ni valores de ambiente: la base de datos, el broker y IAM entran como variables de entorno al arrancar. Los nombres exactos que lee el servicio están en `academic-management-api/src/main/resources/application.yml`.

---

## Alertas críticas

| Alerta | Condición de disparo | Severidad | Acción inmediata |
|--------|----------------------|-----------|------------------|
| **BD no responde** | Timeout a `academic_db` > 5 s durante 2 minutos | P0 | Verificar conectividad a PostgreSQL. No reiniciar el servicio hasta que la BD acepte conexiones. Escalar a DBA. |
| **reference-data-service no responde** | Timeout HTTP a `:8002` > 3 s durante 1 minuto | P1 | Las operaciones de apertura de ficha fallarán (requieren validar `training_center_id`). Lectura de fichas/programas existentes no se ve afectada. Verificar estado de reference-data-service. |
| **Fichas en estado incorrecto (bloqueo operacional)** | `scheduling-service` reporta 404 en fichas que deberían estar `EXECUTION` | P1 | Consultar estado real de la ficha en BD. Ver procedimiento de reabrir ficha bloqueada. |
| **Tasa de error 5xx > 2 %** | Más de 2 % de respuestas 5xx en ventana de 5 min | P1 | Revisar logs por traza de error. Verificar estado de `academic_db`. |
| **DLQ con mensajes** | La DLQ operativa definida para Academic acumula > 10 mensajes sin procesar | P2 | Revisar mensajes en DLQ; identificar evento fallido y causa. Ver procedimiento de DLQ en Escenarios de falla. |
| **Programa sin competencias activas** | Programa en `is_active = true` con cero competencias activas | P2 | Posible inconsistencia de datos. Auditar el programa afectado. Las fichas abiertas con ese programa pueden quedar sin asignación de horas. |
| **Pool de conexiones agotado** | `db_pool_waiting > 0` durante más de 1 minuto | P2 | Revisar si hay transacciones largas abiertas; identificar fichas con operaciones pendientes en vuelo. |

---

## Procedimientos comunes

### Reinicio del servicio

El servicio es stateless (el estado está en `academic_db`). No hay caché que limpiar. El reinicio es seguro salvo que haya transacciones en vuelo — verificar primero.

```bash
# Verificar que no hay transacciones activas largas antes de reiniciar
psql -h postgres-academic.internal -U academic_svc -d academic_db \
  -c "SELECT pid, now() - query_start AS duration, query, state \
      FROM pg_stat_activity WHERE datname='academic_db' AND state = 'active' \
      ORDER BY duration DESC LIMIT 5;"

# Con Docker Compose
docker compose restart academic-management-api

# Con Kubernetes
kubectl rollout restart deployment/academic-management-api -n sena-platform

# Verificar que levantó correctamente
kubectl rollout status deployment/academic-management-api -n sena-platform

# Confirmar healthcheck post-reinicio
curl -s http://localhost:8003/health | jq .
```

### Revision de logs

```bash
# Docker Compose — últimas 200 líneas
docker compose logs --tail=200 academic-management-api

# Docker Compose — seguimiento en tiempo real
docker compose logs -f academic-management-api

# Kubernetes — pod activo
kubectl logs -l app=academic-management-api -n sena-platform --tail=200

# Kubernetes — seguimiento
kubectl logs -f -l app=academic-management-api -n sena-platform

# Filtrar solo errores
kubectl logs -l app=academic-management-api -n sena-platform | grep '"level":"error"'

# Filtrar por número de ficha
kubectl logs -l app=academic-management-api -n sena-platform | grep '"ficha_number":"2758369"'

# Filtrar por correlation_id de una solicitud específica
kubectl logs -l app=academic-management-api -n sena-platform | grep '"correlation_id":"<uuid>"'
```

Campos relevantes en los logs estructurados (JSON):

| Campo | Descripción |
|-------|-------------|
| `level` | `info` / `warn` / `error` |
| `msg` | Mensaje descriptivo |
| `correlation_id` | ID de la solicitud HTTP de origen |
| `ficha_number` | Número de ficha SENA involucrada (si aplica) |
| `program_code` | Código del programa involucrado (si aplica) |
| `duration_ms` | Tiempo de respuesta de la operación |

### Reabrir ficha bloqueada en estado incorrecto

Usar cuando una ficha quedó en un estado que bloquea operaciones downstream (por ejemplo: la ficha debe estar en `EXECUTION` para que `scheduling-service` pueda asignar horas, pero está en `INDUCTION` por un error de migración o falla parcial en la transición).

**Estados válidos de `enrollment_ficha.status`:**

```
INDUCTION -> EXECUTION -> PRODUCTIVE_STAGE -> COMPLETED
                                           \-> CANCELLED
```

**Paso 1: Diagnosticar el estado actual de la ficha**

```sql
-- Conectar a academic_db
psql -h postgres-academic.internal -U academic_svc -d academic_db

-- Consultar ficha por su número externo
SELECT
    id,
    ficha_number,
    status,
    start_date,
    expected_end_date,
    actual_end_date,
    training_shift,
    training_modality,
    max_capacity,
    program_id,
    training_center_id
FROM enrollment_ficha
WHERE ficha_number = '2758369';
```

**Paso 2: Verificar el programa asociado**

```sql
SELECT
    tp.id,
    tp.program_code,
    tp.name,
    tp.training_level,
    tp.is_active,
    COUNT(c.id) AS competency_count
FROM training_program tp
LEFT JOIN competency c ON c.program_id = tp.id AND c.is_active = true
WHERE tp.id = '<program_id_de_la_ficha>'
GROUP BY tp.id;
```

**Paso 3: Corregir el estado de la ficha**

Ejecutar SOLO si se tiene autorización del coordinador académico responsable. Registrar en el sistema de incidencias antes de ejecutar.

```sql
-- Iniciar transacción explícita para poder hacer rollback si algo falla
BEGIN;

-- Ver el estado actual antes de modificar
SELECT id, ficha_number, status FROM enrollment_ficha WHERE ficha_number = '2758369';

-- Actualizar al estado correcto
-- Ajustar el valor de status según el estado de negocio real de la ficha:
-- INDUCTION, EXECUTION, PRODUCTIVE_STAGE, COMPLETED, CANCELLED
UPDATE enrollment_ficha
SET status = 'EXECUTION'
WHERE ficha_number = '2758369'
  AND status = 'INDUCTION';

-- Verificar que afectó exactamente 1 fila
-- Si affected rows = 0, la condición no coincidió — revisar antes de continuar
-- Si affected rows > 1, hacer ROLLBACK inmediatamente

-- Confirmar el cambio solo si todo se ve correcto
COMMIT;

-- En caso de duda: ROLLBACK;
```

**Paso 4: Verificar post-corrección**

```sql
-- Confirmar el nuevo estado
SELECT id, ficha_number, status FROM enrollment_ficha WHERE ficha_number = '2758369';
```

```bash
# Verificar que scheduling-service ya puede leer la ficha
curl -s -H "Authorization: Bearer <token>" http://localhost:8003/api/v1/fichas/<ficha_id> | jq '.status'
# Esperado: "EXECUTION"
```

**Paso 5: Registrar en el log de auditoría**

Notificar al equipo de `audit-service` para registrar el cambio manual, incluyendo: número de ficha, estado anterior, estado nuevo, operador que ejecutó, timestamp y justificación.

---

## Escenarios de falla y recuperacion

### Escenario 1: PostgreSQL no disponible

**Síntoma:** Errores 503 en todas las rutas; log muestra `Connection refused` hacia `academic_db`.

**Impacto:** Servicio completamente inoperativo. No hay caché de respaldo. `scheduling-service` no puede consultar fichas activas. Interrumpe la creación de horarios.

**Pasos de recuperación:**

1. Confirmar que PostgreSQL está caído:
   ```bash
   psql -h postgres-academic.internal -U academic_svc -d academic_db -c "SELECT 1;"
   ```
2. Si la BD está caída, escalar al equipo de infraestructura / DBA.
3. No reiniciar el servicio mientras la BD esté caída — no mejora la situación y puede complicar el diagnóstico.
4. Una vez que la BD recupera, verificar reconexión automática:
   ```bash
   curl -s http://localhost:8003/health/db | jq .
   ```
5. Si la reconexión automática no ocurre en 2 minutos, reiniciar el servicio.
6. Verificar que no quedaron transacciones incompletas (fichas a medio abrir o cerrar):
   ```sql
   SELECT ficha_number, status, updated_at
   FROM enrollment_ficha
   ORDER BY updated_at DESC
   LIMIT 20;
   ```

### Escenario 2: reference-data-service no responde

**Síntoma:** Los endpoints de apertura de ficha devuelven 503 o 502. Log muestra timeout hacia `http://reference-data-service:8002`. Los endpoints de consulta de fichas y programas existentes continúan funcionando.

**Causa:** La apertura de nuevas fichas requiere validar `training_center_id` contra `reference-data-service` (llamada HTTP síncrona). Si ese servicio no responde, la validación falla.

**Impacto:** Solo las operaciones de apertura de fichas nuevas fallan. La lectura de fichas y programas existentes no se ve afectada.

**Pasos de recuperación:**

1. Verificar el estado de `reference-data-service`:
   ```bash
   curl -s http://reference-data-service:8002/health | jq .
   ```
2. Si está caído, seguir el runbook de `reference-data-service`.
3. Este servicio no tiene circuit breaker automático configurado en esta versión. Las solicitudes de apertura de fichas seguirán fallando hasta que `reference-data-service` recupere.
4. Una vez que `reference-data-service` recupera, las operaciones de apertura de fichas se recuperan automáticamente sin necesidad de reiniciar este servicio.
5. Comunicar al equipo de coordinadores académicos que la apertura de fichas está temporalmente suspendida.

### Escenario 3: Ficha en estado incorrecto bloquea scheduling-service

**Síntoma:** `scheduling-service` reporta que no puede construir horarios para una ficha específica, o que la ficha no existe en estado esperado. El log de `academic-management-service` puede mostrar una discrepancia entre el estado persistido y el esperado por la lógica de negocio.

**Causa probable:** Falla parcial durante una transición de estado (crash del servicio a mitad de una operación), intervención manual en la BD, o migración de datos que no actualizó los estados correctamente.

**Pasos de recuperación:**

Ejecutar el procedimiento completo descrito en la sección "Reabrir ficha bloqueada en estado incorrecto" (arriba).

Adicionalmente, verificar si hay otras fichas afectadas en el mismo centro:

```sql
-- Fichas que deberían estar en EXECUTION pero están en INDUCTION
-- (ajustar fechas y criterios según el período académico afectado)
SELECT ficha_number, status, start_date, training_center_id
FROM enrollment_ficha
WHERE status = 'INDUCTION'
  AND start_date < CURRENT_DATE
ORDER BY start_date;
```

### Escenario 4: Programa sin competencias — fichas no pueden asignarse

**Síntoma:** Al intentar abrir una ficha para un programa, el sistema devuelve 422 indicando que el programa no tiene competencias activas. O bien, fichas existentes quedan sin cobertura de horas porque se desactivaron competencias.

**Diagnóstico:**

```sql
-- Programas activos sin competencias activas
SELECT tp.program_code, tp.name, COUNT(c.id) AS active_competencies
FROM training_program tp
LEFT JOIN competency c ON c.program_id = tp.id AND c.is_active = true
WHERE tp.is_active = true
GROUP BY tp.id, tp.program_code, tp.name
HAVING COUNT(c.id) = 0;
```

**Pasos de recuperación:**

1. Identificar si las competencias fueron desactivadas intencionalmente o por error.
2. Si fue por error, reactivar a través del endpoint REST de la API (no directamente en BD):
   ```bash
   curl -X PATCH http://localhost:8003/programs/{program_id}/competencies/{competency_id} \
     -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{"is_active": true}'
   ```
3. Si la desactivación es válida (programa actualizado), el coordinador académico debe registrar las nuevas competencias a través del módulo M5 antes de abrir nuevas fichas para ese programa.
4. **Restriccion de negocio:** No se puede reactivar una competencia desactivada si existen fichas abiertas con resultados de aprendizaje asociados a ella (invariante del dominio). En ese caso, debe crearse una nueva competencia con distinto código.

### Escenario 5: Mensajes en DLQ de Academic

**Síntoma:** Alerta por más de 10 mensajes en la DLQ operativa definida para Academic.

Academic separa la DLQ de publicación `academic-events.dlq` de la DLQ del
consumidor R1 `academic-events.r1.dlq`. La retención continúa pendiente; el
reproceso del consumidor R1 requiere autorización. El consumidor R1 viene
apagado: solo recibe mensajes si se inicia con `ACADEMIC_R1_CONSUMER_ENABLED=true`.

**Publicación confiable:** el patrón esperado inserta el evento en Outbox dentro
de la misma transacción que modifica el dato de negocio; un relay publica al
broker y marca la fila como publicada después del ACK. El publicador de Academic
usa reintentos `1s → 4s → 16s` (tres tras el intento original), distintos del
retry de consumo.

**Consumidores del topic `academic-events`:**

| Evento | Consumidores |
|--------|-------------|
| `academic.program.created` | `audit-service` |
| `academic.ficha.opened` | `audit-service`, `monitoring-service` |
| `academic.ficha.closed` | `audit-service`, `monitoring-service` |
| `academic.competency.updated` | `audit-service`, `actors-service` |

**Pasos de recuperación:**

1. Inspeccionar `academic-events.r1.dlq` en RabbitMQ Management y registrar
   `message_id`, `event_type` y la razón de DLQ.
2. Identificar el `event_type` y el `correlation_id` del evento fallido.
3. Verificar el estado del consumidor fallido (`audit-service`, `monitoring-service` o `actors-service`).
4. Si el error es transitorio, un operador autorizado ejecuta
   `POST /api/v1/events/dlq/reprocess-next`. El endpoint conserva `message_id`
   para que la deduplicación siga siendo válida.
5. Si el error es permanente (payload malformado), registrar en el sistema de incidencias. Si el evento es crítico para auditoría, notificar al equipo de auditoría para registro manual.
6. Confirmar que la DLQ pase de 1 a 0 y que exista un solo recibo para el mismo
   `event_id` en `academic_management.processed_event`.
7. Retención máxima en DLQ: pendiente de decisión.

### Escenario 6: Inconsistencia de datos — ficha con training_center_id inexistente

**Síntoma:** Las fichas de un centro de formación no aparecen en consultas que unen con `reference-data-service`. O bien, el `training_center_id` almacenado en `enrollment_ficha` no coincide con ningún `training_center` activo.

**Diagnóstico:** Este es un dato de referencia externa — `academic-management-service` almacena el UUID pero no tiene FK directa a `reference-data-service`.

```sql
-- Listar fichas agrupadas por training_center_id para auditar
SELECT training_center_id, COUNT(*) AS ficha_count, MIN(start_date), MAX(start_date)
FROM enrollment_ficha
WHERE status IN ('INDUCTION', 'EXECUTION', 'PRODUCTIVE_STAGE')
GROUP BY training_center_id
ORDER BY ficha_count DESC;
```

Validar cada `training_center_id` contra `reference-data-service`:

```bash
curl -s http://reference-data-service:8002/api/v1/training-centers/<training_center_id> | jq '.is_active'
```

Si el centro fue desactivado en `reference-data-service` pero las fichas aún están activas en este servicio, escalar al coordinador académico para definir la acción de negocio (no modificar unilateralmente).

---

## Escalamiento

| Nivel | Condición | Receptor | Medio |
|-------|-----------|----------|-------|
| L1 — Operaciones | Alerta P2 / síntoma contenido | Equipo de plataforma | Slack `#ops-alerts` |
| L2 — Backend | Alerta P1 / fichas bloqueadas afectan scheduling | Tech lead de academic-management | Slack + llamada directa |
| L3 — Infraestructura | P0 / PostgreSQL caído | Equipo de infraestructura / DBA | PagerDuty |
| L4 — Dominio académico | Corrección manual de estado de ficha / datos incorrectos | Coordinador académico responsable del centro afectado | Correo + aprobación documentada |
| L5 — Producto | Pérdida de datos de programas o fichas / inconsistencia generalizada | Product owner del módulo M5/M6 | Correo + reunión urgente |

**Información a incluir en el escalamiento:**

- Timestamp del primer síntoma
- Texto del log de error con `correlation_id`
- Resultado de `/health` y `/health/db`
- Número(s) de ficha afectada(s) (`ficha_number`)
- Código(s) de programa afectado(s) (`program_code`)
- Centro de formación afectado (`training_center_id`)
- Servicios downstream impactados (`scheduling-service` si corresponde)
