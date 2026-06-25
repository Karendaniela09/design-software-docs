# Eventos - [Nombre del Servicio]

> Estado: 🔴 Pendiente | Última actualización: YYYY-MM-DD
> Autor: [Nombre Apellido] | Equipo: [nombre del equipo]

## Contexto

Este documento define los eventos de dominio que el servicio **[Nombre del Servicio]** publica y consume. Los eventos permiten la comunicación asíncrona con otros microservicios, desacoplando las operaciones y mejorando la resiliencia del sistema.

## Estructura de un evento

Todos los eventos deben seguir la siguiente estructura estándar:

```json
{
  "event_id": "123e4567-e89b-12d3-a456-426614174000",
  "event_type": "EVENT_TYPE_NAME",
  "occurred_at": "2026-06-24T10:30:00.123Z",
  "source": "service-name",
  "correlation_id": "abc-123-def",
  "actor_id": "coordinator_001",
  "data": {
    // Datos específicos del evento
  }
}