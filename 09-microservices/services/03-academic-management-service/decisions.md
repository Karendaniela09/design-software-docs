# Decisiones internas — academic-management-service

> Estado: 🟢 Estable | Última actualización: 2026-06-20
> Para decisiones que afectan más de un servicio → crear ADR en `05-architecture/decisions/records/`

La estrategia de outbox, confirmación, idempotencia y DLQ se documenta en [ADR-025](../../../05-architecture/decisions/records/ADR-025-academic-resilient-messaging.md).

| # | Decisión | Alternativas descartadas | Motivo | Fecha |
|---|----------|--------------------------|--------|-------|
| 01 | Combinar M5 (programas) y M6 (fichas) en un solo servicio | Dos servicios separados | Fichas referencian directamente al programa; separarlos requeriría llamadas síncronas frecuentes entre servicios sin beneficio real en este volumen | 2026-06-17 |
| 02 | Las fichas cerradas son inmutables | Permitir edición post-cierre | Integridad de los horarios ya generados que referencian la ficha; el cierre es un hecho de negocio irreversible | 2026-06-17 |
| 03 | `training_shift` y `training_modality` como ENUMs locales de BD (no FK a catálogo de reference-data-service) | FK hacia tabla de catálogo en reference-data-service; lookup vía HTTP en cada escritura | La creación de una ficha no puede depender de la disponibilidad en tiempo de ejecución de reference-data-service. Los valores de jornada y modalidad son estables por normativa SENA (Acuerdo 009/2024) y cambiarían solo con una nueva versión del sistema. El ENUM local garantiza integridad sin acoplamiento operacional. Si los valores cambian en el futuro, se gestiona con una migración de esquema | 2026-06-20 |
| 04 | `enrollment_ficha.status` como VARCHAR con transiciones aplicadas por código (no CHECK constraint de BD) | ENUM de BD con CHECK; máquina de estados en la BD vía trigger | Las reglas de transición son lógica de negocio compleja: el paso a `PRODUCTIVE_STAGE` depende del porcentaje de horas ejecutadas; el paso a `COMPLETED` requiere que todos los aprendices activos tengan nota definitiva. Estas condiciones no son expresables con un CHECK de BD. Centralizar en la capa de aplicación permite testear las reglas de transición de forma aislada y auditarlas en el historial de código | 2026-06-20 |
| 05 | Historial de matrículas de aprendices mediante tabla `learner_ficha_enrollment` (no un campo `ficha_id` directo en el aprendiz) | `ficha_id` único en la entidad del aprendiz | Un aprendiz puede transferirse de una ficha a otra durante su formación (traslados de sede, cambio de jornada, reprogramaciones). Con un campo directo en el aprendiz se perdería el historial de la ficha anterior. La tabla de matrícula permite registrar la fecha de vinculación, la fecha de retiro, el motivo del traslado y el estado en cada ficha de forma separada, sin borrar registros históricos | 2026-06-20 |
| 06 | Jerarquía curricular `tech_line` → `tech_network` → `knowledge_network` → `training_program` replica la estructura organizacional del SENA (Acuerdo 009/2024) | Estructura plana; jerarquía simplificada de dos niveles | La normativa SENA establece esta jerarquía de cuatro niveles para clasificar programas. Los reportes institucionales y los permisos por regional ya están organizados por esta taxonomía. Aplanarla implicaría rehacer la correspondencia con la estructura real cada vez que se genere un informe o se configuren permisos por línea tecnológica | 2026-06-20 |

## Decisiones abiertas HU-ACAD-10 a HU-ACAD-15

Estas decisiones quedan abiertas para arquitectura/producto; este PR de Docs no las resuelve:

| Tema | Estado | Nota |
|------|--------|------|
| Semántica de `expected_end_date: null` | Abierta | Definir impacto en actualización operativa y reportes. |
| Retención de DLQ | Abierta | Definir duración y responsabilidad operativa. |
| DLQ por consumidor R1 | Abierta | ADR-025 (PROPOSED) propone que el consumidor R1 use `academic-events.r1.dlq` y que la DLQ de publicación siga separada; se cierra al aceptar el ADR. |
| Reprocesamiento de DLQ R1 | Abierta | ADR-025 (PROPOSED) propone que un operador autorizado use `POST /api/v1/events/dlq/reprocess-next` conservando `message_id`; se cierra al aceptar el ADR. El endpoint está en el contrato OpenAPI. |
| Feature RBAC para operar la DLQ | Abierta | Hoy el endpoint exige `ACADEMIC_FICHA_MANAGE`. Definir si la operación de DLQ merece un feature propio. |
| Consumidor R1 de referencia | Abierta | Solo registra recibos (`processed_event`) y viene apagado por defecto. Definir qué consumidor real adopta el inbox idempotente. |
| Ubicación/semántica de `row_version` | Abierta | Confirmar si viaja en body, header u otro mecanismo. |
| Respuesta ante `404` de Actors | Abierta | Definir si Academic responde 404, 409, 422, 503 u otro error. |
| Autenticación M2M/scope Academic → Actors | Abierta | Confirmar client credentials, scope y feature requeridos. |
| Preconditions Scheduling/Actors para transiciones | Abierta | Definir APIs/HUs para `EXECUTION → PRODUCTIVE_STAGE` y `PRODUCTIVE_STAGE → COMPLETED`. |
| Campos nullable de reportes | Abierta | Confirmar `days_remaining`, `is_delayed` y otros nulos cuando falte `expected_end_date`. |
