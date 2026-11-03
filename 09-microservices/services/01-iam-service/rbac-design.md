# Diseño RBAC — iam-service

> Fase: 03-Design | Estado: 🟡 Borrador | Fecha: 2026-06-17
> Prerequisito: [data-model.md](./data-model.md) · [overview.md](../../../05-architecture/overview.md)

## Problema que resuelve este diseño

El modelo `permission = resource + action` es demasiado plano para los requisitos de SENA:
- Un coordinador solo puede ver fichas **de su propio centro**, no de todos los centros
- Un instructor solo puede ver **su propio horario**, no todos los horarios del centro
- La UI necesita saber qué módulos y vistas mostrar/ocultar por rol
- Los servicios downstream necesitan filtrar datos según el scope del usuario autenticado

Este documento define el modelo RBAC (Role-Based Access Control) con tres dimensiones:
`Módulo → Feature (permiso) → Scope (alcance de los datos)`

---

## Roles del sistema — Basado en estructura SENA

Fuente: Decreto 249/2004 (estructura interna SENA), Acuerdo 00003/2012 (Estatuto de la Formación Profesional Integral).

| Código de rol | Nombre SENA | Descripción |
|---------------|------------|-------------|
| `SYSTEM_ADMIN` | Administrador de Sistema | Gestión técnica de usuarios, roles y parámetros del sistema |
| `CENTER_DIRECTOR` | Subdirector de Centro | Máxima autoridad operativa del centro; aprueba procesos críticos |
| `COORDINATOR` | Coordinador Académico | Gestiona fichas, instructores y horarios de su centro |
| `AREA_LEADER` | Líder de Área Tecnológica | Coordina instructores de un área; ve fichas de su área |
| `INSTRUCTOR` | Instructor | Ve su horario; registra seguimiento de sus fichas |
| `LEARNER` | Aprendiz | Ve el horario y estado de su ficha activa |
| `ADMIN_STAFF` | Funcionario Administrativo | Gestiona catálogos, parámetros y estructura de referencia |

---

## Módulos del sistema

| Código de módulo | Nombre visible | Servicio backend |
|-----------------|---------------|-----------------|
| `MOD_IDENTITY` | Identidad y Seguridad | `iam-service` |
| `MOD_REFERENCE` | Datos de Referencia | `reference-data-service` |
| `MOD_ACADEMIC` | Gestión Académica | `academic-management-service` |
| `MOD_ENVIRONMENT` | Ambientes de Formación | `training-environment-service` |
| `MOD_SCHEDULING` | Horarios | `scheduling-service` |
| `MOD_ACTORS` | Instructores y Aprendices | `actors-service` |
| `MOD_DOCUMENTS` | Documentos | `document-service` |
| `MOD_MONITORING` | Seguimiento y KPIs | `monitoring-service` |
| `MOD_NOTIFICATIONS` | Notificaciones | `notification-service` |
| `MOD_AUDIT` | Auditoría | `audit-service` |
| `MOD_DASHBOARD` | Panel Principal | cross-cutting |

---

## Catálogo de Features (permisos atómicos)

### MOD_IDENTITY

| Código de feature | Descripción | Nivel de acción |
|------------------|-------------|----------------|
| `IDENTITY_USER_VIEW` | Ver lista y detalle de usuarios; consultar sesiones de otros usuarios (administrador global); la consulta de sesiones propias no exige este feature | READ |
| `IDENTITY_USER_MANAGE` | Crear, editar y desactivar usuarios; habilitar la revocación administrativa de sesiones ajenas por un administrador global; la revocación de sesiones propias no exige este feature | WRITE |
| `IDENTITY_ROLE_VIEW` | Ver roles y sus features asignados | READ |
| `IDENTITY_ROLE_MANAGE` | Gestionar roles y asignar features | WRITE |
| `IDENTITY_ROLE_ASSIGN` | Asignar roles a usuarios | WRITE |
| `IDENTITY_SCOPE_MANAGE` | Gestionar overrides de scope por usuario | WRITE |

### MOD_REFERENCE

| Código de feature | Descripción | Nivel de acción |
|------------------|-------------|----------------|
| `REF_CATALOG_VIEW` | Ver catálogos y sus valores | READ |
| `REF_CATALOG_MANAGE` | CRUD de catálogos y valores | WRITE |
| `REF_HIERARCHY_VIEW` | Ver jerarquía institucional | READ |
| `REF_HIERARCHY_MANAGE` | CRUD de jerarquía (centros, departamentos) | WRITE |
| `REF_PARAMETER_VIEW` | Ver parámetros del sistema | READ |
| `REF_PARAMETER_MANAGE` | Editar parámetros del sistema | WRITE |

### MOD_ACADEMIC

