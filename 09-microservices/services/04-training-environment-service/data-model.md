# Modelo de datos — training-environment-service

> Estado: 🟢 Estable | Última actualización: 2026-10-26
> Naming: entidades y atributos en inglés (HALT-DB-NAMING)

## Convenciones de modelado (transversales)

> **Estándar autoritativo:** [06-data/modeling-conventions.md](../../../06-data/modeling-conventions.md) (ratificado en ADR-004). Resumen aplicable:

- **Tres conceptos de estado (no confundir):** (1) *ciclo de vida del registro* (técnico) → `is_active` + soft delete (`deleted_at`); (2) *estado de negocio* (parametrizable) → FK `status_id` → catálogo `status`; (3) *enum técnico cerrado* (CC/CE, EMAIL/IN_APP…) → `VARCHAR` + `CHECK (... IN (...))`. **No se usa el tipo `ENUM` nativo de Postgres** (su `ALTER TYPE` bloquea migraciones independientes por servicio).
- **Estados de negocio parametrizables:** el servicio implementa `status_category` + `status` (+ `status_transition` si aplica) en su propia BD; los agregados con máquina de estados referencian `status_id`. Solo migran estados de **negocio**; los enums técnicos cerrados (`*_type`, `channel`…) permanecen como `VARCHAR + CHECK`.
- **Auditoría (tablas transaccionales):** `created_at`/`created_by`, `updated_at`/`updated_by`, `deleted_at`/`deleted_by` (soft delete), `is_active` y `row_version`. Acciones del sistema usan `SYSTEM_ACTOR_ID = 00000000-0000-0000-0000-000000000000`. Catálogos: `created_*`/`updated_*` + `is_active` (sin soft delete). Append-only: solo el timestamp de inserción.
- **Acciones referenciales:** cada FK declara `ON UPDATE`/`ON DELETE`. Por defecto: catálogo/padre → `RESTRICT`; hijo de agregado (composición) → `CASCADE`; FK opcional → `SET NULL`.
- **Nomenclatura de constraints:** `pk_<tabla>`, `uq_<tabla>_<cols>`, `fk_<tabla>_<ref>`, `ck_<tabla>_<regla>`, `ix_<tabla>_<cols>`.

## Entidades propias

### `environment_type`

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `code` | VARCHAR(20) | No | Único (ej: `CLASSROOM`, `LAB`, `WORKSHOP`) |
| `name` | VARCHAR(100) | No | Aula, Laboratorio, Taller, etc. |
| `description` | TEXT | Sí | |
| `created_at` | TIMESTAMPTZ | No | |

### `environment`

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `environment_type_id` | UUID | No | FK → environment_type |
| `training_center_id` | UUID | No | Referencia externa → reference-data-service |
| `name` | VARCHAR(100) | No | Nombre del ambiente (ej: `Aula 201`) |
| `capacity` | INT | No | Número máximo de personas |
| `location` | VARCHAR(200) | Sí | Descripción de ubicación dentro del centro |
| `is_active` | BOOLEAN | No | false = ambiente fuera de servicio |
| `created_at` | TIMESTAMPTZ | No | |
| `updated_at` | TIMESTAMPTZ | No | |

```sql
CHECK (capacity > 0)
```

### `availability_rule`

Regla recurrente de disponibilidad (hasta 24 por ambiente según dominio).

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `environment_id` | UUID | No | FK → environment |
| `day_of_week` | SMALLINT | No | 1=Lunes … 7=Domingo |
| `start_time` | TIME | No | Inicio de disponibilidad |
| `end_time` | TIME | No | Fin de disponibilidad |
| `effective_from` | DATE | No | Fecha desde la que aplica la regla |
| `effective_until` | DATE | Sí | Null = vigencia indefinida |
| `created_at` | TIMESTAMPTZ | No | |

```sql
CHECK (end_time > start_time)
CHECK (day_of_week BETWEEN 1 AND 7)
```

### `maintenance`

Período de mantenimiento programado; bloquea el ambiente para reservas.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `environment_id` | UUID | No | FK → environment |
| `start_date` | DATE | No | |
| `end_date` | DATE | No | |
| `description` | TEXT | No | Motivo del mantenimiento |
| `created_by` | UUID | No | ID de usuario (iam-service) |
| `created_at` | TIMESTAMPTZ | No | |

```sql
CHECK (end_date > start_date)
```

### `reservation`

Reserva puntual de un ambiente fuera del horario de clase asignado.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `environment_id` | UUID | No | FK → environment |
| `reservation_date` | DATE | No | |
| `start_time` | TIME | No | |
| `end_time` | TIME | No | |
| `reason` | TEXT | Sí | |
| `requester_id` | UUID | No | ID del usuario (iam-service) |
| `status` | VARCHAR(20) NOT NULL DEFAULT 'PENDING' | No | PENDING / CONFIRMED / CANCELLED |
| `created_at` | TIMESTAMPTZ | No | |
| `updated_at` | TIMESTAMPTZ | No | |

```sql
CHECK (status IN ('PENDING','CONFIRMED','CANCELLED'))
```

### Prevención de solapamientos (exclusion constraints)

