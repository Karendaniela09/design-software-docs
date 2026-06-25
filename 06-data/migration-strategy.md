# Estrategia de migración de datos

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Datos

## Contexto

Este documento describe la estrategia de migración de datos para el sistema **Horarios SENA**. Se utiliza **Flyway** como herramienta de migración, integrada con Spring Boot, para gestionar los cambios en el esquema de base de datos de forma controlada y versionada.

## Principios

1. **Versionado:** Cada migración tiene un número de versión incremental.
2. **Idempotencia:** Las migraciones deben poder ejecutarse múltiples veces sin causar errores.
3. **Independencia:** Las migraciones son independientes del código de la aplicación.
4. **Trazabilidad:** Cada cambio queda registrado en la tabla `flyway_schema_history`.

## Estructura de migraciones

Las migraciones se almacenan en `src/main/resources/db/migration/` dentro del backend de cada microservicio.

### Nomenclatura

| Tipo | Formato | Ejemplo |
|------|---------|---------|
| Versión | `V<version>__<description>.sql` | `V1__initial_schema.sql` |
| Reversible | `V<version>__<description>_reversible.sql` | `V2__add_column_is_active.sql` |
| Rollback | `V<version>__<description>_rollback.sql` | (Opcional, se recomienda uso de `U` para undo) |

### Ejemplo de estructura de archivos

```text
backend/src/main/resources/db/migration/
├── V1__initial_schema.sql
├── V2__add_is_active_column.sql
├── V3__create_audit_table.sql
└── V4__add_indexes.sql