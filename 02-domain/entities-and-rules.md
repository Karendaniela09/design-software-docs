# Entidades y Reglas de Negocio — Dominio SENA Gestión de Horarios

> Estado: 🟡 Borrador | Última actualización: 2026-08-28
> Fuente: análisis de equipos M1-M9 · estructura pública SENA (Acuerdo 00003/2012, Decreto 249/2004, Circular 1-2014)

## Propósito

Este documento captura las reglas de negocio del dominio que **no son derivables del código**:
restricciones regulatorias, políticas operativas y restricciones de datos establecidas por el SENA.
Sirve como referencia para validaciones en servicios, contratos de API y modelo de datos.

---

## Dominio M1 — Identidad y Acceso

### RN-IAM-01: Bloqueo por intentos fallidos
Después de 5 intentos de login fallidos consecutivos, la cuenta se bloquea por 15 minutos.
Después de 10 intentos, el bloqueo es de 24 horas. El contador se resetea en login exitoso.

### RN-IAM-02: Vigencia de sesiones
El `access_token` expira en 15 minutos. El `refresh_token` expira en 7 días.
Un usuario puede tener múltiples sesiones activas simultáneas (browser + móvil).

### RN-IAM-03: Roles y centros
Un usuario puede tener un rol a nivel global (`training_center_id = null`) o restringido
a un centro específico. Un coordinador solo opera dentro de su centro asignado.

### RN-IAM-04: Instructor = Usuario
Todo instructor debe tener una cuenta de usuario activa en iam-service.
El sistema crea el usuario y el perfil de instructor de forma coordinada.
No puede existir un instructor sin usuario, ni un usuario instructor sin perfil en actors-service.

### RN-IAM-05: Contraseña temporal
Al crear un usuario nuevo, el sistema genera una contraseña temporal que el usuario
debe cambiar en su primer login. Contraseñas temporales expiran en 72 horas.

### RN-IAM-06: Autorización por feature y scope
La autorización se resuelve con un **feature-check**: cada operación exige un feature atómico
(no `resource+action`). El alcance de datos se determina por el **scope** del rol
(`GLOBAL`, `TRAINING_CENTER`, `OWN_*`), combinado con el centro asignado del usuario
(`training_center_id`; ver RN-IAM-03). El catálogo RBAC (roles, features, módulos) admite
**overrides** por usuario que conceden o revocan features puntuales sobre lo que otorga el rol.
La verificación de estos permisos es **local** en cada servicio: el JWT RS256 se valida contra
las claves públicas de JWKS, sin llamada síncrona a iam-service.

> **Entidad de integración — `outbox`**: iam-service persiste sus eventos de dominio en una
> tabla `outbox` (schema `identity`) dentro de la misma transacción que muta el estado, y un
> relay (`OutboxRelayScheduler.poll`) los publica al topic `iam-events`. Es el mecanismo que
> garantiza consistencia entre el cambio de estado y la emisión del evento (Outbox pattern);
> no es una entidad de negocio sino de integración.

---

## Dominio M2/M4 — Estructura Institucional y Catálogos

### RN-REF-01: Jerarquía de centros
La jerarquía es: Macrorregión → Microrregión → Departamento → Municipio → Centro de Formación.
Un centro pertenece a un único municipio. No se puede reasignar un centro a otro municipio.

### RN-REF-02: Código SENA de centro
El `center_code` es asignado por la Dirección General del SENA y es inmutable.
Ejemplo: `5101001` (Centro Agroempresarial, Caldas, Antioquia).

### RN-REF-03: Catálogos de sistema
Los catálogos del sistema (`Catalog` / `CatalogDetail`) son de solo lectura para el usuario
final. Solo el rol `ADMIN_STAFF` o `SYSTEM_ADMIN` puede modificarlos.

### RN-REF-04: Parámetros del sistema
Los parámetros como `MAX_HOURS_PER_WEEK_STAFF` (planta: 40 h), `MAX_HOURS_PER_WEEK_CONTRACTOR`
(contratista: 48 h según contrato) y `MIN_ATTENDANCE_PERCENTAGE` (80%) son configurables
pero requieren rol `SYSTEM_ADMIN` para modificarlos.

