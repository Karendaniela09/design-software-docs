# Corrección HU019

## Causa

`TestPostgresReservationRepository_HU019_IndexesFiltersAndExclusion` asumía
que los cuatro índices y la restricción de exclusión ya existían en la base de
datos. En una PostgreSQL limpia el fixture no creaba esos objetos, por lo que
la prueba fallaba antes de validar el comportamiento del repositorio.

## Corrección aplicada

Se agregó `prepareHU019IndexFixture` al test para preparar de forma idempotente:

- `idx_reservation_environment_date`;
- `idx_reservation_requester_created_at`;
- `idx_reservation_requester_date`;
- `idx_reservation_status_date`;
- `excl_reservation_no_overlap`;
- tablas mínimas de `training_environment` necesarias para el escenario.

La corrección solo hace reproducible el fixture de prueba. No cambia la lógica
de producción ni elimina índices históricos.

## Verificación

```text
TestPostgresReservationRepository_HU019_IndexesFiltersAndExclusion: PASS
Suite ./internal/adapter/out/persistence: 16 PASS, 0 FAIL
```
