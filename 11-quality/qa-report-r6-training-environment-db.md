# Technical QA Report — R6 Training Environment Database

**Author:** Juan Sebastián González Horta (`jsgh1`)
**Team:** Training Environment
**Review date:** 2026-10-22
**Scope:** Liquibase schema evolution for `training_environment.maintenance`
**Requirement:** R6 — schema evolution without service downtime
**Status:** R6 technically PASS for the documented local laboratory scope; formal approval remains pending QA/Architecture review.

## 1. Executive summary

R6 changes the real domain table `training_environment.maintenance` from the legacy `reason` column to `reason_detail` using an expand/backfill/contract migration. The design keeps the old column available while consumers are being adapted, copies historical values before the cutover, and provides a tested rollback path.

The final laboratory run validated EXPAND, BACKFILL, CONTRACT, CONTRACT rollback, and full rollback of EXPAND/BACKFILL in four disposable Docker PostgreSQL databases. The laboratories were identified as `develop`, `qa`, `staging`, and simulated `main`; these labels do not represent official institutional environments.

The database and Go v2 results are accepted for local laboratory evidence only. The Go v2 branch is published as `origin/feat/r6-service-reason-detail`; its maintenance integration tests passed against PostgreSQL 16 with EXPAND/BACKFILL applied, and the CONTRACT/rollback checks were recorded in the service evidence. This report does not claim a production deployment, a zero-downtime measurement under continuous institutional traffic, or authorization to run CONTRACT on a shared database. Formal approval remains pending the architect responsible.

## 2. Repositories and traceability

