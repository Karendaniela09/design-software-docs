# Modelo de datos — iam-service

> Estado: 🟢 Estable | Última actualización: 2026-10-24 (HU-IAM-019: seeds sintéticos, sin cambio de schema)
> Naming: entidades y atributos en inglés (HALT-DB-NAMING)
> Ver diseño RBAC completo en [rbac-design.md](./rbac-design.md)

## Convenciones de modelado (transversales)

> **Estándar autoritativo:** [06-data/modeling-conventions.md](../../../06-data/modeling-conventions.md) (ratificado en ADR-004). Resumen aplicable:

- **Tres conceptos de estado (no confundir):** (1) *ciclo de vida del registro* (técnico) → `is_active` + soft delete (`deleted_at`); (2) *estado de negocio* (parametrizable) → FK `status_id` → catálogo `status`; (3) *enum técnico cerrado* (CC/CE, EMAIL/IN_APP…) → `VARCHAR` + `CHECK (... IN (...))`. **No se usa el tipo `ENUM` nativo de Postgres** (su `ALTER TYPE` bloquea migraciones independientes por servicio).
- **Estados de negocio parametrizables:** el servicio implementa `status_category` + `status` (+ `status_transition` si aplica) en su propia BD; los agregados con máquina de estados referencian `status_id`. Solo migran estados de **negocio**; los enums técnicos cerrados (`*_type`, `channel`…) permanecen como `VARCHAR + CHECK`.
- **Auditoría (tablas transaccionales):** `created_at`/`created_by`, `updated_at`/`updated_by`, `deleted_at`/`deleted_by` (soft delete), `is_active` y `row_version`. Acciones del sistema usan `SYSTEM_ACTOR_ID = 00000000-0000-0000-0000-000000000000`. Catálogos: `created_*`/`updated_*` + `is_active` (sin soft delete). Append-only: solo el timestamp de inserción.
- **Acciones referenciales:** cada FK declara `ON UPDATE`/`ON DELETE`. Por defecto: catálogo/padre → `RESTRICT`; hijo de agregado (composición) → `CASCADE`; FK opcional → `SET NULL`.
- **Nomenclatura de constraints:** `pk_<tabla>`, `uq_<tabla>_<cols>`, `fk_<tabla>_<ref>`, `ck_<tabla>_<regla>`, `ix_<tabla>_<cols>`.

## Entidades propias

---

### `user`

Cuenta de acceso al sistema. Cualquier persona que interactúa con la plataforma.

| Campo | Tipo | Nullable | PII | Descripción |
|-------|------|----------|-----|-------------|
| `id` | UUID | No | — | PK |
| `email` | VARCHAR(255) | No | ✓ | Único; usado como login |
| `password_hash` | TEXT | No | — | Bcrypt hash, cost factor 12 |
| `first_name` | VARCHAR(100) | No | ✓ | Nombre(s) del usuario |
| `last_name` | VARCHAR(100) | No | ✓ | Apellido(s) del usuario |
| `actor_type` | VARCHAR(20) | No | — | Determina el actor_id en el JWT. CHECK IN (`USER`, `INSTRUCTOR`, `LEARNER`) |
| `actor_id` | UUID | Sí | — | FK lógica al actor en actors-service (null para ADMIN) |
| `is_active` | BOOLEAN | No | — | false = cuenta deshabilitada |
| `last_login_at` | TIMESTAMPTZ | Sí | — | Última autenticación exitosa |
| `failed_attempts` | SMALLINT | No | — | Contador de intentos fallidos; se resetea en login exitoso |
| `locked_until` | TIMESTAMPTZ | Sí | — | null = cuenta no bloqueada |
| `must_change_password` | BOOLEAN | No | — | true = debe cambiar la contraseña en el próximo login (RN-IAM-05) |
| `password_temporary_expires_at` | TIMESTAMPTZ | Sí | — | Expiración de la contraseña temporal (72 h); null = no es temporal |
| `created_at` | TIMESTAMPTZ | No | — | |
| `updated_at` | TIMESTAMPTZ | No | — | |

