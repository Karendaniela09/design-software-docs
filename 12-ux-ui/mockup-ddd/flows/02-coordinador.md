<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: DDD de flujo UX (Coordinador Académico, rol CORE del MVP) + prompts Stitch
fase: diseño (UX/UI)
estado: draft
dependencias_entrada: 07-api/contracts/openapi/{scheduling,training-environment,academic-management,actors}.yaml; data-model.md de scheduling/training-environment/academic-management-service; 12-ux-ui/{design-system,navigation-map}.md; 04-requirements/{functional,user-stories}.md
consumidores_siguientes: Google Stitch (generación de mockup); validación de diseño con coordinadores reales
tldr: 12 pantallas/modales del Coordinador Académico (Dashboard, Horarios, Detalle de horario, Crear/editar horario, Modal Agregar/editar sesión, Modal Confirmar publicación, Panel de conflictos, Modal Resolver conflicto, Disponibilidad, Detalle de ambiente, Fichas, Detalle de ficha) derivadas de los contratos y data-models reales de scheduling (CORE), training-environment, academic-management y actors; cada pantalla declara su MFE dueño (ver `../micro-frontends.md`); el conflicto es ciudadano de primera clase en Dashboard y en pantalla propia.
decisiones_clave: `GET /schedules` no filtra por instructor/ambiente (limitación real del contrato — esos atributos viven en `class_session`, no en `schedule`); no existe `GET /instructors/available` en el contrato — Disponibilidad de instructores se compone cruzando `GET /instructors` con `GET /instructors/{id}/availability-exceptions`; `scheduling_conflict.conflict_type` real solo tiene 3 valores (el contrato no incluye `ENVIRONMENT_MAINTENANCE`/`INSTRUCTOR_UNAVAILABLE` que sí menciona functional.md); `resolveConflict` no acepta body (sin `resolution_notes`); `SessionUpdate` no permite cambiar `competency_id`/`session_date` (solo alta); no hay endpoint de "ocupación por franja" desglosada — se compone cruzando `availability-rules` + `sessions` + el agregado real de `reports/environment-occupancy`
halts_registrados: ninguno
-->

# Flujo — Coordinador Académico (núcleo MVP)

> **ESTADO: PRELIMINAR (v0)** — instrumento de descubrimiento y feedback, no diseño final. Cada
> pantalla está trazada a `endpoint + tabla` real (100%); la trazabilidad a `HU` se cita donde
> existe y se marca `HU: pendiente` donde no.

**Servicio origen (CORE):** `scheduling-service` · **Contrato:** `../../../07-api/contracts/openapi/scheduling.yaml`
**Modelo:** `../../../09-microservices/services/05-scheduling-service/data-model.md`

**Servicios de apoyo** (consultados por el Coordinador, no editados desde este flujo salvo donde se indique):
- `academic-management-service` — fichas y programa. Contrato: `../../../07-api/contracts/openapi/academic-management.yaml` · Modelo: `../../../09-microservices/services/03-academic-management-service/data-model.md`
- `training-environment-service` — ambientes. Contrato: `../../../07-api/contracts/openapi/training-environment.yaml` · Modelo: `../../../09-microservices/services/04-training-environment-service/data-model.md`
- `actors-service` — instructores. Contrato: `../../../07-api/contracts/openapi/actors.yaml` (schema `actors_parameterization`)

---

## Pantalla 1 — Dashboard / Inicio

- **Ruta:** `/` (Inicio del Coordinador) · **Rol:** Coordinador Académico (`COORDINATOR`, scope `TRAINING_CENTER`) · **HU:** pendiente (agrega datos de HU-01, HU-07, HU-09; el dashboard como tal no tiene HU dedicada)
- **MFE:** `shell-host` (marco + nav + saludo) compone widgets de `scheduling-mfe` (sección "Conflictos pendientes" + widget "Horarios en borrador") y `academic-mfe` (KPI "Fichas activas"); ver `../micro-frontends.md`.
- **Endpoints:**
  - `GET /fichas` (`listFichas`, academic-management.yaml) — filtros `training_center_id`, `status=EXECUTION`
  - `GET /schedules` (`listSchedules`, scheduling.yaml) — filtro `status=DRAFT`
  - `GET /reports/schedule-conflicts` (`reportScheduleConflicts`, scheduling.yaml) — filtro `is_resolved=false`, paginación por cursor (`cursor`/`limit`)
- **Tablas/campos reales:** `enrollment_ficha.status`; `schedule.{ficha_id, period, name, status, updated_at}`; `scheduling_conflict.{schedule_id, conflict_type, description, detected_at, is_resolved}`

**Propósito:** vista de aterrizaje que resume el estado operativo del centro y prioriza los
conflictos sin resolver, para que el coordinador actúe primero sobre lo crítico.

**Layout (revisado v2 — sin redundancia):**
1. **Header** "Inicio" + saludo breve (`user.full_name`) + **un único** botón primario "Crear horario" (arriba a la derecha).
2. **Sección destacada de CONFLICTOS (única representación):** banda ancha "Conflictos pendientes (N)"
   en color crítico + icono; lista los **top 3** conflictos (`conflict_type` con icono, `schedule_id`
   [referencia], `detected_at`, enlace "Ver panel"); pie **"mostrando 3 de N · Ver todos"** → Panel
   (Pantalla 7). Si `N=0` → estado positivo "Sin conflictos pendientes" (check verde). **No** existe,
   además, una tarjeta KPI de conflictos (se elimina la duplicación de v1).
3. **Fila de 2 tarjetas KPI** (solo conteo, nunca conflictos): **Fichas activas** (`enrollment_ficha`
   `status=EXECUTION`) y **Horarios en borrador** (`schedule` `status=DRAFT`); cada tarjeta con **un
   solo** enlace "Ver todos".
4. **Widget "Horarios recientes en borrador":** top 3–5 filas (`ficha_id` [ref], `period`, `name`,
   `updated_at`, "Continuar edición") + pie **"mostrando X de N · Ver todos"**.
5. **Sin** fila inferior de accesos directos (las acciones ya están en la nav lateral + botón "Crear horario"). El rol/usuario **solo** en el menú superior.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Tarjeta / fila "Conflictos pendientes" | `GET /reports/schedule-conflicts?is_resolved=false` | navega al Panel de conflictos (Pantalla 7) |
| Tarjeta / fila "Horarios en borrador" | `GET /schedules?status=DRAFT` | navega a Crear/editar horario (Pantalla 4) con el `id` seleccionado |
| Tarjeta "Fichas activas" | `GET /fichas?status=EXECUTION` | navega a Fichas (Pantalla 11) |

