<!-- RESUMEN-EJECUTIVO
capacidad: contrato REST de notification-service
fase: implementación incremental
estado: accepted
fuente_maquina: 07-api/contracts/openapi/notification.yaml
tldr: API pública para solicitar una notificación y consultar su resultado. El listado de inbox es gap explícito y no pertenece a monitoring-service.
-->

# Contrato — notification-api

> Estado: 🟡 En progreso | Última actualización: 2026-10-24

> **Fuente de verdad:** [`07-api/contracts/openapi/notification.yaml`](../../../../../07-api/contracts/openapi/notification.yaml), espejo documental de `shared-contracts/openapi/notification.yaml`.

## Base URL

`/api/v1` (el `servers` del contrato). El proceso `notification-api` sirve las rutas del contrato **solo** bajo ese prefijo, en cualquier ambiente: `POST /notifications` y `GET /notifications/{id}` sin prefijo responden `404`
([ADR-022](../../../../../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md) §3, HU-NOTIF-010).

Detrás del edge, la ruta pública es `/notification` + el `servers` del contrato, por ejemplo `/notification/api/v1/notifications/{id}`; el edge quita `/notification` antes de llegar al servicio.

## Endpoints de negocio

| Método | Ruta | Descripción | Estado |
|--------|------|-------------|--------|
| `POST` | `/api/v1/notifications` | Solicita una entrega manual/síncrona. | ✅ |
| `GET` | `/api/v1/notifications/{id}` | Consulta el estado de una notificación por UUID. | ✅ |
| `GET` | `/api/v1/notifications` | Bandeja por destinatario/cursor. | 🟡 Pendiente; no usar `/sent-notifications` de Monitoring. |

## Salud

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Liveness, como lo lista el contrato. |
| `GET` | `/api/v1/ready` | Readiness (DB), como lo lista el contrato. |
| `GET` | `/health` | Mismo handler, también en la raíz: el edge enruta `/notification/health` como ruta exacta y quita el prefijo. |
| `GET` | `/ready` | Mismo handler, también en la raíz (ídem `/notification/ready`). |

## `POST /api/v1/notifications`

