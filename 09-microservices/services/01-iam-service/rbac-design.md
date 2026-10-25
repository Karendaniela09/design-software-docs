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
| `ACT_LEARNER_VIEW` | Ver lista y perfil de aprendices | READ |
| `ACT_LEARNER_VIEW_OWN` | Ver solo el propio perfil (aprendiz) | READ |
| `ACT_LEARNER_MANAGE` | CRUD de aprendices | WRITE |
| `ACT_COMPETENCY_VIEW` | Ver competencias asignadas a instructores | READ |
| `ACT_COMPETENCY_ASSIGN` | Asignar/revocar competencias a instructores | WRITE |
| `ACT_PRODUCTIVE_STAGE_MANAGE` | Gestionar etapas productivas | WRITE |
| `ACT_COMPANY_VIEW` | Ver empresas vinculadas | READ |
| `ACT_COMPANY_MANAGE` | CRUD de empresas | WRITE |
| `ACT_ACTIVITY_LOG_VIEW` | Ver bitácora de actividad de actores | READ |
| `ACT_INTERNAL_FICHA_LEARNER_COUNT` | Contar aprendices activos por ficha (interno, servicio-a-servicio) | READ |

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
| `ENV_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ |
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
| `ACT_INSTRUCTOR_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_PROFILE | ❌ | ❌ |
| `ACT_INSTRUCTOR_MANAGE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ | ❌ |
| `ACT_LEARNER_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_FICHAS | ❌ | ❌ |
| `ACT_LEARNER_VIEW_OWN` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_FICHAS | ✅ OWN_PROFILE | ❌ |
| `ACT_COMPETENCY_VIEW` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_PROFILE | ❌ | ❌ |
| `ACT_COMPETENCY_ASSIGN` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ❌ | ❌ | ❌ |
| `ACT_PRODUCTIVE_STAGE_MANAGE` | ✅ GLOBAL | ✅ TRAINING_CENTER | ✅ TRAINING_CENTER | ✅ OWN_FICHAS | ❌ | ❌ |
| `ACT_INTERNAL_FICHA_LEARNER_COUNT` | ✅ GLOBAL | ❌ | ❌ | ❌ | ❌ | ❌ |
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

> **M2M / service-to-service:** `ACT_INTERNAL_FICHA_LEARNER_COUNT` no se otorga a roles
> humanos de operación diaria. Debe emitirse en tokens de cliente de servicio
> (client credentials) para `academic-management-service` con scope `GLOBAL`, de modo
> que pueda invocar
> `GET /internal/fichas/{ficha_id}/active-learners/count` en actors-service.
> `SYSTEM_ADMIN` conserva el feature con scope `GLOBAL` solo para diagnóstico.
> El JWT de llamada también debe incluir `ACADEMIC_FICHA_VIEW:GLOBAL` cuando Actors
> valide la existencia de la ficha contra Academic Management (acuerdo IAM/Academic).

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
