# reference-data-api

> Estado: 🟡 En progreso | Última actualización: 2026-08-01
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Arquitectura

> **Diseño previsto — no implementado.** La capa de aplicación aún no está construida. Este documento es **agnóstico de lenguaje**: sirve para cualquier backend.

## Tipo de componente
`-api` — REST API sincrónica.

## Responsabilidad
Exponer la jerarquía institucional (geográfica y organizativa) y los catálogos parametrizables del sistema; es la **fuente de verdad de datos maestros** que otros servicios consumen por `id`.

## Tecnologías
| Capa | Tecnología |
|------|-----------|
| Runtime | Agnóstico — cualquier backend (a definir) |
| Framework | A definir |
| Persistencia | PostgreSQL 16 · schema `institutional_structure` |
| Autenticación | JWT emitido por `iam-service` (RBAC feature + scope) |

## Variables de entorno (genéricas)
| Variable | Descripción |
|----------|-------------|
| `SERVICE_PORT` | Puerto de escucha |
| `DB_URL` | Cadena de conexión a PostgreSQL |
| `JWT_PUBLIC_KEY` | Clave pública para verificar el token de `iam-service` |
| `LOG_LEVEL` | Nivel de logs |

## Escalado, salud y observabilidad
- **Sin estado** (stateless): escala horizontalmente por réplicas tras el gateway.
- Endpoints de salud del contrato: `GET /api/v1/health/live` (alias `GET /api/v1/health`) y `GET /api/v1/health/ready`; readiness verifica la conexión a BD.
- Logs estructurados con `request_id`; métricas RED por endpoint (ver [13-operations/observability.md](../../../../../13-operations/observability.md)).
- Datos de baja volatilidad → candidato a caché de lectura (ver [ADR/roadmap]).

## Contrato
Ver [contract.md](./contract.md) · Modelo de datos: [data-model.md](../../data-model.md)
