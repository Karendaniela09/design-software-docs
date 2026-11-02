<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: contrato de API (OpenAPI 3.1)
fase: diseño (api-first)
estado: accepted
dependencias_entrada: 09-microservices/services/01-iam-service/data-model.md, 07-api/guidelines.md, 07-api/contracts/openapi/_shared.yaml
consumidores_siguientes: backend iam-service, frontend, pruebas de contrato
tldr: Autenticación JWT + RBAC (users/roles/features/scope-overrides/sessions) con paginación y reporte login-audit por cursor. La fuente de verdad es openapi.yaml.

## Claim `ficha_id` para aprendices

Cuando IAM emite un JWT para un usuario cuyo perfil es exclusivamente `LEARNER`,
consulta a Actors mediante el endpoint interno protegido por mTLS
`GET /internal/learners/by-user/{user_id}/active-ficha`. Si existe una ficha
activa válida, IAM incluye `ficha_id` como un UUID en el JWT. El claim representa
la ficha activa actual del aprendiz y no debe conservarse de un token anterior.

Para perfiles distintos de `LEARNER`, IAM no consulta Actors y no emite
`ficha_id`. Si Actors responde sin ficha, con un perfil inexistente o con un
error controlado, el login puede continuar sin ese claim. Scheduling consume el
JWT de IAM y aplica `ficha_id` para el alcance propio del aprendiz; no consulta
directamente el endpoint interno de Actors.
decisiones_clave: OpenAPI publicable en 07-api/contracts/openapi/iam.yaml; envelope de error estándar (guidelines §7); reportes por servicio
halts_registrados: ninguno
-->

# Contrato — iam-api

> Estado: 🟢 Aceptado | Última actualización: 2026-10-24

> **Fuente de verdad (normativa):** el spec OpenAPI 3.1 en
> [`07-api/contracts/openapi/iam.yaml`](../../../../../07-api/contracts/openapi/iam.yaml).
> Este documento es la **narrativa** que lo explica; ante cualquier diferencia, **manda el
> `openapi.yaml`**. Convenciones transversales en [07-api/guidelines.md](../../../../../07-api/guidelines.md).

## Base URL

`/api/v1`

---

## Endpoints operacionales (fuera de `/api/v1`, HU-IAM-011)

