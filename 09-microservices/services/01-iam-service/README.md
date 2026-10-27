# iam-service

> Estado: 🟡 Revisión | Última actualización: 2026-10-26
> Autor: Kevin Andrey Culma (Arquitecto) | Equipo: Arquitectura.

| Campo | Valor |
|---|---|
| Módulo | M1 |
| App repo | `design-software-iam-service` |
| DB repo | `design-software-iam-db` |
| Stack | Java / Spring Boot / Maven |
| Deployables | iam-api |
| Estado observado | Implementado con contrato OpenAPI y controladores que implementan interfaces generadas. |

## Responsabilidad

Identidad, autenticación, sesiones, RBAC, JWT/JWKS y auditoría de login.

## Persistencia

- Esquemas: identity, identity_audit, rbac, rbac_catalog, session
- Tablas: identity.outbox, identity.user, identity_audit.audit_login, rbac.role, rbac.role_feature, rbac.user_role, rbac.user_scope_override, rbac_catalog.feature, rbac_catalog.module, session.password_reset_request, session.refresh_token

## API detectada

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/api/v1/auth/.well-known/jwks.json` | `.\design-software-iam-service\iam-adapters\src\main\java\co\sena\iam\adapter\in\rest\JwksController.java` |
| GET | `/health` | `.\design-software-iam-service\iam-adapters\src\main\java\co\sena\iam\adapter\in\rest\HealthController.java` |
| GET | `/ready` | `.\design-software-iam-service\iam-adapters\src\main\java\co\sena\iam\adapter\in\rest\HealthController.java` |

## Configuración

- `IAM_DB_DSN`
- `IAM_DB_PASSWORD`
- `IAM_DB_USERNAME`
- `IAM_EVENTS_EXCHANGE`
- `IAM_JWT_ISSUER`
- `IAM_JWT_KEY_ID`
- `IAM_JWT_PREVIOUS_KEY_ID`
- `IAM_JWT_PREVIOUS_PUBLIC_KEY`
- `IAM_JWT_PRIVATE_KEY`
- `IAM_OUTBOX_RELAY_BATCH_SIZE`
- `IAM_OUTBOX_RELAY_INITIAL_DELAY_MS`
- `IAM_OUTBOX_RELAY_POLL_INTERVAL_MS`

## Notas

Publica eventos IAM por outbox/RabbitMQ; expone JWKS para validación de JWT por otros servicios.

## Seguridad

La configuración del emisor RS256, la publicación JWKS, la rotación de claves, las cookies de
refresh y los límites operativos están documentados en [security.md](./security.md). La política
común de audiencia entre servicios continúa pendiente de decisión transversal (T-09).
