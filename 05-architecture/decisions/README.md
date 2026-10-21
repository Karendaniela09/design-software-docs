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
| [ADR-011](./records/ADR-011-document-outbox-inbox-resilience.md) | Outbox transaccional e inbox idempotente para document-service | ACCEPTED |
| [ADR-012](./records/ADR-012-actors-security-hardening.md) | Seguridad y control de acceso para actors-service (OAuth2 RS256, mTLS, RBAC) | ACCEPTED |

- [ADR-010: Observabilidad de Monitoring para R3](./records/ADR-010-monitoring-r3-observability.md) — propuesta, pendiente de revisión.

