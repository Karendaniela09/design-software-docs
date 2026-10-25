# QA Report — R4 Security Hardening — Academic Management Service

**Service:** `design-software-academic-management-service`  
**Code branch:** `feat/r4-security-jose-montealegre`  
**Target:** `develop`  
**Related work item:** HU-ACAD-11  
**Date:** 2026-10-23  
**Status:** Implementation candidate verified locally; deployed cross-service gates pending. The business rules were approved by the project owner on 2026-10-24 (ADR-030, ACCEPTED).

> **Superseded in part — owner decisions of 2026-10-24.** The executed-hours gate
> (80%) of `EXECUTION` → `PRODUCTIVE_STAGE` described below was removed: that
> transition has no hours condition, and the Scheduling report is informative
> evidence only. The completion rule
> documented below as a numeric "final grade" per learner (the Actors gate, the
> Actors DB final-grade table, the `ACT_LEARNER_FINAL_GRADE_MANAGE` and
> `ACT_INTERNAL_FICHA_FINAL_GRADE_SUMMARY` features and the related commits
> `3ef5c53`, `ab6289f` and `1ef70a5`) is withdrawn. SENA does not grade with
> numbers: a ficha is completed only when every active learner has `APPROVED` on
> 100% of the active RAPs of the ficha's program (RN-ACAD-07, ADR-030). The
> original evidence is kept for traceability; it must not be read as describing the
> current rule. The corrected implementation lives in the same branches, on top of
> the commits listed here, and its evidence is recorded in the pull requests.

## Scope

This report records the technical, security, contract, database, test and integration evidence for the Academic R4 submission. It is the canonical quality document; implementation code and automated tests remain in their owning repositories.

The reviewed change hardens JWT validation, authorization and training-center isolation, protects ficha state transitions with Scheduling and Actors evidence, adds cancellation justification, updates database migrations and shared contracts, and documents residual integration dependencies.

## Repositories, branches and commits reviewed

| Repository | Validation branch | Commit / evidence |
|---|---|---|
| Academic Management Service | `feat/r4-security-jose-montealegre` | `b2ff3d3` — lifecycle evidence, cancellation and security |
| Academic Management DB | `fix/r4-security-academic-management` | `3bea934` — cancellation audit fields and rollback |
| Actors Service | `fix/r4-security-academic-management` | `3ef5c53` — final grades and internal summary (superseded by RAP judgments, see the note above) |
| Actors DB | `fix/r4-security-academic-management` | `ab6289f` — final-grade persistence (superseded by the RAP judgment table) |
| IAM Service | `fix/r4-security-academic-management` | `1f6fa55` — rebased audience-bound M2M token implementation |
| IAM DB | `fix/r4-security-academic-management` | `1ef70a5` — grants and features |
| Scheduling Service | `fix/r4-security-academic-management` | `0427fc0` — execution aggregate, authorization and enabled outbox delivery |
| Scheduling DB | `fix/r4-security-academic-management` | `cbac3d4` — duplicate-safe R4 migration and rollback |
| Shared Contracts | `fix/r4-security-academic-management` | `c36fb6f` — Academic, Actors, IAM and Scheduling contracts |
| Documentation | `docs/academic-r4-security` | `3c9fcf5` — canonical ADR and quality evidence |

The frontend validation branch is `design-software-academic-management-mfe/feat/plan-mejoramiento-joseale879` and is published at the latest cleanup commit `0df3abd`. Shared contracts are at `c36fb6f` on `fix/r4-security-academic-management`. The frontend branch is included for Web Shell/MFE and Pact/E2E validation, but it does not replace the backend evidence above.

## Consolidated frontend evidence

### Correction rerun — 2026-10-24

The Academic Management MFE validation branch was rerun locally after the
review corrections. The following commands passed on the published branch
`0df3abd`:

| Command | Result |
|---|---|
| `npm run lint` | PASS |
| `npm run typecheck` | PASS |
| `npm run test:coverage` | PASS; 19 files, 100 tests; application 81.92% and adapter 82.90% statements |
| `npm run test:pact` | PASS; 1 file, 1 test |
| `npm run build` | PASS; `remoteEntry.js` 22,961 bytes raw |
| `npm run check:bundle-budget` | PASS; JavaScript 140,945 bytes gzip of 170,000 allowed |
| `npm run check:tokens` | PASS; one consumer verified |

