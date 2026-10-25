# Runbook — notification-service

> Estado: 🟡 En progreso | Última actualización: 2026-10-24

## Componentes

| Componente | Puerto | Health | Readiness |
|------------|--------|--------|-----------|
| `notification-api` | `8080` por defecto | `GET /health` y `GET /api/v1/health` | `GET /ready` y `GET /api/v1/ready` (DB) |
| `notification-worker` | `8081` por defecto para health server | `GET /health` | `GET /ready` (DB + broker) |

`notification-api` sirve las rutas del contrato bajo `/api/v1` (el `servers` del contrato, ADR-022 §3). `/health` y `/ready`
siguen también en la raíz porque el edge enruta `/notification/health` y `/notification/ready` como rutas exactas y quita el
prefijo `/notification`. Las rutas de negocio sin `/api/v1` responden `404`. El health server del worker no es parte del
contrato y no cambia.

```bash
curl -sf http://localhost:8080/health
curl -sf http://localhost:8080/api/v1/health
curl -sf http://localhost:8080/ready | jq .
curl -sf http://localhost:8080/api/v1/ready | jq .
curl -sf http://localhost:8081/ready | jq .
```

## Variables de entorno

### API

| Variable | Requerida | Default | Descripción |
|----------|-----------|---------|-------------|
| `NOTIFICATION_DB_DSN` | Sí | — | DSN PostgreSQL. |
| `IAM_JWT_ISSUER` | Sí | — | `iss` esperado en el token de acceso (`sena-iam-service`). Sin default: el proceso no arranca sin ella. |
| `IAM_JWKS_URL` | Sí | — | JWKS de IAM (`.../api/v1/auth/.well-known/jwks.json`). `https`, o `http` solo en loopback o en un host de la lista siguiente. Sin default. |
| `NOTIFICATION_JWKS_HTTP_ALLOWED_HOSTS` | No | vacía | Hosts exactos, separados por comas, que pueden servir el JWKS por `http` desde la red interna (p. ej. `iam-api`). Vacía = solo `https` o loopback. Una entrada mal formada detiene el arranque. |
| `PORT` | No | `8080` | Puerto HTTP. |
| `NOTIFICATION_SMTP_ADDR` | No en API actual | `mailhog:1025` | SMTP para solicitud manual que entrega inmediatamente. |
| `NOTIFICATION_SMTP_FROM` | No | `notifications@sena.local` | Remitente. |
| `NOTIFICATION_DEPLOYMENT_ENVIRONMENT` | No | `develop` | Ambiente OTel. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | No | `localhost:4317` | Collector OTLP/gRPC. |
| `OTEL_EXPORTER_OTLP_INSECURE` | No | `true` | Transporte OTLP local. |

### Worker

| Variable | Requerida | Default | Descripción |
|----------|-----------|---------|-------------|
| `NOTIFICATION_DB_DSN` | Sí | — | DSN PostgreSQL. |
| `NOTIFICATION_AMQP_URL` | Sí | — | URL RabbitMQ. |
| `NOTIFICATION_SMTP_ADDR` | Sí | — | Host:puerto SMTP. |
| `NOTIFICATION_SMTP_FROM` | No | `notifications@sena.local` | Remitente. |
| `NOTIFICATION_RECIPIENT_STUB_EMAIL` | Solo desarrollo | `dev-notifications@sena.local` | Stub temporal. Debe deshabilitarse en QA/Staging/Main; producción no depende síncronamente de Actors. |
| `NOTIFICATION_RETRY_MAX_ATTEMPTS` | No | `3` | Máximo de intentos. |
| `NOTIFICATION_RETRY_INITIAL_INTERVAL_MS` | No | `500` | Backoff inicial. |
| `NOTIFICATION_RETRY_MAX_INTERVAL_MS` | No | `30000` | Backoff máximo. |
| `WORKER_HEALTH_PORT` | No | `8081` | Puerto health/readiness del worker. |
| `NOTIFICATION_DEPLOYMENT_ENVIRONMENT` | No | `develop` | Ambiente OTel. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | No | `localhost:4317` | Collector. |

> DSN, AMQP y credenciales SMTP se gestionan como secretos. No commitear valores reales.

## Verificación rápida

### Solicitud manual

Las rutas de negocio exigen un token de IAM con `NOTIFICATION_SEND` (envío) o `NOTIFICATION_VIEW` (consulta); sin token
responden `401`. `$TOKEN` es un access token vigente de IAM con esa feature.

