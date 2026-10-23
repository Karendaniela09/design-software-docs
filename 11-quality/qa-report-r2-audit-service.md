# R2 — Audit Service Performance and Data Technical Report

> Status: 🟢 Verified | Last updated: 2026-10-22
> Author: Freinier Cardona | Team: Audit / ADSO 3145555

## 1. Context

This report documents the implementation and reproducible evidence for R2 of
the improvement plan. `design-software-audit-service` contains the k6 scenario
and execution scripts, `design-software-audit-db` contains the Liquibase
migration, and `design-software-docker-infra` orchestrates the local
environment. Credentials, tokens and `.env` files are not versioned.

## 2. Scope

The validation covers the contracted read endpoints only:

- `GET /api/v1/audit-records` — list;
- `GET /api/v1/audit-records/{id}` — detail;
- `GET /api/v1/audit-records/export` — export.

IAM authentication, `AUDIT_LOG_VIEW`, `AUDIT_EXPORT` and training-center scope
remain enabled. No routes, authorization bypasses or production data are
introduced. The disposable `SYSTEM_ADMIN` identity used on 2026-10-22
received a real RS256 JWT through `POST /api/v1/auth/login`; no token was
fabricated.

## 3. Deliverables and traceability

| R2 criterion | Versioned deliverable | Verification status |
|---|---|---|
| k6 load: 50 VUs, 5 minutes, p95 < 300 ms, errors < 1% | `performance/k6/audit-query.js`, `scripts/run-r2-k6.ps1`, `performance/results/{before,after}` | PASS: after p95 15.63 ms, 0% errors, 265,542 iterations, 100% checks and exit code 0. |
| Three `EXPLAIN (ANALYZE, BUFFERS)` plans before and after | `performance/sql/r2-explain.sql`, `performance/sql/r2-seed.sql`, `scripts/run-r2-data.ps1` | PASS: PostgreSQL 16 with an isolated 200,002-row fixture. |
| Liquibase indexes with rollback | Changeset `r2-audit-performance-query-indexes` and rollback SQL in `audit-db` | PASS: `rollback-count 1` executed and the three R2 indexes were absent afterward. |
| Comparative report | This report and [ADR-016](../05-architecture/decisions/records/ADR-016-audit-r2-performance-data.md) | PASS: before/after JSON and Markdown summaries are versioned separately. |

## 4. Environment validation

On 2026-10-21, an isolated Compose project was started with PostgreSQL,
RabbitMQ, the 19 audit-db migrations, technical roles and both audit-service
processes. `audit-query-api:8081/ready` and `audit-worker:8082/ready`
returned `200`; the worker maintained an active RabbitMQ connection.

### 4.1 Initial authenticated attempt — 2026-10-21

The harness stopped before k6 because IAM did not expose JWKS (`000` when
requesting `/api/v1/auth/.well-known/jwks.json`). The local technical
principal `design_software_app` was created only in the temporary database.
The next startup failed while resolving `E2E_IAM_MTLS_PASSWORD` in
`actorsActiveFichaClient`; the rebuilt Compose image retained that placeholder
although it was absent from the inspected IAM checkout.

No `k6-summary.json` was generated in this attempt, no 50-VU five-minute run
was claimed, and no fabricated tokens, mocks or authorization bypasses were
used.

### 4.2 Final authenticated run — 2026-10-22

The blocker was resolved in isolated Compose project `audit-r2-final`. Real
IAM migrations were applied and a disposable account with Audit features was
created. For `SYSTEM_ADMIN`, the optional `active-ficha` Actors integration
was empty in the test runtime because the contract queries it only for
identities that are exclusively `LEARNER`. The RSA key, passwords and token
were ephemeral and were neither printed nor versioned.

Both runs used exactly 50 VUs for five minutes, the same 200,002-row fixture
and the same list/detail/export mix:

| Phase | HTTP p95 | Audit errors | Checks | Iterations | k6 exit code | Result |
|---|---:|---:|---:|---:|---:|---|
| `before` (without the three R2 indexes) | 1,075.20 ms | 0.00% | 17,964 / 17,964 | 17,963 | 99 | Fails p95 target |
| `after` (with the three R2 indexes) | 15.63 ms | 0.00% | 265,543 / 265,543 | 265,542 | 0 | PASS |

The p95 decreased by 98.55% and completed iterations increased 14.78 times.
All endpoints returned `200` in both phases.

## 5. Data results

Measurements were repeated on 2026-10-22 with PostgreSQL 16 and an isolated
Compose project.

| Query | Before | After | Observed effect |
|---|---|---|---|
| List by training center and event type | Incremental sort; 0.276 ms | Ordered index scan; 0.293 ms | Both are sub-millisecond; the point difference is execution noise. |
| List by source service | Parallel sequential scan + sort; 69.563 ms | Ordered index scan; 0.217 ms | 99.69% faster; full scan and sort removed. |
| Center export (160,002 rows) | Incremental sort; 136.727 ms | Ordered index scan; 84.088 ms | 38.50% faster; incremental sort removed. |

