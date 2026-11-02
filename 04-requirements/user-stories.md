# Historias de Usuario

> Estado: 🟡 En progreso | Última actualización: 2026-08-28
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Producto

> Fuente: [functional.md](./functional.md) · [02-domain/entities-and-rules.md](../02-domain/entities-and-rules.md) · [03-product/problem-framing.md](../03-product/problem-framing.md)

> **Historias de planeación vs. de ejecución.** Las historias `HU-01..HU-23` de este documento son las de **planeación** del producto (por rol de negocio). La construcción real se ejecutó con IDs por épica — **`HU-IAM-001..012`** (EP-IAM) y **`HU-NOTIF-001..008`** (EP-NOTIF) — documentadas en la sección [Historias construidas](#rol-sistema--plataforma-historias-construidas) con su estado, fecha e issue. El estado vivo por historia está en **GitHub Project #3**.

## Cómo leer este documento

Las historias se numeran `HU-##` y se agrupan por **rol**: Coordinador académico, Instructor, Aprendiz y Administrador/Director. Cada historia sigue el formato *Como… quiero… para…* con **criterios de aceptación** verificables, anclados a las reglas de negocio (RN-*) de [entities-and-rules.md](../02-domain/entities-and-rules.md) y a los requisitos funcionales (RF-*) de [functional.md](./functional.md). La trazabilidad completa está en [traceability-matrix.md](./traceability-matrix.md).

Roles (RBAC): `COORDINATOR`, `INSTRUCTOR`, `LEARNER`, `ADMIN_STAFF`/`CENTER_DIRECTOR`/`SYSTEM_ADMIN`.

---

## Rol: Coordinador académico

El coordinador es el usuario primario del MVP: construye y publica los horarios de su centro.

### HU-01 — Registrar una ficha de caracterización
**Como** coordinador **quiero** registrar una ficha con su número SENA, programa y cupo **para** poder construirle un horario. *(RF-ACAD-02)*

Criterios de aceptación:
- Puedo asociar la ficha a un programa existente y fijar su `max_capacity`.
- El `ficha_number` es único; el sistema rechaza duplicados (RN-ACAD-03).
- El `max_capacity` no puede aumentarse después de creado (RN-ACAD-06).

### HU-02 — Cambiar el estado de una ficha
**Como** coordinador **quiero** transicionar una ficha (p. ej. `INDUCTION → EXECUTION`) **para** habilitar la construcción de su horario. *(RF-ACAD-03)*

Criterios de aceptación:
- Solo puedo ejecutar transiciones autorizadas para mi rol (RN-ACAD-05).
- Al pasar a `EXECUTION` se emite `academic.ficha.opened`.
- No puedo cancelar una ficha si esa transición está reservada al director (RN-ACAD-05).

### HU-05 — Consultar ambientes disponibles
**Como** coordinador **quiero** ver los ambientes libres para una franja y fecha **para** elegir dónde ubicar una sesión. *(RF-ENV-04)*

Criterios de aceptación:
- La consulta responde en < 300 ms (p95) (NFR-PERF-01).
- La lista descuenta ambientes en mantenimiento y ya reservados (RN-ENV-03).
- No aparecen ambientes cuya `capacity` sea menor que el cupo de la ficha (RN-ENV-01).

### HU-06 — Consultar instructores disponibles
**Como** coordinador **quiero** ver los instructores habilitados y libres para una competencia y franja **para** asignarlos a una sesión. *(RF-ACT-03)*

Criterios de aceptación:
- La consulta responde en < 300 ms (p95) (NFR-PERF-02).
- Solo aparecen instructores con `CompetencyAssignment` activa para esa competencia (RN-ACT-02).
- No aparecen instructores con excepción de disponibilidad en esa franja (RN-ACT-02).

### HU-07 — Crear un borrador de horario
**Como** coordinador **quiero** crear un borrador de horario para una ficha en ejecución **para** empezar a agregarle sesiones. *(RF-SCH-01)*

Criterios de aceptación:
- Solo puedo crear el borrador si la ficha está en `EXECUTION` (RN-ACAD-04).
- Puedo tener varios `DRAFT` a la vez, pero un solo `PUBLISHED` por ficha/período (RN-SCH-02).
- El borrador queda ligado a mi centro (scope) (RN-IAM-03).

### HU-08 — Agregar sesiones de clase al borrador
**Como** coordinador **quiero** agregar sesiones (competencia + instructor + ambiente + franja + fecha) **para** ir armando el horario. *(RF-SCH-02, RF-SCH-04)*

Criterios de aceptación:
- La sesión dura entre 1 y 6 h y cae dentro de la disponibilidad del ambiente (RN-SCH-05).
- No puedo crear sesiones en domingo ni en festivos (RN-SCH-06).
- Al guardar, el sistema ejecuta la validación inmediata de conflictos (RN-SCH-04).

### HU-09 — Ver y resolver conflictos antes de publicar
**Como** coordinador **quiero** que el sistema detecte y liste los conflictos del horario **para** corregirlos antes de publicar. *(RF-SCH-03)*

Criterios de aceptación:
- El sistema clasifica cada conflicto (`INSTRUCTOR_DOUBLE_BOOKED`, `ENVIRONMENT_DOUBLE_BOOKED`, `SESSIONS_OVERLAP`, `ENVIRONMENT_MAINTENANCE`, `INSTRUCTOR_UNAVAILABLE`) con una descripción legible (RN-SCH-03).
- `POST /schedules/{id}/validate` valida un horario de 20 sesiones en < 2 s (NFR-PERF-03).
- Mientras existan conflictos activos, el botón/acción de publicar permanece bloqueado (RN-SCH-04).

### HU-10 — Publicar el horario
**Como** coordinador **quiero** publicar el horario sin conflictos con una sola acción **para** oficializarlo y comunicarlo. *(RF-SCH-05)*

Criterios de aceptación:
- Solo puedo publicar si la validación completa no arroja conflictos (RN-SCH-04).
- El horario publicado queda **inmutable**; para cambiarlo debo crear una nueva versión, que archiva la anterior (RN-SCH-01).
- Al publicar se emite `scheduling.schedule.published` (inicia seguimiento, notifica actores, habilita PDF).

### HU-11 — Gestionar aprendices de una ficha
**Como** coordinador **quiero** matricular aprendices y actualizar su estado **para** reflejar quién está activo en la ficha. *(RF-ACT-04)*

Criterios de aceptación:
- Un aprendiz `DROPOUT`/`TRANSFERRED`/`GRADUATED` no aparece en el horario (RN-ACT-03).
- No puedo reducir el cupo por debajo del número de aprendices activos (RN-ACAD-06).

### HU-13 — Administrar competencias del instructor
**Como** coordinador **quiero** registrar qué competencias puede impartir cada instructor y su tipo de vinculación **para** que el motor los ofrezca correctamente. *(RF-ACT-01)*

Criterios de aceptación:
- Puedo asignar/retirar competencias (`CompetencyAssignment`) a un instructor (RN-ACT-02).
- El tipo de vinculación fija el límite de horas semana (RN-ACT-01).

### HU-20 — Consultar KPIs de seguimiento por ficha
**Como** coordinador **quiero** ver los KPIs de asistencia y avance de mis fichas **para** detectar desviaciones a tiempo. *(RF-MON-02)*

Criterios de aceptación:
- Veo asistencia acumulada frente al mínimo reglamentario (80 %) (RN-MON-02).
- Cada medición es un registro histórico (append-only), no se sobrescribe (RN-CROSS-01).

### HU-21 — Atender y resolver alertas
**Como** coordinador **quiero** recibir y resolver alertas de riesgo **para** intervenir sobre fichas y aprendices en riesgo. *(RF-MON-03, RF-MON-04)*

Criterios de aceptación:
- Recibo la alerta según el nivel (`INFO`→`CRITICAL`) y su acción asociada (RN-MON-04).
- Al resolver, queda registrado quién, cuándo y las notas; la alerta no se elimina (`is_resolved = true`) (RN-MON-05).

### HU-22 — Descargar el horario en PDF
**Como** coordinador **quiero** descargar el horario publicado en PDF **para** difundirlo o archivarlo. *(RF-DOC-01)*

Criterios de aceptación:
- El PDF se genera bajo demanda y se descarga con una URL firmada de expiración corta (ADR-003).
- El binario no se guarda en base de datos; solo la `storage_key` (ADR-003).

### HU-23 — Crear un plan de mejoramiento
**Como** coordinador **quiero** crear un plan de mejoramiento para un aprendiz en riesgo **para** dar seguimiento a su recuperación. *(RF-MON-05)*

Criterios de aceptación:
- Para una ficha en estado crítico, debo crear el plan dentro de 5 días hábiles o el sistema emite `IMPROVEMENT_PLAN_OVERDUE` (RN-MON-06).

---

## Rol: Instructor

### HU-14 — Registrar mi disponibilidad y excepciones
**Como** instructor **quiero** declarar mis franjas disponibles y mis excepciones **para** que no me asignen clases cuando no puedo. *(RF-ACT-02)*

Criterios de aceptación:
- Una excepción registrada hace que el motor detecte `INSTRUCTOR_UNAVAILABLE` en esa franja (RN-SCH-03).
- El cambio se refleja en `GET /instructors/available`.

### HU-15 — Consultar mi horario de la semana
**Como** instructor **quiero** consultar mi horario vigente por semana **para** conocer mi carga con anticipación. *(RF-SCH-06)*

Criterios de aceptación:
- Veo solo sesiones de horarios `PUBLISHED` (RN-SCH-01).
- La consulta responde en < 500 ms (p95) (NFR-PERF-04).
- Conozco mi horario con ≥ 48 h de anticipación (meta de producto).

---

## Rol: Aprendiz

### HU-12 — Consultar el horario de mi ficha
**Como** aprendiz **quiero** ver el horario vigente de mi ficha **para** saber cuándo y dónde tengo clase. *(RF-SCH-06)*

Criterios de aceptación:
- Veo el horario `PUBLISHED` de mi ficha, con ambiente e instructor por sesión.
- Si estoy `DROPOUT`/`TRANSFERRED`/`GRADUATED` no aparezco como asistente (RN-ACT-03).
- La vista funciona en móvil (responsive, ≥ 360 px) (NFR-USA-02).

---

## Rol: Administrador / Director de centro

> **Nota de trazabilidad (construido).** Las historias `HU-16` (login), `HU-17` (RBAC por rol/centro) y `HU-18` (gestión de usuarios) son historias de **planeación**; su capacidad ya está **construida y ampliada** en `iam-service` bajo la épica **EP-IAM**. Mapa: `HU-16` → **HU-IAM-001** (login + lockout); `HU-17` → **HU-IAM-004/005/006** (catálogo RBAC + gestión de usuarios/roles + autorización feature+scope); `HU-18` → **HU-IAM-003** (contraseña temporal) + **HU-IAM-008** (provisión usuario↔actor). Ver detalle y criterios verificados en [Historias construidas](#rol-sistema--plataforma-historias-construidas).

### HU-16 — Iniciar sesión de forma segura
**Como** usuario **quiero** autenticarme con mis credenciales **para** acceder según mi rol. *(RF-IAM-01)*

Criterios de aceptación:
- Recibo `access_token` (15 min) y `refresh_token` (7 días) (RN-IAM-02).
- Tras 5 intentos fallidos la cuenta se bloquea 15 min; tras 10, 24 h (RN-IAM-01).
- En mi primer login debo cambiar la contraseña temporal (RN-IAM-05).

### HU-17 — Controlar el acceso por rol y centro
**Como** administrador **quiero** que cada usuario solo acceda a lo permitido por su feature y scope **para** proteger los datos entre centros. *(RF-IAM-03)*

Criterios de aceptación:
- Un acceso sin token devuelve 401; un acceso a otro centro devuelve 403 `SCOPE_VIOLATION` (NFR-SEC-01/02).
- Un coordinador solo opera dentro de su centro asignado (RN-IAM-03).

### HU-18 — Gestionar usuarios e instructores
**Como** administrador **quiero** crear usuarios y sus perfiles de actor **para** dar acceso al personal del centro. *(RF-IAM-02, RF-IAM-04)*

Criterios de aceptación:
- Al crear un instructor se crea de forma coordinada su usuario y su perfil en `actors-service` (RN-IAM-04).
- La contraseña temporal caduca en 72 h (RN-IAM-05).

### HU-19 — Administrar la jerarquía institucional y catálogos
**Como** administrador **quiero** mantener la jerarquía institucional y los catálogos del sistema **para** que el resto de módulos tenga datos de referencia consistentes. *(RF-REF-01, RF-REF-02)*

Criterios de aceptación:
- El `center_code` es inmutable y un centro pertenece a un único municipio (RN-REF-01/02).
- Solo `ADMIN_STAFF`/`SYSTEM_ADMIN` pueden editar catálogos; para el resto son solo lectura (RN-REF-03).

---

## Rol: Sistema / Plataforma (historias construidas)

> Historias de **ejecución** efectivamente construidas y verificadas en el ambiente **`dev`**. IDs por épica (no del backlog de planeación). El actor es la **plataforma / administrador de plataforma**, no un rol de negocio del MVP. Estado vivo por historia en **GitHub Project #3**.

### EP-IAM — `iam-service` (épica issue docs#79)

#### HU-IAM-001 — Login seguro con bloqueo y auditoría · ✅ Done·Dev (2026-08-28) · docs#80
**Como** plataforma **quiero** autenticar por credenciales, bloquear ante abuso y registrar cada intento **para** dar acceso seguro y trazable. *(RF-IAM-01, RF-IAM-05)*

Criterios verificados:
- Emite `access_token` (15 min) y `refresh_token` (7 días).
- Bloqueo tras 5 intentos fallidos (15 min) y tras 10 (24 h); reinicio en login exitoso.
- Registra cada intento en `audit_login` y expone `GET /auth/me` con el usuario autenticado.

#### HU-IAM-002 — Gestión de sesiones (refresh / logout / revocar) · ✅ Done·Dev (2026-08-28) · docs#81
**Como** plataforma **quiero** renovar, cerrar y revocar sesiones **para** controlar el ciclo de vida del acceso. *(RF-IAM-06)*

Criterios verificados:
- El `refresh_token` renueva el `access_token`; logout cierra la sesión.
- El usuario puede listar sus sesiones activas y revocarlas individualmente.

#### HU-IAM-003 — Contraseña temporal y reset · ✅ Done·Dev (2026-08-28) · docs#82
**Como** plataforma **quiero** entregar contraseñas temporales y permitir su cambio **para** onboarding seguro del personal. *(RF-IAM-02)*

Criterios verificados:
- La contraseña temporal caduca en 72 h y debe cambiarse en el primer login.
- Existe flujo de reset de contraseña.

#### HU-IAM-004 — Catálogo RBAC · ✅ Done·Dev (2026-08-28) · docs#83
**Como** plataforma **quiero** un catálogo de módulos, features y roles **para** sustentar la autorización. *(RF-IAM-03)*

Criterios verificados:
- Se administran módulos, features y roles como catálogo del sistema.

#### HU-IAM-005 — Gestión de usuarios y roles (scope / centro) · ✅ Done·Dev (2026-08-28) · docs#84
**Como** plataforma **quiero** crear usuarios y asignarles roles con alcance **para** reflejar la estructura organizativa. *(RF-IAM-03)*

Criterios verificados:
- Un rol puede ser global (`training_center_id = null`) o restringido a un centro.
- Se asignan/retiran roles a usuarios respetando el scope.

#### HU-IAM-006 — Autorización por feature + scope/centro · ✅ Done·Dev (2026-08-28) · docs#85
**Como** plataforma **quiero** autorizar cada operación por feature y alcance **para** aislar datos entre centros. *(RF-IAM-03)*

Criterios verificados:
- Acceso sin token → 401; acceso a otro centro → 403 (violación de scope).
- La autorización combina feature + scope/centro.

#### HU-IAM-007 — Eventos de dominio vía outbox · ✅ Done·Dev (2026-08-28) · docs#86
**Como** plataforma **quiero** publicar eventos de dominio de forma confiable **para** integrar otros servicios. *(RF-IAM-07)*

Criterios verificados:
- Patrón outbox publica hacia `iam-events` (p. ej. `session.started`, `iam.user.created`) con entrega at-least-once.

#### HU-IAM-008 — Provisión usuario ↔ actor · ⚠️ Parcial·Dev (lado iam Done, 2026-08-28) · docs#87
**Como** plataforma **quiero** coordinar la creación del usuario con su perfil de actor **para** mantener la invariante usuario↔actor. *(RF-IAM-04)*

Criterios verificados / estado:
- El lado `iam` emite `iam.user.created` con `actor_type` y `actor_id` (invariante de RF-IAM-04).
- La **saga E3** que materializa el perfil en `actors-service` queda **DIFERIDA** hasta que ese servicio exista.

#### HU-IAM-009 — Reporte de auditoría de login · ✅ Done·Dev (2026-08-28) · docs#88
**Como** plataforma **quiero** consultar el histórico de accesos **para** auditar la actividad. *(RF-IAM-08)*

Criterios verificados:
- `GET /reports/login-audit` con paginación por cursor.

#### HU-IAM-010 — JWT verificable + JWKS + rotación · ✅ Done·Dev (2026-08-28) · docs#89
**Como** plataforma **quiero** JWT verificables localmente por cada servicio **para** autorizar sin llamada síncrona a `iam`. *(RF-IAM-09)*

Criterios verificados:
- El JWT lleva los claims del proyecto; la clave pública se expone en `/.well-known/jwks.json`.
- Hay rotación de llaves de firma (DEC-008).

#### HU-IAM-011 — Observabilidad y sondas de salud · ✅ Done·Dev (2026-08-28) · docs#90
**Como** plataforma **quiero** trazas y sondas de salud **para** operar el servicio. *(NFR-OBS-04/06/07)*

Criterios verificados:
- Instrumentación OpenTelemetry; trazas visibles en Tempo.
- Split `/health` (liveness) y `/ready` (readiness con BD + broker).

#### HU-IAM-012 — Levantado local y prueba E2E · ✅ Done·Dev (2026-08-28) · docs#91
**Como** plataforma **quiero** el servicio corriendo localmente y probado extremo a extremo **para** validar la integración. *(E2E de integración)*

Criterios verificados:
- Servicio levantado en local y flujo E2E ejecutado con éxito (162 tests en CI).

### EP-NOTIF — `notification-service` (extraído de `monitoring`, ADR-005)

#### HU-NOTIF-001 — Envío por API asíncrono · ✅ Done·Dev (2026-08-28)
**Como** plataforma **quiero** aceptar solicitudes de notificación por API sin bloquear **para** desacoplar al emisor de la entrega. *(RF-NOTIF-01)*

Criterios verificados:
- La API valida y responde `202 Accepted`; la entrega ocurre de forma asíncrona.

#### HU-NOTIF-002 — Entrega dirigida por evento · ✅ Done·Dev (2026-08-28)
**Como** plataforma **quiero** generar notificaciones a partir de eventos de dominio **para** reaccionar a lo que ocurre en el sistema. *(RF-NOTIF-02)*

Criterios verificados:
- Consume eventos del broker y produce la notificación correspondiente.

#### HU-NOTIF-003 — Canales EMAIL e IN_APP · ✅ Done·Dev (2026-08-28)
**Como** plataforma **quiero** entregar por varios canales **para** llegar al destinatario por el medio adecuado. *(RF-NOTIF-03)*

Criterios verificados:
- Soporta canales `EMAIL` e `IN_APP`.

#### HU-NOTIF-004 — Resiliencia (retry / DLQ / idempotencia) · ✅ Done·Dev (2026-08-28)
**Como** plataforma **quiero** tolerar fallos sin duplicar ni perder mensajes **para** una entrega confiable. *(RF-NOTIF-04)*

Criterios verificados:
- Reintentos, DLQ para no entregables e **idempotencia por `event_id`** (probada: no duplica ante reintrega).

#### HU-NOTIF-005 — Plantillas de notificación · ✅ Done·Dev (2026-08-28)
**Como** plataforma **quiero** componer el contenido con plantillas **para** estandarizar los mensajes. *(RF-NOTIF-05)*

Criterios verificados:
- Gestiona plantillas por tipo/canal.

#### HU-NOTIF-006 — Consulta de notificaciones · ✅ Done·Dev (2026-08-28)
**Como** plataforma **quiero** consultar las notificaciones emitidas **para** dar visibilidad y soporte. *(RF-NOTIF-06)*

Criterios verificados:
- Endpoint `GET` para consultar notificaciones.

#### HU-NOTIF-007 — Observabilidad · ✅ Done·Dev (2026-08-28)
**Como** plataforma **quiero** trazas y sondas de salud **para** operar el servicio. *(RF-NOTIF-07)*

Criterios verificados:
- OpenTelemetry (exporta por OTLP/gRPC `:4317`); endpoints `/health` y `/ready`.

#### HU-NOTIF-008 — Publicación de `notification.notification.sent` · ✅ Done·Dev (2026-08-28)
**Como** plataforma **quiero** anunciar cada entrega **para** que otros servicios reaccionen. *(RF-NOTIF-07)*

Criterios verificados:
- Publica el evento `notification.notification.sent` al completar la entrega.

---

## Puntos abiertos

- **HU-11 / HU-12**: pendiente confirmar si un aprendiz puede pertenecer a más de una ficha activa (PA-04 en [vision.md](../03-product/vision.md)).
- Historias de **etapa productiva** (visitas a empresa, convenios) quedan fuera del MVP (ver [scope.md](../01-context/scope.md)).

## Referencias

- [functional.md](./functional.md) · [non-functional.md](./non-functional.md) · [traceability-matrix.md](./traceability-matrix.md)
- [02-domain/entities-and-rules.md](../02-domain/entities-and-rules.md)
- [03-product/product-backlog.md](../03-product/product-backlog.md)

## HU-REF-020 — Integración E2E real con IAM

> Responsable: Valery Sinai Trujillo Quintero | Épica: EP-REF | Issue: [docs#250](https://github.com/code-sena/design-software-docs/issues/250).
> Estado de esta adaptación: En progreso; pendiente de validación/merge en los repositorios originales. No se declara Done·Dev por los resultados de las copias personales.

**Como** equipo de integración, **quiero** levantar el flujo real entre Reference Data e IAM **para** autenticar y autorizar operaciones reproducibles sin ajustes locales no versionados.

| Criterio | Aceptación exigida |
|---|---|
| E1 | IAM inicia con JDK 21, reactor Maven raíz y migraciones oficiales; esquema validado |
| E2 | Usuarios/roles/campos de seguridad reproducibles en la base de validación; cambios de IAM en su repositorio responsable |
| E3 | Login de administrador emite JWT real con issuer/sub/exp y roles/features esperados |
| E4 | Reference Data verifica firma y feature real por endpoint; administrador GET/POST/PUT 200/201/200; aprendiz 403; token ausente/malformado/firma alterada 401 |
| Integración visual | El remote real carga dentro del shell, crea/edita/consulta un parámetro persistente y respeta permisos del IAM real; sin sesión fija del BFF |

DoR: repositorio responsable y variables de integración identificados. DoD: tests reales en verde, docs sincronizados, revisión QA/Arquitectura y PR fusionados a develop; board/hu-log actualizados por un responsable con permisos. Esta HU no implica cerrar las historias de otros aprendices.

### R1 de Reference Data — complemento individual de ingeniería

R1 es el reto asignado, no una HU nueva ni un reemplazo del ID HU-REF-020. Se exige outbox transaccional, consumidor idempotente con tabla de deduplicación, backoff exponencial, DLQ/replay y caos automatizado con cero pérdidas/efectos duplicados en el escenario medido. El efecto se define como actualización de la proyección operativa. Véanse [ADR-021](../05-architecture/decisions/records/ADR-021-reference-data-resilient-messaging.md) y [casos de prueba](../11-quality/reference-data-hu-ref-020-r1-validation.md).
## Referencias de ejecucion de Actors identificadas en QA

Los IDs y criterios de estas historias se mantienen en Project #3. Este indice enlaza solamente historias presentes en la evidencia publicada; no declara su estado.

| HU | Issue | Evidencia QA |
|----|-------|--------------|
| HU-ACT-005 / HU-ACT-025 | [#189](https://github.com/code-sena/design-software-docs/issues/189) / [#379](https://github.com/code-sena/design-software-docs/issues/379) | [Plan de mejoramiento](../11-quality/test-evidence-hu-act-005.md) |
| HU-ACT-012 / HU-ACT-026 | [#196](https://github.com/code-sena/design-software-docs/issues/196) / [#380](https://github.com/code-sena/design-software-docs/issues/380) | [Aprendices activos por ficha](../11-quality/test-evidence-hu-act-012.md) |
| HU-ACT-011 / HU-ACT-027 | [#195](https://github.com/code-sena/design-software-docs/issues/195) / [#381](https://github.com/code-sena/design-software-docs/issues/381) | [Reportes de seguimiento](../11-quality/test-evidence-hu-act-027.md) |
| HU-ACT-010 / HU-ACT-028 | [#194](https://github.com/code-sena/design-software-docs/issues/194) / [#382](https://github.com/code-sena/design-software-docs/issues/382) | [Planes de mejoramiento](../11-quality/test-evidence-hu-act-028.md) |

## HU-SHELL-019 — Menú por rol y por secciones (basado en features)

> Épica: EP-E2E-DEV | Issue: [docs#493](https://github.com/code-sena/design-software-docs/issues/493) | Dominio: shell | Estado: Backlog (docs-first: este criterio se actualiza antes que el código).

**Como** usuario del portal, **quiero** un menú lateral agrupado en secciones que solo muestre lo que mi rol puede usar, **para** encontrar mi trabajo rápido sin ver opciones de otros roles.

| Criterio | Aceptación exigida |
|---|---|
| E1 | El ítem es visible si el usuario tiene al menos uno de los features que exige (tabla de [visual-spec.md](../12-ux-ui/visual-spec.md) §4.2); `me.modules` ya no decide la visibilidad. **Reemplaza el criterio E2 de HU-001** ("el menú se deriva de `me.modules`") |
| E2 | Los ítems personales exigen además `me.actor_type`: "Mi horario" y "Mi disponibilidad" de instructor solo con `INSTRUCTOR`; "Mi horario" de aprendiz solo con `LEARNER`. COORDINATOR, CENTER_DIRECTOR y SYSTEM_ADMIN no los ven aunque tengan `SCH_VIEW_OWN` |
| E3 | Secciones Planeación, Formación, Documentos y Administración; el primer grupo (Inicio y lo personal) no lleva rótulo; una sección sin ítems visibles no muestra rótulo |
| E4 | Con los grants sembrados de develop: INSTRUCTOR 8 ítems, COORDINATOR 7, SYSTEM_ADMIN 13, LEARNER 3 |
| E5 | "Inicio" siempre visible; ninguna ruta cambia; el ítem activo expone `aria-current="page"`; el drawer móvil cumple el contrato de accesibilidad de visual-spec §4.1 |

**Razón:** con los grants reales y el filtro por módulo, un COORDINATOR veía 11 ítems (incluidos los dos "Mi …" ajenos) y un APRENDIZ veía "Horarios", "Parametrización" y "Datos de referencia". `SCH_VIEW_OWN` lo tienen también los roles de alcance GLOBAL o TRAINING_CENTER, así que el feature solo no basta: los ítems personales usan `actor_type`. `MeResponse` ya trae `features` y `actor_type`; no cambia el contrato. El filtro es solo de presentación: el backend sigue autorizando cada endpoint y cada MFE conserva sus guardas. Refina el Scenario 2 de HU-SHELL-018 (docs#490). Fuera de alcance: ítems o rutas nuevas, renombrar "Disponibilidad" (decisión abierta del dueño), tokens y anatomía de página.
