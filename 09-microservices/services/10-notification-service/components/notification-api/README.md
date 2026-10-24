# notification-api

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Stack: Go

## Tipo de componente

`-api` — API HTTP síncrona del `notification-service`.

## Responsabilidad

- recibir solicitudes manuales/síncronas de notificación;
- validar DTOs generados desde `shared-contracts`;
- consultar una notificación por ID;
- exponer liveness/readiness;
- delegar los casos de uso a `application`, sin lógica de infraestructura en dominio.

No calcula alertas ni accede a `monitoring_db`.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/notifications` | Solicita una notificación. |
| `GET` | `/api/v1/notifications/{id}` | Consulta una notificación. |
| `GET` | `/api/v1/health` | Liveness (como lo lista el contrato). |
| `GET` | `/api/v1/ready` | Readiness (DB) (como lo lista el contrato). |
| `GET` | `/health` | Liveness, también en la raíz: el edge enruta `/notification/health` como ruta exacta. |
| `GET` | `/ready` | Readiness (DB), también en la raíz: el edge enruta `/notification/ready` como ruta exacta. |

Las rutas de negocio solo existen bajo `/api/v1` (el `servers` del contrato; ADR-022 §3). Por el edge se
llaman como `/notification/api/v1/...`. Sin el prefijo `/api/v1` responden `404`.

## Arquitectura

```text
HTTP handler
   ↓
application/usecase
   ↓
ports
   ↓
persistence / notifier / template repository
```

## Contrato

- [contract.md](./contract.md)
- [`07-api/contracts/openapi/notification.yaml`](../../../../../07-api/contracts/openapi/notification.yaml)
