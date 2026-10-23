# Evidencia R6(c) — consumidor Go v2

**Repositorio:** `design-software-training-environment-service`  
**Rama:** `feat/r6-service-reason-detail`  
**Base declarada:** `origin/develop`  
**Commit de evidencia:** `e8c8d7c`  
**Rama remota:** `origin/feat/r6-service-reason-detail`  
**PR:** https://github.com/code-sena/design-software-training-environment-service/pull/new/feat/r6-service-reason-detail  
**Alcance:** consumidor Go v2 durante EXPAND/BACKFILL  
**Estado:** evidencia ejecutada y publicada para revisión de QA y Arquitectura; no constituye aprobación formal.

## Objetivo

Demostrar que el servicio conserva el contrato HTTP público `reason`, pero
persiste, lista y consulta el valor en `training_environment.maintenance.reason_detail`
durante la fase expand/backfill.

## Cambios verificables

- `internal/adapter/out/persistence/postgres_maintenance_repo.go`
  - `List` selecciona `reason_detail`.
  - `Get` selecciona `reason_detail`.
  - `Create` inserta en `reason_detail`.
- `internal/adapter/out/persistence/postgres_maintenance_repo_test.go`
  - crea una maintenance mediante el caso de uso;
  - comprueba que el valor HTTP/dominio se persiste físicamente en `reason_detail`;
  - conserva la validación del outbox y de las restricciones existentes.
- El contrato HTTP continúa exponiendo `reason` para compatibilidad durante la
  transición; el cambio de columna es interno al adaptador PostgreSQL.

## Reproducción

Desde la raíz del repositorio del servicio:

```powershell
$env:TEST_DATABASE_URL = "postgres://usuario:contraseña@localhost:5432/env_db?sslmode=disable"
$env:REQUIRE_POSTGRES_INTEGRATION = "1"
go test -count=1 -v ./internal/adapter/out/persistence
```

La base utilizada debe estar en EXPAND/BACKFILL y contener, como mínimo:

```sql
training_environment.maintenance.reason
training_environment.maintenance.reason_detail
training_environment.outbox
```

La prueba debe comprobar simultáneamente:

1. escritura del caso de uso sobre `reason_detail`;
2. lectura del registro desde `reason_detail`;
3. conservación del campo HTTP `reason`;
4. persistencia del evento en `training_environment.outbox`;
5. ausencia de divergencia entre `reason` y `reason_detail` durante la fase
   de compatibilidad.

## Compatibilidad con CONTRACT

No se debe ejecutar CONTRACT contra esta versión del servicio. El orden
correcto es:

1. publicar y revisar esta rama/PR;
2. desplegar y probar Go v2 contra EXPAND/BACKFILL;
3. confirmar que no existen consumidores activos de `reason`;
4. ejecutar CONTRACT desde `changelog/changelog-r6-contract.yaml`;
5. probar lectura y escritura del servicio después de CONTRACT;
6. ejecutar rollback de CONTRACT y verificar nuevamente el consumidor legacy.

## Resultado de la revisión

La implementación queda preparada en una rama accesible para revisión. El
veredicto de R6(c) debe emitirse únicamente después de ejecutar el comando de
integración con PostgreSQL y adjuntar su salida, el commit exacto y la
configuración del esquema utilizada.

La aprobación formal del R6 completo queda pendiente de QA y de la revisión
del arquitecto responsable.

## Estado de ejecución en esta revisión

La prueba específica de mantenimiento se ejecutó con PostgreSQL 16 real en
Docker y obtuvo PASS. La salida completa está en:

- `evidencias/r6-go-v2-test-output.txt`
- `evidencias/r6-go-v2-test-report.md`
- `evidencias/r6-end-to-end-lab.md`

El comando `go test ./...` también fue ejecutado. La suite completa falla en
`TestPostgresReservationRepository_HU019_IndexesFiltersAndExclusion`, una
prueba histórica de índices de reservas ajena a R6. Ese fallo no se presenta
como PASS ni se atribuye al cambio `reason_detail`; la evidencia R6 usa el
resultado aislado de los tests `TestPostgresMaintenanceRepository_`.
