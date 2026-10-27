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

## Equivalencias de numeración (Reference Data, PR #340)

Las propuestas de Reference Data citadas como ADR-012 y ADR-013 en la revalidación QA del PR #340 se registran ahora como **ADR-020 y ADR-021**. Durante la integración de main, los identificadores 012 y 013 ya estaban asignados a Training Environment y Monitoring. Se conserva su historial en Git y se actualizan los enlaces de la propuesta, sin alterar los ADR de esos dominios.

| Identificador de la revisión previa | Identificador vigente | Estado |
|---|---|---|
| ADR-012 de Reference Data | [ADR-020](./records/ADR-020-reference-data-iam-e2e-integration.md) | PROPOSED |
| ADR-013 de Reference Data | [ADR-021](./records/ADR-021-reference-data-resilient-messaging.md) | PROPOSED |

La renumeración no equivale a aceptación. Arquitectura debe ratificar las responsabilidades y resolver los puntos abiertos de ambas propuestas.

## Registro

| ADR | Título | Estado |
|-----|--------|--------|
| [ADR-001](./records/ADR-001-message-broker.md) | Selección del broker de mensajes (RabbitMQ) | ACCEPTED |
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
| [ADR-020](./records/ADR-020-reference-data-iam-e2e-integration.md) | Integración real Reference Data/IAM/web-shell | PROPOSED |
| [ADR-021](./records/ADR-021-reference-data-resilient-messaging.md) | Inbox, retry, DLQ y replay de Reference Data | PROPOSED |
| [ADR-022](./records/ADR-022-edge-routing-table-by-domain.md) | Tabla de rutas del edge por dominio y origen único para el frontend | ACCEPTED |
| [ADR-023](./records/ADR-023-web-shell-owns-login-and-session.md) | El web-shell es dueño del login y de la sesión | ACCEPTED |
| [ADR-024](./records/ADR-024-monitoring-r2-performance.md) | Optimización de lecturas de Monitoring para R2 | PROPOSED |
| [ADR-025](./records/ADR-025-academic-resilient-messaging.md) | Mensajería resiliente para academic-management | PROPOSED |
| [ADR-027](./records/ADR-027-scheduling-r2-performance.md) | Rendimiento de consultas de Scheduling para R2 | PROPOSED |
| [ADR-030](./records/ADR-030-academic-ficha-lifecycle-preconditions.md) | Academic Management R4 security, lifecycle preconditions (RAP approval), cancellation and MFE integration | ACCEPTED |

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
- [ADR-020: Integración real Reference Data, IAM y web-shell](./records/ADR-020-reference-data-iam-e2e-integration.md) — propuesta (PROPOSED); antes ADR-012 de Reference Data en el PR #340.
- [ADR-021: Mensajería resiliente e inbox idempotente de Reference Data](./records/ADR-021-reference-data-resilient-messaging.md) — propuesta (PROPOSED); antes ADR-013 de Reference Data en el PR #340.
- [ADR-022: Tabla de rutas del edge por dominio y origen único para el frontend](./records/ADR-022-edge-routing-table-by-domain.md) — aceptada (ACCEPTED).
- [ADR-023: El web-shell es dueño del login y de la sesión](./records/ADR-023-web-shell-owns-login-and-session.md) — aceptada (ACCEPTED).
- [ADR-024: Optimización de lecturas de Monitoring para R2](./records/ADR-024-monitoring-r2-performance.md) — propuesta (PROPOSED), pendiente de revisión de Arquitectura.
- [ADR-025: Mensajería resiliente para academic-management](./records/ADR-025-academic-resilient-messaging.md) — propuesta (PROPOSED), pendiente de revisión de Arquitectura.
- [ADR-030: Academic Management R4 security, lifecycle preconditions (RAP approval), cancellation and MFE integration](./records/ADR-030-academic-ficha-lifecycle-preconditions.md) — aceptada (ACCEPTED) por el dueño el 2026-10-24.
