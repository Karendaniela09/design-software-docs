# Mapa actualizado de datos por microservicio

> Estado: 🟡 Revisión | Última actualización: 2026-10-07
> Autor: Kevin Andrey Culma (Arquitecto) | Equipo: Arquitectura.

> Generado desde scripts `01_ddl` de los repos `*-db` en `develop` el 2026-10-07.

| Microservicio | Repo DB | Esquemas | Tablas detectadas |
|---|---|---|---|
| `iam-service` | `design-software-iam-db` | identity, identity_audit, rbac, rbac_catalog, session | identity.outbox, identity.user, identity_audit.audit_login, rbac.role, rbac.role_feature, rbac.user_role, rbac.user_scope_override, rbac_catalog.feature, rbac_catalog.module, session.password_reset_request, session.refresh_token |
| `reference-data-service` | `design-software-reference-data-db` | institutional_structure, parameterization | institutional_structure.department, institutional_structure.institutional_unit, institutional_structure.macroregion, institutional_structure.microregion, institutional_structure.municipality, institutional_structure.training_center, parameterization.catalog, parameterization.catalog_detail, parameterization.parameter |
| `academic-management-service` | `design-software-academic-management-db` | academic_management | academic_management.competency, academic_management.enrollment_ficha, academic_management.knowledge_network, academic_management.learning_outcome, academic_management.outbox, academic_management.processed_event, academic_management.tech_line, academic_management.tech_network, academic_management.training_program |
| `training-environment-service` | `design-software-training-environment-db` | training_environment | training_environment.availability_rule, training_environment.environment, training_environment.environment_type, training_environment.inventory_item, training_environment.item_type, training_environment.maintenance, training_environment.reservation |
| `scheduling-service` | `design-software-scheduling-db` | scheduling | scheduling.class_session, scheduling.environment_availability_projection, scheduling.instructor_availability_projection, scheduling.outbox, scheduling.schedule, scheduling.scheduling_conflict, scheduling.site_travel_time, scheduling.time_slot |
| `actors-service` | `design-software-actors-db` | actors_companies, actors_instructors, actors_learners, actors_parameterization, actors_tracking | actors_companies.company, actors_companies.company_visit, actors_companies.productive_stage, actors_instructors.competency_assignment, actors_instructors.instructor, actors_instructors.instructor_area, actors_instructors.instructor_availability_exception, actors_instructors.instructor_contract, actors_learners.learner, actors_learners.learner_ficha_enrollment, actors_parameterization.status, actors_parameterization.status_category, actors_parameterization.status_transition, actors_tracking.activity_log, actors_tracking.actor_improvement_plan |
| `document-service` | `design-software-document-db` | document | document.document, document.document_template, document.document_template_variable, document.document_template_version, document.document_version |
| `monitoring-service` | `design-software-monitoring-db` | monitoring | monitoring.alert_type, monitoring.ficha_tracking, monitoring.generated_alert, monitoring.improvement_plan, monitoring.kpi_status, monitoring.kpi_tracking, monitoring.kpi_tracking_2026_08, monitoring.kpi_tracking_default, monitoring.kpi_type, monitoring.outbox, monitoring.risk_level, monitoring.sent_notification, monitoring.tracking_session |
| `audit-service` | `design-software-audit-db` | audit | audit.audit_event_seen, audit.audit_record, audit.audit_record_2026_08, audit.audit_record_default |
| `notification-service` | `design-software-notification-db` | notification | notification.notification_template, notification.outbox, notification.sent_notification |

## Reglas de actualizacion

- Los cambios estructurales deben agregarse en `01_ddl` y su rollback en `05_rollbacks`.
- Los seeds funcionales deben ir en `02_dml` con rollback correspondiente cuando aplique.
- Evitar escrituras cruzadas: un servicio no debe mutar tablas de otro bounded context.
- Para `monitoring.sent_notification`, documentar como legado si no se elimina en la migración; la fuente vigente de notificaciones entregadas es `notification.sent_notification`.
