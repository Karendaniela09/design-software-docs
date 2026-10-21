# Runbook — monitoring-service

> Estado: 🟡 En progreso | Última actualización: 2026-10-20

## Componentes operativos

| Componente | Verificación | Objetivo |
|------------|--------------|----------|
| `monitoring-api` | `GET /health` | Liveness HTTP. |
| `monitoring-api` | `GET /ready` | Readiness de BD y broker antes de recibir tráfico. |
| `alert-worker` | proceso + lag AMQP + métricas | Procesar eventos/KPIs sin backlog sostenido. |

No existe un `notification-worker` dentro de este servicio. Incidentes SMTP, `send_status`, DLQ de entrega y Outbox de notificación se atienden con el [runbook de notification-service](../10-notification-service/runbook.md).

## Configuración

La implementación actual es Python/FastAPI y está en evolución. Variables definitivas deben consolidarse en infraestructura/golden template; como mínimo se requieren las conexiones del servicio a:

- `monitoring_db`;
- broker AMQP para el worker cuando se conecte;
- configuración de JWT/JWKS para API;
- OpenTelemetry Collector.

**No configurar credenciales SMTP en Monitoring.**

Variables operativas esperadas:

| Variable | Uso |
| --- | --- |
| `DATABASE_URL` | Conexión a `monitoring_db`. |
| `AMQP_URL` | Conexión RabbitMQ/AMQP para worker, relay y readiness. |
| `JWKS_URL` | JWKS de IAM para validación JWT. |
| `API_HOST` / `API_PORT` | Bind HTTP local o contenedor. |
| `REQUEST_TIMEOUT_SECONDS` | Presupuesto de timeout para operaciones salientes. |
| `READINESS_TIMEOUT_SECONDS` | Timeout de chequeos `/ready`. |
| `OTEL_ENABLED` | Habilita instrumentación OpenTelemetry. |
| `OTEL_SERVICE_NAME` | Nombre de servicio en trazas y métricas. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Endpoint OTLP HTTP del Collector. |
| `DEPLOYMENT_ENVIRONMENT` | Atributo OTel del ambiente. |
| `LOG_LEVEL` | Nivel de logs JSON. |
| `ALERT_WORKER_MODE` | `consumer` o `relay`. |

## Arranque local

```powershell
python -m pip install -e ".[dev]"
$env:DATABASE_URL="postgresql+psycopg://monitoring:monitoring@localhost:5432/monitoring_db"
$env:AMQP_URL="amqp://guest:guest@localhost:5672/"
python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000
```

Worker:

```powershell
$env:ALERT_WORKER_MODE="consumer"
python -m apps.alert_worker.main
```

Relay Outbox:

```powershell
$env:ALERT_WORKER_MODE="relay"
python -m apps.alert_worker.main
```

## Migraciones

Aplicar los changelogs de `design-software-monitoring-db` antes de levantar API/worker. Validar que existan:

```sql
SELECT to_regclass('monitoring.kpi_tracking');
SELECT to_regclass('monitoring.generated_alert');
SELECT to_regclass('monitoring.outbox');
```

## Migración R6 — TEXT a JSONB

Referencia arquitectónica: [ADR-013](../../../05-architecture/decisions/records/ADR-013-monitoring-r6-text-jsonb-migration.md).

### Preparación

1. Confirmar la base de destino y que no sea una base compartida para una prueba destructiva.
2. Obtener y comprobar un respaldo recuperable de PostgreSQL.
3. Verificar disponibilidad de PostgreSQL y acceso al esquema `monitoring`.
4. Ejecutar `liquibase validate` con el repositorio `design-software-monitoring-db` y confirmar la versión de Liquibase compatible con el pipeline.
5. Identificar escritores antiguos que solo conozcan `specific_actions TEXT`; no autorizar CONTRACT mientras puedan escribir.
6. Confirmar que la versión del servicio contiene `specific_actions_compat.py` y que el cambio cuenta con autorización operativa.

### EXPAND y BACKFILL

