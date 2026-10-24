# Secuencia — Login + emisión de JWT (`iam-service`)

> Estado: 🟢 Listo | Última actualización: 2026-10-24
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Arquitectura
> Alcance: flujo construido y probado en `develop` (Java / Spring). Fuente de comportamiento: [authentication.md](../../../07-api/authentication.md), [DEC-001](../../../09-microservices/services/01-iam-service/decisions.md) y [data-model del iam-service](../../../09-microservices/services/01-iam-service/data-model.md).

Flujo de autenticación por contraseña: validación de credenciales, verificación de bloqueo por
intentos fallidos (lockout), emisión del par de tokens JWT (RS256) y registro síncrono de la
auditoría de login más el *staging* del evento `iam.session.started` en el Outbox (misma
transacción). El JWT se firma con RS256; el `access token` vive 15 min y el `refresh token` 7 días.

```mermaid
sequenceDiagram
    autonumber
    actor Cliente
    participant API as iam-api (AuthController)
    participant Svc as AuthService
    participant DB as iam_db (identity/session)

    Cliente->>API: POST /api/v1/auth/login (email, password)
    API->>Svc: authenticate(email, password)
    Svc->>DB: SELECT user WHERE email
    DB-->>Svc: user (hash bcrypt, failed_attempts, locked_until)

    alt Usuario bloqueado (locked_until > now)
        Svc-->>API: LockedException
        API-->>Cliente: 423 Locked
    else Credenciales inválidas
        Svc->>Svc: bcrypt.verify(password, hash) = false
        Svc->>DB: UPDATE failed_attempts += 1 (lockout si excede umbral)
        Svc->>DB: INSERT audit_login (result = FAILURE)
        Svc-->>API: BadCredentialsException
        API-->>Cliente: 401 Unauthorized
    else Credenciales válidas
        Svc->>Svc: bcrypt.verify(password, hash) = true
        Svc->>DB: reset failed_attempts = 0
        Svc->>Svc: cargar roles/features/scopes (RBAC)
        Svc->>Svc: firmar access token RS256 (exp 15m) + refresh token (exp 7d)
        Note over Svc,DB: misma transacción
        Svc->>DB: INSERT refresh_token (hash SHA-256)
        Svc->>DB: INSERT audit_login (result = SUCCESS)
        Svc->>DB: INSERT identity.outbox (event = iam.session.started, payload en columna data)
        Svc-->>API: TokenPair (access, refresh)
        API-->>Cliente: 200 OK { access_token, ... } + Set-Cookie: refresh_token (HttpOnly; Secure; SameSite=Strict)
    end
```

## Notas

- El bloque `INSERT identity.outbox` deja el evento en *staging*; su publicación a `iam-events`
  la realiza el relay de forma asíncrona — ver [outbox-relay-events.md](./outbox-relay-events.md).
- El evento se persiste bajo la columna `data`; el relay lo renombra a `payload` al publicar.
- La clave pública de verificación RS256 se expone vía JWKS ([DEC-008](../../../09-microservices/services/01-iam-service/decisions.md)); los servicios downstream validan el token localmente sin llamar a iam.
- Cobertura de prueba: cubierto por las suites de `iam` (unit + ITs contra Postgres real: login, refresh, RBAC) y por el E2E de compose (login→JWT→endpoints→outbox→relay).
