# R2 — Rendimiento y datos de audit-service

> Estado: 🟡 En revisión | Última actualización: 2026-10-21
> Autor: Freinier Cardona | Equipo: Auditoría / ADSO 3145555

## Contexto

Este informe reúne la implementación y la evidencia reproducible del R2 del
plan de mejoramiento. La fuente ejecutable está repartida por responsabilidad:
`design-software-audit-service` contiene el escenario k6 y los scripts,
`design-software-audit-db` contiene la migración Liquibase y
`design-software-docker-infra` orquesta el entorno local. No se versionan
contraseñas, tokens, archivos `.env` ni resultados dependientes de una máquina.

## Alcance

Se evalúan exclusivamente los endpoints de lectura ya contratados:

- listado `GET /api/v1/audit-records`;
- detalle `GET /api/v1/audit-records/{id}`;
- exportación `GET /api/v1/audit-records/export`.

La prueba conserva IAM, `AUDIT_LOG_VIEW`, `AUDIT_EXPORT` y el alcance del
centro de formación. No agrega rutas, bypass de autenticación ni datos de
producción.

## Entregables y trazabilidad

| Criterio R2 | Entrega versionada | Estado verificable |
|-------------|-------------------|--------------------|
| Carga k6: 50 VUs, 5 min, p95 < 300 ms, errores < 1 % | `design-software-audit-service/performance/k6/audit-query.js` | Umbrales y duración definidos; falta una ejecución autenticada para aprobar las dos métricas. |
| Tres `EXPLAIN (ANALYZE, BUFFERS)` antes y después | `performance/sql/r2-explain.sql`, `performance/sql/r2-seed.sql`, `scripts/run-r2-data.ps1` | Ejecutado en PostgreSQL 16 con fixture aislado de 200 002 filas. |
| Índices Liquibase con rollback | Changeset `r2-audit-performance-query-indexes` y SQL de rollback en `design-software-audit-db` | Rollback `rollback-count 1` probado y los tres índices quedaron ausentes. |
| Informe comparativo | Este documento y [ADR-015](../../05-architecture/decisions/records/ADR-015-audit-r2-performance-data.md) | Versionado; las salidas crudas quedan fuera de Git. |

## Validación del entorno

El 2026-10-21 se levantó un proyecto Compose aislado con PostgreSQL, RabbitMQ,
las 19 migraciones de audit-db, los roles técnicos y ambos procesos de
audit-service. Los endpoints internos `audit-query-api:8081/ready` y
`audit-worker:8082/ready` respondieron `200`; el worker mantuvo una conexión
activa con RabbitMQ. Esta comprobación no sustituye la prueba de carga ni
requiere credenciales de usuario IAM.

## Resultados de datos

Las mediciones se ejecutaron el 2026-10-21 en PostgreSQL 16 y un proyecto
Compose aislado. Son evidencia de planificación y selección de índices; deben
repetirse si cambian el motor, recursos Docker o la forma del fixture.

| Consulta representada | Antes | Después | Efecto observado |
|-----------------------|-------|---------|------------------|
| Listado por centro y tipo de evento | incremental sort; 0.849 ms; 14 hit / 0 read buffers | index scan ordenado; 0.277 ms; 5 hit / 4 read buffers | 67.4 % menos tiempo; desaparece el incremental sort. |
| Listado por servicio origen | parallel sequential scan + sort; 76.578 ms; 5 354 hit / 0 read | index scan ordenado; 0.190 ms; 4 hit / 3 read | 99.8 % menos tiempo; elimina scan completo y sort. |
| Exportación por centro (160 002 filas) | incremental sort; 117.388 ms; 7 816 hit / 284 read | index scan ordenado; 99.244 ms; 5 266 hit / 1 145 read | 15.5 % menos tiempo; elimina incremental sort. |

Después de `rollback-count 1`, la comprobación `to_regclass` devolvió
`t | t | t`: los tres índices R2 estaban ausentes. El script los reaplica y
finaliza actualizando el esquema completo para no dejar el entorno a medio
estado.

## Reproducción local

Desde un checkout con los repositorios como hermanos, crear archivos locales a
partir de sus plantillas, sin versionarlos:

```powershell
Copy-Item design-software-audit-service/.env.example design-software-audit-service/.env
Copy-Item design-software-audit-service/.env.worker.example design-software-audit-service/.env.worker
Copy-Item docker-infra/design-software-docker-infra/.env.example docker-infra/design-software-docker-infra/.env
```

Completar únicamente los valores locales de `.env`, incluida una cuenta IAM de
prueba con `AUDIT_LOG_VIEW` y `AUDIT_EXPORT`; no guardar un access token. Para
los planes y rollback, desde `design-software-audit-service`:

```powershell
pwsh .\scripts\run-r2-data.ps1 `
  -InfraDirectory ..\docker-infra\design-software-docker-infra `
  -EnvFile ..\docker-infra\design-software-docker-infra\.env
```

Para la carga autenticada, desde `design-software-docker-infra`:

```powershell
docker compose --env-file .env --profile tooling up -d postgres
docker compose --env-file .env --profile tooling run --rm liquibase-audit update
docker compose --env-file .env --profile audit-bootstrap run --rm audit-db-principals
docker compose --env-file .env --profile iam --profile audit up -d --build
docker compose --env-file .env --profile audit-load run --rm audit-k6
```

k6 produce `performance/results/k6-summary.json` localmente. El escenario
termina con código distinto de cero cuando `http_req_duration` p95 no es menor
de 300 ms o `audit_request_errors` no es menor de 1 %.

## Estado de aceptación

| AC | Estado | Evidencia |
|----|--------|-----------|
| 50 VUs por cinco minutos | Configurado | El escenario fija `vus: 50` y `duration: 5m`. |
| p95 < 300 ms y errores < 1 % | Pendiente de aprobación | Los thresholds están activos, pero no existe una corrida autenticada con la cuenta requerida en este workspace. |
| Tres planes antes y después | Cumplido | Tabla de resultados y script reproducible. |
| Changeset y rollback probado | Cumplido | Changeset, rollback SQL y verificación de ausencia de los tres índices. |
| Informe antes y después | Cumplido | Este informe conserva cifras, alcance y limitación de la carga. |

## Referencias

- [ADR-015 — Rendimiento reproducible de las consultas de Auditoría](../../05-architecture/decisions/records/ADR-015-audit-r2-performance-data.md)
- [Ficha técnica de audit-service](../../09-microservices/services/09-audit-service/README.md)
- `design-software-audit-service/.env.example`
- `design-software-audit-service/.env.worker.example`
- `design-software-docker-infra/.env.example`
