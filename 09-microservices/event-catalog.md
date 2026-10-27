# Catálogo de eventos

> Estado: 🟡 Revisión | Última actualización: 2026-08-06
> Naming: nombres de eventos en inglés (HALT-DB-NAMING — los eventos son contratos de integración)

Inventario centralizado de todos los eventos que circulan entre microservicios.
Los eventos siguen el envelope estándar definido en [`_template/service/events.md`](./_template/service/events.md).

## Convención de naming

`<service>.<entity>.<action>` — todo en minúsculas con puntos, en inglés. El verbo en pasado.

Ejemplo: `scheduling.class_session.created`

## Eventos por publicador

### iam-service

| Evento | Descripción | Consumidores |
|--------|-------------|-------------|
| `iam.user.created` | Usuario nuevo creado | `actors-service`, `audit-service` |
| `iam.user.deactivated` | Usuario desactivado | `audit-service`, `actors-service` |
| `iam.role.assigned` | Rol asignado a usuario | `audit-service` |
| `iam.session.started` | Sesión iniciada | `audit-service` |

### reference-data-service

| Evento | Descripción | Consumidores |
|--------|-------------|-------------|
| `reference.catalog.updated` | Catálogo modificado | `audit-service`, (consumidores invalidan caché) |
| `reference.training_center.created` | Centro nuevo registrado | `audit-service` |

### academic-management-service

| Evento | Descripción | Consumidores |
|--------|-------------|-------------|
| `academic.program.created` | Programa de formación creado | `audit-service` |
| `academic.ficha.opened` | Ficha de caracterización abierta o habilitada | `audit-service`, `monitoring-service` |
| `academic.ficha.closed` | Ficha cerrada | `audit-service`, `monitoring-service` |
| `academic.competency.updated` | Competencia modificada | `audit-service`, `actors-service` |
| `academic.enrollment_ficha.created` | Evento histórico fuera del contrato HU-ACAD-10 a HU-ACAD-15; no renombrar sin revisar consumidores | `audit-service`, `scheduling-service`, `monitoring-service` |
| `academic.enrollment_ficha.status_changed` | Evento histórico fuera del contrato HU-ACAD-10 a HU-ACAD-15; no renombrar sin revisar consumidores | `audit-service`, `monitoring-service`, `actors-service` |

> **Nota de naming HU-ACAD-10 a HU-ACAD-15:** el contrato acordado usa
> `academic.program.created`, `academic.ficha.opened`, `academic.ficha.closed` y
> `academic.competency.updated`. Los eventos `academic.enrollment_ficha.created` y
> `academic.enrollment_ficha.status_changed` se mantienen como históricos hasta revisar
> compatibilidad/deprecación con consumidores.

### training-environment-service

| Evento | Descripción | Consumidores |
|--------|-------------|-------------|
| `environment.environment.created` | Ambiente nuevo registrado | `audit-service`, `scheduling-service` |
| `environment.availability.changed` | Disponibilidad de ambiente modificada | `audit-service`, `scheduling-service` |
| `environment.maintenance.started` | Mantenimiento iniciado | `audit-service`, `scheduling-service` |
| `environment.reservation.created` | Reserva confirmada | `audit-service` |

### scheduling-service

| Evento | Descripción | Consumidores |
|--------|-------------|-------------|
| `scheduling.class_session.created` | Sesión de clase programada | `audit-service`, `monitoring-service`, `conflict-validator-worker` |
| `scheduling.class_session.updated` | Sesión de clase modificada | `audit-service`, `conflict-validator-worker` |
| `scheduling.class_session.cancelled` | Sesión cancelada | `audit-service`, `monitoring-service` |
| `scheduling.conflict.detected` | Conflicto de horario detectado | `audit-service`, `monitoring-service` |
| `scheduling.conflict.resolved` | Conflicto previamente detectado resuelto | `audit-service`, `monitoring-service` |
| `scheduling.schedule.published` | Horario publicado a los actores | `audit-service`, `monitoring-service`, `actors-service`, `document-service` |

### actors-service

