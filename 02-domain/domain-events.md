# Eventos de dominio

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Dominio

## Contexto

Los eventos de dominio representan hechos importantes que ocurren en el sistema y que pueden ser de interés para otros módulos o servicios. Se utilizan para comunicación asíncrona entre microservicios, auditoría y trazabilidad.

Cada evento debe incluir:

- `event_id`: Identificador único del evento.
- `event_type`: Tipo de evento (ej. `SchedulePlanned`).
- `occurred_at`: Fecha y hora en que ocurrió.
- `source`: Microservicio que generó el evento.
- `correlation_id`: Identificador para trazabilidad (ej. ID de solicitud HTTP).
- `run_id`: Identificador de ejecución (para seguimiento de flujos).
- `actor_id`: Usuario o sistema que causó el evento.
- `data`: Payload específico del evento.

---

## Eventos por dominio

### Gestión de Horarios (scheduling-service)

| Evento | Descripción | Payload |
|--------|-------------|---------|
| `SchedulePlanned` | Se ha creado un nuevo horario. | `schedule_id`, `instructor_id`, `environment_id`, `training_group_id`, `start_time`, `end_time`, `created_by` |
| `ScheduleChanged` | Se ha modificado un horario existente. | `schedule_id`, `old_values`, `new_values`, `changed_by`, `reason` |
| `ScheduleCancelled` | Se ha cancelado un horario. | `schedule_id`, `cancelled_by`, `reason` |
| `ConflictDetected` | Se ha detectado un conflicto de horario. | `schedule_id`, `conflict_type` (instructor, environment, group), `conflicting_schedule_id`, `detected_at` |
| `TrainingSessionExecuted` | Se ha ejecutado una sesión de formación real. | `schedule_id`, `actual_start_time`, `actual_end_time`, `instructor_id`, `attendance_count` |
| `AttendanceTraceRegistered` | Se ha registrado asistencia detallada. | `schedule_id`, `learner_id`, `attended`, `observation` |

---

### Gestión Académica (academic-management-service)

| Evento | Descripción | Payload |
|--------|-------------|---------|
| `ProgramCreated` | Se ha creado un nuevo programa de formación. | `program_id`, `code`, `name`, `version`, `created_by` |
| `CompetencyLinkedToProgram` | Se ha vinculado una competencia a un programa. | `program_id`, `competency_id`, `hours`, `order` |
| `RAPLinkedToCompetency` | Se ha vinculado un RAP a una competencia. | `competency_id`, `rap_id`, `order`, `hours` |

---

### Gestión de Actores (actors-service)

| Evento | Descripción | Payload |
|--------|-------------|---------|
| `InstructorRegistered` | Se ha registrado un nuevo instructor. | `instructor_id`, `name`, `type` (staff/contractor), `specialties` |
| `InstructorAssignedToUnit` | Se ha asignado un instructor a una unidad institucional. | `instructor_id`, `unit_id`, `start_date`, `end_date` |
| `LearnerEnrolledInGroup` | Se ha matriculado un aprendiz en una ficha. | `learner_id`, `training_group_id`, `enrollment_date` |

---

### Gestión de Proyectos Formativos (formative-project-service)

| Evento | Descripción | Payload |
|--------|-------------|---------|
| `FormativeProjectStarted` | Se ha iniciado un proyecto formativo. | `project_id`, `training_group_id`, `start_date`, `project_lead` |
| `FormativeProjectMilestoneReached` | Se ha alcanzado un hito del proyecto. | `project_id`, `milestone_name`, `phase_id`, `completed_at` |
| `DependencyCompleted` | Se ha completado una dependencia entre fases. | `phase_id`, `depends_on_phase_id`, `completed_at` |
| `EvidenceSubmitted` | Se ha subido una evidencia. | `evidence_id`, `deliverable_id`, `learner_id`, `submitted_at` |
| `EvidenceValidated` | Se ha validado una evidencia (aprobada/rechazada). | `evidence_id`, `validated_by`, `status`, `comments` |
| `LearnerProgressUpdated` | Se ha actualizado el progreso de un aprendiz. | `learner_id`, `project_id`, `progress_percentage`, `updated_at` |

---

### Transversales (iam-service, audit-service, notification-service)

| Evento | Descripción | Payload |
|--------|-------------|---------|
| `UserLoggedIn` | Un usuario ha iniciado sesión. | `user_id`, `role`, `ip_address`, `timestamp` |
| `UserLoggedOut` | Un usuario ha cerrado sesión. | `user_id`, `timestamp` |
| `AuditEvidenceRegistered` | Se ha registrado una acción en auditoría. | `user_id`, `action`, `entity_type`, `entity_id`, `old_value`, `new_value`, `ip_address` |
| `PolicyViolationDetected` | Se ha detectado una violación de política de seguridad. | `user_id`, `policy_name`, `details`, `detected_at` |
| `NotificationSent` | Se ha enviado una notificación. | `recipient_id`, `channel` (email, sms, push), `subject`, `sent_at` |

---

### Gestión de Documentos (document-service)

| Evento | Descripción | Payload |
|--------|-------------|---------|
| `PdfGenerationRequested` | Se ha solicitado la generación de un PDF. | `document_id`, `template_id`, `data`, `requested_by` |
| `PdfGenerated` | Se ha generado un PDF correctamente. | `document_id`, `url`, `size_bytes`, `generated_at` |
| `DocumentLifecycleChanged` | Se ha cambiado el estado de un documento. | `document_id`, `old_status`, `new_status`, `changed_by` |

---

## Flujo de eventos en escenarios clave

### 1. Creación de un horario

```text
1. Coordinador crea horario → SchedulePlanned (scheduling-service)
2. Se valida conflictos → si hay conflicto, ConflictDetected (scheduling-service)
3. Se notifica al instructor → NotificationSent (notification-service)
4. Se registra en auditoría → AuditEvidenceRegistered (audit-service)