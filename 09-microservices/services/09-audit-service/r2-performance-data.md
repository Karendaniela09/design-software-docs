# R2 Performance and Data Engineering Note

**Owner:** Freinier Cardona  
**Domain:** Audit  
**Service:** `audit-service`  
**Status:** ACCEPTED FOR QA REVIEW  
**Verification date:** 2026-10-22

## Purpose

This note defines the service-level implementation and evidence for R2. It is
the companion to [ADR-016 — Reproducible Audit Query Performance](../../../05-architecture/decisions/records/ADR-016-audit-r2-performance-data.md)
and to the preserved developer report
[`r2-audit-rendimiento-datos.md`](../../../11-quality/r2-audit-rendimiento-datos.md).

The developer report remains the source of the detailed execution narrative.
This note organizes the service design, data flow, controls and evidence
according to the documentation standard without replacing that report.

## Scope and non-goals

R2 measures only these authenticated read endpoints:

- `GET /api/v1/audit-records`;
- `GET /api/v1/audit-records/{id}`;
- `GET /api/v1/audit-records/export`.

The change does not add routes, change authorization, bypass IAM, change the
append-only model or measure worker ingestion throughput. The load identity
uses `SYSTEM_ADMIN` with `AUDIT_LOG_VIEW:GLOBAL` and `AUDIT_EXPORT:GLOBAL` in a
disposable local database.

## Logical data flow

```text
Disposable IAM account
        |
        | POST /api/v1/auth/login -> RS256 access token
        v
      IAM API ---- JWKS --------------------+
        |                                   |
        | Bearer token                      | signature and claims
        v                                   v
      k6 load generator --> audit-query-api --> PostgreSQL audit.audit_record
          |                    |                    |
          | 70% list           | read-only          | three R2 indexes
          | 20% detail         | RBAC + scope       | EXPLAIN evidence
          | 10% export         v                    v
          +--------------> sanitized results   rollback verification
```

The isolated Compose project also starts RabbitMQ and `audit-worker` so the
readiness contract is checked, but the R2 load targets only the read API.

## Implementation decision

The database change adds exactly three ordered composite indexes:

1. `(training_center_id, event_type, received_at DESC, id DESC)`;
2. `(source_service, received_at DESC, id DESC)`;
3. `(training_center_id, received_at DESC, id DESC)`.

The changeset is `r2-audit-performance-query-indexes` in `audit-db`. Its
rollback drops all three objects. No query route or permission was changed.

The k6 scenario uses a `constant-vus` executor with exactly 50 VUs for 5
minutes. It logs into IAM once in `setup()`, keeps the token in memory, checks
HTTP 200 for every request and writes sanitized evidence. The acceptance gate
requires p95 below 300 ms, audit request error rate below 1%, zero failed
checks and k6 exit code 0.

## Security and data controls

| Control | Implementation |
|---|---|
| Authentication | Real IAM login and RS256/JWKS validation; no fabricated JWTs |
| Authorization | `AUDIT_LOG_VIEW` for list/detail and `AUDIT_EXPORT` for export |
| Scope | `GLOBAL` in the disposable acceptance identity |
| Credentials | Local ignored `.env` files only; never command-line or committed |
| Evidence sanitization | `setup_data` is removed from k6 JSON before retention |
| Data isolation | PostgreSQL fixture in disposable Compose project `audit-r2` |
| Write protection | R2 exercises read endpoints; audit records remain append-only |
| Rollback | Liquibase `rollback-count 1` and explicit `to_regclass` proof |

## Evidence inventory

| Evidence | Location | Required result |
|---|---|---|
| k6 baseline | `performance/results/before/` | p95 failure is expected; checks and error rate remain valid |
| k6 optimized run | `performance/results/after/` | p95 < 300 ms, errors < 1%, zero failed checks, exit 0 |
| SQL plans before | `performance/results/explain-before.txt` | three plans without R2 indexes |
| SQL plans after | `performance/results/explain-after.txt` | the same three plans with R2 indexes |
| Fixture confirmation | `performance/results/seed.txt` | 200,002 inserted records |
| Rollback proof | `performance/results/rollback-verification.txt` | `t | t | t` |

The exact metrics and execution trace remain in the developer report. The
versioned k6 JSON also contains `r2_validation`, including exit code and the
individual acceptance criteria.

## Reproduction entry points

From `audit-service`:

```powershell
.\scripts\run-r2-data.ps1 `
  -InfraDirectory ..\design-software-docker-infra `
  -EnvFile ..\design-software-docker-infra\.env `
  -ProjectName audit-r2

.\scripts\run-r2-k6.ps1 -Phase before `
  -InfraDirectory ..\design-software-docker-infra `
  -EnvFile ..\design-software-docker-infra\.env `
  -ProjectName audit-r2

.\scripts\run-r2-k6.ps1 -Phase after `
  -InfraDirectory ..\design-software-docker-infra `
  -EnvFile ..\design-software-docker-infra\.env `
  -ProjectName audit-r2
```

The developer must review command output, exit code and all generated files. A
pre-existing result file is not evidence of a new execution.