---

## Dominio M3 — Ambientes de Formación

### RN-ENV-01: Capacidad máxima
Un ambiente no puede ser asignado a una sesión de clase si el número de aprendices de la
ficha supera su `capacity`. El sistema debe verificar `capacity >= enrollment_ficha.max_capacity`.

### RN-ENV-02: Reglas de disponibilidad
Cada ambiente puede tener hasta 24 reglas de disponibilidad recurrentes (6 días × 4 franjas).
Una regla define el día de la semana y el bloque horario disponible.

### RN-ENV-03: Bloqueo por mantenimiento
Un `Maintenance` con fechas que se solapan con una sesión de clase impide la asignación
o invalida una sesión ya asignada (genera `SchedulingConflict` de tipo `ENVIRONMENT_MAINTENANCE`).

### RN-ENV-04: Tipos de ambiente
No todos los tipos de ambiente son aptos para todas las competencias.
Las competencias de laboratorio requieren ambiente tipo `LAB` o `WORKSHOP`.
Las teóricas pueden usar `CLASSROOM`. La validación de tipo corresponde al equipo académico,
no al motor de horarios (el motor solo verifica disponibilidad).

---

## Dominio M5/M6 — Programas y Fichas

### RN-ACAD-01: Estructura curricular
La unidad mínima de formación es el `LearningOutcome` (RAP: Resultado de Aprendizaje).
Un `Competency` agrupa múltiples RAPs. Un `TrainingProgram` agrupa múltiples `Competency`.
Esta jerarquía es definida por el SENA a nivel nacional y es de solo lectura en los centros.

### RN-ACAD-02: Duración de programa
La duración total de un programa es fija (en horas) y es la suma de las horas de sus competencias.
Ejemplo: Técnico en Sistemas = 1.584 horas (Resolución 3267 de 2004).

### RN-ACAD-03: Número de ficha
El `ficha_number` es asignado por el sistema SOFIA Plus del SENA y es único a nivel nacional.
Ejemplo: `2849655`. No se genera dentro de esta plataforma; se importa o ingresa manualmente.

### RN-ACAD-04: Estados de ficha
Las fichas siguen el ciclo: `INDUCTION → EXECUTION → PRODUCTIVE_STAGE → COMPLETED`.
Un horario solo puede crearse para fichas en estado `EXECUTION`.
Las fichas `COMPLETED` o `CANCELLED` no admiten nuevas sesiones de clase.

### RN-ACAD-05: Transiciones de estado permitidas

| Desde | Hacia | Quién puede |
|-------|-------|-------------|
| `INDUCTION` | `EXECUTION` | COORDINATOR |
| `EXECUTION` | `PRODUCTIVE_STAGE` | COORDINATOR |
| `EXECUTION` | `CANCELLED` | CENTER_DIRECTOR |
| `PRODUCTIVE_STAGE` | `COMPLETED` | COORDINATOR |
| Cualquier estado | `CANCELLED` | CENTER_DIRECTOR |

### RN-ACAD-06: Cupo máximo
El `max_capacity` de una ficha es fijado al momento de la creación y no puede aumentarse.
Puede reducirse si hay retiros de aprendices, pero nunca quedar por debajo del número
de aprendices activos actuales.

### RN-ACAD-07: Cierre de ficha por aprobación de RAP
En el SENA no hay nota numérica: cada RAP (`LearningOutcome`) recibe un **juicio evaluativo** por
aprendiz, `APPROVED` (aprobado) o `NOT_APPROVED` (no aprobado); la ausencia de juicio significa
pendiente. Una ficha solo pasa de `PRODUCTIVE_STAGE` a `COMPLETED` si **cada aprendiz activo tiene
aprobado el 100 % de los RAP activos** del programa de la ficha. Un RAP `NOT_APPROVED` o pendiente
no cuenta. No existe umbral parcial ni nota. Una ficha **sin aprendices activos no puede pasar a
`COMPLETED`**. El juicio vive en `actors-service`; la lista de RAP requeridos la resuelve
`academic-management-service` (decisión del dueño del 2026-10-24; ver
[ADR-030](../05-architecture/decisions/records/ADR-030-academic-ficha-lifecycle-preconditions.md),
aceptado).