Para garantizar a nivel de base de datos que un ambiente no se reserve dos veces en franjas horarias que se cruzan, se usa una `EXCLUDE` constraint GiST sobre `reservation`. Esta constraint impide a nivel de motor que dos reservas no canceladas del mismo `environment_id` tengan rangos de tiempo solapados:

```sql
ALTER TABLE reservation ADD CONSTRAINT ex_reservation_overlap
  EXCLUDE USING gist (
    environment_id WITH =,
    tsrange( (reservation_date + start_time), (reservation_date + end_time) ) WITH &&
  ) WHERE (status <> 'CANCELLED');
```

Requiere la extensión `btree_gist` (necesaria para combinar el operador de igualdad `=` sobre `environment_id` con el operador de solapamiento `&&` sobre el rango temporal dentro del mismo índice GiST).

Esta protección a nivel de BD **complementa, no reemplaza**, la validación de conflictos del scheduling-service: el scheduling-service ofrece la validación temprana y la experiencia de usuario, mientras que la `EXCLUDE` constraint actúa como última línea de defensa frente a condiciones de carrera o escrituras concurrentes.

### `item_type`

Catálogo técnico de tipos de elementos inventariables, creado por HU-005 junto con el dominio de inventario aprobado en ADR-001.

| Campo | Tipo | Nullable | Descripción |
|---|---|---|---|
| `id` | UUID | No | PK; se genera con `gen_random_uuid()` |
| `name` | VARCHAR(100) | No | Nombre único del tipo |
| `category` | VARCHAR(50) | Sí | Categoría opcional |
| `created_at` | TIMESTAMPTZ | No | Alta del catálogo |

`name` tiene restricción `UNIQUE`.

### `inventory_item`

Unidad física inventariada por ambiente, identificada de forma única por su placa o serial (`asset_tag`).

| Campo | Tipo | Nullable | Descripción |
|---|---|---|---|
| `id` | UUID | No | PK; se genera con `gen_random_uuid()` |
| `environment_id` | UUID | No | FK interna a `environment.id` |
| `item_type_id` | UUID | No | FK interna a `item_type.id` |
| `asset_tag` | VARCHAR(50) | No | Placa/serial único |
| `status` | VARCHAR(20) | No | Default `AVAILABLE`; valores `AVAILABLE`, `DAMAGED`, `LOST`, `IN_MAINTENANCE` |
| `acquired_at` | DATE | Sí | Fecha de adquisición |
| `created_at` | TIMESTAMPTZ | No | Alta del registro |

`asset_tag` es único; `status` está limitado por `chk_inventory_item_status`. Las FK internas se llaman `fk_inventory_item_environment` y `fk_inventory_item_item_type`; los índices `ix_inventory_item_environment_id` y `ix_inventory_item_item_type_id` permiten filtrar por ambiente y tipo.

## Referencias externas

| Campo | Referencia lógica | Servicio propietario |
|-------|-------------------|----------------------|
| `training_center_id` | `training_center.id` | `reference-data-service` |
| `requester_id` | `user.id` | `iam-service` |
| `created_by` | `user.id` | `iam-service` |

## Índices relevantes

| Tabla | Campos | Tipo | Motivo |
|-------|--------|------|--------|
| `availability_rule` | `(environment_id, day_of_week)` | B-Tree | Consulta de disponibilidad por scheduling (< 300 ms) |
| `maintenance` | `(environment_id, start_date, end_date)` | B-Tree | Overlap con franjas solicitadas |
| `reservation` | `(environment_id, reservation_date)` | B-Tree | Overlap con nuevas reservas |
| `reservation` | `(requester_id, created_at)` | B-Tree | historial por usuario |

## Remediación de congruencia — R3 (2026-08-06)

Cierre de brechas contrato↔BD detectadas en la evaluación de congruencia
(`CONGRUENCIA-contratos-docs-bd.md`, en `delivery/status/` — bitácora fuera del repo de docs).
Se implementa vía **changeset nuevo** `remediation-training-960` (no se modifica ningún
changeset corrido). Columnas agregadas (todas nullable o con default → seguras sobre datos existentes):

| Tabla | Columna nueva | Tipo | Justificación |
|-------|---------------|------|---------------|
| `environment_type` | `code` | `VARCHAR(30)` UNIQUE (nullable) | Identificador semántico del catálogo (LAB, CLASSROOM…) que el contrato usa; faltaba en el DDL. |
| `environment` | `is_active` | `BOOLEAN NOT NULL DEFAULT true` | Estado operativo (ciclo de vida técnico). |
| `environment` | `updated_at` | `TIMESTAMPTZ NOT NULL DEFAULT now()` | Auditoría de actualización. |
| `availability_rule` | `effective_from` / `effective_until` | `DATE` (nullable) | Vigencia de la regla de disponibilidad. |
| `reservation` | `reason` | `VARCHAR(255)` (nullable) | Motivo de la reserva (expuesto por el contrato). |
| `reservation` | `updated_at` | `TIMESTAMPTZ NOT NULL DEFAULT now()` | Auditoría de actualización. |

**Reconciliación de naming (fix de contrato, sin cambio de BD):** la columna real de
`maintenance` es **`reason`** (nullable); el contrato decía `description` (NOT NULL) → se
corrigió el contrato a `reason`.