### Final correction audit — 2026-10-24

The local audit revisited the ten findings from
`correcciones-pendientes-r4-2026-10-23.md`:

| Finding | Current result | Evidence or blocker |
|---|---|---|
| 1. Private CI checkout | Blocked externally | `CODE_SENA_READ_TOKEN` and repository read access are required by GitHub Actions. |
| 2. Real E2E and axe | Partial / failed gate | Academic MFE `npm run build` passed and emitted `dist/remoteEntry.js` (22,961 bytes). The Web Shell smoke was executed with Academic on port 5103; all three federation specs failed because the remaining eight remotes are unavailable, the Shell API proxy was not pointed at the integrated ports, and two UI assertions are stale. No authenticated/restricted Playwright states or seeded R4 ficha were available. |
| 3. Integrated Lighthouse | Blocked externally | No integrated Academic Web Shell URL is available for `LIGHTHOUSE_URLS`. |
| 4. Provider Pact | Blocked externally | No Broker, provider URL, provider states endpoint or protected Pact credentials are available. |
| 5. Coordinated migrations | Partial | Scheduling was rerun in disposable PostgreSQL with 25/25 changesets. Current Academic, Actors and IAM coordinated migration execution remains pending. |
| 6. E5/projection/resilience | Partial | IAM, Academic, Actors and Scheduling containers reached HTTP 200 in the isolated stack; Scheduling persistence and service tests pass locally. The Academic–Scheduling projection, real authorized transitions, RAP-coverage completeness (formerly final-grade completeness) and RabbitMQ retry/DLQ for the R4 business event remain unverified. |
| 7. E7 integrated cancellation | Partial | Academic validation and persistence are covered locally; real IAM roles, public event inspection and cross-service audit flow remain pending. |
| 8. Maven suites | Passed locally | Academic 193, Actors 99 (2 skipped), IAM 191 and Scheduling 137 tests passed with Maven. |
| 9. SHA traceability | Rectified locally | Current branch/commit tables were refreshed; Scheduling DB fix is `cbac3d4` and Docs is published through `6556634`. |
| 10. Formal approval | Pending | QA/Product approval and PR reviews must be recorded by authorized reviewers. |

The local environment does not contain the required TLS material, IAM private
key, Web Shell deployment, authenticated browser states, provider states or
institutional secrets. Consequently, findings 1–4 and 10 cannot be advanced
from this workspace; findings 5–7 can only be closed after the integrated
services and data are supplied. No credentials, tokens or browser states were
committed or generated as substitutes.

The Docker compose review also confirmed that the standard infrastructure file
does not define an `academic-api`, Actors or Scheduling service for a complete
Academic E2E flow. The separate monitoring integration compose provides only an
Academic/IAM monitoring setup, not the four-service R4 stack. Therefore a local
browser run cannot be made representative by simply inventing `E2E_BASE_URL`.

### Additional isolated stack attempt — 2026-10-24

The existing isolated `ds-monitoring-r3` compose was used to advance the local
validation without touching `develop` volumes. IAM, Academic, Actors and
Scheduling images were rebuilt from the reviewed branches; ephemeral IAM keys
and a local test account were generated by the repository bootstrap script; the
four services, PostgreSQL and RabbitMQ were started; and the service health
checks returned HTTP 200. The integration configuration required explicit local
issuer/JWKS variables and a RabbitMQ password synchronization. OTEL export was
disabled only for Academic because no local collector was running.

This proves local service reachability and real IAM/JWKS-ready infrastructure,
but it does not close point 2 or point 6: the MFE Web Shell is not part of this
compose, no protected Playwright storage states or browser seed are available,
and no approved R4 transition fixture was supplied. The stack also contains the
historical R3 monitoring harness, so its domain scripts cannot be presented as
HU-ACAD-11/E5/E7 acceptance evidence. No institutional secret or generated
credential was committed.

