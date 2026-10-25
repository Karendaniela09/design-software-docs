# Test Evidence — actors-mfe — [HU-ACT-012 / HU-ACT-026]

> Status: 🟡 In progress (the run against the real backend with a Bearer token is not recorded yet) | Last update: 2026-10-24
> Author: Laura Vanessa Pérez Perdomo (`@vanessaperdomo`) | Team: QA / Actors MFE
> Evaluating Instructor: Jesús Ariel González Bonilla
> QA Reviewers: Danna Barrios (`@Dannabarrios`), Andrey Culma (`@Andrey31072`)

---

## Identification

| Field | Value |
|---|---|
| **User Story** | **HU-ACT-026** ([FRONTEND], [#380](https://github.com/code-sena/design-software-docs/issues/380)): active learners by ficha. Backend story: HU-ACT-012 ([#196](https://github.com/code-sena/design-software-docs/issues/196)) |
| **Microfrontend** | `design-software-actors-mfe` (React 18 + Vite + Module Federation + TypeScript) |
| **Integration Backend** | `actors-service`: `GET /learners?ficha_id=&enrollment_status_id=&page=&limit=` (contract `actors.yaml`, feature `ACT_LEARNER_VIEW`) |
| **Pull Request** | [code-sena/design-software-actors-mfe#13](https://github.com/code-sena/design-software-actors-mfe/pull/13) |
| **Evaluated HEAD Commit** | [`8d6e6dc`](https://github.com/code-sena/design-software-actors-mfe/commit/8d6e6dc) |
| **Tester / Developer** | Laura Vanessa Pérez Perdomo (`@vanessaperdomo`); independent re-run by the project owner |
| **Execution Environment** | Local, mock mode of the MFE (`VITE_ACTORS_API_MODE=mock`) for the UI tests; `fetch` stubbed for the HTTP client tests |
| **Execution date** | 2026-10-24 |
| **Institutional Framework** | Improvement Plan — Acta 01-2026 (Items 8 and 9) and Acta 02-2026 (Items 7 and 14) |

The view changed after the first evidence of this document (2026-10-21): the count no longer comes from the service-to-service endpoint `/internal/fichas/{id}/active-learners/count` but from `pagination.total_items` of the list request; the stage cards and the stage filter were removed because `GET /learners` does not return the stage; the ficha is a UUID. This document describes the view of `8d6e6dc`.

---

## Executed Test Cases

| TC ID | AC ID | Description | Precondition | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|:---:|
| **TC-001** | AC-001 | Global unit test suite | Dependencies installed (clean `npm ci`), `design-software-design-system` and `design-software-frontend-platform` at `develop` as sibling folders | 1. Run `npx vitest run --maxWorkers=1`. | 26 test files and 125 tests passing. | 26 files and 125 tests. At the first run 122 passed; 3 existing tests (`ActorStatusParametrization` E1 and two in `App.test.tsx`) exceeded the 5 s default timeout because the PC was out of memory, and the 17 tests of those two files pass with `--testTimeout=60000`. | **PASS** |
| **TC-002** | AC-002 | Design token audit (Criterion E2) | Style rules configured | 1. Run `npm run check:tokens`. | 0 local tokens, 0 broken references, 0 duplicated canonical values. | E2 green. | **PASS** |
| **TC-003** | AC-003 | HTTP client of the list endpoint | `fetch` stubbed | 1. Run `npx vitest run src/infrastructure/learner-http.test.ts`. | The request is `/api/v1/learners?page=1&limit=20&ficha_id=…` (plus `enrollment_status_id=…` when given) and carries `Authorization: Bearer <session token>`. | 3 tests passed (2 existing and `asks the list endpoint for the learners of a ficha and sends the session token`). | **PASS** |
| **TC-004** | AC-004 | Clean TypeScript compilation and production build | Vite Module Federation configuration | 1. Run `npx tsc -p tsconfig.app.json --noEmit`.<br>2. Run `npm run build`. | No type errors; `dist/remoteEntry.js` generated. | Type check without errors; build succeeded in 1 min 41 s. | **PASS** |
| **TC-005** | AC-005 | Count from the list request | Mock mode | 1. Run `src/application/useActiveLearnersByFicha.test.tsx` and `src/ui/ActiveLearnersByFicha.test.tsx`. | One call to `listLearners(1, { ficha_id })`; the count card shows `pagination.total_items`; no call to `/internal/...`. | `takes the count from pagination.total_items of the same list request` and `lists the learners of the ficha and shows the total of the list request as the count` passed. | **PASS** |
| **TC-006** | AC-006 | Learner table | Ficha with a learner | 1. Load the demo ficha. | Columns document, full name, email (mailto link) and phone; no stage column. | Passed in `ActiveLearnersByFicha.test.tsx`. | **PASS** |
| **TC-007** | AC-007 | Search over the loaded page | Learner roster visible | 1. Type a term in the search box. | The table filters by document, name or email, case-insensitive; with no match the message says so. | Passed in `ActiveLearnersByFicha.test.tsx` and `active-learners.test.ts` (domain). | **PASS** |
| **TC-008** | AC-008 | Ficha as UUID | No ficha chosen | 1. Type `3145555` and submit.<br>2. Type the UUID of the demo ficha and submit.<br>3. Repeat with the `FichaSelector` injected by the shell. | The ficha number is rejected without calling the API; the UUID loads the learners; the selector of the shell replaces the text field. | Passed in `ActiveLearnersByFicha.test.tsx`. | **PASS** |
| **TC-009** | AC-009 | Active enrollments only | `activeEnrollmentStatusId` given | 1. Run the hook with the status id. | The request adds `enrollment_status_id`; the mock filters on the current enrollment. | Passed in `useActiveLearnersByFicha.test.tsx` and `learner-mock.test.ts`. | **PASS** |
| **TC-010** | AC-010 | Resilience | API error and empty ficha | 1. Make the API fail once.<br>2. Open a ficha without learners. | Alert with the message and retry button that recovers; empty state with count 0. | Passed in `ActiveLearnersByFicha.test.tsx` and `useActiveLearnersByFicha.test.tsx`. | **PASS** |

---

## Execution Output: Global Unit Test Suite

```text
 Test Files  2 failed | 24 passed (26)
      Tests  3 failed | 122 passed (125)
```

The three failures were timeouts above 5 s (11.3 s, 5.5 s and 5.2 s) of tests that this branch does not touch, with the PC out of memory. Run alone with a larger timeout:

```text
> npx vitest run --maxWorkers=1 --testTimeout=60000 src/ui/ActorStatusParametrization.test.tsx src/ui/App.test.tsx
 Test Files  2 passed (2)
      Tests  17 passed (17)
```

## Execution Output: Tests of the View

```text
> npx vitest run --maxWorkers=1 --no-file-parallelism src/domain/active-learners.test.ts src/application/useActiveLearnersByFicha.test.tsx src/ui/ActiveLearnersByFicha.test.tsx src/infrastructure/learner-http.test.ts src/infrastructure/learner-mock.test.ts
 Test Files  5 passed (5)
      Tests  20 passed (20)
```

## Execution Output: Token Audit (Criterion E2)

```text
> npm run check:tokens
E2 en verde: 1 consumidores importan @sena/design-system sin tokens locales, referencias inexistentes ni valores canonicos duplicados.
```

---

## Not yet validated

- The view against the real `actors-service` with a Bearer token issued by IAM (200 with the `ACT_LEARNER_VIEW` feature, 403 without it). The unit tests stub `fetch`.
- The count of active enrollments only (`activeEnrollmentStatusId`) depends on the shell injecting the id of the "active" enrollment status; without it the card says "Con inscripción vigente".
- The mockup of the screen is pending design ([#389](https://github.com/code-sena/design-software-docs/pull/389)).

---

## Recorded Defects

| BUG ID | TC ID | Severity | Description | Evidence | Status |
|---|---|---|---|---|:---:|
| — | — | — | No open defects in the executed cases. | Test execution logs above | **RESOLVED** |

---

## Traceability

| HU ID | AC ID | TC ID | Status |
|---|---|---|:---:|
| HU-ACT-026 | AC-001 | TC-001 | **PASS** |
| HU-ACT-026 | AC-002 | TC-002 | **PASS** |
| HU-ACT-026 | AC-003 | TC-003 | **PASS** |
| HU-ACT-026 | AC-004 | TC-004 | **PASS** |
| HU-ACT-026 | AC-005 | TC-005 | **PASS** |
| HU-ACT-026 | AC-006 | TC-006 | **PASS** |
| HU-ACT-026 | AC-007 | TC-007 | **PASS** |
| HU-ACT-026 | AC-008 | TC-008 | **PASS** |
| HU-ACT-026 | AC-009 | TC-009 | **PASS** |
| HU-ACT-026 | AC-010 | TC-010 | **PASS** |

---

## References

- [Pull Request #13 in design-software-actors-mfe](https://github.com/code-sena/design-software-actors-mfe/pull/13)
- [Frontend story HU-ACT-026 in design-software-docs #380](https://github.com/code-sena/design-software-docs/issues/380)
- [Backend issue HU-ACT-012 in design-software-docs #196](https://github.com/code-sena/design-software-docs/issues/196)
- [Actors OpenAPI contract](../07-api/contracts/openapi/actors.yaml)
- [Quality testing strategy](./testing-strategy.md)
- [Git conventions](../00-governance/git-conventions.md)
