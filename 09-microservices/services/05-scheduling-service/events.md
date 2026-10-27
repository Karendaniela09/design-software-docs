# Eventos — scheduling-service

> Estado: 🟢 Estable | Última actualización: 2026-10-26

---

## Eventos publicados

Topic: `scheduling-events`

### `scheduling.class_session.created`

Se emite cuando el `scheduling-engine-workflow` crea una nueva sesión de clase dentro de un horario.

**Consumidores:** `monitoring-service`, `audit-service`, `document-service`

**Payload:**

```json
{
  "event_id": "uuid-v4",
  "event_type": "scheduling.class_session.created",
  "version": "1.0",
  "timestamp": "2026-06-20T10:00:00Z",
  "source_service": "scheduling-service",
  "payload": {
    "sessionId": "uuid-v4",
    "scheduleId": "uuid-v4",
    "competencyId": "uuid-v4",
    "instructorId": "uuid-v4",
    "environmentId": "uuid-v4",
    "timeSlotId": "uuid-v4",
    "sessionDate": "2026-07-01"
  }
}
```

Payload schema: `events/scheduling.class_session.created.schema.json` in shared-contracts.

---

### `scheduling.class_session.cancelled`

Se emite cuando una sesión de clase es cancelada. Puede originarse desde `schedules-api` o desde `scheduling-engine-workflow` al detectar un conflicto irreconciliable.

**Consumidores:** `monitoring-service`, `audit-service`, `document-service`, `actors-service`

**Payload:**

```json
{
  "event_id": "uuid-v4",
  "event_type": "scheduling.class_session.cancelled",
  "version": "1.0",
  "timestamp": "2026-06-20T11:30:00Z",
  "source_service": "scheduling-service",
  "payload": {
    "sessionId": "uuid-v4",
    "scheduleId": "uuid-v4",
    "cancelledAt": "2026-06-20T11:30:00Z"
  }
}
```

Payload schema: `events/scheduling.class_session.cancelled.schema.json` in shared-contracts.

---

### `scheduling.conflict.detected`

> Pendiente de verificación: el `OutboxRelay` actual no registra este tipo de evento. No debe
> considerarse emitido hasta que se identifique un productor en el código desplegable.

**Consumidores:** `monitoring-service`, `audit-service`

**Payload:**

```json
{
  "event": "scheduling.conflict.detected",
  "version": "1.0",
  "source": "scheduling-service",
  "event_id": "uuid-v4",
  "timestamp": "2026-06-20T09:15:00Z",
  "data": {
    "conflict_id": "uuid-v4",
    "schedule_id": "uuid-v4",
    "conflict_type": "ENVIRONMENT_OVERLAP",
    "session_a_id": "uuid-v4",
    "session_b_id": "uuid-v4",
    "description": "El ambiente A-201 ya está asignado a otra ficha en el bloque horario 08:00–12:00 del martes",
    "detected_at": "2026-06-20T09:15:00Z"
  }
}
```

**Valores válidos para `conflict_type`:**

| Valor | Descripción |
|---|---|
| `ENVIRONMENT_OVERLAP` | Mismo ambiente asignado en el mismo bloque horario |
| `INSTRUCTOR_OVERLAP` | Mismo instructor asignado en el mismo bloque horario |
| `FICHA_OVERLAP` | La misma ficha tiene dos sesiones superpuestas |

---

### `scheduling.schedule.published`

Se emite cuando un horario en estado `UNDER_REVIEW` es promovido a `PUBLISHED`. Este evento es **crítico** y se publica mediante **Outbox pattern** para garantizar entrega at-least-once.

**Consumidores:** `monitoring-service`, `audit-service`, `document-service` (genera PDF del horario), `actors-service`

**Payload:**

```json
{
  "event_id": "uuid-v4",
  "event_type": "scheduling.schedule.published",
  "version": "1.0",
  "timestamp": "2026-06-20T14:00:00Z",
  "source_service": "scheduling-service",
  "payload": {
    "scheduleId": "uuid-v4",
    "fichaId": "uuid-v4",
    "period": "2026-1",
    "sessionCount": 48,
    "publishedBy": "uuid-v4",
    "publishedAt": "2026-06-20T14:00:00Z",
    "instructorIds": ["uuid-v4", "uuid-v4"],
    "environmentIds": ["uuid-v4", "uuid-v4"]
  }
}
```

Payload schema: `events/scheduling.schedule.published.schema.json` in shared-contracts.

---

### `scheduling.schedule.created`

Se emite al crear el borrador del horario. El payload reproduce los campos de `ScheduleEvents.ScheduleCreated`.

```json
{
  "event_id": "uuid-v4",
  "event_type": "scheduling.schedule.created",
  "version": "1.0",
  "timestamp": "2026-06-20T09:00:00Z",
  "source_service": "scheduling-service",
  "payload": {
    "scheduleId": "uuid-v4",
    "fichaId": "uuid-v4",
    "period": "2026-1",
    "name": "Horario 2026-1",
    "createdBy": "uuid-v4",
    "createdAt": "2026-06-20T09:00:00Z"
  }
}
```

Payload schema: `events/scheduling.schedule.created.schema.json` in shared-contracts.

---

### `scheduling.schedule.validated`

