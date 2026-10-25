<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: DDD de flujo UX (Administrador de Centro / Director) + prompts Stitch
fase: diseño (UX/UI)
estado: draft
dependencias_entrada: 07-api/contracts/openapi/{monitoring,iam,reference-data}.yaml; 09-microservices/services/{08-monitoring,01-iam,02-reference-data}-service/data-model.md; 12-ux-ui/design-system.md, navigation-map.md; 04-requirements/user-stories.md; 12-ux-ui/mockup-ddd/micro-frontends.md
consumidores_siguientes: Google Stitch; validación de diseño
tldr: Panel de KPIs con drill-down por indicador (monitoring-mfe), administración de usuarios/roles
  — lista, alta/edición, detalle y asignación de rol (iam-mfe) — y datos de referencia — jerarquía
  editable + catálogos/parámetros de solo lectura para este rol, con el modal de edición documentado
  como componente compartido de reference-mfe (reference-mfe) —, con RBAC citado por endpoint y MFE
  dueño declarado en cada pantalla.
decisiones_clave: monitoring reporta solo su propio dominio (no utilización de ambientes/carga de
  instructores: fuera de su contrato); catálogos y parámetros son de solo lectura para este rol
  (RN-REF-03/RF-REF-03), editables solo por ADMIN_STAFF/SYSTEM_ADMIN; iam.yaml no expone GET de
  roles por usuario (limitación conocida del contrato); cada pantalla declara su MFE dueño (ver
  micro-frontends.md); el modal de edición de catálogos/valores/parámetros se documenta aquí como
  componente reference-mfe compartido con 06-backoffice.md aunque este rol no puede activarlo
halts_registrados: ninguno
-->

> **ESTADO: PRELIMINAR (v0)** — instrumento de descubrimiento, no diseño final. Trazabilidad
> completa a **endpoint + tabla**; trazabilidad a HU se cierra después (ver
> [README.md](../README.md)).

# Flujo — Administrador de Centro / Director

**Rol:** Administrador de Centro / Director (rol de negocio `CENTER_DIRECTOR`/`ADMIN_STAFF` en IAM)
**Navegación:** [navigation-map.md](../../navigation-map.md) → Administrador de Centro → Panel de
indicadores · Administración.

**Servicios origen:**
- Pantallas 1–2 — `monitoring-service` · Contrato: `../../../07-api/contracts/openapi/monitoring.yaml` · Modelo: `../../../09-microservices/services/08-monitoring-service/data-model.md`
- Pantallas 3–6 — `iam-service` · Contrato: `../../../07-api/contracts/openapi/iam.yaml` · Modelo: `../../../09-microservices/services/01-iam-service/data-model.md`
- Pantallas 7–8 — `reference-data-service` · Contrato: `../../../07-api/contracts/openapi/reference-data.yaml` · Modelo: `../../../09-microservices/services/02-reference-data-service/data-model.md`

---

## Pantalla 1 — Panel de indicadores (KPIs)

- **Ruta:** `/admin/indicadores` · **Rol:** Administrador de Centro / Director · **HU:** pendiente
  (relacionado a discovery M9 — ver [navigation-map.md](../../navigation-map.md); HU-20 solo cubre
  la consulta de KPIs del coordinador por ficha individual, no este tablero agregado).
- **Endpoints:**
  - `GET /api/v1/reports/indicators` (`x-required-feature: MON_REPORT_VIEW`) — agregado de fichas
    por `kpi_status_code` + `risk_level_code`. Filtros: `status`, `assigned_instructor_id`, `page`,
    `page_size`, `sort`. → `{ data: IndicatorsReportEntry[], pagination }` con
    `{ kpi_status_code, risk_level_code, ficha_count, avg_active_alert_count, as_of }`.
  - `GET /api/v1/reports/kpi-summary` (`x-required-feature: MON_REPORT_VIEW`) — última medición de
    cada KPI por ficha. Filtros: `ficha_tracking_id`, `kpi_type`, `status`, `from`, `to`, `page`,
    `page_size`, `sort`. → `{ data: KpiSummaryReportEntry[], pagination }` con
    `{ ficha_tracking_id, kpi_type_code, kpi_type_name, current_value, unit, threshold_value,
    kpi_status_code, risk_level_code, period_start, period_end, measured_at }`.
- **Catálogos de apoyo (para leyendas/badges):** `GET /api/v1/kpi-statuses` (`MON_KPI_VIEW`) →
  `KpiStatus{code, risk_level_id}`; `GET /api/v1/risk-levels` (`MON_ALERT_VIEW`) →
  `RiskLevel{code, label, color_hex, priority_order}` (INFO→LOW→MEDIUM→HIGH→CRITICAL,
  `priority_order` 1 = mayor urgencia).
- **Errores del contrato:** `401`, `403`, `429` (`TooManyRequests` en ambos reportes).
- **MFE:** `monitoring-mfe` ([micro-frontends.md](../micro-frontends.md))

**Alcance (nota de precisión):** `monitoring-service` **solo publica reportes de su propio
dominio** (seguimiento de fichas: asistencia, avance curricular, riesgo de deserción, avance de
etapa productiva). El navigation-map menciona "utilización de ambientes" y "carga de
instructores", pero esos datos **no existen en el contrato de monitoring** (pertenecen a otros
dominios aún sin reporte contratado); esta pantalla v0 **no los incluye** para no inventar campos.

**Propósito:** dar visibilidad ejecutiva del estado de seguimiento de todas las fichas del centro,
resaltando cuántas están en riesgo o crítico, para decidir dónde intervenir.

**Layout:**
- **Barra de filtros** (arriba): selector de **Tipo de KPI** (`ATTENDANCE`, `CURRICULUM_PROGRESS`,
  `DROPOUT_RISK`, `PRODUCTIVE_STAGE_PROGRESS`), selector de **Estado** (`ON_TRACK`/`AT_RISK`/
  `CRITICAL`, desde `kpi_status`), rango de fechas (`from`/`to` sobre `measured_at`), botón
  **Actualizar**.
