# Eventos — reference-data-service

> Estado: 🟢 Estable | Ultima actualizacion: 2026-06-20

---

## Eventos publicados

Este servicio publica eventos al topic **`reference-data-events`**.

### `reference.catalog.updated`

Se emite cada vez que se modifica un catalogo del sistema (MODALITY, SHIFT, u otro).

| Campo | Tipo | Descripcion |
|---|---|---|
| `event_type` | `string` | `"reference.catalog.updated"` |
| `catalog_id` | `uuid` | Identificador interno del catalogo |
| `catalog_code` | `string` | Codigo del catalogo (ej. `MODALITY`, `SHIFT`) |
| `changed_items` | `array` | Lista de items afectados en este cambio |
| `changed_items[].item_id` | `uuid` | Identificador del item |
| `changed_items[].code` | `string` | Codigo del item |
| `changed_items[].label` | `string` | Etiqueta legible del item |
| `changed_items[].change_type` | `enum` | `ADDED`, `UPDATED` o `DEACTIVATED` |
| `updated_by` | `uuid` | ID del usuario administrador que realizo el cambio |
| `updated_at` | `datetime` | Timestamp ISO 8601 del cambio |

**Payload de ejemplo:**

```json
{
  "event_type": "reference.catalog.updated",
  "catalog_id": "b3f1a2d4-0001-4e5f-9c8b-1a2b3c4d5e6f",
  "catalog_code": "MODALITY",
  "changed_items": [
    {
      "item_id": "c1d2e3f4-0011-4a5b-8c9d-0e1f2a3b4c5d",
      "code": "VIRTUAL",
      "label": "Virtual",
      "change_type": "ADDED"
    },
    {
      "item_id": "d4e5f6a7-0022-4b6c-9d0e-1f2a3b4c5d6e",
      "code": "PRESENCIAL",
      "label": "Presencial",
      "change_type": "UPDATED"
    }
  ],
  "updated_by": "a1b2c3d4-dead-beef-cafe-000000000001",
  "updated_at": "2026-06-20T14:32:00Z"
}
```

**Consumidores:**

| Servicio | Accion |
|---|---|
| `audit-service` | Registra el cambio en el log de auditoria |
| `scheduling-service` | Invalida cache Redis de catalogo `MODALITY` o `SHIFT` |
| `actors-service` | Invalida cache Redis de catalogo segun `catalog_code` |

---

### `reference.training_center.created`

Se emite cuando se crea un nuevo centro de formacion en la jerarquia institucional.

| Campo | Tipo | Descripcion |
|---|---|---|
| `event_type` | `string` | `"reference.training_center.created"` |
| `training_center_id` | `uuid` | Identificador interno del centro de formacion |
| `center_code` | `string` | Codigo unico del centro |
| `name` | `string` | Nombre completo del centro |
| `municipality_id` | `uuid` | Municipio al que pertenece el centro |
| `created_by` | `uuid` | ID del usuario administrador que creo el centro |
| `created_at` | `datetime` | Timestamp ISO 8601 de la creacion |

**Payload de ejemplo:**

```json
{
  "event_type": "reference.training_center.created",
  "training_center_id": "e5f6a7b8-0033-4c7d-ae1f-2a3b4c5d6e7f",
  "center_code": "CT-BOG-042",
  "name": "Centro de Formacion Regional Bogota Sur",
  "municipality_id": "f7a8b9c0-0044-4d8e-bf20-3b4c5d6e7f80",
  "created_by": "a1b2c3d4-dead-beef-cafe-000000000001",
  "created_at": "2026-06-20T09:15:00Z"
}
```

**Consumidores:**

| Servicio | Accion |
|---|---|
| `audit-service` | Registra la creacion en el log de auditoria |

---

## Eventos consumidos

`reference-data-service` **no consume eventos de otros servicios.**

Es un servicio de escritura manual (operaciones administrativas) y fuente de verdad para datos de referencia. Todos los demas servicios leen de el; el no depende de eventos externos para mantenerse actualizado.

---

## Formato de envelope

Todos los eventos publicados por este servicio siguen el envelope estandar del sistema:

```json
{
  "envelope_version": "1.0",
  "event_id": "<uuid-v4>",
  "event_type": "<tipo.del.evento>",
  "source_service": "reference-data-service",
  "source_port": 8002,
  "occurred_at": "<ISO 8601>",
  "correlation_id": "<uuid-v4 opcional>",
  "payload": { }
}
```

| Campo | Descripcion |
|---|---|
| `event_id` | UUID v4 unico por evento; usado para deduplicacion |
| `event_type` | Nombre canonico del evento (ej. `reference.catalog.updated`) |
| `source_service` | Siempre `reference-data-service` |
| `source_port` | Siempre `8002` |
| `occurred_at` | Timestamp de cuando ocurrio el hecho de negocio |
| `correlation_id` | ID de la solicitud HTTP que origino el evento (para trazabilidad) |
| `payload` | Objeto con los campos especificos del evento (descritos arriba) |

---

## Politica de reintentos

| Parametro | Valor |
|---|---|
| Topic principal | `reference-data-events` |
| Dead-letter queue | `reference-data-events.dlq` |
| Reintentos antes de DLQ | 3 |
| Backoff histórico entre reintentos | 1 s, 5 s, 30 s; no es una progresión exponencial. R1 propone 1 s, 2 s, 4 s (sección siguiente) |
| Retencion en DLQ | 7 dias |
| Alertas | Alerta Slack/PagerDuty si DLQ > 0 mensajes en ventana de 5 min |

Los mensajes que fallen los 3 reintentos se enrutan a `reference-data-events.dlq`. El equipo de plataforma es responsable de revisar y reprocesar mensajes en la DLQ. No se descartan mensajes de forma silenciosa.

---

## Nota sobre cache

Los consumidores de catalogos (`scheduling-service`, `actors-service`) deben invalidar su cache Redis al recibir `reference.catalog.updated` para evitar datos obsoletos.

La clave de cache recomendada a invalidar sigue el patron:

```
catalog:<catalog_code>
```

Ejemplo: al recibir un evento con `catalog_code = "MODALITY"`, el consumidor debe ejecutar:

```
DEL catalog:MODALITY
```

Los consumidores no deben asumir que su cache local esta actualizada si no han procesado todos los eventos pendientes en `reference-data-events`.

## R1 — consumo y recuperación de la proyección (diseño 2026-10-20)

La política anterior describe la DLQ heredada; R1 no redefine esa cola. Según [ADR-021](../../../05-architecture/decisions/records/ADR-021-reference-data-resilient-messaging.md), se conserva el envelope/contrato publicado y los tipos `reference.catalog.updated` y `reference.training_center.created`; no se añade un evento de negocio nuevo.

| Recurso | Política propuesta |
|---|---|
| Consumidor | `reference-data.projection.v1`, ACK manual y QoS 1 |
| Cola principal | quorum durable `reference-data.projection` |
| Retry | quorum `.retry.1000`, `.retry.2000`, `.retry.4000` con TTL 1/2/4 s; dead-lettering at-least-once y overflow reject-publish |
| DLQ de R1 | `reference-data.projection.dlq`, durable y sin expiración automática; exchange `reference-data.projection.dlx` |
| DLQ heredada | `reference-data-events.dlq`, se conserva para compatibilidad; su TTL no se modifica |
| Efecto | Proyección técnica de eventos, no inserción repetida del catálogo ni implementación de otros consumidores |
| Deduplicación | `(consumer_name,event_id)` más hash de tipo + JSON compactado; ID igual/contenido distinto se rechaza |
| Replay | Conservar ID/cuerpo; reset de intentos; confirmar publicación antes de ACK; límite operativo |

Se valida event_id UUID, source, version, fecha RFC3339Nano y agregado esperado. El publicador de outbox conserva la identidad/fecha persistidas. `published` solo indica entrega al broker o DLQ. Los retries agotados llegan a la DLQ después de un intento inicial y tres reintentos. Si no se puede confirmar la transferencia, se reencola.

La cola y las tablas fueron validadas sobre código original en el entorno aislado y en el CI del shell sobre los SHA documentados; la integración compartida requiere los merges pendientes. [Matriz de pruebas](../../../11-quality/reference-data-hu-ref-020-r1-validation.md).