| Código de feature | Descripción | Nivel de acción |
|------------------|-------------|----------------|
| `ACADEMIC_PROGRAM_VIEW` | Ver programas de formación y competencias | READ |
| `ACADEMIC_PROGRAM_MANAGE` | CRUD de programas y estructura curricular | WRITE |
| `ACADEMIC_FICHA_VIEW` | Ver fichas de caracterización | READ |
| `ACADEMIC_FICHA_VIEW_OWN` | Ver solo fichas propias (como instructor asignado) | READ |
| `ACADEMIC_FICHA_MANAGE` | Crear y editar fichas | WRITE |
| `ACADEMIC_FICHA_STATUS` | Cambiar estado de una ficha | WRITE |

### MOD_ENVIRONMENT

| Código de feature | Descripción | Nivel de acción |
|------------------|-------------|----------------|
| `ENV_VIEW` | Ver ambientes y disponibilidad | READ |
| `ENV_MANAGE` | CRUD de ambientes y tipos | WRITE |
| `ENV_MAINTENANCE_MANAGE` | Registrar y editar mantenimientos | WRITE |
| `ENV_RESERVATION_MANAGE` | Gestionar reservas de ambientes | WRITE |
| `ENV_AVAILABILITY_QUERY` | Consultar disponibilidad para asignación | READ |

### MOD_SCHEDULING

| Código de feature | Descripción | Nivel de acción |
|------------------|-------------|----------------|
| `SCH_VIEW_ALL` | Ver todos los horarios del centro | READ |
| `SCH_VIEW_OWN` | Ver solo el propio horario | READ |
| `SCH_VIEW_FICHA` | Ver horario de una ficha específica | READ |
| `SCH_CREATE` | Crear borrador de horario | WRITE |
| `SCH_EDIT` | Editar sesiones de un borrador | WRITE |
| `SCH_DELETE_DRAFT` | Eliminar un borrador de horario | DELETE |
| `SCH_PUBLISH` | Publicar un horario validado | PUBLISH |
| `SCH_ARCHIVE` | Archivar un horario publicado | WRITE |
| `SCH_CONFLICT_VIEW` | Ver conflictos detectados en borradores | READ |
| `SCH_CONFLICT_RESOLVE` | Marcar conflictos como resueltos | WRITE |

### MOD_ACTORS

| Código de feature | Descripción | Nivel de acción |
|------------------|-------------|----------------|
| `ACT_INSTRUCTOR_VIEW` | Ver lista y perfil de instructores | READ |
| `ACT_INSTRUCTOR_MANAGE` | CRUD de instructores | WRITE |
| `ACT_INSTRUCTOR_FICHA_ASSIGN` | Asignar y retirar instructores de una ficha (asignacion administrativa que gestiona el coordinador, HU-ACT-033) | WRITE |
| `ACT_LEARNER_VIEW` | Ver lista y perfil de aprendices | READ |
| `ACT_LEARNER_VIEW_OWN` | Ver solo el propio perfil (aprendiz) | READ |
| `ACT_LEARNER_MANAGE` | YES GLOBAL | YES TRAINING_CENTER | YES TRAINING_CENTER | NO | NO | NO |
| `ACT_LEARNER_MANAGE` | CRUD de aprendices | WRITE |
| `ACT_COMPETENCY_VIEW` | Ver competencias asignadas a instructores | READ |
| `ACT_COMPETENCY_ASSIGN` | Asignar/revocar competencias a instructores | WRITE |
| `ACT_PRODUCTIVE_STAGE_MANAGE` | Gestionar etapas productivas | WRITE |
| `ACT_COMPANY_VIEW` | Ver empresas vinculadas | READ |
| `ACT_COMPANY_MANAGE` | CRUD de empresas | WRITE |
| `ACT_ACTIVITY_LOG_VIEW` | Ver bitácora de actividad de actores | READ |
| `ACT_INTERNAL_FICHA_LEARNER_COUNT` | Contar aprendices activos por ficha (interno, servicio-a-servicio) | READ |
| `ACT_LEARNER_RAP_ASSESSMENT_MANAGE` | Registrar o corregir el juicio evaluativo (APPROVED / NOT_APPROVED) de un aprendiz sobre un RAP de su ficha | WRITE |
| `ACT_INTERNAL_FICHA_RAP_COVERAGE` | Verificar la cobertura de aprobación de RAP de los aprendices activos de una ficha (interno, servicio-a-servicio) | READ |

### MOD_DOCUMENTS

| Código de feature | Descripción | Nivel de acción |
|------------------|-------------|----------------|
| `DOC_VIEW` | Ver documentos disponibles | READ |
| `DOC_DOWNLOAD` | Descargar documentos | READ |
| `DOC_CREATE` | Generar nuevos documentos | WRITE |
| `DOC_TEMPLATE_MANAGE` | CRUD de plantillas de documentos | WRITE |
| `DOC_ARCHIVE` | Archivar documentos | WRITE |

