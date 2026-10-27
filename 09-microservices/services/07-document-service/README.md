# document-service

> Estado: implementacion parcial documentada; ultima revision contra el codigo: 2026-10-26.
> El estado de las historias en GitHub Project #3 no se pudo verificar desde este entorno.
> Equipo: Arquitectura.

| Campo | Valor |
|---|---|
| Modulo | Transversal |
| App repo | `design-software-document-service` |
| DB repo | `design-software-document-db` |
| Stack | Python / FastAPI |
| Deployables observados | `document-api`, `template-api`, `pdf-renderer-worker`, `document-lifecycle-worker`, `outbox-dispatcher` y el comando de reproceso de DLQ |
| Evidencia de operacion | Los detalles de rutas, variables y estados implementados estan en las fichas por componente enlazadas abajo. |

## Responsabilidad

Gestiona documentos, versiones y plantillas; genera archivos en object storage y entrega eventos de dominio. La base de datos conserva metadatos y claves de almacenamiento, no el contenido del archivo.

## Persistencia

- Esquema: `document`.
- Tablas principales: `document`, `document_template`, `document_template_variable`, `document_template_version` y `document_version`.
- La evidencia del modelo fisico esta en [data-model.md](./data-model.md).

## API y componentes

| Componente | Evidencia y alcance |
|---|---|
| `document-api` | [Contrato narrativo](./components/document-api/contract.md). El codigo implementa generacion asincrona, consulta/listado, historial de versiones y URL firmada. |
| `template-api` | [README del componente](./components/template-api/README.md), con las operaciones y variables de entorno observadas. |
| `pdf-renderer-worker` | [README operativo](./components/pdf-renderer-worker/README.md), con renderizado, reintentos y entrega de eventos. |
| Outbox, inbox y reproceso | [Eventos](./events.md) y [runbook](./runbook.md). La actualizacion de estas instrucciones operativas sigue en Docs PR #437. |

El contrato OpenAPI publicado esta en [document.yaml](../../../07-api/contracts/openapi/document.yaml). El contrato narrativo distingue las rutas implementadas de las operaciones documentadas que siguen sin implementacion; las seis operaciones pendientes no se dan por cerradas sin decision de dominio.

## Salud y configuracion

El despliegue expone sondas de salud en las APIs. La matriz de rutas y las variables se documentan por componente y en [docker-infra](https://github.com/code-sena/design-software-docker-infra/blob/develop/docker-compose.yml); ya no se considera que el servicio carezca de configuracion por el hecho de que el README anterior no la inventariara.

## Trazabilidad

Las HUs de Document y sus referencias a RF se registran en [traceability-matrix.md](../../../04-requirements/traceability-matrix.md). El mapeo documental se pudo actualizar con el backlog; el estado Done/Dev de Project #3 queda sin certificar porque el tablero no estuvo disponible.
