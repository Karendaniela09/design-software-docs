# Technical Report R6 — TEXT to JSONB Migration

**Project:** Code-SENA  
**Challenge:** R6 — EXPAND → BACKFILL → CONTRACT → ROLLBACK  
**Field:** `monitoring.improvement_plan.specific_actions`  
**Owner:** Nicolas Estid Ruiz Sastoque  
**Last updated:** October 21, 2026

## 1. Executive summary

R6 implements a progressive `TEXT` to `JSONB` migration for `monitoring.improvement_plan.specific_actions`, preserving compatibility during the transition and separating CONTRACT into an independent operational changelog.

The implementation is distributed across four repositories:

- `design-software-monitoring-db`: changesets, SQL, and rollbacks.
- `design-software-monitoring-service`: persistence compatibility, serialization, and tests.
- `design-software-docker-infra`: Liquibase service with the `r6-contract` profile.
- `design-software-docs`: ADR, data model, decisions, and runbook.

The previous report was removed from `design-software-monitoring-db/docs` because it was duplicated and outdated. The official documentation remains in `design-software-docs`; personal evidence is stored under `docs/plan-mejoramiento-R6`.

## 2. Versions and commits

| Repository | Branch | R6 commits | Final commit |
|---|---|---:|---|
| `design-software-monitoring-db` | `hu-r6-nicolas-dev` | 3 | `c9bac2e` |
| `design-software-monitoring-service` | `hu-r6-nicolas-dev` | 2 | `90de34a` |
| `design-software-docker-infra` | `hu-r6-nicolas-dev` | 1 | `8f75bbd` |
| `design-software-docs` | `feat/r6-documentation` | 2 | `1d05bd2` |

Relevant commits include the initial EXPAND/BACKFILL/CONTRACT/ROLLBACK implementation (`3dc359f`), service compatibility and tests (`68f6edb`), the isolated PostgreSQL CI job (`90de34a`), the Liquibase `r6-contract` profile (`8f75bbd`), documentation and ADR (`0641156`), and QA corrections (`1d05bd2`).

## 3. Monitoring DB implementation

### EXPAND

Changeset `r6-monitoring-expand-specific-actions-v2-991` adds nullable `specific_actions_v2 JSONB`, keeps `specific_actions TEXT NOT NULL`, validates the table with preconditions, prevents duplicate-column creation, and provides a rollback that removes the v2 column. Main file: `01_ddl/04_alter/r6_expand_specific_actions_v2.sql`.

### BACKFILL

Changeset `r6-monitoring-backfill-specific-actions-v2-992` updates only rows where `specific_actions_v2 IS NULL`, preserves the original TEXT, and produces:

```json
{
  "version": 1,
  "actions": [
    { "text": "original value" }
  ]
}
```

The conversion preserves Unicode, quotation marks, special characters, empty strings, and line breaks. The supported representation contains one action.

### Final synchronization

`01_ddl/04_alter/r6_sync_specific_actions_v2.sql` was added in `c9bac2e`. It is transactional and idempotent, reports discrepancies before and after execution, updates only compatible version-1 documents with one action, and does not overwrite null, malformed, or unsupported-version documents. It must run after old writers are stopped and before CONTRACT.

### CONTRACT

Changeset `r6-monitoring-contract-specific-actions-v2-993` runs from `changelog/changelog-contract.yaml` with context `r6-contract`. It verifies that there are no nulls, invalid documents, or TEXT/JSONB differences; removes the TEXT column; renames `specific_actions_v2` to `specific_actions`; and sets `specific_actions JSONB NOT NULL`.

CONTRACT is not executed during conventional startup and requires authorization, backup, and operational validation.

### ROLLBACK

The CONTRACT rollback reconstructs `specific_actions TEXT NOT NULL` from `actions[0].text`, keeps `specific_actions_v2 JSONB NULL`, and preserves compatible JSONB documents. Full reconstruction is not guaranteed for multiple actions, future versions, additional fields, or unsupported JSONB documents.

## 4. Monitoring Service compatibility

The service supports all three states:

| State | Behavior |
|---|---|
| Before EXPAND | Read and write TEXT. |
| During EXPAND/BACKFILL | TEXT/JSONB coexistence and synchronization. |
| After CONTRACT | Read and write JSONB. |

The HTTP contract keeps `specific_actions` as a string. Storage migration does not change OpenAPI to an object because the backend continues to serialize the value as text.

Related tests:

- `tests/test_specific_actions_compat.py`
- `tests/test_router_serialization.py`
- `tests/test_r6_postgres_integration.py`
- `tests/test_r6_http_postgres_integration.py`
- `tests/test_monitoring_http_contract.py`

The isolated PostgreSQL CI workflow was prepared in `90de34a`; its remote result must be attached when available and is not claimed as an approved result in this report.

## 5. Executed evidence

Complete evidence is under [`docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6`](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6). Four ephemeral isolated PostgreSQL databases were used: DEV, QA, STAGING, and simulated PROD. None was a shared or real production database.