**Estados:** *loading* (skeleton en las 3 tarjetas KPI y en ambas listas, independientes entre sí)
· *empty* (sin conflictos: mensaje positivo "Sin conflictos pendientes" con icono de éxito; sin
borradores: "No hay horarios en borrador") · *error* (banner de reintento por widget, no bloquea
los demás) · *conflicto* (la tarjeta de conflictos siempre usa icono + texto + color crítico, y se
adelanta en el orden visual cuando `count > 0`, conforme al principio "el conflicto es ciudadano
de primera clase").

```text
PROMPT STITCH
Pantalla "Inicio" del Coordinador Académico en la plataforma SENA — Gestión de Horarios, en español,
dentro del app shell (barra superior con marca + campana de notificaciones + menú de usuario que
muestra nombre y rol; nav lateral: Inicio, Horarios, Ambientes, Fichas). Encabezado "Inicio" con
saludo breve "Hola, María García" y UN solo botón primario arriba a la derecha: "Crear horario".

Orden vertical, con UNA sola representación de cada cosa (no duplicar nada):
1) Sección destacada "Conflictos pendientes (4)" en color crítico con icono de alerta: lista los 3
   conflictos más recientes; cada fila con un icono según el tipo (instructor doble-asignado /
   ambiente doble-asignado / sesiones solapadas), el horario afectado, la fecha y un enlace "Ver
   panel". Al pie: "Mostrando 3 de 4 · Ver todos". Es la ÚNICA parte que muestra conflictos: NO crear
   además una tarjeta KPI de conflictos.
2) Fila con SOLO 2 tarjetas KPI de conteo: "Fichas activas: 12" y "Horarios en borrador: 3", cada una
   con un único enlace "Ver todos".
3) Sección "Horarios recientes en borrador": tabla breve de 3 filas (ficha, período, nombre, última
   edición, botón "Continuar edición"), con pie "Mostrando 3 de 3 · Ver todos".

Reglas estrictas: NO agregar una fila inferior de accesos directos ni repetir botones que ya estén en
la nav lateral o en las tarjetas (una sola vez cada acción). El nombre y el rol del usuario van SOLO
en el menú superior, no en el sidebar ni en el saludo. Los números deben ser coherentes con las
listas (si el contador dice 4, o se muestran 4 o el pie dice "Mostrando 3 de 4"). Estado vacío de
conflictos: mensaje positivo con check verde "Sin conflictos pendientes". Estilo institucional sobrio,
alto contraste WCAG AA, sombras sutiles, densidad moderada sin sobrecargar. Responsive: en móvil todo
se apila y la sección de conflictos queda primero.

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

**Mockup:** _(pendiente — se guardará en `../mockups/02-coordinador/dashboard.png` y se enlazará aquí)_

---

## Pantalla 2 — Horarios (lista)

- **Ruta:** `/horarios` · **Rol:** Coordinador Académico · **HU:** pendiente (soporta HU-07 a HU-10 como punto de entrada)
- **MFE:** `scheduling-mfe`
- **Endpoint:** `GET /schedules` (`listSchedules`, scheduling.yaml)
- **Filtros reales del contrato:** `ficha_id` (uuid, referencia externa a `enrollment_ficha.id`), `period` (string ≤10, ej. `2026-1`), `status` (enum `DRAFT`/`UNDER_REVIEW`/`PUBLISHED`/`ARCHIVED`), `from`/`to` (rango de `created_at`) — más `page`/`page_size`/`sort` estándar.
- **Tabla/campos reales:** `schedule.{id, ficha_id, period, name, status, published_at, row_version, created_by, created_at, updated_at}`

> **Nota de congruencia (no se inventa):** el contrato de `GET /schedules` **no expone** filtro por
> `instructor_id` ni `environment_id` — esos son atributos de `class_session` (nivel sesión), no de
> `schedule` (nivel agregado). El filtro por instructor/ambiente existe en `GET /sessions` (ver
> Pantalla 4). Esta pantalla implementa los filtros reales: ficha, período, estado y rango de
> fecha; el filtro "por instructor/ambiente" pedido en la navegación se resuelve navegando a la
> sesión concreta desde el Panel de conflictos o desde Disponibilidad, no desde esta lista.

**Propósito:** punto de entrada para ubicar, continuar o revisar cualquier horario del centro por
ficha, período o estado.

**Layout:** header "Horarios" + botón primario "Nuevo horario"; barra de filtros (selector de
ficha con búsqueda, campo período, selector de estado, rango de fechas); tabla densa con columnas
**Ficha** (referencia `ficha_id`, muestra número si el cliente lo resuelve contra
academic-management-service), **Período**, **Nombre**, **Estado** (badge icono+texto: BORRADOR
neutro / EN_REVISIÓN advertencia / PUBLICADO éxito / ARCHIVADO neutro atenuado), **Publicado el**
(`published_at`, si aplica), **Última actualización** (`updated_at`); pie de tabla con
**paginación REAL y visible** — barra ‹ anterior · 1 2 3 … › siguiente, **selector de tamaño de
página** (`page_size`: 10/20/50) y texto **"Mostrando X–Y de N"** — alineada a los parámetros
`page`/`page_size` de `GET /schedules`; orden (`sort`). Nunca una tabla infinita sin control.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Fila → "Ver" (`status` `DRAFT`/`UNDER_REVIEW`) | `GET /schedules/{id}` | abre Crear/editar horario (Pantalla 4) |
| Fila → "Ver" (`status` `PUBLISHED`/`ARCHIVED`) | `GET /schedules/{id}` | abre Detalle de horario, solo lectura (Pantalla 3) |
| Botón "Nuevo horario" | — (la creación real dispara `POST /schedules` en Pantalla 4) | abre Pantalla 4 en modo alta |
| Filtros (ficha/período/estado/fecha) | `GET /schedules?ficha_id=&period=&status=&from=&to=` | refresca la tabla |
| Paginación / orden | `GET /schedules?page=&page_size=&sort=` | cambia de página |

**Estados:** *loading* (skeleton de filas) · *empty* ("No hay horarios que coincidan con los
filtros" + botón "Nuevo horario") · *error* (banner + reintentar) · el badge de estado siempre usa
icono + texto (no solo color), incluyendo un indicador adicional si el horario `UNDER_REVIEW` tiene
conflictos activos (icono de alerta junto al badge).

```text
PROMPT STITCH
Pantalla "Horarios" del Coordinador Académico, plataforma SENA — Gestión de Horarios, en español,
dentro del app shell. Encabezado "Horarios" con botón primario "Nuevo horario" a la derecha. Barra
de filtros con: selector "Ficha" (buscable), campo "Período" (ej. 2026-1), selector "Estado"
(Borrador / En revisión / Publicado / Archivado), y un rango de fechas. Tabla densa con columnas:
Ficha, Período, Nombre, Estado (badge con icono + texto — círculo gris "Borrador", triángulo
ámbar "En revisión", check verde "Publicado", candado gris "Archivado"), Publicado el, Última
actualización. Al pie de la tabla, una barra de paginación REAL y visible: "‹ anterior · 1 2 3 …
siguiente ›", un selector de tamaño de página ("10 / 20 / 50 por página") y el texto "Mostrando
1–20 de 87". Mostrar el estado vacío con un icono de calendario y el texto "No hay horarios que
coincidan con los filtros". Estilo institucional, alto contraste WCAG AA, filas con hover sutil,
objetivos táctiles ≥44px. Responsive: en móvil la tabla colapsa a tarjetas apiladas por horario, con
la misma barra de paginación al final del listado.

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

**Mockup:** _(pendiente — `../mockups/02-coordinador/horarios-lista.png`)_

---

## Pantalla 3 — Detalle de horario (solo lectura)

- **Ruta:** `/horarios/:id` — mismo recurso que la edición; el cliente decide el modo de render
  según `schedule.status`: `DRAFT`/`UNDER_REVIEW` → Pantalla 4 (editable), `PUBLISHED`/`ARCHIVED` →
  esta pantalla · **Rol:** Coordinador Académico · **HU:** pendiente (vista de lectura derivada de
  HU-07/HU-08/HU-10; no tiene HU dedicada)
- **MFE:** `scheduling-mfe`
- **Endpoints:**
  - `GET /schedules/{id}` (`getSchedule`, scheduling.yaml)
  - `GET /schedules/{id}/sessions` (`listScheduleSessions`) — filtro `status` (`ACTIVE`/`CANCELLED`); `page`/`page_size`/`sort`
- **Tabla/campos reales:** `schedule.{id, ficha_id, period, name, status, published_at, published_by, row_version}`; `class_session.{id, competency_id, environment_id, instructor_id, time_slot_id, session_date, day_of_week, start_time, end_time, status, notes}`

**Propósito:** consultar un horario que ya no es editable (`PUBLISHED`/`ARCHIVED`) — su definición
completa de sesiones — sin exponer ninguna acción de mutación.

**Layout:** header con `ficha_id` (referencia), `period`, `name`, badge de `status` (PUBLICADO
éxito / ARCHIVADO neutro atenuado) y, si `PUBLISHED`, `published_at`/`published_by`; tabla de
sesiones **sin columna de acciones** (mismas columnas que Pantalla 4: Día, Franja, Fecha,
Competencia, Instructor, Ambiente, Estado) con **paginación REAL y visible** (barra ‹ anterior · 1
2 3 … › siguiente, selector de tamaño de página `page_size`: 10/20/50, "Mostrando X–Y de N")
alineada a `GET /schedules/{id}/sessions`; enlace "Ver conflictos (histórico)" hacia el Panel de
conflictos (Pantalla 7, filtrado por este `schedule_id`, sin filtro de `is_resolved` para ver
también los ya resueltos); botón "Volver a Horarios".

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Cargar sesiones | `GET /schedules/{id}/sessions?status=&page=&page_size=&sort=` | pobla/pagina la tabla |
| "Ver conflictos (histórico)" | navega a Panel de conflictos (Pantalla 7) con `schedule_id` fijo | — |
| "Volver a Horarios" | — | navega a Pantalla 2 |

**Estados:** *loading* (skeleton en header y tabla) · *empty* (`ARCHIVED` sin sesiones activas:
"Este horario no tiene sesiones activas") · *error* (banner + reintentar). No aplica estado
*conflicto*: por contrato, `publish` exige cero conflictos sin resolver, de modo que un horario
`PUBLISHED` nunca los tiene (los `ARCHIVED` pudieron tenerlos resueltos, visibles solo en el
histórico del Panel de conflictos).

```text
PROMPT STITCH
Pantalla "Detalle de horario" (solo lectura) del Coordinador Académico, plataforma SENA — Gestión
de Horarios, en español, dentro del app shell. Encabezado "Ficha 2589341 — Período 2026-1" con un
badge de estado "Publicado" (icono check verde) y el texto "Publicado el 15 ene 2026 por María
García". NO mostrar ningún botón de edición (nada de "Guardar", "Agregar sesión", "Publicar"): esta
pantalla es de solo consulta. Debajo, una tabla de sesiones de solo lectura con columnas: Día,
Franja horaria, Fecha, Competencia, Instructor, Ambiente, Estado (sin columna de acciones). Al pie
de la tabla, una barra de paginación REAL y visible: "‹ anterior · 1 2 3 · siguiente ›", selector de
tamaño de página ("10 / 20 / 50 por página") y "Mostrando 1–20 de 32". Sobre la tabla, un botón
secundario "Ver conflictos (histórico)" y, en la esquina superior izquierda, un enlace "‹ Volver a
Horarios". Estilo institucional, alto contraste WCAG AA. Responsive: en móvil la tabla colapsa a
tarjetas apiladas por sesión, con la misma barra de paginación al final.

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

**Mockup:** _(pendiente — `../mockups/02-coordinador/horario-detalle.png`)_

---

## Pantalla 4 — Crear / editar horario

- **Ruta:** `/horarios/nuevo` (alta) y `/horarios/:id` (edición, solo `DRAFT`/`UNDER_REVIEW`) · **Rol:** Coordinador Académico · **HU:** HU-07 (crear borrador), HU-08 (agregar sesiones), HU-10 (publicar)
- **MFE:** `scheduling-mfe`
- **Endpoints:**
  - `POST /schedules` (`createSchedule`) — body `ScheduleCreate{ficha_id, period, name?}` → `201` `DRAFT`
  - `GET /schedules/{id}` (`getSchedule`) / `PUT /schedules/{id}` (`updateSchedule`) — body `{name?, row_version}`
  - `GET /schedules/{id}/sessions` (`listScheduleSessions`) — filtro `status` (`ACTIVE`/`CANCELLED`)
  - `POST /schedules/{id}/sessions` (`addScheduleSession`) — body `SessionCreate{competency_id, environment_id, instructor_id, time_slot_id, session_date, notes?}`
  - `PUT /sessions/{id}` (`updateSession`) — body `{instructor_id?, environment_id?, time_slot_id?, notes?}` · `DELETE /sessions/{id}` (`deleteSession`) · `POST /sessions/{id}/cancel` (`cancelSession`)
  - `POST /schedules/{id}/validate` (`validateSchedule`) — body `{row_version}` → `DRAFT → UNDER_REVIEW`
  - `POST /schedules/{id}/publish` (`publishSchedule`) — body `{row_version}` → `UNDER_REVIEW → PUBLISHED`
- **Tabla/campos reales:** `schedule.{ficha_id, period, name, status, row_version}`; `class_session.{id, competency_id, environment_id, instructor_id, time_slot_id, session_date, day_of_week, start_time, end_time, status, notes}` (`day_of_week`/`start_time`/`end_time` son copia desnormalizada e inmutable de `time_slot`)

**Propósito:** construir el horario de una ficha agregando sesiones y llevarlo, sin conflictos,
hasta la publicación.

**Layout:** header con `ficha_id` (referencia), `period`, `name` (editable) y badge de `status`;
tabla de sesiones (columnas: **Día** [`day_of_week`, 1=lunes…7=domingo], **Franja**
[`time_slot`/`start_time`–`end_time`], **Fecha** [`session_date`], **Competencia**
[`competency_id`, ref. academic-management-service], **Instructor** [`instructor_id`, ref.
actors-service], **Ambiente** [`environment_id`, ref. training-environment-service], **Estado**
[`ACTIVE`/`CANCELLED`]) con acciones editar/cancelar/eliminar por fila; botón "Agregar sesión" que
abre el **Modal: Agregar/editar sesión** (Pantalla 5); barra de acciones inferior fija: "Guardar",
"Validar", "Publicar" (este último abre el **Modal: Confirmar publicación**, Pantalla 6).

> **Flujo real derivado del contrato (no inventado):** agregar/editar/eliminar sesiones solo se
> permite mientras `schedule.status = DRAFT` (`409 SCHEDULE_IMMUTABLE` en otro caso). `Validar`
> transiciona `DRAFT → UNDER_REVIEW` de forma síncrona y puede dejar conflictos activos. Una vez en
> `UNDER_REVIEW` las sesiones ya no se editan desde aquí — los conflictos se resuelven en el Panel
> de conflictos (Pantalla 7) vía el **Modal: Resolver conflicto** (Pantalla 8). `Publicar` solo
> tiene éxito si no quedan conflictos sin resolver (`409 UNRESOLVED_CONFLICTS` en otro caso).

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Crear horario (alta) | `POST /schedules` | `201` → `status=DRAFT`, navega a edición |
| Botón "Agregar sesión" | abre **Modal: Agregar/editar sesión** (Pantalla 5) en modo alta | `POST /schedules/{id}/sessions` al confirmar → `201` añade fila |
| Fila → "Editar" | abre **Modal: Agregar/editar sesión** (Pantalla 5) en modo edición | `PUT /sessions/{id}` al confirmar → `200` actualiza fila |
| Cancelar sesión | `POST /sessions/{id}/cancel` | `200` → `status=CANCELLED` |
| Eliminar sesión | `DELETE /sessions/{id}` | `204` quita fila; `409 SCHEDULE_IMMUTABLE` si no está en `DRAFT` |
| Guardar nombre del horario | `PUT /schedules/{id}` | `200`; `409 SCHEDULE_IMMUTABLE` / `ROW_VERSION_MISMATCH` |
| Validar | `POST /schedules/{id}/validate` | `200` → `status=UNDER_REVIEW` (puede incluir conflictos) |
| Botón "Publicar" | abre **Modal: Confirmar publicación** (Pantalla 6) | `POST /schedules/{id}/publish` al confirmar → `200` → `status=PUBLISHED`, inmutable, navega a Detalle de horario (Pantalla 3); `409 UNRESOLVED_CONFLICTS` bloquea |

**Estados:** *loading* (skeleton en tabla de sesiones) · *empty* ("Aún no hay sesiones — agrega la
primera") · *error* (`409` de doble-booking mostrado inline, icono + texto sobre los campos
Instructor/Ambiente/Franja del formulario, nunca solo un borde rojo) · *conflicto* (banner
persistente "Este horario tiene N conflictos sin resolver" con acceso directo al Panel de
conflictos, visible mientras `status=UNDER_REVIEW` y existan conflictos activos; el botón
"Publicar" queda deshabilitado con tooltip explicando el motivo) · *success* (confirmación modal al
publicar; el horario pasa a solo lectura).

```text
PROMPT STITCH
Pantalla "Editar horario" del Coordinador Académico, plataforma SENA — Gestión de Horarios, en
español. Encabezado con "Ficha 2589341 — Período 2026-1" y un badge de estado "Borrador" (icono
círculo gris) y un botón primario "Agregar sesión" arriba a la derecha de la tabla. Debajo, una
tabla de sesiones con columnas: Día, Franja horaria, Fecha, Competencia, Instructor, Ambiente,
Estado, y acciones (editar/cancelar/eliminar) por fila — tanto "Agregar sesión" como "Editar" abren
un modal aparte (no lo dibujes aquí, es otra pantalla). En la parte inferior, una barra de acciones
fija con tres botones: "Guardar", "Validar" (secundario) y "Publicar" (primario, deshabilitado con
un candado + tooltip "Resuelve los conflictos pendientes" cuando aplica). Mostrar también un banner
superior de advertencia "Este horario tiene 2 conflictos sin resolver" con un enlace "Ver panel de
conflictos". Estilo institucional, WCAG AA, formularios con validación en línea. Responsive.

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

**Mockup:** _(pendiente — `../mockups/02-coordinador/horario-editar.png`)_

---

## Pantalla 5 — Modal: Agregar/editar sesión

- **Ruta:** modal sobre `/horarios/:id` (no tiene ruta propia; se abre/cierra por estado de UI) · **Rol:** Coordinador Académico · **HU:** HU-08 (agregar sesiones)
- **MFE:** `scheduling-mfe`
- **Endpoints:**
  - `POST /schedules/{id}/sessions` (`addScheduleSession`, scheduling.yaml) — modo alta — body `SessionCreate{competency_id, environment_id, instructor_id, time_slot_id, session_date, notes?}`
  - `PUT /sessions/{id}` (`updateSession`) — modo edición — body `SessionUpdate{instructor_id?, environment_id?, time_slot_id?, notes?}`
  - Poblar selectores: `GET /training-programs/{program_id}/competencies` (academic-management.yaml, requiere resolver antes `ficha.program_id` vía `GET /fichas/{ficha_id}`), `GET /instructors` (actors.yaml), `GET /training-environments` (training-environment.yaml), `GET /time-slots` (scheduling.yaml)
- **Tabla/campos reales:** `class_session.{competency_id, environment_id, instructor_id, time_slot_id, session_date, notes}` (alta); en edición solo `{instructor_id, environment_id, time_slot_id, notes}` son mutables

> **Nota de congruencia (no se inventa):** `SessionUpdate` (`PUT /sessions/{id}`) **no** admite
> cambiar `competency_id` ni `session_date` — ambos son inmutables tras la creación de la sesión
> (solo se reasignan instructor, ambiente, franja horaria y notas). El modal en **modo edición**
> muestra Competencia y Fecha en solo lectura (atenuadas, sin selector) y deja editables Instructor,
> Ambiente, Franja horaria y Notas; el modal en **modo alta** habilita los 5 campos + Notas. La
> lista de competencias se resuelve por el `program_id` de la ficha del horario (`GET
> /training-programs/{program_id}/competencies`), no por un endpoint de competencias suelto (no
> existe en el contrato).

**Propósito:** capturar (o reasignar) una sesión de clase validando en línea el doble-booking de
instructor/ambiente antes de que el backend lo rechace.

**Layout:** modal centrado (bottom sheet en móvil) con título "Agregar sesión" / "Editar sesión";
contexto de solo lectura arriba: "Ficha 2589341 — Período 2026-1" (`ficha_id`/`period` del
horario); campos: **Competencia** (selector buscable, editable solo en alta), **Instructor**
(selector buscable), **Ambiente** (selector buscable), **Franja horaria** (`time_slot`, selector
con `day_of_week` + `start_time`–`end_time`), **Fecha** (`session_date`, editable solo en alta),
**Notas** (textarea opcional); pie del modal: botón secundario "Cancelar" + botón primario "Agregar
sesión" / "Guardar cambios".

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Confirmar en modo alta | `POST /schedules/{id}/sessions` | `201` cierra el modal y añade la fila en Pantalla 4; `409 INSTRUCTOR_DOUBLE_BOOKED`/`ENVIRONMENT_DOUBLE_BOOKED` → error inline bajo Instructor/Ambiente, modal permanece abierto; `409 SCHEDULE_IMMUTABLE` → banner de error, modal se cierra (el horario ya no es `DRAFT`) |
| Confirmar en modo edición | `PUT /sessions/{id}` | `200` cierra el modal y actualiza la fila; mismos `409` que en alta |
| "Cancelar" / cerrar modal | — | descarta cambios, vuelve a Pantalla 4 sin llamar al backend |

**Estados:** *loading* (spinner en selectores mientras cargan competencias/instructores/ambientes/franjas; botón de confirmar deshabilitado hasta que los 5 campos requeridos tengan valor) · *error* (`409` de doble-booking: icono + texto en rojo bajo el campo afectado, nunca solo borde rojo; error de red: banner dentro del modal con "Reintentar") · *success* (el modal se cierra y la fila aparece/actualiza con una confirmación breve tipo toast en Pantalla 4).

```text
PROMPT STITCH
Modal "Agregar sesión" (variante "Editar sesión") del Coordinador Académico, plataforma SENA —
Gestión de Horarios, en español, superpuesto sobre la pantalla "Editar horario". Encabezado del
modal: título "Agregar sesión" y, debajo en gris, el contexto de solo lectura "Ficha 2589341 —
Período 2026-1". Formulario con selectores con búsqueda: "Competencia" (ej. "Programación de
software"), "Instructor" (ej. "Juan Pérez"), "Ambiente" (ej. "Aula 201"), "Franja horaria" (ej.
"Lunes 07:00–10:00"), y un campo de fecha "Fecha de la sesión". Un campo de texto opcional "Notas".
Mostrar un ejemplo de error de doble-asignación: bajo el selector "Instructor" un texto en rojo con
icono de alerta "Este instructor ya tiene una sesión en este horario". Pie del modal con dos
botones: "Cancelar" (secundario) y "Agregar sesión" (primario). Genera también la VARIANTE "Editar
sesión": mismo modal pero con los campos "Competencia" y "Fecha de la sesión" mostrados en gris,
de solo lectura (sin selector), y el botón primario dice "Guardar cambios". Estilo institucional,
WCAG AA, validación en línea. Responsive: en móvil el modal se convierte en hoja inferior (bottom
sheet) que ocupa la pantalla completa.

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

**Mockup:** _(pendiente — `../mockups/02-coordinador/modal-sesion.png`)_

---

## Pantalla 6 — Modal: Confirmar publicación

- **Ruta:** modal sobre `/horarios/:id` · **Rol:** Coordinador Académico · **HU:** HU-10 (publicar)
- **MFE:** `scheduling-mfe`
- **Endpoints:**
  - `GET /schedules/{id}/conflicts?is_resolved=false` (`listScheduleConflicts`) — chequeo final antes de confirmar
  - `POST /schedules/{id}/publish` (`publishSchedule`, scheduling.yaml) — body `RowVersionRequest{row_version}`
- **Tabla/campos reales:** `schedule.{id, ficha_id, period, name, row_version}`; conteo de `scheduling_conflict` con `is_resolved=false`

**Propósito:** confirmación explícita antes de una acción irreversible (el horario queda
inmutable), con un último chequeo de conflictos para evitar el `409 UNRESOLVED_CONFLICTS`.

**Layout:** modal centrado con título "Publicar horario"; resumen de solo lectura: `ficha_id`
(referencia), `period`, `name`, cantidad de sesiones activas; si el chequeo final encuentra
conflictos sin resolver (condición de carrera — el botón "Publicar" de Pantalla 4 ya se deshabilita
en ese caso, pero el modal vuelve a verificar) muestra un banner crítico "Este horario tiene N
conflictos sin resolver" con icono + texto y botón "Ir al Panel de conflictos"; si no hay
conflictos, muestra un mensaje de confirmación positivo "N sesiones activas · sin conflictos
pendientes" y el botón de confirmar habilitado; pie del modal: "Cancelar" + "Confirmar publicación".

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Abrir el modal | `GET /schedules/{id}/conflicts?is_resolved=false` | recalcula el conteo de conflictos pendientes |
| "Confirmar publicación" | `POST /schedules/{id}/publish` | `200` → `status=PUBLISHED`, cierra el modal y navega a Detalle de horario (Pantalla 3); `409 UNRESOLVED_CONFLICTS` → banner crítico, botón de confirmar se deshabilita; `409 ROW_VERSION_MISMATCH` → banner "El horario cambió, recarga e intenta de nuevo" |
| "Cancelar" / cerrar modal | — | vuelve a Pantalla 4 sin publicar |

**Estados:** *loading* (spinner mientras verifica conflictos al abrir) · *conflicto* (banner crítico
bloqueante, botón de confirmar deshabilitado) · *error* (`409 ROW_VERSION_MISMATCH` o error de red:
banner + reintentar) · *success* (confirmación breve y navegación a la vista de solo lectura).

```text
PROMPT STITCH
Modal "Publicar horario" del Coordinador Académico, plataforma SENA — Gestión de Horarios, en
español, superpuesto sobre la pantalla "Editar horario". Título "Publicar horario". Resumen de solo
lectura: "Ficha 2589341 — Período 2026-1", "8 sesiones activas". Mostrar DOS variantes de contenido
del mismo modal: (1) variante SIN conflictos — un bloque verde con icono de check y el texto "Sin
conflictos pendientes — listo para publicar"; (2) variante CON conflictos — un bloque crítico
rojo/naranja con icono de alerta y el texto "Este horario tiene 2 conflictos sin resolver" y un
botón secundario "Ir al Panel de conflictos". Pie del modal con dos botones: "Cancelar" (secundario)
y "Confirmar publicación" (primario; en la variante con conflictos se muestra deshabilitado con un
candado). Nota abajo del todo en texto pequeño: "Al publicar, el horario queda de solo lectura".
Estilo institucional, WCAG AA. Responsive: en móvil el modal ocupa el ancho completo con márgenes
seguros.

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

**Mockup:** _(pendiente — `../mockups/02-coordinador/modal-publicar.png`)_

---

## Pantalla 7 — Panel de conflictos

> **Ciudadano de primera clase.** Esta pantalla existe porque detectar y comunicar un conflicto es
> la razón de ser del sistema (design-system §1.2); su representación visual es prioritaria sobre
> cualquier otro contenido.

- **Ruta:** `/horarios/:id/conflictos` (por horario) con pestaña adicional "Todo mi centro" (reporte) · **Rol:** Coordinador Académico · **HU:** HU-09 (ver y resolver conflictos)
- **MFE:** `scheduling-mfe`
- **Endpoints:**
  - `GET /schedules/{id}/conflicts` (`listScheduleConflicts`, scheduling.yaml) — filtros `is_resolved`, `conflict_type`; `page`/`page_size`/`sort`
  - `GET /reports/schedule-conflicts` (`reportScheduleConflicts`) — filtros `schedule_id`, `conflict_type`, `is_resolved`, `from`/`to`; paginación por cursor (colección grande/continua)
  - `POST /conflicts/{id}/resolve` (`resolveConflict`)
- **Tabla/campos reales:** `scheduling_conflict.{id, schedule_id, session_a_id, session_b_id, conflict_type, description, is_resolved, detected_at}`

> **Nota de congruencia (no se inventa):** `functional.md` (RF-SCH-03) y `HU-09` describen 5 tipos
> de conflicto (incluyendo `ENVIRONMENT_MAINTENANCE` e `INSTRUCTOR_UNAVAILABLE`), pero el `enum`
> real de `conflict_type` en `scheduling.yaml`/`data-model.md` solo define 3:
> `INSTRUCTOR_DOUBLE_BOOKED`, `ENVIRONMENT_DOUBLE_BOOKED`, `SESSIONS_OVERLAP`. Esta pantalla usa el
> enum real del contrato; el gap queda documentado en el reporte final de esta tarea.

**Propósito:** listar, clasificar y permitir resolver cada conflicto detectado antes de publicar.

**Layout:** tabs "Este horario" / "Todo mi centro"; filtros por tipo de conflicto y estado
(pendiente/resuelto); lista de **tarjetas** (no solo tabla) — cada tarjeta: icono grande distintivo
por `conflict_type` (dos personas cruzadas = instructor doble-asignado; puerta cruzada = ambiente
doble-asignado; flechas superpuestas = sesiones solapadas), texto `description`, referencia corta a
`session_a_id`/`session_b_id`, fecha `detected_at`, badge "Pendiente" (crítico) / "Resuelto"
(éxito) con icono + texto, botón "Marcar como resuelto" (solo si `is_resolved=false`, abre el
**Modal: Resolver conflicto**, Pantalla 8). Pie de lista
con **paginación REAL y visible**, distinta por pestaña: en **"Este horario"** — barra ‹ anterior ·
1 2 3 … › siguiente, selector de tamaño de página (`page_size`: 10/20/50) y "Mostrando X–Y de N",
alineada a `page`/`page_size`/`sort` de `GET /schedules/{id}/conflicts`; en **"Todo mi centro"** —
control ‹ anterior · siguiente › (sin salto directo a página, por ser paginación por cursor),
selector de tamaño de página (`limit`: 10/20/50) y "Mostrando X de N" (N = conflictos cargados
hasta el cursor actual), alineado a `cursor`/`limit` de `GET /reports/schedule-conflicts`. Nunca una
lista infinita sin control.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Filtrar por tipo/estado | `GET /schedules/{id}/conflicts?conflict_type=&is_resolved=` | refresca la lista |
| Marcar como resuelto | abre **Modal: Resolver conflicto** (Pantalla 8) | `POST /conflicts/{id}/resolve` al confirmar → `200` → `is_resolved=true`; `409` si ya estaba resuelto |
| Ver sesión en conflicto | navega a Pantalla 4 (o Pantalla 3 si el horario ya no es `DRAFT`/`UNDER_REVIEW`) y resalta `session_a_id`/`session_b_id` | — |
| Pestaña "Todo mi centro" | `GET /reports/schedule-conflicts?is_resolved=&conflict_type=&cursor=` | lista paginada por cursor de todos los horarios del centro (scope `TRAINING_CENTER` del JWT) |

**Estados:** *loading* (skeleton de tarjetas) · *empty* ("Sin conflictos — este horario puede
publicarse", icono de check, color éxito) · *error* (banner + reintentar) · *conflicto* (estado por
defecto de esta pantalla: cada tarjeta pendiente usa color crítico + icono + texto explícito del
tipo, nunca solo color).

```text
PROMPT STITCH
Pantalla "Panel de conflictos" del Coordinador Académico, plataforma SENA — Gestión de Horarios,
en español. Encabezado "Conflictos — Horario Ficha 2589341, Período 2026-1" con dos pestañas: "Este
horario" (activa) y "Todo mi centro". Fila de filtros: tipo de conflicto (Instructor doble-asignado
/ Ambiente doble-asignado / Sesiones solapadas) y estado (Pendiente / Resuelto). Debajo, una lista
de tarjetas de conflicto en color crítico (rojo/naranja) para los pendientes: cada tarjeta muestra
un icono grande distintivo del tipo, el texto de descripción ("El instructor Juan Pérez tiene dos
sesiones que se solapan el 2026-02-10 de 07:00 a 10:00"), la fecha de detección, y un botón
"Marcar como resuelto" (abre un modal de confirmación aparte, no lo dibujes aquí). Las tarjetas resueltas se muestran atenuadas con un icono de check verde y
badge "Resuelto". Mostrar también el estado vacío como una tarjeta central con icono de check verde
grande y el texto "Sin conflictos — este horario puede publicarse". Al pie de la lista, una barra de
paginación REAL y visible: en la pestaña "Este horario", "‹ anterior · 1 2 3 · siguiente ›" con
selector de tamaño de página ("10 / 20 / 50 por página") y "Mostrando 1–4 de 4"; en la pestaña
"Todo mi centro" (paginación por cursor), "‹ anterior · siguiente ›" sin números de página, con el
mismo selector de tamaño de página y "Mostrando 10 de 23". Estilo institucional, alto contraste WCAG
AA, el color nunca es la única señal (siempre icono + texto). Responsive: tarjetas en columna única
en móvil, con la barra de paginación al final.

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

**Mockup:** _(pendiente — `../mockups/02-coordinador/panel-conflictos.png`)_

---

## Pantalla 8 — Modal: Resolver conflicto

- **Ruta:** modal sobre `/horarios/:id/conflictos` (o sobre la pestaña "Todo mi centro") · **Rol:** Coordinador Académico · **HU:** HU-09 (ver y resolver conflictos)
- **MFE:** `scheduling-mfe`
- **Endpoint:** `POST /conflicts/{id}/resolve` (`resolveConflict`, scheduling.yaml) — **sin body**
- **Tabla/campos reales:** `scheduling_conflict.{id, schedule_id, session_a_id, session_b_id, conflict_type, description, is_resolved, detected_at}`

> **Nota de congruencia (no se inventa):** el contrato de `resolveConflict` **no** acepta un cuerpo
> de petición (no hay campo `resolution_notes` ni similar en `scheduling.yaml`) — la acción real es
> únicamente marcar `is_resolved = true`. Este modal es una **confirmación**, no un formulario: no
> se inventa un campo de notas que el backend no persiste.

**Propósito:** evitar que "Marcar como resuelto" sea un clic accidental de un solo paso, mostrando
el detalle del conflicto antes de confirmar la resolución.

**Layout:** modal centrado con título "Resolver conflicto"; icono grande según `conflict_type`;
texto `description` completo; referencia a `session_a_id` y, si existe, `session_b_id`; fecha
`detected_at`; si este es el **último** conflicto pendiente del horario (calculado en cliente sobre
la lista ya cargada de Pantalla 7), un texto adicional "Al resolverlo, este horario podrá
publicarse."; pie del modal: "Cancelar" + botón primario "Confirmar resolución".

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| "Confirmar resolución" | `POST /conflicts/{id}/resolve` | `200` → `is_resolved=true`, cierra el modal y actualiza la tarjeta en Pantalla 7; `409` (ya estaba resuelto) → banner de error dentro del modal, refresca la lista al cerrar |
| "Cancelar" / cerrar modal | — | no llama al backend, vuelve a Pantalla 7 |

**Estados:** *error* (`409` conflicto ya resuelto por otro usuario: banner "Este conflicto ya fue
resuelto" con botón "Entendido" que cierra y refresca; error de red: banner + "Reintentar") ·
*success* (el modal se cierra y la tarjeta pasa a "Resuelto" con una confirmación breve).

```text
PROMPT STITCH
Modal "Resolver conflicto" del Coordinador Académico, plataforma SENA — Gestión de Horarios, en
español, superpuesto sobre el "Panel de conflictos". Título "Resolver conflicto". Icono grande de
alerta según el tipo (dos personas cruzadas para instructor doble-asignado). Texto de descripción
completo: "El instructor Juan Pérez tiene dos sesiones que se solapan el 2026-02-10 de 07:00 a
10:00". Referencia corta a las dos sesiones involucradas y la fecha de detección "Detectado el 2026-
02-08". Un texto adicional en verde: "Al resolverlo, este horario podrá publicarse." (mostrar solo
en esta variante, es el último conflicto pendiente). Pie del modal con dos botones: "Cancelar"
(secundario) y "Confirmar resolución" (primario). Estilo institucional, WCAG AA, el color nunca es
la única señal (siempre icono + texto). Responsive: en móvil el modal ocupa el ancho completo con
márgenes seguros.

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