Se emite cuando la validación de un horario termina. El payload reproduce los campos de `ScheduleEvents.ScheduleValidated`.

```json
{
  "event_id": "uuid-v4",
  "event_type": "scheduling.schedule.validated",
  "version": "1.0",
  "timestamp": "2026-06-20T09:30:00Z",
  "source_service": "scheduling-service",
  "payload": {
    "scheduleId": "uuid-v4",
    "fichaId": "uuid-v4",
    "period": "2026-1",
    "validatedAt": "2026-06-20T09:30:00Z"
  }
}
```

Payload schema: `events/scheduling.schedule.validated.schema.json` in shared-contracts.

---

## Eventos consumidos

Source topic: `environment-events`

### `environment.availability.changed`

Emitido por `training-environment-service` cuando cambia la disponibilidad de un ambiente (por ejemplo, un ambiente pasa de disponible a no disponible por asignación o cierre temporal).

**Acción del scheduling-service:**

El `conflict-validator-worker` actualiza el read model local de disponibilidad de ambientes (per ADR-002: los servicios mantienen proyecciones locales de datos de otros dominios). Si el ambiente afectado tiene sesiones futuras asignadas, el worker lanza una validación de conflictos sobre esas sesiones y emite `scheduling.conflict.detected` si corresponde.

**Payload esperado:**

```json
{
  "event": "environment.availability.changed",
  "data": {
    "environment_id": "uuid-v4",
    "available": false,
    "effective_from": "2026-06-21T00:00:00Z",
    "reason": "Cierre administrativo"
  }
}
```

---

### `environment.maintenance.started`

Emitido por `training-environment-service` cuando un ambiente entra en periodo de mantenimiento no programado o programado.

**Acción del scheduling-service:**

El `conflict-validator-worker` identifica todas las sesiones futuras asignadas al ambiente en mantenimiento. Por cada sesión afectada:

1. Actualiza el read model local marcando el ambiente como no disponible en el rango de mantenimiento.
2. Emite `scheduling.conflict.detected` con `conflict_type: ENVIRONMENT_OVERLAP` para que `monitoring-service` y `audit-service` registren el impacto.
3. No cancela sesiones automáticamente; la cancelación explícita queda a cargo de un coordinador vía `schedules-api`.

**Payload esperado:**

```json
{
  "event": "environment.maintenance.started",
  "data": {
    "environment_id": "uuid-v4",
    "maintenance_id": "uuid-v4",
    "start_date": "2026-06-22",
    "end_date": "2026-06-25",
    "description": "Mantenimiento eléctrico preventivo"
  }
}
```

---

## Formato de envelope

Todos los eventos publicados por `scheduling-service` siguen este envelope estándar:

```json
{
  "event_id":  "<uuid-v4 único por evento>",
  "event_type": "<dominio>.<entidad>.<acción>",
  "version":   "1.0",
  "timestamp": "<ISO-8601 UTC>",
  "source_service": "scheduling-service",
  "payload":   { }
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `event_id` | UUID v4 | Identificador único del evento, usado para deduplicación |
| `event_type` | string | Nombre del evento en notación `dominio.entidad.acción` |
| `version` | string | Versión del esquema del evento |
| `timestamp` | ISO-8601 | Momento en que ocurrió el hecho de negocio (no el de publicación al broker) |
| `source_service` | string | Servicio que origina el evento; siempre `scheduling-service` |
| `payload` | object | Payload específico del evento |

---

## Política de entrega

El `OutboxRelay` publica los eventos pendientes con confirmación de RabbitMQ. Si la publicación falla,
la fila queda en estado `PENDING` y vuelve a intentarse en el siguiente ciclo de polling; el código
actual no limita el número de intentos ni envía estos registros a una DLQ. La entrega es at-least-once,
por lo que los consumidores deduplican por `event_id`.

Para los eventos consumidos (`environment.availability.changed`, `environment.maintenance.started`), el `conflict-validator-worker` aplica procesamiento idempotente usando `event_id` para evitar duplicar actualizaciones en el read model.

---

## Outbox pattern

Los cinco tipos de evento publicados por `scheduling-service` se guardan en la tabla `outbox` de
`scheduling_db` dentro de la transacción del cambio de estado. El relay los publica con entrega
at-least-once incluso si RabbitMQ falla temporalmente.

**Flujo:**

1. La transacción que promueve el horario a `PUBLISHED` en `scheduling_db` inserta simultáneamente un registro en la tabla `outbox` dentro de la misma transacción de base de datos.
2. Un proceso relay (parte del componente `schedules-api`) hace polling sobre la tabla `outbox` y publica los registros pendientes al topic `scheduling-events`.
3. Una vez confirmada la publicación por el broker, el registro se marca como `published` en `outbox`.
4. Los consumidores deben manejar duplicados usando `event_id` para deduplicación.

**Esquema de la tabla `outbox`:**

```sql
CREATE TABLE outbox (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id      UUID NOT NULL UNIQUE,
  event_type    VARCHAR(128) NOT NULL,
  payload       JSONB NOT NULL,
  status        VARCHAR(16) NOT NULL DEFAULT 'PENDING', -- PENDING | PUBLISHED | FAILED
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at  TIMESTAMPTZ
);
```

Ver `architecture/overview.md` para la descripción completa del patrón Outbox a nivel de plataforma.
