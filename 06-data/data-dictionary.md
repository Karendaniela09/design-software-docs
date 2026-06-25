# Diccionario de datos

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Datos

## Contexto

Este documento contiene el diccionario de datos del sistema **Horarios SENA**. Describe cada tabla y campo con su tipo, propósito, restricciones y relación con otras tablas. Está organizado por esquema.

---

## reference_schema

### Tabla: `macroregion`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `name` | VARCHAR(100) | Nombre de la región | NOT NULL, UNIQUE |
| `description` | TEXT | Descripción adicional | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `microregion`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `macroregion_id` | UUID | Referencia a macroregión | FK(macroregion.id) |
| `name` | VARCHAR(100) | Nombre de la microregión | NOT NULL, UNIQUE |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `department`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `microregion_id` | UUID | Referencia a microregión | FK(microregion.id) |
| `name` | VARCHAR(100) | Nombre del departamento | NOT NULL, UNIQUE |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `municipality`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `department_id` | UUID | Referencia a departamento | FK(department.id) |
| `name` | VARCHAR(100) | Nombre del municipio | NOT NULL, UNIQUE |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `location`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `municipality_id` | UUID | Referencia a municipio | FK(municipality.id) |
| `address` | VARCHAR(255) | Dirección completa | NOT NULL |
| `postal_code` | VARCHAR(20) | Código postal | - |
| `latitude` | NUMERIC(10,6) | Latitud geográfica | - |
| `longitude` | NUMERIC(10,6) | Longitud geográfica | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `training_center`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `microregion_id` | UUID | Referencia a microregión | FK(microregion.id) |
| `code` | VARCHAR(20) | Código del centro | NOT NULL, UNIQUE |
| `name` | VARCHAR(150) | Nombre del centro | NOT NULL |
| `type` | VARCHAR(50) | Tipo de centro | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `institutional_unit`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `training_center_id` | UUID | Referencia a centro | FK(training_center.id) |
| `location_id` | UUID | Referencia a ubicación | FK(location.id) |
| `name` | VARCHAR(150) | Nombre de la unidad | NOT NULL |
| `unit_type` | VARCHAR(50) | Tipo: Sede, Tecnoacademia, Tecnoparque | - |
| `phone` | VARCHAR(20) | Teléfono de contacto | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `catalog`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `code` | VARCHAR(20) | Código del catálogo | NOT NULL, UNIQUE |
| `name` | VARCHAR(100) | Nombre del catálogo | NOT NULL |
| `description` | TEXT | Descripción | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `catalog_detail`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `catalog_id` | UUID | Referencia a catálogo | FK(catalog.id) |
| `state_id` | UUID | Referencia a estado | FK(state.id) |
| `code` | VARCHAR(20) | Código del detalle | NOT NULL, UNIQUE |
| `name` | VARCHAR(100) | Nombre del detalle | NOT NULL |
| `description` | TEXT | Descripción | - |
| `display_order` | INTEGER | Orden de visualización | - |
| `valid_from` | DATE | Inicio de vigencia | - |
| `valid_to` | DATE | Fin de vigencia | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `state`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `code` | VARCHAR(20) | Código del estado | NOT NULL, UNIQUE |
| `name` | VARCHAR(50) | Nombre del estado | NOT NULL |
| `description` | TEXT | Descripción | - |
| `color` | VARCHAR(7) | Color hexadecimal (#RRGGBB) | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `parameter`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `module_id` | UUID | Referencia a módulo | FK(module.id) |
| `state_id` | UUID | Referencia a estado | FK(state.id) |
| `code` | VARCHAR(50) | Código del parámetro | NOT NULL, UNIQUE |
| `name` | VARCHAR(100) | Nombre del parámetro | NOT NULL |
| `value` | TEXT | Valor del parámetro | NOT NULL |
| `data_type` | VARCHAR(20) | Tipo de dato (STRING, INTEGER, BOOLEAN, DATE) | - |
| `min_value` | NUMERIC(10,2) | Valor mínimo | - |
| `max_value` | NUMERIC(10,2) | Valor máximo | - |
| `is_editable` | BOOLEAN | Editable por administrador | DEFAULT TRUE |
| `description` | TEXT | Descripción | - |

---

## academic_schema

### Tabla: `technological_line`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `code` | VARCHAR(20) | Código de línea | NOT NULL, UNIQUE |
| `name` | VARCHAR(100) | Nombre de la línea | NOT NULL |
| `description` | TEXT | Descripción | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `technological_network`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `technological_line_id` | UUID | Referencia a línea | FK(technological_line.id) |
| `code` | VARCHAR(20) | Código de red | NOT NULL, UNIQUE |
| `name` | VARCHAR(100) | Nombre de la red | NOT NULL |
| `description` | TEXT | Descripción | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `knowledge_network`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `technological_network_id` | UUID | Referencia a red tecnológica | FK(technological_network.id) |
| `code` | VARCHAR(20) | Código de red de conocimiento | NOT NULL, UNIQUE |
| `name` | VARCHAR(100) | Nombre de la red | NOT NULL |
| `description` | TEXT | Descripción | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `training_program`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `knowledge_network_id` | UUID | Referencia a red de conocimiento | FK(knowledge_network.id) |
| `training_type_id` | UUID | Referencia a tipo de formación | FK(catalog_detail.id) |
| `modality_id` | UUID | Referencia a modalidad | FK(catalog_detail.id) |
| `code` | VARCHAR(20) | Código del programa | NOT NULL, UNIQUE |
| `name` | VARCHAR(150) | Nombre del programa | NOT NULL |
| `version` | VARCHAR(10) | Versión del diseño | - |
| `duration_hours` | INTEGER | Horas totales | CHECK(duration_hours > 0) |
| `is_custom` | BOOLEAN | A la medida | DEFAULT FALSE |
| `valid_from` | DATE | Inicio de vigencia | - |
| `valid_to` | DATE | Fin de vigencia | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `competency`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `competency_type_id` | UUID | Referencia a tipo de competencia | FK(catalog_detail.id) |
| `code` | VARCHAR(20) | Código de competencia | NOT NULL, UNIQUE |
| `name` | VARCHAR(150) | Nombre de la competencia | NOT NULL |
| `description` | TEXT | Descripción | - |
| `total_hours` | INTEGER | Horas totales | CHECK(total_hours > 0) |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `learning_outcome`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `outcome_type_id` | UUID | Referencia a tipo de RAP | FK(catalog_detail.id) |
| `code` | VARCHAR(20) | Código del RAP | NOT NULL, UNIQUE |
| `name` | VARCHAR(250) | Nombre del RAP | NOT NULL |
| `description` | TEXT | Descripción detallada | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `program_competency`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `program_id` | UUID | Referencia a programa | FK(training_program.id) |
| `competency_id` | UUID | Referencia a competencia | FK(competency.id) |
| `order_in_curriculum` | INTEGER | Orden en la malla | NOT NULL |
| `hours_in_program` | INTEGER | Horas en el programa | CHECK(hours_in_program > 0) |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |
| **UNIQUE** | (program_id, competency_id) | - | - |
| **UNIQUE** | (program_id, order_in_curriculum) | - | - |

### Tabla: `competency_outcome`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `competency_id` | UUID | Referencia a competencia | FK(competency.id) |
| `outcome_id` | UUID | Referencia a RAP | FK(learning_outcome.id) |
| `order_in_competency` | INTEGER | Orden dentro de la competencia | NOT NULL |
| `hours_in_competency` | INTEGER | Horas para este RAP | CHECK(hours_in_competency > 0) |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |
| **UNIQUE** | (competency_id, outcome_id) | - | - |
| **UNIQUE** | (competency_id, order_in_competency) | - | - |

### Tabla: `training_group`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `program_id` | UUID | Referencia a programa | FK(training_program.id) |
| `modality_id` | UUID | Referencia a modalidad | FK(catalog_detail.id) |
| `shift_id` | UUID | Referencia a jornada | FK(catalog_detail.id) |
| `code` | VARCHAR(20) | Código de la ficha | NOT NULL, UNIQUE |
| `name` | VARCHAR(100) | Nombre de la ficha | - |
| `learner_count` | INTEGER | Número de aprendices | - |
| `start_date` | DATE | Fecha de inicio | - |
| `end_date` | DATE | Fecha de fin | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `offer`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `program_id` | UUID | Referencia a programa | FK(training_program.id) |
| `training_center_id` | UUID | Referencia a centro | FK(training_center.id) |
| `start_date` | DATE | Fecha de inicio de oferta | - |
| `end_date` | DATE | Fecha de fin de oferta | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

---

## scheduling_schema

### Tabla: `time_slot`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `day_of_week` | INTEGER | Día de la semana (0-6) | CHECK(day_of_week BETWEEN 0 AND 6) |
| `start_time` | TIME | Hora de inicio | NOT NULL |
| `end_time` | TIME | Hora de fin | NOT NULL, CHECK(end_time > start_time) |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `schedule`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `instructor_id` | UUID | Referencia lógica a instructor | NOT NULL |
| `environment_id` | UUID | Referencia lógica a ambiente | NOT NULL |
| `training_group_id` | UUID | Referencia lógica a ficha | NOT NULL |
| `time_slot_id` | UUID | Referencia a franja horaria | FK(time_slot.id) |
| `date` | DATE | Fecha del horario | NOT NULL |
| `status` | VARCHAR(20) | SCHEDULED, CANCELLED, EXECUTED | NOT NULL, DEFAULT 'SCHEDULED' |
| `description` | TEXT | Descripción adicional | - |
| `created_at` | TIMESTAMP | Fecha de creación | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP | Fecha de actualización | DEFAULT CURRENT_TIMESTAMP |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `assignment`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `schedule_id` | UUID | Referencia a horario | FK(schedule.id) |
| `instructor_id` | UUID | Instructor asignado | NOT NULL |
| `environment_id` | UUID | Ambiente asignado | NOT NULL |
| `training_group_id` | UUID | Ficha asignada | NOT NULL |
| `assigned_by` | VARCHAR(100) | Responsable de la asignación | - |
| `assigned_at` | TIMESTAMP | Fecha de asignación | DEFAULT CURRENT_TIMESTAMP |

### Tabla: `conflict`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `schedule_id` | UUID | Referencia a horario | FK(schedule.id) |
| `conflict_type` | VARCHAR(20) | INSTRUCTOR, ENVIRONMENT, GROUP | NOT NULL |
| `conflicting_schedule_id` | UUID | Horario conflictivo | FK(schedule.id) |
| `description` | TEXT | Descripción del conflicto | - |
| `detected_at` | TIMESTAMP | Fecha de detección | DEFAULT CURRENT_TIMESTAMP |
| `resolved` | BOOLEAN | Resuelto/No resuelto | DEFAULT FALSE |

### Tabla: `class_session`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `schedule_id` | UUID | Referencia a horario | FK(schedule.id) |
| `actual_start_time` | TIMESTAMP | Hora real de inicio | - |
| `actual_end_time` | TIMESTAMP | Hora real de fin | - |
| `status` | VARCHAR(20) | EXECUTED, CANCELLED, PENDING | NOT NULL |
| `attendance_count` | INTEGER | Número de asistentes | - |

### Tabla: `observation`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `schedule_id` | UUID | Referencia a horario | FK(schedule.id) |
| `author` | VARCHAR(100) | Autor de la observación | NOT NULL |
| `text` | TEXT | Contenido de la observación | NOT NULL |
| `severity` | VARCHAR(20) | INFO, WARNING, CRITICAL | NOT NULL |
| `status` | VARCHAR(20) | OPEN, IN_PROGRESS, RESOLVED | NOT NULL, DEFAULT 'OPEN' |
| `created_at` | TIMESTAMP | Fecha de creación | DEFAULT CURRENT_TIMESTAMP |

---

## actors_schema

### Tabla: `instructor`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `first_name` | VARCHAR(50) | Nombre | NOT NULL |
| `last_name` | VARCHAR(50) | Apellido | NOT NULL |
| `email` | VARCHAR(100) | Correo electrónico | NOT NULL, UNIQUE |
| `phone` | VARCHAR(20) | Teléfono | - |
| `document_id` | VARCHAR(20) | Número de documento | NOT NULL, UNIQUE |
| `hire_type` | VARCHAR(20) | STAFF / CONTRACTOR | NOT NULL |
| `specialties` | TEXT[] | Array de especialidades | - |
| `max_hours_per_week` | INTEGER | Horas máximas semanales | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |
| `created_at` | TIMESTAMP | Fecha de creación | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP | Fecha de actualización | DEFAULT CURRENT_TIMESTAMP |

### Tabla: `learner`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `training_group_id` | UUID | Referencia a ficha | FK(training_group.id) |
| `first_name` | VARCHAR(50) | Nombre | NOT NULL |
| `last_name` | VARCHAR(50) | Apellido | NOT NULL |
| `email` | VARCHAR(100) | Correo electrónico | NOT NULL, UNIQUE |
| `document_id` | VARCHAR(20) | Número de documento | NOT NULL, UNIQUE |
| `phone` | VARCHAR(20) | Teléfono | - |
| `enrollment_date` | DATE | Fecha de matrícula | - |
| `status` | VARCHAR(20) | ACTIVE, WITHDRAWN, GRADUATED | NOT NULL, DEFAULT 'ACTIVE' |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `manager`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `training_center_id` | UUID | Referencia a centro | FK(training_center.id) |
| `first_name` | VARCHAR(50) | Nombre | NOT NULL |
| `last_name` | VARCHAR(50) | Apellido | NOT NULL |
| `email` | VARCHAR(100) | Correo electrónico | NOT NULL, UNIQUE |
| `role` | VARCHAR(50) | Rol del directivo | NOT NULL |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `company`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `name` | VARCHAR(150) | Nombre de la empresa | NOT NULL |
| `nit` | VARCHAR(20) | NIT de la empresa | NOT NULL, UNIQUE |
| `address` | VARCHAR(255) | Dirección | - |
| `contact_name` | VARCHAR(100) | Nombre de contacto | - |
| `contact_phone` | VARCHAR(20) | Teléfono de contacto | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `productive_stage`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `learner_id` | UUID | Referencia a aprendiz | FK(learner.id) |
| `company_id` | UUID | Referencia a empresa | FK(company.id) |
| `start_date` | DATE | Fecha de inicio | NOT NULL |
| `end_date` | DATE | Fecha de fin | - |
| `status` | VARCHAR(20) | ACTIVE, COMPLETED, SUSPENDED | NOT NULL, DEFAULT 'ACTIVE' |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

---

## iam_schema

### Tabla: `user`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `username` | VARCHAR(50) | Nombre de usuario | NOT NULL, UNIQUE |
| `email` | VARCHAR(100) | Correo electrónico | NOT NULL, UNIQUE |
| `password_hash` | VARCHAR(255) | Hash de la contraseña (BCrypt) | NOT NULL |
| `first_name` | VARCHAR(50) | Nombre | - |
| `last_name` | VARCHAR(50) | Apellido | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |
| `created_at` | TIMESTAMP | Fecha de creación | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP | Fecha de actualización | DEFAULT CURRENT_TIMESTAMP |

### Tabla: `role`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `name` | VARCHAR(50) | Nombre del rol | NOT NULL, UNIQUE |
| `description` | TEXT | Descripción | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `permission`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `name` | VARCHAR(50) | Nombre del permiso | NOT NULL, UNIQUE |
| `description` | TEXT | Descripción | - |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |

### Tabla: `user_role`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `user_id` | UUID | Referencia a usuario | FK(user.id) |
| `role_id` | UUID | Referencia a rol | FK(role.id) |
| **UNIQUE** | (user_id, role_id) | - | - |

### Tabla: `role_permission`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `role_id` | UUID | Referencia a rol | FK(role.id) |
| `permission_id` | UUID | Referencia a permiso | FK(permission.id) |
| **UNIQUE** | (role_id, permission_id) | - | - |

### Tabla: `session`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `user_id` | UUID | Referencia a usuario | FK(user.id) |
| `ip_address` | VARCHAR(45) | Dirección IP | - |
| `start_time` | TIMESTAMP | Inicio de sesión | DEFAULT CURRENT_TIMESTAMP |
| `end_time` | TIMESTAMP | Fin de sesión | - |

### Tabla: `token`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `user_id` | UUID | Referencia a usuario | FK(user.id) |
| `token` | TEXT | JWT | NOT NULL, UNIQUE |
| `expires_at` | TIMESTAMP | Fecha de expiración | NOT NULL |
| `revoked` | BOOLEAN | Revocado/No revocado | DEFAULT FALSE |

---

## audit_schema

### Tabla: `audit_log`

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `user_id` | UUID | Usuario que realizó la acción | NOT NULL |
| `action` | VARCHAR(20) | CREATE, UPDATE, DELETE, LOGIN, LOGOUT | NOT NULL |
| `entity_type` | VARCHAR(50) | Entidad afectada | NOT NULL |
| `entity_id` | UUID | ID de la entidad afectada | NOT NULL |
| `old_value` | JSONB | Valor anterior (para UPDATE y DELETE) | - |
| `new_value` | JSONB | Valor nuevo (para CREATE y UPDATE) | - |
| `ip_address` | VARCHAR(45) | IP desde donde se realizó la acción | - |
| `timestamp` | TIMESTAMP | Fecha y hora de la acción | DEFAULT CURRENT_TIMESTAMP |

---

## Referencias

- [models.md](./models.md) — Modelos conceptual, lógico y físico
- [migration-strategy.md](./migration-strategy.md) — Estrategia de migraciones
- [02-domain/entities-and-rules.md](../02-domain/entities-and-rules.md) — Reglas de negocio
- [05-architecture/overview.md](../05-architecture/overview.md) — Esquemas por microservicio