**Retención PII**: Datos del `user` → 5 años después de desactivación (normativa SENA).
**Regla**: max 5 intentos fallidos → bloqueo 15 min. Max 10 intentos → bloqueo 24 h.

> **Nota de diseño — referencia polimórfica**: `actor_type` + `actor_id` forman una referencia polimórfica hacia el servicio de actores. No se puede aplicar FK a nivel de base de datos porque el actor reside en otro servicio (actors-service). Esta es una decisión de diseño explícita y aceptada en la arquitectura de microservicios; no constituye una violación de normalización sino una restricción de integridad referencial que se delega al dominio de aplicación.

---

### `module`

Grupo funcional de alto nivel del sistema. Corresponde a secciones de la UI (navegación principal).

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `code` | VARCHAR(30) | No | UNIQUE; ej: `MOD_SCHEDULING`, `MOD_MONITORING` |
| `name` | VARCHAR(100) | No | Nombre visible en UI |
| `description` | TEXT | Sí | |
| `display_order` | SMALLINT | No | Orden en el menú lateral |
| `icon_key` | VARCHAR(50) | Sí | Clave del ícono para la UI |
| `is_active` | BOOLEAN | No | DEFAULT true |
| `created_at` | TIMESTAMPTZ | No | |
| `updated_at` | TIMESTAMPTZ | No | |

**Dato de referencia**: los módulos son definidos en el deploy inicial y no cambian en runtime.

---

### `feature`

Capacidad específica dentro de un módulo. Es la unidad de permiso del sistema.
Un `feature` representa una acción o conjunto de acciones sobre una vista o recurso.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `module_id` | UUID | No | FK → module |
| `code` | VARCHAR(60) | No | UNIQUE; ej: `SCH_CREATE`, `MON_ALERT_RESOLVE` |
| `name` | VARCHAR(120) | No | Nombre descriptivo |
| `description` | TEXT | Sí | Para qué sirve este feature |
| `action_level` | VARCHAR(20) | No | Tipo de acción. CHECK IN (`READ`, `WRITE`, `DELETE`, `PUBLISH`, `APPROVE`) |
| `is_active` | BOOLEAN | No | DEFAULT true |
| `created_at` | TIMESTAMPTZ | No | |
| `updated_at` | TIMESTAMPTZ | No | |

**~50 features pre-cargados** — ver catálogo completo en [rbac-design.md](./rbac-design.md).

---

### `role`

Conjunto de features y scopes asignables a usuarios.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `name` | VARCHAR(50) | No | UNIQUE; ej: `COORDINATOR`, `INSTRUCTOR` |
| `display_name` | VARCHAR(100) | No | Nombre en UI (ej: `Coordinador Académico`) |
| `description` | TEXT | Sí | |
| `is_system_role` | BOOLEAN | No | true = no puede eliminarse |
| `created_at` | TIMESTAMPTZ | No | |

**7 roles pre-cargados**: SYSTEM_ADMIN, CENTER_DIRECTOR, COORDINATOR, AREA_LEADER, INSTRUCTOR, LEARNER, ADMIN_STAFF.

---

### `role_feature`

Asignación de un feature a un rol, con su scope de acceso.
Reemplaza la tabla `permission` y la tabla `role_permission` del modelo plano anterior.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `role_id` | UUID | No | FK → role |
| `feature_id` | UUID | No | FK → feature |
| `scope_type` | VARCHAR(30) | No | Alcance de datos. CHECK IN (`GLOBAL`, `TRAINING_CENTER`, `AREA`, `OWN_FICHAS`, `OWN_SCHEDULE`, `OWN_PROFILE`, `OWN_FICHA_AS_LEARNER`) |

**Constraint UNIQUE**: `(role_id, feature_id)` — un rol tiene un scope por feature.
**~120 registros** al iniciar, según la matriz en [rbac-design.md](./rbac-design.md).

---

### `user_role`

