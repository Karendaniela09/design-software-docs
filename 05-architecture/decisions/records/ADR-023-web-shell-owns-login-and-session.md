# ADR-023: El web-shell es dueño del login y de la sesión

**Estado:** ACCEPTED (2026-10-24)
**Fecha:** 2026-10-24
**Autores:** Jesús Ariel González Bonilla (PM + Arquitecto)
**Equipos involucrados:** Arquitectura, Frontend, IAM

> Es la decisión **D2** de la ruta de cierre. Se apoya en [ADR-022](./ADR-022-edge-routing-table-by-domain.md) para las rutas y en [`07-api/authentication.md`](../../../07-api/authentication.md) para tokens y almacenamiento.

---

## Contexto

- **`develop` no tiene login.** Sin sesión, `/login` del shell queda en blanco. Al levantarlo en local (2026-10-24), la única forma de entrar fue inyectar a mano un token real en `sessionStorage['sena.access_token']`. Sin login, ningún QA puede usar un ambiente desplegado y ningún micro con MFE puede probarse de punta a punta desde el navegador.
- **El primer `/auth/me` tarda unos 5 s** con la JVM en frío, y el shell muestra "Cargando sesión…" sin timeout ni aviso.
- **Hay tres PR abiertos que tocan el login:**
  - `web-shell#17` + `frontend-platform#8` (HU `docs#250`): pantalla de login en el shell, ciclo de sesión real con IAM y cliente HTTP autenticado inyectado al remote de reference-data. Tienen CI verde en su rama, pero #17 está en conflicto.
  - `iam-mfe#10`: alinea el adaptador de autenticación del MFE al contrato de IAM y entrega la sesión al host por callback. El propio PR aclara que "el shell sigue siendo responsable de administrar la sesión".
  - Además, en `/iam/usuarios`, el iam-mfe de `develop` muestra su propia pantalla de login.
- **Reglas ya vigentes:**
  - [ADR-009](./ADR-009-frontend-framework-and-build-strategy.md): `frontend-platform` es la fachada única sobre `fetch` y el almacenamiento; ningún MFE los toca directo. Además, un remote caído no puede tumbar el shell.
  - [`authentication.md`](../../../07-api/authentication.md): `access_token` de 15 min **en memoria** y `refresh_token` de 7 días **en cookie `HttpOnly` (`Secure`, `SameSite=Strict`)**.
  - [ADR-018](./ADR-018-iam-session-revocation-r4.md): `/auth/me` valida contra la sesión persistida.
  - El contrato `remote-props.ts` de `frontend-platform`: hoy el shell solo envía `basePath`.

## Decisión

Se decide que **el web-shell es dueño del login y de la sesión**, y que los remotes la consumen sin gestionarla.

1. **La pantalla `/login` vive en el web-shell**, fuera de `AppShell`. Funciona aunque ningún remote esté disponible: la entrada al sistema no puede depender de que un MFE cargue.
2. **`frontend-platform` implementa el cliente de sesión** (login, refresh, logout, me) y el cliente HTTP autenticado. Es la única pieza que lee o escribe el token.
3. **Los remotes no hacen login ni leen el token.** Reciben del shell, por el contrato `remote-props`, el cliente HTTP autenticado y la identidad y permisos de la sesión. **iam-mfe se limita a administrar identidad** (usuarios, roles, sesiones activas) y su pantalla de login se retira.
4. **El shell llama a IAM por el edge** (ADR-022): `POST /iam/api/v1/auth/login`, `POST /iam/api/v1/auth/refresh`, `POST /iam/api/v1/auth/logout` y `GET /iam/api/v1/auth/me`.
5. **Ciclo de vida:**
   - Al cargar la app: un `POST /auth/refresh` silencioso, que el navegador acompaña con la cookie. Si responde 200, hay sesión; si responde 401, se va a `/login`.
   - Sin sesión: redirige a `/login` y, tras entrar, vuelve a la ruta pedida.
   - `401 TOKEN_EXPIRED`: un solo intento de refresh; si falla, limpia la sesión y vuelve a `/login`.
   - Logout: `POST /auth/logout`, que revoca la sesión y borra la cookie, más la limpieza local.
   - `/auth/me` con timeout (del orden de 10 s), y al vencer muestra un error con reintento en vez de "Cargando sesión…" indefinido.
