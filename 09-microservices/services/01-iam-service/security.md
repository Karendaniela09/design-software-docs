# Seguridad — iam-service

> Estado: 🟡 Revisión | Última actualización: 2026-10-26

## Emisión y verificación de tokens

- IAM firma los access tokens con RS256 usando `IAM_JWT_PRIVATE_KEY`. El servicio no arranca si
  falta la clave privada o `IAM_JWT_ISSUER`; no se definen secretos ni emisores por defecto.
- El `kid` identifica la clave vigente (`IAM_JWT_KEY_ID`). Durante la rotación, IAM puede publicar
  además la clave pública anterior mediante `IAM_JWT_PREVIOUS_PUBLIC_KEY` y
  `IAM_JWT_PREVIOUS_KEY_ID`; ambas variables deben configurarse juntas.
- `GET /api/v1/auth/.well-known/jwks.json` publica las claves públicas. Nunca se publica la clave
  privada. Los servicios consumidores verifican localmente la firma y los claims del token usando
  este JWKS; no llaman a IAM en cada petición.
- El token contiene el `sub`, roles, features efectivos con scope, `training_center_id` y expiración.
  Cada servicio protegido aplica autorización sobre sus propios recursos y debe denegar cuando
  falten los permisos o el scope requerido.

## Sesión del navegador

El refresh token se entrega solo en la cookie `refresh_token`, con `HttpOnly`, `Secure`,
`SameSite=Strict` y el path público `/iam/api/v1/auth`. El login y la renovación no deben devolver
el refresh token en el cuerpo de la respuesta. El access token tiene una vida corta documentada en
el [contrato de autenticación](../../../07-api/authentication.md).

## Secretos y datos de operación

- Inyectar `IAM_JWT_PRIVATE_KEY`, credenciales de base de datos y secretos del broker desde el
  gestor de secretos del ambiente; no escribirlos en archivos versionados, logs ni reportes.
- Actuator Prometheus (`/actuator/prometheus`) es para la red interna de observabilidad y no debe
  exponerse por el edge. Las sondas `/health` y `/ready` se enrutan de acuerdo con
  [ADR-022](../../../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md).
- No registrar el bearer token ni el contenido de `Set-Cookie`. Para correlación operativa se usa
  `X-Correlation-Id` y las trazas OpenTelemetry, según el [runbook](./runbook.md).

## Decisión transversal pendiente

El proyecto todavía no define una política común de issuer y audience para todos los consumidores
(T-09 / MON-03). Esta página describe los requisitos observados en IAM; no establece una audience
que no esté acordada por Arquitectura.