EXPAND y BACKFILL pertenecen a `changelog/changelog-master.yaml`, mediante los changesets `r6-monitoring-expand-specific-actions-v2-991` y `r6-monitoring-backfill-specific-actions-v2-992`.

Desde `design-software-docker-infra`, con variables de entorno cargadas, el patrón de ejecución es:

```powershell
docker compose --profile tooling run --rm liquibase-monitoring update
```

Verificar la forma del esquema y la equivalencia sin modificar datos:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'monitoring'
  AND table_name = 'improvement_plan'
  AND column_name IN ('specific_actions', 'specific_actions_v2')
ORDER BY ordinal_position;

SELECT count(*) AS inconsistentes
FROM monitoring.improvement_plan
WHERE specific_actions_v2 IS NULL
   OR specific_actions_v2->'actions'->0->>'text' IS DISTINCT FROM specific_actions;
```

El resultado esperado durante la transición es TEXT `NOT NULL`, JSONB nullable y cero filas inconsistentes después de BACKFILL. El riesgo principal son escrituras concurrentes de versiones antiguas entre BACKFILL y CONTRACT; repetir BACKFILL solo llena v2 nula y no corrige por sí mismo divergencias posteriores.

Cuando existan escritores antiguos, detenerlos antes de CONTRACT y ejecutar el SQL operativo `01_ddl/04_alter/r6_sync_specific_actions_v2.sql` del commit DB validado. El script solo resincroniza documentos JSONB con `version: 1`, un único elemento `actions[0].text` de tipo string y texto TEXT no nulo; no sobrescribe documentos fuera de ese formato. Registrar los conteos `discrepancias_before` y `discrepancias_after`, y exigir cero después de la sincronización.

### CONTRACT

CONTRACT usa `changelog/changelog-contract.yaml` y el changeset `r6-monitoring-contract-specific-actions-v2-993`, separado del changelog habitual. Sus precondiciones bloquean datos nulos, documentos con versión/forma no soportada y diferencias entre TEXT y JSONB.

La definición Compose de `liquibase-monitoring-contract` usa la imagen `ds-liquibase:latest`, perfil `r6-contract`, volumen del repositorio DB en `/workspace`, `working_dir: /workspace`, dependencia de PostgreSQL saludable y `--changeLogFile=changelog/changelog-contract.yaml`; además fija las tablas de control Liquibase en `public`. El entrypoint no incluye `update` de forma fija: prepara Liquibase y requiere añadir el comando explícito:

```powershell
docker compose --profile r6-contract run --rm liquibase-monitoring-contract update
```

El perfil evita que se incluya en un arranque convencional sin activación explícita, pero activar el perfil no sustituye la autorización ni las comprobaciones de equivalencia, respaldo, base de destino y ausencia de escritores antiguos. No ejecutar CONTRACT solo porque el contenedor pueda arrancar.

### ROLLBACK

Considerar rollback ante una divergencia detectada antes de CONTRACT, un fallo de compatibilidad del servicio o una decisión operativa de restaurar la representación anterior. Los scripts disponibles son `r6_backfill_specific_actions_v2.rollback.sql`, `r6_expand_specific_actions_v2.rollback.sql` y `r6_contract_specific_actions_v2.rollback.sql` en `design-software-monitoring-db/05_rollbacks/01_ddl/04_alter/`. El resultado esperado del rollback CONTRACT es `specific_actions TEXT NOT NULL` y `specific_actions_v2 JSONB NULL`; cualquier evidencia con `JSONB NOT NULL` debe marcarse como histórica y reconciliarse antes de aprobar.

Antes de ejecutarlo, identificar la fase real, respaldar el estado actual y verificar que cada documento JSONB use `version: 1`, un único elemento en `actions` y `actions[0].text` string. La reconstrucción TEXT no es segura para múltiples acciones, versiones futuras, documentos inválidos o información adicional fuera de `actions[0].text`; esos datos podrían perderse al volver a TEXT. Tras el rollback, comprobar columnas, nulabilidad, equivalencia extraída y operaciones HTTP.

### Seguridad operativa

- No ejecutar CONTRACT sobre entornos compartidos sin autorización explícita.
- No destruir volúmenes ni usar `down -v`.
- No utilizar bases de producción en pruebas destructivas.
- No exponer credenciales en comandos, logs o documentación.
- No ejecutar rollback sin verificar la representación efectiva de los datos.
- La exigencia R6 de rollback en DEV, QA, STAGING y PROD simulada permanece pendiente hasta conservar evidencia trazable por ambiente.
- La identidad Liquibase de los changesets 991/992/993 debe coincidir con el historial aplicado; no editar `DATABASECHANGELOG` manualmente para ocultar diferencias.
- El workflow de integración R6 debe reportar aprobadas, fallidas y omitidas por separado; un CI verde con pruebas omitidas no demuestra compatibilidad PostgreSQL/HTTP.

## Verificación de readiness

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
Invoke-RestMethod http://localhost:8000/api/v1/ready
```

