<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: DDD de flujo UX (Auth) + prompts Stitch
fase: diseño (UX/UI)
estado: draft
dependencias_entrada: 09-microservices/services/01-iam-service/components/iam-api/openapi.yaml; 01-iam-service/data-model.md; 12-ux-ui/design-system.md, navigation-map.md; 04-requirements/user-stories.md
consumidores_siguientes: Google Stitch; validación de diseño
tldr: Pantallas de autenticación y el app shell por rol, derivadas del contrato iam y el modelo de datos, con prompts listos para Stitch.
decisiones_clave: 202 siempre en reset (no revela si el email existe); shell con nav por rol desde /auth/me.features + actor_type (HU-SHELL-019)
halts_registrados: ninguno
-->

# Flujo — Autenticación y App Shell (transversal)

**Servicio origen:** `iam-service` · **Contrato:** `../../../09-microservices/services/01-iam-service/components/iam-api/openapi.yaml`
**Modelo:** `../../../09-microservices/services/01-iam-service/data-model.md`

---

## Pantalla 1 — Login

- **Ruta:** `/login` · **Rol:** anónimo · **HU:** autenticación (HU de acceso)
- **Endpoint:** `POST /api/v1/auth/login` → `TokenResponse { access_token, token_type, expires_in, user{ id, email, full_name, roles[], training_center_id, features[] } }`; el refresh token ya no va en el cuerpo: viaja en la cookie `refresh_token` (`Set-Cookie`, `HttpOnly`; HU-IAM-018, ADR-023 §6)
- **Datos/errores del contrato:** `INVALID_CREDENTIALS` (401), `ACCOUNT_LOCKED` (401), `ACCOUNT_INACTIVE` (401), `RATE_LIMIT_EXCEEDED` (429).
- **MFE:** `iam-mfe` ([micro-frontends.md](../micro-frontends.md))

**Propósito:** autenticar al usuario y llevarlo al espacio de su rol.

**Layout:** columna centrada, marca SENA arriba; card con título "Ingresar", campo **Correo**
(`email`), campo **Contraseña** (`password`, con mostrar/ocultar), enlace "¿Olvidó su contraseña?",
botón primario **Ingresar**. Nota institucional al pie.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Ingresar | `POST /auth/login` | éxito → redirige según `user.roles` (Coordinador→dashboard, etc.); error → mensaje |
| ¿Olvidó su contraseña? | — | navega a `/forgot-password` |

**Estados:** *loading* (botón con spinner, campos bloqueados) · *error* (banner: credenciales
inválidas / cuenta bloqueada / demasiados intentos — texto + icono, no solo color) · *success*
(redirección).

```text
PROMPT STITCH
Pantalla de inicio de sesión para una plataforma web institucional del SENA (Colombia), en español.
Columna centrada sobre fondo claro. Arriba, marca "SENA — Gestión de Horarios" (verde institucional,
placeholder). Tarjeta central con título "Ingresar", un campo "Correo" (email) y un campo "Contraseña"
con icono para mostrar/ocultar, un enlace "¿Olvidó su contraseña?" y un botón primario grande "Ingresar".
Debajo, un banner de error de ejemplo con icono de alerta y texto "Correo o contraseña incorrectos"
(color crítico + icono, no solo color). Estilo sobrio, alto contraste WCAG AA, esquinas suaves,
tipografía sans-serif. Mostrar también el estado de carga (botón con spinner). Responsive (móvil y escritorio).

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Pantalla 2 — Recuperar contraseña

- **Ruta:** `/forgot-password` · **Rol:** anónimo
- **Endpoint:** `POST /api/v1/auth/password-reset/request` → **202 siempre** (no revela si el email existe).
- **MFE:** `iam-mfe` ([micro-frontends.md](../micro-frontends.md))

**Layout:** card con título "Recuperar contraseña", texto explicativo, campo **Correo**, botón
**Enviar enlace**, enlace "Volver a ingresar".

**Estados:** *success* → mensaje neutro "Si el correo existe, enviamos instrucciones" (nunca confirma
existencia) · *loading* · *rate-limit* (429).

```text
PROMPT STITCH
Pantalla "Recuperar contraseña" de la plataforma SENA — Gestión de Horarios, en español. Tarjeta
centrada con título "Recuperar contraseña", un párrafo breve explicativo, un campo "Correo", un botón
primario "Enviar enlace" y un enlace secundario "Volver a ingresar". Mostrar el estado de éxito como un
mensaje neutro: "Si el correo existe, enviaremos instrucciones para restablecer la contraseña". Estilo
institucional, alto contraste WCAG AA, sobrio. Responsive.

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Pantalla 3 — Nueva contraseña (confirmar reset)

