# Runbook — document-service

> Estado: 🟢 Estable | Última actualización: 2026-10-26

Servicio transversal de generación y ciclo de vida de documentos. Recibe solicitudes de otros servicios (vía eventos o API), genera PDFs y archivos estructurados a partir de plantillas Handlebars, y los almacena en object storage. Nunca almacena binarios en base de datos.

**Componentes desplegables:**

| Componente | Puerto | Rol |
|------------|--------|-----|
| `document-api` | 8007 | REST API: consulta, descarga y versionado de documentos |
| `template-api` | 8007 (`/templates`) | CRUD de plantillas HTML/Handlebars |
| `document-lifecycle-worker` | worker | Consume eventos externos; orquesta ciclo de vida |
| `pdf-renderer-worker` | worker | Renderiza plantillas y sube binarios a MinIO/S3 |
| `document-outbox-dispatcher` | worker | Entrega eventos confirmados desde PostgreSQL a RabbitMQ |

---

## Healthcheck

| Endpoint | Respuesta esperada | SLO |
|----------|--------------------|-----|
| `GET /health` | `200 { "status": "ok" }` | < 200 ms |
| `GET /health/db` | `200` cuando `document_db` acepta conexiones | < 500 ms |
| `GET /health/storage` | `200` cuando object storage (MinIO/S3) es accesible | < 1 s |

**Verificación manual:**

```bash
curl -sf http://document-service:8007/health | jq .
curl -sf http://document-service:8007/health/db | jq .
curl -sf http://document-service:8007/health/storage | jq .
```

**Verificación directa de object storage:**

```bash
# DEV/QA (MinIO)
mc alias set minio "$MINIO_URL" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY"
mc ls minio/"$S3_BUCKET"

# Prod (AWS S3)
aws s3 ls s3://"$S3_BUCKET" --max-items 5
```

**SLO de disponibilidad:** 99% mensual (máximo ~7.3 h de downtime/mes).

## Entrega de eventos y recuperación de la DLQ

El `document-outbox-dispatcher` ejecuta `python -m apps.outbox_dispatcher.main`. Requiere
`DB_URL` (o el alias `DATABASE_URL`) y `AMQP_URL`; opcionalmente usa `EVENTS_EXCHANGE`
(`document-events` por defecto), `OUTBOX_POLL_SECONDS` (1 segundo) y `LOG_LEVEL`. No elimine filas
pendientes de `document.event_outbox`: un fallo del broker conserva el evento y aplica backoff para
reintentar.

Para revisar pendientes:

```sql
SELECT event_id, event_type, attempts, available_at, last_error
FROM document.event_outbox
WHERE published_at IS NULL
ORDER BY available_at, created_at;
```

Para revisar mensajes fallidos, inspeccione la cola durable `pdf-renderer.dlq` y su cabecera
`x-failure-reason`. Después de corregir la causa, reprocesar explícitamente desde el entorno del
servicio:

```bash
AMQP_URL="$AMQP_URL" DLQ_QUEUE=pdf-renderer.dlq \
  GENERATION_QUEUE=document-generation-queue \
  python -m apps.replay_dlq.main --limit 1
```

El comando conserva el cuerpo y `correlation_id`, publica con confirmación y solo entonces
confirma el mensaje original de la DLQ. Aumente `--limit` únicamente después de revisar el volumen y
la causa de los mensajes. La generación repetida es idempotente mediante `document.message_inbox`
y `document_version.correlation_id`.

---

## Variables de entorno requeridas

