# ADR-006: Estrategia polyglot fit-driven y estructura hexagonal por stack

**Estado:** ACCEPTED (2026-08-14)
**Fecha:** 2026-08-14 (rev. 3, 2026-10-24: nombres de directorio del árbol Python)
**Autores:** Jesús Ariel González Bonilla (PM + Arquitecto)
**Equipos involucrados:** Arquitectura, Backend, Frontend, Formación (aprendices SENA)

---

## Contexto

Proyecto formativo (aprendices SENA). El objetivo es **aprovechar la mejor herramienta para cada
escenario** y **demostrar la fortaleza de microservicios**: cada servicio puede usar el lenguaje que
le da ventaja, porque la arquitectura ([ADR-005](./ADR-005-microservices-topology-and-transversal-capabilities.md))
garantiza repos independientes, contract-first y **cero código compartido de dominio entre servicios**.

**Principio rector:** **DDD + Hexagonal + TDD + SDD aplican por igual en todos los stacks.** El dominio
es puro; el lenguaje vive en los *adapters*.

## Decisión

### 1. Polyglot fit-driven (no un número fijo de stacks)

No se fija "3 stacks". Se define un **conjunto candidato** — **{Go, Java, Python, Node/TS}** — y cada
lenguaje **se gana su lugar por ventaja**, bajo dos reglas:

- **Amortización por clúster:** un lenguaje entra cuando un **clúster de ≥2–3 servicios** obtiene
  ventaja real. Cada lenguaje paga un **impuesto fijo**: golden template + **shared platform lib** +
  instrumentación **OTel** + config **CI/Pact** + un **mentor**. Un lenguaje con un solo servicio paga
  el impuesto completo por beneficio mínimo → no se justifica.
- **Drop-if-no-fit:** si tras el análisis un lenguaje no reúne un clúster con ventaja, **se retira** y
  sus servicios se absorben en otro. **Techo práctico: 4 lenguajes** para un equipo formativo; más es
  esparcirse.

### 2. Mapa actual (13 componentes runtime)

| Stack | Servicios | Ventaja | Estado |
|-------|-----------|---------|--------|
| **Node/TS** | `web-bff`, `mobile-bff` | El frontend ya es TS → tipos/ecosistema compartidos; el BFF pertenece al consumidor (frontend) | ✅ se lo gana |
| **Java · Spring Boot** | `iam`, `scheduling`, `academic-management`, `actors` | Transaccional + dominio rico (Spring Security, JPA, invariante `EXCLUDE` + workflow) | ✅ se lo gana |
| **Go** | `gateway`, `audit`, `notification`, `reference-data`, `training-environment` | Edge + workers de alto throughput + CRUD liviano con caché | ✅ se lo gana |
| **Python · FastAPI** | `monitoring`, `document` | Analítica de KPIs (pandas/ML de deserción a futuro) + templating/PDF | 🟡 **en validación** — si `monitoring` no tiene analítica real, este clúster se absorbe en Go/Java |

`shared-contracts` no lleva stack (son specs). El mapa **evoluciona** según fit; reasignar es de bajo
riesgo (ver Consecuencias).

### 3. Capas hexagonales canónicas (idénticas en todos los stacks)

```
domain/       model (agregados, entidades, value objects) · event · service   → PURO
application/  usecase (uno por HU) · port/in · port/out
adapter/      in/ (http, amqp) · out/ (persistence, messaging, client)
<entrypoints> uno por componente desplegable: solo bootstrap + wiring
```
Regla (Grep-verificable, cualquier stack): `entrypoint → adapter → application → domain`.
En Python, `in/` y `out/` se llaman `inbound/` y `outbound/` (ver la nota bajo el árbol Python).

### 4. SDD (spec-driven) y TDD

- **SDD:** el servicio se genera/valida contra `shared-contracts` (OpenAPI → stubs + DTOs). El spec es la fuente.
- **TDD:** unit del dominio + integración de adapters, con el runner del stack.

### 5. Golden template **y** shared platform lib (por stack)

Dos piezas distintas, no una:

- **Golden template** — esqueleto de servicio (capas, regla de dependencia, Dockerfile, CI). Resuelve el **día 1** (se clona).
- **Shared platform lib** — librería **versionada, platform-only (CERO dominio)** con el cross-cutting:
  JWT validation, error-envelope, patrón Outbox, health-checks, instrumentación OTel. Vive aparte
  (`sena-platform-go`, `co.sena:platform-spring-boot-starter`, `sena-platform-py`, `@sena/bff-commons`)
  y se **actualiza una vez + bump de versión** — sin re-copiar a 13 servicios.
  > Guardarraíl: la lib es **platform-only**; meter dominio ahí reintroduce el monolito distribuido (R-ADR-005).
  > **Secuencia para aprendices:** arrancar con el template; **extraer la lib cuando el cross-cutting se estabilice**
  > (no library-izar el día 1 — el versionado prematuro es carga).

### 6. Observabilidad = OpenTelemetry (estándar cross-stack)

Con varios lenguajes, el tracing/métricas/logs se unifican con **OpenTelemetry**: instrumentación
nativa en Go/Java/Python/Node + **collector común** (en `docker-infra`). La instrumentación OTel vive
en la **shared platform lib** de cada stack → todo servicio queda instrumentado igual sin esfuerzo.

### 7. Gate de contrato en CI (no aspiracional)

`shared-contracts` + **Pact broker** con gate **ejecutable**: los consumer tests corren en el CI del
consumidor; la provider verification corre contra el contrato publicado; **una violación de contrato
= build en rojo = bloquea merge/deploy**. Sin este gate, la verificación no cuenta.