Asignación de rol a usuario, opcionalmente restringida a un centro de formación.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `user_id` | UUID | No | FK → user |
| `role_id` | UUID | No | FK → role |
| `training_center_id` | UUID | Sí | null = rol global; UUID = rol restringido al centro |
| `assigned_by` | UUID | No | FK → user (quien hizo la asignación) |
| `assigned_at` | TIMESTAMPTZ | No | |
| `expires_at` | TIMESTAMPTZ | Sí | null = asignación permanente |

**Constraint UNIQUE**: `(user_id, role_id, training_center_id)`.

---

### `user_scope_override`

Override explícito de acceso para un usuario específico. Permite conceder o revocar features
individualmente sin cambiar el rol. Se usa para casos excepcionales y temporales.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `user_id` | UUID | No | FK → user |
| `feature_id` | UUID | No | FK → feature |
| `scope_type` | VARCHAR(30) | No | Alcance del override. CHECK IN (`GLOBAL`, `TRAINING_CENTER`, `AREA`, `OWN_FICHAS`, `OWN_SCHEDULE`, `OWN_PROFILE`, `OWN_FICHA_AS_LEARNER`) |
| `is_allowed` | BOOLEAN | No | true = acceso adicional; false = bloqueo explícito |
| `reason` | TEXT | No | Justificación del override |
| `granted_by` | UUID | No | FK → user (quien otorgó) |
| `expires_at` | TIMESTAMPTZ | Sí | null = sin expiración |
| `created_at` | TIMESTAMPTZ | No | |

---

### `refresh_token`

Token de renovación del access JWT. Un usuario puede tener múltiples sesiones activas
(ej: browser + móvil simultáneamente).

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `user_id` | UUID | No | FK → user |
| `token_hash` | TEXT | No | Hash SHA-256 del refresh token |
| `device_hint` | VARCHAR(200) | Sí | User-agent resumido; para mostrar sesiones activas |
| `ip_address` | VARCHAR(45) | Sí | PII; IP de origen |
| `expires_at` | TIMESTAMPTZ | No | DEFAULT: now() + 7 días |
| `is_revoked` | BOOLEAN | No | DEFAULT false |
| `revoked_at` | TIMESTAMPTZ | Sí | |
| `created_at` | TIMESTAMPTZ | No | |

**Retención**: `refresh_token` → eliminar registros con `expires_at < NOW() - 30 días`.

---

### `password_reset_request`

Solicitud de recuperación de contraseña.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `user_id` | UUID | No | FK → user |
| `token_hash` | TEXT | No | Hash del token enviado al email |
| `expires_at` | TIMESTAMPTZ | No | DEFAULT: now() + 1 hora |
| `is_used` | BOOLEAN | No | DEFAULT false |
| `requested_at` | TIMESTAMPTZ | No | |
| `ip_address` | VARCHAR(45) | Sí | PII |

**Regla**: máximo 3 solicitudes activas por usuario cada 24 h (anti-spam).

---

### `audit_login`

Log de intentos de autenticación. Separado del audit-service porque IAM no publica eventos
de sus propias fallas de autenticación (evitar bucle o exposición de credenciales).

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `user_id` | UUID | Sí | null si el email no existe |
| `email_attempted` | VARCHAR(255) | No | PII |
| `outcome` | VARCHAR(20) | No | CHECK IN (`SUCCESS`, `INVALID_PASSWORD`, `USER_NOT_FOUND`, `ACCOUNT_LOCKED`, `TOKEN_EXPIRED`) |
| `ip_address` | VARCHAR(45) | Sí | PII |
| `user_agent` | TEXT | Sí | |
| `attempted_at` | TIMESTAMPTZ | No | |

**Retención**: 90 días.
**Particionamiento/retención**: Retención 90 días. Se recomienda particionar por `attempted_at` (RANGE mensual) y purgar particiones > 90 días.
**Regla**: Solo INSERT — igual que AuditRecord.

---

### `outbox`

