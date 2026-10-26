# Eventos — iam-service

> Estado: 🟢 Estable | Última actualización: 2026-06-20

---

## Eventos publicados

iam-service publica todos sus eventos en el topic `iam-events`.

| Evento | Topic | Descripción | Consumidores |
|--------|-------|-------------|-------------|
| `iam.user.created` | `iam-events` | Se emite cuando un nuevo usuario es registrado en el sistema | `actors-service`, `audit-service` |
| `iam.user.deactivated` | `iam-events` | Se emite cuando un usuario es desactivado | `actors-service`, `audit-service` |
| `iam.role.assigned` | `iam-events` | Se emite cuando se asigna un rol a un usuario | `audit-service` |
| `iam.session.started` | `iam-events` | Se emite cuando un usuario inicia sesión exitosamente | `audit-service` |
| `iam.scope_override.granted` | `iam-events` | Se emite al crear una excepción de autorización por usuario y feature | Consumidores de autorización y auditoría |
| `iam.scope_override.revoked` | `iam-events` | Se emite al revocar una excepción de autorización por usuario y feature | Consumidores de autorización y auditoría |

---

### `iam.user.created`

Emitido inmediatamente después de que un nuevo usuario es creado y persistido en la base de datos.

```json
{
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "event_type": "iam.user.created",
  "version": "1.0",
  "timestamp": "2026-06-20T10:30:00Z",
  "source_service": "iam-service",
  "correlation_id": "f1e2d3c4-b5a6-7890-fedc-ba0987654321",
  "payload": {
    "user_id": "usr_9f8e7d6c-5b4a-3210-fedc-ba9876543210",
    "email": "carlos.moreno@sena.edu.co",
    "first_name": "Carlos",
    "last_name": "Moreno",
    "document_type": "CC",
    "document_number": "1234567890",
    "default_max_hours_per_week": 40.0,
    "actor_type": "INSTRUCTOR",
    "actor_id": "act_1a2b3c4d-5e6f-7890-abcd-ef1234567890",
    "roles": [
      {
        "role_name": "INSTRUCTOR",
        "training_center_id": "33333333-3333-4333-8333-333333333333"
      }
    ],
    "created_at": "2026-06-20T10:30:00Z"
  }
}
```

**Campos del payload:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `user_id` | `string (UUID)` | Identificador único del usuario en iam-service |
| `email` | `string` | Correo electrónico institucional del usuario |
| `first_name` | `string` | Nombre(s) del usuario |
| `last_name` | `string` | Apellido(s) del usuario |
| `document_type` | `string \| null` | Tipo de documento requerido para aprovisionar perfiles `INSTRUCTOR`/`LEARNER` en actors-service |
| `document_number` | `string \| null` | Número de documento requerido para aprovisionar perfiles `INSTRUCTOR`/`LEARNER` en actors-service |
| `default_max_hours_per_week` | `number \| null` | Tope semanal por defecto requerido cuando `actor_type=INSTRUCTOR` |
| `actor_type` | `string` | Tipo de actor: `INSTRUCTOR`, `LEARNER`, `USER` |
| `actor_id` | `string (UUID)` | Identificador del actor correspondiente en actors-service |
| `roles` | `object[]` | Lista de roles iniciales asignados al momento de la creación (`role_name`, `training_center_id`) |
| `created_at` | `string (ISO 8601)` | Fecha y hora de creación del usuario |

---

### `iam.user.deactivated`

Emitido cuando un usuario es desactivado por un administrador o por política del sistema.

```json
{
  "event_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "event_type": "iam.user.deactivated",
  "version": "1.0",
  "timestamp": "2026-06-20T14:15:00Z",
  "source_service": "iam-service",
  "correlation_id": "g2f3e4d5-c6b7-8901-gfed-cb1098765432",
  "payload": {
    "user_id": "usr_9f8e7d6c-5b4a-3210-fedc-ba9876543210",
    "email": "carlos.moreno@sena.edu.co",
    "reason": "contract_ended",
    "deactivated_by": "usr_admin_0a1b2c3d-4e5f-6789-abcd-ef0123456789",
    "deactivated_at": "2026-06-20T14:15:00Z"
  }
}
```