- **Ruta:** `/reset-password?token=…` · **Rol:** anónimo
- **Endpoint:** `POST /api/v1/auth/password-reset/confirm { token, new_password }` → 204. Error `RESET_TOKEN_EXPIRED` (400).
- **MFE:** `iam-mfe` ([micro-frontends.md](../micro-frontends.md))

**Layout:** card "Nueva contraseña": campo **Nueva contraseña** (mín 8), campo **Confirmar contraseña**,
indicador de fuerza, botón **Guardar**. Regla de coincidencia visible.

**Estados:** *error* token expirado/usado (400) con opción de solicitar de nuevo · *success* → confirmación + ir a login.

```text
PROMPT STITCH
Pantalla "Nueva contraseña" de la plataforma SENA — Gestión de Horarios, en español. Tarjeta centrada
con título "Definir nueva contraseña", campo "Nueva contraseña" (con medidor de fortaleza), campo
"Confirmar contraseña", texto de requisitos (mínimo 8 caracteres) y botón "Guardar". Incluir el estado
de error "El enlace expiró o ya fue usado" con un botón "Solicitar uno nuevo". Estilo institucional,
alto contraste WCAG AA. Responsive.

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Pantalla 4 — App Shell (marco por rol)

- **Ruta:** `/` (contenedor de todas las áreas autenticadas)
- **Endpoint:** `GET /api/v1/auth/me` → `{ id, email, full_name, actor_type, roles[], features[], modules[] }`.
- **Deriva:** `features[]` + `actor_type` construyen el menú lateral ([visual-spec §4.2](../../visual-spec.md), HU-SHELL-019; `modules[]` queda solo como respaldo, no deriva el menú); el rol determina el área de aterrizaje ([navigation-map.md](../../navigation-map.md)).
- **MFE:** `shell-host` ([micro-frontends.md](../micro-frontends.md)) — marco, sesión, nav y notificaciones (contenedor); sin lógica de dominio.

**Propósito:** marco común (top bar + nav lateral por rol) donde se montan todas las pantallas.

**Layout:**
- **Top bar:** marca SENA · buscador (opcional) · icono de **notificaciones** con badge · menú de
  usuario (nombre, rol, cerrar sesión).
- **Nav lateral (según `features` + `actor_type`):** cada ítem es visible si el usuario tiene alguno de los features requeridos
  y, cuando aplica, el `actor_type` indicado; la tabla de ítems por sección está en [visual-spec §4.2](../../visual-spec.md).
  Ejemplos: Coordinador: Inicio, Horarios, Disponibilidad, Fichas, Seguimiento, Indicadores, Documentos;
  Instructor: Mi horario, Mi disponibilidad, Notificaciones, Fichas (propias);
  Aprendiz: Mi horario, Notificaciones;
  Administrador: Usuarios, Datos de referencia, Parametrización, Auditoría, Indicadores (según features concedidos).
- **Área de contenido** a la derecha.

**Estados:** *loading* (skeleton de nav y top bar) · *sin conexión* (banner offline básico, tolerante a conectividad).

```text
PROMPT STITCH
Marco (app shell) de una aplicación web institucional del SENA — Gestión de Horarios, en español,
responsive. Barra superior con la marca "SENA — Gestión de Horarios" a la izquierda, un icono de
notificaciones con un badge numérico y, a la derecha, un menú de usuario que muestra nombre y rol
("María García — Coordinador") con opción "Cerrar sesión". Navegación lateral izquierda colapsable con
íconos + texto para un Coordinador: "Inicio", "Horarios", "Disponibilidad", "Fichas". Área de contenido
principal a la derecha con un encabezado de página y espacio para tablas/tarjetas. Incluir un banner
sutil de "Sin conexión — mostrando datos guardados" para el estado offline. Estilo sobrio, verde
institucional (placeholder), alto contraste WCAG AA, navegable por teclado. Mostrar variante móvil con
nav lateral como menú hamburguesa.

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Pantalla 5 — Panel de notificaciones (desde la campana del shell)