**Mockup:** _(pendiente — `../mockups/02-coordinador/modal-resolver-conflicto.png`)_

---

## Pantalla 9 — Disponibilidad

- **Ruta:** `/disponibilidad` · **Rol:** Coordinador Académico · **HU:** HU-05 (ambientes disponibles), HU-06 (instructores disponibles)
- **MFE:** `environment-mfe` (panel Ambientes) + `actors-mfe` (panel Instructores)
- **Endpoints:**
  - `GET /training-environments` (`listTrainingEnvironments`, training-environment.yaml) — filtros `environment_type_id`, `training_center_id`, `is_active`, `available_date`, `available_start_time`, `available_end_time`
  - `GET /environment-types` (`listEnvironmentTypes`) — para poblar el filtro de tipo
  - `GET /instructors` (`listInstructors`, actors.yaml) — filtros `document_number`, `area`, `training_center_id`, `is_active`
  - `GET /instructors/{id}/availability-exceptions` (`listInstructorAvailabilityExceptions`) — filtros `from`/`to`
  - `GET /reports/environment-utilization` (`reportEnvironmentUtilization`) — `from`/`to` obligatorios; reporte de ocupación por ambiente
  - `GET /reports/instructor-load` (`reportInstructorLoad`) — reporte de carga/disponibilidad por instructor
