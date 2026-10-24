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
  - `develop` y `qa` admiten **datos sintéticos de prueba** (seeds con `context` `dev`/`qa` y `labels` de Liquibase; decisión del dueño del 2026-10-24, HU-IAM-019). Nunca datos personales reales. Ver [Datos sintéticos (develop y qa)](#datos-sintéticos-develop-y-qa).
  - `staging`/`main` reciben **solo catálogos de negocio** (semillas reales, idempotentes con `ON CONFLICT DO NOTHING`); los datos sintéticos y de prueba se aíslan para que **no** se promuevan.
- En `qa`/`staging`/`main` las migraciones son **forward-only**; el rollback es plan de contingencia documentado, apoyado en los **tags de release** (`04_tcl/`), no operación rutinaria.

---

## Datos sintéticos (develop y qa)

> Decisión del dueño (2026-10-24): `develop` y `qa` se prueban con **datos sintéticos**. El código es el mismo en los cuatro ambientes ([ADR-022](../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md) §6): lo único que cambia entre ambientes son los datos y los valores que se inyectan al desplegar. Antes de HU-IAM-019 no había ningún usuario con el que se pudiera iniciar sesión: el hash de `admin@sena.edu.co` es ficticio.

### Qué existe hoy: usuarios sintéticos de IAM (HU-IAM-019)

Un usuario por cada rol del catálogo RBAC (`rbac.role`, 7 roles). Los siete tienen `first_name = Synthetic`, correo en el dominio reservado `@example.test` (nunca resuelve a un buzón real) e ID fijo reconocible `5e000000-0000-4000-8000-0000000000NN`:

| NN | Rol | Correo | `actor_type` |
|---|---|---|---|
| 01 | `SYSTEM_ADMIN` | `synthetic.system-admin@example.test` | `USER` |
| 02 | `CENTER_DIRECTOR` | `synthetic.center-director@example.test` | `USER` |
| 03 | `COORDINATOR` | `synthetic.coordinator@example.test` | `USER` |
| 04 | `AREA_LEADER` | `synthetic.area-leader@example.test` | `USER` |
| 05 | `INSTRUCTOR` | `synthetic.instructor@example.test` | `INSTRUCTOR` |
| 06 | `LEARNER` | `synthetic.learner@example.test` | `LEARNER` |
| 07 | `ADMIN_STAFF` | `synthetic.admin-staff@example.test` | `USER` |

- **Ninguna contraseña vive en el repositorio.** El seed deja `password_hash = '!unprovisioned-synthetic-user'`, que no es un BCrypt: `BCryptPasswordEncoder.matches()` da siempre `false`, así que nadie puede entrar con él. Las contraseñas reales se generan al desplegar y se ponen con el script de provisión (abajo). `must_change_password` queda en `false`: son cuentas de prueba, no personas, y forzar el cambio solo añadiría un paso a cada login automatizado.
- Cada usuario se asigna a sí mismo su rol (`assigned_by = id`, igual que los demás fixtures) y sin `training_center_id`, como el resto de los seeds de IAM.
- Los fixtures anteriores (`hu-ref-018-*@example.test`, `hu-iam-017-learner@example.test`) siguen existiendo y no se tocan; los sintéticos son el juego oficial para QA. (`hu-ref-018-*` ya usa el context `dev,qa`; `hu-iam-017-learner` no lleva context: ver la deuda previa más abajo.)
- **Un rol nuevo en el catálogo exige su usuario sintético**: un changeset nuevo (nunca editar el aplicado, su checksum ya está registrado) y su variable `SYNTHETIC_PASSWORD_<ROL>` en el script de provisión.
- Otros dominios no tienen aún datos sintéticos propios; cuando los tengan seguirán esta misma regla (context + sin secretos en el repo).

### Cómo se selecciona: context de Liquibase

El seed es el changeset `hu-iam-019-seed-synthetic-users-002` (`iam-db`, `02_dml/04_patches`, rollback espejo en `05_rollbacks/02_dml/04_patches`). Usa **el mismo `context: "dev,qa"` que las otras fixtures de prueba** de IAM (`hu-ref-018-jwt-fixture-001`) — no se creó un context nuevo — y la label `synthetic` para poder localizarlo.

Cada `include` del changelog maestro lleva además `contextFilter: <carpeta>` (`01_ddl`, `02_dml`, `03_dcl`, `04_tcl`), que Liquibase combina con **AND** con el context del changeset. Por eso quien pasa `--contexts` debe pasar también los cuatro contexts de carpeta:

| Ambiente | Argumento de `update` | ¿Aplica los usuarios sintéticos? |
|---|---|---|
| develop | `--contexts=01_ddl,02_dml,03_dcl,04_tcl,dev` | Sí |
| qa | `--contexts=01_ddl,02_dml,03_dcl,04_tcl,qa` | Sí |
| staging, main | `--contexts=01_ddl,02_dml,03_dcl,04_tcl` | **No** |

```bash
# develop (el argumento va al final: el compose ya fija el resto del comando)
docker compose --env-file .env.develop --profile tooling run --rm liquibase-iam update \
  --contexts=01_ddl,02_dml,03_dcl,04_tcl,dev
```

> **Riesgo conocido — sin `--contexts`, Liquibase aplica todo.** Si el `update` no recibe `--contexts`, corren **todos** los changesets sin importar su context, incluidos los de `dev,qa`. Hoy el `docker-compose.yml` de docker-infra no fija `--contexts`, así que un `update` simple en `staging`/`main` **sí** cargaría las fixtures de prueba. La garantía "nunca en staging ni main" depende de que esos despliegues pasen el filtro explícito de la tabla anterior (un valor inyectado por ambiente, no código distinto). Tras desplegar `staging`/`main`, comprobar que no hay usuarios sintéticos: `SELECT count(*) FROM identity."user" WHERE email LIKE 'synthetic.%@example.test';` debe dar `0`. Fijar el filtro por ambiente en docker-infra queda como deuda aparte.
>
> **Deuda previa, fuera de HU-IAM-019:** el changeset `hu-iam-017-seed-learner-006` (`hu-iam-017-learner@example.test`, con hash BCrypt) no lleva `context`, así que llega a **todos** los ambientes aunque se filtre; hay que decidir si se le asigna `dev,qa` o se retira.

### Provisión de contraseñas (en cada despliegue de develop y qa)

Script: `design-software-iam-db/scripts/provision-synthetic-passwords.sql` (psql 15 o superior por `\getenv`; la imagen `postgres:16` lo cumple). Lee las contraseñas de variables de entorno, las convierte a BCrypt dentro de la base con `crypt()` / `gen_salt('bf', 10)` (el mismo coste que el codificador del servicio) y verifica cada hash antes de confirmar. Mismo patrón que `test/hu-ref-020/prepare.sql`.

1. Aplicar las migraciones de `iam-db` con los contexts de la tabla anterior.
2. Generar, **en el momento del despliegue**, siete contraseñas aleatorias de entre 12 y 72 bytes y exportarlas como variables del proceso. Nunca en un archivo versionado, ni en un `.env` que viva en git:

   | Variable | Usuario |
   |---|---|
   | `SYNTHETIC_PASSWORD_SYSTEM_ADMIN` | `synthetic.system-admin@example.test` |
   | `SYNTHETIC_PASSWORD_CENTER_DIRECTOR` | `synthetic.center-director@example.test` |
   | `SYNTHETIC_PASSWORD_COORDINATOR` | `synthetic.coordinator@example.test` |
   | `SYNTHETIC_PASSWORD_AREA_LEADER` | `synthetic.area-leader@example.test` |
   | `SYNTHETIC_PASSWORD_INSTRUCTOR` | `synthetic.instructor@example.test` |
   | `SYNTHETIC_PASSWORD_LEARNER` | `synthetic.learner@example.test` |
   | `SYNTHETIC_PASSWORD_ADMIN_STAFF` | `synthetic.admin-staff@example.test` |

3. Ejecutar el script contra la base IAM del ambiente. Con el contenedor `postgres` del compose, pasando las variables **por nombre** (sin escribir el valor en la línea de comandos):

   ```bash
   for v in SYSTEM_ADMIN CENTER_DIRECTOR COORDINATOR AREA_LEADER INSTRUCTOR LEARNER ADMIN_STAFF; do
     export "SYNTHETIC_PASSWORD_$v=$(openssl rand -base64 24)"
   done
   docker compose --env-file .env.develop exec -T \
     -e SYNTHETIC_PASSWORD_SYSTEM_ADMIN -e SYNTHETIC_PASSWORD_CENTER_DIRECTOR -e SYNTHETIC_PASSWORD_COORDINATOR \
     -e SYNTHETIC_PASSWORD_AREA_LEADER -e SYNTHETIC_PASSWORD_INSTRUCTOR -e SYNTHETIC_PASSWORD_LEARNER \
     -e SYNTHETIC_PASSWORD_ADMIN_STAFF postgres \
     sh -c 'psql -X -q -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
     < ../design-software-iam-db/scripts/provision-synthetic-passwords.sql
   echo "exit=$?"   # 0 = los siete usuarios quedaron con su hash verificado
   ```

4. Entregar las contraseñas a quienes prueban por un **canal seguro** (gestor de secretos o mensaje cifrado). No por issue, PR, chat abierto ni log de CI. Para rotarlas, repetir los pasos 2 y 3: el script es repetible, cambia los hashes y limpia bloqueos por intentos fallidos.
5. Cerrar la sesión de shell (o `unset` de las variables) al terminar.

**Garantías del script.** Corre en una sola transacción con `ON_ERROR_STOP`: cualquier guardia fallida termina con **código de salida 3** (nunca 0) y deja la base intacta. En psql 16 `\quit 1` no sirve para esto: ignora el argumento y sale con 0 ([iam-db#80](https://github.com/code-sena/design-software-iam-db/pull/80)).

| Guardia | Falla cuando |
|---|---|
| Base esperada | La base no tiene el schema IAM (`identity`, `rbac`) o `pgcrypto`. |
| Usuarios presentes | Falta alguno de los siete usuarios con su ID, correo y rol: la base no recibió los contexts `dev`/`qa` (por ejemplo, `staging` o `main`). |
| Variables | Falta alguna `SYNTHETIC_PASSWORD_*` (el mensaje nombra cuáles, nunca imprime valores). |
| Longitud | Alguna contraseña mide menos de 12 o más de 72 bytes (BCrypt ignora lo que pasa de 72). |
| Verificación | Tras actualizar, algún hash no es `$2a$10$…` o no verifica contra su contraseña. |

Solo toca filas que coinciden a la vez en ID fijo, correo y dominio `@example.test`: no puede modificar una cuenta real.

> **Aviso.** `pgcrypto` necesita la contraseña en claro en el servidor, así que el texto de la sentencia la contiene. Ejecutar el script por socket local o TLS y mantener `log_statement` en su valor por defecto (`none`) en el servidor de destino.

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