La transición `EXECUTION` → `PRODUCTIVE_STAGE` **no tiene condición de horas ejecutadas** (el dueño
retiró el 80 % propuesto); la única regla documentada sobre llegar a la etapa productiva es
`RN-ACT-04` (70 % de avance curricular del aprendiz, configurable). El reporte de ejecución de
`scheduling-service` queda como evidencia informativa, sin bloquear nada.

---

## Dominio M7 — Actores (Instructores y Aprendices)

### RN-ACT-01: Tipo de vinculación del instructor
| Tipo | Horas máximas semana | Observaciones |
|------|---------------------|---------------|
| `STAFF` (planta) | 40 h | Incluye tiempo de preparación y seguimiento |
| `CONTRACTOR` (OPS) | Según contrato | Generalmente 48 h máx |
| `HOURLY` (hora-cátedra) | Según contrato | Sin límite fijo; verificar contrato individual |

### RN-ACT-02: Competencias del instructor
Un instructor solo puede ser asignado a una sesión de clase de una competencia si tiene
al menos una `CompetencyAssignment` activa con `competency_id` coincidente.
Esta validación es responsabilidad del `scheduling-service` durante la detección de conflictos.

### RN-ACT-03: Estado del aprendiz
| Estado | Puede recibir clases | Aparece en horario |
|--------|---------------------|-------------------|
| `ACTIVE` | Sí | Sí |
| `DROPOUT` | No | No |
| `TRANSFERRED` | No | No (aparece en nueva ficha) |
| `GRADUATED` | No | No |

### RN-ACT-04: Etapa productiva
Un aprendiz solo puede iniciar etapa productiva si:
1. La ficha está en estado `PRODUCTIVE_STAGE`
2. El aprendiz tiene al menos 70% de avance curricular (regla configurable)
3. La empresa tiene convenio activo con el SENA

### RN-ACT-05: Visitas a empresa
Mínimo 2 visitas de seguimiento durante toda la etapa productiva (Acuerdo 00003/2012, Art. 65).
La primera visita debe realizarse dentro de los 30 días de iniciada la etapa productiva.

### RN-ACT-06: Plan de mejoramiento individual
Un plan de mejoramiento puede crearse para un instructor o aprendiz.
Un plan para instructor se origina generalmente en bajo desempeño durante el seguimiento.
Un plan para aprendiz se origina en baja asistencia, bajo avance o problemas disciplinarios.

---

## Dominio M8 — Horarios (Scheduling)

### RN-SCH-01: Ciclo de vida del horario
```
DRAFT → UNDER_REVIEW → PUBLISHED
                 ↘ ARCHIVED (si se reemplaza por otro)
```
Un horario `PUBLISHED` es **inmutable**. Cualquier cambio requiere crear un nuevo horario
en `DRAFT` y publicarlo, lo que archiva automáticamente el anterior.

### RN-SCH-02: Unicidad de horario por período
Solo puede existir un horario `PUBLISHED` por ficha por período.
Puede haber múltiples `DRAFT` simultáneos mientras se construye el definitivo.

### RN-SCH-03: Conflictos bloqueantes
Los siguientes conflictos impiden la publicación:
- `INSTRUCTOR_DOUBLE_BOOKED`: mismo instructor en dos sesiones que se solapan en tiempo
- `ENVIRONMENT_DOUBLE_BOOKED`: mismo ambiente en dos sesiones que se solapan
- `SESSIONS_OVERLAP`: dos sesiones de la misma ficha que se solapan en tiempo
- `ENVIRONMENT_MAINTENANCE`: ambiente en mantenimiento durante la sesión
- `INSTRUCTOR_UNAVAILABLE`: instructor con excepción de disponibilidad en ese período

### RN-SCH-04: Detección de conflictos
La detección de conflictos se ejecuta:
1. Al guardar cada sesión de clase (validación inmediata)
2. Al solicitar `POST /schedules/{id}/validate` (validación completa del horario)
3. Obligatoriamente antes de `POST /schedules/{id}/publish`

