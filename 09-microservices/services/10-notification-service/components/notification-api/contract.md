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

El OpenAPI v0.1 garantiza `202 Accepted` para una solicitud aceptada, pero todavía **no fija un
schema de respuesta**. La implementación puede devolver información adicional, pero los consumidores
no deben depender de un body hasta que se formalice en `shared-contracts`.

## `GET /api/v1/notifications/{id}`

- `200`: `SentNotification`.
- `400`: UUID inválido.
- `404`: no existe.
- `503`: dependencia no disponible.

## Seguridad

Objetivo de arquitectura:

- JWT validado en gateway/API;
- autorización específica para envío manual;
- un usuario final solo puede consultar su propia bandeja cuando se incorpore el endpoint de listado;
- no exponer `recipient_email` ni `failure_reason` sin necesidad funcional.

> La conexión RBAC completa debe mantenerse trazada como requisito de implementación si todavía no está activa en el código.

## Errores

Envelope transversal:

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "channel debe ser EMAIL o IN_APP",
  "trace_id": "..."
}
```

## Gap de inbox

La UI global necesita listado paginado/cursor. Hasta que se agregue a `shared-contracts`, se registra como pendiente:

```text
GET /api/v1/notifications?recipient_id=<uuid>&cursor=<cursor>&limit=<n>
```

No debe implementarse de nuevo bajo `monitoring-api`.