Bandeja transaccional de eventos de dominio (patrón Outbox). Cada acción que emite un evento (`iam.user.created`, `iam.user.deactivated`, `iam.role.assigned`, `iam.session.started`) inserta aquí **en la misma transacción**; un relay los publica luego en el topic `iam-events`.

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| `id` | UUID | No | PK |
| `event_id` | UUID | No | UNIQUE — idempotencia de publicación |
| `event_type` | TEXT | No | ej: `iam.user.created` |
| `payload` | JSONB | No | Envelope del evento (shared-contracts) |
| `created_at` | TIMESTAMPTZ | No | |
| `published_at` | TIMESTAMPTZ | Sí | null = pendiente de publicar |

**Introducido por:** changeset `iam-outbox-table-001` (iam-db, prerequisito F3). **Regla:** append + update de `published_at`; el relay marca publicado (at-least-once).

---

## Índices relevantes

| Tabla | Campos indexados | Tipo | Motivo |
|-------|-----------------|------|--------|
| `user` | `email` | UNIQUE | Login |
| `user` | `actor_id` | B-Tree | Lookup del usuario dado un actor_id |
| `user` | `is_active` | Partial | Filtrar solo cuentas activas |
| `user` | `(last_name, first_name)` | B-Tree | Búsqueda por nombre |
| `module` | `code` | UNIQUE | Lookup por código de módulo |
| `feature` | `code` | UNIQUE | Lookup por código de feature |
| `role_feature` | `(role_id, feature_id)` | UNIQUE | Evita duplicados |
| `role_feature` | `feature_id` | B-Tree | Roles que tienen un feature dado |
| `user_role` | `(user_id, role_id, training_center_id)` | UNIQUE | Evita asignaciones duplicadas |
| `user_role` | `user_id` | B-Tree | Roles de un usuario (para construir JWT) |
| `user_scope_override` | `(user_id, feature_id)` | B-Tree | Overrides del usuario |
| `refresh_token` | `token_hash` | UNIQUE | Validación del refresh token |
| `refresh_token` | `(user_id, is_revoked)` | B-Tree | Sesiones activas por usuario |
| `audit_login` | `(email_attempted, attempted_at)` | B-Tree | Rate limiting y detección de ataques |
| `outbox` | `created_at WHERE published_at IS NULL` | Partial | Eventos pendientes para el relay (`ix_outbox_unpublished`) |

---

## Datos pre-cargados (seeds)

Al inicializar el sistema se insertan:

| Tabla | Registros iniciales |
|-------|-------------------|
| `module` | 10 módulos (ver [rbac-design.md](./rbac-design.md)) |
| `feature` | ~50 features (ver catálogo en [rbac-design.md](./rbac-design.md)) |
| `role` | 7 roles base |
| `role_feature` | ~120 asignaciones (ver matriz en [rbac-design.md](./rbac-design.md)) |
| `user` | 1 usuario SYSTEM_ADMIN con `first_name` y `last_name` por variable de entorno |
| `user_role` | 1 asignación SYSTEM_ADMIN → GLOBAL |

> El hash de `admin@sena.edu.co` (seed `seed-demo-iam-001`) es ficticio: con ese usuario no se puede iniciar sesión.

### Usuarios sintéticos (solo `develop` y `qa`, HU-IAM-019)

El changeset `hu-iam-019-seed-synthetic-users-002` (`02_dml/04_patches`, `context: "dev,qa"`, rollback espejo) inserta **7 usuarios en `user` y 7 asignaciones en `user_role`**, uno por cada rol de `role`, con nombres ficticios, correo `synthetic.<rol>@example.test`, `actor_type` según el rol (`USER`, `INSTRUCTOR` o `LEARNER`), ID fijo `5e000000-0000-4000-8000-0000000000NN` y `password_hash = '!unprovisioned-synthetic-user'` (no es BCrypt: nadie puede entrar hasta que el despliegue provea las contraseñas). **No cambia el schema.** La lista completa, la selección por context y el procedimiento de provisión de contraseñas están en [10-devops/environments.md](../../../10-devops/environments.md#datos-sintéticos-develop-y-qa); el procedimiento operativo, en el [runbook](./runbook.md#provisionar-las-contraseñas-de-los-usuarios-sintéticos-develop-y-qa).
