# ADR-025: Mensajería resiliente para academic-management

**Estado:** PROPOSED
**Fecha:** 2026-10-20
**Autores:** Jhon Camilo Suaza Sanchez
**Equipos involucrados:** Arquitectura, Academic Management, Datos, DevOps

---

## Contexto

El dominio academic-management publica eventos cuando cambia información de programas, competencias o fichas. Una caída de RabbitMQ no puede hacer que se pierda el evento de un cambio ya confirmado en PostgreSQL. RabbitMQ también puede entregar el mismo mensaje más de una vez.

## Decisión

Se decide aplicar outbox transaccional e idempotencia durable:

1. La transacción de negocio escribe el evento en academic_management.outbox.
2. Un relay publica los eventos pendientes y solo marca published_at después de recibir un publisher confirm positivo.
3. Una publicación fallida se reintenta con backoff de 1, 4 y 16 segundos. Agotados los intentos, el mensaje se envía a academic-events.dlq.
4. El consumidor R1 escucha academic-events.r1.consumer. Después de sus reintentos fallidos, RabbitMQ enruta el mensaje a academic-events.r1.dlq. Es un consumidor de referencia que solo registra recibos: viene apagado por defecto (ACADEMIC_R1_CONSUMER_ENABLED=false) y su cola y binding se declaran únicamente al encenderlo.
5. academic_management.processed_event impone unicidad por (consumer_name, event_id). El registro atómico evita un segundo efecto para el mismo mensaje.
6. Un operador autorizado puede ejecutar POST /api/v1/events/dlq/reprocess-next; el reproceso conserva message_id.

## Consecuencias

### Positivas

- Un cambio confirmado conserva su evento aunque RabbitMQ esté temporalmente caído.
- La confirmación del broker evita declarar una publicación antes de que RabbitMQ la acepte.
- Las entregas repetidas se reconocen con una clave durable.
- La DLQ permite observar y reprocesar fallos agotados.

### Negativas / Trade-offs

- La publicación es asíncrona y existe una ventana de consistencia eventual.
- processed_event crece y necesita una política operativa de retención.
- Los mensajes en DLQ requieren intervención explícita de un operador autorizado.

### Riesgos

- Un reproceso manual sin autorización o trazabilidad podría repetir operaciones.
- Una configuración incorrecta de exchanges, bindings o publisher confirms puede impedir la entrega.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Publicar directamente desde el caso de uso | Puede perder el evento si PostgreSQL confirma y RabbitMQ falla. |
| Confiar únicamente en el ACK de RabbitMQ | No evita efectos duplicados ante redeliveries. |
| Deduplicación solo en memoria | Se pierde al reiniciar y no funciona entre réplicas. |

## Referencias

- [Validación integrada R1](../../../11-quality/academic-r1-validation-report.md)
- [Decisiones de academic-management](../../../09-microservices/services/03-academic-management-service/decisions.md)
- Implementación propuesta: code-sena/design-software-academic-management-service PR #18.
