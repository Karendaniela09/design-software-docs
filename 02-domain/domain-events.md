# Eventos de Dominio — SENA Gestión de Horarios

> Estado: 🟡 Borrador | Última actualización: 2026-08-28
> Naming: nombres de eventos en inglés (HALT-DB-NAMING — los eventos son contratos de integración)
> Relacionado: [event-catalog.md](../09-microservices/event-catalog.md) · [domain-map.md](./domain-map.md)

## Diferencia con el event-catalog

- **Este documento (domain-events)**: vista de negocio — qué significa cada evento en el dominio, qué lo dispara y qué cambia de estado.
- **[event-catalog.md](../09-microservices/event-catalog.md)**: vista técnica — topics, payloads, consumidores, envelope.

## Convención de naming

`<context>.<entity>.<action>` — minúsculas, puntos, en inglés. El verbo va en pasado (el evento describe algo que **ya ocurrió**).

Ejemplo: `scheduling.schedule.published`

---

## Eventos por bounded context

### iam-service (Identidad)

| Evento | Disparado por | Significado de negocio | Cambio de estado |
|--------|---------------|------------------------|------------------|
| `iam.user.created` | Creación de usuario | Una persona obtuvo acceso al sistema | actors-service crea el perfil de actor asociado |
| `iam.user.deactivated` | Desactivación de cuenta | Una persona perdió el acceso | Se revocan tokens; actors marca el actor inactivo |
| `iam.role.assigned` | Asignación de rol | Cambió el nivel de acceso de un usuario | El próximo login refleja los nuevos features |
| `iam.session.started` | Login exitoso | Un usuario abrió una sesión (se emitió un token) | audit registra el inicio de sesión; monitoring/notification pueden reaccionar |

> Los 4 eventos de iam-service se emiten vía **Outbox** (`identity.outbox`) → relay (`OutboxRelayScheduler.poll`) → topic `iam-events`. La emisión es consistente con la transacción de BD (no hay doble escritura).

### reference-data-service (Datos de referencia)

| Evento | Disparado por | Significado de negocio | Cambio de estado |
|--------|---------------|------------------------|------------------|
| `reference.catalog.updated` | Edición de catálogo | Cambió un valor de referencia | Los consumidores invalidan su caché |
| `reference.training_center.created` | Alta de centro | Un nuevo centro entró al sistema | Disponible para asignar fichas y usuarios |

### academic-management-service (Académico)

| Evento | Disparado por | Significado de negocio | Cambio de estado |
|--------|---------------|------------------------|------------------|
| `academic.program.created` | Alta de programa | Un nuevo programa de formación está disponible | Puede instanciarse en fichas |
| `academic.ficha.opened` | Ficha pasa a EXECUTION | Comenzó la formación de una cohorte | monitoring inicia el seguimiento de la ficha |
| `academic.ficha.closed` | Ficha pasa a COMPLETED/CANCELLED | Terminó el ciclo de la ficha | monitoring cierra el seguimiento; scheduling no admite nuevas sesiones |
| `academic.competency.updated` | Edición de competencia | Cambió una competencia del currículo | actors actualiza su read model de competencias |

### training-environment-service (Ambientes)

| Evento | Disparado por | Significado de negocio | Cambio de estado |
|--------|---------------|------------------------|------------------|
| `environment.environment.created` | Alta de ambiente | Un nuevo espacio físico está disponible | scheduling lo incorpora a su read model |
| `environment.availability.changed` | Cambio de regla de disponibilidad | Cambió cuándo se puede usar un ambiente | scheduling actualiza su read model; puede invalidar sesiones |
| `environment.maintenance.started` | Inicio de mantenimiento | Un ambiente quedó temporalmente no disponible | scheduling marca conflictos en sesiones afectadas |

### scheduling-service (Horarios — CORE)

| Evento | Disparado por | Significado de negocio | Cambio de estado |
|--------|---------------|------------------------|------------------|
| `scheduling.class_session.created` | Alta de sesión en borrador | Se agregó una clase a un horario en construcción | monitoring (futuro) y audit registran |
| `scheduling.class_session.cancelled` | Cancelación de sesión | Una clase fue eliminada del horario | monitoring ajusta el seguimiento |
| `scheduling.conflict.detected` | Validación del motor | Se encontró un conflicto que bloquea publicación | El coordinador debe resolverlo antes de publicar |
| `scheduling.schedule.published` | Publicación del horario | El horario es oficial e inmutable | monitoring inicia/actualiza seguimiento; actors notifica; document puede generar PDF |

