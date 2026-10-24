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
  - **Liquibase aplica todos los changesets cuando `update` no recibe `--contexts`.** Cada `include` del changelog maestro lleva `contextFilter: <carpeta>` (`01_ddl`, `02_dml`, `03_dcl`, `04_tcl`) combinado con AND con el context del changeset, por eso un despliegue que filtra debe pasar también esos cuatro contexts. `staging`/`main` deben desplegarse con el filtro explícito (sin `dev`/`qa`).
  - Seeds sintéticos o de prueba vigentes en `iam-db`: `hu-iam-019-seed-synthetic-users-002` (7 usuarios, uno por rol), `hu-ref-018-jwt-fixture-001` (2 usuarios para JWT/RBAC de parámetros).

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