- **Fila de tarjetas de KPI** (3, una por `kpi_status_code` agregado de `/reports/indicators`):
  cada tarjeta muestra el número grande de `ficha_count`, subtítulo `avg_active_alert_count`
  ("alertas activas promedio") y color+icono+texto del `risk_level_code` asociado (verde/ON_TRACK,
  ámbar/AT_RISK, rojo-crítico/CRITICAL — nunca solo color). Pie de tarjeta: "Actualizado: `as_of`".
- **Gráfico de distribución:** barras o dona con `ficha_count` por `risk_level_code` (usa
  `color_hex` del catálogo `risk_level` como base, con icono/etiqueta de apoyo).
- **Tabla densa** (de `/reports/kpi-summary`, widget de resumen — **no** es la pantalla de lista):
  columnas Ficha (`ficha_tracking_id`, truncado con tooltip), KPI (`kpi_type_name`), Valor actual
  (`current_value` + `unit`), Umbral (`threshold_value`), Estado (badge `kpi_status_code` coloreado
  por `risk_level_code` + icono), Período (`period_start`–`period_end`), Medido (`measured_at`).
  Muestra **top N** registros (`page_size` reducido, ej. 10, ordenado por urgencia) con texto
  **"Mostrando X de N · Ver todos"**; sin barra de paginación aquí (es widget, RN de calidad #3).
  "Ver todos" navegaría a la futura pantalla de lista completa de KPIs (esa sí pagina). **Cada fila
  es clicable** y abre el Drill-down de KPI (Pantalla 2) con el `ficha_tracking_id` y `kpi_type_code`
  de esa fila.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Filtro Tipo de KPI / Estado / rango de fechas | `GET /reports/kpi-summary?...` | refresca la tabla |
| Filtro Estado (tarjetas) | `GET /reports/indicators?status=...` | refresca tarjetas y gráfico |
| Actualizar | ambos GET | refresca todo el tablero |
| Fila de la tabla densa | — (usa `ficha_tracking_id` + `kpi_type_code` ya cargados en la fila) | abre Drill-down de KPI (Pantalla 2) con la serie histórica y el umbral de esa medición |

**Estados:** *loading* (skeleton de tarjetas + gráfico + tabla) · *empty* ("No hay fichas en
seguimiento para este filtro") · *error* (banner con reintento; `429` muestra mensaje de límite de
solicitudes) · *success*.

```text
PROMPT STITCH
Pantalla "Panel de indicadores" para el Administrador/Director de un centro SENA, dentro de la
plataforma Horarios SENA, en español, responsive, dentro del app shell (barra superior + nav
lateral "Indicadores" activo). Arriba, una barra de filtros con selectores "Tipo de KPI"
(Asistencia, Avance curricular, Riesgo de deserción, Avance etapa productiva), "Estado" (En
seguimiento, En riesgo, Crítico), un rango de fechas y un botón "Actualizar". Debajo, tres tarjetas
de KPI grandes en fila: "En seguimiento" (verde, número grande de fichas, subtítulo "alertas
activas promedio: 0.4"), "En riesgo" (ámbar, con ícono de advertencia) y "Crítico" (rojo, con
ícono de alerta) — el color nunca es la única señal, siempre acompañado de ícono y texto. Debajo,
un gráfico de barras horizontal mostrando la distribución de fichas por nivel de riesgo. Al fondo,
una tabla densa (widget de resumen, top 10 registros, filas con hover indicando que son clicables)
con columnas "Ficha", "KPI", "Valor actual", "Umbral", "Estado" (badge con ícono), "Período",
"Medido", con el texto "Mostrando 10 de 47 · Ver todos" debajo (sin barra de paginación — es un
widget, no la lista completa). Incluir el estado vacío ("No hay fichas en seguimiento para este
filtro") y el estado de carga con skeletons en tarjetas y tabla. Estilo institucional sobrio, verde
SENA (placeholder), alto contraste WCAG AA, tablas densas con buen espaciado.

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

## Pantalla 2 — Drill-down de KPI

- **Ruta:** `/admin/indicadores/:ficha_tracking_id/:kpi_type` (panel/pantalla abierta desde una
  fila de la Pantalla 1) · **Rol:** Administrador de Centro / Director · **HU:** pendiente (extiende
  el discovery M9 del tablero agregado; no existe HU dedicada al detalle puntual de un KPI).
- **Endpoints:**
  - `GET /api/v1/kpi-trackings` (`x-required-feature: MON_KPI_VIEW`) — **paginación por cursor**
    (colección de crecimiento continuo, particionada por `measured_at`; solo lectura, la produce el
    `alert-worker`). Filtros: `ficha_tracking_id` (fijo en esta pantalla), `kpi_type`, `kpi_status`,
    `from`, `to`, `cursor`, `limit` → `{ data: KpiTracking[], pagination }` con `{ id,
    ficha_tracking_id, kpi_type_id, current_value, threshold_value, kpi_status_id, period_start,
    period_end, measured_at }`.
  - `GET /api/v1/kpi-trackings/{id}` (`MON_KPI_VIEW`) — detalle de una medición puntual (al hacer
    clic en un punto del gráfico o una fila de la tabla).
  - **Catálogos de apoyo (ya cargados en Pantalla 1):** `GET /api/v1/kpi-statuses` (`MON_KPI_VIEW`),
    `GET /api/v1/risk-levels` (`MON_ALERT_VIEW`) — para resolver el badge de estado con color+icono+texto.
- **Errores del contrato:** `401`, `403`, `404` (`ficha_tracking_id` inexistente o fuera del scope
  del centro).
- **MFE:** `monitoring-mfe` ([micro-frontends.md](../micro-frontends.md))

**Nota de precisión (no se inventa):** `KpiTracking` solo trae `kpi_type_id`/`kpi_status_id` (UUID),
no sus códigos legibles. Esta pantalla reutiliza el `kpi_type_code`/`kpi_type_name` con que se
navegó desde la fila de origen en Pantalla 1 (que sí vienen resueltos en `KpiSummaryReportEntry`) en
vez de agregar un `GET /kpi-types/{id}` adicional que el contrato no exige para este flujo.

**Propósito:** profundizar en un único indicador de una ficha (ej. Asistencia de la ficha
`2589341`) mostrando su evolución en el tiempo contra el umbral que dispara alerta, para decidir si
amerita una intervención.

**Layout:**
- **Encabezado:** Ficha (`ficha_tracking_id` truncado con tooltip), KPI (`kpi_type_name`), badge
  grande de estado actual (`kpi_status_code` + `risk_level_code`, color+icono+texto), Valor actual
  (`current_value` + `unit`), Umbral vigente (`threshold_value`). Botón **‹ Volver al panel**.
- **Filtro de rango de fechas** (`from`/`to` sobre `measured_at`) arriba del gráfico.
- **Gráfico de línea temporal:** `current_value` por `measured_at`, con una línea de referencia
  horizontal punteada en `threshold_value`; los puntos que cruzan el umbral se resaltan (color
  crítico + icono, nunca solo color).
- **Tabla densa de mediciones** (debajo del gráfico): columnas Período (`period_start`–
  `period_end`), Medido (`measured_at`), Valor (`current_value` + `unit`), Umbral
  (`threshold_value`), Estado (badge). Fila clicable → `GET /kpi-trackings/{id}`.
- **Paginación por CURSOR** (al pie — `kpi_tracking` es una colección de crecimiento continuo,
  mismo patrón que el resto del sistema para estas colecciones): control **"‹ anterior ·
  siguiente ›"** (sin números de página absolutos), selector de tamaño (`limit`: 10/20/50) y texto
  **"Mostrando X de N aprox."**, alineado a `cursor`/`limit` de `GET /kpi-trackings`.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Filtro rango de fechas | `GET /kpi-trackings?ficha_tracking_id=&kpi_type=&from=&to=` | refresca gráfico y tabla |
| Cargar más / siguiente | `GET /kpi-trackings?cursor=&limit=` | avanza en la serie histórica |
| Fila de la tabla / punto del gráfico | `GET /kpi-trackings/{id}` | muestra el detalle puntual de esa medición (útil para enlace directo) |
| ‹ Volver al panel | — | regresa a Panel de indicadores (Pantalla 1) |

**Estados:** *loading* (skeleton de encabezado + gráfico + tabla) · *empty* ("No hay mediciones de
este KPI en el rango seleccionado") · *error* (banner con reintento; `404` si la ficha no existe o
no pertenece a este centro) · *conflicto/alerta* (los puntos sobre el umbral crítico se destacan
con color+icono+texto) · *success*.

```text
PROMPT STITCH
Pantalla "Detalle de indicador" (drill-down de KPI) para el Administrador/Director de un centro
SENA, plataforma Horarios SENA, en español, responsive, dentro del app shell (nav lateral
"Indicadores" activo), abierta desde una fila del panel de indicadores. Encabezado con "Ficha
2589341 — Asistencia" y un badge grande de estado "En riesgo" (ámbar, icono de advertencia), el
valor actual "76%" y el umbral vigente "80%", con un botón secundario "‹ Volver al panel" arriba a
la izquierda. Debajo, un selector de rango de fechas y un gráfico de línea temporal mostrando la
evolución del valor del KPI mes a mes, con una línea horizontal punteada marcando el umbral del 80%
y los puntos por debajo del umbral resaltados en rojo con un pequeño ícono de alerta. Debajo del
gráfico, una tabla densa con columnas "Período", "Medido", "Valor", "Umbral", "Estado" (badge con
ícono), con filas clicables. Al pie, una barra de paginación por CURSOR: "‹ anterior · siguiente ›"
(sin números de página), un selector de tamaño (10/20/50) y el texto "Mostrando 10 de 18 aprox.".
Mostrar el estado vacío ("No hay mediciones de este KPI en el rango seleccionado") y el estado de
carga con skeleton en encabezado, gráfico y tabla. Estilo institucional sobrio, verde SENA
(placeholder), alto contraste WCAG AA.

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

## Pantalla 3 — Administración — Usuarios

- **Ruta:** `/admin/usuarios` · **Rol:** Administrador de Centro / Director · **HU:** HU-18
  (Gestionar usuarios e instructores, *RF-IAM-02, RF-IAM-04*), HU-17 (Controlar el acceso por rol y
  centro, *RF-IAM-03*).
- **Endpoints:**
  - `GET /api/v1/users` (`IDENTITY_USER_VIEW`) — filtros `training_center_id`, `role`, `is_active`,
    `page`, `page_size`, `sort`. → `{ data: User[], pagination }` con `{ id, email, first_name,
    last_name, full_name, actor_type, actor_id, is_active, last_login_at, created_at, updated_at }`.
  - `GET /api/v1/roles` (`IDENTITY_ROLE_VIEW`) → `Role[]{ id, name, display_name, description,
    is_system_role, created_at }` — puebla el selector de filtro **Rol**.
  - El resto de operaciones sobre un usuario (alta, edición, roles, sesiones, desactivación) vive en
    las pantallas dedicadas de detalle/formulario (Pantallas 4–6) abiertas desde esta lista.
- **Errores del contrato:** `401`, `403`.
- **MFE:** `iam-mfe` ([micro-frontends.md](../micro-frontends.md))

**Propósito:** ubicar rápidamente al personal del centro por rol o estado, y ser el punto de
entrada hacia el alta, el detalle o la edición de cada usuario, dentro del alcance del propio
centro (scope `TRAINING_CENTER`, análogo a RN-IAM-03).

**Layout:**
- **Barra de filtros:** selector **Rol** (poblado con `GET /roles`), selector **Estado** (Activo/
  Inactivo → `is_active`), botón primario **+ Nuevo usuario** (abre Form: Crear/editar usuario,
  Pantalla 4, en modo alta).
- **Tabla densa:** columnas Nombre completo (`full_name`), Correo (`email`), Tipo de actor
  (badge `actor_type`), Estado (badge Activo/Inactivo), Último acceso (`last_login_at`). Fila
  clicable → abre Detalle de usuario (Pantalla 5).
- **Barra de paginación** (pantalla de LISTA — real, no widget): debajo de la tabla, ‹ anterior ·
  1 2 3 … › siguiente, selector de tamaño de página (`page_size`: 10/20/50) y texto **"Mostrando
  X–Y de N"**, alineado a `page`/`page_size` de `GET /users`.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| + Nuevo usuario | — (abre Pantalla 4 en modo alta; la creación real dispara `POST /users` desde ahí) | abre Form: Crear/editar usuario |
| Fila de la tabla | `GET /users/{id}` | abre Detalle de usuario (Pantalla 5) |
| Filtro Rol / Estado | `GET /users?role=&is_active=` | refresca la tabla |
| Paginación (‹ › · página) / selector `page_size` | `GET /users?page=&page_size=` | refresca la tabla con la página/tamaño elegido |

**Estados:** *loading* (skeleton de tabla) · *empty* ("No hay usuarios con estos filtros") ·
*error* (banner de red/permiso, `403` con mensaje "no tiene permiso para esta acción") · *success*.

```text
PROMPT STITCH
Pantalla "Administración — Usuarios" para el Administrador/Director de un centro SENA, plataforma
Horarios SENA, en español, responsive, dentro del app shell (nav lateral "Administración" activo).
Barra superior de la sección con selector "Rol", selector "Estado" (Activo/Inactivo) y un botón
primario "+ Nuevo usuario". Debajo, una tabla densa con columnas "Nombre completo", "Correo",
"Tipo de actor" (badge), "Estado" (badge verde/gris) y "Último acceso", con filas seleccionables
(hover indicando que abren el detalle). Debajo de la tabla, una barra de paginación REAL y visible:
flecha "‹ anterior", números de página "1 2 3 …", flecha "siguiente ›", un selector de tamaño de
página (10/20/50) y el texto "Mostrando 1–20 de 84". Mostrar el estado vacío de la tabla y el
estado de carga con skeleton. Estilo institucional sobrio, verde SENA (placeholder), alto contraste
WCAG AA, objetivos táctiles ≥44px.

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

## Pantalla 4 — Form: Crear/editar usuario

- **Ruta:** modal sobre `/admin/usuarios` (alta) y formulario embebido en la pestaña Perfil de
  Detalle de usuario, Pantalla 5 (edición) · **Rol:** Administrador de Centro / Director · **HU:**
  HU-18 (*RF-IAM-02, RF-IAM-04*).
- **Endpoints:**
  - `POST /api/v1/users` (`IDENTITY_USER_MANAGE`) — `UserCreate{ email, first_name, last_name,
    actor_type[USER|INSTRUCTOR|LEARNER], actor_id?, initial_role, training_center_id? }` →
    `UserCreateResponse{ id, email, temporary_password }` (caduca en 72 h, RN-IAM-05).
  - `PUT /api/v1/users/{id}` (`IDENTITY_USER_MANAGE`) — `UserUpdate{ first_name, last_name,
    actor_type, actor_id, is_active }` → `User`.
  - `GET /api/v1/roles` (`IDENTITY_ROLE_VIEW`) → puebla el selector **Rol inicial** (solo en alta).
- **Errores del contrato:** `400`, `401`, `403`, `404`, `409` (correo duplicado en alta), `422`.
- **MFE:** `iam-mfe` ([micro-frontends.md](../micro-frontends.md))

**Nota de precisión (no se inventa):** `UserUpdate` **no incluye `email`** — el correo es
inmutable después de la creación; en modo edición el campo Correo se muestra de solo lectura.
Tampoco incluye `initial_role`/`training_center_id` — el rol inicial solo se fija en el alta;
cambios de rol posteriores pasan por el Modal Asignar/revocar rol (Pantalla 6), no por este
formulario.

**Propósito:** dar de alta un usuario con su rol inicial, o editar los datos de perfil de uno
existente, sin mezclar la gestión de roles (que vive en su propio modal).

**Layout:**
- **Modo alta** (modal, disparado desde "+ Nuevo usuario" en Pantalla 3): campos **Correo**
  (`email`), **Nombre** (`first_name`), **Apellido** (`last_name`), **Tipo de actor** (select
  Usuario/Instructor/Aprendiz), **Actor vinculado** (`actor_id`, opcional, campo UUID/búsqueda),
  **Rol inicial** (select, poblado por `GET /roles`), **Centro de formación** (`training_center_id`,
  opcional). Botón primario **Crear**.
- **Modo edición** (formulario embebido en la pestaña Perfil de Detalle de usuario, Pantalla 5):
  mismos campos salvo **Correo** (solo lectura) y sin **Rol inicial**/**Centro** (no aplican en
  `UserUpdate`); incluye además el interruptor **Activo/Inactivo** (`is_active`). Botón **Guardar**.
- Al crear con éxito: tarjeta de confirmación con `temporary_password`, botón copiar y aviso
  "Caduca en 72 horas" (no se vuelve a mostrar tras cerrar el modal).

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Crear (modo alta) | `POST /users` | `201` → tarjeta con contraseña temporal; `409` si el correo ya existe; `422` validación por campo |
| Guardar (modo edición) | `PUT /users/{id}` | `200` → actualiza el usuario; toast de éxito; `422` validación por campo |
| Cancelar | — | cierra sin guardar |

**Estados:** *loading* (botón con spinner, campos bloqueados) · *error* (`422` inline por campo;
`409` "Este correo ya está registrado") · *success* (alta: tarjeta de contraseña temporal; edición:
toast "Usuario actualizado").

```text
PROMPT STITCH
Modal/formulario "Crear usuario" (y su variante "Editar perfil de usuario") para el
Administrador/Director de un centro SENA, plataforma Horarios SENA, en español, responsive. Modo
alta: modal centrado con título "Nuevo usuario" y los campos "Correo", "Nombre", "Apellido", "Tipo
de actor" (select Usuario/Instructor/Aprendiz), "Actor vinculado" (campo opcional con búsqueda),
"Rol inicial" (select) y "Centro de formación" (select opcional), con un botón primario "Crear"
abajo. Al confirmar, mostrar una tarjeta de éxito con la contraseña temporal generada (ej.
"Xk9#mPz2"), un botón de copiar y el aviso "Caduca en 72 horas" con icono de reloj. Modo edición
(mostrar como variante, embebida en un panel): mismos campos pero "Correo" en modo solo lectura con
icono de candado, sin "Rol inicial" ni "Centro", con un interruptor "Activo/Inactivo" y un botón
primario "Guardar". Mostrar validación en línea de ejemplo (ej. "Este correo ya está registrado" en
rojo con icono bajo el campo Correo) y el estado de carga (botón con spinner). Estilo institucional
sobrio, verde SENA (placeholder), alto contraste WCAG AA, objetivos táctiles ≥44px.

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

## Pantalla 5 — Detalle de usuario

- **Ruta:** `/admin/usuarios/:id` (panel lateral sobre `/admin/usuarios`) · **Rol:** Administrador
  de Centro / Director · **HU:** HU-18 (*RF-IAM-02, RF-IAM-04*), HU-17 (Controlar el acceso por rol
  y centro, *RF-IAM-03*).
- **Endpoints:**
  - `GET /api/v1/users/{id}` (`IDENTITY_USER_VIEW`) → `User` (perfil).
  - `GET /api/v1/users/{id}/sessions` (`IDENTITY_USER_VIEW`) → `Session[]{ id, device_hint,
    ip_address, created_at, expires_at, is_revoked, revoked_at }`.
  - `DELETE /api/v1/users/{id}/sessions/{session_id}` (sesión ajena: `IDENTITY_USER_MANAGE` de un
    administrador global; sesión propia: sin feature) → `204`.
  - `POST /api/v1/users/{id}/deactivate` (`IDENTITY_USER_MANAGE`) → `204` (soft delete + revoca
    sesiones).
- **Errores del contrato:** `401`, `403`, `404`.
- **MFE:** `iam-mfe` ([micro-frontends.md](../micro-frontends.md))

**Limitación conocida del contrato (no inventar campos):** `iam.yaml` no expone un `GET` para
listar los roles **actualmente asignados** a un usuario (solo `POST`/`DELETE` en
`/users/{id}/roles`). La pestaña **Roles** de este panel solo puede mostrar las asignaciones hechas
**durante la propia sesión de trabajo** (estado en memoria del cliente, alimentado por el Modal
Asignar/revocar rol, Pantalla 6) — no un historial persistente. Se deja marcado como pendiente de
contrato en vez de inventar un `GET`.

**Propósito:** consultar el perfil completo de un usuario, sus roles (dentro de la limitación
anterior) y auditar/revocar sus sesiones activas, antes de decidir si editarlo, asignarle un rol o
desactivarlo.

**Layout:** panel lateral derecho con 3 pestañas:
- **Perfil:** campos de `User` en solo lectura (correo, nombre completo, tipo de actor, actor
  vinculado, estado, último acceso, creado/actualizado) + botón **Editar** (abre Form: Crear/editar
  usuario, Pantalla 4, en modo edición) + botón **Desactivar** (rojo).
- **Roles:** lista de chips de roles asignados en esta sesión de trabajo (ver limitación arriba)
  con botón **×** por chip (abre el Modal Asignar/revocar rol, Pantalla 6, en modo revocar) + botón
  **Asignar rol** (abre el mismo modal en modo asignar).
- **Sesiones:** tabla de `Session[]` (dispositivo, IP, creada, expira, estado) con botón
  **Revocar** por fila.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Botón Editar (Perfil) | — (abre Pantalla 4 en modo edición) | abre Form: Crear/editar usuario |
| Desactivar | `POST /users/{id}/deactivate` | modal de confirmación → `204` → usuario pasa a Inactivo; sus sesiones se revocan |
| Asignar rol | — (abre Pantalla 6 en modo asignar) | abre Modal: Asignar/revocar rol |
| Revocar rol (chip ×) | — (abre Pantalla 6 en modo revocar, prellenado) | abre Modal: Asignar/revocar rol |
| Ver sesiones | `GET /users/{id}/sessions` | lista sesiones activas |
| Revocar sesión | `DELETE /users/{id}/sessions/{session_id}` | `204` → sesión removida de la lista |

**Estados:** *loading* (skeleton del panel) · *empty* (pestaña Roles: "Aún no se asignaron roles en
esta sesión de trabajo"; pestaña Sesiones: "Sin sesiones activas") · *error* (banner de
red/permiso) · *confirm* (modal de confirmación antes de desactivar) · *success* (toasts por cada
acción).

```text
PROMPT STITCH
Panel lateral "Detalle de usuario" para el Administrador/Director de un centro SENA, plataforma
Horarios SENA, en español, responsive, abierto desde una fila de la lista de usuarios. Panel
deslizante desde la derecha con el nombre completo y correo del usuario arriba, y tres pestañas:
"Perfil" (campos de solo lectura — nombre, apellido, tipo de actor, estado con badge, último
acceso — con botones "Editar" y "Desactivar" en rojo abajo), "Roles" (una lista de chips de roles
asignados con botón × en cada uno para revocar, y un botón "Asignar rol" arriba) y "Sesiones"
(tabla de dispositivo, IP, fecha de creación, expiración, con botón "Revocar" por fila). Mostrar el
estado vacío de la pestaña Roles ("Aún no se asignaron roles en esta sesión de trabajo") y el
estado de carga con skeleton. Incluir un modal de confirmación de ejemplo para "Desactivar usuario"
con texto de advertencia. Estilo institucional sobrio, verde SENA (placeholder), alto contraste
WCAG AA, objetivos táctiles ≥44px.

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

## Pantalla 6 — Modal: Asignar/revocar rol

- **Ruta:** modal sobre `/admin/usuarios/:id` (Detalle de usuario, Pantalla 5) · **Rol:**
  Administrador de Centro / Director · **HU:** HU-17 (Controlar el acceso por rol y centro,
  *RF-IAM-03*).
- **Endpoints:**
  - `POST /api/v1/users/{id}/roles` (`IDENTITY_ROLE_ASSIGN`) — `AssignRoleRequest{ role_name,
    training_center_id?, expires_at? }` → `UserRole{ id, user_id, role_id, role_name,
    training_center_id, assigned_by, assigned_at, expires_at }`.
  - `DELETE /api/v1/users/{id}/roles/{role_name}` (`IDENTITY_ROLE_ASSIGN`) → `204`.
  - `GET /api/v1/roles` (`IDENTITY_ROLE_VIEW`) → puebla el selector **Rol**.
- **Errores del contrato:** `400`, `401`, `403`, `404`, `409` (rol ya asignado).
- **MFE:** `iam-mfe` ([micro-frontends.md](../micro-frontends.md))

**Propósito:** dar o quitar un rol a un usuario, opcionalmente restringido a un centro y con
expiración, sin abandonar el detalle del usuario.

**Layout:** modal con dos modos:
- **Asignar** (formulario): select **Rol** (`role_name`, desde `GET /roles`), campo **Centro**
  (`training_center_id`, opcional — vacío = rol global; texto de ayuda "null = rol global; UUID =
  restringido al centro"), campo **Expira el** (`expires_at`, opcional, fecha). Botón primario
  **Asignar**.
- **Revocar** (confirmación): texto "¿Revocar el rol «{role_name}» de {full_name}?" con el detalle
  de centro/expiración si aplica. Botón primario destructivo **Revocar**.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Asignar | `POST /users/{id}/roles` | `201` → chip de rol agregado en Detalle de usuario; `409` si el rol ya está asignado |
| Revocar | `DELETE /users/{id}/roles/{role_name}` | `204` → chip removido de Detalle de usuario |
| Cancelar | — | cierra sin cambios |

**Estados:** *loading* (botón con spinner) · *error* (`409` "Este usuario ya tiene el rol X"; `404`
rol inexistente) · *success* (toast + cierre del modal).

```text
PROMPT STITCH
Modal "Asignar rol" (y su variante de confirmación "Revocar rol") para el Administrador/Director de
un centro SENA, plataforma Horarios SENA, en español, responsive, abierto desde el Detalle de
usuario. Modo asignar: modal centrado con título "Asignar rol a Laura Ramírez", un select "Rol"
(ej. Coordinador Académico, Instructor, Director de Centro), un campo opcional "Centro de
formación" con texto de ayuda "Vacío = rol global", un campo de fecha opcional "Expira el", y un
botón primario "Asignar" abajo. Modo revocar (mostrar como variante): modal más pequeño con icono
de advertencia, el texto "¿Revocar el rol «Instructor» de Laura Ramírez?" y dos botones: "Cancelar"
(secundario) y "Revocar" (primario, rojo). Mostrar un ejemplo de error en línea ("Este usuario ya
tiene este rol asignado", con icono, en rojo bajo el select Rol) y el estado de carga (botón con
spinner). Estilo institucional sobrio, verde SENA (placeholder), alto contraste WCAG AA.

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

## Pantalla 7 — Administración — Datos de referencia

- **Ruta:** `/admin/datos-referencia` · **Rol:** Administrador de Centro / Director · **HU:** HU-19
  (Administrar la jerarquía institucional y catálogos, *RF-REF-01, RF-REF-02*), con matiz de RBAC
  descrito abajo.
- **Nota de RBAC (precisión sobre HU-19):** el criterio de aceptación de HU-19 dice *"Solo
  `ADMIN_STAFF`/`SYSTEM_ADMIN` pueden editar catálogos; para el resto son solo lectura"*
  (RN-REF-03), y `functional.md` (RF-REF-03) restringe la edición de **parámetros** a
  `SYSTEM_ADMIN`. Por lo tanto, para el rol Administrador de Centro / Director esta pantalla es:
  **jerarquía de su centro → editable**; **catálogos → solo lectura**; **parámetros → solo
  lectura**. La UI debe ocultar/deshabilitar los controles de edición de catálogos y parámetros
  para este rol en vez de asumir que están disponibles. El modal de edición (Form: Editar catálogo
  / valor de catálogo / parámetro, Pantalla 8) existe como componente de `reference-mfe`, pero para
  este rol permanece **inactivo** (sin trigger habilitado) — se documenta en la Pantalla 8 para
  completar el inventario del MFE, no porque este rol pueda invocarlo.
- **Endpoints:**
  - **Mi centro y sedes** (editable):
    - `GET /api/v1/training-centers` (`REF_HIERARCHY_VIEW`) — filtros `municipality_id`,
      `center_code`, `is_active`. → `{ data: TrainingCenter[], pagination }` con `{ id,
      municipality_id, center_code, name, address, phone, is_active, created_at, updated_at }`.
    - `PUT /api/v1/training-centers/{id}` (`REF_HIERARCHY_MANAGE`) — `TrainingCenterUpdate{
      municipality_id, center_code, name, address, phone, is_active }`; el campo `center_code` es
      inmutable en la UI (RN-REF-01) aunque el schema lo permita — se muestra de solo lectura.
    - `GET /api/v1/institutional-units` (`REF_HIERARCHY_VIEW`) — filtro `training_center_id`,
      `unit_type`, `is_active`. → `{ data: InstitutionalUnit[], pagination }` con `{ id,
      training_center_id, name, unit_type[ACADEMIC|ADMINISTRATIVE|MIXED], is_active, created_at }`.
    - `POST /api/v1/institutional-units` (`REF_HIERARCHY_MANAGE`) —
      `InstitutionalUnitCreate{ training_center_id, name, unit_type, is_active }`.
    - `PUT /api/v1/institutional-units/{id}` (`REF_HIERARCHY_MANAGE`) — `InstitutionalUnitUpdate`.
    - `DELETE /api/v1/institutional-units/{id}` (`REF_HIERARCHY_MANAGE`) — `204` (soft delete
      `is_active=false`).
  - **Catálogos del sistema** (solo lectura para este rol; edición ver Pantalla 8):
    - `GET /api/v1/catalogs` (`REF_CATALOG_VIEW`) — filtros `code`, `is_active`. →
      `{ data: Catalog[], pagination }` con `{ id, code, name, description, is_active,
      created_at }`.
    - `GET /api/v1/catalogs/{catalog_id}/details` (`REF_CATALOG_VIEW`) → `{ data:
      CatalogDetail[], pagination }` con `{ id, catalog_id, code, label, display_order, is_active,
      created_at }`.
  - **Parámetros del sistema** (solo lectura para este rol; edición ver Pantalla 8):
    - `GET /api/v1/parameters` (`REF_PARAMETER_VIEW`) — filtros `key`, `value_type`. →
      `{ data: Parameter[], pagination }` con `{ id, key, value, value_type[integer|string|
      boolean|json], description, created_at }`.
- **Errores del contrato:** `401`, `403`, `404`, `409` (código duplicado), `422`.
- **MFE:** `reference-mfe` ([micro-frontends.md](../micro-frontends.md))

**Propósito:** que el Director mantenga al día los datos de su propio centro (sedes/unidades) y
consulte —sin poder alterar— los catálogos y parámetros que gobiernan el resto del sistema.

**Layout:** 3 pestañas dentro de la misma pantalla.
- **Pestaña "Mi centro":** tarjeta con los datos del `TrainingCenter` del Director (`center_code`
  de solo lectura, `name`/`address`/`phone` editables) y botón **Guardar**. Debajo, tabla de
  `InstitutionalUnit` (Nombre, Tipo, Estado) del centro con botón **+ Nueva sede** y edición/
  desactivación por fila. **Pantalla de LISTA → barra de paginación real** debajo de la tabla
  (‹ anterior · 1 2 3 … › siguiente, selector `page_size` 10/20/50, "Mostrando X–Y de N"),
  alineada a `page`/`page_size` de `GET /institutional-units`.
- **Pestaña "Catálogos" (candado/solo lectura):** lista de `Catalog` (código, nombre) con
  expansión a sus `CatalogDetail` (código, etiqueta, orden). Mensaje visible: *"Solo
  ADMIN_STAFF/SYSTEM_ADMIN pueden editar catálogos"* — sin botones de crear/editar/eliminar para
  este rol (el modal de edición existe como componente de `reference-mfe`, ver Pantalla 8, pero su
  trigger está deshabilitado aquí). **Pantalla de LISTA → paginación real** para la lista de
  catálogos (‹ anterior · 1 2 3 … › siguiente, selector `page_size` 10/20/50, "Mostrando X–Y de N"),
  alineada a `page`/`page_size` de `GET /catalogs`; los `CatalogDetail` expandidos usan su propia
  página si `N` supera el `page_size` (mismo patrón, sobre `GET /catalogs/{id}/details`).
- **Pestaña "Parámetros" (candado/solo lectura):** tabla de `Parameter` (clave, valor, tipo,
  descripción). Mensaje visible: *"Solo SYSTEM_ADMIN puede configurar parámetros del sistema"* —
  sin botón de edición para este rol (mismo modal de la Pantalla 8, trigger deshabilitado).
  **Pantalla de LISTA → paginación real** debajo de la tabla (‹ anterior · 1 2 3 … › siguiente,
  selector `page_size` 10/20/50, "Mostrando X–Y de N"), alineada a `page`/`page_size` de
  `GET /parameters`.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Guardar (Mi centro) | `PUT /training-centers/{id}` | actualiza nombre/dirección/teléfono |
| + Nueva sede | `POST /institutional-units` | crea unidad institucional |
| Editar sede | `PUT /institutional-units/{id}` | actualiza sede |
| Desactivar sede | `DELETE /institutional-units/{id}` | soft delete (`is_active=false`) |
| Ver catálogo | `GET /catalogs/{id}/details` | expande valores del catálogo (solo lectura) |
| Filtro Parámetros (clave/tipo) | `GET /parameters?key=&value_type=` | refresca tabla (solo lectura) |
| Paginación / `page_size` (Mi centro) | `GET /institutional-units?page=&page_size=` | refresca tabla de sedes |
| Paginación / `page_size` (Catálogos) | `GET /catalogs?page=&page_size=` | refresca lista de catálogos |
| Paginación / `page_size` (Parámetros) | `GET /parameters?page=&page_size=` | refresca tabla de parámetros |

**Estados:** *loading* (skeleton por pestaña) · *empty* ("Este centro aún no tiene sedes
registradas" / "Sin catálogos activos" / "Sin parámetros configurados") · *error* (banner de red)
· *success* (toast al guardar centro/sede) · *readonly* (candado visible + tooltip explicando la
restricción de rol en Catálogos y Parámetros).

```text
PROMPT STITCH
Pantalla "Administración — Datos de referencia" para el Administrador/Director de un centro SENA,
plataforma Horarios SENA, en español, responsive, dentro del app shell (nav lateral
"Administración" activo). Tres pestañas horizontales: "Mi centro", "Catálogos" y "Parámetros". En
"Mi centro": una tarjeta superior con los datos del centro de formación (código de centro en modo
solo lectura con un pequeño ícono de candado, y campos editables de nombre, dirección y teléfono,
con botón "Guardar"); debajo, una tabla de sedes/unidades institucionales con columnas Nombre,
Tipo y Estado, botón "+ Nueva sede" y acciones de editar/desactivar por fila, y debajo de esa
tabla una barra de paginación REAL y visible ("‹ anterior", números "1 2 3 …", "siguiente ›",
selector de tamaño de página 10/20/50 y "Mostrando 1–10 de 23"). En "Catálogos":
mostrar un banner sutil con ícono de candado y el texto "Solo ADMIN_STAFF/SYSTEM_ADMIN pueden
editar catálogos"; debajo, una lista paginada de catálogos (ej. Modalidad, Jornada) que al
expandirse muestra sus valores (código, etiqueta, orden) sin ningún botón de edición, con su
propia barra de paginación real ("‹ anterior · 1 2 3 · siguiente ›", selector de tamaño de
página, "Mostrando X–Y de N"). En "Parámetros":
mismo patrón de banner de solo lectura con el texto "Solo SYSTEM_ADMIN puede configurar
parámetros del sistema"; debajo, una tabla con columnas Clave, Valor, Tipo y Descripción, sin
botón de edición, con su barra de paginación real debajo ("‹ anterior · 1 2 3 · siguiente ›",
selector de tamaño de página 10/20/50, "Mostrando X–Y de N"). Incluir estados vacíos por pestaña
y skeleton de carga. Estilo institucional sobrio, verde SENA (placeholder), alto contraste WCAG
AA, objetivos táctiles ≥44px, responsive.

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

## Pantalla 8 — Form: Editar catálogo / valor de catálogo / parámetro

> **Nota de RBAC (leer antes de usar esta pantalla):** para el rol **Administrador de Centro /
> Director** este formulario **no es alcanzable**: los botones que lo abrirían (editar catálogo,
> editar valor de catálogo, editar parámetro) están **ocultos/deshabilitados** en la Pantalla 7,
> conforme a RN-REF-03 (catálogos → `ADMIN_STAFF`/`SYSTEM_ADMIN`) y RF-REF-03 (parámetros →
> `SYSTEM_ADMIN`). Se documenta aquí porque `reference-mfe` **es dueño de este componente** y debe
> aparecer en el inventario de pantallas del MFE aunque este rol no pueda activarlo; el mismo
> componente aparece **activo** para `ADMIN_STAFF`/`SYSTEM_ADMIN` en
> [06-backoffice.md § Pantalla 4](./06-backoffice.md#pantalla-4--parametrización--catálogos), que
> ya especifica la lista maestro-detalle donde vive el botón "Editar"/"Agregar valor"/"Nuevo
> parámetro" que dispara este modal.

- **Ruta:** modal sobre la lista maestro-detalle de catálogos/parámetros (Pantalla 7 en modo
  solo-lectura para este rol; [06-backoffice.md § Pantalla 4](./06-backoffice.md#pantalla-4--parametrización--catálogos)
  en modo edición para `ADMIN_STAFF`/`SYSTEM_ADMIN`) · **Rol:** `ADMIN_STAFF`/`SYSTEM_ADMIN`
  (edición); Administrador de Centro / Director (sin acceso, ver nota de RBAC) · **HU:** HU-19
  (*RF-REF-01, RF-REF-02*).
- **Endpoints:**
  - `PUT /api/v1/catalogs/{id}` (`REF_CATALOG_MANAGE`) — `CatalogUpdate{ code, name, description,
    is_active }` → `Catalog`.
  - `PUT /api/v1/catalogs/{catalog_id}/details/{id}` (`REF_CATALOG_MANAGE`) —
    `CatalogDetailUpdate{ code, label, display_order, is_active }` → `CatalogDetail`.
  - `PUT /api/v1/parameters/{id}` (`REF_PARAMETER_MANAGE`) — `ParameterUpdate{ value, value_type,
    description }` → `Parameter`. **Sin `DELETE`**: `parameter` no tiene `is_active`/`deleted_at`;
    los valores se superseden vía `PUT`, no se eliminan (ver `reference-data.yaml`).
- **Errores del contrato:** `400`, `401`, `403`, `404`, `409` (código duplicado en catálogo/valor),
  `422`.
- **MFE:** `reference-mfe` ([micro-frontends.md](../micro-frontends.md))

**Nota de precisión (no se inventa):** `ParameterUpdate` **no incluye `key`** — la clave del
parámetro es inmutable; en el modal el campo Clave se muestra de solo lectura. `value_type` sí es
editable en el schema, aunque cambiar el tipo de un valor ya en uso es una operación delicada — el
formulario debe advertirlo con un aviso no bloqueante, no bloquear el guardado (el contrato no
define una validación cruzada para esto).

**Propósito:** editar un catálogo, uno de sus valores, o el valor de un parámetro del sistema, en
un modal reutilizable independientemente de qué lista maestro-detalle lo invoque.

**Layout:** modal con 3 variantes según la entidad que se edita (una a la vez):
- **Editar catálogo:** campos **Código** (`code`), **Nombre** (`name`), **Descripción**
  (`description`, textarea opcional), interruptor **Activo** (`is_active`). Botón **Guardar**.
- **Editar valor de catálogo:** campos **Código** (`code`, único dentro del catálogo padre),
  **Etiqueta** (`label`), **Orden** (`display_order`, numérico opcional), interruptor **Activo**
  (`is_active`). Botón **Guardar**.
- **Editar parámetro:** campo **Clave** (`key`, solo lectura con icono de candado), campo **Valor**
  (`value`, input tipado según `value_type`: numérico/texto/interruptor/editor JSON), select **Tipo**
  (`value_type`, con aviso si se cambia), **Descripción** (`description`, textarea opcional). Botón
  **Actualizar valor** (no hay "Eliminar": el contrato no expone `DELETE` para parámetros).

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Guardar (catálogo) | `PUT /catalogs/{id}` | `200` → catálogo actualizado; `409` código duplicado |
| Guardar (valor de catálogo) | `PUT /catalogs/{catalog_id}/details/{id}` | `200` → valor actualizado; `409` código duplicado dentro del catálogo |
| Actualizar valor (parámetro) | `PUT /parameters/{id}` | `200` → nuevo `value`/`value_type`; sin historial expuesto por contrato |
| Cancelar | — | cierra sin guardar |

**Estados:** *loading* (botón con spinner) · *error* (`422` validación por campo; `409` código
duplicado) · *aviso no bloqueante* (cambio de `value_type` en un parámetro existente) · *success*
(toast "Cambios guardados") · *sin acceso para este rol* (Administrador de Centro/Director: el
trigger que abriría este modal aparece deshabilitado con tooltip explicando la restricción de rol,
según la Pantalla 7).

```text
PROMPT STITCH
Modal "Editar catálogo" (con sus variantes "Editar valor de catálogo" y "Editar parámetro del
sistema") para el rol ADMIN_STAFF/SYSTEM_ADMIN de la plataforma Horarios SENA, en español,
responsive, invocado desde la lista maestro-detalle de catálogos y parámetros. Variante "Editar
catálogo": modal centrado con título "Editar catálogo — Modalidad", campos "Código", "Nombre",
"Descripción" (textarea) y un interruptor "Activo", con botón primario "Guardar". Variante "Editar
valor de catálogo" (mostrar como segunda composición): título "Editar valor — Presencial", campos
"Código", "Etiqueta", "Orden" (numérico) e interruptor "Activo". Variante "Editar parámetro"
(mostrar como tercera composición): título "Editar parámetro — MAX_HOURS_PER_WEEK", campo "Clave"
en modo solo lectura con icono de candado, campo "Valor" (mostrar como numérico, ej. "48"), select
"Tipo" (integer/string/boolean/json) con un aviso ámbar "Cambiar el tipo puede afectar cómo se
interpreta el valor existente", y campo "Descripción", con botón primario "Actualizar valor" (sin
botón de eliminar). Mostrar un ejemplo de error en línea ("Este código ya existe en este catálogo",
rojo con icono) y el estado de carga (botón con spinner). Estilo institucional sobrio, alto
contraste WCAG AA, objetivos táctiles ≥44px.

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
_(pendiente — guardar en `../mockups/05-administrador/` y enlazar aquí: indicadores.png,
indicador-detalle.png, usuarios.png, usuario-form.png, usuario-detalle.png,
usuario-rol-modal.png, datos-referencia.png, datos-referencia-editar-modal.png)_
