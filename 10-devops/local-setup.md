# Setup local

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: DevOps

Cómo levantar la base de datos del proyecto y aplicar las migraciones de cada módulo en local, y cómo levantar los servicios de dominio detrás del edge. Complementa a [migration-strategy.md](../06-data/migration-strategy.md). Las rutas del edge están decididas en [ADR-022](../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md).

## Prerrequisitos

- Docker + Docker Compose.
- Repos `*-db` clonados junto a la carpeta de infraestructura (ver estructura del monorepo).

## Arquitectura local

Una **única base de datos PostgreSQL 16** en contenedor, y un servicio Liquibase por módulo (perfil `tooling`) que aplica el `changelog-master.yaml` del repo correspondiente. La configuración por ambiente vive en archivos de entorno: `.env.develop`, `.env.qa`, `.env.staging`, `.env.main`.

> **Nota de secretos:** los archivos `.env.*` **no deben contener contraseñas reales versionadas**. Usar `.env.example` como plantilla y mantener los valores reales fuera de git (ver [security-rules.md](../00-governance/security-rules.md)).

## Pasos

1. **Seleccionar ambiente y levantar Postgres.** Docker Compose lee `.env` por defecto, así que hay que pasar el archivo explícitamente:

   ```bash
   docker compose --env-file .env.develop up postgres -d
   ```

