# Runbook — monitoring-service

> Estado: 🟡 En progreso | Última actualización: 2026-10-24

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
| `DATABASE_URL` | Conexión a `monitoring_db` con el **usuario de aplicación** (miembro de `monitoring_writer`), nunca con el superusuario. Ver [Usuario de base de datos](#usuario-de-base-de-datos). |
| `AMQP_URL` | Conexión RabbitMQ/AMQP para worker, relay y readiness. |
| `JWKS_URL` | JWKS de IAM (`http://iam-api:8080/api/v1/auth/.well-known/jwks.json`) para validar la firma de los JWT. Obligatoria para la API: sin ella los endpoints protegidos responden `503 AUTH_NOT_CONFIGURED`. |
| `JWT_ISSUER` | `iss` esperado. Por defecto `sena-iam-service`; en cada ambiente se inyecta el mismo valor con que corre IAM (`IAM_JWT_ISSUER`). |
| `JWT_AUDIENCE` | `aud` esperado. Vacío por defecto: los access tokens de IAM no llevan `aud`. Ver [Autenticación](#autenticación). |
| `API_HOST` / `API_PORT` | Bind HTTP local o contenedor. |
| `REQUEST_TIMEOUT_SECONDS` | Presupuesto de timeout para operaciones salientes. |
| `READINESS_TIMEOUT_SECONDS` | Timeout de chequeos `/ready`. |
| `OTEL_ENABLED` | Habilita instrumentación OpenTelemetry. |
| `OTEL_SERVICE_NAME` | Nombre de servicio en trazas y métricas. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Base del endpoint OTLP **HTTP** del Collector (`http://otel-collector:4318`); el servicio le agrega `/v1/traces`, `/v1/metrics` y `/v1/logs`. No apuntarla a `:4317` (gRPC): ver [local-setup](../../../10-devops/local-setup.md#gotchas-de-observabilidad--deploy). |
| `DEPLOYMENT_ENVIRONMENT` | Atributo OTel del ambiente. |
| `LOG_LEVEL` | Nivel de logs JSON. |
| `ALERT_WORKER_MODE` | `consumer` o `relay`. |

### Autenticación

monitoring acepta la misma sesión que el resto de los módulos: el access token JWT RS256 que emite `iam-service` ([authentication.md](../../../07-api/authentication.md)). No tiene emisor, llave ni audience propios, y el mismo artefacto con las mismas variables corre en `develop`, `qa`, `staging` y `main` (ADR-022 §6); solo cambian los valores inyectados.

| Verificación | Regla |
|---|---|
| Firma | RS256, con la clave pública del JWKS de IAM (`JWKS_URL`) elegida por el `kid` del token. El cliente cachea el conjunto de claves y lo refresca cuando aparece un `kid` desconocido (IAM publica la clave actual y la anterior durante una rotación; una clave nueva puede tardar hasta 30 s en verse). |
| Expiración | `exp` obligatorio y vigente. |
| Emisor | `iss` igual a `JWT_ISSUER` (por defecto `sena-iam-service`). |
| Sujeto | `sub` obligatorio. |
| Audience | **IAM no emite `aud` en los tokens de usuario**, así que `JWT_AUDIENCE` queda vacío y no se exige audience. Si se configura, `aud` pasa a ser obligatorio y debe coincidir. Con `JWT_AUDIENCE` vacío, un token que sí traiga `aud` se rechaza (falla cerrado): el día que IAM emita un audience hay que configurarlo aquí de forma explícita. |
| RBAC | El claim `features` trae pares `CODE:SCOPE_TYPE`; cada endpoint exige su código `MON_*` (`x-required-feature` del contrato). El sufijo de scope **todavía no se interpreta**: ver [Riesgos conocidos](#riesgos-conocidos). |

Respuestas: sin `Authorization: Bearer`, token inválido, mal firmado, de otro emisor o vencido → `401 UNAUTHORIZED`; feature ausente → `403 FORBIDDEN`; `JWKS_URL` sin configurar → `503 AUTH_NOT_CONFIGURED`; JWKS de IAM inalcanzable → `503 DEPENDENCY_UNAVAILABLE` (la sesión del usuario no es inválida: IAM no responde).

No existe llave pública local, emisor local ni modo sin firma en el servicio; las pruebas firman con una llave descartable y la sirven como JWKS.

### Usuario de base de datos

La API, el `alert-worker` y el relay de Outbox se conectan a `monitoring_db` con el **usuario de aplicación**: un rol con `LOGIN` miembro de `monitoring_writer` (`SELECT/INSERT/UPDATE/DELETE` sobre el esquema `monitoring`, grants de `design-software-monitoring-db/03_dcl`). En el stack local lo crea `design-software-docker-infra/create-app-user.sh` (`APP_DB_USER` / `APP_DB_PASSWORD`, igual que iam, notification, actors y scheduling). El servicio nunca necesita DDL, por lo que no debe recibir el superusuario (`POSTGRES_USER`) ni el dueño del esquema:

```
DATABASE_URL=postgresql+psycopg://<APP_DB_USER>:<APP_DB_PASSWORD>@<host>:5432/<base>
```

Verificación: `SELECT usename FROM pg_stat_activity WHERE datname = '<base>'` solo debe mostrar el usuario de aplicación para las conexiones del servicio, y `SELECT rolsuper FROM pg_roles WHERE rolname = '<usuario>'` debe dar `false`.

## Arranque local

```powershell
python -m pip install -e ".[dev]"
$env:DATABASE_URL="postgresql+psycopg://monitoring:monitoring@localhost:5432/monitoring_db"
$env:AMQP_URL="amqp://guest:guest@localhost:5672/"
$env:JWKS_URL="http://localhost:8080/api/v1/auth/.well-known/jwks.json"
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

## Imágenes de contenedor

Cada deployable tiene su Dockerfile en `deploy/` ([ADR-006](../../../05-architecture/decisions/records/ADR-006-polyglot-stack-strategy.md)):

| Componente | Dockerfile | Proceso |
|------------|------------|---------|
| `monitoring-api` | `deploy/Dockerfile.api` | `uvicorn apps.api.main:app` en el puerto `8000`. |
| `alert-worker` | `deploy/Dockerfile.worker` | `python -m apps.alert_worker.main`. `ALERT_WORKER_MODE=consumer` (por defecto) consume eventos AMQP; `relay` publica el Outbox. |

Las dos imágenes parten de `python:3.11-slim`, instalan las dependencias fijadas en `requirements-runtime.lock` y después el paquete con `--no-deps`, de modo que API y worker corren con las mismas versiones. El worker no abre ningún puerto HTTP. Sin `DATABASE_URL` o sin `AMQP_URL` el proceso falla al arrancar; no hay valores por defecto. El modo `relay` es un contenedor aparte del modo `consumer`: se levanta con la misma imagen y `ALERT_WORKER_MODE=relay`.

> Hasta que `monitoring-service` incorpore `deploy/Dockerfile.worker` (PR #7), el compose de `docker-infra` ejecuta el worker y el relay con la imagen del API (`extends: monitoring-api` más `command`). El comportamiento es el mismo; solo cambia la imagen.

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

La definición Compose de `liquibase-monitoring-contract` usa la imagen `ds-liquibase:latest`, perfil `r6-contract`, volumen del repositorio DB en `/workspace`, `working_dir: /workspace`, dependencia de PostgreSQL saludable y `--changeLogFile=changelog/changelog-contract.yaml`; además fija las tablas de control Liquibase en `public`. Su `--contexts` es el `LIQUIBASE_CONTEXTS` del ambiente seguido de `,r6-contract` (el changeset de CONTRACT lleva ese context; sin él el servicio no aplicaría nada), ver [Contexts de Liquibase por ambiente](../../../10-devops/environments.md#contexts-de-liquibase-por-ambiente). El entrypoint no incluye `update` de forma fija: prepara Liquibase y requiere añadir el comando explícito:

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

## P1 — La API responde 401 o 503 a un usuario con sesión válida

Impacto: el MFE de Monitoring no carga indicadores ni alertas.

1. `401 UNAUTHORIZED` con un token recién emitido por IAM: comparar el `iss` del token con `JWT_ISSUER` (debe ser el `IAM_JWT_ISSUER` con que corre IAM). Si el token trae `aud`, configurar `JWT_AUDIENCE` con ese valor.
2. `503 AUTH_NOT_CONFIGURED`: falta `JWKS_URL` en el servicio.
3. `503 DEPENDENCY_UNAVAILABLE`: monitoring no alcanza el JWKS de IAM. Verificar que `iam-api` responde `GET /api/v1/auth/.well-known/jwks.json` desde la red del servicio. Las claves ya cacheadas siguen sirviendo hasta que el conjunto expira (5 min).
4. `401` solo en tokens nuevos tras una rotación de claves de IAM: el servicio refresca el JWKS al ver un `kid` desconocido, con un mínimo de 30 s entre refrescos.

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

## Riesgos conocidos

- **El scope de los features no se aplica.** monitoring valida el feature (`MON_KPI_VIEW`, `MON_DASHBOARD_OWN`, …) pero ignora el `SCOPE_TYPE` del claim (`OWN_FICHAS`, `TRAINING_CENTER`, `GLOBAL`), así que un instructor con `MON_KPI_VIEW:OWN_FICHAS` ve los datos de todas las fichas. El paso 6 de [authentication.md](../../../07-api/authentication.md) ("extraer `scope_type` y aplicar filtro de datos") queda como HU aparte; hasta entonces el servicio no restringe los datos por propietario ni por centro de formación para ningún usuario que tenga el feature.
- **Códigos de error de autenticación.** El servicio responde `UNAUTHORIZED` / `FORBIDDEN`; [authentication.md](../../../07-api/authentication.md) lista `MISSING_TOKEN`, `TOKEN_INVALID`, `TOKEN_EXPIRED` e `INSUFFICIENT_PERMISSIONS`, y `shared-contracts/errors/error-codes.yaml` lista `UNAUTHENTICATED` y `FORBIDDEN`. Las tres fuentes divergen; unificarlas es una decisión de contratos fuera de esta HU.

## Escalamiento

| Nivel | Responsable | Caso |
|-------|-------------|------|
| L1 | Equipo Monitoring | health, BD, lag, errores de API/worker |
| L2 | Líder técnico Monitoring | reglas KPI, duplicidad, contratos de evento |
| L3 | Arquitectura/Infra | broker, base de datos, cambios de frontera |
| Transferencia | Equipo Notification | entrega EMAIL/IN_APP, retries, DLQ, templates |
