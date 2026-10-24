# Informe técnico — R2 Rendimiento y datos de Monitoring

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: José David Amaya Mosquera | Equipo: Monitoring / ADSO 3145555

## 1. Identificación

| Campo | Valor |
|---|---|
| Persona | José David Amaya Mosquera |
| Dominio | Monitoring |
| Reto | R2 — Rendimiento y datos |
| Servicio | `monitoring-service` |
| Base de datos | `monitoring-db` |
| Rama del servicio | `feat/r2-performance-data-monitoring` |
| Rama de la base de datos | `feat/r2-performance-data-monitoring` |
| Rama de documentación | `docs/r2-performance-data-monitoring` |
| Commit de `monitoring-service` | `68b9cae` |
| Commit de `monitoring-db` | `a04ffc2` |
| Fecha de validación local | 20 de octubre de 2026 |

El commit de documentación se identifica en el historial de la rama
`docs/r2-performance-data-monitoring`; el PR debe enlazarlo junto con los dos
commits de implementación.

## 2. Alcance implementado

Se implementó únicamente el reto individual R2 dentro del dominio Monitoring:

- consulta optimizada de resumen de KPI en `monitoring-service`;
- índices de lectura en `monitoring-db`;
- changeset Liquibase con rollback;
- script k6 versionado para los endpoints principales;
- ADR y este informe en `design-software-docs`.

No se modificaron otros dominios ni se migraron repositorios consumidores.

## 3. Cambios de código

### `monitoring-service`

Archivos modificados:

```text
src/monitoring/adapter/inbound/http/router.py
performance/k6/monitoring.js
```

`/reports/kpi-summary` dejó de usar la combinación `GROUP BY` + `MAX` para
obtener el registro más reciente. Ahora usa `DISTINCT ON` sobre
`(ficha_tracking_id, kpi_type_id)`, con orden determinista por
`measured_at DESC, id DESC`, y conserva el contrato de respuesta y los filtros
existentes.

El script k6 cubre estas lecturas:

```text
/kpi-types
/kpi-statuses
/ficha-trackings
/kpi-trackings
/generated-alerts
/reports/kpi-summary
/reports/indicators
```

### `monitoring-db`

Archivos modificados:

```text
01_ddl/10_indexes/changelog.yaml
01_ddl/10_indexes/r2_performance_indexes.sql
05_rollbacks/01_ddl/10_indexes/r2_performance_indexes.rollback.sql
```

El changeset agrega tres índices:

```text
ix_kpi_tracking_measured_at_id
ix_kpi_tracking_ficha_tracking_id_kpi_type_id_measured_at_id
ix_generated_alert_generated_at_id
```

## 4. Evidencia de consultas

La comparación se ejecutó con `EXPLAIN (ANALYZE, BUFFERS)` sobre PostgreSQL
16 en el stack Docker local. Para evitar alterar los datos funcionales del
entorno, el benchmark cargó datos sintéticos dentro de una transacción y
finalizó con `ROLLBACK`.

Fixture utilizada durante la medición:

- 10.000 fichas de seguimiento;
- 50.000 registros de KPI;
- 20.000 alertas generadas.

### 4.1 Lectura ordenada de KPI

Consulta representativa:

```sql
SELECT *
FROM monitoring.kpi_tracking
ORDER BY measured_at DESC, id DESC
LIMIT 50;
```

| Estado | Plan observado | Tiempo de ejecución |
|---|---|---:|
| Antes | `Parallel Append` / escaneo secuencial y `Sort` | 20,174 ms |
| Después | `Merge Append` con `ix_kpi_tracking_measured_at_id` | 0,149 ms |

### 4.2 Resumen del último KPI por ficha y tipo

La implementación anterior usaba `GROUP BY` + `MAX` y alcanzó 42,062 ms en
la medición inicial. La implementación final cambia la forma de la consulta a
`DISTINCT ON` y utiliza el índice compuesto de R2.

| Estado | Plan observado | Tiempo de ejecución |
|---|---|---:|
| Baseline de la consulta anterior | `HashAggregate` sobre escaneos completos | 42,062 ms |
| Consulta final `DISTINCT ON` | `Merge Append` con índice compuesto | 25,567 ms |

