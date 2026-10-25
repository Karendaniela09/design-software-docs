# Imágenes del frontend: shell y MFE servidos por el edge

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: DevOps, Frontend

Cómo se construyen y se sirven las imágenes del frontend (HU-SHELL-011, [ADR-022](../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md) §5 y §6). Hay **10 imágenes**, una por repo: `design-software-web-shell` y los 9 `design-software-<dominio>-mfe`. Cada repo trae su `Dockerfile` y su `nginx.conf`.

## Contexto

El edge es el único origen del navegador (ADR-022 §1). Para las dos familias de rutas del frontend, Traefik reenvía a una imagen estática:

| Prioridad | Ruta | Servicio (nombre en compose) | Qué hace el edge |
|---|---|---|---|
| 20 | `/mfe/<dominio>/*` | `<dominio>-mfe-static:8080` | Quita el prefijo `/mfe/<dominio>`: el contenedor sirve su `dist/` en la raíz. |
| 10 | todo lo demás (`/`) | `web-shell-static:8080` | Sin `stripPrefix`. El fallback a `index.html` lo hace el nginx del shell, no Traefik. |

La tabla vive en `docker-infra/traefik/dynamic.yml` (HU-SHELL-009). Los 9 dominios con MFE son `iam`, `scheduling`, `academic-management`, `training-environment`, `reference-data`, `actors`, `document`, `monitoring` y `audit` (`notification` no tiene MFE).

## Qué hay en cada imagen

Build de dos etapas: Node compila (`npm run build`) y nginx sirve `dist/` en el **puerto 8080** (ADR-007 §2), como usuario `nginx` sin privilegios. La imagen es **la misma en `develop`, `qa`, `staging` y `main`**: no recibe variables por ambiente (ADR-022 §6).

| Imagen | Base del build | Cabeceras de caché | Fallback |
|---|---|---|---|
| `<dominio>-mfe-static` | `base: '/mfe/<dominio>/'` en `vite.config.ts`, solo en `vite build` | `remoteEntry.js` e `index.html`: `no-cache`. `/assets/*` (con hash): `public, max-age=31536000, immutable` | Ninguno: una ruta desconocida responde 404. Un remote no es una página. |
| `web-shell-static` | `/` | `index.html` y `remotes.*.json`: `no-cache`. `/assets/*`: `immutable` | `index.html` para cualquier ruta que no sea un archivo, salvo `/assets/*`, que responde 404 de verdad. |

Ninguna imagen emite cabeceras CORS: el shell, los remotes y el API comparten origen.

### La base de los MFE

Cada MFE se compila con `base: '/mfe/<dominio>/'` para que sus chunks y su CSS resuelvan bajo esa ruta. En `vite.config.ts` es `base: command === 'build' ? '/mfe/<dominio>/' : '/'`: la condición es **build contra servidor de desarrollo**, no el ambiente. El valor es el mismo en los 4 ambientes y `npm run dev` sigue sirviendo en la raíz de los puertos 5101–5109.

Los chunks y el CSS que genera Module Federation resuelven relativos a su propio `remoteEntry.js`. Lo que `base` cambia es lo que Vite reescribe (el `index.html` y las URL de los assets importados). Un archivo de `public/` que el código pida con una ruta absoluta (`/images/logo.png`) **no** sigue la base: el navegador lo pediría al origen del shell. Se referencia como `${import.meta.env.BASE_URL}images/logo.png` (en `iam-mfe` y `actors-mfe` ya es así).

### El manifest de remotes del shell

El shell lee `remotes/remotes.<env>.json` en runtime y no tiene ninguna URL de `remoteEntry.js` en el código.

| Archivo | Contenido | Quién lo usa |
|---|---|---|
| `remotes.develop.json` | `http://localhost:5101` … `5109` | `npm run dev` (desarrollo local con servidores de desarrollo) |
| `remotes.qa.json`, `remotes.staging.json`, `remotes.main.json` | `/mfe/<dominio>/remoteEntry.js`, de mismo origen, **idénticos** | El build de producción |

`vite build` usa el modo `production`, que el shell traduce a `main`: la imagen siempre lee `remotes.main.json`, sin importar en qué ambiente corra. Los de `qa` y `staging` existen para que la regla "el mismo manifest en los 4 ambientes" sea literal. Un test del shell (`deployed-manifest.test.ts`) impone que los tres sean idénticos y de mismo origen.