**Campos del payload:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `user_id` | `string (UUID)` | Identificador único del usuario desactivado |
| `email` | `string` | Correo electrónico del usuario desactivado |
| `reason` | `string` | Motivo de la desactivación: `contract_ended`, `policy_violation`, `request_by_user`, `inactivity`, `admin_action` |
| `deactivated_by` | `string (UUID)` | `user_id` del administrador que ejecutó la acción |
| `deactivated_at` | `string (ISO 8601)` | Fecha y hora de la desactivación |

---

### `iam.role.assigned`

Emitido cuando se asigna o reasigna un rol a un usuario, opcionalmente con alcance de centro de formación y fecha de expiración.

```json
{
  "event_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "event_type": "iam.role.assigned",
  "version": "1.0",
  "timestamp": "2026-06-20T09:00:00Z",
  "source_service": "iam-service",
  "correlation_id": "h3g4f5e6-d7c8-9012-hgfe-dc2109876543",
  "payload": {
    "user_id": "usr_9f8e7d6c-5b4a-3210-fedc-ba9876543210",
    "role_id": "role_4d5e6f7a-8b9c-0123-defa-456789012345",
    "role_name": "instructor",
    "training_center_id": "tc_7g8h9i0j-1k2l-3456-mnop-qrstuvwxyz01",
    "assigned_by": "usr_admin_0a1b2c3d-4e5f-6789-abcd-ef0123456789",
    "assigned_at": "2026-06-20T09:00:00Z",
    "expires_at": "2027-06-20T09:00:00Z"
  }
}
```

**Campos del payload:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `user_id` | `string (UUID)` | Identificador del usuario al que se le asigna el rol |
| `role_id` | `string (UUID)` | Identificador único del rol en el sistema RBAC |
| `role_name` | `string` | Nombre legible del rol: `instructor`, `evaluator`, `coordinator`, `admin`, `trainee` |
| `training_center_id` | `string (UUID) \| null` | Centro de formación en cuyo contexto aplica el rol; `null` si es global |
| `assigned_by` | `string (UUID)` | `user_id` del administrador que asignó el rol |
| `assigned_at` | `string (ISO 8601)` | Fecha y hora de la asignación |
| `expires_at` | `string (ISO 8601) \| null` | Fecha de expiración del rol; `null` si no expira |

---

### `iam.session.started`

Emitido cada vez que un usuario se autentica exitosamente y obtiene un JWT válido.

```json
{
  "event_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "event_type": "iam.session.started",
  "version": "1.0",
  "timestamp": "2026-06-20T08:45:00Z",
  "source_service": "iam-service",
  "correlation_id": "i4h5g6f7-e8d9-0123-ihgf-ed3210987654",
  "payload": {
    "user_id": "usr_9f8e7d6c-5b4a-3210-fedc-ba9876543210",
    "ip_address": "192.168.1.42",
    "user_agent_hint": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "session_id": "sess_5e6f7a8b-9c0d-1234-efab-567890123456",
    "started_at": "2026-06-20T08:45:00Z"
  }
}
```

**Campos del payload:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `user_id` | `string (UUID)` | Identificador del usuario que inicia sesión |
| `ip_address` | `string` | Dirección IP del cliente en formato IPv4 o IPv6 |
| `user_agent_hint` | `string` | Primeros 200 caracteres del User-Agent del cliente para auditoría |
| `session_id` | `string (UUID)` | Identificador único de la sesión JWT emitida |
| `started_at` | `string (ISO 8601)` | Fecha y hora de inicio de la sesión |

---

### `iam.scope_override.granted`

