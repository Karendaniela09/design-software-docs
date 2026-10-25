# Setup local

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: DevOps

Cómo levantar la base de datos del proyecto y aplicar las migraciones de cada módulo en local. Complementa a [migration-strategy.md](../06-data/migration-strategy.md).

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
solos al levantar el perfil del dominio que los necesita, sin tener que enumerar `--profile edge` o
`--profile broker` a mano.

| Perfil | Qué levanta | Build context (portable) |
|--------|-------------|---------------------------|
| `notification` | `notification-api` + `notification-worker` + `rabbitmq`/`mailhog` + `traefik` (edge) | `${BACKEND_REPOS_DIR:-../../backend}/design-software-notification-service` |
| `iam` | `iam-api` + `rabbitmq` (eventos `iam-events`) + `traefik` (edge) | `${BACKEND_REPOS_DIR:-../../backend}/design-software-iam-service` |
| `edge` | Solo `traefik`, si se necesita levantarlo sin ningún dominio | — |
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

---

## Gotchas de observabilidad / deploy

- **OTel — el puerto depende del stack, no lo copies entre servicios.** El endpoint OTLP correcto **difiere por runtime**:
  - **`iam` (agent Java):** `:4318` con **http/protobuf**.
  - **`notification` (SDK Go):** `:4317` con **gRPC**.
  - **`monitoring` (SDK Python):** `:4318` con **http/protobuf**. En Python no hay un protocolo implícito: lo decide el paquete exportador que se importe. `opentelemetry-exporter-otlp-proto-grpc` apunta por defecto a `localhost:4317` (gRPC, sin ruta) y `opentelemetry-exporter-otlp-proto-http` a `http://localhost:4318` con una ruta por señal (`/v1/traces`, `/v1/metrics`, `/v1/logs`). `monitoring-service` importa el exportador HTTP y le agrega esa ruta a `OTEL_EXPORTER_OTLP_ENDPOINT` (`http://otel-collector:4318`); su `requirements-runtime.lock` no incluye el exportador gRPC. `document` (Python) no está verificado: su servicio del compose no define `OTEL_*`.

  **No copies la config OTLP de un stack a otro** (por ejemplo, la de `notification` a un micro Java o Python). Apuntar el `iam` (Java) a `:4317` produjo `Connection reset` → **0 trazas** en Tempo, sin error visible en el arranque. Si un servicio no emite trazas, revisá primero puerto + protocolo contra su runtime y, en Python, contra el exportador que importa.
- **Bug del socket de Docker Desktop / WSL rompe el edge Traefik en local.** El bind-mount del socket de Docker en Docker Desktop sobre WSL no siempre expone un socket real, y el provider Docker de Traefik queda sin descubrir servicios → el edge no enruta. **Workaround:** usar el **provider `file`** de Traefik (configuración estática de rutas) en lugar del provider Docker, o correr en un entorno con socket de Docker real. **Estado: `E2-edge` no validado localmente** por este bug — el enrutado por edge se ha verificado por otras vías, no por el descubrimiento automático vía socket.

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
