# CI/CD

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: DevOps

Pipeline de integración y entrega para el sistema de Gestión de Horarios SENA. Describe los controles automatizados sobre los cambios y cómo se promueven entre ambientes. Complementa a [00-governance/git-conventions.md](../00-governance/git-conventions.md), a [environments.md](./environments.md) y a [06-data/migration-strategy.md](../06-data/migration-strategy.md).

> **Honestidad sobre el estado:** la disciplina de ramas, Pull Requests y Conventional Commits **ya se practica** (es la forma de trabajo actual, definida en git-conventions). La **automatización** de esos controles como pipeline está **implementada solo para este repo de docs** (workflow `docs-ci.yml`, HU-SHELL-013; ver [Controles del repo docs](#controles-del-repo-docs)) y todavía **no es obligatoria** para mergear: marcarla en el ruleset lo decide el dueño (D7). Para los repos de código sigue **prevista, no implementada**. Cada control indica su estado.

---

## Alcance

Los controles cubren tres capas que **ya existen**:

1. Validar que la **documentación** siga las convenciones (git-conventions, documentation-rules).
2. Validar que los **changelogs Liquibase** sean correctos y aplicables antes de promover.
3. Construir y probar la **capa de aplicación**: en `develop` ya corren microservicios con suites de pruebas — `iam-service` con **162 tests** (incluidos ITs contra Postgres) y `notification-service` con pruebas **E2E**.

> **El gap no es la falta de tests, es la falta de CI.** La capa de aplicación ya existe y tiene pruebas, pero **ninguna corre automáticamente en un pipeline**: build, tests unitarios/ITs, imágenes de contenedor y el gate de contratos (Pact) se ejecutan hoy **a mano en local**. Automatizarlos es la deuda priorizada de esta página (ver [Pendientes](#pendientes-de-automatización-priorizados)).

---

## Controles del pipeline

| Control | Qué verifica | Estado |
|---------|--------------|--------|
| **Conventional Commits** | Formato `<type>(NN-section): description` en inglés; tipos permitidos (`docs`, `fix`, `chore`, `refactor`) | 🟢 **Implementado para el título del PR** en el repo docs (`docs-ci.yml`; con squash es el commit que llega a `main`). No valida el mensaje de cada commit de la rama; en repos de código, pendiente |
| **Validación de documentación** | Enlaces relativos, unicidad de ADR, datos personales y lint OpenAPI sobre lo que cambia el PR (ver [Controles del repo docs](#controles-del-repo-docs)) | 🟢 **Implementado** en el repo docs (`docs-ci.yml`); falta marcarlo como obligatorio (D7) |
| **Lint de changelogs** | Estructura de cada changelog, `id` + `author` únicos por changeset, presencia de `rollback` espejo | 🟡 Regla definida ([migration-strategy.md](../06-data/migration-strategy.md)); linter pendiente |
| **Validación Liquibase** | `liquibase validate` + `status` contra una BD limpia; que el `changelog-master.yaml` aplique en orden sin error | 🟡 Se ejecuta manual en local ([local-setup.md](./local-setup.md)); en CI pendiente |
| **PR checks** | Revisión obligatoria antes de merge a rama protegida; sin commits directos a `develop`/`qa`/`staging`/`main` | 🟡 Reglas de rama vigentes; enforcement automático pendiente |
| **Seeds idempotentes** | Que los `02_dml` usen `ON CONFLICT DO NOTHING`/`MERGE` y que los datos de prueba estén aislados por `context`/`labels` | 🟡 Regla definida; verificación pendiente |
| **Secret scanning** | Que no se versionen credenciales reales en `.env.*` ni en el diff | 🔴 **Pendiente — riesgo real** (ver [security-threat-model.md](../05-architecture/security-threat-model.md) §Secretos) |
| **Contract testing (Pact)** | Gate de compatibilidad de contratos entre consumidor y proveedor sobre `shared-contracts` (OpenAPI/eventos) | 🟡 Gate definido y ejecutable (skill de contratos); **corre a mano, no en CI** |
| **Build / tests de aplicación** | Compilación y pruebas de los servicios (`iam`: 162 tests incl. ITs Postgres; `notification`: E2E) | 🟡 **Las pruebas existen y pasan en local; no corren en CI** (deuda — sin guardián automático) |
| **`@SpringBootTest` de contexto completo** | Que cada servicio Java arranque el contexto Spring completo en el pipeline (no solo `@WebMvcTest` por controller) | 🔴 Pendiente — **regla obligatoria** (ver nota abajo) |

---

## Controles del repo docs

Workflow [`.github/workflows/docs-ci.yml`](../.github/workflows/docs-ci.yml) (HU-SHELL-013): corre en cada PR hacia `main` del repo `design-software-docs`, sin secretos. Los scripts están en [`scripts/ci/`](../scripts/ci/README.md) y se pueden ejecutar en local. **Cada control mira solo lo que cambia el PR** (diff contra la base), para que la deuda que ya existe en `main` no haga fallar PRs ajenos.

| Control | Qué verifica | Estado |
|---------|--------------|--------|
| **Título del PR** | Conventional Commits con tipos `docs`, `fix`, `chore`, `refactor`; scope opcional y descripción | 🟢 Implementado; no obligatorio aún (D7) |
| **Enlaces relativos** | Cada enlace relativo de los `.md` agregados o modificados apunta a un archivo o carpeta existente (ignora anclas y enlaces externos; los enlaces ya rotos antes del PR solo avisan) | 🟢 Implementado; no obligatorio aún (D7) |
| **Unicidad de ADR** | Un número por ADR en el árbol del PR; un ADR nuevo no reutiliza un número de `main` ni uno que agrega un PR abierto más antiguo (caso ADR-020) | 🟢 Implementado; no obligatorio aún (D7) |
| **Datos personales** | Las líneas agregadas no contienen `CC`/`cédula` seguido de 6 a 10 dígitos; el número se enmascara en el reporte | 🟢 Implementado (heurística por patrón); no obligatorio aún (D7) |
| **Lint OpenAPI** | `redocly lint` de `07-api/contracts/openapi/*.yaml` tocados por el PR con el `redocly.yaml` del repo; falla solo por errores nuevos frente a la base | 🟢 Implementado; no obligatorio aún (D7) |

---

## Flujo previsto por Pull Request

```
Rama hija (hu-NN-dev)  ──PR──▶  develop
        │
        ├─ check: Conventional Commit válido
        ├─ check: liquibase validate + status (BD efímera limpia)
        ├─ check: rollback espejo presente por changeset
        ├─ check: secret scanning (sin credenciales en el diff)
        └─ review humano aprobado
                     │
                     ▼  (todos los checks en verde)
                  merge a develop
```

El mismo conjunto de checks corre en los PRs hacia `qa`, `staging` y `main`, endureciéndose en cada nivel (ver Promoción).

---

## Promoción por ramas/ambientes

La promoción sigue **`develop → qa → staging → main`** ([git-conventions.md](../00-governance/git-conventions.md)):

| PR hacia | Origen | Migraciones | Endurecimiento |
|----------|--------|-------------|----------------|
| `develop` | ramas `hu-*-dev` | forward + rollback local | validación básica |
| `qa` | `hu-*-qa` (merge/cherry-pick desde develop) | **forward-only** | + validación funcional |
| `staging` | `hu-*-staging` (desde qa) | **forward-only** | + validación de preproducción |
| `main` | `release/<iteracion>` (desde staging) | **forward-only** | + tag de release (`04_tcl/`) |

- **Forward-only** en `qa`/`staging`/`main`: el pipeline no revierte migraciones en el flujo normal; el rollback es contingencia documentada.
- Cada release etiqueta una versión (`04_tcl/`) para permitir `rollback <tag>` como plan de contingencia.
- Los **datos de prueba no se promueven**: se aíslan con `context`/`labels` de Liquibase para que no lleguen a `staging`/`main`.

---

## Pendientes de automatización (priorizados)

> **Riesgo ya materializado — no hipotético.** La ausencia de CI de aplicación **ya dejó pasar bugs**: el incidente de *ambiguous mapping* (dos `@RestController` sobre la misma interfaz OpenAPI que rompen el arranque de Spring) solo lo caza un `@SpringBootTest` de contexto completo corriendo en el pipeline — un `@WebMvcTest` de un controller aislado no lo detecta. Además hay **3 ITs flaky en `develop`** sin guardián automático que los vigile. Las pruebas existen; lo que falta es que **corran solas en cada PR**.

| # | Acción | Prioridad |
|---|--------|-----------|
| 1 | Secret scanning en cada PR y sacar `.env.*` del control de versiones | **Crítica** |
| 2 | **Pipeline de aplicación**: build + tests unitarios + ITs de `iam` (162, con Postgres) y E2E de `notification` en cada PR — cerrar el gap que dejó pasar *ambiguous mapping* | **Crítica** |
| 3 | **`@SpringBootTest` de contexto completo obligatorio por servicio Java** como check bloqueante (garantiza que el contexto Spring arranca; guardián directo contra *ambiguous mapping*) | **Crítica** |
| 4 | Gate de contratos (Pact) como check obligatorio en CI, no manual | Alta |
| 5 | Estabilizar y vigilar los **3 ITs flaky** de `develop` (quarantine + fix, no ignore) | Alta |
| 6 | Job de CI que corra `liquibase validate` + `update` + `rollback` contra una BD efímera por PR | Alta |
| 7 | Linter de Conventional Commits como check obligatorio (repo docs: el check del título del PR ya existe, falta hacerlo obligatorio — D7; repos de código: pendiente) | Alta |
| 8 | Enforcement automático de ramas protegidas (no merge sin checks en verde) | Media |

### Regla: `@SpringBootTest` de contexto completo obligatorio por servicio Java

Cada servicio Java debe incluir al menos un **`@SpringBootTest` que levante el contexto Spring completo** (full-boot) y correr en CI como check bloqueante. Es el único tipo de prueba que caza fallos de arranque como el *ambiguous mapping* (mapeos ambiguos, beans duplicados, wiring cross-módulo roto); un `@WebMvcTest` acotado a un controller no los ve. Sin este guardián en el pipeline, un servicio puede mergear "verde" y no arrancar.

## Referencias

- [00-governance/git-conventions.md](../00-governance/git-conventions.md) — ramas, PRs, Conventional Commits
- [00-governance/documentation-rules.md](../00-governance/documentation-rules.md) — reglas de contenido
- [scripts/ci/README.md](../scripts/ci/README.md) — scripts del workflow de CI del repo docs (`docs-ci.yml`)
- [06-data/migration-strategy.md](../06-data/migration-strategy.md) — changelogs, seeds, rollbacks, tags
- [environments.md](./environments.md) — ambientes y `.env`
- [05-architecture/deployment.md](../05-architecture/deployment.md) — topología de despliegue
