# ADR-022: Tabla de rutas del edge por dominio y origen único para el frontend

**Estado:** ACCEPTED (2026-10-24)
**Fecha:** 2026-10-24
**Autores:** Jesús Ariel González Bonilla (PM + Arquitecto)
**Equipos involucrados:** Arquitectura, DevOps, Frontend, Backend

> Concreta el §4 de [ADR-007](./ADR-007-edge-gateway-and-port-convention.md) ("`/<dominio>/...` → `<service>:8080`") y ajusta su §1 en cómo se descubren las rutas. Es la decisión **D3** de la ruta de cierre.

---

## Contexto

ADR-007 fijó un edge Traefik único por ambiente y la regla general `/<dominio>/...`. No fijó la tabla concreta, ni cómo la consumen el shell y los MFE. Al levantar `develop` completo en local (2026-10-24: 10 backends, shell y 9 MFE) quedó a la vista lo que esa falta provoca:

- **El edge de `develop` solo enruta 3 dominios.** `traefik/local-dynamic.yml` cubre iam, scheduling y document; academic-management, reference-data y training-environment ni siquiera tienen perfil en el compose. El proveedor Docker de Traefik (labels) falla en Docker Desktop con "Error response from daemon", y sin el override de archivo todo responde 404.
- **Cada MFE asume una base distinta y ninguno llega a su backend.** El proxy de desarrollo del shell solo conoce `/api/v1` → IAM, `/audit/api/v1` → `:8081` y `/time-slots` → `localhost:8080` fijo en el código:

  | MFE | Llama a | Resultado |
  |---|---|---|
  | academic-management | `/api/v1/fichas` | Va a IAM: 404 |
  | monitoring | `/api/v1/kpi-types`, `/api/v1/risk-levels`… | Va a IAM: 404 |
  | scheduling | `/time-slots` | Va a `:8080` fijo: `ECONNREFUSED` |
  | training-environment | `/training-environments` (sin prefijo) | Recibe el `index.html` del shell y cae a datos mock sin avisar |

- **`/reports` aparece en 9 contratos OpenAPI.** Sin un prefijo de dominio, el edge no puede saber a qué servicio va. Por la misma razón, cada PR de micro arregla el proxy del shell "para su micro" y los PR se pisan.
- **Las rutas de la SPA del shell y las del API comparten prefijo.** El shell monta cada remote en `/<dominio>/*` (ADR-009 §10). Si el edge mandara todo `/iam` a `iam-api`, recargar el navegador en `/iam/usuarios` llegaría al backend y no al shell. `web-shell#24` ya tuvo que acotar su proxy a `/audit/api/v1` por esto.
- **Los 12 contratos de `07-api` declaran `servers: /api/v1`**, pero no todos los servicios lo cumplen. Verificado por el edge con token:

  | Cumplen `/api/v1` | No cumplen |
  |---|---|
  | iam, scheduling, audit, monitoring, document | training-environment (`/environment-types`), reference-data (`/macroregions`), academic-management en sus catálogos (`/tech-lines`, `/training-programs`; `fichas` y `reports` sí lo cumplen) |

  notification queda **no verificado**.

## Decisión

Se decide que **el navegador habla con un solo origen por ambiente, el edge**, y que el edge enruta con la tabla única de abajo, versionada en `docker-infra`.

### 1. Tres familias de rutas, en este orden de prioridad

| Prioridad | Regla | Destino | Ejemplo |
|---|---|---|---|
| 1 | `PathPrefix(/<dominio>/api/)` | El servicio del dominio, con `stripPrefix /<dominio>` | `/scheduling/api/v1/schedules` → `scheduling-api:8080/api/v1/schedules` |
| 1 | `Path` exacto de los health y ready que no cuelgan de `/api/` | El servicio, con `stripPrefix /<dominio>` | `/iam/ready` → `iam-api:8080/ready`; `/academic-management/actuator/health` |
| 2 | `PathPrefix(/mfe/<dominio>/)` | El estático del remote | `/mfe/iam/remoteEntry.js` |
| 3 | Todo lo demás (`/`) | El estático del web-shell, con fallback a `index.html` | `/iam/usuarios` → shell |

La regla 3 es la que permite recargar o compartir cualquier ruta interna de la SPA sin chocar con el API.

### 2. Tabla de dominios

| Prefijo | Servicio (nombre en compose) | Notas |
|---|---|---|
| `/iam` | `iam-api:8080` | |
| `/scheduling` | `scheduling-api:8080` | |
| `/academic-management` | `academic-api:8080` | |
| `/training-environment` | `training-api:8080` | |
| `/reference-data` | `reference-data-api` | Hoy comparte red con `iam-api` (`:8082`) porque su validador JWKS solo acepta `http` en loopback. Es deuda. |
| `/actors` | `actors-api:8080` | Expone HTTPS con mTLS. El edge necesita un `serversTransport` con certificado de cliente; se resuelve en su HU. |
| `/document` | `document-api:8080` y `document-template-api:8080` | `/document/api/v1/document-templates` va a template-api; el resto de `/document/api/` a document-api. |
| `/monitoring` | `monitoring-api:8000` | Enrutar no basta: monitoring tiene que aceptar los tokens de IAM (hoy usa emisor, llave y audience propios). |
| `/audit` | `audit-query-api:8080` | |
| `/notification` | `notification-api:8080` | |

Los nombres de servicio son los del compose de `docker-infra`. Los prefijos son los mismos `basePath` con que el shell monta cada remote (`remote-registry.ts`).

