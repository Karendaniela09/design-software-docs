# Eventos — document-service

> Estado: 🟢 Estable | Última actualización: 2026-10-26

---

## Eventos publicados

Topic: `document-events`

---

### `document.document.generated`

Se publica cuando un documento ha sido generado exitosamente y su binario esta disponible en el almacenamiento de objetos.

**Payload:**

```json
{
  "document_id": "8f3c0000-0000-0000-0000-000000000001",
  "template_code": "SCHEDULE_CERTIFICATE",
  "domain": "SCHEDULE",
  "owner_entity_id": "5c1a0000-0000-0000-0000-000000000002",
  "owner_service": "scheduling-service",
  "storage_key": "SCHEDULE/2026/06/5c1a0000-0000-0000-0000-000000000002/8f3c0000-0000-0000-0000-000000000001-v1.pdf",
  "mime_type": "application/pdf",
  "size_bytes": 204800,
  "generated_by": "pdf-renderer-worker",
  "generated_at": "2026-06-20T14:32:00Z"
}
```

Se publica solo con la primera version del documento.

| Campo | Tipo | Descripcion |
|---|---|---|
| `document_id` | `string` | Identificador unico del documento generado |
| `template_code` | `string` | Codigo de la plantilla Handlebars utilizada |
| `domain` | `string` | Dominio de negocio al que pertenece el documento |
| `owner_entity_id` | `string` | ID de la entidad propietaria del documento (estudiante, grupo, etc.) |
| `owner_service` | `string` | Servicio que solicito la generacion |
| `storage_key` | `string` | Ruta del binario en MinIO/S3 |
| `mime_type` | `string` | Tipo MIME del documento generado |
| `size_bytes` | `integer` | Tamano del archivo en bytes |
| `generated_by` | `string` | Componente que ejecuto la generacion |
| `generated_at` | `string (ISO 8601)` | Marca de tiempo de finalizacion de la generacion |

**Consumidores conocidos:** `audit-service`

