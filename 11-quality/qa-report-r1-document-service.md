# Informe técnico R1 — Resiliencia y mensajería (Document)

**Responsable:** Danna Valentina Barrios Penagos. **Rama:** `hu-r1-dev` desde `develop`. **Fecha:** 20 de octubre de 2026.

**Decisión de diseño:** ADR-011 en el repositorio `design-software-docs` (`05-architecture/decisions/records/ADR-011-document-outbox-inbox-resilience.md`).
**Capturas de pantalla:** se entregan junto con el MD de entrega a QA y no se guardan en este repositorio.

## 1. Qué se entrega

| Criterio del reto | Implementación | Prueba |
|---|---|---|
| (a) Outbox transaccional | `complete_generation` escribe la versión, el estado, el recibo del inbox y las filas de `event_outbox` en una sola transacción. El proceso `apps.outbox_dispatcher.main` entrega las filas pendientes. | `test_generation_request_becomes_an_available_downloadable_document`, caos |
| (b) Consumidor idempotente con tabla de deduplicación | `document.message_inbox` con clave primaria `(consumer_name, document_id, message_id)`; la redelivery se responde desde el recibo sin renderizar. `event_id` determinístico. | `test_new_version_and_redelivered_message`, caos |
| (c) Reintentos con backoff exponencial y DLQ con reproceso manual | Render: `min(backoff * 2^(n-1), 30 s)`. Publicación del outbox: `min(2^(n-1), 300 s)`. DLQ `pdf-renderer.dlq`; `apps.replay_dlq.main` republica con confirmación y solo entonces hace ACK. | `test_definitive_failure_...`, `test_manual_dlq_replay_...`, `test_long_retry_delay_...` |
| (d) Prueba de caos automatizada | Dos escenarios (sección 4): uno en proceso y otro contra los contenedores desplegados, con reinicio real del worker y del dispatcher. | `test_broker_outage_after_commit_...` y `test_chaos_broker_outage_and_service_restart_...` |

## 2. Cómo reproducirlo

Requisitos: Docker, Python 3.12 y el stack Document levantado con el perfil de `docker-infra`:

```bash
docker compose --profile document --profile iam --profile tooling --profile edge up -d --build
pip install -e '.[dev]'
```

Variables de la prueba de integración: `TEST_POSTGRES_DB_URL`, `TEST_AMQP_URL`, `TEST_S3_ENDPOINT` (y opcionalmente `TEST_S3_ACCESS_KEY`, `TEST_S3_SECRET_KEY`). Para los escenarios de caos se agregan:

- `TEST_CHAOS_COMPOSE_FILE`: ruta absoluta del `docker-compose.yml` de `docker-infra`.
- `TEST_CHAOS_PROJECT` y `TEST_CHAOS_ENV_FILE` (opcionales): nombre del proyecto Compose y su archivo de entorno.

```bash
python -m pytest -q
python -m pytest -q tests/test_pdf_renderer_worker_integration.py -k "broker_outage or service_restart"
```

Sin `TEST_CHAOS_COMPOSE_FILE` los dos escenarios de caos se omiten limpiamente (`5 passed, 2 skipped`, sin errores). Si el stack usa otro nombre de proyecto de Compose, el fallo indica configurar `TEST_CHAOS_PROJECT` y `TEST_CHAOS_ENV_FILE`.

**Aislamiento.** El worker y el dispatcher desplegados comparten la base de datos con los que corren dentro de `pytest` y publicarían las filas del outbox antes que la prueba. Por eso el fixture `infra` los detiene al empezar y los vuelve a iniciar al terminar, salvo en la prueba marcada `deployed_stack`, que los gobierna ella misma. No hay pasos manuales.

## 3. Resultados

Línea base: la suite del servicio sobre `develop` limpio (sin R1) da **98 passed**.

Con los cambios de R1, suite completa, stack levantado y caos habilitado, en dos corridas seguidas:

```text
tests/test_pdf_renderer_worker_integration.py
  test_generation_request_becomes_an_available_downloadable_document   PASSED
  test_new_version_and_redelivered_message                             PASSED
  test_definitive_failure_marks_the_document_failed_and_sends_the_message_to_the_dlq   PASSED
  test_manual_dlq_replay_recovers_after_a_transient_renderer_failure   PASSED
  test_long_retry_delay_keeps_the_broker_connection_alive              PASSED
  test_broker_outage_after_commit_preserves_events_and_restart_is_idempotent   PASSED
  test_chaos_broker_outage_and_service_restart_lose_no_event_and_duplicate_none   PASSED

======================= 101 passed in 150.63s (0:02:30) =======================
```

Migraciones: el changeset `975` se aplica sobre los 18 anteriores (total 19) desde una base nueva. En una base nueva los roles `document_reader`, `document_writer` y `document_admin` pueden no existir, por lo que los `GRANT` son condicionales y el changeset usa `splitStatements: false`. Rollback probado: elimina ambas tablas y deja 18 changesets; reaplicar restaura 19.

Recorrido por el gateway con IAM real (generación, outbox, inbox, eventos y descarga): 29 de 30 comprobaciones. La que falla es el preflight CORS, que `docker-infra` no configura para ningún dominio y que no pertenece a este reto.

Estado de las tablas tras el recorrido (consulta a PostgreSQL):

```text
         event_type          | attempts | published | event_id
-----------------------------+----------+-----------+----------
 document.version.created    |        0 | t         | c79f8673
 document.document.generated |        0 | t         | 3b3c08bf
 ...

    consumer_name    | document |  message_id  | version
---------------------+----------+--------------+----------
 pdf-renderer-worker | a51e5094 | corr-7a5beb8 | 61c9b0e7
 ...

 published | pending
-----------+---------
         8 |       0
```

## 4. Prueba de caos

**Escenario A — en proceso** (`test_broker_outage_after_commit_preserves_events_and_restart_is_idempotent`): el worker confirma la versión con dos eventos pendientes; se detiene RabbitMQ y el despacho reporta `(0 publicados, 2 aplazados)`; al reiniciarlo reporta `(2 publicados, 0 aplazados)`; un worker nuevo recibe de nuevo el mismo comando y no crea otra versión ni otros eventos.

**Escenario B — contra los contenedores desplegados** (`test_chaos_broker_outage_and_service_restart_lose_no_event_and_duplicate_none`):

1. Se detiene el dispatcher y se publica el comando de generación; el worker desplegado confirma la versión y las dos filas quedan pendientes en el outbox.
2. Se detiene RabbitMQ a mitad del flujo.
3. Se **reinician el worker y el dispatcher** con el broker todavía caído; el dispatcher aplaza las dos filas (`attempts > 0`) y no se pierde nada: siguen en PostgreSQL.
4. Se levanta RabbitMQ; el dispatcher reiniciado publica las dos filas.
5. Se comprueba que llegaron exactamente dos eventos, de tipos distintos y con `event_id` distintos.
6. Se reenvía el mismo comando al worker reiniciado: sigue habiendo una versión, cero eventos nuevos y cero filas pendientes.

Con esto se demuestran los dos criterios del Acta: **cero eventos perdidos y cero efectos duplicados** tras detener el broker y reiniciar el servicio.

## 5. Decisiones y límites

- **Entrega al menos una vez.** Una confirmación del broker seguida de un fallo antes del commit de `published_at` puede repetir un evento con el mismo `event_id`; los consumidores deduplican por `event_id`.
- **Filas del outbox que fallan siempre.** Se reintentan con backoff de hasta 300 s y no hay una DLQ específica para ellas; son visibles por `attempts` y `last_error`. Se añadiría un límite y un estado de fallo si se exigiera un tope duro. La DLQ con reproceso manual cubre los mensajes de generación.
- **Solicitud de generación.** `POST /documents/generate` publica directo a la cola y responde 503 si no puede; el outbox protege los eventos posteriores al render.
- **Bloqueo durante la publicación.** El dispatcher mantiene el bloqueo de la fila mientras publica; es simple y correcto, y con un volumen muy alto convendría reclamar por lotes.