La comparación de esta fila debe interpretarse como una optimización de
consulta, no como una comparación de la misma sentencia textual: el cambio
incluye la eliminación del patrón `GROUP BY` + `MAX`.

### 4.3 Lectura ordenada de alertas

Consulta representativa:

```sql
SELECT *
FROM monitoring.generated_alert
ORDER BY generated_at DESC, id DESC
LIMIT 50;
```

| Estado | Plan observado | Tiempo de ejecución |
|---|---|---:|
| Antes | Escaneo secuencial y `top-N heapsort` | 3,080 ms |
| Después | Escaneo por `ix_generated_alert_generated_at_id` | 0,143 ms |

Los tiempos son los reportados por PostgreSQL para el fixture local; no son un
SLO productivo ni sustituyen una prueba con datos representativos.

## 5. Evidencia Liquibase y rollback

Comandos ejecutados sobre el stack Docker local:

```text
liquibase validate
liquibase update
liquibase rollbackCount 1
liquibase update
```

Resultados:

- `validate`: correcto, sin errores de validación.
- `update`: ejecutó `r2-monitoring-performance-indexes`.
- `rollbackCount 1`: correcto; eliminó los tres índices de R2.
- `update` posterior: correcto; reinstaló el changeset final.
- Verificación posterior: los tres índices existen en el esquema `monitoring`.

## 6. Prueba k6

Comando ejecutado con la imagen oficial de k6 y el script versionado:

```text
docker run --rm --network ds-develop_default \
  -v <monitoring-service>/performance/k6/monitoring.js:/scripts/monitoring.js:ro \
  -e K6_BASE_URL=http://r2-monitoring-api-test:8000/api/v1 \
  -e MONITORING_K6_TOKEN=<token-efímero-de-prueba> \
  grafana/k6:latest run /scripts/monitoring.js
```

La instancia bajo prueba utilizó una clave pública efímera montada solo para
esta ejecución; no se extrajeron ni reutilizaron claves privadas de IAM.

Configuración y resultado:

| Métrica | Resultado | Criterio R2 | Estado |
|---|---:|---:|---|
| Usuarios virtuales | 50 | 50 | PASS |
| Duración | 5 min | 5 min | PASS |
| Solicitudes | 72.594 | — | — |
| Errores HTTP | 0,00 % | < 1 % | PASS |
| Checks | 100,00 % | > 99 % | PASS |
| p95 HTTP | 205,3 ms | < 300 ms | PASS |

El p95 corresponde a `http_req_duration`. La ejecución finalizó sin VU
interrumpidos y los recursos temporales fueron retirados después de la prueba.

## 7. Pruebas adicionales

En `monitoring-service` se ejecutó la suite dentro de la imagen Docker del
servicio:

```text
pytest -q
```

Resultado:

```text
28 passed, 6 skipped, 1 warning
```

También se ejecutó:

```text
ruff check apps src tests
python -m compileall -q apps src tests
```

Resultado: ambos checks correctos.

La imagen `monitoring-api` se construyó correctamente con el Dockerfile del
stack local.

## 8. Limitaciones y siguientes validaciones

- La medición SQL usa datos sintéticos transaccionales y fue revertida; se debe
  repetir en un entorno con volumen y distribución representativos antes de
  fijar capacidad productiva.
- La carga k6 se ejecutó contra una instancia temporal del API y PostgreSQL
  local. El resultado demuestra el comportamiento del cambio en el entorno de
  validación, no una garantía de rendimiento en producción.
- La rama de documentación publica la evidencia y referencia los SHA de código
  `68b9cae` y `a04ffc2`; el segundo commit todavía requiere autorización de
  escritura en el remoto de `monitoring-db` para poder asociarlo a un PR.
- Este reto no modifica la promoción de ramas ni fusiona PRs. La integración
  debe seguir el flujo aprobado por el repositorio.

## 9. Referencias

- [ADR-024 — Optimización de lecturas de Monitoring para R2](../05-architecture/decisions/records/ADR-024-monitoring-r2-performance.md)
- [Contrato OpenAPI de Monitoring](../07-api/contracts/openapi/monitoring.yaml)
