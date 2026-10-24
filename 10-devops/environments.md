# Ambientes

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: DevOps

Los ambientes del sistema de Gestión de Horarios SENA, cómo se configuran y qué reglas rigen en cada uno. Complementa a [00-governance/git-conventions.md](../00-governance/git-conventions.md), a [local-setup.md](./local-setup.md) y a [06-data/migration-strategy.md](../06-data/migration-strategy.md).

## Los cuatro ambientes

Cada ambiente es también una **rama protegida**: no se trabaja directamente sobre ella, recibe cambios por Pull Request y representa una etapa de madurez creciente.

| Ambiente | Rama | Propósito | Base de datos | Migraciones |
|----------|------|-----------|---------------|-------------|
| **develop** | `develop` | Integración del trabajo en curso | BD de desarrollo | Forward + rollback local permitido |
| **qa** | `qa` | Validación funcional y técnica | BD de QA | **Forward-only** |
| **staging** | `staging` | Preproducción / validación previa al release | BD de preproducción | **Forward-only** |
| **main** | `main` | Producción / documentación estable | BD de producción | **Forward-only** |

Promoción: **`develop → qa → staging → main`**. El detalle del flujo de ramas (ramas `hu-*` por ambiente, `release/*` hacia `main`) está en [git-conventions.md](../00-governance/git-conventions.md).

> **Estado real (difiere por ambiente):**
> - **`develop`** ya corre **capa de aplicación**: perfiles de docker-compose que levantan `iam-api` (Java) y `notification` (api + worker, Go) sobre la BD compartida, con **edge Traefik** (`/iam/*` + StripPrefix, ADR-007) y **stack de observabilidad** (OTel → Tempo/Grafana, ADR-008).
> - **`qa` / `staging` / `main`** materializan **solo la capa de datos** (PostgreSQL 16 en contenedor + migraciones Liquibase por módulo). Los perfiles de aplicación **aún no están promovidos** a estos ambientes — son parte del estado objetivo (ver [05-architecture/deployment.md](../05-architecture/deployment.md)).

---

## Puertos expuestos al host por ambiente (ADR-007)

Cada ambiente aísla sus recursos por puerto para poder coexistir en la misma máquina. En `develop` estos recursos están vivos; en `qa`/`staging`/`main` hoy solo aplica la fila de Postgres (el resto queda reservado para cuando se promuevan los perfiles de aplicación).

| Recurso | develop | qa | staging | main |
|---|---|---|---|---|
| Edge (Traefik) — único entry point | 18080 | 18081 | 18082 | 18083 |
| Traefik dashboard | 18090 | 18091 | 18092 | 18093 |
| Postgres | 15432 | 15433 | 15434 | 15435 |
| RabbitMQ mgmt | 15672 | 15673 | 15674 | 15675 |
| Grafana / Tempo / Prometheus / Loki (ADR-008) | base + offset | +1 | +2 | +3 |
| `iam-api` (y cualquier `-api` de dominio) | **no expuesto** — solo vía edge | | | |

El detalle operativo de bring-up de estos puertos vive en [local-setup.md](./local-setup.md).

Detrás del edge, las rutas por dominio (`/<dominio>/api/` → servicio, `/mfe/<dominio>/` → remote, el resto → shell) están en [ADR-022](../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md).

---

## Configuración por ambiente — `.env.<ambiente>`

La configuración de cada ambiente vive en un archivo de entorno propio:

| Archivo | Ambiente |
|---------|----------|
| `.env.develop` | develop |
| `.env.qa` | qa |
| `.env.staging` | staging |
| `.env.main` | main |

Docker Compose lee `.env` por defecto, por lo que el archivo se pasa **explícitamente** en cada comando:

```bash
docker compose --env-file .env.develop up postgres -d
docker compose --env-file .env.develop --profile tooling run --rm liquibase-<modulo> update
```

Estos archivos parametrizan la conexión a Postgres (host, puerto, nombre de BD, usuario, clave) del ambiente correspondiente y, además, la **configuración de la capa de aplicación** de los perfiles que corren en ese ambiente:

- **Datos:** conexión a Postgres del ambiente.
- **Aplicación (`iam`):** `IAM_DB_USERNAME` / `IAM_DB_PASSWORD` (usuario de aplicación, ver `create-app-user.sh`), `IAM_JWT_PRIVATE_KEY` / `IAM_JWT_ISSUER` (y demás `IAM_JWT_*`).
- **Edge / infra:** `EDGE_PORT` (puerto del Traefik del ambiente), `BACKEND_REPOS_DIR` (carpeta de repos de backend clonados para el build context).

El detalle operativo de los comandos y la tabla completa de variables por servicio están en [local-setup.md](./local-setup.md).

---

## Base de datos por ambiente

- Cada ambiente tiene su **propia base de datos**, con la misma estructura: **una BD, un schema por módulo** (`identity`/`rbac`/`session`, `academic_management`, `training_environment`, `monitoring`, `institutional_structure`, `document`, `audit`, `scheduling`, …). Ningún módulo escribe en `public`.
- El **tracking de Liquibase se aísla por módulo** (`--liquibase-schema-name=<modulo>`), de modo que cada servicio tenga su propia `databasechangelog` y su historial sea auditable y reversible de forma independiente.
- **Datos por ambiente:**
  - `develop` admite **datos de prueba** (seeds con `context`/`labels` de Liquibase).
  - `qa`/`staging`/`main` reciben **solo catálogos de negocio** (semillas reales, idempotentes con `ON CONFLICT DO NOTHING`); los datos de prueba se aíslan para que **no** se promuevan.
- En `qa`/`staging`/`main` las migraciones son **forward-only**; el rollback es plan de contingencia documentado, apoyado en los **tags de release** (`04_tcl/`), no operación rutinaria.

---

## Advertencia de secretos

> **Riesgo real y prioritario.** Los archivos `.env.*` **no deben contener contraseñas reales versionadas en git**. Si una credencial de base de datos queda en el repositorio (o en su historial), cualquiera con acceso al repo obtiene acceso a los datos del ambiente, incluida PII sujeta a la Ley 1581/2012.

Reglas:

- Versionar únicamente un **`.env.example`** con valores ficticios como plantilla; mantener los valores reales **fuera de git**.
- Ante una credencial que haya estado versionada: **rotar primero, avisar después** ([security-rules.md](../00-governance/security-rules.md)), sacar el archivo del control de versiones y evaluar limpieza del historial.
- Estado objetivo: mover los secretos a un **Secret Manager** cuando exista la capa de aplicación.

Detalle en [05-architecture/security-threat-model.md](../05-architecture/security-threat-model.md) §Secretos y nota de secretos en [local-setup.md](./local-setup.md).

## Referencias

- [local-setup.md](./local-setup.md) — comandos por ambiente
- [ci-cd.md](./ci-cd.md) — validación y promoción automatizadas (previsto)
- [00-governance/git-conventions.md](../00-governance/git-conventions.md) — ramas protegidas y flujo de promoción
- [06-data/migration-strategy.md](../06-data/migration-strategy.md) — seeds, contexts, rollbacks, tags
- [05-architecture/deployment.md](../05-architecture/deployment.md) — topología de despliegue por ambiente
