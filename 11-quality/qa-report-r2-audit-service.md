# QA Report — R2 Audit Service Performance and Data

**Owner:** Freinier Cardona  
**Training group:** ADSO 3145555  
**Domain:** Audit  
**Status:** PASS — evidence review completed  
**Verification date:** 2026-10-22

## 1. Objective

Verify that the Audit read API meets the R2 performance target after adding
three reversible PostgreSQL indexes, while preserving IAM authentication,
RBAC permissions, data scope and the append-only audit model.

The detailed developer execution report is preserved at
[`r2-audit-rendimiento-datos.md`](./r2-audit-rendimiento-datos.md). This QA
report provides the standardized test matrix and acceptance gate.

## 2. Traceability

| Artifact | Branch / reference |
|---|---|
| `audit-service` | `fix/audit-r2-performance-data`, commit `19529e8` |
| `audit-db` | `fix/audit-r2-performance-data`, commit `2e13a4b` |
| `docker-infra` | `fix/audit-r2-performance-data`, commit `6316f88` |
| `docs` | `fix/audit-r2-performance-data` |
| IAM service | `develop`, commit `6987e0f` |
| IAM database | `develop`, commit `a1e01a4` |
| Global architecture decision | [ADR-016](../05-architecture/decisions/records/ADR-016-audit-r2-performance-data.md) |
| Service design note | [R2 performance and data note](../09-microservices/services/09-audit-service/r2-performance-data.md) |

## 3. Automated test matrix

| Test ID | Test / command | Endpoint or control | Result |
|---|---|---|---|
| TC-R2-001 | k6 `before`, 50 VUs for 5 minutes | List, detail and export mix without R2 indexes | PASS as baseline; p95 1,075.20 ms intentionally fails target |
| TC-R2-002 | k6 `after`, 50 VUs for 5 minutes | List, detail and export mix with R2 indexes | PASS; p95 15.63 ms, exit code 0 |
| TC-R2-003 | k6 checks | `GET /api/v1/audit-records` | PASS; all list checks returned 200 |
| TC-R2-004 | k6 checks | `GET /api/v1/audit-records/{id}` | PASS; all detail checks returned 200 |
| TC-R2-005 | k6 checks | `GET /api/v1/audit-records/export` | PASS; all export checks returned 200 |
| TC-R2-006 | `EXPLAIN (ANALYZE, BUFFERS)` before/after | Three measured SQL paths | PASS; both plan sets are versioned |
| TC-R2-007 | Liquibase update | `r2-audit-performance-query-indexes` | PASS; three indexes applied |
| TC-R2-008 | Liquibase `rollback-count 1` | Three R2 index objects | PASS; verification is `t | t | t` |
| TC-R2-009 | k6 evidence sanitization | `setup_data`, Bearer token and credentials | PASS; setup data removed before retention |
| TC-R2-010 | Compose configuration | IAM, PostgreSQL, RabbitMQ, audit API and k6 | PASS; configuration parses and isolated project is used |

## 4. Performance acceptance gate

| Criterion | Required | Observed `after` | Status |
|---|---:|---:|---|
| Virtual users | 50 | 50 | PASS |
| Duration | 5 minutes | 5 minutes | PASS |
| HTTP p95 | < 300 ms | 15.63 ms | PASS |
| Audit request error rate | < 1% | 0.00% | PASS |
| Failed checks | 0 | 0 of 265,543 | PASS |
| k6 exit code | 0 | 0 | PASS |

The baseline is expected to fail only the p95 target, demonstrating the
performance problem that R2 addresses. It recorded 0% request errors and zero
failed endpoint checks.

## 5. Data and rollback gate

- Fixture size: 200,002 records.
- Database: PostgreSQL 16.15.
- Query plans: three before and three after, with `ANALYZE, BUFFERS`.
- Changeset: `r2-audit-performance-query-indexes`.
- Indexes: exactly three, aligned to the measured filters and ordering.
- Rollback: executed through Liquibase, not manually.
- Rollback proof: all three `to_regclass(...) IS NULL` checks returned true.
- Final state: changeset reapplied after the rollback proof.

## 6. Security and quality checklist

| Control | Verification | Status |
|---|---|---|
| Real IAM authentication | Login obtains the token through the contractual IAM endpoint | PASS |
| JWT integrity | IAM emits RS256 and audit-service validates JWKS | PASS |
| Authorization | `AUDIT_LOG_VIEW` and `AUDIT_EXPORT` remain required | PASS |
| No bypass or mock token | No fabricated token or anonymous mode in k6 | PASS |
| Secret handling | `.env` files are ignored and setup data is removed | PASS |
| Scope preservation | Acceptance identity uses `GLOBAL`; no route or scope bypass added | PASS |
| Append-only model | R2 changes only query indexes and rollback metadata | PASS |
| Reproducibility | Compose project, fixture, SQL plans and scripts are identified | PASS |

## 7. Limitations

- Results come from one isolated Docker Desktop host and do not represent
  production network or storage latency.
- The workload uses a controlled 200,002-row fixture.
- The aggregate p95 combines list, detail and export requests; independent
  endpoint percentiles are not published.
- The acceptance identity uses `GLOBAL`; a separate k6 run for
  `TRAINING_CENTER` scope is not included.
- The optional IAM-to-Actors `active-ficha` path is not exercised for the
  `SYSTEM_ADMIN` test identity.

## 8. QA conclusion

R2 passes the documented performance, data-plan, rollback, authentication and
evidence gates. The optimized authenticated run is below the 300 ms p95 target
with zero request errors, zero failed checks and exit code 0. The evidence is
ready for architectural and QA review.

