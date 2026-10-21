# Entrega de eventos a Monitoring, Notification y Audit

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

El relay publica en `scheduling-events` usando `event_type` como routing key.
El antiguo `convertAndSend(exchange, payload)` utilizaba el exchange por defecto
y trataba el nombre del exchange como routing key, por lo que no entregaba el
evento a los consumidores del topic.

Cada publicación contiene el envelope común: `event_id` estable de la outbox,
`event_type`, `version`, `timestamp` UTC, `source_service` y `payload`. El relay
marca `PUBLISHED` después del confirm del broker y de comprobar que no hubo
devolución por falta de ruta. Ante un fallo conserva `PENDING` para reintentar.
Los consumidores deduplican por `event_id`.

La cancelación de sesión escribe un único evento e incluye `ficha_id`; evita
el segundo evento que antes creaba el puerto de mensajería para la misma acción.
Monitoring actualiza su contexto de planificación y conserva la asignación de
Actors. Un horario publicado o una cancelación no son mediciones de asistencia
ni de currículo: no se fabrican porcentajes para generar alertas.

Configurar `OUTBOX_ENABLED=true`, `RABBITMQ_HOST`, `RABBITMQ_USERNAME` y
`RABBITMQ_PASSWORD`. La aplicación activa confirms correlacionados y returns.
Las migraciones oficiales de Scheduling deben existir antes de iniciar el relay.

`OutboxDeliveryTest` comprueba envelope, routing, ACK/NACK y retención para
reintento. La receta `deploy/Dockerfile.scheduling-integration` de docker-infra
ejecuta estas pruebas. La verificación entre servicios se encuentra en
`design-software-monitoring-service/scripts/test_r3_scheduling.py`; declara
explícitamente sus UUID de referencia aislados de competencia/ambiente y no afirma haber
validado disponibilidad de Training Environment.
