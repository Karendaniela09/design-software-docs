<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: hallazgos de descubrimiento (mockup-first) para feedback
fase: diseño (UX/UI) — preliminar
estado: draft
dependencias_entrada: mockup-ddd/flows/*.md; contratos openapi; data-model; functional.md; rbac-design.md
consumidores_siguientes: refinamiento de contratos/HU/RBAC; construcción posterior de backend/frontend
tldr: Vacíos concretos (contrato ↔ requisito ↔ RBAC) que emergieron al derivar las pantallas de los contratos reales. NO se inventaron campos; se documentaron los gaps.
decisiones_clave: mockup-first como instrumento de precisión; nada se corrige aún, es feedback
halts_registrados: audit-service sin API REST (bloquea pantalla de auditoría)
-->

# Hallazgos de descubrimiento (mockup-first) — feedback

Al derivar las 22 pantallas **de los contratos y el data-model reales** (no de supuestos),
emergieron vacíos entre lo que la UI necesita y lo que hoy existe. **No se inventó nada**;
aquí quedan como feedback para refinar contratos / HU / RBAC **más adelante** (no ahora).

> **Actualización (refinamiento con retros de aprendices).** El triage de las 22 retrospectivas contra
> el estado real de los repos, más su materialización en el mockup y el spec de cambio de modelo aditivo,
> viven ahora en **[refinamiento-alignment.md](refinamiento-alignment.md)**. Estado de los bloqueantes de
> abajo: **B2 y B3 RESUELTOS en contrato** — el rbac de BD ya tenía `SCH_VIEW_OWN` (LEARNER→OWN_FICHA_AS_LEARNER,
> INSTRUCTOR→OWN_SCHEDULE) y `MON_DASHBOARD_OWN` (INSTRUCTOR→OWN_FICHAS); el hueco real estaba en el OpenAPI, que
> exigía solo `SCH_VIEW_ALL`/`MON_DASHBOARD_FULL`. Se corrigió con `x-required-feature-any` en
> `07-api/contracts/openapi/{scheduling,monitoring}.yaml` (5 GET de horarios/sesiones + `/ficha-trackings`).
> **B1 RESUELTO**: se agregó el API de solo lectura de auditoría — contrato
> [contrato OpenAPI canónico de audit-service](https://github.com/code-sena/design-software-audit-service/blob/develop/api/openapi/audit.yaml) + componente
> `audit-query-api` (GET `/audit-records` cursor+filtros, `/{id}`, `/export`; features `AUDIT_LOG_VIEW`/`AUDIT_EXPORT`
> que ya existían en rbac). La pantalla de auditoría ya es construible. **Sin bloqueantes abiertos.**

## 🔴 Bloqueantes (para cuando se construya)

| # | Flujo | Hallazgo | Impacto |
|---|---|---|---|
| B1 | back-office (Auditoría) | **RESUELTO:** `audit-query-api` expone `GET /audit-records`, detalle y exportación; el contrato canónico vive en `design-software-audit-service/api/openapi/audit.yaml` y aplica `AUDIT_LOG_VIEW`/`AUDIT_EXPORT`. | La pantalla de auditoría es construible y verificable. |
| B2 | Aprendiz | Feature **`SCH_VIEW_OWN`** (scope `OWN_FICHA_AS_LEARNER`) **no está declarado en ningún endpoint** de `scheduling.yaml` — todos los `GET` exigen `SCH_VIEW_ALL` | El aprendiz no podría ver solo su horario |
| B3 | Instructor | `GET /ficha-trackings` exige `MON_DASHBOARD_FULL`; no hay feature "mis fichas" acotado al instructor | Selector de ficha en "Seguimiento" quedaría bloqueado |

## 🟠 Gaps de contrato/reporte (faltan endpoints/campos que la UI espera)

| # | Flujo | Hallazgo |
|---|---|---|
| G1 | Coordinador / Admin | `monitoring` **no tiene** reportes de "utilización de ambientes" ni "carga de instructores" (los menciona `navigation-map.md`) |
| G2 | Coordinador | **No existe `GET /instructors/available`** (RF-ACT-03/HU-06 lo mencionan) → se compone con `GET /instructors` + `/{id}/availability-exceptions` |
| G3 | Admin | `iam.yaml` **no expone `GET`** de los roles asignados a un usuario (solo `POST`/`DELETE`) |
| G4 | Instructor | "Mi disponibilidad" solo cubre **excepciones/bloqueos** (`InstructorAvailabilityException`); no hay endpoint para **franjas positivas recurrentes** (HU-14 lo sugiere) |
| G5 | Coordinador | `GET /schedules` no filtra por `instructor_id`/`environment_id` (viven en `class_session`, no en `schedule`) |
| G6 | Aprendiz | `sent_notification` **no tiene estado leído/no-leído** (solo `send_status` de entrega del sistema) |
| G7 | back-office | Descarga de documento **solo versión vigente** (no por `version_id`) |

## 🟡 Divergencias requisito ↔ contrato (a reconciliar)

| # | Hallazgo |
|---|---|
| D1 | `scheduling_conflict.conflict_type` real tiene **3 valores** (`INSTRUCTOR_DOUBLE_BOOKED`, `ENVIRONMENT_DOUBLE_BOOKED`, `SESSIONS_OVERLAP`); `functional.md`/HU-09 mencionan **5** (faltan `ENVIRONMENT_MAINTENANCE`, `INSTRUCTOR_UNAVAILABLE`) |
| D2 | RBAC: el **Director/Admin de centro no edita** catálogos ni parámetros (solo `ADMIN_STAFF`/`SYSTEM_ADMIN`); la UI lo refleja como solo-lectura con candado |

## 🔵 Resoluciones cross-servicio (BFF / read models)

Varias pantallas necesitan **nombres** que viven en otro servicio (sin FK física, por diseño):
- `Session` trae `competency_id`/`instructor_id`/`environment_id` → los **nombres** (`Competency.name`,
  `Instructor.full_name`, `Environment.name`) se resuelven en academic-management / actors /
  training-environment (patrón **BFF / read model local**, RF-SCH-07).
- El mapeo `iam.user_id → actors.instructor.id` no lo expone `GET /auth/me` directamente.

## Cómo se usa este feedback
- **No se corrige ahora.** Es insumo para: (1) completar contratos faltantes (audit REST, reportes de
  monitoring, `GET` de roles), (2) reconciliar RBAC (features `OWN` para aprendiz/instructor),
  (3) afinar HU cuando se escriban, (4) definir la capa **BFF/read-model** al construir el frontend.
- Cada hallazgo está también anotado dentro del flujo correspondiente en `flows/*.md`.
