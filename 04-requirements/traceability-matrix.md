# Matriz de Trazabilidad

> Estado: 🟡 En progreso | Última actualización: 2026-08-28
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Producto

> Fuente: [functional.md](./functional.md) · [user-stories.md](./user-stories.md) · [02-domain/entities-and-rules.md](../02-domain/entities-and-rules.md)

> **Dos capas de IDs** (ver [`00-governance/agile-conventions.md`](../00-governance/agile-conventions.md)). Las historias `HU-01..HU-23` son los IDs **de planeación** del backlog (capa de producto). La construcción real usa IDs **de ejecución** por microservicio, agrupados en épicas de ejecución `EP-<MICRO>-NN`: **`HU-IAM-001..012`** (épica **EP-IAM-01**, issue docs#79; issues docs#80–#91) y **`HU-NOTIF-001..008`** (épica **EP-NOTIF-01**). La sección [Matriz de ejecución real](#matriz-de-ejecución-real-construido) mapea estos IDs reales a sus RF, servicio y estado. El estado vivo por historia vive en **GitHub Project #3**; este `.md` es la SSOT de la trazabilidad HU↔RF.

## Propósito

Relaciona cada **requisito funcional (RF-*)** con la **historia de usuario (HU-*)** que lo motiva, el **servicio/módulo** dueño, la **regla de negocio (RN-*)** que lo gobierna y la **decisión de arquitectura (ADR)** aplicable. Permite verificar cobertura: que ningún RF quede sin historia ni sin dueño, y que cada decisión de arquitectura respalde requisitos reales.

Leyenda de servicios: `iam`, `reference-data`, `academic-management`, `training-environment`, `scheduling` (**CORE**), `actors`, `document`, `monitoring` (**CORE**), `notification`, `audit`.

---

## Matriz RF ↔ HU ↔ Servicio ↔ RN ↔ ADR

| RF | Historia(s) | Servicio / Módulo | Regla(s) RN | ADR | Épica |
|----|-------------|-------------------|-------------|-----|-------|
| RF-IAM-01 | HU-16 | `iam-service` (M1) | RN-IAM-02 | — | EPC-01 |
| RF-IAM-02 | HU-18 | `iam-service` (M1) | RN-IAM-05 | — | EPC-01 |
| RF-IAM-03 | HU-17 | `iam-service` (M1) | RN-IAM-03 | — | EPC-01 |
| RF-IAM-04 | HU-18 | `iam-service` (M1) | RN-IAM-04 | — | EPC-01 |
| RF-IAM-05 | HU-16 | `iam-service` (M1) | RN-IAM-01 | — | EPC-01 |
| RF-REF-01 | HU-19 | `reference-data-service` (M2) | RN-REF-01, RN-REF-02 | — | EPC-03 |
| RF-REF-02 | HU-19 | `reference-data-service` (M4) | RN-REF-03 | ADR-004 | EPC-03 |
| RF-REF-03 | HU-19 | `reference-data-service` (M4) | RN-REF-04 | — | EPC-03 |
| RF-ACAD-01 | HU-01 | `academic-management-service` (M5) | RN-ACAD-01, RN-ACAD-02 | — | EPC-04 |
| RF-ACAD-02 | HU-01, HU-11 | `academic-management-service` (M6) | RN-ACAD-03, RN-ACAD-06 | — | EPC-04 |
| RF-ACAD-03 | HU-02 | `academic-management-service` (M6) | RN-ACAD-04, RN-ACAD-05 | ADR-004 | EPC-04 |
| RF-ENV-01 | HU-03 | `training-environment-service` (M3) | RN-ENV-01, RN-ENV-04 | — | EPC-05 |
| RF-ENV-02 | HU-03 | `training-environment-service` (M3) | RN-ENV-02 | — | EPC-05 |
| RF-ENV-03 | HU-04 | `training-environment-service` (M3) | RN-ENV-03 | — | EPC-05 |
| RF-ENV-04 | HU-05 | `training-environment-service` (M3) | RN-ENV-01, RN-ENV-03 | ADR-002 | EPC-05 |
| RF-SCH-01 | HU-07 | `scheduling-service` (M8) **CORE** | RN-ACAD-04, RN-SCH-02 | ADR-004 | EPC-07 |
| RF-SCH-02 | HU-08 | `scheduling-service` (M8) **CORE** | RN-SCH-05 | — | EPC-07 |
| RF-SCH-03 | HU-09 | `scheduling-service` (M8) **CORE** | RN-SCH-03, RN-SCH-04 | ADR-001, ADR-002 | EPC-07 |
| RF-SCH-04 | HU-08 | `scheduling-service` (M8) **CORE** | RN-SCH-05, RN-SCH-06 | — | EPC-07 |
| RF-SCH-05 | HU-10 | `scheduling-service` (M8) **CORE** | RN-SCH-01 | ADR-001, ADR-004 | EPC-08 |
| RF-SCH-06 | HU-12, HU-15 | `scheduling-service` (M8) **CORE** | RN-SCH-01, RN-ACT-03 | — | EPC-08 |
| RF-SCH-07 | (soporte de HU-05/06/07) | `scheduling-service` (M8) **CORE** | RN-SCH-03 | ADR-002 | EPC-07 |
| RF-ACT-01 | HU-13 | `actors-service` (M7) | RN-ACT-01, RN-ACT-02 | — | EPC-06 |
| RF-ACT-02 | HU-14 | `actors-service` (M7) | RN-ACT-02 | ADR-002 | EPC-06 |
| RF-ACT-03 | HU-06 | `actors-service` (M7) | RN-ACT-02 | ADR-002 | EPC-06 |
| RF-ACT-04 | HU-11 | `actors-service` (M7) | RN-ACT-03 | — | EPC-06 |
| RF-ACT-05 | (fuera de MVP) | `actors-service` (M7) | RN-ACT-04, RN-ACT-05 | — | EPC-12 |
| RF-DOC-01 | HU-22 | `document-service` | — | ADR-003 | EPC-10 |
| RF-DOC-02 | HU-22 | `document-service` | — | ADR-003 | EPC-10 |
| RF-MON-01 | (disparo por HU-10) | `monitoring-service` (M9) **CORE** | RN-MON-01 | ADR-001 | EPC-09 |
| RF-MON-02 | HU-20 | `monitoring-service` (M9) **CORE** | RN-MON-02, RN-CROSS-01 | — | EPC-09 |
| RF-MON-03 | HU-21 | `monitoring-service` (M9) **CORE** | RN-MON-04, RN-MON-05 | — | EPC-09 |
| RF-MON-04 | HU-21 | `monitoring-service` (M9) **CORE** | RN-MON-03 | — | EPC-09 |
| RF-MON-05 | HU-23 | `monitoring`/`actors` (M9/M7) | RN-MON-06, RN-ACT-06 | — | EPC-11 |
| RF-AUD-01 | (transversal, todas) | `audit-service` | RN-CROSS-01 | ADR-001 | EPC-02 |
| RF-AUD-02 | (transversal) | `audit-service` / broker | RN-CROSS-01 | ADR-001 | EPC-02 |
| RF-AUD-03 | (transversal) | todos | RN-CROSS-01..05 | ADR-004 | EPC-02 |

> Las historias `HU-16/17/18` mapeadas arriba a `RF-IAM-*` son IDs **de planeación**; la implementación real de `iam` se ejecutó con `HU-IAM-001..012` (ver siguiente sección). `HU-16/17/18` quedan como referencia histórica del backlog.

---

## Matriz de ejecución real (construido)

Historias efectivamente construidas y verificadas en el ambiente **`dev`**. Estado por historia en **GitHub Project #3** (aquí se fija la trazabilidad HU real ↔ RF). Ningún servicio de estas épicas está promovido a `qa`/`staging`/`main` todavía.

#### Mapeo épicas de ejecución → producto

| Épica de ejecución | Microservicio | Realiza (producto) |
|--------------------|---------------|--------------------|
| `EP-IAM-01` | `iam-service` | `EPC-01` (Identidad y control de acceso) |
| `EP-NOTIF-01` | `notification-service` | Transversal (capacidad de entrega; sin `EPC-NN` propia — ver [`15-project-control/open-questions.md`](../15-project-control/open-questions.md)) |

### EP-IAM-01 — `iam-service` (épica issue docs#79) · 12/12 Done·Dev

| HU real | RF | Capacidad construida | Servicio | Issue | Estado |
|---------|----|----------------------|----------|-------|--------|
| HU-IAM-001 | RF-IAM-01, RF-IAM-05 | Login + lockout 5/10 + `audit_login` + `GET /auth/me` | `iam-service` | docs#80 | ✅ Done·Dev |
| HU-IAM-002 | RF-IAM-06 | Refresh / logout / listar y revocar sesiones (access 15 m / refresh 7 d) | `iam-service` | docs#81 | ✅ Done·Dev |
| HU-IAM-003 | RF-IAM-02 | Contraseña temporal 72 h + reset | `iam-service` | docs#82 | ✅ Done·Dev |
| HU-IAM-004 | RF-IAM-03 | Catálogo RBAC (módulos / features / roles) | `iam-service` | docs#83 | ✅ Done·Dev |
| HU-IAM-005 | RF-IAM-03 | Gestión de usuarios + asignación de roles (scope / centro) | `iam-service` | docs#84 | ✅ Done·Dev |
| HU-IAM-006 | RF-IAM-03 | Autorización por feature + scope / centro | `iam-service` | docs#85 | ✅ Done·Dev |
| HU-IAM-007 | RF-IAM-07 | Eventos de dominio vía outbox → `iam-events` | `iam-service` | docs#86 | ✅ Done·Dev |
| HU-IAM-008 | RF-IAM-04 | Provisión usuario ↔ actor: emite `iam.user.created` con `actor_type`/`actor_id` (invariante); **saga E3 diferida** a `actors-service` | `iam-service` | docs#87 | ⚠️ Parcial·Dev (lado iam Done) |
| HU-IAM-009 | RF-IAM-08 | Reporte `GET /reports/login-audit` (paginación por cursor) | `iam-service` | docs#88 | ✅ Done·Dev |
| HU-IAM-010 | RF-IAM-09 | JWT claims + JWKS `/.well-known/jwks.json` + rotación (DEC-008) | `iam-service` | docs#89 | ✅ Done·Dev |
| HU-IAM-011 | NFR-OBS-04/06/07 | Observabilidad OTel + health (`/health`, `/ready`) | `iam-service` | docs#90 | ✅ Done·Dev |
| HU-IAM-012 | (E2E integración local) | Servicio levantado localmente y probado E2E | `iam-service` | docs#91 | ✅ Done·Dev |

### EP-NOTIF-01 — `notification-service` (extraído de `monitoring`, ADR-005) · 8/8 Done·Dev

| HU real | RF | Capacidad construida | Servicio | Estado |
|---------|----|----------------------|----------|--------|
| HU-NOTIF-001 | RF-NOTIF-01 | Envío por API asíncrono → `202 Accepted` | `notification-service` | ✅ Done·Dev |
| HU-NOTIF-002 | RF-NOTIF-02 | Entrega dirigida por evento (consumo del broker) | `notification-service` | ✅ Done·Dev |
| HU-NOTIF-003 | RF-NOTIF-03 | Canales `EMAIL` / `IN_APP` | `notification-service` | ✅ Done·Dev |
| HU-NOTIF-004 | RF-NOTIF-04 | Resiliencia: retry + DLQ + idempotencia por `event_id` | `notification-service` | ✅ Done·Dev |
| HU-NOTIF-005 | RF-NOTIF-05 | Plantillas de notificación | `notification-service` | ✅ Done·Dev |
| HU-NOTIF-006 | RF-NOTIF-06 | Consulta `GET` de notificaciones | `notification-service` | ✅ Done·Dev |
| HU-NOTIF-007 | RF-NOTIF-07 | Observabilidad (OTel, `/health`, `/ready`) | `notification-service` | ✅ Done·Dev |
| HU-NOTIF-008 | RF-NOTIF-07 | Publica `notification.notification.sent` al entregar | `notification-service` | ✅ Done·Dev |

### Cobertura inversa (ejecución real): HU real → RF

| Historia real | RF que la implementan | Servicio |
|---------------|-----------------------|----------|
| HU-IAM-001 | RF-IAM-01, RF-IAM-05 | `iam-service` |
| HU-IAM-002 | RF-IAM-06 | `iam-service` |
| HU-IAM-003 | RF-IAM-02 | `iam-service` |
| HU-IAM-004 | RF-IAM-03 | `iam-service` |
| HU-IAM-005 | RF-IAM-03 | `iam-service` |
| HU-IAM-006 | RF-IAM-03 | `iam-service` |
| HU-IAM-007 | RF-IAM-07 | `iam-service` |
| HU-IAM-008 | RF-IAM-04 | `iam-service` |
| HU-IAM-009 | RF-IAM-08 | `iam-service` |
| HU-IAM-010 | RF-IAM-09 | `iam-service` |
| HU-IAM-011 | NFR-OBS-04/06/07 | `iam-service` |
| HU-IAM-012 | (E2E, sin RF único) | `iam-service` |
| HU-NOTIF-001 | RF-NOTIF-01 | `notification-service` |
| HU-NOTIF-002 | RF-NOTIF-02 | `notification-service` |
| HU-NOTIF-003 | RF-NOTIF-03 | `notification-service` |
| HU-NOTIF-004 | RF-NOTIF-04 | `notification-service` |
| HU-NOTIF-005 | RF-NOTIF-05 | `notification-service` |
| HU-NOTIF-006 | RF-NOTIF-06 | `notification-service` |
| HU-NOTIF-007 | RF-NOTIF-07 | `notification-service` |
| HU-NOTIF-008 | RF-NOTIF-07 | `notification-service` |

---

## Cobertura inversa: HU → RF

Verifica que cada historia esté respaldada por al menos un requisito funcional.

| Historia | RF que la implementan | Rol |
|----------|-----------------------|-----|
| HU-01 | RF-ACAD-01, RF-ACAD-02 | Coordinador |
| HU-02 | RF-ACAD-03 | Coordinador |
| HU-03 | RF-ENV-01, RF-ENV-02 | Admin |
| HU-04 | RF-ENV-03 | Admin |
| HU-05 | RF-ENV-04 | Coordinador |
| HU-06 | RF-ACT-03 | Coordinador |
| HU-07 | RF-SCH-01 | Coordinador |
| HU-08 | RF-SCH-02, RF-SCH-04 | Coordinador |
| HU-09 | RF-SCH-03 | Coordinador |
| HU-10 | RF-SCH-05 | Coordinador |
| HU-11 | RF-ACT-04, RF-ACAD-02 | Coordinador |
| HU-12 | RF-SCH-06 | Aprendiz |
| HU-13 | RF-ACT-01 | Coordinador |
| HU-14 | RF-ACT-02 | Instructor |
| HU-15 | RF-SCH-06 | Instructor |
| HU-16 | RF-IAM-01, RF-IAM-05 | Todos |
| HU-17 | RF-IAM-03 | Admin |
| HU-18 | RF-IAM-02, RF-IAM-04 | Admin |
| HU-19 | RF-REF-01, RF-REF-02, RF-REF-03 | Admin |
| HU-20 | RF-MON-02 | Coordinador |
| HU-21 | RF-MON-03, RF-MON-04 | Coordinador |
| HU-22 | RF-DOC-01, RF-DOC-02 | Coordinador |
| HU-23 | RF-MON-05 | Coordinador |

---

## Trazabilidad de decisiones de arquitectura (ADR → RF)

| ADR | Decisión | RF que soporta |
|-----|----------|----------------|
| [ADR-001](../05-architecture/decisions/records/ADR-001-message-broker.md) | Broker RabbitMQ (eventos, DLQ) | RF-SCH-03/05, RF-MON-01, RF-AUD-01/02 |
| [ADR-002](../05-architecture/decisions/records/ADR-002-scheduling-read-models.md) | Read models locales en scheduling | RF-SCH-07, RF-SCH-03, RF-ENV-04, RF-ACT-02/03 |
| [ADR-003](../05-architecture/decisions/records/ADR-003-object-storage.md) | Object storage compatible S3 | RF-DOC-01, RF-DOC-02 |
| [ADR-004](../05-architecture/decisions/records/ADR-004-status-parametrization-and-audit-standard.md) | Estados parametrizables + auditoría | RF-ACAD-03, RF-SCH-01/05, RF-REF-02, RF-AUD-03 |

---

## Cobertura de criterios de éxito del MVP

Enlaza los criterios funcionales (CF-*) de [problem-framing.md](../03-product/problem-framing.md) con los RF que los cumplen.

| Criterio | Descripción | RF |
|----------|-------------|----|
| CF-01 | Crear borrador de horario para ficha activa | RF-SCH-01 |
| CF-02 | Detectar conflictos antes de publicar | RF-SCH-03 |
| CF-03 | Publicar horario sin conflictos con una acción | RF-SCH-05 |
| CF-04 | Instructor consulta su horario por semana | RF-SCH-06 |
| CF-05 | Aprendiz consulta el horario de su ficha | RF-SCH-06 |
| CF-06 | Horario publicado inmutable; cambios crean versión | RF-SCH-05 |

---

## Notas de cobertura y puntos abiertos

- **RF-ACT-05** (etapa productiva) y **EPC-12** están fuera del MVP; se listan para completitud pero no tienen historia priorizada en el alcance actual.
- **RF-MON-01** y **RF-AUD-01/02/03** son requisitos disparados por eventos o transversales; su "historia" es indirecta (se activan desde HU-10 o aplican a todas las operaciones).
- Los puntos abiertos PA-01…PA-04 (ver [vision.md](../03-product/vision.md)) pueden modificar la relación RF ↔ HU si cambian los supuestos (p. ej. integración SOFIA Plus, multi-ficha por aprendiz).

## Referencias

- [functional.md](./functional.md) · [user-stories.md](./user-stories.md) · [non-functional.md](./non-functional.md)
- [02-domain/entities-and-rules.md](../02-domain/entities-and-rules.md)
- [03-product/product-backlog.md](../03-product/product-backlog.md) · [03-product/problem-framing.md](../03-product/problem-framing.md)
- ADRs: [001](../05-architecture/decisions/records/ADR-001-message-broker.md) · [002](../05-architecture/decisions/records/ADR-002-scheduling-read-models.md) · [003](../05-architecture/decisions/records/ADR-003-object-storage.md) · [004](../05-architecture/decisions/records/ADR-004-status-parametrization-and-audit-standard.md)

## Trazabilidad HU-REF-020 y reto individual R1

| Entrega | Requisitos | Servicio / repositorios | Tracker | Decisión | Gate actual |
|---|---|---|---|---|---|
| HU-REF-020, EP-REF | RF-IAM-01, RF-REF-02/03; autenticación/autorización real | reference-data-service, iam-db, reference-data-mfe, web-shell, frontend-platform, docker-infra | [docs#250](https://github.com/code-sena/design-software-docs/issues/250) | [ADR-020](../05-architecture/decisions/records/ADR-020-reference-data-iam-e2e-integration.md) | En progreso; PASS local y CI del shell en SHA probado; CI propio MFE, revisión de Arquitectura y merges pendientes |
| R1 Reference Data | NFR-REC-03; outbox/deduplicación/retry/DLQ/caos | reference-data-service, reference-data-db, docker-infra | Reto del plan individual, relacionado con docs#250; no se inventa una HU nueva | [ADR-021](../05-architecture/decisions/records/ADR-021-reference-data-resilient-messaging.md) | En progreso; PASS local y CI del shell en SHA probado; CI propio MFE, revisión de Arquitectura y merges pendientes |

La trazabilidad se completa con [casos y evidencia](../11-quality/reference-data-hu-ref-020-r1-validation.md). Los resultados en repositorios personales no acreditan Done·Dev en code-sena. El board Project #3 sigue siendo la fuente del estado vivo.