- **Ruta:** — (overlay/dropdown desde el icono de notificaciones del **top bar**, disponible en
  toda ruta autenticada, montado por el App Shell — Pantalla 4). **Ver todas** navega a la
  pantalla de lista **Notificaciones** del rol (p. ej. `/notificaciones` para Aprendiz, ver
  [flows/04-aprendiz.md — Pantalla 2](../flows/04-aprendiz.md); equivalente en Instructor/Administrador
  vía `shell-host` con capacidades de `notification-service`; el listado completo permanece bloqueado
  hasta que exista el contrato de `GET /notifications`).
- **Rol:** cualquier usuario autenticado · **HU:** pendiente (deriva de `navigation-map.md`, el
  ícono de notificaciones del top bar ya descrito en Pantalla 4).
- **Endpoint:** pendiente de `GET /notifications` en `notification.yaml`; no usar `/sent-notifications`
  de Monitoring. El widget no se implementa hasta formalizar la colección de bandeja y su paginación.
- **Modelo:** `SentNotification { id, generated_alert_id, recipient_id, recipient_email, channel,
  subject, body_summary, send_status, failure_reason, sent_at, created_at }`
  (`monitoring-service data-model.md`). **Nota de precisión:** no existe campo leído/no leído —
  solo `send_status` (`PENDING`/`SENT`/`FAILED`), igual que en la pantalla de lista.
- **MFE:** `shell-host` (contenedor: icono + badge + overlay en el top bar); los datos pertenecen a
  `notification-service`, no a `monitoring-mfe`.

**Propósito:** dar acceso rápido, desde cualquier pantalla, a los avisos más recientes del usuario
(cambios de horario, alertas) sin abandonar el contexto actual, con salida a la bandeja completa.

**Layout:** al hacer clic en el icono de notificaciones (top bar, con **badge** numérico de no
leídas/pendientes) se abre un **dropdown/overlay** anclado bajo el icono: título "Notificaciones",
lista breve de las **últimas 5** (`subject` + `body_summary` truncado a 1 línea + marca de tiempo
relativa + badge de `send_status` con icono, misma convención visual que la pantalla de lista),
y al pie un enlace **"Ver todas"** que cierra el overlay y navega a la pantalla completa de
Notificaciones. Cierra al hacer clic fuera o con `Esc` (navegable por teclado).

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Icono de notificaciones | Pendiente: `GET /notifications?...&limit=5` | no habilitar el dropdown hasta aprobar el contrato |
| Ver todas | — (navegación) | cierra el dropdown → navega a la pantalla de lista Notificaciones (monitoring, pagina por cursor) |
| Clic en una tarjeta del dropdown | Pendiente: `GET /notifications/{id}` | navegará al detalle cuando exista la colección de bandeja |

**Estados:** *loading* (skeleton de 5 filas dentro del overlay) · *empty* ("No tienes
notificaciones nuevas" dentro del overlay, sin lista) · *error* (texto inline + icono "No pudimos
cargar tus notificaciones" con botón "Reintentar", el overlay permanece abierto) · *badge* (número
de notificaciones `PENDING`/recientes sin abrir; oculto si es cero — nunca "0" visible).