2. **Aplicar los changelogs de un módulo** (perfil `tooling`):

   ```bash
   docker compose --env-file .env.develop --profile tooling run --rm liquibase-<modulo> update
   ```

   Módulos disponibles: `liquibase-academic`, `liquibase-actors`, `liquibase-audit`, `liquibase-document`, `liquibase-iam`, `liquibase-monitoring`, `liquibase-notification`, `liquibase-reference`, `liquibase-scheduling`, `liquibase-training`.

   **Qué datos se aplican lo decide `LIQUIBASE_CONTEXTS`** del `.env.<ambiente>` (el compose ya lo pasa como `--contexts`; no se escribe en el comando). Para develop: `LIQUIBASE_CONTEXTS=01_ddl,02_dml,03_dcl,04_tcl,dev`. Si la variable falta o está vacía rige `01_ddl,02_dml,03_dcl,04_tcl`, que **no** incluye los datos de prueba (`dev`/`qa`). Valores de los cuatro ambientes y reglas en [environments.md](./environments.md#contexts-de-liquibase-por-ambiente).

3. **Verificar** el estado de las migraciones de un módulo:

   ```bash
   docker compose --env-file .env.develop --profile tooling run --rm liquibase-<modulo> status --verbose
   ```

## Rollback local

```bash
docker compose --env-file .env.develop --profile tooling run --rm liquibase-<modulo> rollbackCount 1
```

Para volver a un release etiquetado: `rollback <tag>` (los tags se definen en `04_tcl/`; ver [migration-strategy.md](../06-data/migration-strategy.md)).

## Apagar y limpiar

```bash
docker compose --env-file .env.develop down          # detiene los contenedores
docker compose --env-file .env.develop down -v       # además borra el volumen de datos (reinicio limpio)
```

## Orden recomendado de aplicación

Aplicar primero `reference-data` (catálogos e institucional) e `iam` (identidad), y luego el resto de módulos que los referencian.

---

## Perfiles de aplicación (servicios de dominio)

Además de `tooling` (migraciones), el compose tiene un perfil por servicio de dominio ya desplegado. Un
servicio puede pertenecer a más de un perfil en la lista `profiles:` — así, `traefik` y `rabbitmq` se traen
solos al levantar el perfil del dominio que los necesita, sin tener que enumerar `--profile broker` a
mano. El frontend (shell y remotes) no va en esos perfiles: se pide con `--profile edge`.

| Perfil | Qué levanta | Build context (portable) |
|--------|-------------|---------------------------|
| `notification` | `notification-api` + `notification-worker` + `rabbitmq`/`mailhog` + `traefik` (edge) | `${BACKEND_REPOS_DIR:-../../backend}/design-software-notification-service` |
| `iam` | `iam-api` + `actors-api` + `rabbitmq` (eventos `iam-events`) + `traefik` (edge) | `${BACKEND_REPOS_DIR:-../../backend}/design-software-iam-service` |
| `actors` | `actors-api` + `rabbitmq` + `traefik` (edge) | `${BACKEND_REPOS_DIR:-../../backend}/design-software-actors-service` |
| `scheduling` | `scheduling-api` + `iam-api` (JWKS) + `rabbitmq` + `traefik` (edge) | `${BACKEND_REPOS_DIR:-../../backend}/design-software-scheduling-service` |
| `academic` | `academic-api` + `iam-api` (JWKS) + `rabbitmq` + `traefik` (edge) | `${BACKEND_REPOS_DIR:-../../backend}/design-software-academic-management-service` |
| `reference` | `reference-data-api` + `iam-api` (JWKS) + `rabbitmq` + `traefik` (edge) | `${BACKEND_REPOS_DIR:-../../backend}/design-software-reference-data-service` |
| `training` | `training-api` + `iam-api` (JWKS) + `rabbitmq` + `traefik` (edge) | `${BACKEND_REPOS_DIR:-../../backend}/design-software-training-environment-service` |
| `document` | `document-api` + `document-template-api` + renderer + dispatcher + `minio` + `rabbitmq` + `traefik` (edge). Necesita `iam` para autenticar | `${BACKEND_REPOS_DIR:-../../backend}/design-software-document-service` |
| `audit` | `audit-query-api` + `audit-worker` + `rabbitmq` + `traefik` (edge). Necesita `iam` para autenticar | `${AUDIT_SERVICE_DIR:-../../design-software-audit-service}` |
| `monitoring` | Stack local R3 de `monitoring-api` con su propio nginx (`monitoring-edge`, `:15000`); **no** trae `traefik`. Para ver `/monitoring/...` por el edge, agregar `--profile edge` | `${BACKEND_REPOS_DIR:-../../backend}/design-software-monitoring-service` |
| `edge` | `traefik` + el frontend que sirve: `web-shell-static` y los 9 `<dominio>-mfe-static` (HU-SHELL-011). Se suma a cualquier perfil de dominio: `--profile edge --profile iam`. Los perfiles de dominio solos traen `traefik` pero no el frontend (`/` y `/mfe/...` responden `502`) | `${FRONTEND_REPOS_DIR:-..}/design-software-web-shell` y `design-software-<dominio>-mfe`, más `design-system` y `frontend-platform` como contextos de build con nombre |
| `observability` | Collector OTel + Tempo + Prometheus + Loki + Grafana (ADR-008) | — |

`BACKEND_REPOS_DIR` (default `../../backend`) apunta a la carpeta con los repos de backend clonados junto a
`docker-infra` — **nunca** a un worktree privado de una HU, para que el build sea reproducible para cualquiera
que clone el monorepo de repos tal como está documentado.

### Levantar iam-service local (HU-IAM-012)

```bash
# 1. Levanta postgres + iam-api + rabbitmq (perfil iam trae el broker solo).
#    Usar --build siempre en servicios de aplicación para no correr una imagen stale.
docker compose --env-file .env.develop --profile iam up -d --build

# 2. Aplicar el schema de iam (si no está aplicado)
docker compose --env-file .env.develop --profile tooling run --rm liquibase-iam update

# 3. Con trazas E2E cross-servicio (Tempo/Grafana, ADR-008) — agregar observability:
docker compose --env-file .env.develop --profile iam --profile observability up -d --build
```

> **Gotcha — contenedor stale:** levantá los servicios de aplicación con `up -d --build` y, **antes de reportar un bug de deploy** (un 404, un endpoint que "no existe"), **verificá el SHA de la imagen** que corre contra el que acabás de construir (`docker compose images` / `docker inspect`). Un contenedor viejo sin reconstruir ya dio falsos 404 que parecían bugs de código.

- **Acceso**: solo por el edge — `GET http://localhost:${EDGE_PORT:-18080}/iam/health` (ADR-007; el `-api` no
  se expone al host). El resto del contrato vive bajo `/iam/api/v1/...` (p. ej.
  `POST /iam/api/v1/auth/login`).
- **Env vars obligatorias** (sin default de secreto): `IAM_DB_USERNAME`/`IAM_DB_PASSWORD` (usuario de
  aplicación, ver `create-app-user.sh`), `IAM_JWT_PRIVATE_KEY`, `IAM_JWT_ISSUER`. Ver
  [runbook.md del servicio](../09-microservices/services/01-iam-service/runbook.md) para la tabla completa y
  [.env.example](../../../../infraestructure/design-software-docker-infra/.env.example) para la plantilla.
- **Trazas**: con `observability` activo, Grafana en `http://localhost:${GRAFANA_PORT:-3000}` → Explore →
  Tempo, buscar por `trace_id` (se ve en las cabeceras de respuesta / logs JSON del `iam-api`, ADR-008). Un
  login + operación autorizada debe mostrarse como **una sola traza** con spans HTTP (edge → iam-api) + DB
  (Postgres) + AMQP (publicación a `iam-events` cuando corresponde, p. ej. `iam.session.started`).

### Levantar notification-service local (perfil `notification`)

Simétrico a `iam`. El perfil `notification` levanta `notification-api` + `notification-worker` (Go) + `rabbitmq` + `mailhog` + `traefik` (edge).

```bash
# 1. Levanta postgres + notification-api + notification-worker + rabbitmq + mailhog + traefik.
#    --build para no correr imágenes stale (mismo gotcha que iam).
docker compose --env-file .env.develop --profile notification up -d --build

# 2. Aplicar el schema si aplica (perfil tooling)
docker compose --env-file .env.develop --profile tooling run --rm liquibase-<modulo> update

# 3. Con trazas E2E (Tempo/Grafana, ADR-008):
docker compose --env-file .env.develop --profile notification --profile observability up -d --build
```

- **RabbitMQ — reset dirigido del volumen:** el broker se aprovisiona desde `definitions.json`, que **debe incluir `users` y `permissions`**; si falta un usuario/permiso o cambió el aprovisionamiento, **reseteá el volumen de RabbitMQ** (no el de Postgres) para que reaplique las definitions:

  ```bash
  docker compose --env-file .env.develop rm -sfv rabbitmq   # borra solo el contenedor+volumen de rabbitmq
  docker compose --env-file .env.develop --profile notification up -d --build
  ```

  > **No uses `down -v`** para esto: borraría también el volumen de Postgres y perderías el schema/seed. Reseteá **solo** `rabbitmq`.
- **MailHog:** captura el correo saliente del worker para inspección local (no envía a destinatarios reales).
- **Acceso:** igual que iam, solo por el edge Traefik; los `-api` no se exponen al host.

### Levantar los dominios nuevos (perfiles `academic`, `reference`, `training`)

Estos tres perfiles se agregaron con HU-SHELL-009. Cada uno trae `postgres`, `rabbitmq`, `iam-api` (los servicios validan el JWT contra su JWKS) y el edge, y **construye desde el Dockerfile del repo del servicio** (`BACKEND_REPOS_DIR`), no desde copias locales.

```bash
# Un dominio
docker compose --env-file .env.develop --profile academic up -d --build

# Varios a la vez
docker compose --env-file .env.develop --profile academic --profile reference --profile training up -d --build

# Los dominios con servicio en el compose, detrás del edge
docker compose --env-file .env.develop \
  --profile iam --profile actors --profile scheduling --profile academic --profile reference \
  --profile training --profile document --profile audit --profile notification up -d --build
```

Antes de levantar, aplicar el schema del módulo (`liquibase-academic`, `liquibase-reference`, `liquibase-training`, perfil `tooling`) y crear el usuario de aplicación (`create-app-user.sh`), igual que para `iam`.

**Dependencias que viven en el repo de cada servicio** (el compose es válido hoy, pero el contenedor corre solo cuando llega la HU de ese repo):

| Perfil | Qué falta | HU |
|--------|-----------|----|
| `academic` | `deploy/Dockerfile.api`. Hoy el repo solo tiene `deploy/Dockerfile.r3-test`, que corre un test y no un servicio. | HU-ACAD-019 |
| `reference` | Validador JWKS configurable. Hoy solo acepta `http` en loopback, así que `reference-data-api` en su propio contenedor (ya no comparte la red de `iam-api`) termina al arrancar con `jwks url must use https outside local loopback`. | HU-REF-031 |
| `training` | El `Dockerfile.environment-api` usa Go 1.25 contra `go.mod` 1.26 y no compila. | HU-ENV-020 |

---

## Edge: tabla de rutas por dominio (ADR-022, HU-SHELL-009)

El navegador habla con **un solo origen por ambiente, el edge**. Las rutas viven en un archivo, [`traefik/dynamic.yml`](https://github.com/code-sena/design-software-docker-infra/blob/develop/traefik/dynamic.yml) de `docker-infra` (proveedor de archivo de Traefik), y es **la misma tabla en `develop`, `qa`, `staging` y `main`** (ADR-022 §4 y §6): se revisa en un PR y se promueve por el mismo git-flow que el resto. Los servicios ya no llevan labels de Traefik y el edge no usa el socket de Docker.

Tres familias, en este orden de prioridad (en Traefik gana el número mayor):

| Prioridad | Regla | Destino | Ejemplo |
|-----------|-------|---------|---------|
| 30 | `PathPrefix(/<dominio>/api/)` | El servicio del dominio, con `stripPrefix /<dominio>` | `/scheduling/api/v1/schedules` → `scheduling-api:8080/api/v1/schedules` |
| 30 | `Path` exactos `/<dominio>/health`, `/<dominio>/ready` y `/<dominio>/actuator/health` | El servicio, con `stripPrefix /<dominio>` | `/iam/ready` → `iam-api:8080/ready` |
| 20 | `PathPrefix(/mfe/<dominio>/)` | `<dominio>-mfe-static`, con `stripPrefix /mfe/<dominio>` | `/mfe/iam/remoteEntry.js` → `iam-mfe-static:8080/remoteEntry.js` |
| 10 | `PathPrefix(/)`, todo lo demás | `web-shell-static` | `/iam/usuarios` → HTML del shell |

La regla de prioridad 10 permite recargar o compartir cualquier ruta de la SPA (`/iam/usuarios`) sin chocar con el API (`/iam/api/v1/...`).

| Prefijo | Servicio (nombre en compose) | Perfil | MFE |
|---------|------------------------------|--------|-----|
| `/iam` | `iam-api:8080` | `iam` | sí |
| `/scheduling` | `scheduling-api:8080` (con rate limit 60/min, ráfaga 20) | `scheduling` | sí |
| `/academic-management` | `academic-api:8080` | `academic` | sí |
| `/training-environment` | `training-api:8080` | `training` | sí |
| `/reference-data` | `reference-data-api:8080` | `reference` | sí |
| `/actors` | `actors-api:8080` por HTTPS | `actors` | sí |
| `/document` | `document-api:8080`; `/document/api/v1/document-templates` → `document-template-api:8080` (prioridad 31) | `document` | sí |
| `/monitoring` | `monitoring-api:8000` | `monitoring` | sí |
| `/audit` | `audit-query-api:8080` | `audit` | sí |
| `/notification` | `notification-api:8080` | `notification` | no |

**Qué cambia respecto del enrutado anterior.** Antes `/iam`, `/scheduling`, `/audit` y `/notification` mandaban todo lo que colgaba del prefijo al servicio, y document respondía en `/api/v1/documents` y `/api/v1/document-templates` sin prefijo. Ahora el prefijo de dominio solo cubre `/api/` y los health. Por eso `/api/v1/documents` pasa a ser `/document/api/v1/documents`, y un servicio cuyas rutas no cuelgan de `/api/v1` (hoy notification, con `POST /notifications`) queda sin ruta de negocio por el edge hasta que se alinee a su contrato (ADR-022 §3: no hay reglas especiales en el edge para tapar esa deriva).

**Lo que la tabla da por supuesto de otras HU:**

- `web-shell-static` y los 9 `<dominio>-mfe-static`: **HU-SHELL-011** construye las imágenes (cada repo trae su `Dockerfile`) y `docker-compose.yml` define los servicios en el perfil `edge`, con `build.additional_contexts` para `design-system` y `frontend-platform` (ver [frontend-images.md](./frontend-images.md)). Sin el perfil `edge` las familias de prioridad 20 y 10 responden `502` desde el edge. Contrato con esa HU: son imágenes nginx que escuchan en `8080` (ADR-007 §2), sin publicar puerto al host; el edge quita `/mfe/<dominio>` y el contenedor sirve su `dist/` en la raíz (el MFE se compila con `base: '/mfe/<dominio>/'`, ADR-022 §5); el fallback a `index.html` lo hace el nginx del shell, no Traefik. `FRONTEND_REPOS_DIR` (default `..`) apunta a la carpeta con los repos del frontend, igual que `BACKEND_REPOS_DIR` para el backend.
- `actors` expone HTTPS con mTLS. El edge todavía no presenta certificado de cliente (`serversTransport`), así que `/actors/...` falla en el edge con un 5xx hasta **HU-ACT-020**.
- Si el servicio de un dominio no está levantado, su ruta responde `502` (no `404`): la ruta existe, el backend no.

### Verificar las tres familias

```bash
docker compose --env-file .env.<ambiente> --profile edge --profile iam up -d --build   # API + shell + remotes
EDGE_URL=http://localhost:18080 bash scripts/edge-smoke.sh
SKIP_DOMAINS="actors" EDGE_URL=http://localhost:18080 bash scripts/edge-smoke.sh   # omite dominios cuyo servicio no corre
```

El script no necesita token: comprueba **quién respondió**. Para cada dominio, que `/<dominio>/api/...` llegue al servicio (no al shell ni a un 5xx) y que su health responda 200; que `/mfe/<dominio>/remoteEntry.js` devuelva JavaScript; y que las rutas de la SPA (`/<dominio>/...`, `/`) devuelvan el HTML del shell. Termina con código distinto de cero si algo falla.

### Agregar un dominio

En `traefik/dynamic.yml`: un `service` por backend, el middleware `strip-<dominio>` (y `strip-mfe-<dominio>` si tiene MFE), los routers `<dominio>-api` y `<dominio>-health` (prioridad 30) y `<dominio>-mfe` (20); luego sumarlo a `scripts/edge-smoke.sh` y al perfil que corresponda en `docker-compose.yml` (con `traefik` en su lista `profiles`). No hay variable por ambiente: la tabla es la misma en los cuatro.

---

## Gotchas de observabilidad / deploy

- **OTel — el puerto depende del stack, no lo copies entre servicios.** El endpoint OTLP correcto **difiere por runtime**:
  - **`iam` (agent Java):** `:4318` con **http/protobuf**.
  - **`notification` (SDK Go):** `:4317` con **gRPC**.
  - **`monitoring` (SDK Python):** `:4318` con **http/protobuf**. En Python no hay un protocolo implícito: lo decide el paquete exportador que se importe. `opentelemetry-exporter-otlp-proto-grpc` apunta por defecto a `localhost:4317` (gRPC, sin ruta) y `opentelemetry-exporter-otlp-proto-http` a `http://localhost:4318` con una ruta por señal (`/v1/traces`, `/v1/metrics`, `/v1/logs`). `monitoring-service` importa el exportador HTTP y le agrega esa ruta a `OTEL_EXPORTER_OTLP_ENDPOINT` (`http://otel-collector:4318`); su `requirements-runtime.lock` no incluye el exportador gRPC. `document` (Python) no está verificado: su servicio del compose no define `OTEL_*`.

  **No copies la config OTLP de un stack a otro** (por ejemplo, la de `notification` a un micro Java o Python). Apuntar el `iam` (Java) a `:4317` produjo `Connection reset` → **0 trazas** en Tempo, sin error visible en el arranque. Si un servicio no emite trazas, revisá primero puerto + protocolo contra su runtime y, en Python, contra el exportador que importa.
- **El socket de Docker Desktop / WSL rompía el edge Traefik en local (resuelto con HU-SHELL-009).** El bind-mount del socket de Docker en Docker Desktop sobre WSL no siempre expone un socket real, y el provider Docker de Traefik quedaba sin descubrir servicios → el edge no enrutaba (todo respondía 404). **Ya no aplica:** el edge usa el **provider `file`** (`traefik/dynamic.yml`, [ver arriba](#edge-tabla-de-rutas-por-dominio-adr-022-hu-shell-009)) en los cuatro ambientes, sin labels ni socket, así que no hay override local ni variables `TRAEFIK_DOCKER_*`. El enrutado por edge se valida con `scripts/edge-smoke.sh`.

---

### Puertos expuestos al host por ambiente (ADR-007)

| Recurso | develop | qa | staging | main |
|---|---|---|---|---|
| Edge (Traefik) — único entry point | 18080 | 18081 | 18082 | 18083 |
| Traefik dashboard | 18090 | 18091 | 18092 | 18093 |
| Postgres | 15432 | 15433 | 15434 | 15435 |
| RabbitMQ mgmt | 15672 | 15673 | 15674 | 15675 |
| Grafana / Tempo / Prometheus / Loki (ADR-008) | base + offset | +1 | +2 | +3 |
| `iam-api` (y cualquier `-api` de dominio) | **no expuesto** — solo vía edge | | | |