## Estructura de carpetas por stack (idiomática)

Mismas capas, empaquetado idiomático. La regla de dependencia es idéntica en los cuatro.

### Java · Spring Boot (Maven multi-módulo — los módulos *enforzan* el hexágono)

```
design-software-scheduling-service/
├── pom.xml (parent)
├── scheduling-core/        domain + application · SIN Spring web / SIN JPA
│   └── src/main/java/co/sena/scheduling/{domain/{model,event,service},application/{usecase,port/in,port/out}}
├── scheduling-adapters/    in/rest · out/persistence(JPA→scheduling_db) · out/messaging(outbox) · out/client
├── scheduling-api/         deployable (Spring Boot app + Dockerfile)
├── scheduling-engine/      deployable (workflow + Dockerfile)
├── conflict-validator/     deployable (worker + Dockerfile)
└── contracts/              OpenAPI ← shared-contracts (openapi-generator)
```

### Go (`internal/` + `cmd/`)

```
design-software-notification-service/
├── go.mod / go.sum
├── internal/{domain/{model,event,service}, application/{usecase,port/in,port/out},
│             adapter/{in/http,in/amqp,out/persistence(pgx→notification_db),out/messaging,out/client}}
├── cmd/{notification-api/main.go, notification-worker/main.go}   (cada carpeta = 1 contenedor)
├── deploy/Dockerfile.api · Dockerfile.worker
└── api/  (oapi-codegen ← shared-contracts) · *_test.go (TDD)
```

### Python · FastAPI (`src/` + `apps/`)

```
design-software-monitoring-service/
├── pyproject.toml / poetry.lock
├── src/monitoring/{domain/{model,event,service}, application/{usecase,port/{inbound,outbound}}  (port=Protocols),
│                   adapter/{inbound/{http(FastAPI+Pydantic),amqp},outbound/{persistence(SQLAlchemy→monitoring_db),messaging,client(httpx)}}}
├── apps/{api/main.py, alert_worker/main.py}   (entrypoints = contenedores)
├── deploy/Dockerfile.api · Dockerfile.worker
└── contracts/ (datamodel-code-generator) · tests/ (pytest)
```

> **Python: `inbound/` y `outbound/`, no `in/` y `out/`.** `in` es una palabra reservada de Python, así que `from monitoring.adapter.in.http import ...` y `port.in` son un `SyntaxError` al importar. Por eso, en este stack, los directorios que en Go, Java y Node/TS se llaman `in/` y `out/` se llaman `inbound/` y `outbound/` (es el árbol que tiene `design-software-monitoring-service`). La regla de dependencia no cambia. Corrección de la rev. 3: la rev. 2 mostraba `in/` y `out/` también para Python.

### Node/TS (BFF · `src/` + `apps/`) — dominio delgado, mayormente agregación

```
design-software-web-bff/
├── package.json / tsconfig.json
├── src/{domain/ (reglas de agregación, poco), application/{usecase,port/in,port/out},
│         adapter/{in/http(handlers, DTOs), out/client(clientes a los servicios), out/cache}}
├── apps/server.ts       (entrypoint = contenedor)
├── deploy/Dockerfile
└── contracts/ (openapi-typescript ← shared-contracts) · *.spec.ts (TDD)
```

## Consecuencias

### Positivas
- Se aprovecha la ventaja real de cada lenguaje; las fronteras duras **fuerzan** la disciplina de contratos.
- El mapa evoluciona por fit; el conocimiento hexagonal se transfiere entre stacks.
- Node para BFF alinea el BFF con su dueño (frontend) sin costo de ecosistema extra.

### Negativas / Trade-offs
- **Impuesto × N lenguajes**: cada stack necesita template + shared lib + OTel + CI + mentor. Por eso el **techo de 4** y la regla de amortización.
- **Portabilidad matizada:** los **invariantes y reglas del dominio portan limpio** entre lenguajes; el **idioma no** (composición en Go vs modelo rico en Java vs duck typing en Python vs TS). Reasignar = reescribir adapters + re-idiomatizar el dominio: **más barato con hexagonal, no gratis.**
- Mantener el estándar exige mentoría por stack.

### Riesgos
- "Cada quien su lenguaje" → zoológico. Mitigación: amortización por clúster + drop-if-no-fit (esta ADR).
- Deriva entre implementaciones del mismo patrón. Mitigación: shared platform lib + **gate Pact en CI (rojo bloquea)**.
- Un lenguaje "a medias" (sin lib + OTel + gate) no demuestra microservicios, demuestra fragmentación.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Número fijo de stacks (3) | Rígido; el fit-driven con amortización + drop es más honesto y evolutivo. |
| Single-stack | Máxima velocidad/calidad, pierde el objetivo formativo multi-stack. |
| Polyglot ad-hoc (cada quien elige) | Sin clúster ni fit → duplicación caótica del cross-cutting. |
| BFF en Python forzado | El BFF es del frontend (TS); Node comparte tipos/ecosistema → mejor fit. |
| Cross-cutting solo en template | Diverge al primer fix; se necesita **shared lib versionada**. |

## Referencias

- [ADR-005](./ADR-005-microservices-topology-and-transversal-capabilities.md) — topología de microservicios
- [pattern-guide.md](../../pattern-guide.md) · [service-boundary-rules.md](../../../09-microservices/service-boundary-rules.md)
- `TOPOLOGIA-REPOS.md` (workspace) — árbol de los repos
