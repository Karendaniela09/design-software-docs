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
| [qa-report-r4-security-scheduling.md](./qa-report-r4-security-scheduling.md) | Informe de auditoría de seguridad y verificación OWASP ASVS L1 para scheduling-service | 🟢 |
| [qa-report-r4-security-actors.md](./qa-report-r4-security-actors.md) | Technical report and QA verification OWASP ASVS L1 for actors-service R4 | 🟢 |
| [qa-report-r4-security-iam.md](./qa-report-r4-security-iam.md) | Technical report and QA evidence for IAM R4 session revocation | 🟢 |
| [qa-report-r1-document-service.md](./qa-report-r1-document-service.md) | Informe técnico y evidencias QA del Document Service | 🟡 |
| [qa-report-r3-monitoring-service.md](./qa-report-r3-monitoring-service.md) | Informe técnico y evidencias QA de Monitoring Service R3 | 🟡 |
| [test-evidence-hu-act-012.md](./test-evidence-hu-act-012.md) | Test evidence and technical validation for the Active Learners by Ficha view (HU-ACT-026) | 🟡 |
| [qa-report-r5-audit.md](./qa-report-r5-audit.md) | Informe técnico y evidencias QA de Auditoría R5 | 🟡 |
| [qa-report-r2-audit-service.md](./qa-report-r2-audit-service.md) | Technical report and QA acceptance evidence for Audit R2 performance and data | 🟢 |
| [qa-report-r2-monitoring-service.md](./qa-report-r2-monitoring-service.md) | Informe técnico y evidencias de rendimiento y datos (R2) de Monitoring Service | 🟡 |
| [qa-report-r2-scheduling-service.md](./qa-report-r2-scheduling-service.md) | Informe técnico y evidencias de rendimiento y datos (R2) de Scheduling: k6, ranking SQL, planes a dos escalas y rollback | 🟡 |
| [qa-report-r6-monitoring-db.md](./qa-report-r6-monitoring-db.md) | Informe técnico y evidencias QA de la migración R6 de Monitoring DB | 🟡 |
| [academic-r1-validation-report.md](./academic-r1-validation-report.md) | Validación integrada de Academic Management y R1 | 🟡 |

## Plantillas

| Plantilla | Descripción |
|-----------|-------------|
| [_template-qa-report.md](./_template-qa-report.md) | Reporte de QA: cobertura, defectos, HUs verificadas y gate de calidad |
| [_template-test-evidence.md](./_template-test-evidence.md) | Evidencia de pruebas: casos TC-NNN, defectos y trazabilidad AC-HU-TC |

## Puntos abiertos

- **No hay CI todavía**: las suites de `iam` (~162 tests) y `notification` (unit + E2E) se ejecutan a mano; hay 3 tests de integración *flaky* en `develop` sin pipeline que los estabilice. Deuda nombrada: HU-NOTIF-009 (docs#78) para CI + gate Pact automatizado; se enlaza con [TD-010](../15-project-control/technical-backlog.md) y [ci-cd.md](../10-devops/ci-cd.md).
- Umbral de cobertura exacto y su gate automatizado en CI: pendiente de cerrar junto con [ci-cd.md](../10-devops/ci-cd.md).
- Selección del set de prueba para los servicios que **aún no** tienen capa de aplicación: se decidirá por stack (Java o Go, según ADR-006) al iniciar su construcción.

- [QA R6 Training Environment DB](./qa-report-r6-training-environment-db.md).

## Validación Reference Data

- [reference-data-hu-ref-020-r1-validation.md](./reference-data-hu-ref-020-r1-validation.md): revalidación al 2026-10-24. Frontend Platform y Web Shell tienen CI aprobado sobre los SHA documentados; MFE mantiene CI propio pendiente por SHELL_DEPS_TOKEN. Los ADR-020/021 siguen PROPOSED y los PR originales requieren revisión/merge.
