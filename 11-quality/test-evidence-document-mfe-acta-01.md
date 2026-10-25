# Test Evidence — document-mfe — [HU-DOC-011 / HU-DOC-005, HU-DOC-006, HU-DOC-007]

> Status: 🟡 In progress (unit, integration, coverage, tokens and bundle budget re-run on the final head; E2E, accessibility, Lighthouse and Pact are not re-run, see "Not yet validated") | Last update: 2026-10-24
> Author of the work: `@CristianJPalma` (apprentice, ADSO ficha 3145555) | Adaptation to ADR-022 and ADR-023 and re-run: project owner

## Identification

| Field | Value |
|---|---|
| **User Story** | **HU-DOC-011** ([#424](https://github.com/code-sena/design-software-docs/issues/424)): document-mfe reads the real API through the edge and meets its quality gates. It protects the screens of HU-DOC-005 (generated documents), HU-DOC-006 (document templates) and HU-DOC-007 (versions and download). |
| **Microfrontend** | `design-software-document-mfe` (React 18 + Vite + Module Federation + TypeScript) |
| **Pull Request** | [code-sena/design-software-document-mfe#9](https://github.com/code-sena/design-software-document-mfe/pull/9) |
| **Evaluated HEAD Commit** | [`149377b`](https://github.com/code-sena/design-software-document-mfe/commit/149377b) on `feat/document-mfe-f1-f7` (includes `develop` with the static image served under `/mfe/document/`) |
| **Execution Environment** | Local, Windows, Node 24 (the CI uses Node 22), `design-software-design-system` and `design-software-frontend-platform` at `develop` as sibling folders; the unit and integration tests stub the injected `httpClient` |
| **Execution date** | 2026-10-24 |
| **Decisions** | Rows 06 to 09 of [`decisions.md`](../09-microservices/services/07-document-service/decisions.md) (no new ADR: the decisions are internal to the front end of the document service and rely on [ADR-022](../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md) and [ADR-023](../05-architecture/decisions/records/ADR-023-web-shell-owns-login-and-session.md)) |

## Scope

The remote does not log in, does not read or store the token and does not define its own HTTP client. The shell injects the authenticated `httpClient` and the `permissions` through `remote-props` (ADR-023), and every call goes to the relative base `/document/api/v1` (ADR-022 §3); `/document/api/v1/document-templates` is routed by the edge to `template-api`, the rest to `document-api`.

The shell menu opens `/document/documentos` and `/document/documentos/plantillas`. Without an injected client the remote asks the shell to provide it instead of falling back to local data; the in-memory data only exists in `npm run dev`.

## Executed Test Cases

| TC ID | Description | Command | Expected Result | Actual Result | Status |
|---|---|---|---|---|:---:|
| TC-001 | Type check and lint | `npm run typecheck`; `npm run lint` | No type errors, no lint errors | No errors | **PASS** |
| TC-002 | Unit and integration suite | `npx vitest run --maxWorkers=1 tests/unit tests/integration` | All tests pass | 23 files, 149 tests passed | **PASS** |
| TC-003 | Coverage in `application` and `adapter` (criterion F.2) | `npm run test:coverage -- --maxWorkers=1` | Thresholds of 80 % (statements, branches, functions, lines) enforced in `vite.config.ts` | 92.46 % statements, 81.62 % branches, 89.74 % functions, 94.69 % lines | **PASS** |
| TC-004 | Design token audit (criterion E2) | `check-consumer-tokens --consumer document-mfe` of `design-software-design-system` | 0 local tokens, 0 unknown variables, 0 duplicated canonical values | E2 green for 1 consumer | **PASS** |
| TC-005 | Production build and bundle budget (criterion F.4) | `npm run build`; `npm run budget:bundle` | Build succeeds; `remoteEntry.js`, JS gzip and CSS gzip below `bundle-budget.json` | `remoteEntry.js` 21 091 / 60 000 B; JS gzip 125 203 / 220 000 B; CSS gzip 5 076 / 60 000 B | **PASS** |
| TC-006 | Remote as the shell mounts it | `tests/integration/AppRemote.test.tsx` (6 tests) | Lists documents through the injected client on `/document/api/v1`; opens the template list on the menu route; asks the shell for the client when it is missing; hides the generate action without `DOC_CREATE` and shows it with it; never reads or writes a token | Passed | **PASS** |
| TC-007 | Adapter over the injected client and permission mapping | `tests/unit/remoteHttpClient.test.ts` (9 tests) | Relative same-origin base; GET with its query dropping empty values; JSON and multipart bodies forwarded as they are; failures of the injected client reach the hooks with their message; no token or `Authorization` of its own; session permission codes map to the UI features | Passed | **PASS** |
| TC-008 | States and errors of the three screens | `tests/integration/*.test.tsx`, `tests/unit/mappersAndRepository.test.ts` | Loading, empty and error states with **Reintentar**; a version-history failure is never shown as an empty list; when the template catalog fails the document table keeps its rows and shows `—` as the template code | Passed | **PASS** |

## Execution Output

```text
 Test Files  23 passed (23)
      Tests  149 passed (149)

Statements   : 92.46% ( 601/650 )
Branches     : 81.62% ( 351/430 )
Functions    : 89.74% ( 175/195 )
Lines        : 94.69% ( 571/603 )
```

```text
> npm run budget:bundle
OK   remoteEntry.js: 21091 / 60000 bytes
OK   js total gzip: 125203 / 220000 bytes
OK   css total gzip: 5076 / 60000 bytes
```

```text
> check-consumer-tokens --consumer document-mfe
E2 en verde: 1 consumidores importan @sena/design-system sin tokens locales, referencias inexistentes ni valores canonicos duplicados.
```

## Not yet validated

- **End-to-end (F.1), accessibility (F.3), Lighthouse (F.4) and consumer contracts (F.5)** need the full stack behind the edge (docker-infra, the shell image, this MFE image and the synthetic IAM users). The apprentice reported 17 Playwright scenarios passing, axe with no serious or critical violation, Lighthouse 96 performance / 98 accessibility and both Pact verifications passing **before** the adaptation to ADR-022 and ADR-023. After the adaptation the E2E signs in through the shell login with the synthetic users of IAM (`E2E_*_PASSWORD`, see `.env.example`); it was **not re-run**, and neither were the other three suites. They stay local until the stack is part of the CI.
- The CI of the repository runs lint, types, tokens, coverage, build and bundle budget, and **fails** (does not skip) when `SHELL_DEPS_TOKEN` is missing (HU-SHELL-015, [#368](https://github.com/code-sena/design-software-docs/issues/368)). The run on the final head is the evidence of that job.
- The filters by template and by date are applied by the client on the received page because the contract does not support them (decision 06); the filter does not search across pages.

## Recorded Defects

| BUG ID | Severity | Description | Status |
|---|---|---|:---:|
| BUG-001 | P1 | The previous version of the CI workflow skipped every quality gate and still reported success when the read secret was missing (a green check proved nothing) | Fixed in this PR: the job fails with the reason |
| BUG-002 | P1 | The remote read the access token from `sessionStorage` through a local shim and the CI seeded IAM users with SQL from the MFE repository | Fixed in this PR: injected `httpClient`, seed removed (ADR-023) |

## Traceability

| HU ID | Acceptance criterion | Test cases | Status |
|---|---|---|---|
| HU-DOC-011 | Scenario 1: API through the edge with the shell session | TC-006, TC-007 | PASS |
| HU-DOC-011 | Scenario 2: permissions from the session | TC-006, TC-007 | PASS |
| HU-DOC-011 | Scenario 2: a real `403` from the API reaches the view as an error | TC-008 covers the propagation of errors; the real `403` is part of the E2E, not re-run | Pending |
| HU-DOC-011 | Scenario 3: quality gates | TC-001 to TC-005 | PASS |
| HU-DOC-011 | Scenario 4: E2E, accessibility and contract | not re-run | Pending |

## References

- [Decisions of document-service](../09-microservices/services/07-document-service/decisions.md)
- [QA report of the Document Service](./qa-report-r1-document-service.md)
- [Testing strategy](./testing-strategy.md)
- [Frontend images and the shell](../10-devops/frontend-images.md)
