
### 📄 Archivo 2: `09-microservices/_template/data-model.md`

```markdown
# Data Model - [Nombre del Servicio]

> Estado: 🔴 Pendiente | Última actualización: YYYY-MM-DD
> Autor: [Nombre Apellido] | Equipo: [nombre del equipo]

## Contexto

Este documento define el modelo de datos transaccional del servicio **[Nombre del Servicio]** . Describe las entidades, atributos, relaciones y restricciones que se almacenan en su propia base de datos.

## Esquema
[servicio]_schema

text

## Entidades

### 1. [Entidad 1]

**Descripción:** Breve descripción de la entidad.

**Atributos:**

| Atributo | Tipo | Descripción | Restricciones |
|----------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `field1` | VARCHAR(100) | Descripción del campo | NOT NULL |
| `field2` | INTEGER | Descripción del campo | CHECK(field2 > 0) |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |
| `created_at` | TIMESTAMP | Fecha de creación | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP | Fecha de actualización | DEFAULT CURRENT_TIMESTAMP |

**Relaciones:**

| Relación | Tipo | Descripción |
|----------|------|-------------|
| `Entity2` | 1:N | Un [Entidad 1] tiene muchos [Entidad 2]. |
| `Entity3` | N:1 | Muchos [Entidad 1] pertenecen a un [Entidad 3]. |

**Índices:**

| Índice | Campos | Propósito |
|--------|--------|-----------|
| `idx_[entidad]_field1` | `field1` | Búsquedas por field1. |
| `idx_[entidad]_field2_field3` | `field2`, `field3` | Consultas frecuentes con ambos campos. |

---

### 2. [Entidad 2]

**Descripción:** Breve descripción de la entidad.

**Atributos:**

| Atributo | Tipo | Descripción | Restricciones |
|----------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `entity1_id` | UUID | Referencia a [Entidad 1] | FK([Entidad 1].id) |
| `field1` | TEXT | Descripción del campo | NOT NULL |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |
| `created_at` | TIMESTAMP | Fecha de creación | DEFAULT CURRENT_TIMESTAMP |

**Relaciones:**

| Relación | Tipo | Descripción |
|----------|------|-------------|
| `Entity1` | N:1 | Muchos [Entidad 2] pertenecen a un [Entidad 1]. |

**Índices:**

| Índice | Campos | Propósito |
|--------|--------|-----------|
| `idx_[entidad]_entity1_id` | `entity1_id` | Búsquedas por entidad padre. |

---

### 3. [Entidad 3]

**Descripción:** Breve descripción de la entidad.

**Atributos:**

| Atributo | Tipo | Descripción | Restricciones |
|----------|------|-------------|---------------|
| `id` | UUID | Identificador único | PK, DEFAULT gen_random_uuid() |
| `field1` | VARCHAR(50) | Descripción del campo | NOT NULL, UNIQUE |
| `field2` | DATE | Descripción del campo | NOT NULL |
| `status` | VARCHAR(20) | Estado del registro | CHECK(status IN ('ACTIVE', 'INACTIVE', 'PENDING')) |
| `is_active` | BOOLEAN | Activo/Inactivo | DEFAULT TRUE |
| `created_at` | TIMESTAMP | Fecha de creación | DEFAULT CURRENT_TIMESTAMP |

**Relaciones:**

| Relación | Tipo | Descripción |
|----------|------|-------------|
| `Entity1` | 1:N | Un [Entidad 3] tiene muchos [Entidad 1]. |

**Índices:**

| Índice | Campos | Propósito |
|--------|--------|-----------|
| `idx_[entidad]_field1` | `field1` | Búsquedas por field1. |

---

## Diagrama de entidades (textual)

```text
┌─────────────────┐          ┌─────────────────┐
│   [Entidad 1]   │ 1      N │   [Entidad 2]   │
│                 │──────────│                 │
│ - id (PK)       │          │ - id (PK)       │
│ - field1        │          │ - entity1_id    │
│ - field2        │          │ - field1        │
└─────────────────┘          └─────────────────┘
        │
        │ N
        │
        ▼
┌─────────────────┐          ┌─────────────────┐
│   [Entidad 3]   │ 1      N │   [Entidad 1]   │
│                 │──────────│                 │
│ - id (PK)       │          │ - id (PK)       │
│ - field1        │          │ - field1        │
│ - field2        │          │ - entity3_id    │
└─────────────────┘          └─────────────────┘
Restricciones de integridad
Restricción	Descripción
field2 > 0	El campo field2 debe ser positivo.
status IN ('ACTIVE', 'INACTIVE', 'PENDING')	Status debe ser uno de los valores permitidos.
UNIQUE(field1)	El campo field1 debe ser único.