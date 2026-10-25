# Test Evidence — actors-mfe — [HU-ACT-028 / HU-ACT-010]

> Status: 🟡 In progress (the run against the real backend with a Bearer token is not recorded yet) | Last update: 2026-10-24
> Author of the first attempt: `@Karendaniela09` | Rebuild on the layers and re-run: project owner

## Identification

| Field | Value |
|---|---|
| **User Story** | **HU-ACT-028** ([FRONTEND], [#382](https://github.com/code-sena/design-software-docs/issues/382)): improvement plans of instructors and learners. Backend story: HU-ACT-010 ([#194](https://github.com/code-sena/design-software-docs/issues/194)) |
| **Microfrontend** | `design-software-actors-mfe` (React 18 + Vite + Module Federation + TypeScript) |
| **Pull Request** | [code-sena/design-software-actors-mfe#8](https://github.com/code-sena/design-software-actors-mfe/pull/8) |
| **Evaluated HEAD Commit** | [`0e67e53`](https://github.com/code-sena/design-software-actors-mfe/commit/0e67e53860f97c7494d00abc88d389b5b5fdfaef) (includes `develop` with the merged activity log and active learners views) |
| **Execution Environment** | Local, mock mode of the MFE (`VITE_ACTORS_API_MODE=mock`) for the UI tests; `fetch` stubbed for the HTTP client tests |
| **Execution date** | 2026-10-24 |

## Scope

The screen manages the **individual** improvement plan of an instructor or a learner (`actors_tracking.actor_improvement_plan`, rule RN-ACT-06). The plan of a ficha (`monitoring.improvement_plan`) is a different concept with its own screen in `monitoring-mfe` (HU-MON-008); see decision 12 in [`decisions.md`](../09-microservices/services/06-actors-service/decisions.md) of the actors service.

Operations of the contract ([`actors.yaml`](../07-api/contracts/openapi/actors.yaml)), relative to `/api/v1` (public path `/actors/api/v1`, ADR-022 §3): `GET /improvement-plans` (filters `instructor_id`, `learner_id`, `status_id`; `page`, `page_size`), `GET /improvement-plans/{id}`, `POST /improvement-plans` and `PUT /improvement-plans/{id}`. Permissions are the ones of the contract: read `ACT_ACTIVITY_LOG_VIEW`, write `ACT_PRODUCTIVE_STAGE_MANAGE`; the backend validates them and the view hides the write controls unless the shell passes `canManagePlans`.

A write is confirmed by re-reading the plan from the server before the screen reports success; if the re-read fails or does not reflect what was sent, the save is reported as not confirmed.

## Executed Test Cases

| TC ID | Description | Command | Expected Result | Actual Result | Status |
|---|---|---|---|---|:---:|
| TC-001 | Global unit test suite | `npx vitest run --maxWorkers=1 --testTimeout=60000` (clean `npm ci`, `design-software-design-system` and `design-software-frontend-platform` at `develop` as sibling folders) | All tests pass | 30 test files, 147 tests passed; 32 files and 155 tests with `design-software-actors-mfe#10` merged on top | **PASS** |
| TC-002 | Type check and production build | `npx tsc -p tsconfig.app.json --noEmit`; `npm run build` | No type errors; `remoteEntry.js` generated | No errors; build succeeded | **PASS** |
| TC-003 | Design token audit (Criterion E2) | `npm run check:tokens` | 0 local tokens, 0 unknown variables, 0 duplicated canonical values | E2 green | **PASS** |
| TC-004 | Domain rules | `src/domain/improvement-plan.test.ts` (5 tests) | Exactly one actor in the body; UUID, date and text validation; update with only the changed fields and never `completed_at`; re-read check | Passed | **PASS** |
| TC-005 | HTTP client | `src/infrastructure/improvement-plans-http.test.ts` (3 tests) | Contract paths and query (`page`, `page_size`, filters), bodies of POST and PUT, `Authorization: Bearer <session token>`, backend error mapped to `ApiError` | Passed | **PASS** |
| TC-006 | List, filters and paging | `src/application/useImprovementPlans.test.tsx`, `src/ui/ImprovementPlansPage.test.tsx` | The list loads; the filters go back to page 1; a value that is not a UUID is rejected; retry after an error | Passed | **PASS** |
| TC-007 | Create with confirmation | same files | Required fields validated before sending; POST then GET of the created plan; the list shows it | Passed | **PASS** |
| TC-008 | Update with confirmation | same files | Detail and edit; PUT then GET; a server that does not reflect the change is reported; the closing status fills `completed_at` in the mock like the backend | Passed | **PASS** |
| TC-009 | Shell integration points | `src/ui/ImprovementPlansPage.test.tsx` | `StatusSelector` and `statusLabels` of the shell replace the UUID field; `canManagePlans={false}` hides create and edit | Passed | **PASS** |

## Execution Output

```text
 Test Files  30 passed (30)
      Tests  147 passed (147)
```

```text
> npm run check:tokens
E2 en verde: 1 consumidores importan @sena/design-system sin tokens locales, referencias inexistentes ni valores canonicos duplicados.
```

## Not yet validated

- The screen against the real `actors-service` with a Bearer token issued by IAM (200 with the features above, 403 without them). The unit tests stub `fetch`; there is no E2E script in the repository.
- Actor and status are typed as UUIDs unless the shell injects `StatusSelector`; there is no actor picker yet.
- The mockup of the screen is pending design ([#389](https://github.com/code-sena/design-software-docs/pull/389)).

## Recorded Defects

| BUG ID | Severity | Description | Status |
|---|---|---|:---:|
| — | P1 (fixed by the rebuild) | The first attempt was a parallel mock-first application that read the token from `window` globals, with its own CI workflow, dependency changes and an ADR inside the repository. | **RESOLVED** |

## References

- [Pull Request #8 in design-software-actors-mfe](https://github.com/code-sena/design-software-actors-mfe/pull/8)
- [Frontend story HU-ACT-028 in design-software-docs #382](https://github.com/code-sena/design-software-docs/issues/382)
- [Backend issue HU-ACT-010 in design-software-docs #194](https://github.com/code-sena/design-software-docs/issues/194)
- [Actors OpenAPI contract](../07-api/contracts/openapi/actors.yaml)
- [Quality testing strategy](./testing-strategy.md)
