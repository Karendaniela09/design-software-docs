# ADR-011: Outbox transaccional e inbox idempotente para document-service

**Estado:** ACCEPTED (2026-10-20)
**Fecha:** 2026-10-20
**Autores:** Danna Valentina Barrios Penagos
**Equipos involucrados:** Arquitectura, Backend (document-service), Base de datos (document-db), DevOps

---

## Contexto

`document-service` genera PDFs de forma asíncrona. El worker `pdf-renderer-worker` consume `document-generation-queue`, renderiza el documento, lo guarda en el object storage ([ADR-003](./ADR-003-object-storage.md)), confirma la versión en PostgreSQL y publica dos eventos de dominio en el exchange `document-events` ([ADR-001](./ADR-001-message-broker.md)).

El diseño anterior confirmaba la versión en PostgreSQL y **después** publicaba los dos eventos en RabbitMQ. PostgreSQL y RabbitMQ no comparten transacción. Si el broker caía entre ambos pasos, el documento quedaba `AVAILABLE` pero uno o los dos eventos podían no emitirse. Volver a entregar el mensaje de generación evitaba una segunda versión gracias a `correlation_id`, pero la recuperación de los eventos dependía de esa reentrega.

Se necesita que el servicio no pierda eventos de dominio ni produzca efectos duplicados ante caídas del broker o reinicios del servicio.

## Decisión

Se decide adoptar el patrón **outbox transaccional** para los eventos del dominio y una **tabla de deduplicación (inbox)** para el consumidor de comandos de generación.

1. `document_version`, el estado del documento, el recibo de `message_inbox` y las filas de `event_outbox` se guardan en **la misma transacción** de PostgreSQL.
2. `message_inbox` registra `(consumer_name, document_id, message_id)` asociado a `version_id`; `message_id` es el `correlation_id` del mensaje. Una reentrega consulta este recibo antes de renderizar. La restricción única de `document_version` sigue protegiendo las carreras.
3. Un proceso independiente (`outbox-dispatcher`) reclama las filas pendientes con `FOR UPDATE SKIP LOCKED`, publica con confirmación del broker y marca `published_at`. Un fallo incrementa `attempts` y reprograma `available_at` con **backoff exponencial** con tope de 300 segundos.
4. El `event_id` es determinístico por `(version_id, event_type)`. La entrega es **al menos una vez**; un evento reenviado conserva su identidad y los consumidores deduplican por `event_id`.
5. Se mantienen los reintentos del render con backoff y la DLQ `pdf-renderer.dlq`. El reproceso es **explícito**: republica el cuerpo original a la cola principal, espera la confirmación y solo entonces hace ACK en la DLQ.
6. Las tablas `document.event_outbox` y `document.message_inbox` se crean con el changeset `975` de `document-db`, con script de rollback.

## Consecuencias

### Positivas

- El worker completa la versión aunque RabbitMQ esté caído; los eventos quedan pendientes en PostgreSQL y se entregan al recuperarse el broker.
- Una redelivery no crea otra versión ni otros eventos.
- Los eventos pendientes o con fallos son visibles y consultables (`published_at`, `attempts`, `last_error`).
- Se pueden ejecutar varios dispatchers a la vez sin publicar la misma fila dos veces.

### Negativas / Trade-offs

- Hay un proceso más que desplegar (`outbox-dispatcher`); sin él, `event_outbox` crece y los eventos no llegan al broker.
- El dispatcher mantiene el bloqueo de la fila mientras publica. Es simple y correcto; con un volumen muy alto convendría reclamar por lotes y publicar fuera de la transacción.
- Las filas del outbox que fallan indefinidamente se reintentan sin límite (con backoff de hasta 300 s) y no hay una DLQ específica para ellas; se detectan por `attempts` y `last_error` altos.

### Riesgos

- Una confirmación del broker seguida de un fallo antes del commit de `published_at` puede repetir un evento. No se promete entrega exactamente una vez a consumidores externos; se promete una identidad estable para deduplicar.
- `POST /documents/generate` conserva su publicación directa a la cola y su respuesta 503 si no puede publicarse. Este ADR protege los **eventos de dominio posteriores al render**; la durabilidad de la solicitud de generación antes de encolarse requeriría una evolución aparte.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Publicar dentro de la transacción SQL | RabbitMQ no participa en el commit de PostgreSQL. |
| Reintentar solo por redelivery de la cola de generación | Deja sin recuperación una versión ya confirmada cuando no se reentrega el comando. |
| Transacción distribuida entre el broker y la base de datos | Añade coordinación y no está disponible en los adaptadores actuales. |
| Una DLQ específica para el outbox con límite de intentos | Se difiere: los fallos permanentes del dispatcher son visibles por `attempts` y `last_error`, y el reproceso de la DLQ de generación ya cubre los mensajes de entrada. Se puede añadir si se requiere un límite duro. |

## Referencias

- Documento relacionado en este repo: [ADR-001-message-broker.md](./ADR-001-message-broker.md) y [ADR-003-object-storage.md](./ADR-003-object-storage.md)
- Modelo de datos del servicio: `../../../09-microservices/services/07-document-service/data-model.md`
- Implementación: `code-sena/design-software-document-service` (PR #5) y `code-sena/design-software-document-db` (PR #59, changeset `975`)