El `Dockerfile` del shell fija `VITE_REMOTE_SOURCE=federation` en el build. Sin eso, `vite build` empaqueta los stubs de remotes (`vite.config.ts` y `main.tsx` solo federan con ese valor) y la imagen no monta ningún remote.

## Cómo se construyen

Cada repo depende de `file:../design-software-design-system` y `file:../design-software-frontend-platform`, y su `package-lock.json` fija ambos como enlaces a esas carpetas hermanas. El build necesita esos dos repos al lado. Se resuelve con **contextos de build con nombre** de BuildKit (el builder por defecto de Docker 23 o superior): el contexto de cada imagen es su propio repo y los hermanos entran por `--build-context`. No hace falta una carpeta padre común ni copiar `node_modules`.

```bash
# Desde la raíz del repo (shell o cualquier -mfe), con los dos hermanos clonados al lado
docker build \
  --build-context design-system=../design-software-design-system \
  --build-context frontend-platform=../design-software-frontend-platform \
  -t design-software-<dominio>-mfe-static .      # shell: -t design-software-web-shell-static
```

El `Dockerfile` copia de cada hermano solo `package.json` y `src/` (lo único que lee el build) a `/workspace`, y construye el repo en `/workspace/app`, de modo que `../design-software-*` resuelve igual que en la máquina del desarrollador. El `Dockerfile` de los 9 MFE es idéntico; solo `vite.config.ts` conoce el dominio.

Otras formas de pasar el contexto:

- **Compose** (`docker-infra`): `build.additional_contexts`.

  ```yaml
  iam-mfe-static:
    build:
      context: ${FRONTEND_REPOS_DIR}/design-software-iam-mfe
      additional_contexts:
        design-system: ${FRONTEND_REPOS_DIR}/design-software-design-system
        frontend-platform: ${FRONTEND_REPOS_DIR}/design-software-frontend-platform
  ```

- **Git** (reproducible, sin clones al lado; los repos privados piden `GIT_AUTH_TOKEN`):
  `--build-context design-system=https://github.com/code-sena/design-software-design-system.git#develop`.

El ejemplo de compose usa los nombres de servicio que fija la tabla del edge. Esos servicios (`web-shell-static` y los nueve `<dominio>-mfe-static`) están en el `docker-compose.yml` de `docker-infra`, en el perfil `edge`: `docker compose --profile edge --profile <dominio> up -d --build`. `FRONTEND_REPOS_DIR` (default `..`) apunta a la carpeta donde están clonados los repos del frontend, junto con `design-software-design-system` y `design-software-frontend-platform`.

## Verificación local

Sin el stack de backends, con Traefik cargando `traefik/dynamic.yml` y las 10 imágenes en la misma red:

```bash
curl -s  http://localhost:<edge>/                         # HTML del shell
curl -s  http://localhost:<edge>/iam/usuarios             # HTML del shell (fallback)
curl -sI http://localhost:<edge>/mfe/<dominio>/remoteEntry.js   # 200, JavaScript, Cache-Control: no-cache
curl -sI http://localhost:<edge>/mfe/<dominio>/assets/<css>     # 200, text/css, immutable
```

`scripts/edge-smoke.sh` de `docker-infra` repite las tres familias de rutas.

## Límites conocidos

- La imagen del shell sigue la fuente de sesión por defecto del código (`mock` mientras no se defina otra). El login y la sesión reales los resuelve HU-SHELL-010 ([ADR-023](../05-architecture/decisions/records/ADR-023-web-shell-owns-login-and-session.md)); sin sesión, `/login` puede quedar en blanco.
- El shell sigue con el proxy de desarrollo de `vite.config.ts` y con la base de API del código actual. La base de API relativa de los MFE (`/<dominio>/api/v1`) y el proxy único hacia el edge son HU-SHELL-012.
- Publicar las imágenes en un registro (CI) está fuera de esta HU.

## Referencias

- [ADR-022](../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md) §5 y §6: cómo consume el frontend el edge y mismo artefacto en los 4 ambientes.
- [ADR-009](../05-architecture/decisions/records/ADR-009-frontend-framework-and-build-strategy.md): estrategia de build y federación.
- [local-setup.md](./local-setup.md) y [environments.md](./environments.md): bring-up local y puertos por ambiente.