Docker Desktop is reachable in the elevated validation session through the
`desktop-linux` context, and Testcontainers successfully started PostgreSQL.
Apache Maven 3.10.0 was installed for the current Windows user at
`C:\Users\nruiz\tools\apache-maven` and was executed with the available JDK 17
and JDK 21 installations. This resolves the former local-tooling block, but it
does not by itself provide the institutional CI secrets or integrated services.

The rerun therefore distinguishes service-level results from environment-level
gates. Academic, Actors, IAM and Scheduling completed successfully after
Scheduling was pointed to a disposable PostgreSQL instance on host port
`15440`. No integrated migration on institutional infrastructure, RabbitMQ,
E2E, axe, production Lighthouse or provider Pact claim is inferred from this
local toolchain correction.

The following evidence was reviewed from the Academic Management MFE and is consolidated in this report. The evidence is historical and was observed locally on 2026-10-20; it does not convert blocked integrated checks into passing results.

### Web Shell/MFE smoke attempt — 2026-10-24

The Academic MFE was rebuilt successfully and its production `remoteEntry.js`
was served on `http://localhost:5103`. The official Web Shell federation smoke
was executed against the real Academic remote with a mock Shell session,
without intercepting remote loading. The run produced three failures: the
federated route did not reach a terminal outcome for the unavailable remotes,
the nine-domain navigation assertion could not complete, and the unavailable
route assertion expects text that no longer matches the current UI. The run
also exposed that the Shell default API proxy is `localhost:8080`, while this
isolated stack uses ports `18081`–`18085`.

The nine local `remoteEntry.js` files were then served and all responded HTTP
200 on ports 5101–5109. This closes only the local remote-availability check.
The full browser smoke still did not pass because the MFE data calls were
proxied to `localhost:8080` instead of the integrated service ports, and the
IAM/Academic/Actors containers were not healthy after the isolated stack was
restarted. This is diagnostic evidence, not a pass: the Shell needs an
integrated API routing configuration and healthy backend dependencies before
E2E/axe can be marked passed. No test was weakened and no unavailable remote
was represented as available.

### Second federated smoke attempt — 2026-10-24

After serving all nine local remotes and increasing the Node heap, the smoke
no longer failed because of missing remote entries or memory. It still failed
three checks: `iamMfe` left the root empty, navigation did not complete within
the test timeout, and the test expects `No pudimos cargar` while the current
UI renders `No se pudo cargar la ruta solicitada`. This identifies remaining
Shell/remote runtime and test-contract alignment work; it is not an E4/E5 pass.

### Federated smoke correction — 2026-10-24

The Web Shell was corrected on branch `fix/r4-security-academic-management`,
commit `ce8b3de`. The `RemoteIndex` navigation callback is now wired from
`ShellRoot` through `RemoteRoutes`; the smoke waits for each remote to finish
mounting before checking for a blank root; and the unavailable-route assertion
matches the current UI copy. With all nine locally built remotes served,
`npm run typecheck` passed and the Web Shell federation smoke completed 3/3
tests successfully. This closes the local federation/navigation check only;
it does not close authenticated E2E, E5/E7 business transitions or institutional
CI gates.

### Temporary business-fixture attempt — 2026-10-24

After RabbitMQ credentials were synchronized in the isolated stack, IAM,
Academic, Actors and Scheduling were restarted. Pact local verification
completed successfully with 4/4 interactions against Academic. Reference Data
was built as `ds-reference-r3:local`, started in the IAM shared network
namespace, its DML seed loaded, and the missing isolated database roles/grants
were applied. The authenticated lookup then returned HTTP 200 for the seeded
training center `a0000000-0000-0000-0000-000000000005`.

A temporary ficha `R4-TEMP-20261024-D` was created through the real Academic
API with a local IAM token (HTTP 201). The authorized `INDUCTION -> EXECUTION`
transition returned HTTP 200, incremented `row_version` from 0 to 1, and
produced two outbox rows; the opened-ficha event was marked published. The
attempted `EXECUTION -> CANCELLED` transition was correctly rejected with HTTP
403 (`ACAD_FICHA_STATUS_ROLE_DENIED`) because the test identity is not a
`CENTER_DIRECTOR`. This is valid negative evidence, not a successful E7
cancellation approval.

