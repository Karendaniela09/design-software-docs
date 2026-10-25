# Estrategia de migraciones (Liquibase)

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Datos

Estándar transversal de cómo se versiona y despliega el esquema de base de datos de cada servicio. Complementa a [modeling-conventions.md](./modeling-conventions.md) (§7 estructura DDL) y a [local-setup.md](../10-devops/local-setup.md).

## Herramienta y unidad de despliegue

- **Liquibase** sobre **PostgreSQL 16**. Cada servicio se despliega desde su repositorio `*-db`.
- Cada repo tiene un **changelog maestro** (`changelog-master.yaml`) que incluye, en orden, los changelogs por carpeta descritos en [modeling-conventions §7](./modeling-conventions.md#7-estructura-ddl-y-orden-de-aplicación-liquibase).
- Cada changeset declara `id` + `author` únicos y define su `rollback` (espejo en `05_rollbacks/`).

## Aislamiento por módulo

- Todos los módulos conviven en **una base de datos**, pero **cada módulo crea y usa su propio schema** (`identity`/`rbac`/`session`, `academic_management`, `training_environment`, `monitoring`, `institutional_structure`, `document`, etc.). Ningún módulo escribe en `public`.
- Se recomienda **aislar el tracking de Liquibase por módulo** (`--liquibase-schema-name=<modulo>`), de modo que cada servicio tenga su propia `databasechangelog` y su historial sea auditable y reversible de forma independiente.

## Orden de aplicación (por qué importa)

1. `00_extensions` → `01_schemas` → `02_types`
2. `03_tables` — **tablas sin llaves foráneas**
3. `04_alter` — **llaves foráneas vía `ALTER TABLE ... ADD CONSTRAINT`, después de crear toda la estructura** (evita rupturas por orden de creación / referencias hacia adelante)
4. `05_views` … `08_triggers` → `10_indexes` (incluye un índice por cada FK)
5. `02_dml` (seeds) → `03_dcl` (roles/grants) → `04_tcl` (tags de versión)

## Datos semilla (seeds)

- Van en `02_dml/` y deben ser **idempotentes**: usar `INSERT ... ON CONFLICT DO NOTHING` (o `MERGE`) para poder re-ejecutarse sin fallar.
- Separar **datos de catálogo** (semilla real de negocio) de **datos de prueba** (que no deben ir a `staging`/`main`); estos últimos se aíslan con `context`/`labels` de Liquibase.
- **Datos sintéticos de prueba** (decisión del dueño, 2026-10-24: `develop` y `qa` se prueban con datos sintéticos; HU-IAM-019):
  - Van en `02_dml/04_patches` con `context: "dev,qa"` y las labels `seed,synthetic,test,<hu>`. Es el context de datos de prueba que ya usan los `-db` (`hu-ref-018-jwt-fixture-001`); no se crean contexts nuevos por HU. El changeset es el mismo en los cuatro ambientes: el ambiente solo decide, al desplegar, si pasa `dev`/`qa` en `--contexts`.
  - Nombres y correos ficticios (`@example.test`), IDs fijos reconocibles, e **ninguna contraseña en el repositorio**: el seed deja un hash inutilizable y la contraseña real se provee al desplegar con un script que la lee de variables de entorno (ver [environments.md](../10-devops/environments.md#datos-sintéticos-develop-y-qa)).
  - **Liquibase aplica todos los changesets cuando `update` no recibe `--contexts`** (y `--contexts=` vacío equivale a no pasarlo). Por eso cada `liquibase-<modulo>` de docker-infra pasa siempre `--contexts=${LIQUIBASE_CONTEXTS:-01_ddl,02_dml,03_dcl,04_tcl}` (HU-SHELL-016): ver [Contexts de Liquibase por ambiente](#contexts-de-liquibase-por-ambiente). Los includes de `01_ddl`…`04_tcl` de `iam-db`, `reference-data-db` y `scheduling-db` (y los de `01_ddl` de `actors-db`) llevan `contextFilter: <carpeta>`, que Liquibase combina con AND con el context del changeset: un despliegue que filtra debe pasar también esos cuatro contexts. Los demás `-db` no usan contexts de carpeta.
  - Seeds sintéticos o de prueba con `context: "dev,qa"` vigentes en `iam-db`: `hu-iam-019-seed-synthetic-users-002` (7 usuarios, uno por rol), `hu-ref-018-jwt-fixture-001` (2 usuarios para JWT/RBAC de parámetros). Los seeds de prueba o demo que **todavía no** lo llevan están en la [auditoría](#auditoría-de-seeds-sin-context-hu-shell-016).

### Contexts de Liquibase por ambiente

El `docker-compose.yml` de docker-infra es **idéntico en los cuatro ambientes** ([ADR-022](../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md) §6). Lo único que cambia es `LIQUIBASE_CONTEXTS` en el `.env.<ambiente>`:

| Ambiente | `LIQUIBASE_CONTEXTS` | ¿Aplica datos de prueba (`dev`/`qa`)? |
|---|---|---|
| develop | `01_ddl,02_dml,03_dcl,04_tcl,dev` | Sí |
| qa | `01_ddl,02_dml,03_dcl,04_tcl,qa` | Sí |
| staging | `01_ddl,02_dml,03_dcl,04_tcl` | No |
| main | `01_ddl,02_dml,03_dcl,04_tcl` | No |

- **El valor por defecto excluye los datos de prueba.** Si `LIQUIBASE_CONTEXTS` no existe o está vacío, el compose usa `01_ddl,02_dml,03_dcl,04_tcl` (el de staging/main) y `.env.example` trae ese mismo valor. Olvidar la variable en develop o qa deja el ambiente sin fixtures; nunca deja a staging o main con ellas.
- Un changeset de datos de prueba lleva `context: "dev,qa"`. No se crean contexts por HU; si algún día hace falta uno nuevo, hay que sumarlo al valor del ambiente que lo aplica y documentarlo en [environments.md](../10-devops/environments.md#contexts-de-liquibase-por-ambiente).
- El `--contexts` del compose no se repite en la línea de comandos: si se escribe después de `update`, gana sobre el del ambiente. `liquibase-monitoring-contract` (perfil `r6-contract`) es el único que suma un context propio, `r6-contract`, porque su único changeset nuevo lo exige.

### Auditoría de seeds sin context (HU-SHELL-016)

Estado de `develop` de los diez `-db` el 2026-10-24. Estos changesets cargan datos de prueba o demo y **no llevan `context`**, así que se aplican también en staging y main. No se editó ningún changeset; cada repo tiene su HU de seguimiento.

Para resolverlos no hace falta tocar el SQL: agregar `context: "dev,qa"` a un changeset ya aplicado **no cambia su checksum** (medido con Liquibase 4.33 sobre `iam-db`: en una base con los 38 changesets aplicados, `validate` no reportó errores y `update` no volvió a ejecutar nada; en una base nueva con el valor de staging/main el changeset queda filtrado). Lo que un ambiente ya cargó no se borra por eso: el context solo cambia las corridas futuras.

| Repo | Changesets sin context con datos de prueba o demo | Seguimiento |
|---|---|---|
| `iam-db` | `seed-demo-iam-001` (`admin@sena.edu.co`, hash ficticio), `hu-iam-017-seed-learner-006` y `hu-iam-017-qa-password-007` (aprendiz de integración; el segundo le fija otro BCrypt válido) | HU-IAM-023 (docs#405) |
| `actors-db` | `hu-act-019-seed-learner-ficha-006` | HU-ACT-030 (docs#406) |
| `reference-data-db` | `seed-demo-reference-001`, `seed-demo-reference-institutional-unit-001` | HU-REF-032 (docs#407) |
| `academic-management-db` | `seed-demo-academic-001` | HU-ACAD-022 (docs#408) |
| `scheduling-db` | `seed-demo-scheduling-001` | HU-SCH-018 (docs#409) |
| `training-environment-db` | `training-017` a `training-021` (datos de prueba de HU-007; el comentario de `02_dml/changelog.yaml` dice que no corren en staging ni main, pero el maestro sí lo incluye) | HU-ENV-021 (docs#411) |

Sin hallazgos: `monitoring-db` (catálogos de negocio), `notification-db` (plantillas) y `audit-db` y `document-db` (no tienen DML). Las demos de `reference-data`, `academic-management`, `scheduling` e `iam` comparten IDs fijos que se referencian entre servicios; deben pasar a `dev,qa` juntas.

## Rollbacks

- Todo changeset forward tiene su rollback espejo en `05_rollbacks/` con la **misma ruta relativa**.
- Rollback de `04_alter` → `DROP CONSTRAINT`; de `03_tables` → `DROP TABLE`; de `02_dml` → `DELETE`/inverso.
- Los rollbacks de datos deben revertir primero los datos y luego el constraint (p. ej. `UPDATE` de valores antes de recrear un `CHECK`).

## Versionado y ambientes

- **Tags de release** en `04_tcl/` al cierre de cada iteración, para poder hacer `rollback <tag>`.
- Promoción por ambientes: `develop → qa → staging → main` (ver [git-conventions.md](../00-governance/git-conventions.md)). Cada ambiente tiene su propio archivo de entorno (`.env.develop/.qa/.staging/.main`).
- **En `qa`/`staging`/`main` las migraciones son forward-only**; los rollbacks se usan en desarrollo local y como plan de contingencia documentado, no como flujo normal en ambientes compartidos.

## Lógica almacenada

- Funciones, vistas y triggers (`05_views`/`06_functions`/`07_procedures`/`08_triggers`) deben marcarse con **`runOnChange: true`** para que Liquibase re-aplique el objeto cuando cambie su definición.
