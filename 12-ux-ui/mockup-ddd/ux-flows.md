<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: UX flows (user journeys) que conectan las 45 pantallas del mockup en recorridos end-to-end
fase: diseño (UX/UI)
estado: draft
dependencias_entrada: mockup-ddd/flows/01-auth.md…06-backoffice.md; screen-inventory.md; micro-frontends.md; navigation-map.md; _template-ux-flows.md
consumidores_siguientes: validación de diseño con usuarios reales; generación/ajuste de mockups en Stitch; construcción de los MFE (orden de navegación real)
tldr: 8 journeys (17 sub-flujos) que hilan las 45 pantallas de flows/*.md en recorridos completos por rol — acceso, núcleo Coordinador (crear→publicar horario), consultas de Coordinador, Instructor, Aprendiz, Administrador y back-office. Cada paso cita pantalla real + #número + MFE dueño; no se inventan pantallas.
decisiones_clave: la unidad de journey agrupa sub-flujos por intención de negocio (ej. "Acceso" cubre login+reset+sesión expirada); los pasos citan SIEMPRE el número de pantalla real de flows/*.md; los cruces de MFE/servicio se marcan explícitamente como composición
halts_registrados: hereda los halts ya documentados en flows/*.md (GAP-1/2/3 de 04-aprendiz.md); Auditoría ya dispone de contrato canónico y no conserva un HALT de API pendiente
-->

# UX Flows — Horarios SENA (mockup-ddd)

> **ESTADO: PRELIMINAR (v0).** Instrumento de descubrimiento y validación de diseño, no un
> diseño final. Conecta las **45 pantallas/modales** ya documentadas en `flows/01-auth.md` a
> `flows/06-backoffice.md` en **journeys end-to-end** por rol. No se inventa ninguna pantalla,
> endpoint ni transición que no esté ya en su archivo de flujo de origen — este documento solo
> **hila el orden de navegación**. Donde una transición depende de un supuesto o un gap ya
> documentado (RBAC, endpoint faltante, condición de carrera), se referencia el archivo de origen
> en vez de repetir el detalle completo.

## Cómo leer este documento

- Cada **paso** cita la pantalla real con la notación: **Nombre de pantalla** (`archivo.md` ·
  **#N** · `mfe-dueño`) → **acción del usuario** → **resultado / siguiente pantalla**.
- `archivo.md` es uno de `01-auth` … `06-backoffice` (dentro de `flows/`); `#N` es el número de
  pantalla dentro de ese archivo (mismo número que en `screen-inventory.md`).
- Cuando un paso **compone varios MFE** (ver [micro-frontends.md](micro-frontends.md)) se marca
  con "**[composición]**". Cuando cruza de servicio sin ser composición de UI (una pantalla
  resuelve un nombre contra otro dominio), se marca "**[cross-service]**".
- **Ramas alternativas / errores** usa el mismo código de error (`409`, `403`, etc.) que el
  archivo de flujo de origen — no se inventan códigos nuevos.
- Todo journey autenticado puede, en cualquier paso, caer en **Estados globales** (`01-auth` ·
  **#6** · `shell-host`: 403 / 404 / 500 / sesión expirada) — ver [§ Estados transversales](#estados-transversales-y-notificaciones) al final, no se repite en cada paso.

## Índice de journeys

| # | Journey | Actor(es) | Sub-flujos |
|---|---|---|---|
| 1 | [Acceso y sesión](#journey-1--acceso-y-sesión) | anónimo → todos los roles | Login+aterrizaje · Recuperar/restablecer contraseña · Sesión expirada |
| 2 | [Coordinador — Crear y publicar horario (CORE)](#journey-2--coordinador--crear-y-publicar-horario-core-end-to-end) | Coordinador Académico | único (end-to-end) |
| 3 | [Coordinador — Consultar disponibilidad](#journey-3--coordinador--consultar-disponibilidad) | Coordinador Académico | único |
| 4 | [Coordinador — Consultar ficha](#journey-4--coordinador--consultar-ficha) | Coordinador Académico | único |
| 5 | [Instructor](#journey-5--instructor) | Instructor | Ver mi horario · Gestionar disponibilidad · Registrar seguimiento |
| 6 | [Aprendiz](#journey-6--aprendiz) | Aprendiz | Ver mi horario · Notificación → horario |
| 7 | [Administrador](#journey-7--administrador-de-centro--director) | Administrador de Centro / Director | Gestionar usuario · Consultar KPIs |
| 8 | [Back-office / Soporte](#journey-8--back-office--soporte) | `ADMIN_STAFF`/`SYSTEM_ADMIN` | Generar documento · Editar/previsualizar plantilla · Consultar auditoría · Parametrizar catálogo |

---

## Journey 1 — Acceso y sesión

**Actor:** anónimo (pasa a autenticado tras login) · todos los roles del sistema (`COORDINATOR`,
`INSTRUCTOR`, `LEARNER`, `CENTER_DIRECTOR`/`ADMIN_STAFF`, `SYSTEM_ADMIN`).
**Precondición:** el usuario tiene una cuenta activa en `iam-service` (o, para el sub-flujo de
sesión expirada, tenía una sesión válida que venció).

### 1.A — Login → aterrizaje según rol

**Precondición:** el usuario no tiene sesión activa.

1. **Login** (`01-auth` · **#1** · `iam-mfe`) → ingresa correo + contraseña, clic **Ingresar** →
   `POST /auth/login` exitoso → `TokenResponse{ user.roles[] }`.
2. **App Shell** (`01-auth` · **#4** · `shell-host`) **[composición]** → se monta con `GET
   /auth/me` (`modules[]` construye el nav lateral); el cliente redirige según `user.roles`
   ([navigation-map.md](../navigation-map.md)):
   - `COORDINATOR` → **Dashboard / Inicio** (`02-coordinador` · **#1** · `shell-host`+
     `scheduling-mfe`+`academic-mfe`) **[composición]**.
   - `INSTRUCTOR` → **Mi horario** (`03-instructor` · **#1** · `scheduling-mfe`) — primer ítem del
     nav de Instructor (Mi horario, Mi disponibilidad, Seguimiento).
   - `LEARNER` → **Mi horario** (`04-aprendiz` · **#1** · `scheduling-mfe`) — primer ítem del nav
     de Aprendiz (Mi horario, Notificaciones).
   - `CENTER_DIRECTOR`/`ADMIN_STAFF` (Administrador de Centro) → **Panel de indicadores** (`05-administrador`
     · **#1** · `monitoring-mfe`) — primer ítem del nav (Indicadores, Administración).
   - `ADMIN_STAFF`/`SYSTEM_ADMIN` con acceso a soporte → aterriza igual en su área de
     Administrador y navega al ítem de nav **"Soporte"** para entrar a `06-backoffice.md`
     (ese flujo no define una pantalla de aterrizaje propia — ver encabezado de
     `06-backoffice.md`).

**Ramas alternativas / errores:**
- Credenciales inválidas → `401 INVALID_CREDENTIALS` → banner de error en **#1**, permanece en Login.
- Cuenta bloqueada/inactiva → `401 ACCOUNT_LOCKED`/`ACCOUNT_INACTIVE` → banner específico en **#1**.
- Demasiados intentos → `429 RATE_LIMIT_EXCEEDED` → banner en **#1**.
- Clic "¿Olvidó su contraseña?" → salta al sub-flujo **1.B**.

### 1.B — Recuperar / restablecer contraseña

**Precondición:** el usuario no recuerda su contraseña (o llega desde el enlace de 1.A).

1. **Login** (`01-auth` · **#1** · `iam-mfe`) → clic **¿Olvidó su contraseña?** → navega a
   **Recuperar contraseña**.
2. **Recuperar contraseña** (`01-auth` · **#2** · `iam-mfe`) → ingresa correo, clic **Enviar
   enlace** → `POST /auth/password-reset/request` → **202 siempre** (no revela si el correo
   existe) → mensaje neutro "Si el correo existe, enviaremos instrucciones".
3. El usuario recibe el enlace (fuera del sistema, por correo) con `token` → abre **Nueva
   contraseña** (`01-auth` · **#3** · `iam-mfe`, ruta `/reset-password?token=…`).
4. **Nueva contraseña** (**#3**) → ingresa y confirma la nueva contraseña, clic **Guardar** →
   `POST /auth/password-reset/confirm{ token, new_password }` → `204` → confirmación → navega a
   **Login** (**#1**).

**Ramas alternativas / errores:**
- Token expirado o ya usado → `400 RESET_TOKEN_EXPIRED` en **#3** → opción "Solicitar uno nuevo"
  (vuelve al paso 2 de este sub-flujo).
- `429` en el paso 2 (rate-limit de solicitudes de reset).

### 1.C — Sesión expirada → login

**Precondición:** el usuario tenía una sesión activa; el `refresh_token` venció o fue revocado.

1. Cualquier pantalla autenticada → una llamada dispara `POST /auth/refresh` (`iam.yaml`) → `401`
   → el shell limpia la sesión local.
2. **Estados globales** (`01-auth` · **#6** · `shell-host`, variante "Sesión expirada") → sin top
   bar ni nav; redirección automática a `/login` tras una breve pausa (o botón inmediato "Ir a
   iniciar sesión").
3. **Login** (`01-auth` · **#1** · `iam-mfe`) → el usuario vuelve a autenticarse → continúa en
   **1.A** desde el paso 1.

---

## Journey 2 — Coordinador: Crear y publicar horario (CORE, end-to-end)

**Nombre:** Construir un horario de ficha, resolver sus conflictos y publicarlo.
**Actor/Rol:** Coordinador Académico (`COORDINATOR`, scope `TRAINING_CENTER`).
**Precondición:** el coordinador tiene sesión activa y al menos una ficha `EXECUTION` en su
centro sin horario `PUBLISHED` vigente para el período que va a crear.

**Pasos:**

1. **Dashboard / Inicio** (`02-coordinador` · **#1** · `shell-host`+`scheduling-mfe`+
   `academic-mfe`) **[composición]** → clic en el único botón primario **"Crear horario"** →
   navega a Crear/editar horario en modo alta.
   - *Entrada alternativa:* desde **Horarios (lista)** (`02-coordinador` · **#2** ·
     `scheduling-mfe`) → clic **"Nuevo horario"** → mismo destino.
2. **Crear / editar horario** (`02-coordinador` · **#4** · `scheduling-mfe`) → completa
   `ficha_id`, `period`, `name` → `POST /schedules` → `201`, `status=DRAFT` → permanece en **#4**
   ya en modo edición del horario recién creado.
3. **#4** → clic **"Agregar sesión"** → abre **Modal: Agregar/editar sesión** (`02-coordinador` ·
   **#5** · `scheduling-mfe`) en modo alta. El modal resuelve selectores **[cross-service]**:
   competencias (academic-management-service vía `program_id` de la ficha), instructores
   (actors-service), ambientes (training-environment-service), franjas (`GET /time-slots`).
4. **Modal Agregar sesión** (**#5**) → completa competencia, instructor, ambiente, franja, fecha
   → confirma → `POST /schedules/{id}/sessions`.
   - **Rama de error (conflicto 409):** `409 INSTRUCTOR_DOUBLE_BOOKED` o
     `409 ENVIRONMENT_DOUBLE_BOOKED` → error inline con icono+texto bajo el campo Instructor o
     Ambiente; **el modal permanece abierto**; el coordinador corrige instructor/ambiente/franja
     y reintenta el mismo paso.
   - **Éxito:** `201` → el modal se cierra, la fila aparece en la tabla de **#4** con una
     confirmación breve (toast).
5. Repite el paso 3–4 tantas veces como sesiones requiera el horario (agregar, o "Editar"/
   "Cancelar"/"Eliminar" sobre filas ya creadas — mismo modal **#5** en modo edición, o `POST
   /sessions/{id}/cancel` / `DELETE /sessions/{id}`).
6. **#4** → clic **"Validar"** → `POST /schedules/{id}/validate` → `200`,
   `status: DRAFT → UNDER_REVIEW` (el motor de conflictos corre en el servidor; el horario puede
   quedar con conflictos detectados).
7. Si `status=UNDER_REVIEW` y hay conflictos: **#4** muestra un banner persistente **"Este horario
   tiene N conflictos sin resolver"** con acceso directo → navega a **Panel de conflictos**
   (`02-coordinador` · **#7** · `scheduling-mfe`). El botón **"Publicar"** de **#4** queda
   deshabilitado (candado + tooltip) mientras `N > 0`.
8. **Panel de conflictos** (**#7**) → revisa las tarjetas (`conflict_type`, sesiones afectadas,
   fecha de detección) → clic **"Marcar como resuelto"** en una tarjeta pendiente → abre **Modal:
   Resolver conflicto** (`02-coordinador` · **#8** · `scheduling-mfe`).
9. **Modal Resolver conflicto** (**#8**) → revisa el detalle (sin campo de notas — el contrato no
   lo acepta) → clic **"Confirmar resolución"** → `POST /conflicts/{id}/resolve` → `200`,
   `is_resolved=true` → el modal se cierra, la tarjeta pasa a "Resuelto" en **#7**.
   - **Rama de error:** `409` (el conflicto ya fue resuelto por otro usuario, condición de
     carrera) → banner "Este conflicto ya fue resuelto" con botón "Entendido" → refresca la
     lista al cerrar.
10. Repite el paso 8–9 hasta que `N=0` (estado positivo "Sin conflictos — este horario puede
    publicarse" en **#7**).
11. Vuelve a **Crear / editar horario** (**#4**) → el botón **"Publicar"** ya está habilitado →
    clic → abre **Modal: Confirmar publicación** (`02-coordinador` · **#6** · `scheduling-mfe`).
12. **Modal Confirmar publicación** (**#6**) → al abrir, `GET /schedules/{id}/conflicts?
    is_resolved=false` recalcula (último chequeo, por si hubo una condición de carrera); si
    `N=0` muestra "Sin conflictos pendientes — listo para publicar" con el botón habilitado →
    clic **"Confirmar publicación"** → `POST /schedules/{id}/publish` → `200`,
    `status: UNDER_REVIEW → PUBLISHED` (inmutable).
    - **Rama de error (conflicto tardío):** `409 UNRESOLVED_CONFLICTS` → banner crítico, botón se
      deshabilita, enlace **"Ir al Panel de conflictos"** → vuelve al paso 8.
    - **Rama de error (versión desactualizada):** `409 ROW_VERSION_MISMATCH` → banner "El horario
      cambió, recarga e intenta de nuevo".
13. Éxito → el modal se cierra y navega a **Detalle de horario** (`02-coordinador` · **#3** ·
    `scheduling-mfe`, solo lectura) → el horario se muestra con badge **PUBLICADO** — **FIN del
    journey**.

**Ramas alternativas / errores (resumen transversal del journey):**
- Cualquier mutación sobre el horario cuando ya no está `DRAFT` → `409 SCHEDULE_IMMUTABLE`
  (agregar/editar/eliminar sesión, paso 4–5).
- El coordinador puede abandonar en cualquier punto y retomar desde **Horarios (lista)** (**#2**)
  filtrando por `status=DRAFT`/`UNDER_REVIEW` — la fila "Ver" reabre **#4**.
- Una vez `PUBLISHED`, el horario es de solo lectura (**#3**); no hay retroceso a **#4** desde
  este journey (crear una nueva versión queda fuera de v0, ver `navigation-map.md`).

---

## Journey 3 — Coordinador: Consultar disponibilidad

**Actor/Rol:** Coordinador Académico.
**Precondición:** el coordinador necesita saber qué ambiente o instructor está libre en una
fecha/franja antes de agregar una sesión (típicamente durante el Journey 2, paso 4).

**Pasos:**

1. **App Shell** (`01-auth` · **#4** · `shell-host`) → clic en el ítem de nav **"Disponibilidad"**
   → navega a Disponibilidad.
2. **Disponibilidad** (`02-coordinador` · **#9** · `environment-mfe`+`actors-mfe`)
   **[composición]** → fija fecha + franja horaria (compartida por ambos paneles) → pestaña
   **"Ambientes"**: `GET /training-environments?available_date=&available_start_time=&
   available_end_time=` refresca las tarjetas con badge Disponible/No disponible.
   - Cambia a la pestaña **"Instructores"**: `GET /instructors` + `GET
     /instructors/{id}/availability-exceptions?from=&to=` por candidato (cruce en cliente,
     documentado como supuesto v0 en `02-coordinador.md`) marca Disponible/Con excepción.
3. **#9**, pestaña Ambientes → clic **"Ver detalle"** en una tarjeta → `GET
   /training-environments/{id}` → navega a **Detalle de ambiente / disponibilidad**
   (`02-coordinador` · **#10** · `environment-mfe`).
4. **Detalle de ambiente** (**#10**) → ajusta el rango de fechas → revisa el KPI "Ocupación en
   el rango" y la grilla semanal "Ocupación por franja" (Ocupada / Libre / Mantenimiento) →
   opcionalmente **"Ver reporte de utilización (horas)"** (detalle complementario).
5. **"Volver a Disponibilidad"** → regresa a **#9**. El coordinador usa lo aprendido (ambiente/
   instructor libre) para completar el **Modal: Agregar/editar sesión** del Journey 2 (paso 4).

**Ramas alternativas / errores:**
- Sin resultados que cumplan el filtro → estado *empty* en el panel correspondiente de **#9**.
- El ambiente no tiene franjas de disponibilidad configuradas → *empty* en **#10**
  ("Este ambiente no tiene franjas de disponibilidad configuradas").
- Para instructores no existe endpoint agregado de "disponibles" (`GET
  /instructors/available` no existe en el contrato); la pantalla compone el dato en cliente —
  gap documentado en `02-coordinador.md` § Pantalla 9, a validar con backend.

---

## Journey 4 — Coordinador: Consultar ficha

**Actor/Rol:** Coordinador Académico.
**Precondición:** el coordinador necesita revisar los datos completos de una ficha (programa,
jornada, modalidad) o ver rápidamente sus horarios asociados.

**Pasos:**

1. **App Shell** (`01-auth` · **#4** · `shell-host`) → clic en el ítem de nav **"Fichas"** →
   navega a Fichas. *(Entrada alternativa desde Dashboard: tarjeta KPI "Fichas activas" en
   `02-coordinador` · **#1** → `GET /fichas?status=EXECUTION` → mismo destino, ya filtrado.)*
2. **Fichas** (`02-coordinador` · **#11** · `academic-mfe`) → filtra por programa/estado/fecha →
   clic en una fila → `GET /fichas/{id}` → abre un panel lateral rápido con los datos completos.
3. Panel lateral rápido (dentro de **#11**) → clic **"Ver detalle completo"** → navega a
   **Detalle de ficha** (`02-coordinador` · **#12** · `academic-mfe`).
4. **Detalle de ficha** (**#12**) → revisa secciones "Programa" (`GET
   /training-programs/{id}`, **[cross-service]**) y "Datos de la ficha"; en la sección
   **"Horarios de esta ficha"** (`GET /schedules?ficha_id=`) ve el widget-resumen (top 5, sin
   paginación propia) de los horarios asociados.
5. **#12** → clic en una fila del widget de horarios → `GET /schedules/{id}` → navega a
   **Detalle de horario** (`02-coordinador` · **#3**, si `status` es `PUBLISHED`/`ARCHIVED`) o a
   **Crear/editar horario** (`02-coordinador` · **#4**, si `DRAFT`/`UNDER_REVIEW`) — misma regla
   de bifurcación por estado que en el Journey 2.
   - *Alternativa:* clic **"Ver todos en Horarios"** → navega a **Horarios (lista)**
     (`02-coordinador` · **#2**) con el filtro `ficha_id` preaplicado.
6. **"Volver a Fichas"** → regresa a **#11**.

**Ramas alternativas / errores:**
- La ficha aún no tiene horarios → widget vacío en **#12** ("Esta ficha aún no tiene horarios")
  con enlace **"Crear horario"** → abre **Crear/editar horario** (**#4**) en modo alta con
  `ficha_id` preasignado → continúa como Journey 2 desde su paso 2.
- Alta de ficha nueva (`POST /fichas`) queda **fuera de alcance de v0** — no hay pantalla de alta
  documentada en `02-coordinador.md` § Pantalla 11.

---

## Journey 5 — Instructor

**Actor/Rol:** Instructor.
**Precondición:** el instructor tiene sesión activa y al menos una sesión de horario `PUBLISHED`
asignada (para 5.A), o una ficha bajo seguimiento (para 5.C).

### 5.A — Ver mi horario → Detalle de sesión

1. **Mi horario (semana)** (`03-instructor` · **#1** · `scheduling-mfe`) — aterrizaje tras login
   (Journey 1.A) → navega semanas con ◀/▶ (`GET /sessions?instructor_id=&from=&to=`) → clic en
   una tarjeta de sesión → `GET /sessions/{id}` → abre **Detalle de sesión** (`03-instructor` ·
   **#2** · `scheduling-mfe`, panel lateral).
2. **Detalle de sesión** (**#2**) → consulta ficha/competencia/ambiente/notas resueltos
   **[cross-service]** (academic-management-service, training-environment-service) → cierra (X)
   → vuelve a **#1**.

**Ramas alternativas / errores:** el instructor no tiene edición aquí (`scope_type =
OWN_SCHEDULE` es de solo lectura); una sesión `CANCELLED` se muestra tachada + icono en ambas
pantallas, nunca solo color; sin sesiones publicadas esa semana → *empty* en **#1**.

### 5.B — Gestionar disponibilidad (crear excepción)

**Precondición:** el instructor necesita bloquear una franja (incapacidad, vacaciones, comisión,
permiso, capacitación u otro) para que el motor de conflictos no lo asigne ahí.

1. **App Shell** → nav **"Mi disponibilidad"** → **Mi disponibilidad** (`03-instructor` · **#3**
   · `actors-mfe`) → `GET /instructors/{id}/availability-exceptions` lista las excepciones
   vigentes/futuras → clic **"+ Nueva excepción"** → abre **Modal/Form: Crear excepción de
   disponibilidad** (`03-instructor` · **#4** · `actors-mfe`).
2. **Modal Crear excepción** (**#4**) → selecciona tipo, inicio, fin, descripción opcional →
   **"Guardar"** → `POST /instructors/{id}/availability-exceptions` → crea el bloqueo, cierra el
   modal, refresca la lista de **#3** con toast "Excepción registrada".

**Ramas alternativas / errores:**
- Validación en línea: `end_datetime` debe ser posterior a `start_datetime`.
- Error de red → banner dentro del modal, el modal permanece abierto para no perder lo digitado.
- **Eliminar** una excepción (fila de **#3**) → `DELETE
  /instructors/{id}/availability-exceptions/{exception_id}` → quita el bloqueo.
- **No existe "editar"**: el contrato no expone `PUT`/`PATCH` sobre la excepción — el patrón real
  es eliminar y volver a crear (gap documentado en `03-instructor.md` § Pantalla 4).

### 5.C — Registrar seguimiento de ficha

**Precondición:** el instructor tiene una ficha asignada en seguimiento (normativa SENA: mínimo
mensual para fichas en Ejecución).

1. **App Shell** → nav **"Seguimiento"** → **Seguimiento de ficha** (`03-instructor` · **#5** ·
   `monitoring-mfe`) → selecciona ficha (`GET /ficha-trackings?assigned_instructor_id=`) → ve
   resumen de riesgo e histórico de `tracking_session` → clic **"+ Registrar seguimiento"** →
   abre **Form: Registrar seguimiento** (`03-instructor` · **#6** · `monitoring-mfe`).
2. **Form Registrar seguimiento** (**#6**) → completa tipo de sesión, fecha, asistentes/total,
   avance curricular (%), observaciones, "Requiere seguimiento adicional" → **"Guardar"** →
   `POST /ficha-trackings/{id}/tracking-sessions` → crea el registro **append-only** (el
   `attendance_percentage` lo calcula el servidor) → cierra el modal, refresca **#5** con toast
   "Seguimiento registrado".

**Ramas alternativas / errores:**
- Validación en línea: `attendance_count ≤ total_learners`; `curriculum_progress_percentage`
  entre 0–100.
- Si `requires_follow_up=true` → aviso adicional "Se generará una alerta de seguimiento" (el
  `alert-worker` puede generar una alerta asociada).
- Gap RBAC documentado (`03-instructor.md` § Pantalla 5): `listFichaTrackings` exige
  `MON_DASHBOARD_FULL`; se asume que el scope `OWN` del JWT acota al instructor, a confirmar con
  backend.

---

## Journey 6 — Aprendiz

**Actor/Rol:** Aprendiz (`LEARNER`).
**Precondición:** el aprendiz tiene sesión activa y su ficha tiene un horario `PUBLISHED`
vigente (para 6.A). Uso previsto: consulta desde móvil, mobile-first.

### 6.A — Ver mi horario → Detalle de clase

1. **Mi horario (semana)** (`04-aprendiz` · **#1** · `scheduling-mfe`) — aterrizaje tras login
   (Journey 1.A) → navega semanas (◀/▶) → tap en una tarjeta de sesión → `GET /sessions/{id}` →
   navega a **Detalle de clase/sesión** (`04-aprendiz` · **#3** · `scheduling-mfe`).
2. **Detalle de clase/sesión** (**#3**) → revisa franja, competencia, instructor, ambiente y nota
   de cambio (si existe) → **"‹ Volver"** → regresa a **#1**, misma semana visible.

**Ramas alternativas / errores:** sesión `CANCELLED` con tratamiento visual distinto (tachado +
icono) en ambas pantallas; semana sin horario publicado → *empty* en **#1**; sesión ya no
disponible → *not-found* en **#3** con botón "‹ Volver a Mi horario"; sin conexión → banner
offline tolerante (design-system §1.4) en ambas.

### 6.B — Notificación → Detalle → ir al horario

1. **Panel de notificaciones** (`01-auth` · **#5** · `shell-host`+`notification-service`, overlay de la
   campana, disponible en cualquier pantalla autenticada) **[composición]** → tap en una tarjeta
   del top-5 → `GET /notifications/{id}` → navega directo al detalle (mismo destino que el
   paso 2 de abajo).
   - *Alternativa:* **"Ver todas"** en el panel → navega a **Notificaciones**
   (`04-aprendiz` · **#2** · `shell-host`+`notification-service`, bloqueado hasta formalizar `GET /notifications`).
2. **Notificaciones** (**#2**) → lista paginada por cursor (pendiente `GET /notifications`) → tap en
   una tarjeta → `GET /notifications/{id}` → navega a **Detalle de notificación** (`04-aprendiz` ·
   **#4** · `shell-host`+`notification-service`).
3. **Detalle de notificación** (**#4**) → lee asunto, resumen completo, estado de entrega
   (`send_status`) → si `generated_alert_id` es `null` (notificación manual), botón **"Ir al
   horario"** visible → navega a **Mi horario** (`04-aprendiz` · **#1**) — **navegación
   genérica, no deep-link a la sesión** (no existe FK `sent_notification`/`generated_alert` →
   `schedule`/`class_session`, GAP-3 de `04-aprendiz.md`).

**Ramas alternativas / errores:**
- `send_status=FAILED` → badge crítico + `failure_reason` visible.
- Si `generated_alert_id` **no** es null (alerta automática de KPI académico) → el botón "Ir al
  horario" **no se muestra** (no aplica).
- Notificación ya no disponible → *not-found* en **#4** con botón "‹ Volver a Notificaciones".
- Gaps RBAC documentados (`04-aprendiz.md`): GAP-1 (`SCH_VIEW_OWN` no cableado en
  `scheduling.yaml`), GAP-2 (`MON_NOTIFICATION_VIEW` no está en la matriz de roles) — se asumen
  para v0, a confirmar con backend antes de construir.

---

## Journey 7 — Administrador de Centro / Director

**Actor/Rol:** Administrador de Centro / Director (`CENTER_DIRECTOR`/`ADMIN_STAFF`).
**Precondición:** el administrador tiene sesión activa con scope `TRAINING_CENTER`.

### 7.A — Gestionar usuario (crear, detalle, asignar/revocar rol)

1. **App Shell** → nav **"Administración"** → **Administración — Usuarios** (`05-administrador`
   · **#3** · `iam-mfe`) → filtra por rol/estado → clic **"+ Nuevo usuario"** → abre **Form:
   Crear/editar usuario** (`05-administrador` · **#4** · `iam-mfe`) en modo alta.
2. **Form Crear usuario** (**#4**, modo alta) → completa correo, nombre, apellido, tipo de actor,
   actor vinculado (opcional), rol inicial, centro (opcional) → **"Crear"** → `POST /users` →
   `201` → tarjeta de confirmación con **contraseña temporal** (caduca en 72 h) → cierra, vuelve
   a **#3** con la lista refrescada.
   - **Rama de error:** `409` correo ya registrado → error inline bajo Correo; `422` validación
     por campo.
3. *Alternativa (editar/gestionar un usuario existente):* **#3** → clic en una fila → `GET
   /users/{id}` → abre **Detalle de usuario** (`05-administrador` · **#5** · `iam-mfe`, panel
   lateral, 3 pestañas).
4. **Detalle de usuario** (**#5**), pestaña **Perfil** → botón **"Editar"** → reabre **#4** en
   modo edición (correo bloqueado, sin rol inicial/centro) → **"Guardar"** → `PUT /users/{id}` →
   `200` → toast "Usuario actualizado", vuelve a **#5**.
   - *Alternativa:* botón **"Desactivar"** → modal de confirmación → `POST
     /users/{id}/deactivate` → `204` → usuario pasa a Inactivo, sus sesiones se revocan.
5. **#5**, pestaña **Roles** → botón **"Asignar rol"** → abre **Modal: Asignar/revocar rol**
   (`05-administrador` · **#6** · `iam-mfe`) en modo asignar → selecciona rol, centro (opcional),
   expiración (opcional) → **"Asignar"** → `POST /users/{id}/roles` → `201` → chip de rol
   agregado en **#5**.
   - **Rama de error:** `409` el usuario ya tiene ese rol asignado.
   - *Revocar:* clic **×** en un chip → **#6** en modo revocar (confirmación) → **"Revocar"** →
     `DELETE /users/{id}/roles/{role_name}` → `204` → chip removido de **#5**.
6. **#5**, pestaña **Sesiones** → `GET /users/{id}/sessions` lista sesiones activas → **"Revocar"**
   por fila → `DELETE /users/{id}/sessions/{session_id}` → `204`.

**Ramas alternativas / errores:**
- Limitación de contrato (`05-administrador.md` § Pantalla 5): `iam.yaml` no expone `GET` de
  roles asignados — la pestaña Roles solo refleja lo asignado **durante la sesión de trabajo
  actual**, no un historial persistente.
- `403` en cualquier acción de gestión si el usuario no tiene `IDENTITY_USER_MANAGE`/
  `IDENTITY_ROLE_ASSIGN`.

### 7.B — Consultar KPIs → Drill-down

1. **Panel de indicadores (KPIs)** (`05-administrador` · **#1** · `monitoring-mfe`) —
   aterrizaje tras login (Journey 1.A) → filtra por tipo de KPI/estado/rango de fechas → revisa
   las 3 tarjetas agregadas y la tabla densa (top N, widget de resumen) → clic en una fila de la
   tabla → navega a **Drill-down de KPI** (`05-administrador` · **#2** · `monitoring-mfe`) con
   `ficha_tracking_id` + `kpi_type_code` de esa fila.
2. **Drill-down de KPI** (**#2**) → ajusta el rango de fechas → revisa el gráfico de línea
   temporal contra el `threshold_value` y la tabla de mediciones (paginada por cursor) → clic
   **"‹ Volver al panel"** → regresa a **#1**.

**Ramas alternativas / errores:**
- Sin mediciones en el rango → *empty* en **#2**.
- `404` si `ficha_tracking_id` no existe o está fuera del scope del centro.
- Nota de alcance: `monitoring-service` solo publica reportes de su propio dominio (seguimiento
  de fichas) — **no** incluye utilización de ambientes ni carga de instructores, aunque
  `navigation-map.md` los mencione (gap documentado en `05-administrador.md` § Pantalla 1).

---

## Journey 8 — Back-office / Soporte

**Actor/Rol:** `ADMIN_STAFF`/`SYSTEM_ADMIN` (área de soporte, dentro del bucket "Administración").
**Precondición:** el usuario tiene sesión activa y navega al ítem de nav **"Soporte"** (con
sub-secciones Documentos, Plantillas, Auditoría, Parametrización — ver encabezado de
`06-backoffice.md`).

### 8.A — Generar documento

1. **Documentos** (`06-backoffice` · **#1** · `document-mfe`) → clic **"Generar documento"** →
   abre **Modal: Generar documento** (`06-backoffice` · **#6** · `document-mfe`).
2. **Modal Generar documento** (**#6**) → selecciona plantilla activa (`GET
   /document-templates?is_active=true`), dominio, servicio propietario, entidad propietaria
   (UUID), título, datos JSON opcional → **"Generar"** → `POST /documents/generate` → `202`,
   `status=GENERATING` → el modal se cierra, la fila aparece en **#1** con badge "Generando…" y
   se sondea `GET /documents/{id}` hasta `AVAILABLE`/`GENERATION_FAILED`.
3. **#1** → clic en la fila (ya `AVAILABLE`) → `GET /documents/{id}` → abre **Detalle de
   documento + versiones** (`06-backoffice` · **#5** · `document-mfe`) → botón **"Descargar
   versión vigente"** → `GET /documents/{id}/download-url` → abre la URL firmada (TTL 300 s) en
   pestaña nueva.

**Ramas alternativas / errores:**
- `GENERATION_FAILED` → badge crítico en **#1**/**#5**, acción **"Reintentar"** reabre **#6**
  con los campos prellenados del intento anterior.