Cleanup was executed and verified against the isolated database: the temporary
ficha count is 0 and matching outbox count is 0. Scheduling hours, Actors final
grades, Academic-Scheduling projection and a real R4 retry/DLQ business event
were not created by this run, so E5 remains partial. A second temporary run
used a `CENTER_DIRECTOR` grant scoped to the seeded center. Its ficha was
cancelled successfully with HTTP 200; the outbox contained
`academic.ficha.closed` with `status=CANCELLED` and the cancellation note was
not present in the public event payload. The temporary user, role grant, ficha
and outbox rows were removed afterward. This closes the local positive E7
authorization/audit check, but not the complete cross-service acceptance gate.

### Initial audit and implementation scope

- The MFE already listed and displayed fichas, but did not yet provide the operational editor, state management or report pages.
- The implementation added the operational ficha form, state-transition manager, capacity and progress reports, HTTP error mapping, Pact consumer coverage, Playwright scenarios, axe checks, Lighthouse configuration and CI quality gates.
- The reviewed shell exposes `academicManagementMfe` at `/academic-management/*`; the remote exposes `App`, `FichasPage`, `FichasReportPage`, `ProgramsPage`, `CurriculumSetupPage` and `ActiveFichasWidget`.
- The host contract currently confirms `basePath` and `apiBaseUrl`; it does not yet inject the Frontend Platform `HttpClient`, capabilities or roles. The MFE therefore uses session cookies and leaves final authorization to the backend.

### Frontend traceability and local results

| Area | Local evidence | Result and limitation |
|---|---|---|
| HU-ACAD-10 | Operational fields, `row_version`, validation and confirmed-response refresh | Implemented locally; real API, session and permission validation pending |
| HU-ACAD-11 | State machine, terminal-state protection, cancellation confirmation and 10–500 character `cancellation_notes` validation | Implemented locally; Actors, Scheduling and real roles pending |
| HU-ACAD-12 | Capacity and progress pages, filtering, sorting and pagination | Implemented locally; real API and training-center scope pending |
| F.1 Playwright | 9 API flows and 4 axe scenarios discovered; no API interception in the real scenarios | Prepared, but not executed without integrated shell/API, users and seed data |
| F.2 Vitest | 99/99 tests; application 81.92% and adapter 82.78% statements | Passed locally |
| F.3 axe | WCAG 2.1 A/AA checks and keyboard/focus scenarios configured | Pending real shell execution |
| F.4 Lighthouse | LHCI thresholds and bundle budget configured; bundle budget passed | Real Lighthouse remained blocked by missing integrated URLs |
| F.5 Pact | Consumer interactions for PUT, PATCH, capacity and progress reports | Local mock consumer passed; Broker publication and provider verification pending |
| F.6 CI | Quality, E2E, axe, Lighthouse and Pact provider verification jobs configured | PR checks failed before functional execution because private dependency access and URLs were unavailable |
| F.7 ADR | Decision on state, errors, permissions and host integration | Consolidated in ADR-030 |

### CI gates and observed blockers

The workflow `quality-gates.yml` defines installation/lint/typecheck/unit/coverage/build, real-service Playwright, axe, Lighthouse and Pact provider verification jobs. In PR #12 runs #1–#4, four jobs could not clone the private `design-software-design-system` repository (`Repository not found`), and Lighthouse stopped because `LIGHTHOUSE_URLS` was not configured. Consequently, those runs do not constitute passing evidence for E2E, axe, Lighthouse or provider Pact verification.

The required external configuration remains: `CODE_SENA_READ_TOKEN`, `E2E_BASE_URL`, authenticated and restricted storage states, ficha/report seed identifiers, `LIGHTHOUSE_URLS`, optional Lighthouse headers, `PACT_BROKER_BASE_URL`, `PACT_BROKER_TOKEN`, `ACADEMIC_PROVIDER_BASE_URL` and `PACT_PROVIDER_STATES_URL`. Docker is now available in the elevated local session, but the integrated environment still requires the service URLs, credentials, seed data and database listener configuration.

### Reproducibility and presentation guidance

