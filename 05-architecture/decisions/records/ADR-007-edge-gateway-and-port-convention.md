# ADR-007: Edge/gateway gestionado y convención de puertos

**Estado:** ACCEPTED (2026-08-14)
**Fecha:** 2026-08-14
**Autores:** Jesús Ariel González Bonilla (PM + Arquitecto)
**Equipos involucrados:** Arquitectura, Backend, DevOps

> Concretada por [ADR-022](./ADR-022-edge-routing-table-by-domain.md): la tabla de rutas por dominio, el orden de prioridad frente a la SPA y el proveedor de archivo en lugar de labels (ajusta el §1).

---

## Contexto

Con múltiples microservicios polyglot ([ADR-006](./ADR-006-polyglot-stack-strategy.md)) y **4 ambientes**,
se necesita: (a) un **punto de entrada único** con authN/routing/rate-limit, y (b) evitar **colisión de
puertos**. El ADR-006 puso tentativamente el `gateway` como servicio Go — un API gateway es, sin embargo,
un problema resuelto.

## Decisión

### 1. El edge es un reverse-proxy gestionado (Traefik), no código

El gateway es **Traefik** configurado en `docker-infra` (no un repo de código). Hace routing,
verificación de **JWT en el borde**, rate-limit y TLS. **Descubre los servicios por labels** → auto-resuelve
ruteo y puertos.

> **Ajusta [ADR-006](./ADR-006-polyglot-stack-strategy.md):** `design-software-gateway` deja de ser un
> repo Go; es **config de Traefik en `docker-infra`**. (Kong es la alternativa si se necesitan plugins.)
> La **agregación** para el frontend es el **BFF** (un servicio), NO el edge: el edge solo enruta + valida.

### 2. En contenedores, los puertos internos no colisionan

Cada servicio corre en su propia red/contenedor → todos escuchan en **`8080` interno** (vía env `PORT`).
El edge los alcanza por **nombre de servicio** (`iam-api:8080`). La colisión solo existe en **puertos
expuestos al host**; y los 4 ambientes son 4 proyectos compose = 4 redes aisladas.

### 3. Convención de puertos (offset por ambiente: develop=0, qa=1, staging=2, main=3)

**Solo se expone al host el edge + infra.** Los `-api` de dominio **no** se exponen (acceso vía edge;
mapeo temporal solo para debug). Los workers no tienen puerto.

| Expuesto al host | develop | qa | staging | main |
|------------------|---------|----|---------|----|
| **Edge (Traefik)** — entry único de la app | 18080 | 18081 | 18082 | 18083 |
| Traefik dashboard | 18090 | 18091 | 18092 | 18093 |
| Postgres (existente) | 15432 | 15433 | 15434 | 15435 |
| RabbitMQ mgmt | 15672 | 15673 | 15674 | 15675 |
| (observabilidad: ver [ADR-008](./ADR-008-observability-opentelemetry.md)) | base+offset | | | |
| **`-api` de dominio** | interno `8080`, **no expuesto** | | | |

### 4. Routing
`/<dominio>/...` → `<service>:8080` (labels Traefik por servicio). Contrato de ruteo versionado con el resto.

## Consecuencias

### Positivas
- Menos código (routing/JWT/rate-limit/TLS resueltos por Traefik); auto-descubrimiento de puertos y rutas.
- Un solo entry point por ambiente; cero colisión por diseño.
- El clúster Go se libera para servicios reales (no mantener un gateway).

### Negativas / Trade-offs
- Traefik es una nueva dependencia de infra que hay que operar/configurar.
- La verificación de JWT en el borde vive en config Traefik (middleware), no en código propio.

### Riesgos
- Config drift de Traefik entre ambientes. Mitigación: la config vive en `docker-infra` y se propaga por el mismo git-flow.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Gateway codeado en Go (ADR-006 original) | Reinventa routing/JWT/rate-limit/TLS ya resueltos; más mantenimiento. |
| Exponer cada `-api` al host | Colisión de puertos + superficie de ataque; rompe el entry único. |
| Kong / Nginx | Válidos; Traefik gana por auto-descubrimiento por labels en compose. |

## Referencias

- [ADR-005](./ADR-005-microservices-topology-and-transversal-capabilities.md) · [ADR-006](./ADR-006-polyglot-stack-strategy.md) · [ADR-008](./ADR-008-observability-opentelemetry.md)
- `TOPOLOGIA-REPOS.md` (workspace)
