# Arquitectura

> Estado: 🟡 En progreso | Última actualización: 2026-08-01
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Arquitectura

Índice de la sección de arquitectura del sistema de Gestión de Horarios SENA. Aquí vive la vista técnica del sistema: el estilo arquitectural, los patrones, las decisiones formales (ADR) y las preocupaciones transversales.

## Estado real del sistema

El diseño describe una plataforma de **9 microservicios** con DDD + Hexagonal, comunicación REST síncrona y eventos asíncronos. **Hoy solo existe la capa de datos**: los repositorios `*-db` con migraciones **Liquibase** sobre **PostgreSQL 16** en **Docker**, con una única base de datos y un **schema por módulo**. La capa de aplicación (APIs, workers, broker, gateway) está **prevista, no construida**. Los documentos de esta sección distinguen de forma explícita lo que existe de lo que está planificado.

## Archivos

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [overview.md](./overview.md) | Vista general: componentes C4, flujos, contratos de borde y NFRs | 🟡 |
| [pattern-guide.md](./pattern-guide.md) | Patrón seleccionado (microservicios + DDD + Hexagonal), reglas de dependencia y bounded contexts | 🟡 |
| [cross-cutting.md](./cross-cutting.md) | Preocupaciones transversales: IAM/RBAC, auditoría, observabilidad, estados parametrizables, errores, idempotencia, zona horaria | 🟡 |
| [deployment.md](./deployment.md) | Topología de despliegue: Postgres en contenedor, runners Liquibase por módulo, promoción por ambientes y estado objetivo | 🟡 |
| [security-threat-model.md](./security-threat-model.md) | Modelo de amenazas STRIDE, controles, superficie de BD y pendientes de seguridad | 🟡 |
| [decisions/](./decisions/) | Registro de decisiones de arquitectura (ADR) | 🟡 |

## Decisiones de arquitectura (ADR)

Toda decisión que cruce una frontera de bounded context o afecte a más de un servicio se documenta como ADR en [decisions/records/](./decisions/records/). ADR vigentes (estado PROPOSED):

| ADR | Decisión | Documentos transversales que la implementan |
|-----|----------|----------------------------------------------|
| [ADR-001](./decisions/records/ADR-001-message-broker.md) | Broker de mensajes asíncrono (RabbitMQ) para eventos | [cross-cutting.md](./cross-cutting.md) §Idempotencia · [deployment.md](./deployment.md) |
| [ADR-002](./decisions/records/ADR-002-scheduling-read-models.md) | Read models en `scheduling-service` para reducir dependencias síncronas a ≤ 2 (CQRS-lite) | [pattern-guide.md](./pattern-guide.md) §Reglas de dependencia |
| [ADR-003](./decisions/records/ADR-003-object-storage.md) | Object storage compatible S3 (MinIO en DEV/QA) para documentos/PDFs | [security-threat-model.md](./security-threat-model.md) I-04 |
| [ADR-004](./decisions/records/ADR-004-status-parametrization-and-audit-standard.md) | Estados parametrizables + estándar de auditoría append-only y soft delete | [cross-cutting.md](./cross-cutting.md) §Estados y §Auditoría · [06-data/modeling-conventions.md](../06-data/modeling-conventions.md) |
| [ADR-018](./decisions/records/ADR-018-iam-session-revocation-r4.md) | Revocación de sesiones en IAM para R4 | [informe QA](../11-quality/qa-report-r4-security-iam.md) |
| [ADR-019](./decisions/records/ADR-019-actors-security-hardening.md) | Endurecimiento de seguridad de Actors para R4 | [informe QA](../11-quality/qa-report-r4-security-actors.md) |
| [ADR-027](./decisions/records/ADR-027-scheduling-r2-performance.md) | Rendimiento de consultas de Scheduling para R2 | [informe QA](../11-quality/qa-report-r2-scheduling-service.md) |

## Relación con 09-microservices

Esta sección da la vista **global**: cómo encajan los 9 servicios entre sí. El detalle **por servicio** (data-model, contratos de API, eventos publicados, read models) vive en [09-microservices](../09-microservices/). La correspondencia es:

- El **mapa de dependencias** y las **reglas de frontera** se especifican en [09-microservices/dependency-map.md](../09-microservices/dependency-map.md) y [service-boundary-rules.md](../09-microservices/service-boundary-rules.md); aquí se resumen en [pattern-guide.md](./pattern-guide.md).
- El **catálogo de eventos** ([09-microservices/event-catalog.md](../09-microservices/event-catalog.md)) es la vista técnica de los [eventos de dominio](../02-domain/domain-events.md); ADR-001 decide el transporte.
- La **propiedad de datos** por servicio ([data-ownership-matrix.md](../09-microservices/data-ownership-matrix.md)) hace cumplir la regla "una base de datos por servicio" (hoy: un schema por módulo en una sola BD).

## Referencias

- [02-domain/domain-map.md](../02-domain/domain-map.md) — diseño estratégico (bounded contexts, context map)
- [06-data/modeling-conventions.md](../06-data/modeling-conventions.md) — estándar de modelado y auditoría (ADR-004)
- [10-devops/](../10-devops/) — setup local, CI/CD y ambientes
