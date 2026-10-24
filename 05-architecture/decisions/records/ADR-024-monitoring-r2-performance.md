# ADR-024: Optimización de lecturas de Monitoring para R2

- **Estado:** PROPOSED (la implementación existe en los PR de código; pendiente de revisión de Arquitectura).
- **Fecha:** 20 de octubre de 2026.
- **Ámbito:** `monitoring-service` y `monitoring-db`.
- **Reto:** R2 — Rendimiento y datos.

## Contexto

El reto R2 del plan de mejoramiento exige medir los endpoints principales de
Monitoring con 50 usuarios virtuales durante cinco minutos, mantener un p95
inferior a 300 ms y una tasa de errores inferior al 1 %. También exige revisar
con `EXPLAIN (ANALYZE, BUFFERS)` las consultas de mayor coste y entregar los
índices como changesets Liquibase con rollback probado.

Las lecturas críticas del servicio ordenan registros recientes de KPI y
alertas. El reporte de resumen de KPI además necesita recuperar el registro más
reciente para cada combinación de ficha y tipo de KPI.

## Decisión

1. Mantener PostgreSQL como motor de consulta y añadir índices específicos en
   `monitoring.kpi_tracking` y `monitoring.generated_alert`.
2. Resolver la lectura "último KPI por ficha y tipo" con PostgreSQL
   `DISTINCT ON`, ordenando por `measured_at DESC, id DESC` para que el criterio
   de desempate sea determinista.
3. Declarar los índices en un changeset Liquibase versionado, con un rollback
   explícito que elimine únicamente los índices de R2.
4. Mantener sin cambios el contrato HTTP de los endpoints. La optimización se
   realiza en la consulta interna del servicio.
5. Ejecutar la carga k6 desde un script versionado con los umbrales del reto:
   `vus: 50`, `duration: 5m`, `p(95)<300`, `http_req_failed<1 %` y checks
   superiores al 99 %.

## Índices

| Tabla | Índice | Uso principal |
|---|---|---|
| `monitoring.kpi_tracking` | `ix_kpi_tracking_measured_at_id` | Paginación ordenada por fecha e identificador |
| `monitoring.kpi_tracking` | `ix_kpi_tracking_ficha_tracking_id_kpi_type_id_measured_at_id` | Último KPI por ficha y tipo |
| `monitoring.generated_alert` | `ix_generated_alert_generated_at_id` | Paginación ordenada de alertas |

Los índices se crean en:

```text
design-software-monitoring-db/01_ddl/10_indexes/r2_performance_indexes.sql
```

El changeset y el rollback están en el mismo repositorio de base de datos.

## Alternativas consideradas

| Alternativa | Decisión | Motivo |
|---|---|---|
| Mantener `GROUP BY` + `MAX` para el resumen | Descartada | Recorre y agrupa más filas antes de recuperar el registro completo. |
| Crear índices sin migración | Descartada | Rompe la trazabilidad, reproducibilidad y reversión exigidas por R2. |
| Resolver el resumen en memoria | Descartada | Traslada el coste al servicio y aumenta el volumen transferido desde PostgreSQL. |
| Usar `DISTINCT ON` con orden determinista | Elegida | Es nativo de PostgreSQL y permite combinar la selección del último registro con el índice compuesto. |

## Consecuencias

### Positivas

- Las lecturas ordenadas pueden utilizar índices en lugar de ordenar toda la
  relación en memoria.
- El resumen de KPI tiene una consulta explícita de "último registro por
  ficha/tipo".
- La optimización se puede instalar y revertir mediante Liquibase.
- El contrato HTTP no cambia para los consumidores.

### Costes y límites

- Los índices consumen espacio y añaden trabajo a las escrituras de las tablas
  monitorizadas.
- `DISTINCT ON` es una decisión específica de PostgreSQL; no se presenta como
  una abstracción portable a otros motores.
- Las cifras del informe R2 se obtuvieron en el entorno Docker local con datos
  sintéticos transaccionales; los datos de benchmark se revirtieron al terminar.
  Debe repetirse la medición con una distribución representativa antes de fijar
  capacidad productiva.

## Reversión

El rollback del changeset elimina:

```text
monitoring.ix_generated_alert_generated_at_id
monitoring.ix_kpi_tracking_ficha_tracking_id_kpi_type_id_measured_at_id
monitoring.ix_kpi_tracking_measured_at_id
```

El rollback se ejecutó en el entorno Docker local y después se volvió a
ejecutar `update` para dejar instalada la versión final del changeset.

## Evidencia relacionada

- [Informe técnico R2 de Monitoring](../../../11-quality/qa-report-r2-monitoring-service.md)
- Script k6: `design-software-monitoring-service/performance/k6/monitoring.js`
- Changeset: `design-software-monitoring-db/01_ddl/10_indexes/changelog.yaml`
