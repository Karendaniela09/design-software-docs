# R6 Schema Evolution — Maintenance Reason

**Service:** Training Environment Service
**Database change:** `maintenance.reason` → `maintenance.reason_detail`
**Status:** DB laboratory validation completed; complete R6 service validation remains pending.

## Decision and scope

The migration uses an expand/backfill/contract sequence on the real `training_environment.maintenance` table. The legacy `reason` column remains available while the consumer is upgraded. CONTRACT is isolated in `changelog/changelog-r6-contract.yaml` and must not run while an old consumer still depends on `reason`.

## Database sequence

| Stage | Database artifact | Purpose |
|---|---|---|
| EXPAND | `964_r6_maintenance_reason_expand.sql` | Adds nullable `reason_detail` and compatibility synchronization. |
| BACKFILL | `965_r6_maintenance_reason_backfill.sql` | Copies existing values without losing legacy data. |
| CONTRACT | `966_r6_reason_contract.sql` in `changelog-r6-contract.yaml` | Removes `reason`; the current SQL does not apply `NOT NULL` to `reason_detail`, so the documentation must not claim that constraint is implemented. |
| Rollback | Versioned rollback scripts for 964, 965 and 966 | Restores the compatible schema and data path. |

## Compatibility and validation

The database checks covered legacy rows, backfill equality, writes through both compatibility paths, CONTRACT, and rollback. Historical/local Go evidence exists, but no accessible Go v2 branch or PR was found in the reviewed refs and the available service still uses `maintenance.reason`. Four isolated Docker PostgreSQL laboratories were used: `develop`, `qa`, `staging`, and `main` (the latter is a simulated laboratory, not an institutional production environment).

The reported DB result was successful for the isolated laboratories: CONTRACT applied, `rollbackCount` completed, the legacy column and synchronization objects were restored, and the test data remained consistent. This evidence does not close service compatibility, does not claim a production deployment, continuous-traffic availability measurement, or validation against shared institutional environments.

## Operational constraints

- Run CONTRACT only after all old consumers have been stopped or upgraded.
- Use an isolated disposable database for reproduction; do not run the procedure against shared environments.
- Record the database and service commit SHAs, Liquibase version, SQL checks, and rollback output for each authorized run.
- Coordinate the final Go consumer release with the database CONTRACT release.

## References

- [ADR-017 — Training Environment schema evolution](../../../05-architecture/decisions/records/ADR-017-training-environment-r6-schema-evolution.md)
- [R6 QA report](../../../11-quality/qa-report-r6-training-environment-db.md)
- [Training Environment service README](README.md)
- [Training Environment DB PR #134](https://github.com/code-sena/design-software-training-environment-db/pull/134)
