<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: contrato de API OpenAPI 3.1
fase: diseño api-first
estado: accepted
dependencias_entrada: 09-microservices/services/02-reference-data-service/data-model.md, 07-api/guidelines.md, 07-api/contracts/openapi/_shared.yaml, 01-iam-service/rbac-design.md (features MOD_REFERENCE)
consumidores_siguientes: backend reference-data-service, frontend, academic-management-service, training-environment-service, actors-service, pruebas de contrato
tldr: Jerarquía institucional (macroregion…institutional_unit), catálogos parametrizables (catalog/catalog_detail) y parámetros del sistema (EAV), con paginación por offset y reporte active-catalog. La fuente de verdad es reference-data.yaml.
decisiones_clave: OpenAPI publicable en 07-api/contracts/openapi/reference-data.yaml; catalog_detail anidado bajo /catalogs/{catalog_id}/details (no tiene sentido fuera del catálogo padre); parameters sin DELETE (tabla sin is_active/deleted_at, se actualiza vía PUT); resto de recursos con soft delete vía is_active
halts_registrados: ninguno
-->

# Contrato — reference-data-api

> Estado: 🟢 Aceptado | Última actualización: 2026-08-06
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Arquitectura

> **Fuente de verdad (normativa):** el spec OpenAPI 3.1 en
> [`07-api/contracts/openapi/reference-data.yaml`](../../../../../07-api/contracts/openapi/reference-data.yaml).
> Este documento es la **narrativa** que lo explica; ante cualquier diferencia, **manda el
> `reference-data.yaml`**. Convenciones transversales en
> [07-api/guidelines.md](../../../../../07-api/guidelines.md).

## Autenticación
Todos los endpoints requieren `Authorization: Bearer <JWT>` emitido por `iam-service`. La autorización se resuelve por **feature + scope** (RBAC), features del módulo `MOD_REFERENCE` (ver [rbac-design.md](../../../01-iam-service/rbac-design.md)).

Los seis features `REF_*` se exigen **solo con alcance `GLOBAL`** ([DEC-006](../../decisions.md)): un grant con un alcance más estrecho (por ejemplo `REF_CATALOG_VIEW:TRAINING_CENTER`) responde `403`, igual que un token sin el feature. Sin token o con un token inválido responde `401`. Si no se pueden obtener las claves de firma de IAM (JWKS), las operaciones protegidas responden `503 DEPENDENCY_UNAVAILABLE`.

## Base URL
`/api/v1`

## Endpoints (derivados del modelo real)

### Jerarquía geográfica e institucional
`macroregion` → `microregion` → `department` → `municipality` → `training_center` → `institutional_unit`. Cada nivel es un recurso plano con CRUD completo (`GET` lista paginada, `POST`, `GET /{id}`, `PUT`, `DELETE` soft vía `is_active`), filtrado por el id del padre en query (`?macroregion_id=`, `?microregion_id=`, `?department_id=`, `?municipality_id=`, `?training_center_id=`).

| Método | Path | Descripción | Feature |
|--------|------|-------------|---------|
| `GET/POST` | `/macroregions` | Listar / crear macrorregiones | `REF_HIERARCHY_VIEW` / `REF_HIERARCHY_MANAGE` |
| `GET/PUT/DELETE` | `/macroregions/{id}` | Detalle / actualizar / desactivar | `REF_HIERARCHY_VIEW` / `REF_HIERARCHY_MANAGE` |
| `GET/POST` | `/microregions` | Listar (filtro `macroregion_id`) / crear | `REF_HIERARCHY_VIEW` / `REF_HIERARCHY_MANAGE` |
| `GET/PUT/DELETE` | `/microregions/{id}` | Detalle / actualizar / desactivar | `REF_HIERARCHY_VIEW` / `REF_HIERARCHY_MANAGE` |
| `GET/POST` | `/departments` | Listar (filtro `microregion_id`) / crear | `REF_HIERARCHY_VIEW` / `REF_HIERARCHY_MANAGE` |
| `GET/PUT/DELETE` | `/departments/{id}` | Detalle / actualizar / desactivar | `REF_HIERARCHY_VIEW` / `REF_HIERARCHY_MANAGE` |
| `GET/POST` | `/municipalities` | Listar (filtro `department_id`) / crear | `REF_HIERARCHY_VIEW` / `REF_HIERARCHY_MANAGE` |
| `GET/PUT/DELETE` | `/municipalities/{id}` | Detalle / actualizar / desactivar | `REF_HIERARCHY_VIEW` / `REF_HIERARCHY_MANAGE` |
| `GET/POST` | `/training-centers` | Listar (filtro `municipality_id`, `center_code`) / crear | `REF_HIERARCHY_VIEW` / `REF_HIERARCHY_MANAGE` |
| `GET/PUT/DELETE` | `/training-centers/{id}` | Detalle / actualizar / desactivar | `REF_HIERARCHY_VIEW` / `REF_HIERARCHY_MANAGE` |
| `GET/POST` | `/institutional-units` | Listar (filtro `training_center_id`, `unit_type`) / crear | `REF_HIERARCHY_VIEW` / `REF_HIERARCHY_MANAGE` |
| `GET/PUT/DELETE` | `/institutional-units/{id}` | Detalle / actualizar / desactivar | `REF_HIERARCHY_VIEW` / `REF_HIERARCHY_MANAGE` |