The local verification sequence is `npm ci`, `npm run lint`, `npm run typecheck`, `npm run test:coverage`, `npm run test:pact`, `npm run build` and `npm run check:bundle-budget`. These commands demonstrate local implementation quality only. The ten-minute demonstration should show the architecture, HU-ACAD-10 editor, HU-ACAD-11 transitions/cancellation, HU-ACAD-12 reports, local gates and ADR-030, explicitly distinguishing local evidence from pending integrated evidence.

## Evidence package and traceability

The implementation must be evaluated through the following evidence chain:

1. Git branch and commit identify the implementation under review.
2. OpenAPI contracts identify the cross-service request/response and authorization surface.
3. Database changesets and rollbacks identify persistence and recovery behavior.
4. Unit, integration, security and contract tests identify expected behavior and rejection paths.
5. CI artifacts identify reproducibility in Java 17, Maven, PostgreSQL/Testcontainers and the configured frontend gates.
6. Deployed E2E evidence must demonstrate IAM → Academic → Actors/Scheduling, PostgreSQL, RabbitMQ, outbox, retry and DLQ behavior.

The final three items are not interchangeable: passing local tests does not prove deployed cross-service behavior.

## Frontend/MFE verification evidence

The frontend branch `feat/plan-mejoramiento-joseale879` was independently validated after a clean `npm ci`:

| Gate | Command / scope | Result |
|---|---|---|
| Static quality | `npm run lint` | PASS |
| Type safety and production bundle | `npm run build` | PASS |
| Unit/integration tests | `npm run test:coverage` | 19 files, 100 tests passed |
| Coverage | Application / adapters | 81.92% / 82.78% statements |
| Consumer contract | `npm run test:pact` | 1 file, 1 test passed; cancellation payload covered locally |
| Bundle budget | `npm run check:bundle-budget` | PASS; `remoteEntry.js` 22,961 / 30,000 raw bytes |

The local frontend gates therefore satisfy the available automated evidence for HU-ACAD-10/11/12, including the required cancellation justification payload and synchronized `row_version` contract. Playwright execution, axe results, Lighthouse against a deployed URL, provider-side Pact verification, Web Shell integration and the CI checkout of private frontend dependencies still require the configured integrated environment and secrets.

## Automated test matrix

| ID | Scenario | Expected result | Status |
|---|---|---:|---|
| SEC-01–08 | Missing, malformed, expired, unsigned, wrong-key and wrong-issuer JWTs | 401 | PASS |
| SEC-09–13 | Missing feature and unauthorized ficha status operations | 403 | PASS |
| SEC-14–15 | Create ficha outside the signed training-center scope | 403; no write | PASS |
| SEC-16–17 | Read foreign ficha or ownership resource | 404; no disclosure | PASS |
| SEC-18 | Coordinator attempts cancellation without `CENTER_DIRECTOR` | 403 | PASS |
| SEC-19 | Report access without view authority | 403 | PASS |
| SEC-20–21 | Foreign training-center report filters and ownership filters | Empty/isolated result | PASS |
| SEC-22 | Bearer token supplied in query string | 401/400 rejection | PASS |

## Security controls verified

- RS256 is explicitly required and the configured issuer is validated.
- JWT time claims and the shape of `sub`, `features` and `roles` are validated.
- Development no longer accepts unsigned tokens.
- Authorization uses signed features, roles and scope claims.
- Ficha creation verifies the requested training center before persistence.
- State changes fail closed when external preconditions cannot be verified.
- Terminal states and future completion dates are protected by domain rules.
- `academic.ficha.opened` is emitted on entry to `EXECUTION`.
- CI runs unit, integration and security regression tests with Java 17 and Testcontainers.

## R4 E5 technical evidence

### Scheduling gate: `EXECUTION` → `PRODUCTIVE_STAGE` (removed on 2026-10-24)

The owner removed this gate: the transition has no hours condition and Academic no
longer reads the Scheduling report. The text below is the original evidence, kept
for traceability and the report stays as informative evidence.

- Academic consumes the Scheduling execution aggregate by ficha and date range.
- The business rule is `executed_hours >= eligible_scheduled_hours * 0.80`.
- Eligible hours include `EXECUTED`, `PENDING` and `NOT_EXECUTED` sessions from active, published schedules; `CANCELLED` sessions are excluded.
- The date interval is inclusive from the ficha start date through the transition date.
- A zero denominator, invalid response, unavailable service or unavailable M2M token rejects the transition without persistence; dependency failures are handled fail-closed.
- Scheduling authorizes the report with audience `scheduling-service` and `SCH_REPORT_VIEW:GLOBAL`.