**Esquema del payload:** `events/document.document.generated.schema.json` en
`design-software-shared-contracts` (PR #17).

---

### `document.version.created`

Se publica cuando se crea una nueva version de un documento existente (actualizacion de plantilla, regeneracion por cambio de datos).

**Payload:**

```json
{
  "version_id": "0a1b2c3d-0000-0000-0000-00000000000a",
  "document_id": "8f3c0000-0000-0000-0000-000000000001",
  "version_number": 2,
  "storage_key": "SCHEDULE/2026/06/5c1a0000-0000-0000-0000-000000000002/8f3c0000-0000-0000-0000-000000000001-v2.pdf",
  "created_by": "pdf-renderer-worker",
  "created_at": "2026-06-20T15:10:00Z"
}
```

Se publica con cada version, incluida la primera.

| Campo | Tipo | Descripcion |
|---|---|---|
| `version_id` | `string` | Identificador unico de la version |
| `document_id` | `string` | Referencia al documento padre |
| `version_number` | `integer` | Numero de version (incremental, comienza en 1) |
| `storage_key` | `string` | Ruta del binario de esta version en MinIO/S3 |
| `created_by` | `string` | Componente o usuario que origino la nueva version |
| `created_at` | `string (ISO 8601)` | Marca de tiempo de creacion de la version |

**Consumidores conocidos:** `audit-service`

**Esquema del payload:** `events/document.version.created.schema.json` en
`design-software-shared-contracts` (PR #17).

---

## Eventos consumidos

---

### `document-generation-queue` (cola interna)

**Origen:** `POST /documents/generate` de document-api.

```json
{ "document_id": "uuid", "template_code": "SCHEDULE_CERTIFICATE", "data_payload": {}, "correlation_id": "corr-5b0f6f0e" }
```

El `pdf-renderer-worker` consume este mensaje, renderiza el PDF, lo sube a MinIO/S3, registra el `document_version`, deja el documento en `AVAILABLE` y publica `document.document.generated` y `document.version.created`. Un mensaje para un documento ya `AVAILABLE` crea una nueva version y solo publica `document.version.created`. La idempotencia es por `correlation_id`.

---

### `scheduling.schedule.published`

> Previsto, no implementado: este evento lo atenderia el `document-lifecycle-worker`.

**Origen:** `scheduling-service`  
**Topic:** `scheduling-events`

Cuando el horario academico de un periodo es publicado y queda en estado definitivo, `document-service` genera automaticamente el PDF de horario para cada grupo o estudiante afectado.

**Flujo:**
1. Se recibe el evento con los datos del horario publicado.
2. Se selecciona la plantilla `schedule-pdf-v{n}` del repositorio de plantillas Handlebars.
3. Se crea un registro de documento con `status=GENERATING` para cada entidad propietaria relevante.
4. El `pdf-renderer-worker` renderiza el PDF combinando la plantilla con los datos del horario.
5. El binario se almacena en MinIO/S3 bajo el prefijo `documents/scheduling/`.
6. El registro del documento pasa a `status=AVAILABLE`.
7. Se publica `document.document.generated`.

**Plantilla utilizada:** `schedule-pdf-v2`

---

### `academic.ficha.opened`

> Previsto, no implementado: este evento lo atenderia el `document-lifecycle-worker`.

**Origen:** `academic-service`  
**Topic:** `academic-events`

Cuando se abre una ficha de matricula para un estudiante, `document-service` genera el comprobante de matricula (enrollment record) en formato PDF.

**Flujo:**
1. Se recibe el evento con el ID del estudiante y los datos de la ficha.
2. Se selecciona la plantilla `enrollment-record-v{n}` del repositorio de plantillas Handlebars.
3. Se crea un registro de documento con `status=GENERATING` vinculado al `owner_entity_id` del estudiante.
4. El `pdf-renderer-worker` renderiza el PDF con los datos academicos del estudiante.
5. El binario se almacena en MinIO/S3 bajo el prefijo `documents/academic/`.
6. El registro del documento pasa a `status=AVAILABLE`.
7. Se publica `document.document.generated`.

**Plantilla utilizada:** `enrollment-record-v1`

---

## Formato de envelope

Todos los eventos siguen el envelope estandar de la plataforma ([`_template/service/events.md`](../../_template/service/events.md) y [`event-catalog.md`](../../event-catalog.md)):

```json
{
  "event_id": "5b0f6f0e-7c0a-5d4e-9a41-0f0e6a1b2c3d",
  "event_type": "document.document.generated",
  "version": "1.0",
  "timestamp": "2026-06-20T14:32:00Z",
  "source_service": "document-service",
  "correlation_id": "corr-5b0f6f0e",
  "payload": {
    "document_id": "8f3c0000-0000-0000-0000-000000000001",
    "template_code": "SCHEDULE_CERTIFICATE",
    "domain": "SCHEDULE",
    "owner_entity_id": "5c1a0000-0000-0000-0000-000000000002",
    "owner_service": "scheduling-service",
    "storage_key": "SCHEDULE/2026/06/5c1a0000-0000-0000-0000-000000000002/8f3c0000-0000-0000-0000-000000000001-v1.pdf",
    "mime_type": "application/pdf",
    "size_bytes": 204800,
    "generated_by": "pdf-renderer-worker",
    "generated_at": "2026-06-20T14:32:00Z"
  }
}
```

| Campo | Descripcion |
|---|---|
| `event_id` | UUID determinista (derivado del `id` de la version y del tipo): un evento republicado conserva su identidad; los consumidores deduplican por `event_id` |
| `event_type` | Nombre completo del evento; es la routing key del topic `document-events` |
| `version` | Version del envelope (`1.0`) |
| `timestamp` | Timestamp de emision en ISO 8601 UTC |
| `source_service` | Servicio emisor (`document-service`) |
| `correlation_id` | Se propaga desde el `X-Correlation-Id` de `POST /documents/generate` |
| `payload` | Payload especifico del evento |

---

## Politica de reintentos

La generacion de PDFs puede fallar por errores transitorios en el renderizador, indisponibilidad de MinIO/S3 o del broker. La politica aplica al `pdf-renderer-worker` (ver [contrato](./components/pdf-renderer-worker/contract.md)).

| Parametro | Valor |
|---|---|
| Reintentos | `RENDER_MAX_RETRIES` (3 por defecto) |
| Espera entre intentos | Exponencial desde `RENDER_BACKOFF_SECONDS` (1 s por defecto, tope 30 s) |
| Comportamiento en fallo definitivo | `status=GENERATION_FAILED` + mensaje a la DLQ `pdf-renderer.dlq` |

**Flujo de reintentos:**

```
Intento 1 → falla → esperar 1s
Intento 2 → falla → esperar 2s
Intento 3 → falla → esperar 4s
Intento 4 → falla → marcar documento status=GENERATION_FAILED
                   → enviar el mensaje original a pdf-renderer.dlq (cabecera x-failure-reason)
                   → NO se publica document.document.generated
```

**Errores que activan reintento:**
- Falla del motor de PDF
- Error de conexion a MinIO/S3 al subir el binario
- Broker o base de datos no disponibles

**Errores que NO activan reintento (DLQ inmediata):**
- Mensaje de generacion invalido
- Documento inexistente, archivado o expirado
- Plantilla no encontrada o inactiva (`template_code` invalido)
- `output_type` distinto de PDF
- Plantilla que no produce contenido (sintaxis Handlebars invalida)

**Acciones post-fallo definitivo:**
- El campo `status` del registro de documento se actualiza a `GENERATION_FAILED` (una regeneracion fallida conserva la version vigente).
- El motivo del fallo viaja en la cabecera `x-failure-reason` del mensaje en la DLQ y en los logs del worker.
- El mensaje que origino la generacion queda en la DLQ para revision manual.

---

## Proceso de generacion asincrona

El `document-service` nunca genera documentos de forma sincrona. Todo flujo de generacion pasa por el `pdf-renderer-worker` via cola interna.

### Flujo implementado (HU-DOC-002 y HU-DOC-004)

```
Cliente o servicio autorizado
        |  POST /documents/generate
        v
[document-api] crea el registro del documento
        status = GENERATING
        document_id asignado
        |
        v
Mensaje encolado en `document-generation-queue`
        { document_id, template_code, data_payload, correlation_id }
        (correlation_id: se propaga desde el header X-Correlation-Id de POST /documents/generate;
         si el cliente no lo envía, document-api genera uno)
        |
        v
[pdf-renderer-worker] toma el mensaje de la cola
        |
        ├── renderiza la plantilla Handlebars con los datos
        ├── genera el PDF
        └── sube el binario a MinIO/S3
        |
        v
[pdf-renderer-worker] registra el document_version y actualiza el documento
        status = AVAILABLE
        storage_key = ruta definitiva en MinIO/S3
        size_bytes, mime_type registrados
        |
        v
[pdf-renderer-worker] publica los eventos de salida → topic: document-events
        document.document.generated (primera version)
        document.version.created    (cada version)
```

### Flujo previsto, no implementado: generacion disparada por eventos de otros servicios

```
Evento entrante (p.ej. scheduling.schedule.published)
        |
        v
[document-lifecycle-worker] recibe el evento del topic externo,
        resuelve el template_code segun el tipo de evento, crea el documento (GENERATING)
        y encola el mensaje en `document-generation-queue`
        |
        v
continua con el flujo implementado (pdf-renderer-worker)
```

El `document-lifecycle-worker` no publica `document.document.generated` ni `document.version.created`: esos eventos los publica el `pdf-renderer-worker`.

**Componentes involucrados:**

| Componente | Puerto / Rol | Responsabilidad en el flujo |
|---|---|---|
| `document-api` | 8007 | Expone REST: solicitud de generacion (`POST /documents/generate`), consulta de documentos, versiones y URL firmada de descarga |
| `template-api` | 8007 (sub-ruta `/templates`) | Administra plantillas HTML/Handlebars |
| `pdf-renderer-worker` | worker interno | Consume `document-generation-queue`, renderiza, sube binarios a MinIO/S3, registra versiones y publica `document.document.generated` y `document.version.created` |
| `document-lifecycle-worker` | worker interno (previsto, no implementado) | Consumira eventos externos para disparar la generacion y orquestara el ciclo de vida (archivado y expiracion) |

**Estados del ciclo de vida del documento** (los de `document.status`, ver [data-model.md](./data-model.md)):

| Estado | Descripcion |
|---|---|
| `GENERATING` | Registro creado, renderizado en progreso; aun no hay archivo |
| `AVAILABLE` | PDF generado y disponible en almacenamiento |
| `GENERATION_FAILED` | Todos los reintentos agotados; el mensaje queda en la DLQ y requiere intervencion manual |
| `ARCHIVED` | Documento archivado |
| `EXPIRED` | Documento vencido por la politica de retencion |

## Entrega durable e idempotencia (HU-DOC-002 / HU-DOC-008)

Cuando el render termina, `document.document.generated` (solo para la primera versión) y
`document.version.created` (para cada versión) se guardan en `document.event_outbox` junto con la
versión del documento dentro de la misma transacción. `document.message_inbox` registra la
correlación procesada por `pdf-renderer-worker`; su clave identifica el consumidor, el documento y
el `correlation_id`. Esto evita volver a crear una versión al recibir o reprocesar el mismo mensaje.

El proceso `outbox_dispatcher` selecciona filas aún no publicadas y disponibles, bloqueándolas con
`SKIP LOCKED` para permitir más de una instancia. Publica el envelope al exchange durable
`document-events`, con `event_type` como routing key, y marca `published_at` solo después de la
confirmación del broker. Si RabbitMQ falla, conserva la fila, aumenta `attempts` y programa un
reintento con backoff exponencial hasta 300 segundos. Puede haber redelivery si el proceso cae tras
la confirmación y antes de confirmar la transacción; por eso los consumidores deduplican por
`event_id`.

Los mensajes de generación que agotan sus reintentos se conservan en `pdf-renderer.dlq`. El
reproceso es manual y confirmado: revisar primero la causa indicada por `x-failure-reason` y luego
usar el comando documentado en el [runbook](./runbook.md#entrega-de-eventos-y-recuperacion-de-la-dlq).
