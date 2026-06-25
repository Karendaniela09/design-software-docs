# Datos

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Datos

## Contenido

Este directorio contiene la documentación relacionada con la persistencia de datos del proyecto **Horarios SENA**. Aquí se definen los modelos de datos (conceptual, lógico y físico), el diccionario de datos detallado y la estrategia de migración para la base de datos PostgreSQL con Flyway.

> **Diferencia con `02-domain`:** esta sección describe la implementación de persistencia (tablas, columnas, tipos, relaciones, índices, migraciones). Las entidades de negocio y sus reglas se documentan en [`02-domain/`](../02-domain/). Un mismo concepto (ej: "Horario") tendrá una definición de dominio allá y un esquema de base de datos aquí.

> **Diferencia con `09-microservices`:** aquí vive el modelo de datos **global** del sistema — diccionario conceptual compartido, estrategia de migración y analítica. El modelo **transaccional propio de cada servicio** (esquema local, tablas internas) se documenta en `09-microservices/services/<servicio>/data-model.md`. No duplicar: si un concepto es solo del servicio, va allá; si es compartido entre varios servicios, va aquí.

## Archivos

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [models.md](./models.md) | Modelos conceptual, lógico y físico de datos. | 🟢 Estable |
| [data-dictionary.md](./data-dictionary.md) | Diccionario de entidades, campos, tipos y reglas de validación. | 🟢 Estable |
| [migration-strategy.md](./migration-strategy.md) | Estrategia para cambios y migraciones de datos con Flyway. | 🟢 Estable |

## Tecnologías

| Capa | Tecnología | Versión |
|------|------------|---------|
| Motor de base de datos | PostgreSQL | 16.x |
| ORM | Spring Data JPA + Hibernate | - |
| Migraciones | Flyway | - |
| Conexión | JDBC (PostgreSQL Driver) | - |

## Principios de diseño de datos

1. **Cada microservicio tiene su propio esquema:** `iam_schema`, `reference_schema`, `academic_schema`, `scheduling_schema`, `actors_schema`, `audit_schema`.
2. **Nombres en inglés:** Todas las tablas y columnas usan nombres en inglés, singular y `snake_case`.
3. **Auditoría:** Todas las tablas tienen `created_at` y `updated_at` (excepto `audit_log` que es append-only).
4. **Soft-delete:** Las entidades críticas usan `is_active` en lugar de eliminación física.
5. **Integridad referencial:** Las claves foráneas físicas se usan dentro del mismo esquema; entre esquemas se usan IDs lógicos (sin FK).
6. **Índices:** Se crean índices para las consultas más frecuentes (ej. conflictos de horario, búsquedas por instructor/ambiente/ficha).

## Referencias

- [02-domain/entities-and-rules.md](../02-domain/entities-and-rules.md)
- [05-architecture/overview.md](../05-architecture/overview.md)
- [09-microservices/](../09-microservices/)