Se publica cuando IAM crea una excepción de feature para un usuario. El payload corresponde al registro confirmado por el caso de uso; `is_allowed` distingue una concesión de un bloqueo explícito. El esquema versionado está en [`iam.scope_override.granted.schema.json`](https://github.com/code-sena/design-software-shared-contracts/blob/develop/events/iam.scope_override.granted.schema.json).

```json
{
  "override_id": "f4c9f76b-235e-4c94-a08c-8015e1a746d8",
  "user_id": "c31de513-92ab-4a87-9f2c-e91068fbb391",
  "feature_code": "ACT_LEARNER_MANAGE",
  "scope_type": "TRAINING_CENTER",
  "is_allowed": true
}
```

### `iam.scope_override.revoked`

Se publica cuando IAM elimina una excepción de feature del usuario. El payload identifica la excepción revocada y al usuario al que pertenecía. El esquema versionado está en [`iam.scope_override.revoked.schema.json`](https://github.com/code-sena/design-software-shared-contracts/blob/develop/events/iam.scope_override.revoked.schema.json).

```json
{
  "override_id": "f4c9f76b-235e-4c94-a08c-8015e1a746d8",
  "user_id": "c31de513-92ab-4a87-9f2c-e91068fbb391"
}
```

## Eventos consumidos

iam-service no consume eventos de otros servicios. Es el servicio de identidad base.

Todos los demás servicios dependen de los eventos que iam-service publica; la dependencia es unidireccional.

---

## Formato de envelope

Todos los eventos publicados por iam-service siguen el mismo envelope estándar:

```json
{
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "event_type": "iam.user.created",
  "version": "1.0",
  "timestamp": "2026-06-20T10:30:00Z",
  "source_service": "iam-service",
  "correlation_id": "f1e2d3c4-b5a6-7890-fedc-ba0987654321",
  "payload": {
    "user_id": "usr_9f8e7d6c-5b4a-3210-fedc-ba9876543210",
    "email": "carlos.moreno@sena.edu.co",
    "first_name": "Carlos",
    "last_name": "Moreno",
    "document_type": "CC",
    "document_number": "1234567890",
    "default_max_hours_per_week": 40.0,
    "actor_type": "INSTRUCTOR",
    "actor_id": "act_1a2b3c4d-5e6f-7890-abcd-ef1234567890",
    "roles": [
      {
        "role_name": "INSTRUCTOR",
        "training_center_id": "33333333-3333-4333-8333-333333333333"
      }
    ],
    "created_at": "2026-06-20T10:30:00Z"
  }
}
```

**Campos del envelope:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `event_id` | `string (UUID v4)` | Identificador único e inmutable del evento. Permite deduplicación en consumidores |
| `event_type` | `string` | Nombre del evento en formato `<servicio>.<entidad>.<accion>` |
| `version` | `string` | Versión del schema del evento. Actualmente `"1.0"` para todos los eventos |
| `timestamp` | `string (ISO 8601)` | Fecha y hora UTC en que ocurrió el evento en la fuente |
| `source_service` | `string` | Servicio que publicó el evento. Siempre `"iam-service"` para este servicio |
| `correlation_id` | `string (UUID v4)` | ID de correlación para trazar la cadena de solicitudes a través de servicios |
| `payload` | `object` | Datos específicos del evento. Estructura varía según `event_type` |

---

## Política de reintentos

iam-service garantiza entrega **at-least-once** para todos los eventos publicados.

### Garantías de entrega

- **Semántica:** At-least-once delivery. Los consumidores deben implementar idempotencia usando `event_id`.
- **Orden:** Los eventos de un mismo `user_id` se publican en la misma partición para preservar el orden relativo.
- **Durabilidad:** Los eventos se persisten en el broker antes de confirmar la transacción de negocio.

### Reintentos del productor

| Intento | Espera antes del reintento | Condición |
|---------|---------------------------|-----------|
| 1 (inicial) | — | Fallo en publicación al broker |
| 2 | 30 segundos | Segundo fallo |
| 3 | 2 minutos | Tercer fallo |
| 4 | 10 minutos | Cuarto fallo (último) |

Tras 3 reintentos fallidos (4 intentos en total), el evento se envía a la **Dead Letter Queue**.

### Dead Letter Queue

- **Topic DLQ:** `iam-events.dlq`
- **Retención DLQ:** 7 días para inspección y reprocesamiento manual
- **Alerta:** Se genera alerta operacional cuando un mensaje llega al DLQ
- **Reprocesamiento:** Los mensajes del DLQ pueden ser reenviados manualmente al topic original tras diagnóstico

### Idempotencia en consumidores

Los consumidores (`actors-service`, `audit-service`) deben usar `event_id` como clave de idempotencia para evitar efectos duplicados ante reentregas.

---

## Topics

| Topic | Descripción | Retención | Particiones |
|-------|-------------|-----------|-------------|
| `iam-events` | Topic principal de iam-service. Contiene todos los eventos de identidad: creación/desactivación de usuarios, asignación de roles e inicio de sesiones | 7 días | 4 |
| `iam-events.dlq` | Dead Letter Queue para eventos que no pudieron ser publicados tras 3 reintentos | 7 días | 1 |

**Notas de configuración:**

- Las 4 particiones de `iam-events` permiten paralelismo en consumidores con hasta 4 instancias por consumer group.
- La clave de partición es `user_id` para garantizar orden de eventos por usuario.
- La retención de 7 días permite a nuevos consumidores hacer replay de eventos recientes durante onboarding o recovery.
