# Resultado de prueba R6(c) — Go v2 contra PostgreSQL

**Resultado:** PASS para las pruebas específicas de mantenimiento R6(c).  
**Fecha UTC:** 2026-10-23T12:28:42.4836490Z  
**Commit probado:** `5356df5483c91582f27d836ce18c776b5a3a13be`  
**Rama:** `feat/r6-service-reason-detail`  
**Base:** PostgreSQL 16 en Docker, `env_db`, puerto local `55432`  
**Modo:** `REQUIRE_POSTGRES_INTEGRATION=1`

## Comando ejecutado

```powershell
$env:TEST_DATABASE_URL = "postgres://postgres:postgres@localhost:55432/env_db?sslmode=disable"
$env:REQUIRE_POSTGRES_INTEGRATION = "1"
go test -count=1 -v ./internal/adapter/out/persistence -run 'TestPostgresMaintenanceRepository_'
```

## Resultado

```text
TestPostgresMaintenanceRepository_HU006_CRUDFiltersAndTransactionalOutbox: PASS
TestPostgresMaintenanceRepository_HU018_TemporalValidation: PASS
PASS
```

La prueba HU006 confirma, entre otros controles, que el valor recibido por el
servicio se persiste físicamente en `training_environment.maintenance.reason_detail`
y que el evento transaccional se registra en `training_environment.outbox`.

## Alcance y limitación

Esta evidencia valida el consumidor Go v2 contra un PostgreSQL real en un
laboratorio Docker. La ejecución de `go test ./...` también fue realizada, pero
la suite completa falló en `TestPostgresReservationRepository_HU019_IndexesFiltersAndExclusion`,
una prueba histórica de índices de reservas ajena a R6. Por eso el resultado
que se presenta como PASS es el test específico de mantenimiento R6(c), no la
suite completa del repositorio.

La aprobación formal del R6 completo sigue requiriendo la revisión de QA y del
arquitecto responsable, además de la validación del flujo DB EXPAND/BACKFILL →
Go v2 → CONTRACT y rollback en el alcance institucional autorizado.

La salida de la suite completa solicitada con
`go test -count=1 -v ./internal/adapter/out/persistence` está conservada en
[`r6-full-persistence-suite-output.txt`](./r6-full-persistence-suite-output.txt).
Los tests R6 de mantenimiento pasan; la suite completa mantiene el fallo
independiente HU019 de índices de reservas.