### actors-service (Actores)

| Evento | Disparado por | Significado de negocio | Cambio de estado |
|--------|---------------|------------------------|------------------|
| actors.instructor.assigned | Asignación de competencia/contrato | Un instructor quedó habilitado para impartir | scheduling actualiza su read model de instructores |
| actors.learner.enrolled | Matrícula de aprendiz | Un aprendiz se vinculó a una ficha | monitoring lo cuenta en la ficha |
| actors.productive_stage.started | Inicio de etapa productiva | Un aprendiz pasó a fase de empresa | monitoring inicia seguimiento de etapa productiva |
| actors.company_visit.completed | Registro de visita | Se cumplió una visita de seguimiento empresarial | monitoring actualiza KPIs de etapa productiva |

Verificación contra actors-service develop: el código emite actors.instructor.availability_changed, actors.learner.enrolled y actors.company_visit.completed. No se encontró productor para actors.instructor.assigned ni actors.productive_stage.started. Resolver si se implementan o se retiran del catálogo requiere decisión de dominio.

### document-service (Documentos)

| Evento | Disparado por | Significado de negocio | Cambio de estado |
|--------|---------------|------------------------|------------------|
| `document.document.generated` | Generación de PDF | Un documento quedó disponible para descarga | El solicitante puede descargarlo |
| `document.version.created` | Nueva versión | Se actualizó un documento | La versión anterior queda en historial |

### monitoring-service (Seguimiento — CORE)

| Evento | Disparado por | Significado de negocio | Cambio de estado |
|--------|---------------|------------------------|------------------|
| `monitoring.alert.triggered` | Umbral de KPI superado | Se detectó una desviación que requiere atención | Notificación a coordinador/instructor |
| `monitoring.kpi.threshold_breached` | KPI en nivel crítico | Una ficha entró en riesgo crítico | Obliga a crear plan de mejoramiento (RN-MON-06) |
| `monitoring.notification.sent` | Envío de notificación | Un actor fue informado | audit registra el envío |

### audit-service

> No publica eventos. Solo consume todos los topics y persiste de forma inmutable.

### notification-service (Notificaciones — TRANSVERSAL)

Microservicio transversal (Go) extraído de monitoring (ADR-005). Es un **consumidor** de eventos de dominio de otros contextos (p. ej. `monitoring.alert.triggered`, `scheduling.schedule.published`, `iam.*`) y publica su propio evento cuando entrega una notificación. Consume con **idempotencia por `event_id`** y **DLQ** ante fallos; las notificaciones ya no viven en monitoring.

| Evento | Disparado por | Significado de negocio | Cambio de estado |
|--------|---------------|------------------------|------------------|
| `notification.notification.sent` | Entrega de una notificación a un actor | Un actor fue informado por un canal (correo, etc.) | audit registra el envío; monitoring puede cerrar el ciclo de la alerta |

---

## Flujo de eventos del caso de uso central — Publicar horario

```
Coordinador publica horario
        │
        ▼
scheduling.schedule.published ──────┬──────────────┬──────────────┐
                                     ▼              ▼              ▼
                          monitoring-service   actors-service   audit-service
                          inicia FichaTracking  notifica a       registra
                          y KPIs base           instructores/    AuditRecord
                                                aprendices
                                     │
                                     ▼
                          (si KPI crítico futuro)
                          monitoring.alert.triggered
                                     │
                                     ▼
                          notification-service (consume con
                          idempotencia por event_id + DLQ)
                                     │
                                     ▼
                          notification.notification.sent → audit
```

> Nota: las notificaciones fueron extraídas de monitoring a **notification-service** (ADR-005). El evento `monitoring.notification.sent` listado arriba corresponde al modelo previo; el envío efectivo lo publica hoy `notification.notification.sent` desde notification-service.

---

## Garantías de entrega

| Propiedad | Valor | Mecanismo |
|-----------|-------|-----------|
| Entrega | At-least-once | Broker (ADR-001) + publisher confirms |
| Idempotencia | Garantizada | `event_id` único por evento; consumers deduplicar |
| Orden | Por partición (ej. por ficha) | Routing key con `ficha_id` |
| Fallo de consumer | Reintentos + DLQ | 3 reintentos con backoff; luego `<topic>.dlq` |
| Durabilidad de eventos críticos | Persistente | Outbox pattern implementado en iam-service (`identity.outbox` → `iam-events`, vía `OutboxRelayScheduler.poll`) y notification-service. scheduling-service aún no existe. |