No forman parte del contrato de negocio (no están en `iam.yaml`) — son un `@RestController` propio, expuesto en la raíz del servidor de la app (no bajo `/actuator`). Detalle operativo (SLO, semántica de cada chequeo) en [runbook.md](../../runbook.md#healthcheck).

| Endpoint | Uso | `200` cuando | `503` cuando |
|----------|-----|--------------|--------------|
| `GET /health` | Liveness probe | El proceso vive | (nunca por dependencias externas; solo si el proceso no responde) |
| `GET /ready` | Readiness probe | BD conecta, y broker AMQP conecta *si `spring.rabbitmq.host` está configurado* | BD no conecta, o el broker configurado no conecta |

Respaldan la propagación de trazas de [ADR-008](../../../../../05-architecture/decisions/records/ADR-008-observability-opentelemetry.md); no requieren `Authorization`.

Además, `GET /actuator/prometheus` (Spring Boot Actuator, HU-IAM-021) expone las métricas HTTP en formato Prometheus. Es un endpoint operativo de la red interna de observabilidad: no está en `iam.yaml`, no requiere `Authorization` y **no se enruta por el edge** (ADR-022 solo enruta `/iam/api/` y los health/ready exactos). Detalle en el [runbook](../../runbook.md#observabilidad-otel--hu-iam-011-correlación-y-métricas--hu-iam-021).

### Cabecera transversal `X-Correlation-Id` (HU-IAM-021)

Todas las respuestas, también las de error, devuelven `X-Correlation-Id`. Si la petición trae la cabecera con 1 a 128 caracteres entre letras, dígitos, `.`, `_` o `-`, el servicio conserva ese valor; si falta o no es válida, genera un UUID. El valor aparece como `correlation_id` en los logs JSON de la petición. Es un cambio aditivo: no altera rutas, parámetros ni esquemas de `iam.yaml`. No sustituye al contexto W3C `traceparent`: el `trace_id` del cuerpo de error es el de la traza OpenTelemetry activa (con respaldo a `X-Request-Id` y, si no hay ninguno, un UUID).

---

## Autenticación

### `POST /auth/login`

Login con email y contraseña. No requiere token.

**Request:**
```json
{ "email": "coordinador@sena.edu.co", "password": "plain-text-password" }
```

**Response 200:**
```http
HTTP/1.1 200 OK
Set-Cookie: refresh_token=Zm9vYmFy...; Path=/iam/api/v1/auth; Max-Age=604800; Expires=...; Secure; HttpOnly; SameSite=Strict
Content-Type: application/json
```
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "coordinador@sena.edu.co",
    "full_name": "María García",
    "roles": ["COORDINATOR"],
    "training_center_id": "uuid-del-centro",
    "features": ["SCH_CREATE:TRAINING_CENTER", "SCH_PUBLISH:TRAINING_CENTER", "..."]
  }
}
```

El `access_token` lleva pre-calculados los features del usuario. TTL: 15 min.

El refresh token (TTL: 7 días) viaja **solo** en la cookie `refresh_token` de `Set-Cookie` y **ya no está en el cuerpo** (HU-IAM-018, [ADR-023](../../../../../05-architecture/decisions/records/ADR-023-web-shell-owns-login-and-session.md) §6). Atributos de la cookie, iguales en los 4 ambientes: `HttpOnly; Secure; SameSite=Strict; Path=/iam/api/v1/auth`. El `Path` es el público: el edge quita el prefijo `/iam` ([ADR-022](../../../../../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md)), así que el servicio recibe `/api/v1/auth/...` pero emite la cookie con la ruta que ve el navegador; se configura con `IAM_REFRESH_COOKIE_PATH` (ver [runbook](../../runbook.md)).

### `POST /auth/refresh`

Renueva el access_token usando la cookie `refresh_token`. No requiere Authorization header ni cuerpo.

**Request:** sin cuerpo. El navegador envía `Cookie: refresh_token=...` por sí solo.

**Response 200:** igual a la de `/auth/login`: `access_token`, `token_type`, `expires_in` y `user` con los features recalculados. El refresh token no rota; la respuesta vuelve a emitir la misma cookie con `Max-Age` igual al tiempo que le queda a la sesión.

**Response 401:**
- Sin la cookie, o vacía: `TOKEN_INVALID` (en el cable, `IAM_TOKEN_INVALID`).
- Refresh token desconocido, vencido o revocado: `TOKEN_REVOKED` (en el cable, `IAM_TOKEN_REVOKED`).

### `POST /auth/logout`

Revoca la sesión y borra la cookie `refresh_token`. Idempotente.

**Headers:** `Authorization: Bearer <access_token>` o la cookie `refresh_token` (basta una; si vienen las dos, se revoca cada sesión). Sin ninguna de las dos válida, responde 401.

**Response 204:** sin body. Siempre trae el borrado de la cookie:
```http
HTTP/1.1 204 No Content
Set-Cookie: refresh_token=; Path=/iam/api/v1/auth; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Secure; HttpOnly; SameSite=Strict
```

### `GET /auth/me`

Información del usuario autenticado con todos sus features calculados.

**Headers:** `Authorization: Bearer <access_token>`

**Response 200:**
```json
{
  "id": "uuid",
  "email": "...",
  "full_name": "...",
  "actor_type": "INSTRUCTOR",
  "actor_id": "uuid-del-instructor",
  "roles": [{ "name": "INSTRUCTOR", "training_center_id": "uuid" }],
  "features": ["SCH_VIEW_OWN:OWN_SCHEDULE", "ACT_INSTRUCTOR_VIEW:OWN_PROFILE", "..."],
  "modules": ["MOD_SCHEDULING", "MOD_ACTORS", "MOD_MONITORING", "MOD_NOTIFICATIONS"]
}
```

`modules` lista los módulos donde el usuario tiene al menos un feature activo (informativo; desde HU-SHELL-019 el menú de la UI NO se deriva de `modules` sino de `features` + `actor_type`, ver [visual-spec §4.2](../../../../../12-ux-ui/visual-spec.md); `modules` se conserva solo como respaldo).

### `POST /auth/password-reset/request`

Solicita un token de reset de contraseña enviado al email.

**Request:**
```json
{ "email": "usuario@sena.edu.co" }
```

**Response 202:** Siempre 202 (no revela si el email existe o no).

### `POST /auth/password-reset/confirm`

Confirma el reset de contraseña con el token recibido por email.

**Request:**
```json
{ "token": "...", "new_password": "nueva-contraseña" }
```

**Response 204.**

### `GET /auth/.well-known/jwks.json`

HU-IAM-010 E2/E3 — clave(s) pública(s) RSA para verificación local del `access_token` (RS256),
formato JWKS estándar (RFC 7517). No requiere `Authorization`. Durante una rotación de clave
responde con dos entradas (actual + saliente, cada una con su `kid`). Detalle completo —
estructura del JWT, algoritmo de verificación por servicio, rotación — en
[`authentication.md`](../../../../../07-api/authentication.md).

> Este endpoint es intencionalmente **externo al OpenAPI de dominio** (`iam.yaml`): es un
> endpoint de infraestructura de seguridad estándar (como `/actuator/health`), no un recurso
> de negocio versionado por el contrato de `iam-api`.

**Response 200:**
```json
{
  "keys": [
    { "kty": "RSA", "use": "sig", "alg": "RS256", "kid": "iam-rsa-1", "n": "...", "e": "AQAB" }
  ]
}
```

---

## Gestión de usuarios

### `GET /users`

Lista usuarios. Paginado.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `training_center_id` | UUID (query) | Filtrar por centro |
| `role` | STRING (query) | Filtrar por nombre de rol |
| `is_active` | BOOLEAN (query) | Filtrar por estado |
| `page` | INT | Default 1 |
| `page_size` | INT | Default 20, max 100 |

**Feature requerido:** `IDENTITY_USER_VIEW`

### `POST /users`

Crea un usuario nuevo.

**Feature requerido:** `IDENTITY_USER_MANAGE`

**Request:**
```json
{
  "email": "nuevo@sena.edu.co",
  "full_name": "Nombre Completo",
  "actor_type": "INSTRUCTOR",
  "actor_id": "uuid-del-instructor",
  "initial_role": "INSTRUCTOR",
  "training_center_id": "uuid-del-centro"
}
```

**Response 201:**
```json
{ "id": "uuid", "email": "...", "temporary_password": "..." }
```

La contraseña temporal se envía también al email del usuario.

### `GET /users/{id}`

**Feature requerido:** `IDENTITY_USER_VIEW`

### `PUT /users/{id}`

Actualizar datos del usuario (no contraseña).

**Feature requerido:** `IDENTITY_USER_MANAGE`

### `POST /users/{id}/deactivate`

Desactiva la cuenta (soft delete). Revoca todos los refresh tokens activos.

**Feature requerido:** `IDENTITY_USER_MANAGE`

### `GET /users/{id}/sessions`

Lista sesiones activas (refresh tokens válidos) del usuario.

**Feature requerido:**
- Ninguno cuando el usuario autenticado consulta sus propias sesiones (autogestión).
- `IDENTITY_USER_VIEW` efectivo cuando un administrador global (`SYSTEM_ADMIN` sin centro de
  formación) consulta las sesiones de otro usuario.

### `DELETE /users/{id}/sessions/{session_id}`

Revoca una sesión específica. El usuario autenticado puede cerrar una sesión propia (autogestión).

**Feature requerido:**
- Ninguno cuando la sesión pertenece al usuario autenticado (autogestión).
- `IDENTITY_USER_MANAGE` efectivo cuando un administrador global revoca una sesión ajena.

Un administrador que solo dispone de `IDENTITY_USER_VIEW` no puede revocar sesiones de otros usuarios.

> **Trazabilidad:** Alineado con la regla de autorización de sesiones implementada en
> [iam-service#44](https://github.com/code-sena/design-software-iam-service/pull/44)
> (IAM R4, merge `c7735cf`, octubre de 2026): consulta y revocación de sesiones propias sin
> feature; consulta de sesiones ajenas con `IDENTITY_USER_VIEW` y revocación con
> `IDENTITY_USER_MANAGE`, ambas solo para un administrador global. Esta regla aún no tiene un ADR
> propio: el ADR-018 trata la validación del estado de sesión, no el reparto VIEW/MANAGE.

---

## Gestión de roles y features

### `GET /roles`

Lista todos los roles con sus features y scopes.

**Feature requerido:** `IDENTITY_ROLE_VIEW`

### `GET /roles/{id}/features`

Lista los features asignados a un rol, con su scope_type.

**Feature requerido:** `IDENTITY_ROLE_VIEW`

### `POST /users/{id}/roles`

Asigna un rol a un usuario.

**Feature requerido:** `IDENTITY_ROLE_ASSIGN`

**Request:**
```json
{
  "role_name": "COORDINATOR",
  "training_center_id": "uuid-del-centro",
  "expires_at": null
}
```

### `DELETE /users/{id}/roles/{role_name}`

Revoca un rol de un usuario.

**Feature requerido:** `IDENTITY_ROLE_ASSIGN`

---

## Gestión de módulos y features (solo lectura)

### `GET /modules`

Lista todos los módulos del sistema con sus features.

**Feature requerido:** `IDENTITY_ROLE_VIEW`

**Response:**
```json
[
  {
    "code": "MOD_SCHEDULING",
    "name": "Horarios",
    "features": [
      { "code": "SCH_CREATE", "name": "Crear horario", "action_level": "WRITE" },
      ...
    ]
  }
]
```

---

## Overrides de scope

### `GET /users/{id}/scope-overrides`

Lista los overrides activos de un usuario.

**Feature requerido:** `IDENTITY_SCOPE_MANAGE`

### `POST /users/{id}/scope-overrides`

Crea un override de acceso para un usuario.

**Feature requerido:** `IDENTITY_SCOPE_MANAGE`

**Request:**
```json
{
  "feature_code": "SCH_VIEW_ALL",
  "scope_type": "TRAINING_CENTER",
  "is_allowed": true,
  "reason": "Cubriendo al coordinador durante licencia",
  "expires_at": "2026-07-15T23:59:59Z"
}
```

### `DELETE /users/{id}/scope-overrides/{override_id}`

Revoca un override.

---

## Reportes (dominio propio)

### `GET /reports/login-audit`

Auditoría de intentos de login sobre la tabla `audit_login`. **Solo lectura**, paginación por
**cursor** (colección grande/continua, guidelines §6).

- **Feature requerido:** `AUDIT_LOG_VIEW`.
- **Filtros:** `user_id`, `email`, `outcome`, `from`, `to`.
- **Inventario:** Usuarios: seguridad/administración · Frecuencia: on-demand · Formato: JSON · Fuente: `identity_audit.audit_login`.

---

## Formato de error estándar

Aplica el **envelope estándar de la plataforma** ([guidelines §7](../../../../../07-api/guidelines.md) /
`_shared.yaml#/components/schemas/Error`):

