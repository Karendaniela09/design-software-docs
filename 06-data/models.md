# Modelos de datos

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Datos

## Contexto

Este documento describe los modelos de datos del sistema **Horarios SENA**, desde el nivel conceptual hasta el físico. Los modelos están organizados por esquema, correspondiente a cada microservicio.

---

## Modelo Conceptual (Alto Nivel)

El sistema gestiona los siguientes conceptos principales, agrupados por dominio:

### Gestión Institucional (reference_schema)
- Macroregión, Microregión, Departamento, Municipio, Ubicación, Centro de Formación, Unidad Institucional.
- Catálogo, Detalle de Catálogo, Estado, Parámetro.

### Gestión Académica (academic_schema)
- Línea Tecnológica, Red Tecnológica, Red de Conocimiento, Programa de Formación, Competencia, RAP.
- ProgramaCompetencia, CompetenciaResultado, Ficha, Oferta.

### Gestión de Recursos (actors_schema y env_schema)
- Instructor, Aprendiz, Directivo, Empresa, Etapa Productiva.
- Ambiente, Recurso, Mantenimiento, Reserva, Disponibilidad.

### Gestión de Horarios (scheduling_schema)
- Franja Horaria, Horario, Asignación, Conflicto, Sesión de Clase, Observación.

### Seguridad y Auditoría (iam_schema y audit_schema)
- Usuario, Rol, Permiso, Sesión, Token.
- Auditoría (append-only).

---

## Modelo Lógico (Relaciones y Atributos)

A continuación se detallan las tablas principales y sus relaciones. Los nombres están en inglés, singular y `snake_case`.

### reference_schema (Estructura Institucional y Catálogos)

| Tabla | Descripción | FK |
|-------|-------------|----|
| `macroregion` | Regiones naturales de Colombia | - |
| `microregion` | Departamentos o agrupaciones dentro de una macroregión | `macroregion_id` |
| `department` | Departamentos geográficos | `microregion_id` |
| `municipality` | Municipios | `department_id` |
| `location` | Direcciones con coordenadas | `municipality_id` |
| `training_center` | Centros de formación | `microregion_id` |
| `institutional_unit` | Sedes, tecnoacademias, tecnoparques | `training_center_id`, `location_id` |
| `catalog` | Catálogos (ej. Modalidades) | - |
| `catalog_detail` | Valores de catálogo | `catalog_id`, `state_id` |
| `state` | Estados del sistema (Activo, Inactivo, etc.) | - |
| `parameter` | Parámetros globales | `module_id`, `state_id` |

### academic_schema (Programas y Oferta)

| Tabla | Descripción | FK |
|-------|-------------|----|
| `technological_line` | Línea tecnológica | - |
| `technological_network` | Red tecnológica | `line_id` |
| `knowledge_network` | Red de conocimiento | `technological_network_id` |
| `training_program` | Programa de formación | `knowledge_network_id`, `training_type_id`, `modality_id` |
| `competency` | Competencia | `competency_type_id` |
| `learning_outcome` | Resultado de Aprendizaje (RAP) | `outcome_type_id` |
| `program_competency` | Relación programa-competencia | `program_id`, `competency_id` |
| `competency_outcome` | Relación competencia-RAP | `competency_id`, `outcome_id` |
| `training_group` | Ficha | `program_id`, `modality_id`, `shift_id` |
| `offer` | Oferta académica | `program_id`, `training_center_id` |

### scheduling_schema (Horarios y Motor)

| Tabla | Descripción | FK |
|-------|-------------|----|
| `time_slot` | Franja horaria | - |
| `schedule` | Horario asignado | `instructor_id` (lógico), `environment_id` (lógico), `training_group_id` (lógico), `time_slot_id` |
| `assignment` | Historial de asignaciones | `schedule_id` |
| `conflict` | Conflictos detectados | `schedule_id` |
| `class_session` | Sesión ejecutada | `schedule_id` |
| `observation` | Observación sobre horario | `schedule_id` |

### actors_schema (Actores)

| Tabla | Descripción | FK |
|-------|-------------|----|
| `instructor` | Instructor (planta/contratista) | - |
| `learner` | Aprendiz | `training_group_id` |
| `manager` | Directivo | `training_center_id` |
| `company` | Empresa | - |
| `productive_stage` | Etapa productiva | `learner_id`, `company_id` |

### iam_schema (Seguridad)

| Tabla | Descripción | FK |
|-------|-------------|----|
| `user` | Usuario del sistema | - |
| `role` | Rol | - |
| `permission` | Permiso | - |
| `user_role` | Relación usuario-rol | `user_id`, `role_id` |
| `role_permission` | Relación rol-permiso | `role_id`, `permission_id` |
| `session` | Sesión de usuario | `user_id` |
| `token` | JWT almacenado | `user_id` |

### audit_schema (Auditoría)

| Tabla | Descripción | FK |
|-------|-------------|----|
| `audit_log` | Registro inmutable de acciones | `user_id` (lógico) |

---

## Modelo Físico (PostgreSQL)

### Convenciones de nomenclatura

- **Tablas:** `snake_case`, singular (ej. `schedule`, `instructor`).
- **Columnas:** `snake_case` (ej. `start_time`, `instructor_id`).
- **Claves primarias:** `id` (UUID) con `DEFAULT gen_random_uuid()`.
- **Claves foráneas:** `<tabla>_id` (ej. `instructor_id`).
- **Auditoría:** `created_at` y `updated_at` con `DEFAULT CURRENT_TIMESTAMP`.
- **Soft-delete:** `is_active` (BOOLEAN).

### Tipos de datos comunes

| Tipo SQL | Uso |
|----------|-----|
| `UUID` | Claves primarias y foráneas. |
| `VARCHAR(n)` | Texto corto (nombres, códigos, emails). |
| `TEXT` | Texto largo (descripciones, observaciones). |
| `INTEGER` | Números enteros (capacidad, conteos, horas). |
| `NUMERIC(10,2)` | Decimales exactos (costos, porcentajes). |
| `BOOLEAN` | Indicadores binarios (activo, cancelado). |
| `DATE` | Fechas (sin hora). |
| `TIMESTAMP` | Fechas con hora. |
| `TIME` | Hora (sin fecha). |
| `JSONB` | Datos semiestructurados (para auditoría y configuraciones). |

### Ejemplo de estructura de tabla (PostgreSQL)

```sql
CREATE TABLE schedule (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instructor_id UUID NOT NULL,
    environment_id UUID NOT NULL,
    training_group_id UUID NOT NULL,
    time_slot_id UUID NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_schedule_instructor_date ON schedule(instructor_id, date);
CREATE INDEX idx_schedule_environment_date ON schedule(environment_id, date);
CREATE INDEX idx_schedule_group_date ON schedule(training_group_id, date);