### Actors gate: `PRODUCTIVE_STAGE` → `COMPLETED`

Corrected by the owner on 2026-10-24 (the first draft used a numeric final grade, now withdrawn):

- Actors is the source of truth for one `APPROVED` / `NOT_APPROVED` judgment per `(learner_id, ficha_id, learning_outcome_id)`; no judgment means pending.
- There is no numeric grade and no threshold.
- Every active learner must have `APPROVED` on 100% of the active RAPs of the ficha's program; Academic resolves the required RAP ids.
- Academic consumes counts only, not individual judgments.
- Actors uses an audience-bound token and the `ACT_INTERNAL_FICHA_RAP_COVERAGE` feature.

## E7 cancellation technical evidence

- `cancellation_notes` is required only for `CANCELLED`.
- Leading and trailing whitespace is removed; the normalized value must contain 10–500 Unicode code points.
- The Academic DB changeset stores the note, cancellation timestamp and actor, with a rollback.
- The note is not returned by the PATCH response and is not published in the public `academic.ficha.closed` event.
- Existing cancelled rows are not backfilled; new cancellation requests are enforced by API and domain validation.

## Database and contract evidence

| Area | Evidence required / reviewed |
|---|---|
| Academic DB | Cancellation audit columns, Liquibase changeset and rollback |
| Actors DB | RAP judgment table, uniqueness/check constraints and rollback (replaces the withdrawn final-grade table) |
| IAM DB | Audience-specific grants/features and rollback |
| Scheduling DB | Runtime tables for sessions, projections and outbox, with rollback |
| Shared Contracts | Versioned OpenAPI for Academic, Actors, IAM and Scheduling |
| Academic API | Status transition, cancellation notes and external precondition errors |
| Events | Outbox publication, public payload exclusion of cancellation notes |

## Verification results from the implementation record

The following results are recorded by the implementation owner and must be reproducible in CI or a clean validation run:

| Repository | Command / scope | Recorded result |
|---|---|---|
| Academic Management Service | `mvn test` | 193 tests; 0 failures, 0 errors |
| Actors Service | `mvn clean test` | 99 tests; 0 failures, 0 errors; 2 skipped |
| Actors Service | Directed internal controller integration suite | 9 tests; 0 failures, 0 errors |
| IAM Service | `mvn test` | 191 tests; 0 failures, 0 errors |
| Scheduling Service | `mvn clean test` | 137 tests; 0 failures, 0 errors against disposable PostgreSQL on host port `15440` |
| Liquibase | Disposable PostgreSQL changelog rerun | Scheduling: 25/25 changesets applied; Academic/Actors/IAM counts remain historical evidence and require a current coordinated rerun |
| Repository hygiene | `git diff --check` | No whitespace errors reported |

The independently rerun local results are recorded below. The deployed E2E, real IAM/JWKS flow, RabbitMQ retry/DLQ and Academic projection synchronization remain unverified.

The historical 2026-10-23 evidence states that the coordinated database changelogs were applied locally: Academic 31, Actors 29, IAM 38 and Scheduling 20 changesets, including `r4-scheduling-runtime-persistence-001`. That evidence remains historical and must be reproduced in the current environment before institutional closure.

The 2026-10-24 rerun with installed Maven passed Academic Management (193 tests, 0 failures/errors), Actors (99 tests, 0 failures/errors, 2 skipped), IAM (191 tests, 0 failures/errors) and Scheduling (137 tests, 0 failures/errors). Scheduling was executed against a disposable PostgreSQL 16 instance on host port `15440`; all 25/25 Liquibase changesets applied successfully. During this validation, the R4 Scheduling DB changeset was corrected because it duplicated tables already owned by canonical changesets; the fix is published as `cbac3d4`.

## HU-ACAD-11 acceptance status

## Consolidated Scheduling DB and Lighthouse evidence

### Scheduling DB changeset 983 — HU-SCH-007

