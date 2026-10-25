# ADR-027: Rendimiento de consultas de Scheduling para R2

> Estado: PROPOSED — la evidencia está consolidada en el [informe QA R2 de Scheduling](../../../11-quality/qa-report-r2-scheduling-service.md); pendiente decisión del equipo de Arquitectura.

**Fecha de decisión:** 2026-10-20
**Última verificación:** 2026-10-24
**Equipo responsable:** Backend, Datos y Arquitectura

## Contexto

R2 pide k6 con 50 VUs por 5 minutos, p95 HTTP < 300 ms, errores < 1 %, ranking de las tres consultas SQL más costosas, `EXPLAIN (ANALYZE, BUFFERS)` antes/después y un changeset reversible con rollback probado.

Las consultas repetidas de Scheduling encontradas durante las cargas fueron: listado paginado de horarios activos, listado paginado de sesiones activas por horario y conteo de horarios activos.

## Decisión

Se conservan los cambios R2 definidos en `design-software-scheduling-db` y `design-software-scheduling-service`:

1. `ix_schedule_active_created_at` sobre `schedule(created_at) WHERE is_active = true`.
2. `ix_class_session_active_schedule_date` sobre `class_session(schedule_id, session_date) WHERE is_active = true`.
3. Compresión JSON habilitada desde 1 KB y `spring.jpa.open-in-view=false` en Scheduling (misma configuración en los cuatro ambientes).

El changeset `r2-scheduling-read-path-indexes-20261020` conserva el autor `juanCarlos` y tiene rollback que elimina los dos índices. No se añadió una migración duplicada al changelog de producción. Ambos índices se registran en el [modelo de datos](../../../09-microservices/services/05-scheduling-service/data-model.md).

## Evidencia que sustenta la decisión

| Escala | Resultado |
|---|---|
| k6, 501 horarios y 10 000 sesiones | p95 10.18 → 10.27 ms; 0 % de errores en ambas corridas. Cumple R2, pero **no muestra mejora HTTP**: con unas 20 sesiones por horario no hay ordenamiento que evitar. |
| `EXPLAIN` a escala pequeña | Horarios: Seq Scan + Sort → Index Scan, 0.271 → 0.079 ms. Sesiones: 0.260 → 0.428 ms en una sola ejecución en frío sobre 20 filas; no concluyente. |
| `EXPLAIN` con 4 000 horarios y 480 120 sesiones | Horarios: Seq Scan + Sort → Index Scan sin Sort. Sesiones: Bitmap Heap Scan + Sort → Index Scan sin Sort, del orden de 0.1 ms frente a 0.6–0.7 ms. Ninguna consulta empeoró su plan. |

El detalle, el método y los límites están en el [informe QA](../../../11-quality/qa-report-r2-scheduling-service.md). El índice de sesiones solo se justifica a partir de unos cien registros por horario; quitarlo es mecánico (una sentencia en el changeset y su rollback) si Arquitectura prefiere medirlo antes con volúmenes de producción.

## Rollback

Liquibase Community no permite `rollback-one-changeset`. Sobre una base con `develop` aplicado, `update` ejecuta un solo changeset, `rollback-count 1` elimina los dos índices y su registro en `DATABASECHANGELOG`, y un segundo `update` los restaura; `validate` no reporta errores.

## Consecuencias y límites

- El plan de horarios usa el índice parcial R2 en ambas escalas.
- El índice de sesiones cuesta 18 MB con 480 120 sesiones y solo mantiene filas activas; su beneficio aparece con horarios de unos cien registros o más.
- La mejora no se atribuye al p95 HTTP de k6: los dos estados cumplen los umbrales de R2.
- La evidencia es de Docker local con datos seed y sintéticos y carga directa al API, no de producción ni del trayecto a través de Traefik.
