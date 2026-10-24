# Architecture Decision Records (ADR)

## Convenciones

- Formato: `ADR-NNN-titulo-corto.md`
- Los ADRs **nunca se eliminan ni se mueven** — permanecen en `records/` con `status: DEPRECATED`
- Cuando una ADR queda obsoleta: cambiar su estado a `DEPRECATED` y agregar al inicio del archivo una línea como `> Reemplazada por: ADR-NNN-nueva.md`
- `99-archive/old-decisions/` se usa solo para documentos de decisión que existían antes de adoptar el formato ADR
- Numeración secuencial desde `ADR-001`

## Template

Usar el archivo [`_template-adr.md`](./_template-adr.md):

```bash
# Reemplazar NNN con el número siguiente y el título con kebab-case
cp 05-architecture/decisions/_template-adr.md \
   05-architecture/decisions/records/ADR-NNN-titulo-corto.md
```

## Registro

| ADR | Título | Estado |
|-----|--------|--------|
| [ADR-001](./records/ADR-001-message-broker.md) | Selección del broker de mensajes (RabbitMQ) | PROPOSED |
| [ADR-002](./records/ADR-002-scheduling-read-models.md) | Read models para reducir dependencias síncronas de scheduling | PROPOSED |
| [ADR-003](./records/ADR-003-object-storage.md) | Estrategia de almacenamiento de objetos (MinIO/S3) | PROPOSED |
| [ADR-004](./records/ADR-004-status-parametrization-and-audit-standard.md) | Parametrización de estados y estándar de auditoría | PROPOSED |
| [ADR-005](./records/ADR-005-microservices-topology-and-transversal-capabilities.md) | Topología de microservicios y capacidades transversales | ACCEPTED |
| [ADR-006](./records/ADR-006-polyglot-stack-strategy.md) | Estrategia de stack polyglot (Go, Java, Python, Node) | ACCEPTED |
| [ADR-007](./records/ADR-007-edge-gateway-and-port-convention.md) | Edge gateway y convención de puertos | ACCEPTED |
| [ADR-008](./records/ADR-008-observability-opentelemetry.md) | Observabilidad — OpenTelemetry + Grafana (LGTM) | ACCEPTED |
| [ADR-009](./records/ADR-009-frontend-framework-and-build-strategy.md) | Framework de frontend y estrategia de compilación | ACCEPTED |
| [ADR-010](./records/ADR-010-monitoring-r3-observability.md) | Observabilidad de Monitoring para R3 | PROPOSED |
| [ADR-011](./records/ADR-011-document-outbox-inbox-resilience.md) | Outbox transaccional e inbox idempotente para document-service | ACCEPTED |
| [ADR-012](./records/ADR-012-training-environment-r3-observability.md) | Observabilidad integral en Training Environment (OpenTelemetry, RED, PostgreSQL, Grafana) | ACCEPTED |
| [ADR-013](./records/ADR-013-monitoring-r6-text-jsonb-migration.md) | Migración progresiva de TEXT a JSONB en planes de mejoramiento de Monitoring | PROPOSED |
| [ADR-014](./records/ADR-014-audit-r5-contract-compatibility.md) | Compatibilidad ejecutable de contratos del dominio de Auditoría | ACCEPTED |
| [ADR-015](./records/ADR-015-scheduling-security-hardening.md) | Scheduling service security hardening and cryptographic JWT validation | ACCEPTED |
| [ADR-016](./records/ADR-016-audit-r2-performance-data.md) | Rendimiento reproducible de las consultas de Auditoría | PROPOSED |
| [ADR-017](./records/ADR-017-training-environment-r6-schema-evolution.md) | Evolución de maintenance.reason a reason_detail — Training Environment R6 | PROPOSED |
| [ADR-018](./records/ADR-018-iam-session-revocation-r4.md) | Validación del estado de sesión y límites de revocación en IAM R4 | PROPOSED |
| [ADR-019](./records/ADR-019-actors-security-hardening.md) | Actors service security hardening, OAuth2 RS256, mTLS, and fine-grained RBAC | PROPOSED |
| [ADR-022](./records/ADR-022-edge-routing-table-by-domain.md) | Tabla de rutas del edge por dominio y origen único para el frontend | ACCEPTED |
| [ADR-023](./records/ADR-023-web-shell-owns-login-and-session.md) | El web-shell es dueño del login y de la sesión | ACCEPTED |

- [ADR-010: Observabilidad de Monitoring para R3](./records/ADR-010-monitoring-r3-observability.md) — propuesta, pendiente de revisión.
- [ADR-011: Outbox transaccional e inbox idempotente para document-service](./records/ADR-011-document-outbox-inbox-resilience.md) — aceptada.
- [ADR-012: Observabilidad de Training Environment para R3](./records/ADR-012-training-environment-r3-observability.md) — aceptada.
- [ADR-013: Migración progresiva de TEXT a JSONB en planes de mejoramiento de Monitoring](./records/ADR-013-monitoring-r6-text-jsonb-migration.md) — propuesta, pendiente de aprobación.
- [ADR-014: Compatibilidad ejecutable de contratos del dominio de Auditoría](./records/ADR-014-audit-r5-contract-compatibility.md) — aceptada; decisión final de R5.
- [ADR-015: Scheduling service security hardening and cryptographic JWT validation](./records/ADR-015-scheduling-security-hardening.md) — aceptada.
- [ADR-016: Rendimiento reproducible de las consultas de Auditoría](./records/ADR-016-audit-r2-performance-data.md) — propuesta, pendiente de revisión arquitectónica.
- [ADR-017: Evolución gradual del motivo de mantenimiento (Training Environment R6)](./records/ADR-017-training-environment-r6-schema-evolution.md) — propuesta, pendiente de revisión.
- [ADR-018: Validación del estado de sesión en IAM R4](./records/ADR-018-iam-session-revocation-r4.md) — propuesta (PROPOSED).
- [ADR-019: Actors service security hardening, OAuth2 RS256, mTLS, and fine-grained RBAC](./records/ADR-019-actors-security-hardening.md) — propuesta (PROPOSED).
- [ADR-022: Tabla de rutas del edge por dominio y origen único para el frontend](./records/ADR-022-edge-routing-table-by-domain.md) — aceptada (ACCEPTED).
- [ADR-023: El web-shell es dueño del login y de la sesión](./records/ADR-023-web-shell-owns-login-and-session.md) — aceptada (ACCEPTED).