The Scheduling DB migration evidence was executed against an isolated
PostgreSQL 16.15 database using Liquibase 4.33.0 and Java 21. The tested
source was `design-software-scheduling-db`, branch `hu-007-dev`, commit
`25a121ecbac0470342217a48cc784d6f876f8033`. The temporary compose override
used a separate container and volume so the existing shared database was not
modified.

- Changeset `hu-sch-007-schedule-immutability-983` was applied as the final
  changeset in an isolated run; 20 changesets completed successfully.
- The immutability QA SQL passed for protected `row_version`, `updated_at` and
  soft-delete fields, while the ordinary `PUBLISHED -> ARCHIVED` transition
  preserved the protected values.
- `rollback-count 1` rolled back exactly changeset 983 successfully.
- The rollback QA SQL passed and confirmed restoration of the previous trigger
  definition and combined-archive behavior.

Observed outputs were `QA 983 immutability checks passed` and
`QA 983 rollback checks passed`. The executable SQL checks remain in the
Scheduling DB repository; this report is the canonical record of their result.

### Lighthouse evidence

The generated Lighthouse run was performed with Lighthouse 12.6.1 in
navigation mode against the local route `http://127.0.0.1:5000/actors`. The
accessibility category scored `1.00` (100%). No production or integrated
Academic Web Shell URL was measured in that artifact, so it is retained here
as local accessibility evidence only; it does not satisfy the pending
production Lighthouse gate for the Academic MFE.

| Criterion | Status | Evidence or remaining action |
|---|---|---|
| E1 — PATCH and cancellation contract | Partial | Implemented and tested; DELETE alias semantics require contract confirmation |
| E2 — Valid and invalid transitions | Partial | Domain rules pass; advanced transitions require E5 evidence |
| E3 — Permissions and roles | Implemented locally | Real IAM-issued claims still require E2E verification |
| E4 — Terminal states | Implemented and tested | No remaining local gap identified |
| E5 — Actors RAP approval (the Scheduling hours gate was removed) | Implemented in coordinated branches; integration pending | The RAP-coverage rule is implemented (the final-grade variant and the 80% hours gate were withdrawn on 2026-10-24). Scheduling migrations were rerun successfully; current coordinated Academic/Actors/IAM database execution and deployed IAM/Actors/Scheduling flow remain pending, together with Product/QA approval |
| E6 — Actual end date | Implemented and tested | Full completion path remains dependent on E5 |
| E7 — Cancellation justification | Implemented in coordinated branches; integration pending | Request/domain validation, persistence, audit fields, rollback and public-event exclusion are implemented. Academic migration applies locally; deployed verification remains pending |
| E8 — Events and outbox | Implemented locally | Real broker delivery, retry, DLQ and distributed correlation remain unverified |

## ASVS boundary

The ASVS L1 assessment performed for the backend is consolidated here rather than stored as a plan dossier in the microservice repository. This report is the canonical QA summary in `design-software-docs`. The assessment results are: 16 controls marked compliant, 1 confirmed non-compliant, 19 not verified and 34 not applicable. This is not a product-wide ASVS certification.

## Required closure actions

1. Record the follow-ups of ADR-030 as the product asks for them (program version, SOFIA Plus, writes after closure, instructor scope HU-ACT-031). The business rules were approved by the owner on 2026-10-24.
2. Validate the Academic–Scheduling and Academic–Actors contracts against the shared-contracts repository in CI.
3. Apply and verify the Academic, Actors, IAM and Scheduling migrations in the integrated environment, including rollback evidence. Local application is complete; integrated-environment verification remains open.
4. Validate the published MFE branch `feat/plan-mejoramiento-joseale879`, then execute the real IAM, Academic, Actors, Scheduling, RabbitMQ and Web Shell/MFE flow.
5. Verify outbox publication, retry and DLQ behavior, plus Academic-to-Scheduling center projection synchronization.
6. Obtain human review and approval for the implementation PRs, complete the live sustentation, and record authorized merges.

## Decision

The R4 security, E5 and E7 implementation is technically documented and locally evidenced in coordinated branches. The submission is not yet fully closed until the business rules are approved, CI/deployed E2E evidence is reproducible, messaging and projection flows are verified, and formal review is completed.