```bash
curl -i -X POST http://localhost:8080/api/v1/notifications \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "recipient_id": "3a286fa0-3fdb-48d5-baf2-0dfd0199a542",
    "recipient_email": "aprendiz@example.invalid",
    "channel": "EMAIL",
    "subject": "Prueba de notificación",
    "source_service": "manual-check"
  }'
```

Esperado: `202 Accepted` con el body `SentNotification` del contrato (incluye `recipient_email` y `created_at`).

### Consulta puntual

```bash
curl -i -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/v1/notifications/<UUID>
```

## P1 — La API responde 401, 403 o 503 en las rutas de negocio

| Respuesta | Causa probable | Qué hacer |
|-----------|----------------|-----------|
| `401` `MISSING_TOKEN` | El cliente no envía `Authorization: Bearer <jwt>` (o usa otro esquema). | Corregir el cliente. |
| `401` `TOKEN_INVALID` | Token malformado, firma de otra clave, `kid` fuera del JWKS, algoritmo distinto de RS256 o `iss` distinto de `IAM_JWT_ISSUER`. | Comparar `iss` del token con `IAM_JWT_ISSUER` y el `kid` con el JWKS de IAM. |
| `401` `TOKEN_EXPIRED` | Access token vencido (TTL 15 min). | Renovar con `POST /auth/refresh`. |
| `403` `INSUFFICIENT_PERMISSIONS` | Token válido sin `NOTIFICATION_SEND` (POST) o `NOTIFICATION_VIEW` (GET) en `features`. | Revisar los grants del rol en IAM. Hoy IAM no emite esas features (ver la brecha en [contract.md](./components/notification-api/contract.md#seguridad)). |
| `503` `DEPENDENCY_UNAVAILABLE` | El servicio no alcanza el JWKS de IAM (`IAM_JWKS_URL`): la solicitud se rechaza, nunca se deja pasar. | Verificar que IAM responde el JWKS desde el contenedor y, si es `http`, que el host está en `NOTIFICATION_JWKS_HTTP_ALLOWED_HOSTS`. |

Un `503` **no** es un token inválido: no pedir al usuario que vuelva a iniciar sesión hasta confirmar que el JWKS responde.
Si el proceso no arranca con `IAM_JWT_ISSUER is required`, `IAM_JWKS_URL is required` o `jwks url must use https ...`,
falta o está mal la variable correspondiente.

## P0 — Base de datos no disponible

**Síntoma:** `/ready` devuelve 503 o API/worker no arrancan.

1. validar `NOTIFICATION_DB_DSN`;
2. ejecutar `SELECT 1` con el mismo usuario;
3. revisar pool/conectividad;
4. no reenviar mensajes manualmente hasta recuperar idempotencia persistente.

## P1 — Broker no disponible

**Síntoma:** readiness del worker 503, consumo detenido.

1. validar `NOTIFICATION_AMQP_URL`;
2. revisar conexiones/colas/exchanges en RabbitMQ;
3. recuperar broker;
4. confirmar que el backlog disminuye; no borrar la cola.

## P1 — Fallos SMTP

```sql
SELECT send_status, count(*)
FROM notification.sent_notification
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY send_status;
```

1. revisar conectividad a `NOTIFICATION_SMTP_ADDR`;
2. validar secreto/relay SMTP si aplica;
3. revisar `failure_reason` sin exponer PII;
4. corregir dependencia y reprocesar desde la DLQ solo después de validar la causa.

## Reproceso de DLQ

Reglas:

- no modificar `event_id` para “evitar” deduplicación;
- un evento con estado `SENT` debe ser no-op;
- un evento `FAILED` puede reintentarse;
- documentar quién reprocesó, cuándo y por qué.

## Outbox estancado

```sql
SELECT count(*) AS pending_outbox
FROM notification.outbox
WHERE published_at IS NULL
  AND created_at < NOW() - INTERVAL '5 minutes';
```

Si crece:

1. verificar broker;
2. revisar logs del relay;
3. confirmar permisos de publicación a `notification-events`;
4. reiniciar únicamente el proceso si el estado persistente está sano.

## Observabilidad

Mínimos operativos:

- trazas HTTP y AMQP;
- propagación de `traceparent` por el salto async/outbox;
- métricas RED HTTP;
- `notification.delivered{channel,status}`;
- contador de retries y tamaño de DLQ;
- logs JSON con `trace_id`/`span_id` y sin PII sensible.

## Escalamiento

| Nivel | Responsable | Casos |
|-------|-------------|-------|
| L1 | Desarrollo/soporte | variables, health, logs, cola |
| L2 | Líder técnico Notification | errores de contrato, retries, idempotencia, templates |
| L3 | Arquitectura/Infra | broker, PostgreSQL, SMTP, pérdida/corrupción de datos |