```json
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "No tiene acceso a este recurso",
    "details": [ { "field": "required_feature", "issue": "SCH_PUBLISH" } ],
    "trace_id": "uuid-v4"
  }
}
```

> El campo `required_feature` del borrador anterior se transporta ahora dentro de `details`
> para no romper el envelope común. Los **códigos** de dominio siguen vigentes:

## Códigos de error propios

| Código | HTTP | Descripción |
|--------|------|-------------|
| `INVALID_CREDENTIALS` | 401 | Email o contraseña incorrectos |
| `ACCOUNT_LOCKED` | 401 | Cuenta bloqueada temporalmente |
| `ACCOUNT_INACTIVE` | 401 | Cuenta desactivada |
| `TOKEN_EXPIRED` | 401 | Access token expirado |
| `TOKEN_REVOKED` | 401 | Refresh token revocado, vencido o desconocido (en el cable, `IAM_TOKEN_REVOKED`) |
| `TOKEN_INVALID` | 401 | Token malformado o firma inválida; también `POST /auth/refresh` sin la cookie `refresh_token` (en el cable, `IAM_TOKEN_INVALID`) |
| `INSUFFICIENT_PERMISSIONS` | 403 | No tiene el feature requerido |
| `SCOPE_VIOLATION` | 403 | Tiene el feature pero no el scope (intenta acceder a datos de otro centro) |
| `USER_NOT_FOUND` | 404 | Usuario no encontrado |
| `RESET_TOKEN_EXPIRED` | 400 | Token de reset expirado o ya usado |
| `RATE_LIMIT_EXCEEDED` | 429 | Demasiados intentos de login o reset |
