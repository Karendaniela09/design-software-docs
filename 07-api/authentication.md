# Estrategia de Autenticación y Autorización

> Estado: 🟢 Implementado (HU-IAM-010; refresh en cookie `HttpOnly`: HU-IAM-018) | Última actualización: 2026-10-24
> Relacionado: [iam-service/rbac-design.md](../09-microservices/services/01-iam-service/rbac-design.md),
> [iam-service/decisions.md](../09-microservices/services/01-iam-service/decisions.md) (DEC-008),
> [ADR-023](../05-architecture/decisions/records/ADR-023-web-shell-owns-login-and-session.md) §6 (almacenamiento de la sesión)

## Resumen

El sistema usa **JWT Bearer stateless** con refresh token. Cada servicio verifica el token
localmente (sin llamar a iam-service por request). La autorización es por **Feature + Scope**,
no por recurso + acción plano.

---

## Flujo de autenticación

```
Cliente                  API Gateway              iam-service
   │                         │                        │
   ├──POST /auth/login───────▶│                        │
   │                         ├───────────────────────▶│
   │                         │                        │ Verifica email + password
   │                         │                        │ Calcula features del usuario
   │                         │◀───────────────────────│
   │◀──access_token (cuerpo)─│                        │
   │   + Set-Cookie:         │                        │
   │   refresh_token         │                        │
   │   (HttpOnly)            │                        │
   │                         │                        │
   ├──GET /schedules─────────▶│                        │
   │  Bearer: access_token   │                        │
   │                         │ Verifica JWT localmente │
   │                         │ (sin llamar a IAM)      │
   │                         ├──forwarda request──────▶│scheduling-service
```

---

## Estructura del JWT — Access Token

```json
{
  "iss": "sena-iam-service",
  "sub": "uuid-del-usuario",
  "iat": 1750000000,
  "exp": 1750000900,
  "actor_type": "INSTRUCTOR",
  "actor_id": "uuid-del-instructor",
  "training_center_id": "uuid-del-centro",
  "roles": ["INSTRUCTOR"],
  "features": [
    "SCH_VIEW_OWN:OWN_SCHEDULE",
    "ACADEMIC_FICHA_VIEW_OWN:OWN_FICHAS",
    "MON_DASHBOARD_OWN:OWN_FICHAS",
    "MON_TRACKING_SESSION_CREATE:OWN_FICHAS",
    "MON_KPI_VIEW:OWN_FICHAS",
    "MON_ALERT_VIEW:OWN_FICHAS",
    "ACT_INSTRUCTOR_VIEW:OWN_PROFILE",
    "REF_CATALOG_VIEW:GLOBAL",
    "DASH_PERSONAL:GLOBAL"
  ]
}
```

### Campos del JWT

| Campo | Descripción |
|-------|-------------|
| `sub` | UUID del usuario en iam-service |
| `actor_type` | `USER` / `INSTRUCTOR` / `LEARNER` — tipo de actor en el sistema |
| `actor_id` | UUID del perfil en actors-service (null si actor_type = USER) |
| `training_center_id` | UUID del centro; null si el usuario tiene alcance global |
| `ficha_id` | UUID de la ficha activa del aprendiz. Solo se emite cuando `actor_type=LEARNER` y existe una ficha activa; no se emite para otros perfiles ni se conserva desde un token anterior. |
| `roles` | Lista de nombres de rol activos del usuario |
| `features` | Lista pre-calculada de `FEATURE_CODE:SCOPE_TYPE` |

**Por qué los features van pre-calculados en el JWT**: cada servicio verifica el token localmente
en O(1) sin llamar a IAM. Trade-off: cambios de rol aplican al siguiente login o refresh.
Mitigación: al revocar un rol crítico, se revoca también el refresh_token activo.

**Cálculo de `features`** (HU-IAM-010 E1): no es la lista plana de features del rol — es el
resultado de aplicar la política de HU-IAM-006 (`AuthorizationPolicy`) sobre el perfil de
autorización del usuario: por cada feature, se toma el scope más amplio entre sus grants por
rol; un override de bloqueo activo elimina la feature por completo (gana sobre cualquier rol);
un override de permiso activo agrega una feature que ningún rol concede. Se recalcula en cada
login y en cada refresh.

**Claims adicionales no listados en la tabla** (uso interno de iam-service, no forman parte del
contrato de autorización que consumen los servicios downstream): `sid` (session id, para que
`/auth/logout` identifique la sesión a revocar), `email`, `name`.

`ficha_id` es un claim contractual de integración entre IAM y los consumidores autorizados. IAM
lo obtiene de Actors mediante el endpoint interno protegido por mTLS y lo incluye únicamente en
JWT emitidos para perfiles `LEARNER`. El valor siempre representa el UUID de la ficha activa
resuelta para el usuario; ante ausencia de ficha, perfil inexistente o fallo controlado de Actors,
el login puede continuar, pero el JWT no contiene `ficha_id`. Scheduling consume este claim del
JWT y no consulta directamente el endpoint interno de Actors.

---

## Verificación en servicios downstream

Cada servicio verifica el JWT con la **clave pública de iam-service** (RS256 asimétrico).
La clave pública se expone en `GET /auth/.well-known/jwks.json` (estándar JWKS).

### Algoritmo de verificación (por servicio)

```
1. Extraer Bearer token del header Authorization
2. Verificar firma con public_key (RS256)
3. Verificar exp > now()
4. Verificar iss = "sena-iam-service"
5. Verificar que features[] contiene el feature requerido por el endpoint
6. Extraer scope_type y aplicar filtro de datos
```