| Evento | Descripción | Consumidores |
|--------|-------------|-------------|
| `actors.instructor.assigned` | Evento declarado; productor no implementado en actors-service develop | `audit-service`, `monitoring-service`, `scheduling-service` |
| `actors.instructor.availability_changed` | Disponibilidad del instructor modificada | `audit-service`, `scheduling-service` |
| `actors.learner.enrolled` | Aprendiz matriculado en ficha | `audit-service`, `monitoring-service` |
| `actors.productive_stage.started` | Evento declarado; productor no implementado en actors-service develop | `audit-service`, `monitoring-service` |
| `actors.company_visit.completed` | Visita a empresa completada | `audit-service`, `monitoring-service` |


Nota: develop de actors-service actualmente emite actors.instructor.availability_changed, actors.learner.enrolled y actors.company_visit.completed. Las filas assigned y productive_stage.started quedan pendientes de decisión de dominio; no se publican hoy.

### document-service

| Evento | Descripción | Consumidores |
|--------|-------------|-------------|
| `document.document.generated` | Documento generado | `audit-service` |
| `document.version.created` | Nueva versión de documento | `audit-service` |
| `document.status.changed` | Cambio de estado del documento (ciclo de vida) | `audit-service` |
| `document.archived` | Documento archivado | `audit-service` |

### monitoring-service

| Evento | Descripción | Consumidores |
|--------|-------------|-------------|
| `monitoring.alert.triggered` | Alerta de KPI disparada | `audit-service`, `notification-service` |
| `monitoring.kpi.threshold_breached` | KPI superó umbral crítico | `audit-service` (Notification no lo consume en v1; recibe `monitoring.alert.triggered`) |

> La **entrega** de notificaciones se extrae a `notification-service`
> ([ADR-005](../05-architecture/decisions/records/ADR-005-microservices-topology-and-transversal-capabilities.md)):
> monitoring solo **detecta y publica**. El antiguo `monitoring.notification.sent` se reemplaza por
> `notification.notification.sent` (publicado por notification-service).

### notification-service

Capacidad transversal: consume eventos de dominio que ameritan notificar y entrega por email / in-app. La implementación actual soporta `scheduling.schedule.published` y `monitoring.alert.triggered`; nuevos tipos se agregan de forma explícita y contract-first. También acepta solicitudes síncronas vía `POST /notifications`. Ningún dominio invoca su worker directamente.

| Evento | Descripción | Consumidores |
|--------|-------------|-------------|
| `notification.notification.sent` | Notificación entregada al usuario | `audit-service` |

### audit-service

> El audit-service no publica eventos. Solo consume y persiste.

## Eventos internos de servicio (no cruzan frontera)

Estos eventos son de **orquestación interna** de un servicio (worker↔worker, scheduler/cron)
y **no son contratos de integración**: no los consume otro microservicio, por lo que no forman
parte del inventario cross-servicio de arriba. Se documentan aquí para trazabilidad.

| Evento interno | Servicio | Propósito |
|----------------|----------|-----------|
| `document.render.requested` | document-service | pdf-renderer: solicitud de render encolada |
| `document.render.completed` | document-service | pdf-renderer: render finalizado |
| `document.render.failed` | document-service | pdf-renderer: render fallido → reintento/DLQ |
| `document.lifecycle.tick` | document-service | document-lifecycle-worker: pulso de cron |
| `monitoring.kpi.tick` | monitoring-service | cron de recálculo de KPIs |

## Normalización pendiente

- `monitoring.alert.triggered` es el nombre canónico y ya debe usarse en los contratos de Monitoring y Notification. `monitoring.alert.generated` queda retirado.
- Definir compatibilidad/deprecación de `academic.enrollment_ficha.created` y `academic.enrollment_ficha.status_changed` sin cambiar los nombres acordados para HU-ACAD-10 a HU-ACAD-15.

## Nota de migración

Los nombres de evento se actualizaron de español a inglés para cumplir HALT-DB-NAMING
(los eventos son contratos de integración entre servicios). El `audit-worker` suscribe por
wildcard, por lo que el cambio de naming no afecta su lógica de consumo. Los contratos de
componentes que referencian topics específicos se actualizan en paralelo.
