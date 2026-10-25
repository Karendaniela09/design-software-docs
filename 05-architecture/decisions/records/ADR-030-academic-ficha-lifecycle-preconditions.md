# ADR-030: Academic Management R4 Security, Lifecycle Preconditions and Cancellation

**Status:** ACCEPTED — approved by the project owner on 2026-10-24 (see "Owner decisions")  
**Date:** 2026-10-23  
**Amended:** 2026-10-24 — completion rule changed from a numeric final grade to 100% RAP approval; executed-hours gate removed; `DELETE /fichas/{id}` kept; open questions decided (owner decisions)  
**Author of origin:** José Alejandro Montealegre (`joseale879`)  
**Source:** Academic R4 implementation record  
**Teams involved:** Academic, Actors, Scheduling, IAM, Shared Contracts, Database  
**Work items:** HU-ACAD-11 (code-sena/design-software-docs#171), HU-ACT-029 (code-sena/design-software-docs#391) and HU-ACT-031 (code-sena/design-software-docs#419)

---

## Context

Academic Management is a Spring Boot resource server that consumes JWTs issued
by IAM and manages programs and fichas. The R4 review identified permissive
development JWT handling, missing explicit issuer/algorithm validation,
insufficient training-center scope enforcement, and unsafe transitions when
Scheduling or Actors evidence is unavailable. The service must reject unsigned
or malformed tokens, enforce features, roles and signed scopes, and fail closed
when required external evidence cannot be verified.

HU-ACAD-11 asks for evidence before a ficha is completed (`PRODUCTIVE_STAGE` to
`COMPLETED`). The reviewed requirements do not specify the M2M audience.
Cancellation also requires an internal justification, while its length and
persistence contract were not defined. The requester delegated the implementation
choices and asked that they be documented on the Academic R4 branch. The first
draft also proposed an executed-hours gate for `EXECUTION` to `PRODUCTIVE_STAGE`;
the owner removed it (see "Owner decisions"). The project owner reviewed and
approved the choices of this ADR on 2026-10-24.

**Owner decision of 2026-10-24 (completion rule).** The first draft of this ADR
modelled a numeric "final grade" per learner as the completion precondition. The
project owner corrected it: SENA does not grade with numbers. Each learning
outcome (RAP, `LearningOutcome`) receives an evaluative judgment per learner,
`APPROVED` or `NOT_APPROVED`, and no judgment means pending. The completion
precondition is RAP approval of 100%, associated with the ficha and its program.
The numeric grade, its 0.00-100.00 scale and the "a grade's presence is enough"
rule are withdrawn. The rule is recorded as RN-ACAD-07 in
`02-domain/entities-and-rules.md`.

## Decision

### R4 security hardening

1. Validate service JWTs with the configured JWKS, issuer, time claims and
   RS256 algorithm.
2. Reject unsigned or malformed tokens in every environment, including
   development.
3. Enforce features, roles and signed training-center or ownership scopes in
   the service layer.
4. Fail closed when the Actors completion evidence cannot be verified.
5. Emit ficha lifecycle events through the existing outbox path.
6. Keep cross-service contracts and cancellation persistence decisions in the
   owning repositories.

### No executed-hours precondition for `EXECUTION` → `PRODUCTIVE_STAGE`

This transition has **no hours precondition**: it behaves as it does in `develop`
(role and state-machine rules only). The first draft required 80% of the eligible
scheduled hours to be executed; no document defines that threshold and the owner
removed it. The only documented rule about reaching the productive stage is
`RN-ACT-04` (a learner needs a configurable 70% of curricular progress to start it),
which this ADR does not change.

Scheduling keeps `GET /api/v1/reports/ficha-execution-summary` and
`/aggregate` as **informative evidence** for coordinators. Academic does not call
them and nothing is gated on them.

### RAP approval evidence for `PRODUCTIVE_STAGE` → `COMPLETED`

**Rule.** A ficha moves from `PRODUCTIVE_STAGE` to `COMPLETED` only if **every
active learner of the ficha has `APPROVED` on 100% of the required RAPs**. There
is no numeric grade, no pass threshold and no tolerance below 100%.

- **Required RAPs.** Academic owns the set: every active `learning_outcome`
  (`is_active = true`, not soft-deleted) whose competency is active and belongs
  to the ficha's program (`enrollment_ficha.program_id`), as they are at the
  moment of the transition (the program version is a follow-up, see below).
- **Active learner.** A learner with a current, active enrollment in the ficha
  and an `ACTIVE` state (RN-ACT-03). Actors owns this definition. **A ficha with
  no active learners cannot be completed.**
- **Judgment.** One evaluative judgment per `(learner, ficha, RAP)`: `APPROVED`
  or `NOT_APPROVED`. No row means pending. Only `APPROVED` counts. The last
  judgment recorded for the triple prevails (upsert).

**Where the judgment lives.** In Actors, which owns the learner and its
enrollment. The table is `actors_learners.learner_rap_assessment`:

| Column | Type | Rule |
|--------|------|------|
| `id` | UUID | PK |
| `learner_id`, `ficha_id` | UUID | Composite FK to `learner_ficha_enrollment (learner_id, ficha_id)`, `ON DELETE RESTRICT` |
| `learning_outcome_id` | UUID | Reference by id to `academic_management.learning_outcome`; no FK between databases |
| `result` | VARCHAR(20) | `CHECK (result IN ('APPROVED','NOT_APPROVED'))` |
| `assessed_by`, `assessed_at` | UUID, TIMESTAMPTZ | Who judged (from the token) and when (server clock) |
| ADR-004 audit | | `created_at/by`, `updated_at/by`, `deleted_at/by`, `is_active`, `row_version` |

`UNIQUE (learner_id, ficha_id, learning_outcome_id)`. Deletion is logical: a
judgment is corrected by upsert, never removed physically.

**Recording.** `PUT /api/v1/fichas/{fichaId}/learners/{learnerId}/rap-assessments/{learningOutcomeId}`
with `{ "result": "APPROVED" | "NOT_APPROVED" }`, protected by
`ACT_LEARNER_RAP_ASSESSMENT_MANAGE` (scope `GLOBAL`, or `TRAINING_CENTER` checked
against the ficha's center). Only an active enrollment is accepted. Actors does
not validate the RAP id against Academic (there is no cross-database FK); an id
outside the ficha's program is stored but never counts toward coverage.

**Coverage.** Academic reads the required RAP ids from its own database and asks
Actors, with an audience-bound M2M token, to verify them:
`POST /internal/fichas/{fichaId}/rap-assessments/coverage` with
`{ "learning_outcome_ids": [...] }` (a `POST` only because the list can hold
hundreds of ids; the call is read-only). Actors answers with counts only:
`required_learning_outcomes`, `active_learners`, `fully_approved_learners` and
`all_active_learners_fully_approved`. Individual judgments and learner
identifiers are not returned to Academic. The token must have audience
`actors-service` and feature `ACT_INTERNAL_FICHA_RAP_COVERAGE:GLOBAL`. Actors
also receives `ACT_INTERNAL_FICHA_LEARNER_COUNT:GLOBAL` and
`ACADEMIC_FICHA_VIEW:GLOBAL` for existing internal ficha checks.

**Errors.** If any active learner lacks `APPROVED` on a required RAP, the
transition is rejected with `409 ACAD_FICHA_RAP_COVERAGE_INCOMPLETE`, and the
message carries the counts. An empty required set (a program with no active
RAPs) and a ficha with no active learners are failed business preconditions
(`409 ACAD_STATUS_PRECONDITION_FAILED`). An unavailable Actors, an invalid
response or an unavailable M2M token fails closed with
`503 ACAD_STATUS_PRECONDITIONS_UNAVAILABLE` and the transition is not persisted.

### M2M token audience

IAM's client-credentials endpoint accepts only allowlisted audiences. It places
the selected audience in the JWT `aud` claim and issues only the features mapped
to that audience. `actors-service` receives the Actors features listed above;
`scheduling-service` receives `SCH_REPORT_VIEW:GLOBAL` (for the informative
execution report; Academic does not call it in this release). Services validate the
audience before granting service-token authorities. Client credentials remain
in secret storage and are not part of the API contract.

`audience` is optional for compatibility: when it is absent IAM treats the
request as `actors-service`, which is the only audience the pre-R4 Academic
client used (the HU-ACAD-10 active-learner count). This lets IAM deploy before
Academic without breaking the existing client. A present but unknown or blank
audience is rejected with `400 invalid_target`. The response always carries the
resolved `audience`. Omitting `audience` is a transitional allowance; a later HU
removes it once every caller sends it explicitly.

### Cancellation justification

`PATCH /api/v1/fichas/{id}/status` requires `cancellation_notes` only when the
target status is `CANCELLED`; it is rejected for other target statuses. Trim
leading/trailing whitespace, then require 10–500 Unicode code points. Persist
the trimmed note with `cancellation_at` and `cancellation_by` for internal
audit. Do not include the note in the PATCH response or the public
`academic.ficha.closed` event. The DB migration permits existing cancelled
rows without retroactive notes; new cancellations must satisfy the API/domain
rule.

`DELETE /api/v1/fichas/{id}` is **kept** as an alias of the transition to
`CANCELLED` (logical deletion; the record is never removed). It applies the same
validations as `PATCH /fichas/{id}/status` to `CANCELLED`: only `CENTER_DIRECTOR`,
the same scope rules, `409` on a terminal ficha, the same `cancellation_notes`
rule and the same `academic.ficha.closed` event. Because the justification is
mandatory, the alias receives it in a JSON body (`{"cancellation_notes": "..."}`)
and answers `204`.

### Frontend and Web Shell integration

The Academic Management MFE follows the same backend lifecycle and security
decision. It uses a `FichasApi` port with application hooks and adapters, sends
session credentials, renders only server-confirmed responses, and does not
duplicate authorization rules locally.

- The editor permits only operational fields and sends the required
  `row_version` for optimistic concurrency.
- The state manager exposes only domain-valid transitions, protects terminal
  states, confirms changes before submission, and requires normalized
  `cancellation_notes` for cancellation.
- Capacity and progress reports use the published API filters, pagination and
  server-provided values such as `training_center_id`, `is_delayed` and elapsed
  days; the UI does not invent business calculations.
- The remote consumes the host router and exposes `academicManagementMfe` at
  `/academic-management/*`; it does not create a second browser router.
- The current host contract confirms `basePath` and `apiBaseUrl`. Bearer
  injection, refresh, capabilities and role delivery through Frontend
  Platform remain an integration follow-up; backend authorization remains the
  source of truth until that contract is approved.

Local MFE evidence includes lint, typecheck, build, bundle-budget validation,
99/99 unit and integration tests, 81.92% application statement coverage,
82.78% adapter statement coverage and a passing Pact consumer test. Real
Web Shell/API E2E, axe, Lighthouse and provider-side Pact verification require
the integrated environment, authenticated storage states, private dependency
access and the configured secrets. The canonical results and limitations are
recorded in `11-quality/qa-report-r4-security-academic-management.md`.

## Consequences

### Positive

- Lifecycle transitions use explicit, auditable evidence from the owning services.
- Completion reflects what SENA evaluates: the approval of each learning outcome,
  not a number.
- Each service keeps its own data: Actors owns the judgments and the learner
  state, Academic owns the curriculum and decides which RAPs are required.
- Cross-service calls fail closed and use separate least-privilege audiences.
- Cancellation reasons are retained for internal audit without public disclosure.

### Negative / trade-offs

- Completing a ficha depends synchronously on IAM and Actors availability.
- `FichaUpdate` changes are incompatible with clients written for the draft
  contract (`row_version` required, `actual_end_date` removed); they are accepted
  before v1.
- Actors cannot tell whether a stored `learning_outcome_id` exists or belongs to
  the ficha's program; such ids are harmless but are not cleaned up.
- The coverage request grows with the number of RAPs of the program (bounded at
  1000 ids by the contract).

### Risks

- If a program's RAPs change between the last judgment and the closure of the
  ficha, the required set changes with them; versioned curricula are a follow-up.
- Judgments can still be recorded or corrected after the ficha is closed
  (follow-up).
- Unit and local integration evidence does not by itself prove IAM, RabbitMQ, or
  cross-service end-to-end operation in a deployed environment.

### Security verification

- `SecurityHardeningIT`: 22 negative scenarios.
- Full Maven verification previously recorded 192 local tests.
- CI workflow uses Java 17, Docker/Testcontainers and Maven reports.
- QA evidence is recorded in `11-quality/qa-report-r4-security-academic-management.md`.

## Alternatives considered

| Alternative | Reason not selected for this implementation |
|-------------|---------------------------------------------|
| Gate `EXECUTION` → `PRODUCTIVE_STAGE` on 80% of the executed scheduled hours (first draft of this ADR) | No document defines the threshold or the measure; `RN-ACT-04` (70% of the learner's curricular progress, configurable) is the only documented rule. Removed by the owner on 2026-10-24; the Scheduling report stays as informative evidence. |
| Remove `DELETE /fichas/{id}` | It would be an incompatible change without a need. The owner decided to keep it as an alias of the transition to `CANCELLED`. |
| Numeric final grade per learner, where having a grade is enough (first draft of this ADR) | SENA does not grade with numbers, and the presence of a number says nothing about whether the learner reached the learning outcomes. Withdrawn by the owner on 2026-10-24. |
| Actors compares the number of `APPROVED` judgments with the number of RAPs | Actors does not know which RAPs are active for the ficha's program; stale, foreign or duplicated judgments would be counted. Academic sends the required set instead. |
| Store the judgments in Academic | The learner, its enrollment and its state belong to Actors; Academic would still need the active-learner set on every transition. Keeping the judgment with the learner keeps the ownership split already in place. |
| Return or publish cancellation notes | The event design explicitly excludes the private cancellation justification. |

## Owner decisions (2026-10-24)

The project owner answered the nine open questions of the proposal and approved
the ADR. The answers are applied in the contracts, the data model and the code of
the Academic R4 bundle.

| # | Question | Decision |
|---|----------|----------|
| 1 | The 80% of executed hours for `EXECUTION` → `PRODUCTIVE_STAGE` | **Removed.** The transition has no hours condition and behaves as in `develop`. No other rule is invented; the documented rule stays `RN-ACT-04` (configurable 70% of curricular progress). The Scheduling report stays as informative evidence. |
| 2 | `DELETE /fichas/{id}` | **Kept** as an alias of the transition to `CANCELLED` (logical deletion, same validations), restored in the contracts and in Academic with its test. |
| 3 | `row_version` required and `actual_end_date` out of `FichaUpdate` | **Accepted** as incompatible changes before v1. They are declared in this ADR and in the `CHANGELOG.md` of the documentation; the OpenAPI in `07-api` already had them and `shared-contracts#9` aligns the shared contract. The Academic MFE was checked: its edit form already sends `row_version` and no screen sends `actual_end_date` in an update (it sends it only in the status change, which keeps it), so no MFE change is needed. |
| 4 | Program version | Stays as is: the active RAPs of the program at the moment of the transition. Follow-up. |
| 5 | Ficha with no active learners | **It cannot be completed** (`409 ACAD_STATUS_PRECONDITION_FAILED`). |
| 6 | Who records judgments | `SYSTEM_ADMIN`, `CENTER_DIRECTOR` and `COORDINATOR` stay. The instructor, limited to the fichas and RAPs they teach, is the work item HU-ACT-031 (code-sena/design-software-docs#419). |
| 7 | Source of the judgments | Entered in this platform; no SOFIA Plus mirror or import. Follow-up. |
| 8 | Writes after closure | No write block once the ficha is `COMPLETED` or `CANCELLED`. Follow-up. |
| 9 | Product and QA approval | Approved by the owner; this ADR is ACCEPTED. |

## Follow-ups

- **Program version (question 4).** `learning_outcome` has no version dimension and
  there is no `training_program_version` table. A versioned curriculum would let
  the required RAP set follow `enrollment_ficha.program_version`.
- **Source of record (question 7).** If the institution needs SOFIA Plus to be the
  source, a mirror or an import of the evaluative judgments report is a new work
  item.
- **Writes after closure (question 8).** Rejecting judgment writes on a closed
  ficha needs the ficha status from Academic in Actors.
- **Instructor scope (question 6).** HU-ACT-031 (code-sena/design-software-docs#419).
- **Audience default.** The absent-audience allowance of the IAM token endpoint is
  transitional and is removed once every caller sends the audience.

None of these needs a work item of its own until the product asks for it.

## References

- `02-domain/entities-and-rules.md` (RN-ACAD-07, RN-ACT-04)
- `09-microservices/services/06-actors-service/data-model.md`
- `06-data/data-dictionary.md`
- `09-microservices/services/03-academic-management-service/decisions.md`
- `09-microservices/services/03-academic-management-service/data-model.md`
- `09-microservices/services/03-academic-management-service/events.md`
- `07-api/contracts/openapi/academic-management.yaml`
- `07-api/contracts/openapi/actors.yaml`
- `07-api/contracts/openapi/scheduling.yaml`
- `07-api/contracts/openapi/iam.yaml`
- `11-quality/qa-report-r4-security-academic-management.md`