| Repository | Responsibility | Reference |
|---|---|---|
| `design-software-training-environment-db` | Liquibase changesets, SQL migrations, changelogs, and rollbacks. | [DB PR #134](https://github.com/code-sena/design-software-training-environment-db/pull/134) |
| `design-software-training-environment-service` | Go consumer compatibility and maintenance API behavior. | `origin/feat/r6-service-reason-detail`, commit `999009a`; PostgreSQL integration evidence is consolidated in this report. |
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
2. **Service compatibility:** the published Go v2 branch was tested against PostgreSQL 16 with EXPAND/BACKFILL applied. The maintenance integration tests passed and verified persistence through `reason_detail` plus the transactional outbox. The HTTP evidence remains historical support; the authoritative current evidence is the PostgreSQL test output committed with the service branch.

The service must be upgraded and verified before CONTRACT is enabled in a shared environment. That requirement is satisfied for the laboratory scope by the published branch, PostgreSQL integration PASS, and reproducible evidence stored in Docs. Shared-environment authorization and Architecture approval remain separate governance conditions.

## 6. CONTRACT validation

CONTRACT was executed from the final independent changelog:

```text
changelog/changelog-r6-contract.yaml
```

The checks validated that:

- `reason` was removed only at the deliberate CONTRACT stage.
- `reason_detail` retained the migrated values after CONTRACT. The current SQL does not apply `NOT NULL` to this column; therefore this report does not claim that constraint.
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
| (c) Previous and new schema during migration | SQL coexistence plus published Go v2 PostgreSQL integration PASS against EXPAND/BACKFILL. | **PASS — local laboratory scope** |
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

**R6 passes technically for the submitted local laboratory scope.** The evidence demonstrates the expand/backfill/contract flow, Go v2 compatibility against EXPAND/BACKFILL, and integral rollback in the isolated database evidence. The result must not be interpreted as approval for institutional deployment. The formal closure remains pending QA/Architecture review, deployment authorization, and any shared-environment validation required by governance.

## 11. Consolidated execution evidence

This section is the single source of truth for the evidence previously kept in
separate Markdown and text files. It consolidates the service implementation
description, the R6 end-to-end laboratory record, the Go v2 test output, the
pre- and post-correction persistence-suite outputs, and the HU019 correction.
The former auxiliary files are intentionally not required to interpret or
reproduce the result.

### 11.1 Evidence identity and reproducibility

| Item | Value |
|---|---|
| Service repository | `design-software-training-environment-service` |
| Service branch | `feat/r6-service-reason-detail` |
| Service evidence commit | `5356df5483c91582f27d836ce18c776b5a3a13be` |
| Current service branch tip | `999009a` |
| DB repository | `design-software-training-environment-db` |
| DB commit reviewed | `4640239879af14032abfcec0c0e641f20f607ff` |
| Database engine | PostgreSQL 16 in Docker |
| Liquibase | 4.33.0 |
| Integration mode | `REQUIRE_POSTGRES_INTEGRATION=1` |
| R6 Go v2 database | `localhost:55432/env_db` |

The service implementation keeps the public HTTP/domain field `reason` for
compatibility while the PostgreSQL adapter reads and writes
`training_environment.maintenance.reason_detail`. The repository tests also
verify the transactional event in `training_environment.outbox`. CONTRACT must
not be executed against the old service consumer; the intended order is Go v2
review and test, confirmation that no active consumer still requires `reason`,
then the isolated CONTRACT changelog and its rollback.

### 11.2 EXPAND/BACKFILL and service compatibility

The disposable laboratory used the real domain table
`training_environment.maintenance`. SQL 964 added `reason_detail` while
retaining `reason`; SQL 965 populated the new column from the legacy data.
The null-safe divergence check after the preparation phase returned:

```text
rows | reason_detail_non_null | divergences
-----+------------------------+------------
1    | 1                      | 0
```

The broader four-laboratory DB run used legacy seed data, exercised compatible
writes, and reported 4 initial rows, 6 rows after compatibility writes, 5
non-null migrated values, and 0 divergences before CONTRACT in each disposable
lab (`develop`, `qa`, `staging`, and simulated `main`). These names identify
local Docker laboratories only.

### 11.3 Go v2 integration command and complete output

The command executed against PostgreSQL 16 in Docker was:

```powershell
$env:TEST_DATABASE_URL = "postgres://postgres:postgres@localhost:55432/env_db?sslmode=disable"
$env:REQUIRE_POSTGRES_INTEGRATION = "1"
go test -count=1 -v ./internal/adapter/out/persistence -run 'TestPostgresMaintenanceRepository_'
```

Execution metadata: UTC `2026-10-23T12:28:42.4836490Z`, Docker Engine
`29.9.1`, container `90a775a89288d39ea9a5e2b41598024f0e1998ed1264c306613ac021aaeae6cb`.

```text
=== RUN   TestPostgresMaintenanceRepository_HU006_CRUDFiltersAndTransactionalOutbox
--- PASS: TestPostgresMaintenanceRepository_HU006_CRUDFiltersAndTransactionalOutbox (0.07s)
=== RUN   TestPostgresMaintenanceRepository_HU018_TemporalValidation
--- PASS: TestPostgresMaintenanceRepository_HU018_TemporalValidation (0.05s)
PASS
ok  github.com/code-sena/design-software-training-environment-service/internal/adapter/out/persistence  1.149s
```

This proves R6(c) in the local scope: the previous-compatible consumer path
and the new persistence path were exercised during EXPAND/BACKFILL. HU006
also verifies the outbox event. It does not claim a shared-environment or
production deployment.

### 11.4 CONTRACT 966 and rollback output

After the divergence check, the isolated CONTRACT SQL 966 was executed. The
observed structure and data were:

```text
column_name   | is_nullable
--------------+------------
reason_detail | YES

rows | reason_detail_non_null
-----+-----------------------
5    | 2
```

The current SQL removes `reason` but does not apply `NOT NULL` to
`reason_detail`; therefore this report makes no stronger claim. The CONTRACT
operation is intentionally isolated in `changelog/changelog-r6-contract.yaml`
and is not part of ordinary service startup.

The rollback then restored the legacy column and synchronization objects. The
post-rollback inspection returned:

```text
column_name   | is_nullable
--------------+------------
reason        | YES
reason_detail | YES

divergences
-----------
0
```

The four-laboratory DB evidence reports PASS 4/4 for CONTRACT rollback and for
the subsequent EXPAND/BACKFILL rollback, with data-preservation checks. This
is valid evidence for isolated Docker laboratories; it is not authorization
to execute a destructive cutover in an institutional database.

### 11.5 HU019 correction and final persistence-suite result

The first complete persistence-package run was not presented as PASS. It
failed in the unrelated reservation-index test because a clean PostgreSQL
database did not contain the fixture indexes and exclusion constraint:

```text
=== RUN   TestPostgresReservationRepository_HU019_IndexesFiltersAndExclusion
    postgres_reservation_indexes_hu019_test.go:41: expected exactly one idx_reservation_requester_created_at index, got 0
--- FAIL: TestPostgresReservationRepository_HU019_IndexesFiltersAndExclusion (0.01s)
FAIL
```

The correction added the idempotent `prepareHU019IndexFixture`, creating the
four expected indexes, `excl_reservation_no_overlap`, and the minimum tables
needed by the scenario. It changes only test preparation, not production
logic.

The same command was then repeated:

```powershell
$env:TEST_DATABASE_URL = "postgres://postgres:postgres@localhost:5432/env_db?sslmode=disable"
$env:REQUIRE_POSTGRES_INTEGRATION = "1"
go test -count=1 -v ./internal/adapter/out/persistence
```

Authoritative final result:

```text
=== RUN   TestPostgresMaintenanceRepository_HU006_CRUDFiltersAndTransactionalOutbox
--- PASS: TestPostgresMaintenanceRepository_HU006_CRUDFiltersAndTransactionalOutbox (0.06s)
=== RUN   TestPostgresMaintenanceRepository_HU018_TemporalValidation
--- PASS: TestPostgresMaintenanceRepository_HU018_TemporalValidation (0.04s)
=== RUN   TestPostgresReservationRepository_HU019_IndexesFiltersAndExclusion
--- PASS: TestPostgresReservationRepository_HU019_IndexesFiltersAndExclusion (0.04s)
=== RUN   TestPostgresReservationRepository_HU008_QueryDetailFiltersScopeAndIndexes
--- PASS: TestPostgresReservationRepository_HU008_QueryDetailFiltersScopeAndIndexes (0.04s)
=== RUN   TestPostgresReservationRepository_HU007_RealExclusionConstraintAndSQLStateMapping
--- PASS: TestPostgresReservationRepository_HU007_RealExclusionConstraintAndSQLStateMapping (0.04s)
=== RUN   TestPostgresReservationRepository_HU009_UpdateAndCancel
--- PASS: TestPostgresReservationRepository_HU009_UpdateAndCancel (0.03s)
PASS
ok  github.com/code-sena/design-software-training-environment-service/internal/adapter/out/persistence  1.829s

Resumen: 16 pruebas PASS; 0 fallos.
```

The historical failing output is retained here as diagnosis and audit trail;
the post-correction run is the authoritative result for the final review.

### 11.6 Consolidated evidence conclusion

The integrated evidence supports the following technical conclusion:

- EXPAND, BACKFILL, CONTRACT and rollback were exercised on a real domain
  table in disposable PostgreSQL Docker laboratories.
- Go v2 was published on `feat/r6-service-reason-detail` and passed the
  targeted maintenance integration tests against EXPAND/BACKFILL.
- The complete persistence package finished with 16 PASS and 0 FAIL after the
  independent HU019 fixture correction.
- CONTRACT leaves `reason_detail` nullable in the current implementation; no
  undocumented `NOT NULL` guarantee is made.
- The four Docker labels are local laboratories, not institutional shared
  environments.

Therefore the technical R6 result remains **PASS in the documented local
laboratory scope**. The only remaining decision is formal review by the
responsible architect and the corresponding institutional authorization before
declaring definitive closure.

## References

- [ADR-017 — Training Environment schema evolution](../05-architecture/decisions/records/ADR-017-training-environment-r6-schema-evolution.md)
- [Training Environment service R6 report](../09-microservices/services/04-training-environment-service/r6-schema-evolution.md)
- [Training Environment service README](../09-microservices/services/04-training-environment-service/README.md)
- [Training Environment DB PR #134](https://github.com/code-sena/design-software-training-environment-db/pull/134)