| Variable | Descripción | Valores válidos / Ejemplo |
|----------|-------------|--------------------------|
| `DATABASE_URL` | Cadena de conexión PostgreSQL a `document_db` | `postgresql://user:pass@host:5432/document_db` |
| `DATABASE_POOL_MIN` | Conexiones mínimas en el pool | `2` |
| `DATABASE_POOL_MAX` | Conexiones máximas en el pool | `10` |
| `STORAGE_PROVIDER` | Proveedor de object storage activo | `MINIO` (dev/QA) \| `S3` (prod) |
| `MINIO_URL` | URL del servidor MinIO (solo cuando `STORAGE_PROVIDER=MINIO`) | `http://minio:9000` |
| `MINIO_ACCESS_KEY` | Access key de MinIO | (secreto) |
| `MINIO_SECRET_KEY` | Secret key de MinIO | (secreto) |
| `S3_BUCKET` | Nombre del bucket en S3 o MinIO | `documents-prod` |
| `S3_REGION` | Región AWS (solo cuando `STORAGE_PROVIDER=S3`) | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | Credencial AWS (solo cuando `STORAGE_PROVIDER=S3`) | (secreto) |
| `AWS_SECRET_ACCESS_KEY` | Credencial AWS (solo cuando `STORAGE_PROVIDER=S3`) | (secreto) |
| `PDF_RENDERER_URL` | URL interna del motor de renderizado PDF | `http://pdf-renderer:3000` |
| `IAM_SERVICE_URL` | URL base de `iam-service` para validación de JWT | `http://iam-service:8001` |
| `KAFKA_BROKERS` | Lista de brokers Kafka | `kafka:9092` |
| `KAFKA_CONSUMER_GROUP` | Grupo de consumo para eventos externos | `document-service-cg` |
| `KAFKA_TOPIC_PUBLISH` | Topic de publicación de eventos propios | `document-events` |
| `KAFKA_TOPIC_SCHEDULING` | Topic de eventos de scheduling a consumir | `scheduling-events` |
| `KAFKA_TOPIC_ACADEMIC` | Topic de eventos académicos a consumir | `academic-events` |
| `DOCUMENT_GENERATION_QUEUE` | Nombre de la cola interna de generación | `document-generation-queue` |
| `JWT_SECRET` | Clave de verificación de tokens JWT | (secreto) |
| `PORT` | Puerto de escucha del API | `8007` |
| `LOG_LEVEL` | Nivel de logging | `info` |
| `ALERT_WEBHOOK_URL` | Webhook para alertas operativas post-fallo definitivo | `https://hooks.slack.com/...` |

---

## Alertas críticas

