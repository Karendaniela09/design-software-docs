# Evidencia R6 — recorrido Go v2 + EXPAND/BACKFILL + CONTRACT/rollback

**Fecha UTC:** 2026-10-23  
**Repositorio servicio:** `design-software-training-environment-service`  
**Commit servicio:** `5356df5483c91582f27d836ce18c776b5a3a13be`  
**Repositorio DB:** `design-software-training-environment-db`  
**DB commit declarado:** `4640239879af14032abfcec0c0e641f20f607ff`  
**Motor:** PostgreSQL 16 en Docker  
**Liquibase declarado:** 4.33.0

## 1. Preparación EXPAND/BACKFILL

En una base PostgreSQL desechable se preparó la tabla real
`training_environment.maintenance` con la columna legacy `reason`, se ejecutó
el SQL 964 de EXPAND y posteriormente el SQL 965 de BACKFILL.

Resultado de la verificación posterior:

```text
rows | reason_detail_non_null | divergences
-----+------------------------+------------
1    | 1                      | 0
```

## 2. Prueba del servicio Go v2

Con la base en EXPAND/BACKFILL se ejecutó:

```powershell
$env:TEST_DATABASE_URL = "postgres://postgres:postgres@localhost:55432/env_db?sslmode=disable"
$env:REQUIRE_POSTGRES_INTEGRATION = "1"
go test -count=1 -v ./internal/adapter/out/persistence -run 'TestPostgresMaintenanceRepository_'
```

Resultado:

```text
TestPostgresMaintenanceRepository_HU006_CRUDFiltersAndTransactionalOutbox: PASS
TestPostgresMaintenanceRepository_HU018_TemporalValidation: PASS
PASS
```

La prueba HU006 verificó que la operación del servicio persiste el valor en
`reason_detail` y crea el evento correspondiente en `training_environment.outbox`.

## 3. CONTRACT 966

Se ejecutó `01_ddl/04_alter/966_r6_reason_contract.sql` después de comprobar
que no existían divergencias.

Resultado de estructura:

```text
column_name  | is_nullable
-------------+------------
reason_detail | YES
```

La columna `reason` desapareció y los datos de `reason_detail` permanecieron:

```text
rows | reason_detail_non_null
-----+-----------------------
5    | 2
```

La evidencia no afirma `NOT NULL`, porque el SQL 966 actual no aplica esa
restricción.

## 4. Rollback

Se ejecutó el rollback 966 y posteriormente se reaplicó el SQL 964 para
restaurar la función y el trigger de sincronización.

Resultado:

```text
column_name  | is_nullable
-------------+------------
reason       | YES
reason_detail | YES

divergences
-----------
0
```

Esto demuestra que el esquema legacy y la sincronización pueden recuperarse
sin divergencias en el laboratorio desechable.

## 5. Resultado y límites

El recorrido local demuestra R6(c) contra EXPAND/BACKFILL y confirma la
reversión estructural del laboratorio. La suite completa del servicio conserva
un fallo ajeno en la prueba histórica de índices de reservas HU019; el test
específico de mantenimiento R6 pasa.

Queda pendiente la revisión de QA y la aprobación del arquitecto responsable.
La evidencia no autoriza por sí sola CONTRACT en un ambiente institucional.
