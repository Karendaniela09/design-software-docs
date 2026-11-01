# HU-INT-REF-002 validation evidence

> Status: In review | Last updated: 2026-10-25
> Author/team: Reference Data team

Issue: [docs#295](https://github.com/code-sena/design-software-docs/issues/295).
Release decision: technical implementation validated; story remains open pending criterion 6 and independent QA review.

## Context

Validation uses actual PostgreSQL, IAM JWT/JWKS, RabbitMQ, the canonical Traefik routes, and production builds of the shell and Reference Data remote. No browser routes or business API responses are mocked. The initial run provisioned a clean, isolated database; subsequent runs resumed only the same disposable project. Fixture credentials, signing keys and raw reports are excluded from version control.

## Content

### Acceptance matrix

| Criterion | Technical result | Evidence |
|---|---|---|
| 1: six-resource list/get | Pass | Real API POST, list and GET by UUID for every resource; browser reads persisted geography, centers and units. |
| 2: parent filters and complete selectors | Pass | API checks all five parent filter names; browser chains location UUIDs and clears descendants; 105 deterministic parent fixtures exceed one API page; form choices include the last page. |
| 3: POST/PUT, constraints and persistence | Pass | 201 create and 200 edit for all six resources; browser reload preserves edited names; missing parents, empty/oversized names and phone length are validated; 100 Unicode characters are accepted at a 100-character limit. |
| 4: UUID and unit types | Pass | Parent payloads contain real UUIDs; ACADEMIC, ADMINISTRATIVE and MIXED persist; lowercase academic is rejected. |
| 5: DELETE and status filter | Pass | All six API deletes return empty 204 and GET preserves is_active=false; active/inactive API filters work; browser verifies inactive municipality, unit and center. |
| 6: approved blocking usages | Pending domain decision | No approved blocking-usage matrix or consumer usage-check contract was supplied. No veto was invented. Existing soft-deactivation remains; this criterion cannot be approved yet. |
| 7: distinct errors | Pass | Shared envelope codes BAD_REQUEST (400), NOT_FOUND (404), CONFLICT (409), IMMUTABLE_FIELD (409), UNAUTHENTICATED (401) and FORBIDDEN (403); browser retains the form and explains a duplicate center code. |
| 8: VIEW versus MANAGE | Pass | A real read-only IAM session lists all six resources; direct POST/PUT/DELETE requests return 403; browser permits consultation and withholds/disables management controls. |
| 9: durable center-created event | Pass against available messaging implementation | Broker outage still permits POST 201 with one committed recoverable outbox event; broker recovery plus backend restart delivers it; three deliberate redeliveries produce one inbox row and one projection effect. Formal acceptance of HU-INT-REF-004 is a separate dependency. |

### Executed checks

- Backend `go test ./...`: passed. Guarded broker/database tests are executed explicitly by the integration runner, rather than counted from their default skipped invocation.
- MFE `npm run typecheck`, `npm run lint`, `npm run check:types`, `npm test`: passed; 19 test files, 78 tests.
- Shell `npm run typecheck:e2e` and `npm run lint`: passed.
- Production shell/MFE Docker builds: passed; pinned inputs were hashed from committed Git blobs with LF line endings, and checked again inside the Linux build.
- Dedicated Playwright suite: four passed, zero skipped, zero flaky. It checks all-resource API CRUD/security, geographical browser CRUD and reload, center/unit browser CRUD and chained selections, and a read-only browser session.
- Real messaging checks `TestIntRef002CreateCenterDuringBrokerOutage` and `TestIntRef002RecoverCenterEventOnce`: passed. Lost events = 0; duplicate projection effects = 0.
- Migration repetition: schema and seed snapshot unchanged after a second Liquibase update. Application role checks passed using the restricted Reference Data login.
- Readiness regression: stopping PostgreSQL produces 503 readiness while liveness remains 200; restoring PostgreSQL restores readiness.
- Documentation OpenAPI lint: zero errors and three non-blocking warnings; relative-link and personal-data checks passed.

### Reproduction and evidence

Run `validation/int-ref-002/run.ps1` from docker-infra in PowerShell 7, with Docker available and all dependency repositories checked out. The default invocation builds the frontend images and allocates a new isolated project; `-SkipBuild` is only appropriate when images already match the candidate. `-Resume` explicitly reuses an existing disposable project. Do not run two projects on the same loopback ports.

The final browser verification completed at 2026-10-25T18:48:48.7775081Z. The verified project is `macro-ref-int002-20261025b`. Local evidence is under `validation/int-ref-002/evidence/`: `result.json`, `browser-summary.json`, and `migration-repeat.txt`. The result deliberately uses `technical_passed_pending_policy`, with passed criteria [1,2,3,4,5,7,8,9] and pending criterion [6]. Raw Playwright output must not be copied into a public delivery because failed assertions can include response data.

| Repository | Candidate revision | Branch |
|---|---|---|
| design-software-reference-data-service | 34c5398 | hu-int-ref-002-dev |
| design-software-reference-data-mfe | eae1b7c | hu-int-ref-002-dev |
| design-software-shared-contracts | 7b881a7 | hu-int-ref-002-dev |
| design-software-web-shell | 3148bf7 | hu-int-ref-002-dev |
| design-software-docker-infra | 624e515 | hu-int-ref-002-dev |
| design-software-docs contract input | def175a860d222b0418bd3833fd4a90ab2157cae | docs/hu-int-ref-002-hierarchy |

These are local candidate commits; this report does not assert publication, merge, deployment or QA approval. The MFE pins the exact contract input revision in its manifest; later evidence-only documentation commits do not change that input.

### Remaining decision and QA boundary

The domain owner must define which usages block deactivation of a municipality, center or unit, who owns each usage, the consumer API/event contract, failure semantics and concurrency behavior. Implement and verify 409 with unchanged state for each approved blocking scenario before accepting criterion 6. Foreign keys alone do not define that policy; external databases must never be queried as a shortcut.

Center code and municipality immutability follow existing RN-REF-01/02. QA should verify that both conflicting updates return IMMUTABLE_FIELD without changing the stored identity, and that repeating the same current UUID with uppercase hex remains compatible.

## References

- [Implementation and policy guide](../10-devops/reference-data-int-ref-002.md)
- [Canonical API](../07-api/contracts/openapi/reference-data.yaml)
- [Messaging architecture](../05-architecture/decisions/records/ADR-021-reference-data-resilient-messaging.md)