- Descargar con `status ≠ AVAILABLE` → `409`, botón deshabilitado con tooltip.
- `storage_key` **nunca** se muestra (write-only) — la descarga siempre pasa por
  `download-url`.
- **Archivar** (fila de **#1**) → `DELETE /documents/{id}` → `204` → `status=ARCHIVED`.

### 8.B — Editar y previsualizar plantilla

1. **Plantillas de documento** (`06-backoffice` · **#2** · `document-mfe`) → clic **"Nueva
   plantilla"** o **"Editar"** en una fila → navega a **Editor / Preview de plantilla**
   (`06-backoffice` · **#7** · `document-mfe`).
2. **Editor de plantilla** (**#7**) → completa/edita código (bloqueado en edición), nombre, tipo
   de salida, cuerpo HTML/Handlebars → clic **"Previsualizar"** → abre el modal de
   previsualización (dentro de **#7**) → completa **Datos de muestra** (JSON) → **"Renderizar"**
   → `POST /document-templates/{id}/preview` → muestra `rendered_html` + avisa
   `missing_placeholders` (no bloqueante).
3. **#7** → clic **"Guardar"** → `POST /document-templates` (creación, `version=1`) o `PUT
   /document-templates/{id}` (edición, incrementa `version`) → toast "Plantilla guardada —
   versión N" → vuelve a **#2** con la lista refrescada.

**Ramas alternativas / errores:**
- `422`/`400` con detalle de campo (ej. `code` duplicado en creación).
- Salir del editor con cambios sin guardar → confirmación antes de abandonar.
- **Desactivar** plantilla (fila de **#2**) → `DELETE /document-templates/{id}` → `204` →
  `is_active=false`.

### 8.C — Consultar auditoría → Detalle

1. **Auditoría** (`06-backoffice` · **#3** · `audit-mfe`) → aplica filtros (actor, tipo de
   entidad, tipo de evento, servicio origen, rango de fechas) → tabla paginada por **cursor** →
   clic **"Ver payload"** en una fila → abre **Modal: Detalle de registro de auditoría**
   (`06-backoffice` · **#8** · `audit-mfe`) con el registro ya cargado (sin round-trip adicional).
2. **Modal Detalle de auditoría** (**#8**) → revisa el `payload` completo en visor JSON
   colapsable, copia `event_id`/JSON si lo necesita → **"Cerrar"** → vuelve a **#3** sin mutar
   nada (append-only, 100 % solo lectura).
   - *Alternativa:* botón **"Exportar"** en **#3** → descarga CSV/JSON de la selección filtrada.

**Ramas alternativas / errores:**
- El contrato canónico de `audit-query-api` define `GET /audit-records` y
  `GET /audit-records/{id}`; un deep link consulta el segundo endpoint dentro del scope RBAC.
- Rango de fechas inválido ("Desde" posterior a "Hasta") → validación en línea en **#3**.

### 8.D — Parametrizar catálogo / parámetro

1. **Parametrización / catálogos** (`06-backoffice` · **#4** · `reference-mfe`) → pestaña
   **"Catálogos"** (maestro-detalle) → clic **"Nuevo catálogo"** (o selecciona un catálogo y clic
   **"Agregar valor"**) → abre el modal correspondiente en **Formularios CRUD: catálogo, valor de
   catálogo y parámetro** (`06-backoffice` · **#9** · `reference-mfe`).
2. **Modal (#9)**, variante catálogo/valor → completa código (solo en alta; bloqueado en
   edición), nombre/etiqueta, descripción/orden, activo → **"Guardar"** → `POST`/`PUT
   /catalogs[/{id}]` o `POST`/`PUT /catalogs/{catalog_id}/details[/{id}]` → toast de éxito →
   cierra, refresca la tabla correspondiente en **#4**.
3. *Alternativa (parámetros):* **#4**, pestaña **"Parámetros del sistema"** → clic **"Editar"**
   en una fila → **#9**, variante parámetro (clave bloqueada, campo Valor tipado según
   `value_type`) → **"Actualizar valor"** → `PUT /parameters/{id}` → `200` (sin `DELETE`: los
   parámetros se superseden, no se eliminan).

**Ramas alternativas / errores:**
- `409` código/clave duplicado (dentro del catálogo padre para valores).
- Cambiar `value_type` de un parámetro existente → aviso no bloqueante (puede afectar cómo se
  interpreta el valor actual).
- Si el usuario no tiene `REF_CATALOG_MANAGE`/`REF_PARAMETER_MANAGE` → **#4** se muestra en modo
  solo lectura (sin botones de creación/edición, RN-REF-03) — este sub-flujo no es alcanzable;
  ver también el mismo componente **#9** documentado como inactivo para el rol Administrador de
  Centro en `05-administrador.md` § Pantalla 8 (Journey 7 no lo invoca).

---

## Estados transversales y notificaciones

Estas dos pantallas de `01-auth.md` no son destino final de ningún journey — son **marco
transversal** disponible desde cualquier pantalla autenticada de los 8 journeys anteriores:

- **Panel de notificaciones** (`01-auth` · **#5** · `shell-host`+`notification-service`) — overlay de
  la campana del top bar, en toda ruta autenticada. "Ver todas" navega a la pantalla de lista de
   Notificaciones del rol (hoy documentada en `04-aprendiz` · **#2**; el mismo patrón se reutiliza
   para Instructor/Administrador vía `notification-service` cuando se documente en sus flujos).
- **Estados globales** (`01-auth` · **#6** · `shell-host`) — se renderiza en lugar del contenido
  cuando cualquier endpoint de cualquier journey devuelve `403` (sin permiso) o `404` (no
  encontrado), o ante un error `500`/de red; la variante "Sesión expirada" es el destino del
  sub-flujo **1.C**. Ver el detalle completo de las 4 variantes en `01-auth.md` § Pantalla 6.

## Referencias

- Pantallas fuente: [flows/01-auth.md](flows/01-auth.md) ·
  [flows/02-coordinador.md](flows/02-coordinador.md) ·
  [flows/03-instructor.md](flows/03-instructor.md) ·
  [flows/04-aprendiz.md](flows/04-aprendiz.md) ·
  [flows/05-administrador.md](flows/05-administrador.md) ·
  [flows/06-backoffice.md](flows/06-backoffice.md)
- Índice maestro de pantallas: [screen-inventory.md](screen-inventory.md)
- Arquitectura de micro-frontends (quién construye qué): [micro-frontends.md](micro-frontends.md)
- Navegación prevista por rol: [../navigation-map.md](../navigation-map.md)
- Plantilla de origen: [../_template-ux-flows.md](../_template-ux-flows.md)