### 3. La ruta pública de un endpoint es `/<dominio>` + el `servers` de su contrato

Ruta pública = `/<dominio>/api/v1/<recurso>`. **El contrato manda**: el servicio expone exactamente lo que declara su OpenAPI (`servers: /api/v1`). training-environment, reference-data y los catálogos de academic-management se alinean al contrato en sus HU de implementación. No se agregan reglas especiales en el edge para tapar esa deriva.

### 4. La tabla se versiona como archivo, no como labels

La tabla vive en `docker-infra` como configuración del **proveedor de archivo** de Traefik, y es **la misma en los 4 ambientes**. Ajusta el §1 de ADR-007 ("descubre los servicios por labels") por tres razones:

- El proveedor por labels falla en Docker Desktop, que es donde trabaja el equipo.
- Un solo archivo se revisa en un PR y se promueve por el mismo git-flow que el resto.
- Funciona igual en el VPS.

### 5. Cómo lo consume el frontend

- **MFE:** la base de su API es relativa y del mismo origen: `/<dominio>/api/v1`. No necesita variable por ambiente ni CORS. Si se ejecuta aislado (fuera del shell), su propio servidor de desarrollo hace proxy de `/<dominio>/api` al edge.
- **Shell en desarrollo:** su proxy de vite reenvía `/<dominio>/api` y `/mfe` al edge (`VITE_EDGE_ORIGIN`, por defecto `http://localhost:18080`). Se eliminan los proxies por micro (`/api/v1` → IAM, `/audit/api/v1` → `:8081`, `/time-slots` → `:8080`).
- **Remotes desplegados:** el manifest apunta a `/mfe/<dominio>/remoteEntry.js` del mismo origen, y cada MFE se compila con `base: '/mfe/<dominio>/'` para que sus chunks y su CSS resuelvan bajo esa ruta. Como las rutas son relativas, **el manifest es el mismo en los 4 ambientes**. En local, con servidores de desarrollo, se mantienen los puertos 5101–5109.

### 6. Lo mismo se despliega en `develop`, `qa`, `staging` y `main`

El código, las imágenes, la tabla de rutas y el manifest de remotes son idénticos en los 4 ambientes. **Lo único que cambia son los datos** (sintéticos en `develop` y `qa`) y los valores que inyecta cada ambiente al desplegar: el dominio, los certificados TLS y los secretos. Ningún componente tiene comportamiento condicionado al ambiente. Así, lo que se prueba en `develop` es lo que llega a `main`.

### Fuera de alcance

- TLS y dominio público de cada ambiente: van en el plan de despliegue.
- Verificación de JWT en el edge (ADR-007 §1): hoy cada servicio valida su token. Esto no cambia aquí.
- Login y sesión: [ADR-023](./ADR-023-web-shell-owns-login-and-session.md).

## Consecuencias

### Positivas

- Un solo origen: sin CORS, sin puertos de backend expuestos, sin proxies por micro.
- Se acaban las colisiones (`/reports`, `/api/v1` genérico) y los PR que se pisan en `vite.config.ts`.
- Las rutas internas de la SPA se pueden recargar y compartir.
- La misma tabla y el mismo manifest sirven en local, en el VPS y en los 4 ambientes: solo cambian los datos y los valores del ambiente.

### Negativas / Trade-offs

- Tres servicios tienen que alinear sus rutas al contrato: training-environment, reference-data y academic-management en sus catálogos.
- Los 9 MFE cambian su base de API a `/<dominio>/api/v1`, y para los ambientes desplegados se compilan con `base` propio.
- El proxy del shell se reescribe una sola vez. Mientras eso no esté mergeado, ningún PR de micro toca `vite.config.ts` por su cuenta.

### Riesgos

- **Una prioridad mal puesta en Traefik rompe los deep links de la SPA o manda el API al shell.** Mitigación: smoke del despliegue con las tres familias de rutas, por ejemplo `GET /iam/usuarios` → HTML del shell y `GET /iam/api/v1/auth/me` → JSON.
- **actors y monitoring necesitan trabajo extra** además de la ruta (mTLS y confianza en IAM). Se registran como HU propias para no bloquear al resto.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Proxies por micro en el shell (lo de hoy) | Colisionan (`/api/v1` va a IAM para todos), no existen en un ambiente desplegado y hacen que los PR se pisen. |
| Rutas por recurso sin prefijo (`/api/v1/fichas` → academic) | `/reports` está en 9 contratos; obliga a mantener a mano una lista de recursos por servicio. |
| Un subdominio por dominio (`iam.api.<ambiente>`) | Exige DNS, TLS y CORS por dominio. Más operación sin ganancia para este tamaño. |
| Agregación en el BFF (ADR-007 §1) | `web-bff` es un esqueleto con un solo caso de uso. Suma un salto. Sigue siendo la opción para agregaciones puntuales, no para el enrutamiento base. |

## Referencias

- [ADR-007](./ADR-007-edge-gateway-and-port-convention.md): edge y convención de puertos.
- [ADR-009](./ADR-009-frontend-framework-and-build-strategy.md): §10 (ruteo anidado por dominio) y §11 (contrato `remote-props`).
- [ADR-023](./ADR-023-web-shell-owns-login-and-session.md): login y sesión del shell.
- [`10-devops/environments.md`](../../../10-devops/environments.md): puertos por ambiente.
- Contratos: [`07-api/contracts/openapi/`](../../../07-api/contracts/openapi/).
