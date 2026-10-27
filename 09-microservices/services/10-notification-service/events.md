# Eventos — notification-service

> Estado: 🟡 En progreso | Última actualización: 2026-10-26
> Transporte: RabbitMQ / AMQP · Entrega: at-least-once

> **Fuente global:** [event-catalog.md](../../event-catalog.md). Todos los mensajes usan el envelope versionado de `shared-contracts`.

## Eventos consumidos

### `monitoring.alert.triggered`

Productor: `monitoring-service`.

El servicio lo consume cuando Monitoring detecta una condición de riesgo y persiste una `generated_alert`. Notification no reevalúa el KPI ni consulta tablas de Monitoring.

Payload mínimo esperado por la implementación actual:

```json
{
  "event_id": "4dff384f-8a57-4ba7-a900-6c479b87b38e",
  "event_type": "monitoring.alert.triggered",
  "source_service": "monitoring-service",
  "payload": {
    "affected_entity_type": "Instructor",
    "affected_entity_id": "3a286fa0-3fdb-48d5-baf2-0dfd0199a542",
    "alert_type_code": "LOW_ATTENDANCE"
  }
}
```

Acciones:

1. deduplicar por `event_id`;
2. resolver destinatario desde datos contractuales/proyección local; no consultar Monitoring ni Actors de forma síncrona;
3. resolver plantilla `ALERT_TRIGGERED` si está activa;
4. intentar entrega;
5. persistir `SENT` o `FAILED`;
6. en éxito, insertar Outbox en la misma transacción.

### `scheduling.schedule.published`

Productor: `scheduling-service`.

La implementación actual notifica a `published_by` como confirmación de publicación. El fan-out a todos los `instructor_ids` requiere una estrategia de idempotencia por destinatario antes de habilitarse.

```json
{
  "event_id": "0db9138b-5ed6-41ed-8557-79ab3fa7a717",
  "event_type": "scheduling.schedule.published",
  "source_service": "scheduling-service",
  "payload": {
    "published_by": "3a286fa0-3fdb-48d5-baf2-0dfd0199a542",
    "schedule_name": "Horario ficha 3145555",
    "ficha": "3145555"
  }
}
```

## Desacoplamiento de resolución de destinatario

El consumidor no realiza llamadas síncronas a Monitoring ni a Actors para completar un evento. Para canales que requieren una dirección de entrega, la dirección debe provenir de un comando autorizado o de una proyección local alimentada por eventos. El email stub configurable de la implementación actual es únicamente una facilidad de desarrollo y debe deshabilitarse en ambientes compartidos.

## Evento publicado

### `notification.notification.sent`

Se publica **solo después de una entrega exitosa** y mediante Outbox.

```json
{
  "event_id": "997706e9-9c62-417c-8615-ad5f4a9993f6",
  "event_type": "notification.notification.sent",
  "version": "1.0",
  "timestamp": "2026-08-26T20:00:00Z",
  "source_service": "notification-service",
  "payload": {
    "notification_id": "a6a9e772-7784-4ffb-9359-2857f8101d74",
    "recipient_id": "3a286fa0-3fdb-48d5-baf2-0dfd0199a542",
    "channel": "EMAIL",
    "sent_at": "2026-08-26T20:00:00Z",
    "trace_parent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
  }
}
```

Payload schema: `events/notification.notification.sent.schema.json` in shared-contracts (proposed in
[shared-contracts PR #18](https://github.com/code-sena/design-software-shared-contracts/pull/18)).
The current envelope has no `correlation_id`; trace propagation uses AMQP headers, while the
optional `trace_parent` payload field lets the outbox relay continue the original trace.

Consumidor: `audit-service`.

## Topología AMQP

| Elemento | Nombre / regla |
|----------|----------------|
| Exchange entrada scheduling | `scheduling-events` |
| Routing key | `scheduling.schedule.published` |
| Exchange entrada monitoring | `monitoring-events` |
| Routing key | `monitoring.alert.triggered` |
| Exchange salida | `notification-events` |
| Evento salida | `notification.notification.sent` |
| DLX | `notification-dlx` |
| DLQ | `notification-worker.dlq` |

## Idempotencia

- `event_id`/`source_event_id` identifica el hecho externo.
- Un evento que ya terminó en `SENT` se ignora en redelivery.
- Un intento `FAILED` puede volver a procesarse.
- El índice único parcial de `sent_notification.source_event_id` es la protección final en BD.

## Reintentos

Fallos transitorios usan backoff exponencial. Valores configurables:

- `NOTIFICATION_RETRY_MAX_ATTEMPTS`
- `NOTIFICATION_RETRY_INITIAL_INTERVAL_MS`
- `NOTIFICATION_RETRY_MAX_INTERVAL_MS`

Un error permanente (p. ej. `event_type` no soportado) no se reintenta; el mensaje se envía a DLQ.

## Regla de frontera

Ningún servicio invoca `notification-worker` directamente. Para notificar:

- publica un evento de dominio soportado, o
- usa `POST /api/v1/notifications` mediante el contrato público.

## Referencias

- [event-catalog.md](../../event-catalog.md)
- [notification-worker/contract.md](./components/notification-worker/contract.md)
- [ADR-001](../../../05-architecture/decisions/records/ADR-001-message-broker.md)
- [ADR-005](../../../05-architecture/decisions/records/ADR-005-microservices-topology-and-transversal-capabilities.md)