### MOD_MONITORING

| Código de feature | Descripción | Nivel de acción |
|------------------|-------------|----------------|
| `MON_DASHBOARD_FULL` | Panel de seguimiento completo del centro | READ |
| `MON_DASHBOARD_OWN` | Panel de seguimiento de fichas propias | READ |
| `MON_TRACKING_SESSION_CREATE` | Registrar sesión de seguimiento | WRITE |
| `MON_TRACKING_SESSION_VIEW` | Ver sesiones de seguimiento | READ |
| `MON_KPI_VIEW` | Ver indicadores KPI por ficha | READ |
| `MON_CATALOG_MANAGE` | Administrar catálogos de monitoreo | WRITE |
| `MON_ALERT_VIEW` | Ver alertas generadas | READ |
| `MON_ALERT_RESOLVE` | Marcar alertas como resueltas | WRITE |
| `MON_IMPROVEMENT_PLAN_MANAGE` | Crear y editar planes de mejoramiento | WRITE |
| `MON_REPORT_VIEW` | Ver reportes agregados de monitoreo | READ |

### MOD_NOTIFICATIONS

| Código de feature | Descripción | Nivel de acción |
|------------------|-------------|----------------|
| `NOTIF_VIEW_OWN` | Ver las notificaciones propias | READ |
| `NOTIF_VIEW_ALL` | Consultar notificaciones dentro del scope autorizado | READ |
| `NOTIF_SEND` | Solicitar una notificación manual | WRITE |
| `NOTIF_TEMPLATE_MANAGE` | Gestionar plantillas de notificación | WRITE |

### MOD_AUDIT

| Código de feature | Descripción | Nivel de acción |
|------------------|-------------|----------------|
| `AUDIT_LOG_VIEW` | Ver log de auditoría del sistema | READ |
| `AUDIT_EXPORT` | Exportar log de auditoría | READ |

### MOD_DASHBOARD

| Código de feature | Descripción | Nivel de acción |
|------------------|-------------|----------------|
| `DASH_CENTER_OVERVIEW` | Panel general del centro (métricas, alertas) | READ |
| `DASH_PERSONAL` | Panel personal (mi horario, mis fichas) | READ |

---

## Tipos de scope (alcance de datos)

El `scope_type` define qué filas puede ver/operar el rol con ese feature.

| scope_type | Descripción | Ejemplo de uso |
|-----------|-------------|----------------|
| `GLOBAL` | Sin restricciones de datos | SYSTEM_ADMIN viendo todos los usuarios |
| `TRAINING_CENTER` | Solo datos del propio centro | COORDINATOR viendo fichas de su centro |
| `AREA` | Solo datos del área tecnológica asignada | AREA_LEADER viendo fichas de su área |
| `OWN_FICHAS` | Solo fichas donde el usuario es instructor asignado | INSTRUCTOR viendo sesiones de seguimiento |
| `OWN_SCHEDULE` | Solo el propio horario del usuario | INSTRUCTOR viendo su horario |
| `OWN_PROFILE` | Solo el propio perfil del usuario | LEARNER viendo su datos de formación |
| `OWN_FICHA_AS_LEARNER` | Solo la ficha propia del aprendiz | LEARNER viendo su horario |

---

## Matriz de Roles y Features

Leyenda: ✅ Permitido | ❌ Sin acceso | scope entre paréntesis

### MOD_IDENTITY y MOD_REFERENCE

| Feature | SYSTEM_ADMIN | CENTER_DIRECTOR | COORDINATOR | INSTRUCTOR | LEARNER | ADMIN_STAFF |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| `IDENTITY_USER_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ | ❌ |
| `IDENTITY_USER_MANAGE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ | ❌ |
| `IDENTITY_ROLE_VIEW` | ✅ GLOBAL | ❌ | ❌ | ❌ | ❌ | ❌ |
| `IDENTITY_ROLE_MANAGE` | ✅ GLOBAL | ❌ | ❌ | ❌ | ❌ | ❌ |
| `IDENTITY_ROLE_ASSIGN` | ✅ GLOBAL | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ | ❌ |
| `REF_CATALOG_VIEW` | ✅ GLOBAL | ✅ GLOBAL | ✅ GLOBAL | ✅ GLOBAL | ✅ GLOBAL | ✅ GLOBAL |
| `REF_CATALOG_MANAGE` | ✅ GLOBAL | ❌ | ❌ | ❌ | ❌ | ✅ GLOBAL |
| `REF_HIERARCHY_VIEW` | ✅ GLOBAL | ✅ GLOBAL | ✅ GLOBAL | ✅ GLOBAL | ❌ | ✅ GLOBAL |
| `REF_HIERARCHY_MANAGE` | ✅ GLOBAL | ❌ | ❌ | ❌ | ❌ | ✅ GLOBAL |
| `REF_PARAMETER_VIEW` | ✅ GLOBAL | ✅ GLOBAL | ❌ | ❌ | ❌ | ✅ GLOBAL |
| `REF_PARAMETER_MANAGE` | ✅ GLOBAL | ❌ | ❌ | ❌ | ❌ | ✅ GLOBAL |

