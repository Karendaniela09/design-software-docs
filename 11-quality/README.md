# Calidad

> Estado: 🟡 En progreso | Última actualización: 2026-08-28
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Calidad

## Contexto

Esta sección define cómo se asegura la calidad del sistema **Horarios SENA**. La construcción avanza por capas y hoy conviven **dos estados** distintos: dos microservicios ya tienen **capa de aplicación construida y probada en `develop`** — `iam-service` (Java / Spring, 12/12 HU) y `notification-service` (Go, 8/8 HU) — mientras que el resto de servicios aún viven solo en su **capa de datos** (repos `*-db` con Liquibase + PostgreSQL 16). El stack es **políglota Java + Go** por decisión de arquitectura ([ADR-006](../05-architecture/decisions/records/ADR-006-polyglot-stack-strategy.md): polyglot fit-driven), no un único lenguaje.

Por eso la estrategia de calidad ya distingue **tres frentes activos**: (1) la **capa de datos** de todos los servicios (migraciones, DDL, seeds, restauración de BD); (2) la **capa de aplicación viva** de `iam` y `notification` (unitarias, contrato/Pact, integración y E2E reales); y (3) lo que aún se probará cuando el resto de servicios construyan su capa de aplicación. La evidencia de lo construido vive en las páginas de servicio: [iam-service](../09-microservices/services/01-iam-service/README.md) ([decisiones](../09-microservices/services/01-iam-service/decisions.md)) y [notification-service](../09-microservices/services/10-notification-service/README.md) ([decisiones](../09-microservices/services/10-notification-service/decisions.md)).

Las prácticas aquí descritas se apoyan en la gobernanza ya definida: la [Definition of Done](../00-governance/definition-of-done.md), la [Definition of Ready](../00-governance/definition-of-ready.md), las [convenciones de Git](../00-governance/git-conventions.md) (git flow `develop → qa → staging → main` y Conventional Commits) y la [estrategia de migraciones](../06-data/migration-strategy.md).

## Contenido

Define prácticas de pruebas, revisión de código y criterios de calidad.

## Archivos

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [testing-strategy.md](./testing-strategy.md) | Estrategia de pruebas por nivel y tipo | 🟡 |
| [code-review.md](./code-review.md) | Criterios y flujo para revisiones de código | 🟡 |

## Plantillas

| Plantilla | Descripción |
|-----------|-------------|
| [_template-qa-report.md](./_template-qa-report.md) | Reporte de QA: cobertura, defectos, HUs verificadas y gate de calidad |
| [_template-test-evidence.md](./_template-test-evidence.md) | Evidencia de pruebas: casos TC-NNN, defectos y trazabilidad AC-HU-TC |

## Puntos abiertos

- **No hay CI todavía**: las suites de `iam` (~162 tests) y `notification` (unit + E2E) se ejecutan a mano; hay 3 tests de integración *flaky* en `develop` sin pipeline que los estabilice. Deuda nombrada: HU-NOTIF-009 (docs#78) para CI + gate Pact automatizado; se enlaza con [TD-010](../15-project-control/technical-backlog.md) y [ci-cd.md](../10-devops/ci-cd.md).
- Umbral de cobertura exacto y su gate automatizado en CI: pendiente de cerrar junto con [ci-cd.md](../10-devops/ci-cd.md).
- Selección del set de prueba para los servicios que **aún no** tienen capa de aplicación: se decidirá por stack (Java o Go, según ADR-006) al iniciar su construcción.

- [Plan de mejoramiento R3 de Monitoring](./plan-mejoramiento/README.md).