```text
PROMPT STITCH
Panel desplegable de notificaciones para la plataforma SENA — Gestión de Horarios, en español.
Mostrar el marco superior (top bar) con la marca a la izquierda y, a la derecha, el icono de
campana de notificaciones con un badge numérico rojo pequeño (ejemplo "3"), del cual cae un
panel/dropdown anclado justo debajo del icono. El panel tiene un título "Notificaciones" y una
lista breve de 5 tarjetas compactas, cada una con: asunto en negrita (ej. "Cambio en tu horario:
sesión del jueves cancelada"), una línea de resumen truncada, una marca de tiempo relativa a la
derecha ("hace 2 h") y un badge pequeño de estado de entrega con icono (mayoría "Enviado" en tono
discreto de éxito, una de ejemplo "No se pudo entregar" en rojo/crítico con icono de alerta). Al
pie del panel, un enlace centrado "Ver todas". Incluir también, como variante aparte en el mismo
lienzo, el estado vacío del panel ("No tienes notificaciones nuevas") y el estado de carga
(skeleton de 5 filas). Estilo sobrio, esquinas suaves, sombra de overlay, alto contraste WCAG AA,
navegable por teclado (foco visible, cierre con Esc). Responsive (variante desktop con el panel
anclado al icono, variante móvil a pantalla casi completa deslizada desde arriba).

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

> **Sin paginador:** es un **widget top N** (no una pantalla de lista) — anti-patrón #3 de
> [README.md](../README.md) exige "top N · Ver todos" sin paginador, cumplido aquí. La pantalla
> de lista completa (con paginación real por cursor) ya está documentada en
> `flows/04-aprendiz.md` — Pantalla 2 y se reutiliza (misma convención) en Instructor/Administrador.

---

## Pantalla 6 — Estados globales / páginas de sistema

- **Ruta:** transversal — se renderiza en lugar del área de contenido del App Shell (Pantalla 4)
  cuando aplica; no tiene una ruta propia (excepto la redirección final a `/login` en el caso de
  sesión expirada). **Rol:** cualquier usuario (autenticado o cuya sesión acaba de expirar).
  **HU:** pendiente (manejo transversal de errores, no ligado a una HU de negocio específica).
- **Endpoint(s) que disparan cada variante:** cualquier endpoint autenticado del sistema puede
  devolver `403` (`_shared.yaml#/components/responses/Forbidden` — feature/scope RBAC
  insuficiente) o `404` (`_shared.yaml#/components/responses/NotFound` — recurso inexistente o
  fuera de scope); un **500/error genérico** no está tipado explícitamente en los contratos (no
  hay `responses/InternalServerError` en `_shared.yaml`) y se documenta como estado transversal de
  fallo de servidor/red, mostrando `error.trace_id` (`_shared.yaml#/components/schemas/Error`)
  cuando el backend lo entrega, para soporte. **Sesión expirada:** se dispara cuando
  `POST /api/v1/auth/refresh` (`iam.yaml`) también responde `401` (refresh_token vencido o
  revocado) — el shell limpia la sesión local y redirige a `/login`.
- **Modelo:** `Error { error: { code, message, details[], trace_id } }`
  (`_shared.yaml#/components/schemas/Error`) — mismo esquema que ya usan los errores 400/401/403/
  404/409/422 de todos los contratos; esta pantalla no inventa campos adicionales, solo los
  presenta a página completa en vez de como banner inline.
- **MFE:** `shell-host` ([micro-frontends.md](../micro-frontends.md)) — páginas de error/offline
  son responsabilidad del contenedor, no de un MFE de dominio.

**Propósito:** dar una respuesta consistente y navegable cuando el flujo normal no puede
continuar (permiso insuficiente, recurso inexistente, fallo del servidor o sesión vencida), sin
dejar al usuario en una pantalla en blanco ni con un stack trace.

