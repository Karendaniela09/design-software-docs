# Requisitos Funcionales

> Estado: 🟡 En progreso | Última actualización: 2026-08-28
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Producto

> Fuente: [02-domain/entities-and-rules.md](../02-domain/entities-and-rules.md) · [03-product/vision.md](../03-product/vision.md) · [09-microservices/service-catalog.md](../09-microservices/service-catalog.md)

## Cómo leer este documento

Los requisitos funcionales se numeran `RF-<MÓDULO>-##`, donde el módulo corresponde al bounded context/servicio dueño. Cada RF describe una capacidad observable del sistema y referencia las **reglas de negocio** (RN-*) de [entities-and-rules.md](../02-domain/entities-and-rules.md) que la gobiernan. La trazabilidad completa RF ↔ historia ↔ servicio ↔ ADR está en [traceability-matrix.md](./traceability-matrix.md).

Prefijos de módulo: `IAM` (identidad), `REF` (datos de referencia), `ACAD` (académico), `ENV` (ambientes), `SCH` (horarios — **CORE**), `ACT` (actores), `DOC` (documentos), `MON` (seguimiento — **CORE**), `NOTIF` (notificaciones), `AUD` (auditoría).

> **Estado de construcción (dev).** A la fecha de esta actualización, dos módulos están **construidos y verificados en el ambiente `dev`**: `IAM` (iam-service, 12/12 HU Done·Dev, épica **EP-IAM** / issue docs#79, historias **HU-IAM-001..012** / issues docs#80–#91) y `NOTIF` (notification-service, 8/8 HU Done·Dev, épica **EP-NOTIF**). El resto de módulos permanecen en especificación. Los ambientes `qa`/`staging`/`main` aún no tienen estos servicios promovidos (solo está avanzada la capa de datos). El estado vivo por historia se lleva en **GitHub Project #3**; estos `.md` son la SSOT de trazabilidad HU↔requisito. Ver [traceability-matrix.md](./traceability-matrix.md) y [user-stories.md](./user-stories.md).

---

## 1. Identidad y acceso — `iam-service`

| ID | Requisito | Regla / Nota |
|----|-----------|--------------|
| **RF-IAM-01** | El sistema debe autenticar usuarios por credenciales y emitir un `access_token` (15 min) y un `refresh_token` (7 días). Un usuario puede tener varias sesiones activas simultáneas. | RN-IAM-02 |
| **RF-IAM-02** | El sistema debe permitir crear usuarios con una contraseña temporal que caduca en 72 h y debe cambiarse en el primer login. | RN-IAM-05 |
| **RF-IAM-03** | El sistema debe autorizar cada operación por **feature + scope**: un rol puede ser global (`training_center_id = null`) o restringido a un centro; un coordinador solo opera en su centro. | RN-IAM-03 |
| **RF-IAM-04** | El sistema debe crear de forma coordinada el usuario y el perfil de actor: no puede existir un instructor sin usuario ni un usuario instructor sin perfil en `actors-service`. | RN-IAM-04 · **Parcial·Dev**: el lado `iam` está hecho — al crear un usuario emite `iam.user.created` con `actor_type`/`actor_id` (invariante de RF-IAM-04). La **saga E3** que materializa el perfil en `actors-service` está **DIFERIDA** hasta que exista ese servicio. |
| **RF-IAM-05** | El sistema debe bloquear la cuenta tras 5 intentos fallidos (15 min) y tras 10 (24 h); el contador se reinicia en login exitoso. | RN-IAM-01 |
| **RF-IAM-06** | El sistema debe gestionar el ciclo de vida de las sesiones: renovar el `access_token` con el `refresh_token`, cerrar sesión (logout), y listar y revocar las sesiones activas del usuario (`access_token` 15 min / `refresh_token` 7 días). | RN-IAM-02 |
| **RF-IAM-07** | El sistema debe publicar sus eventos de dominio mediante el patrón **outbox** hacia el topic/exchange `iam-events` (p. ej. `iam.user.created`, `session.started`), con entrega at-least-once. | ADR-001; RN-CROSS-01 |
| **RF-IAM-08** | El sistema debe exponer un reporte de auditoría de accesos `GET /reports/login-audit` con paginación por cursor. | RN-CROSS-01 |
| **RF-IAM-09** | El sistema debe emitir JWT **verificables localmente por cada servicio**: claims estándar del proyecto, exposición de la clave pública vía JWKS en `/.well-known/jwks.json` y **rotación** de llaves de firma. | DEC-008; NFR-SCALE-03 |

## 2. Datos de referencia — `reference-data-service`

| ID | Requisito | Regla / Nota |
|----|-----------|--------------|
| **RF-REF-01** | El sistema debe gestionar la jerarquía institucional Macrorregión → Microrregión → Departamento → Municipio → Centro. El `center_code` es asignado por el SENA y es inmutable. | RN-REF-01, RN-REF-02 |
| **RF-REF-02** | El sistema debe exponer catálogos del sistema como **solo lectura** para el usuario final; solo `ADMIN_STAFF`/`SYSTEM_ADMIN` los modifica. | RN-REF-03 |
| **RF-REF-03** | El sistema debe permitir a `SYSTEM_ADMIN` configurar parámetros (p. ej. `MAX_HOURS_PER_WEEK_STAFF`, `MIN_ATTENDANCE_PERCENTAGE`, tabla de festivos). | RN-REF-04, RN-SCH-06 |

## 3. Gestión académica — `academic-management-service`

| ID | Requisito | Regla / Nota |
|----|-----------|--------------|
| **RF-ACAD-01** | El sistema debe representar la estructura curricular Programa → Competencia → RAP (`LearningOutcome`), de solo lectura en los centros. | RN-ACAD-01, RN-ACAD-02 |
| **RF-ACAD-02** | El sistema debe registrar fichas de caracterización con `ficha_number` (proveniente de SOFIA Plus, único a nivel nacional) y `max_capacity` fijo, no aumentable. | RN-ACAD-03, RN-ACAD-06 |
| **RF-ACAD-03** | El sistema debe gobernar el ciclo de estados de la ficha (`INDUCTION → EXECUTION → PRODUCTIVE_STAGE → COMPLETED`, o `CANCELLED`) permitiendo solo las transiciones autorizadas por rol. Debe emitir `academic.ficha.opened`/`academic.ficha.closed`. | RN-ACAD-04, RN-ACAD-05 |

## 4. Ambientes de formación — `training-environment-service`

| ID | Requisito | Regla / Nota |
|----|-----------|--------------|
| **RF-ENV-01** | El sistema debe gestionar ambientes con tipo, capacidad y equipamiento. | RN-ENV-01, RN-ENV-04 |
| **RF-ENV-02** | El sistema debe permitir hasta 24 reglas de disponibilidad recurrentes por ambiente (6 días × 4 franjas), cada una con día de la semana y bloque horario. | RN-ENV-02 |
| **RF-ENV-03** | El sistema debe registrar mantenimientos; un mantenimiento que se solapa con una sesión impide o invalida su asignación (conflicto `ENVIRONMENT_MAINTENANCE`). Debe emitir `environment.maintenance.started`. | RN-ENV-03 |
| **RF-ENV-04** | El sistema debe exponer `GET /environments/available` calculando la disponibilidad efectiva (restando mantenimientos y reservas) en **< 300 ms (p95)**. | NFR-PERF-01 |

## 5. Motor de horarios — `scheduling-service` · **CORE**

| ID | Requisito | Regla / Nota |
|----|-----------|--------------|
| **RF-SCH-01** | El sistema debe permitir crear un **borrador** (`DRAFT`) de horario para una ficha en estado `EXECUTION`; solo puede existir un horario `PUBLISHED` por ficha y período. | RN-ACAD-04, RN-SCH-02 |
| **RF-SCH-02** | El sistema debe permitir agregar, editar y cancelar sesiones de clase que vinculan ficha + competencia + instructor + ambiente + franja + fecha. | Modelo `class_session` |
| **RF-SCH-03** | El sistema debe **detectar conflictos** y clasificarlos: `INSTRUCTOR_DOUBLE_BOOKED`, `ENVIRONMENT_DOUBLE_BOOKED`, `SESSIONS_OVERLAP`, `ENVIRONMENT_MAINTENANCE`, `INSTRUCTOR_UNAVAILABLE`. La detección corre al guardar cada sesión, bajo demanda (`/validate`) y **obligatoriamente antes de publicar**. Un horario con conflictos activos **no puede publicarse**. | RN-SCH-03, RN-SCH-04 |
| **RF-SCH-04** | El sistema debe aceptar solo sesiones válidas: duración 1–6 h, dentro de la disponibilidad del ambiente, de lunes a sábado, y no en festivos. | RN-SCH-05, RN-SCH-06 |
| **RF-SCH-05** | El sistema debe **publicar** un horario sin conflictos con una sola acción, dejándolo **inmutable**; cualquier cambio posterior crea un nuevo `DRAFT` y archiva el anterior (`ARCHIVED`). Debe emitir `scheduling.schedule.published`. | RN-SCH-01 |
| **RF-SCH-06** | El sistema debe permitir consultar el horario vigente **por instructor (semana)** y **por aprendiz (ficha)**. | CF-04, CF-05; NFR-PERF-04 |
| **RF-SCH-07** | El sistema debe mantener **read models** locales de instructores/competencias y ambientes/disponibilidad, poblados por eventos, para resolver las consultas de disponibilidad sin dependencias síncronas. | ADR-002 |

> **Validación final pre-publicación:** aunque las consultas de construcción usan read models (consistencia eventual), la validación previa a `publish` verifica el estado fresco de los servicios dueños antes de permitir la publicación (ADR-002, sección Riesgos).

## 6. Actores — `actors-service`

| ID | Requisito | Regla / Nota |
|----|-----------|--------------|
| **RF-ACT-01** | El sistema debe gestionar instructores con su tipo de vinculación (`STAFF` 40 h, `CONTRACTOR`, `HOURLY`) y las competencias que están habilitados a impartir (`CompetencyAssignment`). | RN-ACT-01, RN-ACT-02 |
| **RF-ACT-02** | El sistema debe registrar la disponibilidad y las excepciones del instructor, insumo de la detección de `INSTRUCTOR_UNAVAILABLE`. Debe emitir `actors.instructor.assigned`. El productor aún no aparece en actors-service develop; hoy se emite `actors.instructor.availability_changed`. La implementación o retiro de assigned queda pendiente de decisión de dominio. | RN-ACT-02, RN-SCH-03 |
| **RF-ACT-03** | El sistema debe exponer `GET /instructors/available` (por competencia y franja) en **< 300 ms (p95)**. | NFR-PERF-02 |
| **RF-ACT-04** | El sistema debe gestionar aprendices y su estado (`ACTIVE`, `DROPOUT`, `TRANSFERRED`, `GRADUATED`); solo los `ACTIVE` reciben clases y aparecen en el horario. | RN-ACT-03 |
| **RF-ACT-05** | El sistema debe soportar empresas y etapa productiva (visitas de seguimiento, convenios). *(Alcance parcial en MVP; ver [scope.md](../01-context/scope.md)).* | RN-ACT-04, RN-ACT-05 |

## 7. Documentos — `document-service`

| ID | Requisito | Regla / Nota |
|----|-----------|--------------|
| **RF-DOC-01** | El sistema debe generar PDFs (horario publicado, constancias) y almacenarlos en object storage compatible S3, guardando en BD solo la `storage_key`. La descarga se sirve con URL firmada de expiración corta. | ADR-003 |
| **RF-DOC-02** | El sistema debe versionar los documentos; una nueva versión conserva la anterior en historial. Debe emitir `document.document.generated`. | Modelo `document` |

## 8. Seguimiento y analítica — `monitoring-service` · **CORE**

| ID | Requisito | Regla / Nota |
|----|-----------|--------------|
| **RF-MON-01** | El sistema debe iniciar el seguimiento de una ficha al recibir `scheduling.schedule.published` / `academic.ficha.opened`, y alertar (`TRACKING_OVERDUE`) si no hay seguimiento en > 35 días. | RN-MON-01 |
| **RF-MON-02** | El sistema debe calcular KPIs por ficha (asistencia ≥ 80 %, avance curricular) registrando cada medición como un nuevo registro append-only. | RN-MON-02, RN-CROSS-01 |
| **RF-MON-03** | El sistema debe generar alertas por nivel (`INFO`→`CRITICAL`) según los umbrales configurados y ejecutar la acción asociada; las alertas se resuelven manualmente y no se eliminan (`is_resolved = true`). | RN-MON-04, RN-MON-05 |
| **RF-MON-04** | El sistema debe calcular el **riesgo de deserción** de un aprendiz (≥ 2 indicadores de RN-MON-03). | RN-MON-03 |
| **RF-MON-05** | El sistema debe permitir crear planes de mejoramiento (aprendiz/instructor) y exigirlos para fichas en estado crítico dentro de 5 días hábiles (`IMPROVEMENT_PLAN_OVERDUE`). | RN-MON-06, RN-ACT-06 |

## 9. Auditoría — `audit-service`

| ID | Requisito | Regla / Nota |
|----|-----------|--------------|
| **RF-AUD-01** | El sistema debe registrar de forma **append-only** todas las acciones de negocio, consumiendo todos los topics de eventos, sin permitir edición ni borrado. | RN-CROSS-01, NFR-REC-04 |
| **RF-AUD-02** | El sistema debe garantizar la entrega de eventos con at-least-once, idempotencia por `event_id`, reintentos y DLQ. | ADR-001 |
| **RF-AUD-03** | El sistema debe aplicar el estándar transversal de auditoría y estados parametrizables (autoría, soft delete, `status`). | ADR-004 |

## 10. Notificaciones — `notification-service`

> Servicio **extraído de `monitoring-service`** como bounded context propio (ADR-005). **Construido y verificado en `dev`** (EP-NOTIF, 8/8 HU Done·Dev).

| ID | Requisito | Regla / Nota |
|----|-----------|--------------|
| **RF-NOTIF-01** | El sistema debe aceptar solicitudes de notificación por API de forma **asíncrona**: valida la solicitud y responde **`202 Accepted`** sin bloquear en la entrega. | RN-CROSS-01 |
| **RF-NOTIF-02** | El sistema debe **entregar notificaciones dirigidas por eventos**: consume eventos de dominio del broker y genera la notificación correspondiente. | ADR-001 |
| **RF-NOTIF-03** | El sistema debe soportar múltiples **canales** de entrega: `EMAIL` e `IN_APP`. | Modelo `notification` |
| **RF-NOTIF-04** | El sistema debe ser **resiliente**: reintentos con backoff, **DLQ** para mensajes no entregables e **idempotencia por `event_id`** (no duplica una notificación ante reintregas). | ADR-001; NFR-REC-03 |
| **RF-NOTIF-05** | El sistema debe gestionar **plantillas** de notificación para componer el contenido por tipo/canal. | Modelo `notification_template` |
| **RF-NOTIF-06** | El sistema debe permitir **consultar** las notificaciones emitidas (`GET`). | — |
| **RF-NOTIF-07** | El sistema debe emitir observabilidad (OpenTelemetry, endpoints `/health` y `/ready`) y **publicar `notification.notification.sent`** al completar una entrega. | ADR-001; NFR-OBS-04 |

---

## Reglas transversales aplicables a todos los RF

Derivadas de [entities-and-rules.md](../02-domain/entities-and-rules.md) (sección "Reglas transversales"):

- **Soft delete** — ninguna entidad de negocio se elimina físicamente (`is_active = false`) — RN-CROSS-03.
- **PII protegida** — cifrado en reposo, nunca en logs (solo ID) — RN-CROSS-02, NFR-SEC-04/05.
- **Timestamps en UTC** — conversión a hora Colombia (UTC-5) en presentación — RN-CROSS-04.
- **UUID v4** como identificadores primarios — RN-CROSS-05.

## Puntos abiertos

- **RF-ACT-05**: el alcance de etapa productiva en el MVP está parcialmente definido (PA-03/PA-04 en [vision.md](../03-product/vision.md)).
- Confirmar si la modificación de un horario `PUBLISHED` es siempre por nueva versión (supuesto de RF-SCH-05) — PA-01.

## Referencias

- [02-domain/entities-and-rules.md](../02-domain/entities-and-rules.md) · [02-domain/domain-events.md](../02-domain/domain-events.md)
- [user-stories.md](./user-stories.md) · [non-functional.md](./non-functional.md) · [traceability-matrix.md](./traceability-matrix.md)
- [09-microservices/service-catalog.md](../09-microservices/service-catalog.md)