### MOD_ACADEMIC y MOD_ENVIRONMENT

| Feature | SYSTEM_ADMIN | CENTER_DIRECTOR | COORDINATOR | INSTRUCTOR | LEARNER | ADMIN_STAFF |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| `ACADEMIC_PROGRAM_VIEW` | ✅ GLOBAL | ✅ GLOBAL | ✅ GLOBAL | ✅ GLOBAL | ✅ GLOBAL | ❌ |
| `ACADEMIC_PROGRAM_MANAGE` | ✅ GLOBAL | ❌ | ❌ | ❌ | ❌ | ✅ GLOBAL |
| `ACADEMIC_FICHA_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `ACADEMIC_FICHA_VIEW_OWN` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_FICHAS | ✅ OWN_FICHA_AS_LEARNER | ❌ |
| `ACADEMIC_FICHA_MANAGE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `ACADEMIC_FICHA_STATUS` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `ENV_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_FICHA_AS_LEARNER | ❌ |
| `ENV_MANAGE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `ENV_MAINTENANCE_MANAGE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `ENV_AVAILABILITY_QUERY` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ |

### MOD_SCHEDULING

| Feature | SYSTEM_ADMIN | CENTER_DIRECTOR | COORDINATOR | INSTRUCTOR | LEARNER | ADMIN_STAFF |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| `SCH_VIEW_ALL` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `SCH_VIEW_OWN` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_SCHEDULE | ✅ OWN_FICHA_AS_LEARNER | ❌ |
| `SCH_CREATE` | ✅ GLOBAL | ❌ | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `SCH_EDIT` | ✅ GLOBAL | ❌ | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `SCH_DELETE_DRAFT` | ✅ GLOBAL | ❌ | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `SCH_PUBLISH` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `SCH_ARCHIVE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `SCH_CONFLICT_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `SCH_CONFLICT_RESOLVE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |

### MOD_ACTORS, MOD_MONITORING y MOD_NOTIFICATIONS

| Feature | SYSTEM_ADMIN | CENTER_DIRECTOR | COORDINATOR | INSTRUCTOR | LEARNER | ADMIN_STAFF |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| `ACT_INSTRUCTOR_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_PROFILE | ✅ OWN_FICHA_AS_LEARNER | ❌ |
| `ACT_INSTRUCTOR_MANAGE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ | ❌ |
| `ACT_INSTRUCTOR_FICHA_ASSIGN` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `ACT_LEARNER_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_FICHAS | ❌ | ❌ |
| `ACT_LEARNER_VIEW_OWN` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_FICHAS | ✅ OWN_PROFILE | ❌ |
| `ACT_COMPETENCY_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_PROFILE | ❌ | ❌ |
| `ACT_COMPETENCY_ASSIGN` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `ACT_PRODUCTIVE_STAGE_MANAGE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_FICHAS | ❌ | ❌ |
| `ACT_INTERNAL_FICHA_LEARNER_COUNT` | ✅ GLOBAL | ❌ | ❌ | ❌ | ❌ | ❌ |
| `ACT_LEARNER_RAP_ASSESSMENT_MANAGE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `ACT_INTERNAL_FICHA_RAP_COVERAGE` | ✅ GLOBAL | ❌ | ❌ | ❌ | ❌ | ❌ |
| `MON_DASHBOARD_FULL` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `MON_DASHBOARD_OWN` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_FICHAS | ❌ | ❌ |
| `MON_TRACKING_SESSION_CREATE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_FICHAS | ❌ | ❌ |
| `MON_KPI_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_FICHAS | ❌ | ❌ |
| `MON_CATALOG_MANAGE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `MON_ALERT_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_FICHAS | ❌ | ❌ |
| `MON_ALERT_RESOLVE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `MON_IMPROVEMENT_PLAN_MANAGE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_FICHAS | ❌ | ❌ |
| `MON_REPORT_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `NOTIF_VIEW_OWN` | ✅ GLOBAL | ✅ OWN_PROFILE | ✅ OWN_PROFILE | ✅ OWN_PROFILE | ✅ OWN_PROFILE | ✅ OWN_PROFILE |
| `NOTIF_VIEW_ALL` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `NOTIF_SEND` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `NOTIF_TEMPLATE_MANAGE` | ✅ GLOBAL | ❌ | ❌ | ❌ | ❌ | ❌ |
| `AUDIT_LOG_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ | ❌ |

