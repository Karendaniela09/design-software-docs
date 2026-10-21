# Estado remoto de HU y PR ? corte 19 de octubre de 2026

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

Se consultaron todos los issues del repositorio docs con paginaci?n y los PR de Monitoring. No se cerraron issues ni se fusionaron PR. La consulta de GitHub Projects v2 fue rechazada por falta de `read:project`; `github-projects.json` conserva el error real. Los estados siguientes son los de Issues/PR, no columnas del tablero.

La HU-MON-008 **frontend** es el issue #225, asignado a yersonct, actualmente cerrado; PR MFE #5 se comprueba en la tabla inferior. El issue #112 usa el mismo c?digo para Reportes en una serie anterior y sigue abierto: no deben confundirse.

Las HU-INT-MON-001..004 (#322?325) siguen abiertas y asignadas a otros colaboradores; sus dependencias con IAM, fuentes de dominio, Notification y Audit no se dan por terminadas mediante este reto.

| Issue | T?tulo | Estado | Responsable(s) |
|---|---|---|---|
| [#325](https://github.com/code-sena/design-software-docs/issues/325) | HU-INT-MON-004 — Conectar alertas con Notification y Audit y validar operación completa | open | joseamaya009 |
| [#324](https://github.com/code-sena/design-software-docs/issues/324) | HU-INT-MON-003 — Integrar fuentes de dominio y cálculo de KPI con alert-worker | open | EmersonMolano |
| [#323](https://github.com/code-sena/design-software-docs/issues/323) | HU-INT-MON-002 — Integrar seguimiento de fichas, sesiones, indicadores y planes en el MFE | open | EmersonMolano |
| [#322](https://github.com/code-sena/design-software-docs/issues/322) |  HU-INT-MON-001 — Conectar BD, IAM, MFE y catálogos de monitoreo | open | EmersonMolano |
| [#272](https://github.com/code-sena/design-software-docs/issues/272) | HU-MON-004: Cerrar operabilidad, seguridad y calidad end-to-end | closed | Andrey31072 |
| [#271](https://github.com/code-sena/design-software-docs/issues/271) | HU-MON-003: Implementar alert-worker, evaluacion de KPIs y outbox | closed | Andrey31072 |
| [#270](https://github.com/code-sena/design-software-docs/issues/270) | HU-MON-002: Completar monitoring-api segun contrato OpenAPI | closed | Andrey31072 |
| [#269](https://github.com/code-sena/design-software-docs/issues/269) | HU-MON-001: Implementar modelo de datos y repositorios de monitoreo | closed | Andrey31072, joseale879 |
| [#225](https://github.com/code-sena/design-software-docs/issues/225) | HU-MON-008:  [FRONTEND] Alertas generadas y planes de mejoramiento (MFE) | closed | yersonct |
| [#223](https://github.com/code-sena/design-software-docs/issues/223) | HU-MON-007:  [FRONTEND]Seguimiento de ficha (MFE) | closed | yersonct |
| [#221](https://github.com/code-sena/design-software-docs/issues/221) | HU-MON-006:  [FRONTEND] Panel de indicadores — KPIs (MFE) | closed | joseamaya009 |
| [#220](https://github.com/code-sena/design-software-docs/issues/220) | HU-MON-005:  [FRONTEND]  Parametrización — catálogos de KPI y alertas (MFE) | closed | joseamaya009 |
| [#115](https://github.com/code-sena/design-software-docs/pull/115) | docs(data): sync data-dictionary with HU-MON-F3 (sent_notification -> notification-service, outbox) | closed | Sin asignar |
| [#114](https://github.com/code-sena/design-software-docs/issues/114) | HU-MON-010: Levantado local E2E (perfil monitoring en docker-infra) | open | Sin asignar |
| [#113](https://github.com/code-sena/design-software-docs/issues/113) | HU-MON-009: Observabilidad OTel + health | open | Sin asignar |
| [#112](https://github.com/code-sena/design-software-docs/issues/112) | HU-MON-008: Reportes (kpi-summary, indicators) | open | Sin asignar |
| [#111](https://github.com/code-sena/design-software-docs/issues/111) | HU-MON-007: Planes de mejora (improvement_plan CRUD) | open | Sin asignar |
| [#110](https://github.com/code-sena/design-software-docs/issues/110) | HU-MON-006: Publicación de eventos (outbox → monitoring-events) | open | Sin asignar |
| [#109](https://github.com/code-sena/design-software-docs/issues/109) | HU-MON-005: Alertas + resolución (generated_alert) | open | Sin asignar |
| [#108](https://github.com/code-sena/design-software-docs/issues/108) | HU-MON-004: KPIs + evaluación de umbrales (alert-worker → generated_alert) | open | Sin asignar |
| [#107](https://github.com/code-sena/design-software-docs/issues/107) | HU-MON-003: Sesiones de seguimiento (tracking_session, append-only) | open | Sin asignar |
| [#106](https://github.com/code-sena/design-software-docs/issues/106) | HU-MON-002: Seguimiento de ficha por eventos (academic.ficha.opened/closed) | open | Sin asignar |
| [#105](https://github.com/code-sena/design-software-docs/issues/105) | HU-MON-001: Catálogos (kpi_type, alert_type CRUD; risk_level, kpi_status RO) | open | Sin asignar |
| [#104](https://github.com/code-sena/design-software-docs/issues/104) | HU-MON-F3: Remediación monitoring-db (drop sent_notification, +outbox, seeds, trigger) | closed | Sin asignar |
| [#103](https://github.com/code-sena/design-software-docs/issues/103) | HU-MON-F2: Limpieza de contrato monitoring.yaml (retirar /sent-notifications — TD-011) | closed | Sin asignar |
| [#102](https://github.com/code-sena/design-software-docs/issues/102) | HU-MON-F1: Golden template Python/FastAPI (consolidar esqueleto hexagonal ADR-006) | open | Sin asignar |

| Repositorio / PR | Rama destino | Estado | Fusi?n comprobada |
|---|---|---|---|
| [design-software-monitoring-mfe #2](https://github.com/code-sena/design-software-monitoring-mfe/pull/2) | develop | closed | 2026-10-11T18:39:38Z |
| [design-software-monitoring-mfe #3](https://github.com/code-sena/design-software-monitoring-mfe/pull/3) | develop | closed | 2026-10-12T17:18:48Z |
| [design-software-monitoring-mfe #4](https://github.com/code-sena/design-software-monitoring-mfe/pull/4) | develop | closed | 2026-10-13T02:59:56Z |
| [design-software-monitoring-mfe #5](https://github.com/code-sena/design-software-monitoring-mfe/pull/5) | develop | closed | 2026-10-13T03:50:16Z |
| [design-software-monitoring-mfe #6](https://github.com/code-sena/design-software-monitoring-mfe/pull/6) | develop | closed | 2026-10-15T01:57:29Z |
| [design-software-monitoring-mfe #7](https://github.com/code-sena/design-software-monitoring-mfe/pull/7) | develop | closed | 2026-10-19T18:38:44Z |
| [design-software-monitoring-service #2](https://github.com/code-sena/design-software-monitoring-service/pull/2) | develop | closed | 2026-10-14T04:57:44Z |
| [design-software-monitoring-service #3](https://github.com/code-sena/design-software-monitoring-service/pull/3) | develop | closed | 2026-10-14T05:28:22Z |
| [design-software-monitoring-service #4](https://github.com/code-sena/design-software-monitoring-service/pull/4) | develop | closed | 2026-10-14T05:55:04Z |
| [design-software-monitoring-service #5](https://github.com/code-sena/design-software-monitoring-service/pull/5) | develop | closed | 2026-10-14T06:20:20Z |

P1-D queda PARCIAL: existen HU/PR anteriores fusionados en develop, pero contin?an HU vigentes de integraci?n abiertas y los PR del reto deben ser revisados y fusionados por el equipo.
