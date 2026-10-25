# Eventos — academic-management-service

> Estado: 🟢 Estable | Última actualización: 2026-06-20

---

## Eventos publicados

El servicio publica todos sus eventos en el topic `academic-events`.

| Evento | Topic | Descripción | Consumidores conocidos |
|--------|-------|-------------|------------------------|
| `academic.program.created` | `academic-events` | Un nuevo programa de formación fue registrado | `audit-service` |
| `academic.ficha.opened` | `academic-events` | Una ficha de formación fue abierta y habilitada para inscripciones | `audit-service`, `monitoring-service` |
| `academic.ficha.closed` | `academic-events` | Una ficha de formación fue cerrada (completada o cancelada) | `audit-service`, `monitoring-service` |
| `academic.competency.updated` | `academic-events` | Una competencia asociada a un programa fue creada, modificada o desactivada | `audit-service`, `actors-service` |

---

### `academic.program.created`

Se emite cuando un programa de formación es creado exitosamente dentro de una red de conocimiento.

```json
{
  "program_id": "prog-7f3a1c",
  "program_code": "228101",
  "name": "Tecnología en Análisis y Desarrollo de Software",
  "training_level": "TECHNOLOGIST",
  "total_hours": 2112,
  "knowledge_network_id": "kn-software-tec",
  "created_by": "user-instructor-001",
  "created_at": "2026-06-20T09:15:00Z"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `program_id` | `string` | Identificador interno único del programa |
| `program_code` | `string` | Código SENA del programa |
| `name` | `string` | Nombre completo del programa |
| `training_level` | `enum` | `TECHNOLOGIST`, `TECHNICIAN`, `OPERATOR`, `SPECIAL` |
| `total_hours` | `integer` | Horas totales de formación del programa |
| `knowledge_network_id` | `string` | Red de conocimiento a la que pertenece el programa |
| `created_by` | `string` | ID del usuario que registró el programa |
| `created_at` | `string (ISO 8601)` | Timestamp de creación |

---

### `academic.ficha.opened`

Se emite cuando una ficha de formación es abierta y queda habilitada para la inscripción de aprendices.

```json
{
  "ficha_id": "ficha-9b2d4e",
  "ficha_number": "2758369",
  "program_id": "prog-7f3a1c",
  "program_code": "228101",
  "training_center_id": "tc-regional-bogota",
  "training_shift": "DAY",
  "training_modality": "IN_PERSON",
  "start_date": "2026-08-01",
  "max_capacity": 30,
  "opened_by": "user-coordinator-042",
  "opened_at": "2026-06-20T10:00:00Z"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `ficha_id` | `string` | Identificador interno único de la ficha |
| `ficha_number` | `string` | Número de ficha SENA (visible externamente) |
| `program_id` | `string` | Referencia al programa de formación |
| `program_code` | `string` | Código del programa para facilitar joins downstream |
| `training_center_id` | `string` | Centro de formación donde se ejecuta la ficha |
| `training_shift` | `enum` | `DAY`, `NIGHT`, `MIXED` |
| `training_modality` | `enum` | `IN_PERSON`, `VIRTUAL`, `HYBRID` |
| `start_date` | `string (ISO 8601 date)` | Fecha de inicio de la formación |
| `max_capacity` | `integer` | Cupo máximo de aprendices |
| `opened_by` | `string` | ID del usuario que abrió la ficha |
| `opened_at` | `string (ISO 8601)` | Timestamp de apertura |

---

### `academic.ficha.closed`

Se emite cuando una ficha de formación es cerrada, ya sea por finalización del proceso o por cancelación.

```json
{
  "ficha_id": "ficha-9b2d4e",
  "ficha_number": "2758369",
  "close_reason": "COMPLETED",
  "actual_end_date": "2026-12-15",
  "closed_by": "user-coordinator-042",
  "closed_at": "2026-12-15T17:30:00Z"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `ficha_id` | `string` | Identificador interno único de la ficha |
| `ficha_number` | `string` | Número de ficha SENA |
| `close_reason` | `enum` | `COMPLETED` — proceso finalizado; `CANCELLED` — ficha cancelada antes de completarse |
| `actual_end_date` | `string (ISO 8601 date)` | Fecha real de cierre (puede diferir de la fecha planificada) |
| `closed_by` | `string` | ID del usuario que cerró la ficha |
| `closed_at` | `string (ISO 8601)` | Timestamp de cierre |

---

### `academic.competency.updated`

Se emite cuando una competencia de un programa de formación es creada, modificada o desactivada.

```json
{
  "competency_id": "comp-4c8f2a",
  "competency_code": "220501001",
  "program_id": "prog-7f3a1c",
  "change_type": "UPDATED",
  "updated_by": "user-instructor-017",
  "updated_at": "2026-06-20T14:45:00Z"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `competency_id` | `string` | Identificador interno único de la competencia |
| `competency_code` | `string` | Código normalizado de la competencia |
| `program_id` | `string` | Programa al que pertenece la competencia |
| `change_type` | `enum` | `CREATED`, `UPDATED`, `DEACTIVATED` |
| `updated_by` | `string` | ID del usuario que realizó el cambio |
| `updated_at` | `string (ISO 8601)` | Timestamp del cambio |

---

## Eventos consumidos

`academic-management-service` no consume eventos de otros servicios. Toda la información de referencia (centros de formación, redes de conocimiento, usuarios) se obtiene de forma sincrónica mediante llamadas HTTP a los servicios correspondientes en el momento de la operación.

---

## Formato de envelope

Todos los eventos siguen el envelope canónico del sistema. El payload del negocio se incluye en el campo `payload` y se valida contra [`07-api/contracts/schemas/event-envelope.schema.json`](../../../07-api/contracts/schemas/event-envelope.schema.json), que prohíbe propiedades adicionales en el envelope. `correlation_id` es opcional.

**Ejemplo completo con `academic.ficha.opened`:**

```json
{
  "event_id": "c3d7e9f1-4a2b-4c8d-b5e6-f7a8b9c0d1e2",
  "event_type": "academic.ficha.opened",
  "version": "1.0",
  "timestamp": "2026-06-20T10:00:00Z",
  "source_service": "academic-management-service",
  "correlation_id": "a1b2c3d4-e5f6-4890-abcd-ef1234567890",
  "payload": {
    "ficha_id": "ficha-9b2d4e",
    "ficha_number": "2758369",
    "program_id": "prog-7f3a1c",
    "program_code": "228101",
    "training_center_id": "tc-regional-bogota",
    "training_shift": "DAY",
    "training_modality": "IN_PERSON",
    "start_date": "2026-08-01",
    "max_capacity": 30,
    "opened_by": "user-coordinator-042",
    "opened_at": "2026-06-20T10:00:00Z"
  }
}
```

| Campo del envelope | Tipo | Descripción |
|--------------------|------|-------------|
| `event_id` | `string (UUID v4)` | Identificador único del evento; garantiza idempotencia en consumidores |
| `event_type` | `string` | Nombre canónico del evento (`dominio.entidad.accion`) |
| `version` | `string` | Versión del contrato del evento |
| `timestamp` | `string (ISO 8601)` | Momento en que ocurrió el hecho de negocio |
| `source_service` | `string` | Nombre del servicio emisor |
| `payload` | `object` | Payload específico del evento (ver secciones anteriores) |
| `correlation_id` | `string` | Opcional. ID de la solicitud HTTP que originó el evento; útil para trazabilidad |

No se usan `schema_version`, `occurred_at`, `data` ni `source_port` como campos del envelope. Cualquier dato adicional del evento debe ir dentro de `payload` o esperar una extensión explícita del contrato.

---

## Política de reintentos

| Parámetro | Valor |
|-----------|-------|
| Topic principal | `academic-events` |
| DLQ de publicación | `academic-events.dlq` |
| Cola del consumidor R1 | `academic-events.r1.consumer`; el consumidor viene apagado (`ACADEMIC_R1_CONSUMER_ENABLED=false`) y su cola y binding se declaran solo al encenderlo |
| DLQ del consumidor R1 | `academic-events.r1.dlq`, mediante `academic-events.r1.dlx` |
| Reintentos del publicador Academic | 3 reintentos después del intento original |
| Backoff del publicador Academic | 1s → 4s → 16s |
| Reintentos del consumidor R1 | 1s → 4s → 16s antes de DLQ |
| Retención en DLQ | Pendiente de decisión |
| Reprocesamiento R1 | `POST /api/v1/events/dlq/reprocess-next`, autorizado y conservando `message_id` |

El publicador y el consumidor R1 usan reintentos 1s → 4s → 16s, pero son mecanismos independientes. El relay exige publisher confirm antes de marcar el outbox como publicado. El consumidor conserva el mismo `message_id` y registra una única recepción por `(consumer_name, event_id)`. El consumidor R1 es de referencia: solo registra recibos y no aplica lógica de negocio, por eso viene apagado por defecto (`academic.events.consumer.enabled`, variable `ACADEMIC_R1_CONSUMER_ENABLED`) y debe encenderse de forma explícita para ejercitar la idempotencia y la DLQ. Con el consumidor apagado una cola enlazada a `academic.#` crecería sin que nadie la drene, por eso no se declara. La retención operativa de las DLQ continúa pendiente.

---

## Invariantes de negocio

Las siguientes reglas se validan **antes** de persistir el cambio y emitir el evento correspondiente. Si alguna falla, la operación se rechaza con error 422, no se guarda el cambio de negocio y no se inserta ni publica ningún evento. Con Outbox, la escritura de negocio y la fila de Outbox se confirman o revierten juntas; la publicación ocurre después mediante relay.

### Para `academic.program.created`
- El `program_code` debe ser único en todo el sistema; no puede existir otro programa activo con el mismo código.
- El `knowledge_network_id` debe corresponder a una red de conocimiento existente y activa (verificado via HTTP al servicio de configuración).
- `total_hours` debe ser mayor que 0.
- El programa debe tener al menos una competencia registrada antes de poder considerarse publicable (la competencia puede crearse en la misma transacción).

### Para `academic.ficha.opened`
- El `program_id` debe corresponder a un programa existente y en estado activo.
- `max_capacity` debe ser mayor que 0.
- `start_date` debe ser una fecha futura al momento de apertura.
- No puede existir otra ficha abierta con el mismo `ficha_number`.
- El `training_center_id` debe corresponder a un centro de formación existente y activo (verificado via HTTP).

### Para `academic.ficha.closed`
- La ficha debe estar en un estado no terminal (`INDUCTION`, `EXECUTION` o `PRODUCTIVE_STAGE`) para poder cerrarse; no se puede cerrar una ficha en `COMPLETED` o `CANCELLED`.
- Si `close_reason` es `COMPLETED`, `actual_end_date` no puede ser una fecha futura.
- Si `close_reason` es `CANCELLED`, debe registrarse una justificación en el campo interno `cancellation_notes` (no incluido en el evento, solo en el registro interno).

### Para `academic.competency.updated`
- El `program_id` referenciado debe existir y estar activo.
- El `competency_code` debe ser único dentro del mismo `program_id`.
- Una competencia en estado `DEACTIVATED` no puede volver a `CREATED` ni `UPDATED`; debe crearse una nueva con distinto código.
- No se puede desactivar una competencia si existen fichas abiertas con resultados de aprendizaje asociados a ella.

## HU-ACAD-11 lifecycle and cancellation details (ADR-030)

`EXECUTION` → `PRODUCTIVE_STAGE` has no hours precondition (owner decision of
2026-10-24): Academic does not read Scheduling for it, and the transition applies
only the role and state-machine rules.

Before `PRODUCTIVE_STAGE` → `COMPLETED`, every active learner of the ficha must
have `APPROVED` on 100% of the active RAPs (`LearningOutcome`) of the ficha's
program (RN-ACAD-07). There is no numeric grade: a RAP that is `NOT_APPROVED` or
has no judgment does not count. Academic resolves the required RAP ids from its
own database and asks Actors for the coverage; Actors is authoritative for the
judgments and returns counts only. An incomplete coverage answers
`409 ACAD_FICHA_RAP_COVERAGE_INCOMPLETE`; a program with no active RAPs, or a
ficha with no active learners, answers `409 ACAD_STATUS_PRECONDITION_FAILED`.
Missing or invalid Actors evidence fails closed with `503`.

For a new cancellation, `cancellation_notes` is required only with target status
`CANCELLED` (also through the `DELETE /fichas/{id}` alias, which carries it in
the body). Academic trims it and enforces 10–500 Unicode code points, stores
it with cancellation actor/time, and omits it from the API response and
`academic.ficha.closed` public event. These rules are in ADR-030, accepted by the
project owner on 2026-10-24.
