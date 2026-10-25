# Decisiones internas — monitoring-service

> Estado: 🟢 Vigente | Última actualización: 2026-10-24
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
| 12 | Lecturas de KPI y alertas con índices específicos y `DISTINCT ON` para el último KPI por ficha y tipo; el contrato HTTP no cambia. | Cumplir el objetivo p95 < 300 ms del reto R2 sin afectar a los consumidores. Ver ADR-024. | PROPOSED |
| 13 | La API acepta los access tokens de `iam-service`: firma RS256 contra el JWKS de IAM (`JWKS_URL`), `exp`, `sub` e `iss` (`JWT_ISSUER`, por defecto `sena-iam-service`). **No se exige audience:** IAM no emite `aud`, así que `JWT_AUDIENCE` es opcional y está vacío por defecto; si se configura pasa a ser obligatorio, y un `aud` inesperado se rechaza. El servicio no tiene llave, emisor ni modo sin firma locales. | Misma sesión que el resto de los módulos (ADR-022 §2) y mismo artefacto con las mismas variables en los 4 ambientes (ADR-022 §6). Fallar cerrado ante un `aud` inesperado obliga a una decisión explícita el día que IAM emita uno. Reemplaza la identidad aislada R3 de ADR-010. | PROPOSED |
| 14 | API, `alert-worker` y relay de Outbox se conectan con el **usuario de aplicación** (miembro de `monitoring_writer`), no con el superusuario. | Mínimo privilegio: el servicio solo necesita DML sobre el esquema `monitoring`; el patrón es el de los demás servicios (`create-app-user.sh`). | PROPOSED |

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
- [ADR-024: Optimización de lecturas de Monitoring para R2](../../../05-architecture/decisions/records/ADR-024-monitoring-r2-performance.md)