- **Tabla/campos reales:** `environment.{id, name, environment_type_id, training_center_id, capacity, location, is_active}`; `instructor.{id, full_name, document_number, default_max_hours_per_week, is_active}`; `instructor_availability_exception.{exception_type, start_datetime, end_datetime}`

> **Nota de congruencia (no se inventa):** `RF-ACT-03`/`HU-06` mencionan `GET
> /instructors/available` y `RF-ENV-04` menciona `GET /environments/available`, pero ninguno de los
> dos existe como `operationId` en los contratos reales. Para **ambientes** sí hay equivalente
> funcional: los parámetros `available_date`/`available_start_time`/`available_end_time` de `GET
> /training-environments` calculan la disponibilidad efectiva (descuenta mantenimiento y reservas)
> en el propio servicio. Para **instructores no hay endpoint agregado**: esta pantalla compone la
> disponibilidad en el cliente cruzando `GET /instructors` (candidatos) con `GET
> /instructors/{id}/availability-exceptions?from=&to=` (excepciones en la franja consultada) —
> documentado aquí como supuesto de v0, a validar con backend antes de construir.

**Layout:** selector de fecha + franja horaria (hora inicio/fin) arriba, compartido por ambos
paneles; dos paneles/tabs — **Ambientes**: tarjetas/tabla con `name`, `environment_type`,
`capacity`, `location`, badge "Disponible"/"No disponible" (icono+texto) según los parámetros
`available_*`, enlace a reporte de utilización, y pie de panel con **paginación REAL y visible**
(barra ‹ anterior · 1 2 3 … › siguiente, selector de tamaño de página `page_size`: 10/20/50, y
"Mostrando X–Y de N") alineada a `page`/`page_size` de `GET /training-environments`;
**Instructores**: tabla con `full_name`, `document_number`, área(s)
(`instructor_area.area_name`), `default_max_hours_per_week`, badge "Disponible"/"Con excepción"
(derivado de cruzar `availability-exceptions` en la franja), enlace al reporte de carga, y su
**propia** barra de paginación REAL y visible (misma mecánica: ‹ anterior · 1 2 3 … › siguiente,
selector `page_size` 10/20/50, "Mostrando X–Y de N") alineada a `page`/`page_size` de `GET
/instructors` — independiente de la del panel de Ambientes. Nunca una lista infinita sin control.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Consultar ambientes por fecha/franja | `GET /training-environments?available_date=&available_start_time=&available_end_time=` | refresca lista de ambientes con disponibilidad calculada |
| Filtrar ambientes por tipo/centro | `GET /training-environments?environment_type_id=&training_center_id=` | refresca |
| Tarjeta de ambiente → "Ver detalle" | `GET /training-environments/{id}` | navega a Detalle de ambiente / disponibilidad (Pantalla 10) |
| Consultar instructores | `GET /instructors?area=&training_center_id=` + `GET /instructors/{id}/availability-exceptions?from=&to=` por candidato | marca disponible/con excepción en la franja |
| Ver carga del instructor | `GET /reports/instructor-load?training_center_id=&area=` | abre reporte |

