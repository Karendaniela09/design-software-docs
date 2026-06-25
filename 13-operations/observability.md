# Observabilidad

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: DevOps / Arquitectura

## Contexto

Este documento define la estrategia de observabilidad del sistema **Horarios SENA**. La observabilidad es fundamental para entender el comportamiento del sistema en tiempo real, detectar problemas y diagnosticar fallos.

Se utilizan tres pilares principales: **logs**, **métricas** y **trazas**.

## Pilares de observabilidad

| Pilar | Descripción | Herramienta |
|-------|-------------|-------------|
| **Logs** | Registros estructurados de eventos del sistema. | SLF4J + Logback (backend) / console (frontend) |
| **Métricas** | Indicadores cuantitativos (rendimiento, errores, uso de recursos). | Micrometer + Prometheus |
| **Trazas** | Seguimiento de peticiones a través de múltiples servicios. | Correlation ID (manual) / Jaeger (futuro) |

---

## Logs

### Formato

Los logs deben ser estructurados en formato JSON para facilitar su ingesta y análisis.

```json
{
  "timestamp": "2026-06-24T10:30:00.123Z",
  "level": "INFO",
  "service": "scheduling-service",
  "correlation_id": "abc-123-def",
  "user_id": "coordinator_001",
  "message": "Horario creado exitosamente",
  "schedule_id": "123e4567-e89b-12d3-a456-426614174000",
  "duration_ms": 150
}