### Aplicación del scope en queries

| scope_type | Filtro SQL a aplicar |
|-----------|---------------------|
| `GLOBAL` | Sin filtro adicional |
| `TRAINING_CENTER` | `WHERE training_center_id = $jwt.training_center_id` |
| `OWN_FICHAS` | `WHERE instructor_id = $jwt.actor_id` |
| `OWN_SCHEDULE` | `WHERE instructor_id = $jwt.actor_id` |
| `OWN_PROFILE` | `WHERE id = $jwt.actor_id` |
| `OWN_FICHA_AS_LEARNER` | `WHERE ficha_id IN (SELECT ficha_id FROM learner WHERE user_id = $jwt.sub)` |

---

## Renovación del token (Refresh Flow)

El refresh token viaja **solo en una cookie** (HU-IAM-018, [ADR-023](../05-architecture/decisions/records/ADR-023-web-shell-owns-login-and-session.md) §6). Nunca va en el cuerpo de una respuesta ni de una petición.

| Operación | Qué hace con la cookie `refresh_token` |
|-----------|----------------------------------------|
| `POST /auth/login` | La emite en `Set-Cookie` con `HttpOnly; Secure; SameSite=Strict; Path=/iam/api/v1/auth` y `Max-Age` de 7 días. El cuerpo trae `access_token`, `token_type`, `expires_in` y `user`, sin `refresh_token`. |
| `POST /auth/refresh` | Sin cuerpo. Lee la cookie y emite un `access_token` nuevo con los features recalculados (por si el rol cambió). Vuelve a emitir la misma cookie con `Max-Age` igual al tiempo que le queda a la sesión. El refresh token no rota. |
| `POST /auth/logout` | Revoca la sesión (la de la cookie y la del `sid` del access token, si vienen) y borra la cookie con `Max-Age=0` y los mismos atributos. |

El `Path` es el **público**: el edge quita el prefijo `/iam` ([ADR-022](../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md)), así que iam-service recibe `/api/v1/auth/...` pero emite la cookie con `Path=/iam/api/v1/auth`, la ruta que ve el navegador. Es configurable en el servicio (`IAM_REFRESH_COOKIE_PATH`) y su valor por defecto es el del edge; `Secure`, `HttpOnly` y `SameSite` no se configuran: son iguales en los 4 ambientes.

Si la cookie no viene (o viene vacía), `refresh` responde 401 `TOKEN_INVALID`. Si el refresh token es desconocido, venció o fue revocado, responde 401 `TOKEN_REVOKED`. En el cable, estos dos códigos propios de IAM llevan el prefijo del dominio: `IAM_TOKEN_INVALID` e `IAM_TOKEN_REVOKED`.

TTL refresh_token: 7 días. Si expira, el usuario debe hacer login nuevamente.

---

## Almacenamiento en cliente web

| Token | Almacenamiento | Razón |
|-------|---------------|-------|
| `access_token` | Memoria (JS) | Protege contra XSS; se pierde al recargar la página y se recupera con un `refresh` silencioso |
| `refresh_token` | Cookie `HttpOnly; Secure; SameSite=Strict; Path=/iam/api/v1/auth` | El JavaScript no la lee (XSS); el navegador solo la envía al propio origen (CSRF). Es de primera parte porque el edge da origen único (ADR-022) |

`Secure` exige HTTPS en todo ambiente desplegado, DEV incluido; en local funciona porque los navegadores tratan `http://localhost` como contexto seguro. No hay modo alterno por ambiente.

---

## Configuración de seguridad

| Parámetro | Valor |
|-----------|-------|
| Algoritmo | RS256 (asimétrico — la clave privada nunca sale de iam-service) |
| TTL access_token | 15 minutos |
| TTL refresh_token | 7 días |
| Clave privada | RSA 2048 bits; en Secret Manager (nunca en código ni en repositorio) |
| Rotación de claves | Trimestral; se soportan 2 claves activas durante la transición (via kid en JWKS) |

---

## Propagación entre servicios

Cuando scheduling-service llama a actors-service, propaga el JWT original del usuario
(no usa un token de servicio separado en el MVP). El scope del usuario aplica en toda la cadena.

---

## Errores estándar

| Situación | HTTP | error_code |
|-----------|------|------------|
| Sin header Authorization | 401 | `MISSING_TOKEN` |
| Token malformado o firma inválida | 401 | `TOKEN_INVALID` |
| Token expirado | 401 | `TOKEN_EXPIRED` |
| `POST /auth/refresh` sin la cookie `refresh_token` (o vacía) | 401 | `TOKEN_INVALID` |
| Refresh token revocado, vencido o desconocido | 401 | `TOKEN_REVOKED` |
| Feature no presente en JWT | 403 | `INSUFFICIENT_PERMISSIONS` |
| Feature presente pero scope insuficiente | 403 | `SCOPE_VIOLATION` |

---

## Roadmap de seguridad

| Mejora | Descripción | Fase |
|--------|-------------|------|
| 2FA (TOTP) | Segundo factor para COORDINATOR y CENTER_DIRECTOR | V2 |
| Token blacklist | Revocación inmediata sin esperar expiración del access_token | V2 |
| Token M2M | Access tokens de servicio para comunicación interna (evitar propagar JWT de usuario) | V2 |
| OAuth2 con IdP SENA | Integración con IdP institucional del SENA si se habilita SSO | V3 |