**Estados:** *loading* (skeleton en ambos paneles) · *empty* ("No hay ambientes/instructores que
cumplan el filtro") · *error* (banner + reintentar por panel) · el badge "No disponible"/"Con
excepción" siempre usa icono + texto, coherente con el tratamiento de conflicto del resto del
sistema.

```text
PROMPT STITCH
Pantalla "Disponibilidad" del Coordinador Académico, plataforma SENA — Gestión de Horarios, en
español. Encabezado "Disponibilidad" con un selector de fecha y un rango de hora (inicio/fin)
compartido arriba. Debajo, dos pestañas: "Ambientes" (activa) e "Instructores". En "Ambientes": una
cuadrícula de tarjetas, cada una con nombre del ambiente ("Aula 201"), tipo (Laboratorio/Aula/
Taller), capacidad ("30 personas"), ubicación, y un badge "Disponible" (verde, icono de check) o
"No disponible" (gris/rojo, icono de candado) según la franja seleccionada. Al pie de la cuadrícula
de Ambientes, una barra de paginación REAL y visible: "‹ anterior · 1 2 3 · siguiente ›", selector
de tamaño de página ("10 / 20 / 50 por página") y "Mostrando 1–20 de 34". En "Instructores": una
tabla con columnas Nombre, Documento, Área, Horas máx./semana, y un badge "Disponible" o "Con
excepción" (icono de calendario tachado) si tiene una licencia/incapacidad registrada en esa
franja, con su propia barra de paginación al pie ("‹ anterior · 1 2 3 · siguiente ›", selector de
tamaño de página y "Mostrando 1–20 de 41"), independiente de la de Ambientes. Cada tarjeta de
ambiente tiene un enlace "Ver detalle" (abre otra pantalla, no lo dibujes aquí) y sobre el panel de
Instructores un botón secundario "Ver reporte de carga". Estilo institucional, alto contraste WCAG
AA, objetivos táctiles ≥44px pensando en uso en tablet dentro de los ambientes. Responsive.

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

**Mockup:** _(pendiente — `../mockups/02-coordinador/disponibilidad.png`)_

---

## Pantalla 10 — Detalle de ambiente / disponibilidad

- **Ruta:** `/disponibilidad/ambientes/:id` · **Rol:** Coordinador Académico · **HU:** HU-05 (ambientes disponibles)
- **MFE:** `environment-mfe`
- **Endpoints:**
  - `GET /training-environments/{id}` (`getTrainingEnvironment`, training-environment.yaml)
  - `GET /training-environments/{id}/availability-rules` (`listAvailabilityRules`) — filtro `day_of_week`; franjas recurrentes del ambiente
  - `GET /training-environments/{id}/maintenance` (`listMaintenancePeriods`) — filtros `from`/`to`
  - `GET /sessions?environment_id=&from=&to=&status=ACTIVE` (`listSessions`, scheduling.yaml) — sesiones de horario efectivamente programadas en el rango
  - `GET /reports/environment-occupancy?environment_id=&from=&to=` (`reportEnvironmentOccupancy`, scheduling.yaml) — ocupación agregada por franjas del rango
  - `GET /reports/environment-utilization?environment_id=&from=&to=` (`reportEnvironmentUtilization`, training-environment.yaml) — horas disponibles/reservadas/mantenimiento (complementario, por horas)
- **Tabla/campos reales:** `environment.{id, name, environment_type_id, training_center_id, capacity, location, is_active}`; `availability_rule.{day_of_week, start_time, end_time, effective_from, effective_until}`; `maintenance.{start_date, end_date, reason}`; `class_session.{environment_id, session_date, day_of_week, start_time, end_time, status}`; `EnvironmentOccupancyEntry.{period_from, period_to, occupied_slots, total_slots, occupancy_rate}`

> **Nota de congruencia (no se inventa):** no existe en el contrato un endpoint que devuelva
> directamente "ocupación por franja" desglosada día a día. Se compone en el cliente: las **franjas
> que existen** para el ambiente vienen de `GET /training-environments/{id}/availability-rules`
> (día + hora inicio/fin recurrente); qué franjas están **ocupadas** se determina cruzando esas
> reglas con `GET /sessions?environment_id=&from=&to=&status=ACTIVE` (que trae `day_of_week`/
> `start_time`/`end_time` desnormalizados de cada sesión real programada); los períodos en
> `GET /training-environments/{id}/maintenance` se marcan aparte como "En mantenimiento" (no son
> franjas ocupadas por clase). El **porcentaje agregado** del rango sí es un dato real y propio:
> `GET /reports/environment-occupancy` (`occupied_slots`/`total_slots`/`occupancy_rate`). Documentado
> como supuesto de v0, a validar con backend antes de construir (mismo patrón que la Nota de
> congruencia de Pantalla 9 para instructores).

**Propósito:** ver el detalle de un ambiente y su ocupación real franja por franja en un rango de
fechas, para decidir si es viable asignarlo a una nueva sesión.

**Layout:** header con `name`, `environment_type`, `capacity`, `location`, badge
"Activo"/"Inactivo" (`is_active`), botón "Volver a Disponibilidad"; selector de rango de fechas
(`from`/`to`, reutilizado del selector de Pantalla 9); tarjeta KPI única "Ocupación en el rango" con
`occupancy_rate` en porcentaje y el detalle "`occupied_slots` de `total_slots` franjas" (`GET
/reports/environment-occupancy`); grilla semanal "Ocupación por franja" — filas = franjas
recurrentes (`availability_rule`, agrupadas por `start_time`–`end_time`), columnas = día 1 (lunes) a
7 (domingo); cada celda: "Ocupada" (icono+texto, si hay una `class_session` `ACTIVE` de ese
ambiente en esa franja/día dentro del rango), "Libre" (icono+texto) o "Mantenimiento" (icono+texto,
si el día cae dentro de un `maintenance` del ambiente); enlace "Ver reporte de utilización (horas)"
hacia los datos de `GET /reports/environment-utilization` (horas disponibles/reservadas/
mantenimiento) como detalle complementario.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Cambiar rango de fechas | `GET /reports/environment-occupancy?environment_id=&from=&to=` + `GET /sessions?environment_id=&from=&to=` | recalcula el KPI y la grilla |
| "Ver reporte de utilización (horas)" | `GET /reports/environment-utilization?environment_id=&from=&to=` | abre el detalle de horas disponibles/reservadas/mantenimiento |
| "Volver a Disponibilidad" | — | navega a Pantalla 9 |

**Estados:** *loading* (skeleton en KPI y grilla) · *empty* ("Este ambiente no tiene franjas de
disponibilidad configuradas" si `availability-rules` está vacío) · *error* (banner + reintentar) ·
las celdas "Ocupada"/"Mantenimiento" siempre usan icono + texto, nunca solo color.

```text
PROMPT STITCH
Pantalla "Detalle de ambiente" del Coordinador Académico, plataforma SENA — Gestión de Horarios, en
español, dentro del app shell. Encabezado "Aula 201" con subtítulo "Laboratorio · 30 personas ·
Bloque B, piso 2" y un badge "Activo" (icono check verde); enlace "‹ Volver a Disponibilidad" arriba
a la izquierda. Debajo, un selector de rango de fechas y una única tarjeta KPI: "Ocupación en el
rango: 68%" con el detalle "17 de 25 franjas". Debajo, una grilla semanal "Ocupación por franja" con
columnas Lunes a Domingo y filas por franja horaria (ej. "07:00–10:00", "10:00–13:00"); cada celda
muestra un badge: "Ocupada" (rojo suave, icono de reloj) para franjas con clase programada, "Libre"
(verde, icono de check) para franjas disponibles, o "Mantenimiento" (gris, icono de llave inglesa)
para los días bajo mantenimiento. Al pie, un enlace secundario "Ver reporte de utilización (horas)".
Estilo institucional, alto contraste WCAG AA, objetivos táctiles ≥44px. Responsive: en móvil la
grilla se convierte en una lista de acordeón por día.

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

**Mockup:** _(pendiente — `../mockups/02-coordinador/ambiente-detalle.png`)_

---

## Pantalla 11 — Fichas

- **Ruta:** `/fichas` · **Rol:** Coordinador Académico · **HU:** HU-01 (parcial — el alta detallada de ficha queda fuera de esta pantalla de consulta, ver nota)
- **MFE:** `academic-mfe`
- **Endpoint principal:** `GET /reports/enrollment-by-ficha` (`reportEnrollmentByFicha`, academic-management.yaml) — reporte propio que cruza `enrollment_ficha` + `training_program` y ya resuelve `program_code`/`program_name` (evita un join manual contra `GET /training-programs/{id}`)
- **Filtros reales:** `training_center_id`, `program_id`, `status` (enum `INDUCTION`/`EXECUTION`/`PRODUCTIVE_STAGE`/`COMPLETED`/`CANCELLED`), `from`/`to` (rango de `start_date`)
- **Endpoint de detalle:** `GET /fichas/{id}` (`getFicha`) — trae el registro completo (`program_version`, `expected_end_date`, `actual_end_date`, `training_shift`, `training_modality`, `max_capacity`, `created_at`, `updated_at`)
- **Tabla/campos reales:** `EnrollmentByFichaReportItem.{ficha_id, ficha_number, program_id, program_code, program_name, training_center_id, status, max_capacity, training_shift, training_modality, start_date}`; detalle en `enrollment_ficha`

**Propósito:** consultar rápidamente las fichas del centro con su programa y estado, y abrir el
detalle completo de cada una.

**Layout:** header "Fichas"; filtros por programa, estado y rango de fecha de inicio; tabla densa
con columnas **Ficha** (`ficha_number`), **Programa** (`program_code` — `program_name`), **Estado**
(badge icono+texto: Inducción / Ejecución / Etapa productiva / Finalizada / Cancelada),
**Jornada** (`training_shift`), **Modalidad** (`training_modality`), **Cupo máximo**
(`max_capacity`), **Fecha de inicio** (`start_date`); pie de tabla con **paginación REAL y
visible** — barra ‹ anterior · 1 2 3 … › siguiente, **selector de tamaño de página** (`page_size`:
10/20/50) y texto **"Mostrando X–Y de N"** — alineada a `page`/`page_size` de
`GET /reports/enrollment-by-ficha`; al hacer clic en una fila se abre un panel lateral rápido con
`GET /fichas/{id}` (incluye `program_version`, fechas de cierre esperada y real) y, dentro del
panel, un enlace "Ver detalle completo" hacia Detalle de ficha (Pantalla 12). Nunca una tabla
infinita sin control.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Filtrar por programa/estado/fecha | `GET /reports/enrollment-by-ficha?program_id=&status=&from=&to=` | refresca la tabla |
| Ver detalle de ficha (rápido) | `GET /fichas/{id}` | abre panel lateral con todos los campos |
| Panel lateral → "Ver detalle completo" | — | navega a Detalle de ficha (Pantalla 12) |
| (Fuera de v0) Crear ficha | `POST /fichas` (`createFicha`) — HU-01 | no se detalla en esta pantalla de consulta; queda como pantalla de alta pendiente para una iteración posterior |

**Estados:** *loading* (skeleton de filas) · *empty* ("No hay fichas que coincidan con los
filtros") · *error* (banner + reintentar).

```text
PROMPT STITCH
Pantalla "Fichas" del Coordinador Académico, plataforma SENA — Gestión de Horarios, en español,
dentro del app shell. Encabezado "Fichas". Barra de filtros: selector "Programa" (buscable),
selector "Estado" (Inducción / Ejecución / Etapa productiva / Finalizada / Cancelada), rango de
fechas "Inicio". Tabla densa con columnas: Ficha (número), Programa (código — nombre), Estado
(badge con icono + texto), Jornada (Diurna/Nocturna/Mixta), Modalidad (Presencial/Virtual/Híbrida),
Cupo máximo, Fecha de inicio. Al pie de la tabla, una barra de paginación REAL y visible: "‹
anterior · 1 2 3 … siguiente ›", un selector de tamaño de página ("10 / 20 / 50 por página") y el
texto "Mostrando 1–20 de 56". Al hacer clic en una fila se abre un panel de detalle deslizante
desde la derecha con los datos completos: versión del programa, fecha de inicio, fecha esperada de
cierre, fecha real de cierre (si aplica), y un enlace de texto "Ver detalle completo →" al final del
panel (abre otra pantalla, no lo dibujes aquí). Mostrar el estado vacío con icono de carpeta y el texto
"No hay fichas que coincidan con los filtros". Estilo institucional, alto contraste WCAG AA, filas
con hover sutil. Responsive: en móvil la tabla colapsa a tarjetas apiladas por ficha, con la misma
barra de paginación al final del listado.

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

**Mockup:** _(pendiente — `../mockups/02-coordinador/fichas.png`)_

---

## Pantalla 12 — Detalle de ficha

- **Ruta:** `/fichas/:id` · **Rol:** Coordinador Académico · **HU:** HU-01 (parcial — consulta; el alta queda fuera, igual que en Pantalla 11)
- **MFE:** `academic-mfe` (con enlaces de navegación hacia `scheduling-mfe` para los horarios de la ficha)
- **Endpoints:**
  - `GET /fichas/{id}` (`getFicha`, academic-management.yaml)
  - `GET /training-programs/{id}` (`getTrainingProgram`) — resuelve `program_code`/`name`/`training_level`/`total_hours` a partir de `ficha.program_id`
  - `GET /schedules?ficha_id=&page=&page_size=` (`listSchedules`, scheduling.yaml) — horarios asociados a esta ficha
- **Tabla/campos reales:** `enrollment_ficha.{id, ficha_number, program_id, program_version, training_center_id, status, start_date, expected_end_date, actual_end_date, training_shift, training_modality, max_capacity, created_at, updated_at}`; `training_program.{program_code, name, training_level, total_hours, version}`; `schedule.{id, period, name, status, updated_at}`

> **Nota de congruencia (no se inventa):** `GET /fichas/{id}` solo trae `program_id` (UUID) y
> `program_version` (snapshot congelado al abrir la ficha, no cambia si el programa se actualiza
> después). Para mostrar código/nombre del programa se resuelve con `GET
> /training-programs/{id}` — un segundo llamado, igual que hace `reportEnrollmentByFicha` para la
> lista (Pantalla 11), pero aquí se hace explícito porque esta pantalla no usa ese reporte.
> `training_center_id` es una referencia lógica a reference-data-service **sin endpoint de join**
> (documentado ya en el header del flujo) — se muestra el UUID si el cliente no lo resuelve.

**Propósito:** ver el registro completo de una ficha (incluida la versión congelada del programa) y
sus horarios asociados, sin salir del contexto de Fichas.

**Layout:** header con `ficha_number` en grande, badge de `status` (icono+texto: Inducción /
Ejecución / Etapa productiva / Finalizada / Cancelada), botón "Volver a Fichas"; sección "Programa":
`program_code` — `name`, `training_level`, `total_hours`, "Versión cursada: `program_version`"
(distinta de la versión vigente si el programa cambió después); sección "Datos de la ficha":
`training_center_id` (referencia), `training_shift`, `training_modality`, `max_capacity`,
`start_date`, `expected_end_date`, `actual_end_date` (si aplica), `created_at`/`updated_at`;
sección "Horarios de esta ficha": tabla breve (**Período**, **Nombre**, **Estado**, **Última
actualización**) desde `GET /schedules?ficha_id=`, con pie **"mostrando X de N · Ver todos en
Horarios"** (no lleva paginación propia — es un widget de resumen dentro de una pantalla de
detalle, no una pantalla de lista; "Ver todos" navega a Pantalla 2 con el filtro `ficha_id`
aplicado); cada fila navega a Pantalla 3 o Pantalla 4 según el `status` del horario (misma regla
que en Pantalla 2).

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Cargar detalle | `GET /fichas/{id}` + `GET /training-programs/{id}` | pobla las secciones "Programa" y "Datos de la ficha" |
| Cargar horarios de la ficha | `GET /schedules?ficha_id=&page=1&page_size=5` | pobla el widget "Horarios de esta ficha" |
| Fila de horario | `GET /schedules/{id}` | navega a Pantalla 3 (solo lectura) o Pantalla 4 (editable) según `status` |
| "Ver todos en Horarios" | — | navega a Pantalla 2 con `ficha_id` preaplicado como filtro |
| "Volver a Fichas" | — | navega a Pantalla 11 |

**Estados:** *loading* (skeleton en las 3 secciones, independientes) · *empty* (widget de horarios:
"Esta ficha aún no tiene horarios" con enlace "Crear horario" que abre Pantalla 4 en modo alta con
`ficha_id` preasignado) · *error* (banner de reintento por sección, no bloquea las demás).

```text
PROMPT STITCH
Pantalla "Detalle de ficha" del Coordinador Académico, plataforma SENA — Gestión de Horarios, en
español, dentro del app shell. Encabezado grande "Ficha 2589341" con un badge de estado "Ejecución"
(icono+texto) y un enlace "‹ Volver a Fichas" arriba a la izquierda. Sección "Programa": "233104 —
Análisis y Desarrollo de Software", "Nivel: Tecnólogo", "2.440 horas", "Versión cursada: 3". Sección
"Datos de la ficha" en formato de pares etiqueta-valor: Centro de formación, Jornada (Diurna),
Modalidad (Presencial), Cupo máximo (30), Fecha de inicio, Fecha esperada de cierre, Fecha real de
cierre (si aplica), Creado el, Última actualización. Sección "Horarios de esta ficha": una tabla
breve de 3 filas (período, nombre, estado con badge icono+texto, última actualización), con pie
"Mostrando 3 de 3 · Ver todos en Horarios" (sin paginador, es un widget resumen). Mostrar también el
estado vacío del widget de horarios: icono de calendario y texto "Esta ficha aún no tiene horarios"
con un botón "Crear horario". Estilo institucional, alto contraste WCAG AA. Responsive: en móvil las
secciones se apilan verticalmente.

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

**Mockup:** _(pendiente — `../mockups/02-coordinador/ficha-detalle.png`)_

---

## Mockups generados
_(pendiente — guardar en `../mockups/02-coordinador/` y enlazar aquí: dashboard.png,
horarios-lista.png, horario-detalle.png, horario-editar.png, modal-sesion.png, modal-publicar.png,
panel-conflictos.png, modal-resolver-conflicto.png, disponibilidad.png, ambiente-detalle.png,
fichas.png, ficha-detalle.png)_