Requiere `NOTIFICATION_SEND` (ver [Seguridad](#seguridad)); responde `401` sin token válido y `403` sin la feature.

### Request

```json
{
  "recipient_id": "3a286fa0-3fdb-48d5-baf2-0dfd0199a542",
  "recipient_email": "aprendiz@example.invalid",
  "channel": "EMAIL",
  "subject": "Horario publicado",
  "template_code": "SCHEDULE_PUBLISHED",
  "source_service": "scheduling-service",
  "source_event_id": "0db9138b-5ed6-41ed-8557-79ab3fa7a717"
}
```

Campos requeridos por v0.1: `recipient_id`, `recipient_email`, `channel`, `subject`.

### Response `202`

`202 Accepted` con el schema `SentNotification` del OpenAPI (ver abajo).

## `GET /api/v1/notifications/{id}`

- `200`: `SentNotification`.
- `400`: UUID inválido.
- `401`: sin token válido (ver [Seguridad](#seguridad)).
- `403`: token válido sin `NOTIFICATION_VIEW`.
- `404`: no existe.
- `503`: dependencia no disponible.

## `SentNotification` (respuesta de `202` y `200`)

Campos requeridos por el OpenAPI, siempre presentes: `id`, `recipient_id`, `recipient_email`, `channel`, `subject`,
`send_status`, `created_at`. Los campos nulables que el servicio persiste (`body_summary`, `failure_reason`, `sent_at`) se
devuelven siempre y valen `null` cuando no tienen valor. `generated_alert_id` (opcional) no lo guarda `notification_db`, así
que no se devuelve.

```json
{
  "id": "d868a413-5130-4e7f-bdc4-d3e118f6be24",
  "recipient_id": "3a286fa0-3fdb-48d5-baf2-0dfd0199a542",
  "recipient_email": "aprendiz@example.invalid",
  "channel": "IN_APP",
  "subject": "Horario publicado",
  "body_summary": null,
  "send_status": "SENT",
  "failure_reason": null,
  "sent_at": "2026-10-24T23:58:47.305517Z",
  "created_at": "2026-10-24T23:58:47.741136Z"
}
```

> La copia canónica `shared-contracts/openapi/notification.yaml` aún describe `SentNotification` con todos los campos
> opcionales y sin `recipient_email` ni `created_at` (TD-011). El servicio sigue este espejo (`07-api`) y no el DTO generado
> de esa copia.

## Seguridad

Implementado en el servicio (HU-NOTIF-011), sin depender de que el edge esté presente:

- **Autenticación:** `Authorization: Bearer <jwt>` emitido por IAM. El servicio verifica localmente (sin llamar a IAM por
  request) firma RS256 contra el JWKS de IAM, `iss` = `sena-iam-service`, `exp` y `nbf`. No valida `aud`: IAM no la emite.
  Las llaves se cachean 5 minutos; un `kid` desconocido se cachea negativamente 30 s.
- **Autorización por feature**, la que declara el contrato (`x-required-feature`) y viaja en el claim `features` como
  `FEATURE:SCOPE` (cualquier scope):

| Operación | Feature |
|-----------|---------|
| `POST /api/v1/notifications` | `NOTIFICATION_SEND` |
| `GET /api/v1/notifications/{id}` | `NOTIFICATION_VIEW` |

- `/health` y `/ready` son públicos (`security: []`).
- La autenticación corre antes de validar el payload o buscar el id: un anónimo no aprende nada de ellos.
- Si no se pueden obtener las llaves de IAM, la solicitud se rechaza con `503` (nunca se deja pasar).

| Situación | HTTP | `error_code` |
|-----------|------|--------------|
| Sin `Authorization: Bearer` | 401 | `MISSING_TOKEN` |
| Token malformado, firma inválida, `kid` desconocido, otro emisor, algoritmo distinto de RS256 | 401 | `TOKEN_INVALID` |
| Token expirado | 401 | `TOKEN_EXPIRED` |
| Token válido sin la feature de la operación | 403 | `INSUFFICIENT_PERMISSIONS` |
| Llaves de IAM inaccesibles | 503 | `DEPENDENCY_UNAVAILABLE` |

Configuración, solo por variables de entorno y con el mismo comportamiento en develop, qa, staging y main:
`IAM_JWT_ISSUER` y `IAM_JWKS_URL` (obligatorias, sin default; el proceso no arranca sin ellas) y
`NOTIFICATION_JWKS_HTTP_ALLOWED_HOSTS` (opcional: hosts, separados por comas, cuyo JWKS puede leerse por `http` desde la red
interna, p. ej. `iam-api`; vacía = solo `https` o loopback). Ver
[runtime-configuration-map](../../../../../10-devops/runtime-configuration-map.md).

> **Brecha conocida (features sin emisor):** IAM hoy no emite `NOTIFICATION_SEND` ni `NOTIFICATION_VIEW`. El seed de
> `design-software-iam-db` solo trae `MON_NOTIFICATION_SEND` y `MON_NOTIFICATION_VIEW`, y `rbac-design.md` propone
> `NOTIF_SEND`, `NOTIF_VIEW_ALL` y `NOTIF_VIEW_OWN`. El servicio exige exactamente las features del contrato y no acepta
> alias, así que **un token real de IAM recibe `403` hasta que IAM emita las features del contrato** (o el contrato se
> alinee). Es un pendiente de la HU-INT-NOTIF-001 («grants NOTIFICATION_*», docs#314).

Pendiente fuera de esta HU:

- aislamiento por destinatario (quién puede consultar la notificación de quién): hoy basta la feature, un UUID conocido
  da acceso a cualquier titular de `NOTIFICATION_VIEW`; la política se define en la HU-INT-NOTIF-001 sin inventar un
  scope nuevo;
- un usuario final solo debe consultar su propia bandeja cuando se incorpore el endpoint de listado;
- `failure_reason` se devuelve tal como lo registra el notificador y puede traer detalle de infraestructura (por ejemplo
  el error de SMTP); conviene sanearlo antes de abrir la API a consumidores externos.

## Errores

Envelope del servicio (alineado con `shared-contracts/errors/error-codes.yaml`). `trace_id` es el id de la traza activa:

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "channel debe ser EMAIL o IN_APP",
  "trace_id": "..."
}
```

> `07-api/guidelines.md` §7 y `_shared.yaml` describen un envelope anidado (`{"error": {"code", ...}}`); el servicio
> conserva el plano de `shared-contracts` para todas sus respuestas. Reconciliar ambos es un tema transversal fuera de la
> HU-NOTIF-011.

## Gap de inbox

La UI global necesita listado paginado/cursor. Hasta que se agregue a `shared-contracts`, se registra como pendiente:

```text
GET /api/v1/notifications?recipient_id=<uuid>&cursor=<cursor>&limit=<n>
```

No debe implementarse de nuevo bajo `monitoring-api`.