After `rollback-count 1`, the `to_regclass` check returned `t | t | t`,
confirming that the three R2 indexes were absent. The script reapplies the
changeset and finishes with the complete schema.

## 6. Closing-run identification

- Local window: 2026-10-22, `America/Bogota`.
- PostgreSQL 16.15; Docker 29.7.2; Docker Compose 5.5.0; k6 0.54.0.
- `audit-service`: `fix/audit-r2-performance-data` at `19529e8`.
- `audit-db`: `fix/audit-r2-performance-data` at `2e13a4b`.
- `docker-infra`: `fix/audit-r2-performance-data` at `6316f88`.
- `docs`: `fix/audit-r2-performance-data`.
- `iam-service`: `develop` at `6987e0f`; `iam-db`: `develop` at `a1e01a4`.

## 7. Technical implementation

1. `performance/k6/audit-query.js` defines a `constant-vus` scenario with 50
   VUs for five minutes. `setup()` authenticates through IAM and does not
   fabricate JWTs or disable security.
2. The token remains in memory. Requests use a 70% list, 20% detail and 10%
   export mix, with HTTP 200 checks on every request.
3. Thresholds are `http_req_duration: p(95)<300` and
   `audit_request_errors: rate<0.01`. Acceptance also requires zero failed
   checks and a zero k6 exit code.
4. `scripts/run-r2-data.ps1` creates an isolated Compose project, applies the
   baseline, inserts 200,002 records, captures three
   `EXPLAIN (ANALYZE, BUFFERS)` plans, applies R2, verifies rollback and
   restores the complete schema.
5. `scripts/run-r2-k6.ps1` creates separate `before` and `after` result
   directories, stores sanitized JSON, records `r2_validation` and writes
   `summary.md`.
6. `setup_data` is removed before evidence is retained so the Bearer token
   cannot be versioned.

## 8. Exact reproduction

Requirements: Docker Desktop, Windows PowerShell 5.1 or PowerShell 7, the
sibling repositories and a disposable IAM identity with
`AUDIT_LOG_VIEW` and `AUDIT_EXPORT`.

Create local files from the templates and do not commit them:

```powershell
Copy-Item .\design-software-audit-service\.env.example `
  .\design-software-audit-service\.env
Copy-Item .\design-software-audit-service\.env.worker.example `
  .\design-software-audit-service\.env.worker
Copy-Item .\docker-infra\design-software-docker-infra\.env.example `
  .\docker-infra\design-software-docker-infra\.env
```

Set the infrastructure placeholders and disposable
`AUDIT_LOAD_EMAIL`/`AUDIT_LOAD_PASSWORD` values. The JWT is obtained by
`setup()` from IAM and is not configured or stored.

From `design-software-audit-service`, run:

```powershell
.\scripts\run-r2-data.ps1 `
  -InfraDirectory ..\docker-infra\design-software-docker-infra `
  -EnvFile ..\docker-infra\design-software-docker-infra\.env `
  -ProjectName audit-r2
.\scripts\run-r2-k6.ps1 -Phase before
.\scripts\run-r2-k6.ps1 -Phase after
```

Credentials are read from the ignored local `.env`; this is not anonymous
access. IAM, JWKS, issuer, features and the required permissions remain
mandatory. Automation does not create IAM users or generate credentials.

## 9. Security and data controls

- Real IAM authentication and RS256/JWKS validation remain enabled.
- `AUDIT_LOG_VIEW` and `AUDIT_EXPORT` remain required.
- No fabricated JWT, mock token, anonymous mode or authorization bypass was
  used.
- Secrets remain in ignored local `.env` files and are removed from retained
  k6 evidence.
- The append-only audit model is unchanged; R2 adds only query indexes and
  rollback metadata.
- `GLOBAL` scope was used only for the disposable acceptance identity.

## 10. Evidence, limitations and conclusion

The evidence was produced on one isolated Docker Desktop host with a
controlled 200,002-row fixture. Aggregate p95 combines list, detail and
export requests; independent endpoint percentiles are not published. A
separate `TRAINING_CENTER` scope run is not included, and the optional
IAM-to-Actors `active-ficha` path is not exercised for `SYSTEM_ADMIN`.

R2 is verified. The authenticated `after` run meets the five-minute, 50-VU
target with 15.63 ms HTTP p95, 0.00% request errors, zero failed checks and
k6 exit code 0. The three reversible indexes improve the measured query plans
without changing routes, permissions, scope or the append-only model.

The architectural decision is [ADR-016](../05-architecture/decisions/records/ADR-016-audit-r2-performance-data.md).