**Layout (marco común, dentro del App Shell salvo donde se indique):** ilustración/ícono grande
central, código/título corto, un párrafo explicativo en español simple (nunca expone `message`
técnico crudo del backend — se traduce a lenguaje de usuario; `trace_id` se muestra solo como
texto pequeño "Código de referencia: …" para soporte), y **un botón primario de recuperación**
(varía por variante, ver abajo). Se conserva el top bar del shell en 403/404/500 (el usuario sigue
autenticado y puede navegar); **no** se conserva en "Sesión expirada" (no hay sesión válida).

**Estados (las 4 variantes — misma pantalla, sin fragmentar):**
- **403 — Sin permiso:** título "No tienes permiso para ver esto", texto "Tu rol no tiene acceso a
  esta sección." (deriva de `error.code`, p. ej. `FORBIDDEN`/scope insuficiente), botón primario
  "Volver al inicio" (→ `/`, área de aterrizaje del rol).
- **404 — No encontrado:** título "No encontramos esta página", texto "El recurso que buscas no
  existe o ya no está disponible.", botón primario "Volver al inicio" (→ `/`).
- **500 / Error:** título "Algo salió mal de nuestro lado", texto "Ocurrió un error inesperado.
  Intenta de nuevo en unos minutos.", botón primario "Reintentar" (repite la última acción/carga)
  y enlace secundario "Volver al inicio"; muestra "Código de referencia: {trace_id}" si el backend
  lo entrega.
- **Sesión expirada:** título "Tu sesión expiró", texto "Por seguridad, cerramos tu sesión.
  Ingresa de nuevo para continuar.", sin top bar ni nav; **redirección automática** a `/login`
  tras una breve pausa (o botón primario inmediato "Ir a iniciar sesión" si el usuario prefiere no
  esperar) — reutiliza la Pantalla 1 (Login) de este mismo flujo, sin duplicar su UI aquí.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Volver al inicio (403/404) | — (navegación) | redirige a `/` (App Shell, área del rol) |
| Reintentar (500) | repite el endpoint que falló | vuelve a solicitar los datos de la pantalla origen |
| Ir a iniciar sesión / redirección automática (sesión expirada) | — (navegación) | limpia tokens locales y navega a `/login` (Pantalla 1) |

```text
PROMPT STITCH
Conjunto de páginas de estado/error de sistema para la plataforma SENA — Gestión de Horarios, en
español, dentro del mismo lienzo mostrado como 4 variantes lado a lado (o en pestañas), cada una
centrada verticalmente con un ícono/ilustración simple arriba, un título corto y un párrafo breve
debajo:
1) "403 — Sin permiso": ícono de candado/escudo, título "No tienes permiso para ver esto", texto
"Tu rol no tiene acceso a esta sección.", botón primario "Volver al inicio". Conserva la barra
superior con marca y menú de usuario (el usuario sigue autenticado).
2) "404 — No encontrado": ícono de brújula/lupa, título "No encontramos esta página", texto "El
recurso que buscas no existe o ya no está disponible.", botón primario "Volver al inicio". Conserva
la barra superior.
3) "500 — Error del servidor": ícono de alerta/nube con signo de exclamación, título "Algo salió
mal de nuestro lado", texto "Ocurrió un error inesperado. Intenta de nuevo en unos minutos.", botón
primario "Reintentar" y enlace secundario "Volver al inicio", con un texto pequeño gris "Código de
referencia: 7f3a-91c2" de ejemplo. Conserva la barra superior.
4) "Sesión expirada": SIN barra superior (pantalla anónima), ícono de reloj/candado, título "Tu
sesión expiró", texto "Por seguridad, cerramos tu sesión. Ingresa de nuevo para continuar.", botón
primario "Ir a iniciar sesión". Estilo sobrio, verde institucional (placeholder) para los botones
primarios, colores semánticos de advertencia/crítico para los íconos de 403/500 (icono + texto,
nunca solo color), alto contraste WCAG AA, tipografía sans-serif, responsive (desktop y móvil para
cada una de las 4 variantes).

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Mockups generados
_(pendiente — guardar en `../mockups/01-auth/` y enlazar aquí: login.png, forgot.png, reset.png,
shell.png, notificaciones-panel.png, estados-sistema.png)_
