# Decisiones internas — monitoring-service

> Estado: 🟢 Vigente | Última actualización: 2026-10-20
> Para decisiones que afectan más de un servicio → ADR en `05-architecture/decisions/records/`.

| # | Decisión | Motivo | Estado |
|---|----------|--------|--------|
| 01 | `kpi_type` es catálogo de BD, no enum nativo. | Permite parametrizar nuevos KPI sin deploy. | ACCEPTED |
| 02 | `alert_type.default_threshold` es configurable. | Los umbrales pedagógicos/normativos pueden cambiar. | ACCEPTED |
| 03 | `active_alert_count` es una desnormalización controlada/derivable. | Optimiza dashboard; requiere consistencia por trigger o cálculo derivado. | ACCEPTED |
| 04 | `attendance_percentage` se calcula de forma consistente en persistencia. | Evita divergencia entre escritores. | ACCEPTED |
| 05 | `ficha_tracking` está activo durante la etapa de ejecución. | Reduce ruido y acota el ciclo de seguimiento. | ACCEPTED |
| 06 | `improvement_plan` de Monitoring es a nivel de ficha; el plan individual pertenece a Actors. | Ownership distinto. | ACCEPTED |
| 07 | Las mediciones `kpi_tracking` son append-only. | Conserva historia/tendencia. | ACCEPTED |
| 08 | Monitoring construye su estado principalmente por eventos. | Evita polling/acoplamiento síncrono. | ACCEPTED |
| 09 | Evento canónico de alerta: `monitoring.alert.triggered`. | Unifica contratos y elimina el alias histórico `monitoring.alert.generated`. | ACCEPTED |
| 10 | **Decisión histórica: mantener `notification-worker` dentro de Monitoring.** | Era la opción previa a separar capacidades transversales. | **SUPERSEDED por ADR-005** |
| 11 | Migración progresiva de `improvement_plan.specific_actions` de TEXT a JSONB mediante EXPAND, BACKFILL, CONTRACT y ROLLBACK. | Preservar datos y compatibilidad HTTP durante la evolución del esquema. Ver ADR-013. | PROPOSED                         |

## Consecuencias de ADR-005 para Monitoring

Se eliminan de este bounded context:

- `notification-worker`;
- `sent_notification`;
- credenciales/configuración SMTP;
- lógica `EMAIL` / `IN_APP`;
- reintentos y DLQ de entrega;
- `monitoring.notification.sent`;
- endpoints `/sent-notifications`.

Monitoring conserva `generated_alert` y publica `monitoring.alert.triggered`. Cualquier consumidor interesado, incluido Notification, reacciona mediante el broker.

## Referencias

- [ADR-005](../../../05-architecture/decisions/records/ADR-005-microservices-topology-and-transversal-capabilities.md)
- [notification-service decisions](../10-notification-service/decisions.md)
- [ADR-013: Migración progresiva TEXT a JSONB](../../../05-architecture/decisions/records/ADR-013-monitoring-r6-text-jsonb-migration.md)