`/ready` debe responder `ready` solo si BD y broker están disponibles.

## P0 — `monitoring_db` no responde

Impacto: no se registran/consultan KPIs ni alertas.

1. validar conectividad PostgreSQL;
2. revisar pool, locks y capacidad;
3. evitar consumir/acknowledge eventos si no puede persistirse el resultado;
4. recuperar BD y verificar backlog del worker.

## P1 — Lag del `alert-worker`

Impacto: KPIs/alertas se calculan tarde. Notification puede estar sano pero no recibirá nuevos `monitoring.alert.triggered` hasta que Monitoring procese el backlog.

1. revisar estado del proceso;
2. revisar errores de deserialización/contrato;
3. revisar latencia de BD;
4. revisar profundidad de cola y DLQ de Monitoring;
5. escalar consumidores solo si la semántica de orden/idempotencia lo permite.

## P1 — Mensajes en DLQ de Monitoring

1. identificar routing key `monitoring.alert-worker.dlq`;
2. capturar `event_id`, `event_type`, `correlation_id` y motivo del fallo;
3. corregir causa raíz (contrato, catálogo faltante, BD, regla KPI);
4. reprocesar manualmente solo cuando la idempotencia por `source_event_id` esté verificada;
5. no mover mensajes a colas de Notification.

## Replay de Outbox

Consultar pendientes:

```sql
SELECT id, event_id, event_type, created_at
FROM monitoring.outbox
WHERE published_at IS NULL
ORDER BY created_at;
```

Ejecutar relay:

```powershell
$env:ALERT_WORKER_MODE="relay"
python -m apps.alert_worker.main
```

El relay marca `published_at` únicamente tras ack del broker.

## P1 — Alertas duplicadas

```sql
SELECT source_event_id, count(*)
FROM monitoring.generated_alert
WHERE source_event_id IS NOT NULL
GROUP BY source_event_id
HAVING count(*) > 1;
```

Corregir deduplicación antes de reprocesar mensajes. No “compensar” eliminando notificaciones: ese dato pertenece a otro servicio.

## Resolver una alerta

Usar el endpoint/caso de uso de `monitoring-api` correspondiente. La resolución cambia el estado de `generated_alert`; no modifica registros de Notification.

## Recalcular KPI

El procedimiento de recalculo debe publicar solo los eventos de monitoreo que correspondan y mantener idempotencia. Una recalculación no debe invocar directamente a Notification.

## Incidente de notificación reportado desde una alerta

Si la alerta existe en Monitoring pero el usuario no recibió aviso:

1. comprobar que `monitoring.alert.triggered` fue publicado con `event_id` válido;
2. capturar `event_id`/`correlation_id`;
3. transferir investigación al runbook de `notification-service`;
4. **no** consultar ni modificar tablas de `notification_db` desde Monitoring.

## Escalamiento

| Nivel | Responsable | Caso |
|-------|-------------|------|
| L1 | Equipo Monitoring | health, BD, lag, errores de API/worker |
| L2 | Líder técnico Monitoring | reglas KPI, duplicidad, contratos de evento |
| L3 | Arquitectura/Infra | broker, base de datos, cambios de frontera |
| Transferencia | Equipo Notification | entrega EMAIL/IN_APP, retries, DLQ, templates |