### Catálogos parametrizables
`catalog_detail` se modela **anidado** bajo su `catalog` (no tiene sentido fuera de su catálogo padre, `code` es único solo dentro del catálogo — guidelines §3).

| Método | Path | Descripción | Feature |
|--------|------|-------------|---------|
| `GET/POST` | `/catalogs` | Listar (filtro `code`, `is_active`) / crear catálogo | `REF_CATALOG_VIEW` / `REF_CATALOG_MANAGE` |
| `GET/PUT/DELETE` | `/catalogs/{id}` | Detalle / actualizar / desactivar catálogo | `REF_CATALOG_VIEW` / `REF_CATALOG_MANAGE` |
| `GET/POST` | `/catalogs/{catalog_id}/details` | Valores de un catálogo / agregar valor | `REF_CATALOG_VIEW` / `REF_CATALOG_MANAGE` |
| `GET/PUT/DELETE` | `/catalogs/{catalog_id}/details/{id}` | Detalle / actualizar / desactivar valor | `REF_CATALOG_VIEW` / `REF_CATALOG_MANAGE` |

### Parámetros del sistema (EAV)
La tabla `parameter` **no tiene** `is_active`/`deleted_at` (ver data-model.md), por eso **no se expone `DELETE`**: los valores se superseden vía `PUT`, nunca se eliminan.

| Método | Path | Descripción | Feature |
|--------|------|-------------|---------|
| `GET/POST` | `/parameters` | Listar (filtro `key`, `value_type`) / crear parámetro | `REF_PARAMETER_VIEW` / `REF_PARAMETER_MANAGE` |
| `GET/PUT` | `/parameters/{id}` | Detalle / actualizar valor | `REF_PARAMETER_VIEW` / `REF_PARAMETER_MANAGE` |

## Paginación
Listados: `?page=&page_size=` (offset, guidelines §6) → respuesta envuelta `{ "data": [...], "pagination": {"page","page_size","total_items","total_pages"} }`.

## Ejemplo de respuesta
```json
{
  "id": "uuid",
  "center_code": "9201",
  "name": "Centro de Comercio y Servicios",
  "municipality_id": "uuid",
  "address": "Cra 10 # 20-30",
  "phone": null,
  "is_active": true,
  "created_at": "2026-08-01T14:00:00Z",
  "updated_at": "2026-08-01T14:00:00Z"
}
```

## Reportes (dominio propio)

### `GET /reports/active-catalog`

Inventario de **catálogos activos con sus valores activos**, sobre `catalog` + `catalog_detail`
(`WHERE is_active = true`). **Solo lectura**, paginación por **offset** (colección pequeña y
acotada, no requiere cursor). Permite precargar de una sola llamada todos los
selects/dropdowns parametrizados en vez de resolver `catalog_detail` por catálogo (evita N+1).

- **Feature requerido:** `REF_CATALOG_VIEW`.
- **Filtros:** `catalog_code` (opcional, limita a un único catálogo).
- **Inventario:** Consumidores: frontend (selects/dropdowns), `academic-management-service`,
  `training-environment-service`, `actors-service` · Frecuencia: al iniciar sesión / cacheado
  con TTL en el consumidor · Formato: JSON · Fuente: `catalog` + `catalog_detail`.

## Formato de error estándar
Aplica el **envelope estándar de la plataforma** ([guidelines §7](../../../../../07-api/guidelines.md) /
`_shared.yaml#/components/schemas/Error`):

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "El recurso solicitado no existe",
    "details": [],
    "trace_id": "uuid-v4"
  }
}
```

## Eventos publicados
Al cambiar datos maestros se publica `reference_data.<entity>.<action>` (ver [event-catalog.md](../../../../event-catalog.md)) para que los consumidores refresquen sus referencias.