Un horario con conflictos activos no puede publicarse.

### RN-SCH-05: Franja horaria mínima
Una sesión de clase debe tener una duración mínima de 1 hora y máxima de 6 horas.
El sistema no acepta sesiones fuera de los horarios definidos en `AvailabilityRule` del ambiente.

### RN-SCH-06: Días laborales SENA
El SENA opera de lunes a sábado. No se pueden crear sesiones de clase los domingos
ni en días festivos nacionales. La tabla de festivos es un parámetro del sistema.

---

## Dominio M9 — Seguimiento y Analítica

### RN-MON-01: Frecuencia mínima de seguimiento
Normativa: seguimiento mínimo mensual para fichas en estado `EXECUTION`
(Acuerdo 00003/2012, Circular 1-2014 SENA).
El sistema debe generar una alerta `TRACKING_OVERDUE` si no hay sesión de seguimiento
en más de 35 días para una ficha activa.

### RN-MON-02: Asistencia mínima
El porcentaje mínimo de asistencia reglamentario es del 80% (Acuerdo 00003/2012, Art. 48).
Aplica a cada sesión de clase y también al promedio acumulado de la ficha.
Por debajo de 60% acumulado, el aprendiz puede ser inhabilitado.

### RN-MON-03: Cálculo de riesgo de deserción
Un aprendiz está en riesgo de deserción si tiene al menos 2 de los siguientes indicadores:
1. Asistencia < 70% en las últimas 4 semanas
2. Sin reportes académicos en más de 2 sesiones consecutivas
3. `enrollment_status` = `ACTIVE` pero sin registro de clase en > 2 semanas

### RN-MON-04: Umbrales de alerta por nivel de riesgo
| Nivel | Attendance | Curriculum Progress | Acción automática |
|-------|------------|--------------------|--------------------|
| `INFO` | 80-85% | 70-79% | Notificación al instructor |
| `LOW` | 75-79% | 60-69% | Notificación + plan de mejora sugerido |
| `MEDIUM` | 70-74% | 50-59% | Notificación a coordinador + instructor |
| `HIGH` | 65-69% | 40-49% | Alerta a coordinador + llamado obligatorio |
| `CRITICAL` | < 65% | < 40% | Alerta a director + intervención inmediata |

### RN-MON-05: Resolución de alertas
Una alerta debe ser resuelta manualmente por un COORDINATOR o CENTER_DIRECTOR.
Al resolver, debe quedar registrado quién la resolvió, cuándo y las notas de resolución.
Las alertas no se eliminan; se marcan como `is_resolved = true`.

### RN-MON-06: Plan de mejoramiento obligatorio
Para fichas con `overall_status = CRITICAL`, el coordinador debe crear un plan de mejoramiento
dentro de los 5 días hábiles siguientes a la generación de la alerta crítica.
El sistema genera una alerta secundaria `IMPROVEMENT_PLAN_OVERDUE` si no se crea.

---

## Reglas transversales

### RN-CROSS-01: Inmutabilidad de registros históricos
Los siguientes registros son de solo escritura (append-only):
- `AuditRecord` en audit-service
- `ActivityLog` en actors-service
- `AuditLogin` en iam-service
- `KpiTracking` en monitoring-service (cada medición es un nuevo registro)

### RN-CROSS-02: Datos PII
Los campos marcados como PII (Personally Identifiable Information) están sujetos a:
- Encriptación en reposo en la BD
- No pueden aparecer en logs (solo ID)
- Solo pueden accederse con los features específicos de cada actor

### RN-CROSS-03: Soft delete
Ninguna entidad de negocio se elimina físicamente. Se usa `is_active = false`.
La excepción son los registros temporales (refresh_token expirado, password_reset_request usado).

### RN-CROSS-04: Timestamps en UTC
Todos los timestamps se almacenan en UTC (`TIMESTAMPTZ`).
La conversión a hora de Colombia (UTC-5) es responsabilidad de la capa de presentación.

### RN-CROSS-05: UUIDs como identificadores
Todos los identificadores primarios son UUID v4. No se usan secuencias autoincrementales.
Esto permite generación de ID en el cliente y facilita la federación de datos.
