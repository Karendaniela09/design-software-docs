# Eventos — actors-service

> Estado: 🟢 Estable | Última actualización: 2026-10-26

---

## Eventos publicados

Broker: RabbitMQ, exchange tipo topic actors-events. Cada mensaje usa el envelope compartido definido en events/event-envelope.schema.json. La tabla company_visit_outbox conserva el envelope completo y el dispatcher lo publica sin modificarlo.

### actors.instructor.availability_changed

Se emite al registrar o retirar una excepción de disponibilidad. El payload es el agregado InstructorAvailabilityException serializado por Jackson en camelCase: id, instructorId, exceptionType, startDatetime, endDatetime, description, approvedBy, createdAt, updatedAt, active, deletedAt, deletedBy, createdBy, updatedBy, rowVersion y status. Las fechas locales se publican como cadenas ISO 8601. El esquema compartido es events/actors.instructor.availability_changed.schema.json.

Consumidores declarados: audit-service y scheduling-service.

### actors.learner.enrolled

Se emite al crear una inscripción de aprendiz. El payload corresponde al record LearnerFichaEnrollment serializado en camelCase: id, learnerId, fichaId, enrollmentStatusId, stage, enrollmentDate, completionDate, isCurrent y transferReason. completionDate y transferReason pueden ser null. El esquema compartido es events/actors.learner.enrolled.schema.json.

Consumidores declarados: audit-service y monitoring-service.

### actors.company_visit.completed

Se emite al registrar una visita. El payload SQL contiene visit_id, productive_stage_id, learner_id, instructor_id, assigned_instructor_id, ficha_id y productive_stage_progress; ficha_id y productive_stage_progress pueden ser null. El esquema compartido es events/actors.company_visit.completed.schema.json.

Consumidores declarados: audit-service y monitoring-service.

### Eventos declarados sin productor en develop

actors.instructor.assigned y actors.productive_stage.started siguen descritos como eventos de dominio en la documentación funcional. No se encontró un emisor de esos event_type en el código de actors-service develop. Su producción o retiro requiere decisión de dominio; esta entrega no agrega funcionalidad ni los presenta como publicados.

La asignación instructor → ficha (HU-ACT-033, `POST/DELETE /api/v1/fichas/{fichaId}/instructors`) **no emite evento**: academic-management la lee por `GET /internal/instructors/{id}/fichas`. `actors.instructor.assigned` sigue sin productor hasta que un consumidor (horario, juicios de RAP) lo pida.

## Eventos consumidos

### `iam.user.created`

**Fuente:** `iam-service` — topic `iam-events`