The four synchronization outputs reported:

```text
discrepancies_before = 0
UPDATE 0
discrepancies_after = 0
final_discrepancies = 0
```

Each environment completed CONTRACT and `rollback-count 1` successfully. The post-rollback result was:

```text
specific_actions    TEXT NOT NULL
specific_actions_v2 JSONB NULL
plans               3
populated_jsonb     3
inconsistencies     0
```

Synthetic data included normal text, Unicode, and line breaks. Normalized TEXT and JSONB fingerprints matched in all four isolated environments.

## 6. Results and limitations

Observed results include successful Liquibase validation and update, one approved real-PostgreSQL R6 SQL integration, one approved HTTP/PostgreSQL integration, a general Monitoring Service suite with 34 passed and 8 skipped, successful Ruff validation, and successful Python compilation.

New evidence validated EXPAND/BACKFILL on four ephemeral databases, idempotent synchronization, CONTRACT with Liquibase 4.33.0, `rollback-count 1`, PostgreSQL structure/nullability/count/equivalence/fingerprint queries, Markdown links, and removal of temporary containers and networks.

Open items:

- Remote CI result for the service.
- Repetition in authorized operational environments.
- Evidence of a restored backup.
- Validation with multiple actions or future JSONB versions.

## 7. R6 compliance

| Requirement | Evidence | Status |
|---|---|---|
| R6(a) EXPAND/CONTRACT | Changesets, preconditions, independent changelog, and Liquibase logs | Met in isolated databases; operational promotion pending |
| R6(b) Data and BACKFILL | Three synthetic plans per database, backfill, and final synchronization | Met in isolated databases |
| R6(c) Compatibility | TEXT/JSONB adapter, HTTP serialization, and prepared service tests | Partial until CI and authorized environments are executed |
| R6(d) ROLLBACK in four environments | Four documented CONTRACT → ROLLBACK cycles | Met for ephemeral databases; operational validation pending |

## 8. Environment traceability

| Environment | Database | CONTRACT | ROLLBACK | Final verification |
|---|---|---|---|---|
| DEV | `r6_dev_db` | `specific_actions` became `JSONB NOT NULL`; 3 plans and 3 JSONB documents | Successful with `rollback-count 1` | TEXT restored, JSONB retained, 0 inconsistencies |
| QA | `r6_qa_db` | `specific_actions` became `JSONB NOT NULL`; 3 plans and 3 JSONB documents | Successful with `rollback-count 1` | TEXT restored, JSONB retained, 0 inconsistencies |
| STAGING | `r6_staging_db` | `specific_actions` became `JSONB NOT NULL`; 3 plans and 3 JSONB documents | Successful with `rollback-count 1` | TEXT restored, JSONB retained, 0 inconsistencies |
| Simulated PROD | `r6_prod_sim_db` | `specific_actions` became `JSONB NOT NULL`; 3 plans and 3 JSONB documents | Successful with `rollback-count 1` | TEXT restored, JSONB retained, 0 inconsistencies |

All environments produced the normalized fingerprint `a65ed94bf0bc33bbddc036be663bc1e4` after rollback. Complete Liquibase and PostgreSQL outputs remain in the linked evidence folders.

## 9. QA corrections and evidence files

| Finding | Correction |
|---|---|
| Changeset identity | R6 Liquibase authors were aligned with the expected DB history (`codex`) in `c9bac2e`. |
| Incorrect rollback nullability | Versioned changeset execution confirmed `specific_actions_v2 JSONB NULL` after `rollback-count 1`. |
| Sequence not demonstrated | Separate pre-CONTRACT, CONTRACT, post-CONTRACT, rollback, and final verification outputs were preserved. |
| Pre-CONTRACT discrepancies | `r6_sync_specific_actions_v2.sql` ran in all four isolated environments; final discrepancies were zero. |
| Duplicate documentation | `design-software-monitoring-db/docs/informe-tecnico-r6.md` was removed; official documentation remains here. |
| Opt-in CI | An isolated PostgreSQL job was added to the service workflow; the remote result remains pending. |

Evidence folders:

- [Liquibase identity](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/01-liquibase-identidad)
- [Final synchronization](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/02-sincronizacion-final)
- [DEV rollback](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/04-rollback-dev)
- [QA rollback](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/04-rollback-qa)
- [STAGING rollback](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/04-rollback-staging)
- [Simulated PROD rollback](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/04-rollback-prod-simulada)

## 10. Technical references and scope statement

- [DB PR #62](https://github.com/code-sena/design-software-monitoring-db/pull/62)
- [Service PR #8](https://github.com/code-sena/design-software-monitoring-service/pull/8)
- [Infrastructure PR #43](https://github.com/code-sena/design-software-docker-infra/pull/43)

This report reflects the implementation and evidence available on October 21, 2026. It does not claim tests, deployments, or results that are not supported by the linked logs. The new evidence covers three synthetic records per database, one JSONB version, and one action per document; it does not cover additional conditions.