| Alerta | Condición | Severidad | Acción inmediata |
|--------|-----------|-----------|------------------|
| Object storage no accesible | `/health/storage` retorna 5xx o timeout; error de conexión a S3/MinIO | P0 | Ningún documento puede generarse ni descargarse. Ver [Falla de object storage](#falla-de-object-storage) |
| BD no responde | Timeout en `document_db` > 5 s o `/health/db` retorna 5xx | P0 | Ver [Falla de base de datos](#falla-de-base-de-datos) |
| pdf-renderer-worker detenido | Worker sin heartbeat > 5 min; cola `document-generation-queue` creciendo sin consumidores | P1 | Reiniciar worker; ver [pdf-renderer-worker caído](#pdf-renderer-worker-caido) |
| Cola de generación creciendo | `document-generation-queue` depth > 100 mensajes | P2 | Escalar instancias de `pdf-renderer-worker`; ver [Backlog de generación](#backlog-de-generacion) |
| Documentos en GENERATION_FAILED | Documentos con `status = 'GENERATION_FAILED'` en las últimas 2 h | P1 | Ver [Re-trigger de documentos fallidos](#re-trigger-de-generacion-fallida) |
| document-lifecycle-worker detenido | Worker sin actividad > 10 min; eventos de entrada (`scheduling-events`, `academic-events`) no procesados | P1 | Reiniciar worker; verificar consumer group Kafka |
| Servicio no responde | `/health` retorna 5xx o sin respuesta > 1 min | P0 | Reiniciar pod/contenedor; revisar logs de arranque |

---

## Procedimientos comunes

### Re-trigger de generacion fallida

Usar cuando un documento quedó en `status = 'GENERATION_FAILED'` tras agotar los 3 reintentos del `pdf-renderer-worker`.

**Diagnóstico previo:**

```sql
-- Identificar documentos fallidos recientes
SELECT id, title, domain, owner_service, owner_entity_id,
       status, created_at, updated_at
FROM document
WHERE status = 'GENERATION_FAILED'
ORDER BY updated_at DESC
LIMIT 20;
```

Revisar el campo `failure_reason` si está disponible en el registro, y los logs del `pdf-renderer-worker` para el `document_id` correspondiente:

```bash
# Buscar en los logs del worker el document_id
kubectl logs -l app=pdf-renderer-worker --since=2h | grep '<DOCUMENT_UUID>'
# o con docker
docker logs pdf-renderer-worker 2>&1 | grep '<DOCUMENT_UUID>'
```

**Re-trigger manual (vía API interna):**

```bash
# Si el servicio expone un endpoint de re-trigger
curl -X POST http://document-service:8007/documents/<DOCUMENT_UUID>/retry \
  -H "Authorization: Bearer <INTERNAL_TOKEN>"
```

**Re-trigger manual (vía BD + reencolar):**

Si no hay endpoint de retry disponible:

```sql
BEGIN;

-- Resetear el estado del documento para que sea reelegible
UPDATE document
SET
    status     = 'GENERATING',
    updated_at = NOW()
WHERE id     = '<DOCUMENT_UUID>'
  AND status = 'GENERATION_FAILED';

COMMIT;
```

Luego encolar manualmente el mensaje en `document-generation-queue` con el payload:

```json
{
  "document_id": "<DOCUMENT_UUID>",
  "template_code": "<TEMPLATE_CODE>",
  "data_payload": { }
}
```

**Causa raíz frecuente:** Plantilla no encontrada (`template_code` inválido). En ese caso no hay reintentos automáticos; verificar que la plantilla existe y tiene `is_active = true` antes de re-encolar.

```sql
SELECT id, code, name, output_type, version, is_active
FROM document_template
WHERE code = '<TEMPLATE_CODE>';
```

---

### Recuperar documento de object storage cuando se perdio el metadata en BD

Usar cuando el registro de `document` fue eliminado accidentalmente de la BD o la BD fue restaurada a un punto anterior y se perdieron registros recientes, pero los binarios en MinIO/S3 siguen existentes.

**Paso 1 — Listar los objetos huerfanos en object storage:**

```bash
# DEV/QA (MinIO) — listar por prefijo de dominio
mc ls minio/"$S3_BUCKET"/documents/ --recursive | grep '<DOMINIO_O_FECHA>'

# Prod (S3)
aws s3 ls s3://"$S3_BUCKET"/documents/ --recursive | grep '<DOMINIO_O_FECHA>'
```

**Paso 2 — Identificar el storage_key del objeto a recuperar:**

El `storage_key` sigue el patrón: `documents/<domain>/<year>/<month>/<document_id>.pdf`

Ejemplo: `documents/scheduling/2026/06/doc_01HXYZ123456.pdf`

**Paso 3 — Reconstruir el registro en BD:**

```sql
BEGIN;

INSERT INTO document
    (id, template_id, title, domain, owner_service, owner_entity_id,
     storage_key, mime_type, size_bytes, status, created_by, created_at, updated_at)
VALUES
    ('<DOCUMENT_UUID_ORIGINAL_O_NUEVO>',
     NULL,                            -- NULL si no se conoce la plantilla
     'Documento recuperado — <DESCRIPCION>',
     '<DOMAIN>',                      -- SCHEDULE | FICHA | CERTIFICATE | ACTOR | REPORT
     '<OWNER_SERVICE>',
     '<OWNER_ENTITY_UUID>',
     'documents/<domain>/<year>/<month>/<filename>.pdf',
     'application/pdf',
     <SIZE_BYTES>,                    -- obtener del objeto en storage: mc stat / aws s3api head-object
     'AVAILABLE',
     '<CREATED_BY_UUID>',             -- UUID del operador que ejecuta la recuperación
     NOW(),
     NOW());

COMMIT;
```

**Obtener size_bytes del objeto:**

```bash
# MinIO
mc stat minio/"$S3_BUCKET"/'documents/<domain>/<year>/<month>/<filename>.pdf' | grep Size

# S3
aws s3api head-object \
  --bucket "$S3_BUCKET" \
  --key 'documents/<domain>/<year>/<month>/<filename>.pdf' \
  | jq '.ContentLength'
```

**Paso 4 — Verificar que el documento es accesible:**

```bash
curl -I http://document-service:8007/documents/<DOCUMENT_UUID>
```

**Consideraciones:** Si el `document_id` original no es conocido, asignar un nuevo UUID. Informar al servicio solicitante (`owner_service`) para que actualice la referencia a ese documento.

---

## Escenarios de falla

### Falla de object storage

**Síntoma:** `/health/storage` retorna 503; descarga de documentos retorna 500; generación se detiene completamente; logs muestran `connection refused` o `timeout` hacia MinIO/S3.

**Impacto:** Crítico. Ningún documento puede generarse ni descargarse mientras el storage no esté disponible. Los documentos con `status = 'GENERATING'` quedarán bloqueados.

**Diagnóstico:**

```bash
# DEV/QA — verificar MinIO
curl -sf "$MINIO_URL"/minio/health/live
mc admin info minio/

# Prod — verificar conectividad S3
aws s3 ls s3://"$S3_BUCKET" --max-items 1
```

**Acciones:**

1. Si MinIO no responde en DEV/QA: reiniciar el contenedor/pod de MinIO; verificar volumen persistente.
2. Si S3 no responde en prod: verificar el dashboard de AWS S3 en busca de incidentes regionales; verificar que las credenciales (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) no hayan expirado.
3. Una vez restaurado el storage: los documentos en `GENERATING` que fallaron por esta causa deben ser re-encolados. Ver [Re-trigger de generacion fallida](#re-trigger-de-generacion-fallida).
4. Si el bucket fue eliminado accidentalmente: escalar a L3 (infraestructura/cloud) inmediatamente.

---

### pdf-renderer-worker caido

**Síntoma:** Worker sin heartbeat > 5 min; la cola `document-generation-queue` crece sin que se procesen mensajes; documentos atascados en `status = 'GENERATING'` indefinidamente.

**Diagnóstico:**

```bash
# Verificar estado del worker
kubectl get pods -l app=pdf-renderer-worker
kubectl logs -l app=pdf-renderer-worker --previous --tail=100

# Verificar depth de la cola
# (comando varía según el broker de cola utilizado)
```

```sql
-- Documentos atascados en GENERATING por más de 10 minutos
SELECT id, title, domain, owner_service, created_at,
       NOW() - created_at AS tiempo_atascado
FROM document
WHERE status = 'GENERATING'
  AND created_at < NOW() - INTERVAL '10 minutes'
ORDER BY created_at;
```

**Acciones:**

1. Reiniciar el pod/contenedor del `pdf-renderer-worker`.
2. Verificar que `PDF_RENDERER_URL` apunte a un motor de renderizado disponible.
3. Si el worker sigue fallando al arrancar: revisar logs de inicio; puede ser un problema de memoria (OOM) o dependencia no disponible.
4. Una vez el worker esté operativo, los mensajes en cola se procesarán automáticamente. Los documentos atascados en `GENERATING` deben ser re-encolados manualmente si el worker no los retoma.

---

### Backlog de generacion

**Síntoma:** Cola `document-generation-queue` depth > 100 mensajes; generación de documentos con retraso > 5 min desde la solicitud.

**Causa probable:** Pico de demanda (muchas fichas abiertas simultáneamente, horarios publicados en lote) o lentitud del motor de renderizado.

**Acción inmediata:** Escalar instancias de `pdf-renderer-worker`:

```bash
# Kubernetes
kubectl scale deployment pdf-renderer-worker --replicas=<N>
# Recomendación: escalar de 1 a 3 réplicas como primer paso
```

**Consideración:** Cada réplica consume conexiones a `document_db` y al motor de renderizado. Verificar que `DATABASE_POOL_MAX` y la capacidad del motor soporten N réplicas simultáneas.

---

### Falla de base de datos

**Síntoma:** `/health/db` retorna 503; peticiones al API retornan 500; logs muestran errores de conexión a `document_db`.

**Diagnóstico y acciones:**

```bash
psql "$DATABASE_URL" -c "SELECT 1;"
psql "$DATABASE_URL" -c "
  SELECT count(*), state
  FROM pg_stat_activity
  WHERE datname = 'document_db'
  GROUP BY state;"
```

1. Si hay agotamiento de conexiones: reducir `DATABASE_POOL_MAX` y reiniciar. Escalar a DBA si hay conexiones zombies.
2. Si PostgreSQL no responde: escalar a DBA de guardia. El servicio no puede operar sin BD.
3. Tras restaurar la BD: verificar documentos en `GENERATING` que hayan quedado sin resolución durante la outage.

---

### Plantilla no encontrada en generacion masiva

**Síntoma:** Lote de documentos con `status = 'GENERATION_FAILED'`; logs del worker muestran `template_code not found` o `template inactive`.

**Diagnóstico:**

```sql
-- Identificar plantillas referenciadas que no existen o están inactivas
SELECT DISTINCT d.template_id,
       dt.code,
       dt.is_active,
       COUNT(d.id) AS documentos_fallidos
FROM document d
LEFT JOIN document_template dt ON dt.id = d.template_id
WHERE d.status = 'GENERATION_FAILED'
GROUP BY d.template_id, dt.code, dt.is_active;
```

**Acciones:**

1. Si la plantilla existe pero `is_active = false`: reactivarla (`UPDATE document_template SET is_active = true WHERE code = '<CODE>';`) y re-encolar los documentos fallidos.
2. Si la plantilla no existe: crear o importar la plantilla correcta mediante `template-api`, luego re-encolar.
3. No re-encolar sin resolver la causa raíz; los reintentos fallarán inmediatamente y no generarán backoff.

---

## Escalamiento

| Nivel | Condición para escalar | A quién |
|-------|------------------------|---------|
| **L1 — Operaciones** | Servicio caído; worker detenido; storage no accesible; cola > 100 mensajes | Equipo de guardia de plataforma |
| **L2 — Ingeniería backend** | Fallo repetido en generación con causa desconocida; comportamiento inesperado en versionado; corrupción de metadatos en `document_db` | Equipo backend responsable del servicio |
| **L3 — Infraestructura / Cloud** | Bucket S3 eliminado o inaccesible; fallo de replicación de MinIO; necesidad de restaurar snapshot de object storage; problemas de IAM/permisos en AWS | Equipo de infraestructura o cloud |
| **L4 — DBA** | Problemas de rendimiento en PostgreSQL; migración fallida; necesidad de restaurar `document_db` a punto anterior | DBA de guardia |
| **L5 — Dominio** | Decisiones sobre retención de documentos, política de archivado, requerimientos legales sobre versiones | Área jurídica o coordinación académica |

**Canal de alertas:** Configurar `ALERT_WEBHOOK_URL` con el webhook del canal de operaciones en Slack/Teams. El `pdf-renderer-worker` publica alertas automáticamente tras fallo definitivo (3 reintentos agotados).

**Invariante crítica:** Los binarios de documentos nunca se almacenan en `document_db`. Solo `storage_key` referencia el archivo. Ante cualquier operación de limpieza de BD, verificar que los binarios en object storage sigan siendo accesibles.