**Acción:** actors-service crea o vincula el registro de actor según el campo `actor_type` del payload. Ver [Sincronización con iam-service](#sincronización-con-iam-service) para el detalle completo del mapeo.

---

### `iam.user.deactivated`

**Fuente:** `iam-service` — topic `iam-events`

**Acción:** actors-service localiza el registro de instructor o aprendiz cuyo `user_id` coincide y lo marca como inactivo (`active = false`). El registro se preserva íntegro para trazabilidad histórica; no se elimina. Las asignaciones de competencia y fichas activas del instructor pasan a estado `SUSPENDIDA` hasta resolución manual por parte del coordinador.

---

### `academic.competency.updated`

**Fuente:** `academic-management-service` — topic `academic-events`

**Acción:** actors-service revisa todas las asignaciones de competencia (`asignacion_competencia`) que referencian la `competency_id` modificada. Si el cambio afecta el código, nombre o nivel de la competencia, las asignaciones vigentes se marcan con `requires_review = true` para que el coordinador confirme o revoque la habilitación del instructor. No se desactivan automáticamente — el instructor permanece habilitado hasta revisión explícita.

**Contrato recibido:** `academic.competency.updated` usa el envelope común de Academic (`event_id`, `event_type`, `version`, `timestamp`, `source_service`, `payload` y `correlation_id` opcional). La implementación del consumidor de Actors depende de su HU propia; esta documentación solo registra la integración esperada.

---

## Formato de envelope

Todos los eventos siguen el envelope estándar del ecosistema:

```json
{
  "event_id": "uuid-v4",
  "event_type": "actors.instructor.availability_changed",
  "version": "1.0",
  "timestamp": "2026-06-20T10:00:00Z",
  "source_service": "actors-service",
  "correlation_id": "uuid-v4",
  "payload": { }
}
```

| Campo | Descripción |
|-------|-------------|
| `event_id` | UUID v4 generado por actors-service al guardar el evento en el outbox, en la misma transacción del cambio de negocio. Idempotency key para consumidores. |
| `event_type` | Nombre del evento en formato `<servicio>.<entidad>.<accion>`. |
| `version` | Versión del contrato de payload. Incremento mayor si hay breaking changes. |
| `timestamp` | Momento de publicación en UTC, ISO 8601. |
| `source_service` | Siempre `actors-service` para eventos de este catálogo. |
| `correlation_id` | Propagado desde el request HTTP que originó la acción. Permite rastrear la cadena de llamadas en los logs. |

---

## Política de entrega y reintentos

**Publicación (outbox).**

- **Broker:** RabbitMQ, exchange `actors-events` (ADR-001).
- **Garantía:** al menos una vez. La fila del evento se confirma en la misma transacción que el cambio de negocio y un despachador la publica después. Si el servicio cae entre la confirmación del broker y el marcado de la fila, el mismo `event_id` puede publicarse otra vez.
- **Reintentos:** si el broker no confirma o no puede enrutar el mensaje, la fila vuelve a `PENDING` con back-off exponencial de 1 s, 4 s, 16 s y 64 s; tras 5 intentos queda `DEAD`.
- **Eventos muertos:** `GET /api/v1/ops/actors/outbox/status` cuenta las filas por estado y `POST /api/v1/ops/actors/outbox/{eventId}/replay` reactiva una fila `DEAD`. Es una operación interna (feature `ACT_INSTRUCTOR_MANAGE` mientras no exista un permiso de operaciones); el edge no debe enrutarla a usuarios finales.
- **Varias instancias:** cada fila se reclama con un arrendamiento de 45 s; un proceso caído deja filas que otra instancia recupera al vencer el arrendamiento.
- **Procesamiento idempotente:** los consumidores deben usar `event_id` como clave de idempotencia y deduplicar en su propio almacén.

**Consumo de eventos de IAM.**

- **Cola de mensajes fallidos:** `actors-events.dlq` (Dead Letter Queue de RabbitMQ), configurada por `ACTORS_IAM_DLQ`.
- **Reintentos en consumo:** 3 intentos con backoff exponencial (1 s → 4 s → 16 s) antes de enviar el mensaje a la DLQ.
- **Retención en DLQ:** 7 días. Pasado ese plazo el mensaje expira.
- **Reproducción:** `POST /api/v1/ops/actors/iam-dlq/replay-one` republica un mensaje de la DLQ y lo reconoce en una sola transacción AMQP.
- **Alertas:** un mensaje en `actors-events.dlq` debe generar una alerta dentro de los 5 minutos siguientes a su llegada (regla `rabbitmq_queue_messages_ready{queue="actors-events.dlq"} > 0` en `docker-infra`).

---

## Sincronización con iam-service

Cuando `iam.user.created` llega con `actor_type=INSTRUCTOR`, actors-service crea o vincula el registro instructor usando `user_id` como clave de join. Si `actor_type=LEARNER`, crea o vincula el registro aprendiz de la misma forma. El `user_id` del JWT sirve como join key en todas las operaciones posteriores: cualquier servicio que llame a actors-service con un token válido puede derivar el `instructor_id` o `learner_id` correspondiente a partir del `user_id` embebido en el JWT, sin necesidad de una llamada de resolución separada.

Los campos que actors-service copia del evento `iam.user.created` al registro de actor son:

| Campo en `iam.user.created` | Campo en actors-service |
|-----------------------------|-------------------------|
| `user_id` | `user_id` (join key) |
| `email` | `email` |
| `first_name` | `first_name` |
| `last_name` | `last_name` |
| `actor_type` | determina la entidad destino (`instructor` o `learner`) |

El resto de los campos del perfil de actor (número de documento, tipo de contrato, competencias, etc.) se completan mediante la API de actors-service una vez creado el registro base.