6. **Almacenamiento, igual en los 4 ambientes desde `develop`:**
   - **Access token en memoria**, dentro de `frontend-platform`. No se guarda en `sessionStorage` ni en `localStorage`.
   - **Refresh token en cookie `HttpOnly`, `Secure`, `SameSite=Strict`, con `Path=/iam/api/v1/auth`**, emitida por iam-service en `login` y en `refresh`. `refresh` y `logout` la leen. El `refresh_token` deja de viajar en el cuerpo de la respuesta: es un cambio de contrato en `iam.yaml` que entra con la HU de iam-service.
   - El edge da origen único ([ADR-022](./ADR-022-edge-routing-table-by-domain.md)), así que la cookie es de primera parte y `SameSite=Strict` no estorba.
   - `Secure` exige HTTPS en todo ambiente desplegado, DEV incluido. En local funciona porque los navegadores tratan `http://localhost` como contexto seguro.
7. **El mismo código en todos los ambientes.** No hay comportamiento por ambiente: lo único que cambia entre `develop`, `qa`, `staging` y `main` son los datos (sintéticos en `develop` y `qa`) y los valores que inyecta cada ambiente (dominio, secretos).
8. **Implementación candidata:** `web-shell#17` + `frontend-platform#8`, sujetos a su revisión, al rebase sobre `develop` y a ajustarse a esta decisión: hoy guardan el token en `sessionStorage` y eso hay que cambiarlo. `iam-mfe#10` se acota a administración de identidad, sin login propio.

## Consecuencias

### Positivas

- Un único dueño de la sesión. El token no se reparte por 9 MFE.
- El login sigue funcionando con remotes caídos (resiliencia de ADR-009).
- Ningún token queda en un almacenamiento legible por JavaScript, y recargar la página no saca al usuario.
- Lo que se prueba en `develop` y `qa` es exactamente lo que llega a `staging` y `main`: no hay ramas de comportamiento por ambiente.

### Negativas / Trade-offs

- `remote-props` crece: cliente HTTP, identidad y permisos pasan a ser props estándar para los 9 remotes.
- iam-mfe pierde su pantalla de login y hay que retirarla.
- **El login depende primero de un cambio en iam-service:** emitir la cookie en `login` y `refresh`, leerla en `refresh` y `logout`, y sacar el `refresh_token` del cuerpo. Esa HU va antes que la del login del shell.
- Todo ambiente desplegado necesita TLS desde el primer día, DEV incluido.

### Riesgos

- **Cambio de contrato en `/auth/login` y `/auth/refresh`.** Hoy ningún cliente de `develop` consume el `refresh_token` del cuerpo (el shell no tiene login), así que el impacto es bajo. Igual se registra en `iam.yaml` y en `shared-contracts`.
- **Una cookie mal acotada** (sin `Path` o sin `Secure`) expone el refresh token a más rutas de las necesarias. Mitigación: prueba de integración de la cabecera `Set-Cookie` en iam-service.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Login dentro de iam-mfe, montado por el shell | La entrada al sistema dependería de que un remote cargue. Si iam-mfe falla, nadie entra. |
| Cada MFE autentica por su cuenta | Duplica lógica y reparte el token por 9 repos, contra la fachada de ADR-009. |
| Sesión en el BFF (cookie de sesión; el token nunca llega al navegador) | Es la opción más segura, pero `web-bff` es un esqueleto. Queda como evolución después de v1. |

## Referencias

- [ADR-009](./ADR-009-frontend-framework-and-build-strategy.md) · [ADR-018](./ADR-018-iam-session-revocation-r4.md) · [ADR-022](./ADR-022-edge-routing-table-by-domain.md)
- [`07-api/authentication.md`](../../../07-api/authentication.md) · [`07-api/contracts/openapi/iam.yaml`](../../../07-api/contracts/openapi/iam.yaml)
- PR candidatos: `code-sena/design-software-web-shell#17`, `code-sena/design-software-frontend-platform#8`, `code-sena/design-software-iam-mfe#10`.