> **Aprendiz lee ambientes (2026-11-02):** `LEARNER` recibe `ENV_VIEW` con scope `OWN_FICHA_AS_LEARNER` (solo lectura) para que "Mi horario" muestre el nombre del ambiente. Los endpoints `GET /training-environments` y `/{id}` de training-environment-service validan solo la presencia de la feature (no filtran por scope); `/reservations` exige GLOBAL o TRAINING_CENTER y responde 403 a este scope. No requiere centro de formacion al asignar el rol (`requiresTrainingCenterScope` solo se activa con scope `TRAINING_CENTER`). Seed aditivo en `design-software-iam-db`.
>
> **Visibilidad de instructores para el aprendiz (HU-ACT-033, 2026-11-03).** `LEARNER` recibe `ACT_INSTRUCTOR_VIEW` con scope `OWN_FICHA_AS_LEARNER`: solo ve a los instructores con una asignacion activa a su propia ficha (la ficha sale de su inscripcion activa), en vista reducida `InstructorSummary` (`id`, `full_name`, `first_name`, `last_name`; sin correo, telefono ni documento). Cualquier otro instructor responde 404. Contratos, areas, competencias y excepciones de disponibilidad del instructor siguen cerrados al aprendiz (403). El scope `OWN_FICHA_AS_LEARNER` no activa `requiresTrainingCenterScope` (solo `TRAINING_CENTER` lo hace). La asignacion instructor-ficha la administra el coordinador en actors-service; este punto ya no depende de HU-ACT-031 (docs#419), que trata los juicios de RAP. Seed aditivo `016` en `design-software-iam-db`.

> **M2M / service-to-service:** `ACT_INTERNAL_FICHA_LEARNER_COUNT` no se otorga a roles
> humanos de operación diaria. Debe emitirse en tokens de cliente de servicio
> (client credentials) para `academic-management-service` con scope `GLOBAL`, de modo
> que pueda invocar
> `GET /internal/fichas/{ficha_id}/active-learners/count` en actors-service.
> `SYSTEM_ADMIN` conserva el feature con scope `GLOBAL` solo para diagnóstico.
> El JWT de llamada también debe incluir `ACADEMIC_FICHA_VIEW:GLOBAL` cuando Actors
> valide la existencia de la ficha contra Academic Management (acuerdo IAM/Academic).

---

## Features sin duena funcional: decision del dueno (2026-11-03)

Regla del dueno: ningun feature del catalogo puede quedar huerfano (sin fila en `rbac.role_feature`). Los 9 features de la tabla no tenian ninguna asignacion. El changeset `ds-orphan-features-system-admin-014` (`design-software-iam-db`) los concedio a `SYSTEM_ADMIN` con scope `GLOBAL`; el 2026-11-03 el dueno aprobo la tabla de propuestas y el changeset aditivo `ds-rbac-decisions-2026-11-03-015` concede el resto. Antes de conceder se verifico en `origin/develop` que el servicio dueno acepta el scope.

| Feature | Servicio dueno | Que hace | Concesion aprobada | Verificacion en el servicio |
|---------|----------------|----------|--------------------|-----------------------------|
| `SCH_VIEW_FICHA` | scheduling-service | Ver el horario de una ficha concreta. El controller hoy NO lo exige (usa `SCH_VIEW_ALL`/`SCH_VIEW_OWN`; el contrato dice "sin SCH_VIEW_FICHA") | Solo `SYSTEM_ADMIN` (`GLOBAL`) | Sin consumidor real |
| `MON_TRACKING_SESSION_VIEW` | monitoring-service | Consultar sesiones de seguimiento (listado y detalle) | `CENTER_DIRECTOR`/`COORDINATOR` `TRAINING_CENTER`; `INSTRUCTOR` `OWN_FICHAS` | Solo valida presencia del feature (acepta cualquier scope, igual que el resto de `MON_*`); sin filtro de datos por scope |
| `MON_NOTIFICATION_SEND` | monitoring-service / notification-service | Enviar notificaciones desde monitoreo | **No concedido (solo `SYSTEM_ADMIN` `GLOBAL`)** | Ningun servicio lo exige: notification-service exige `NOTIFICATION_SEND` (otro codigo, que no esta en el catalogo) y un token con `MON_NOTIFICATION_SEND` recibe 403. Pendiente: unificar el codigo antes de conceder |
| `ENV_RESERVATION_MANAGE` | training-environment-service | Crear, editar y cancelar reservas de ambiente (`POST/PATCH/DELETE /reservations`) | `CENTER_DIRECTOR`/`COORDINATOR` `TRAINING_CENTER` | Las mutaciones validan presencia; el filtro por centro de las lecturas de reservas sale de `ENV_VIEW` (`TRAINING_CENTER` ya concedido a esos roles) |
| `DOC_TEMPLATE_MANAGE` | document-service | CRUD de plantillas de documento | `ADMIN_STAFF` `GLOBAL` | Las plantillas son globales; el servicio exige presencia del feature. `ADMIN_STAFF` ya tenia `DOC_TEMPLATE_VIEW` |
| `DOC_ARCHIVE` | document-service | Archivar un documento (borrado logico, `status = ARCHIVED`) | `CENTER_DIRECTOR`/`COORDINATOR` `TRAINING_CENTER`, junto con `DOC_VIEW` y `DOC_CREATE` en el mismo scope | `DOC_VIEW`/`DOC_CREATE` aceptan `GLOBAL` y `TRAINING_CENTER` (`resolve_document_access`); `DOC_ARCHIVE` aun no tiene endpoint en document-service (el grant queda listo, nada lo exige todavia) |
| `IDENTITY_SCOPE_MANAGE` | iam-service | Crear y revocar overrides de scope por usuario | Solo `SYSTEM_ADMIN` (`GLOBAL`) | Es una escalada de privilegios; se mantiene en administracion tecnica |
| `DASH_CENTER_OVERVIEW` | web-bff / shell (sin endpoint backend aun) | Panel general del centro (metricas, alertas) | Solo `SYSTEM_ADMIN` (`GLOBAL`) | Hoy ningun servicio lo exige |
| `DASH_PERSONAL` | web-bff / shell (sin endpoint backend aun) | Panel personal (mi horario, mis fichas) | Solo `SYSTEM_ADMIN` (`GLOBAL`) | Hoy ningun servicio lo exige |

Nota: `DOC_DOWNLOAD` no se abre a `CENTER_DIRECTOR`/`COORDINATOR` en esta decision; con `DOC_VIEW` y `DOC_CREATE` pueden generar y consultar documentos de su centro, pero no descargarlos.

La asignacion de `ACT_LEARNER_MANAGE` sigue HU-11 (gestion de aprendices por ficha) y HU-ACT-007 (inscripcion en ficha): `SYSTEM_ADMIN` con scope `GLOBAL`, y `CENTER_DIRECTOR`/`COORDINATOR` con scope `TRAINING_CENTER`. El seed aditivo vive en `design-software-iam-db`.

---

## AREA_LEADER: "centro ahora, area despues" (decision del dueno, 2026-11-03)

**Decision del dueno:** `AREA_LEADER` recibe **todas las features de solo lectura de `COORDINATOR`** (`VIEW`, `REPORT_VIEW`, `CONFLICT_VIEW`, catalogos y jerarquia). Nunca crear, editar, publicar, archivar, eliminar, gestionar, resolver ni asignar. Mientras no exista infraestructura de area, las recibe con scope `TRAINING_CENTER`.

**Estado actual: AREA_LEADER ve el centro completo, no solo su area.** El changeset `ds-rbac-decisions-2026-11-03-015` (`design-software-iam-db`) concede 25 features: 22 con `TRAINING_CENTER` (`ACADEMIC_FICHA_VIEW`, `ACADEMIC_FICHA_VIEW_OWN`, `ACT_ACTIVITY_LOG_VIEW`, `ACT_COMPANY_VIEW`, `ACT_COMPETENCY_VIEW`, `ACT_INSTRUCTOR_VIEW`, `ACT_LEARNER_VIEW`, `ACT_LEARNER_VIEW_OWN`, `ACT_REPORT_VIEW`, `ENV_AVAILABILITY_QUERY`, `ENV_VIEW`, `ENVIRONMENT_REPORT_VIEW`, `MON_ALERT_VIEW`, `MON_DASHBOARD_FULL`, `MON_DASHBOARD_OWN`, `MON_KPI_VIEW`, `MON_NOTIFICATION_VIEW`, `MON_REPORT_VIEW`, `SCH_CONFLICT_VIEW`, `SCH_REPORT_VIEW`, `SCH_VIEW_ALL`, `SCH_VIEW_OWN`) y 3 catalogos con `GLOBAL`, igual que `COORDINATOR` (`ACADEMIC_PROGRAM_VIEW`, `REF_CATALOG_VIEW`, `REF_HIERARCHY_VIEW`; reference-data rechaza cualquier grant `REF_*` que no sea `GLOBAL`).

**Impactos de aprovisionamiento:** `requiresTrainingCenterScope(roleId)` es `true` si el rol tiene al menos un grant `TRAINING_CENTER`; por eso `CreateUser` y `AssignUserRole` ahora exigen `trainingCenterId` para `AREA_LEADER`. El usuario sintetico `synthetic.area-leader@example.test` recibe el centro sintetico `5e000000-0000-4000-8000-0000000000a5` con el changeset `ds-area-leader-synthetic-training-center-004` (contextos `dev,qa`), igual que `003` lo hace para `CENTER_DIRECTOR` y `COORDINATOR`.

**Por que no `AREA` todavia:**

1. **El JWT no lleva claim de area.** `JwtAccessTokenIssuer` emite `sid, email, name, actor_type, actor_id, roles, features, training_center_id` (y `ficha_id` para aprendices). `rbac.user_role` solo tiene `training_center_id`; no existe columna ni tabla de area para el usuario en iam-db.
2. **Ningun servicio backend filtra por `AREA`.** `AuthorizationPolicy` de iam documenta que `AREA` lo aplica el servicio dueno, pero ninguno lo hace. Verificado en `origin/develop`:

| Servicio | Features de lectura | Scopes que soporta hoy | Comportamiento ante `AREA` |
|----------|---------------------|------------------------|----------------------------|
| scheduling-service | `SCH_VIEW_ALL`, `SCH_VIEW_OWN`, `SCH_CONFLICT_VIEW`, `SCH_REPORT_VIEW` | `GLOBAL`, `TRAINING_CENTER`, `OWN_SCHEDULE`, `OWN_FICHA_AS_LEARNER` | fail-closed 403 ("Scope no resoluble") |
| academic-management-service | `ACADEMIC_FICHA_VIEW`, `ACADEMIC_FICHA_VIEW_OWN` | `GLOBAL`, `TRAINING_CENTER`, `OWN_FICHAS`, `OWN_FICHA_AS_LEARNER` | `AREA` no existe en su enum de scopes; falla con 403 |
| training-environment-service | `ENV_VIEW`, `ENV_AVAILABILITY_QUERY`, `ENVIRONMENT_REPORT_VIEW` | `GLOBAL`, `TRAINING_CENTER` (reservas); en el resto `ENV_VIEW` solo valida presencia | 403 en `/reservations` ("unsupported ENV_VIEW scope"); sin filtro de area en el resto |
| actors-service | `ACT_INSTRUCTOR_VIEW`, `ACT_LEARNER_VIEW`, `ACT_REPORT_VIEW` | `GLOBAL`, `TRAINING_CENTER`, `OWN_PROFILE`, `OWN_FICHAS`; `ACT_INSTRUCTOR_VIEW` tambien `OWN_FICHA_AS_LEARNER` (HU-ACT-033) | scope no soportado (`UnsupportedScopeException`) |
| monitoring-service | `MON_*_VIEW`, `MON_REPORT_VIEW` | presencia del feature | sin filtro por area |
| reference-data / notification | `REF_*_VIEW`, `MON_NOTIFICATION_VIEW` | aceptan `AREA` como valor valido pero no lo aplican | sin filtro por area |

**Seguimiento (scoping real por area):** backlog HU code-sena/design-software-docs#500 — area por usuario en iam, claim `area_id` en el JWT y filtro `AREA` en scheduling, academic-management y actors. Al completarla, un changeset aditivo mueve los grants de `AREA_LEADER` de `TRAINING_CENTER` a `AREA` y se retira esta nota.

---

## Cómo se aplica el scope en cada servicio

El JWT del usuario lleva pre-calculado:
```json
{
  "sub": "uuid-del-usuario",
  "actor_type": "instructor",
  "actor_id": "uuid-del-instructor",
  "roles": ["INSTRUCTOR"],
  "training_center_id": "uuid-del-centro",
  "features": [
    "SCH_VIEW_OWN:OWN_SCHEDULE",
    "ACADEMIC_FICHA_VIEW_OWN:OWN_FICHAS",
    "MON_DASHBOARD_OWN:OWN_FICHAS",
    "MON_TRACKING_SESSION_CREATE:OWN_FICHAS",
    "MON_KPI_VIEW:OWN_FICHAS",
    "MON_ALERT_VIEW:OWN_FICHAS",
    "ACT_INSTRUCTOR_VIEW:OWN_PROFILE"
  ],
  "exp": 1234567890
}
```

Cada servicio downstream aplica el scope del feature según su lógica interna:

| Scope | Cómo lo aplica el servicio |
|-------|---------------------------|
| `GLOBAL` | Sin filtro adicional en la query |
| `TRAINING_CENTER` | Agrega `WHERE training_center_id = <jwt.training_center_id>` |
| `OWN_FICHAS` | Agrega `WHERE instructor_id = <jwt.actor_id>` |
| `OWN_SCHEDULE` | Agrega `WHERE instructor_id = <jwt.actor_id>` en class_session |
| `OWN_PROFILE` | Solo permite ver/editar el recurso cuyo `id = <jwt.actor_id>` |
| `OWN_FICHA_AS_LEARNER` | Agrega `WHERE ficha_id = <jwt.ficha_id>` (aprendiz tiene una ficha activa) |

---

## Overrides de scope por usuario

Para casos excepcionales (ej. un instructor que cubre a un coordinador temporalmente), se pueden agregar features adicionales con un scope específico a un usuario individual mediante `user_scope_override`.

Un override puede ser:
- **Aditivo** (`is_allowed = true`): agrega acceso que el rol no tiene
- **Restrictivo** (`is_allowed = false`): elimina acceso que el rol tiene
- **Con expiración** (`expires_at`): acceso temporal

Los overrides se incluyen en el JWT con el mismo formato: `FEATURE_CODE:SCOPE_TYPE`.

---

## Inicialización del sistema

Al inicializar el sistema se deben crear los registros base:

```sql
-- Módulos del sistema (10 registros)
INSERT INTO module (code, name, display_order) VALUES
  ('MOD_IDENTITY', 'Identidad y Seguridad', 1),
  ('MOD_REFERENCE', 'Datos de Referencia', 2),
  ...

-- Features del sistema (~50 registros, ver catálogo arriba)
INSERT INTO feature (module_id, code, name) VALUES ...

-- Roles del sistema (7 registros)
INSERT INTO role (name) VALUES
  ('SYSTEM_ADMIN'), ('CENTER_DIRECTOR'), ('COORDINATOR'),
  ('AREA_LEADER'), ('INSTRUCTOR'), ('LEARNER'), ('ADMIN_STAFF') ...

-- Asignación de features a roles (ver matriz arriba)
INSERT INTO role_feature (role_id, feature_id, scope_type) VALUES ...
```

La inicialización de datos base se ejecuta mediante seeds en el primer deploy.

## HU-ACAD-11 service-token audiences (ADR-030)

The Academic R4 implementation uses POST /api/v1/auth/token with
grant_type=client_credentials, HTTP Basic client authentication, and an
allowlisted audience. The issued service JWT contains that audience in aud and
receives only the features mapped to it:

| Audience | Feature authorities |
|-----------|---------------------|
| actors-service | ACT_INTERNAL_FICHA_LEARNER_COUNT:GLOBAL, ACT_INTERNAL_FICHA_RAP_COVERAGE:GLOBAL, ACADEMIC_FICHA_VIEW:GLOBAL |
| scheduling-service | SCH_REPORT_VIEW:GLOBAL |

`audience` is optional: when it is omitted IAM treats the request as
`actors-service`, so the pre-R4 Academic client keeps working while IAM is
deployed first. An unknown or blank audience is rejected with `invalid_target`.
Omission is a transitional allowance.

Actors and Scheduling validate the audience before exposing service-token
feature authorities. Credentials are supplied through secret storage. Approved
by the project owner on 2026-10-24; see ADR-030 in the architecture decisions.
The `scheduling-service` audience serves the informative execution report only;
Academic does not call it in this release.

### Judgment of learning outcomes (RAP)

`ACT_LEARNER_RAP_ASSESSMENT_MANAGE` lets a user record or correct a learner's
`APPROVED` / `NOT_APPROVED` judgment on a RAP of the learner's ficha (ADR-030,
RN-ACAD-07). It replaces the numeric final-grade feature of the first draft of
this PR; no such feature was ever released. The roles above are the current seed
(`SYSTEM_ADMIN` global; `CENTER_DIRECTOR` and `COORDINATOR` by training center);
the owner confirmed them on 2026-10-24. Letting `INSTRUCTOR` record judgments,
limited to the fichas and RAPs they teach, is the work item HU-ACT-031
(code-sena/design-software-docs#419). Since 2026-11-03 the DoR source of that
item is decided: "the fichas an instructor teaches" is read from the
coordinator-managed assignment of HU-ACT-033 (code-sena/design-software-docs#498).

### Instructor-to-ficha assignment

`ACT_INSTRUCTOR_FICHA_ASSIGN` lets a user assign an instructor to a ficha and remove
the assignment (soft delete). Owner decision of 2026-11-03: the assignment is
coordinator-managed and lives in actors-service. Seed (`design-software-iam-db`,
changeset `hu-act-033-instructor-ficha-assignment-016`): `SYSTEM_ADMIN` global;
`CENTER_DIRECTOR` and `COORDINATOR` by training center. With `TRAINING_CENTER`
actors-service reads the training center of the ficha from academic-management and
requires the instructor's current contract to be at that center. The same seed grants
`LEARNER` the feature `ACT_INSTRUCTOR_VIEW` at `OWN_FICHA_AS_LEARNER`. Users must log
in again to get the new features in their token.
