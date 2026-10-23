# Technical QA Report — R6 Training Environment Database

**Author:** Juan Sebastián González Horta (`jsgh1`)
**Team:** Training Environment
**Review date:** 2026-10-22
**Scope:** Liquibase schema evolution for `training_environment.maintenance`
**Requirement:** R6 — schema evolution without service downtime
**Status:** PASS for the documented Docker laboratories; institutional promotion is not claimed.

## 1. Executive summary

R6 changes the real domain table `training_environment.maintenance` from the legacy `reason` column to `reason_detail` using an expand/backfill/contract migration. The design keeps the old column available while consumers are being adapted, copies historical values before the cutover, and provides a tested rollback path.

The final laboratory run validated EXPAND, BACKFILL, CONTRACT, CONTRACT rollback, and full rollback of EXPAND/BACKFILL in four disposable Docker PostgreSQL databases. The laboratories were identified as `develop`, `qa`, `staging`, and simulated `main`; these labels do not represent official institutional environments.

The result is accepted for local laboratory evidence. It does not claim a production deployment, a zero-downtime measurement under continuous institutional traffic, or approval to run CONTRACT on a shared database.

## 2. Repositories and traceability

| Repository | Responsibility | Reference |
|---|---|---|
| `design-software-training-environment-db` | Liquibase changesets, SQL migrations, changelogs, and rollbacks. | [DB PR #134](https://github.com/code-sena/design-software-training-environment-db/pull/134) |
| `design-software-training-environment-service` | Go consumer compatibility and maintenance API behavior. | Service implementation is documented in the service report. |
| `design-software-docker-infra` | Disposable Docker/PostgreSQL laboratory orchestration. | Used only for isolated local validation. |
| `design-software-docs` | ADR, service report, and this QA report. | Current documentation branch. |

**Database commit reviewed:** `4640239879af14032abfcec10c0e641f20f607ff`.
**Tools reported by the execution package:** PostgreSQL 16, Liquibase 4.33.0, Docker Desktop 4.90.0, and Docker Engine 29.7.2.

## 3. Domain change and migration design

The affected table is `training_environment.maintenance`. The legacy application reads and writes `reason`, so directly renaming or dropping that column would break the previous consumer. The migration therefore follows this sequence:

| Stage | Artifact | Technical behavior |
|---|---|---|
| EXPAND | `01_ddl/04_alter/964_r6_maintenance_reason_expand.sql` | Adds nullable `reason_detail` and the temporary synchronization mechanism while retaining `reason`. |
| BACKFILL | `01_ddl/04_alter/965_r6_maintenance_reason_backfill.sql` | Copies historical values into `reason_detail` without destroying the original values. |
| CONTRACT | `changelog/changelog-r6-contract.yaml` with `966_r6_reason_contract.sql` | Removes `reason`, keeps `reason_detail`, and applies the final required-column contract. |
| Rollback | Versioned rollback scripts for 964, 965, and 966 | Reconstructs the compatible schema and restores the previous write path. |

Changesets 964 and 965 are part of the ordinary migration history. Changeset 966 is intentionally isolated in a manual CONTRACT changelog and is not included in the ordinary startup changelog. This prevents an automatic destructive cutover while old consumers still depend on `reason`.

## 4. Data preparation and BACKFILL validation

The test data included legacy maintenance rows with non-null values and a null legacy value. After EXPAND and BACKFILL, the checks compared the two representations using PostgreSQL null-safe comparison (`IS DISTINCT FROM`). The validation also exercised writes through both compatibility paths and checked that contradictory values were rejected by the synchronization rules.

The final execution reported, per laboratory:

- 4 initial rows, including 3 non-null legacy reasons and 1 null value.
- 6 rows after the compatibility write checks.
- 5 non-null reasons after EXPAND/BACKFILL.
- 0 divergences between the legacy and new representations before CONTRACT.

The original TEXT values were preserved while the new representation was populated. The evidence scope covers the supported single-action/version-1 representation; it does not prove reconstruction for unsupported future JSON/document versions.

## 5. Compatibility during migration

The compatibility requirement was evaluated in two layers:

1. **Database compatibility:** both columns coexisted during EXPAND/BACKFILL, synchronized writes were checked, and legacy reads remained possible.
2. **Service compatibility:** the existing Go service was compiled and exercised against the expanded schema in the available laboratory scenarios. The final four-laboratory rerun focused on SQL/Liquibase CONTRACT and rollback; it did not repeat new HTTP Go traffic in that specific run.

The service must be upgraded and verified before CONTRACT is enabled in a shared environment. The local Go v2 implementation is documented separately and must be coordinated with the database cutover; this report does not treat a local branch as an institutional deployment.

## 6. CONTRACT validation

CONTRACT was executed from the final independent changelog:

```text
changelog/changelog-r6-contract.yaml
```

The checks validated that:

- `reason` was removed only at the deliberate CONTRACT stage.
- `reason_detail` retained the migrated values and became the final required field.
- The expected row counts and non-null counts remained stable.
- No pre-CONTRACT data divergence remained.

The changeset `r6-env-maintenance-reason-contract-v1` completed successfully in each of the four isolated laboratories.

## 7. Rollback validation

Each laboratory executed the following rollback sequence:

1. Roll back CONTRACT with Liquibase `rollbackCount 1` using the same final CONTRACT changelog.
2. Verify that `reason` was restored.
3. Verify that the synchronization trigger and function were restored.
4. Verify that data written before CONTRACT remained available.
5. Roll back BACKFILL and EXPAND.
6. Verify the final pre-migration schema and preserved test data.

The reported result was PASS in all four Docker laboratories. The rollback test supports the isolated laboratory scope only; it does not replace a shared-environment rehearsal, backup-restore test, or production change approval.

## 8. Verification matrix

| R6 criterion | Evidence reviewed | Result |
|---|---|---|
| (a) Expand/contract on a real domain table | Changesets 964 and 966, independent CONTRACT changelog, preconditions, and schema checks. | **PASS — four isolated laboratories** |
| (b) Test data and backfill | Legacy seed data, null handling, equality checks, compatibility writes, and row-count checks. | **PASS — four isolated laboratories** |
| (c) Previous and new schema during migration | Coexistence of `reason` and `reason_detail`, synchronization checks, and available Go service compatibility validation. | **PASS for laboratory scope; final HTTP rerun not repeated** |
| (d) Rollback in four Docker environments | CONTRACT rollback plus EXPAND/BACKFILL rollback and post-rollback schema/data checks. | **PASS — 4/4 isolated laboratories** |
| Institutional environments | Shared QA, staging, production, continuous traffic, and deployment window. | **NOT CLAIMED** |

## 9. Risks and deployment conditions

- Do not run CONTRACT while an old consumer still requires `reason`.
- CONTRACT must be explicitly authorized and executed from its independent changelog.
- A disposable database and isolated Compose project must be used for future reproductions.
- A backup-restore rehearsal and an authorized shared-environment deployment test remain pending.
- Availability under continuous real traffic was not measured.
- The tested data shape covers the documented version-1/single-action case, not every possible future JSON shape.

## 10. Final decision

**R6 passes for the submitted local Docker laboratory scope.** The evidence demonstrates the expand/backfill/contract flow and integral rollback in four isolated databases. The result must not be interpreted as approval for institutional deployment until the Go consumer cutover, backup procedure, deployment authorization, and shared-environment validation are completed.

## References

- [ADR-017 — Training Environment schema evolution](../05-architecture/decisions/records/ADR-017-training-environment-r6-schema-evolution.md)
- [Training Environment service R6 report](../09-microservices/services/04-training-environment-service/r6-schema-evolution.md)
- [Training Environment service README](../09-microservices/services/04-training-environment-service/README.md)
- [Training Environment DB PR #134](https://github.com/code-sena/design-software-training-environment-db/pull/134)
