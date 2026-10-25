# Test Evidence — actors-mfe — [HU-ACT-027 / HU-ACT-011]

> Status: 🟡 In progress (the run against the real backend with a Bearer token is not recorded yet) | Last update: 2026-10-24
> Author of the view: `@Karendaniela09` | Re-run and rework: project owner

## Identification

| Field | Value |
|---|---|
| **User Story** | **HU-ACT-027** ([FRONTEND], [#381](https://github.com/code-sena/design-software-docs/issues/381)): follow-up reports. Backend story: HU-ACT-011 ([#195](https://github.com/code-sena/design-software-docs/issues/195)) |
| **Microfrontend** | `design-software-actors-mfe` (React 18 + Vite + Module Federation + TypeScript) |
| **Pull Request** | [code-sena/design-software-actors-mfe#10](https://github.com/code-sena/design-software-actors-mfe/pull/10) |
| **Evaluated HEAD Commit** | [`1d26e1e`](https://github.com/code-sena/design-software-actors-mfe/commit/1d26e1e9b383c511aab54312f28435b1aa92d2bd) (includes `develop` with the merged activity log and active learners views) |
| **Execution Environment** | Local; `fetch` and the report services are stubbed in the unit tests |
| **Execution date** | 2026-10-24 |

## Scope

The MFE has a "Reportes" view with two read-only reports:

- Learner tracking: `GET /reports/learner-tracking`, filters `ficha_id`, `enrollment_status`, `from`, `to` (ISO dates; `from` inclusive, `to` exclusive).
- Instructor load and availability: `GET /reports/instructor-load`, filters `training_center_id`, `area`, `from`, `to` (RFC 3339 with time zone).

Both accept `page`, `page_size` (maximum 100) and `sort`, answer `data` and `pagination`, require the feature `ACT_REPORT_VIEW` and document `401`, `403` and `429` ([`actors.yaml`](../07-api/contracts/openapi/actors.yaml)). The response types come from the generated types of the contract. The view reports the `403` of the backend; it neither simulates nor grants the permission, and it has no local fallback in demo mode.

## Authentication and Module Federation

The report services use the shared `request` of `src/infrastructure/actors-api.ts`, which sends the session token (`Authorization: Bearer`) like the rest of the MFE. The remote keeps exposing `./App`; the "Reportes" entry is part of the app navigation.

## Executed Test Cases

| TC ID | Description | Command | Expected Result | Actual Result | Status |
|---|---|---|---|---|:---:|
| TC-001 | Global unit test suite | `npx vitest run --maxWorkers=1 --testTimeout=60000` (clean `npm ci`, `design-software-design-system` and `design-software-frontend-platform` at `develop` as sibling folders) | All tests pass | 28 test files, 133 tests passed | **PASS** |
| TC-002 | Type check and production build | `npx tsc -p tsconfig.app.json --noEmit`; `npm run build` | No type errors; `remoteEntry.js` generated | No errors; build succeeded | **PASS** |
| TC-003 | Design token audit (Criterion E2) | `npm run check:tokens` | 0 local tokens, 0 unknown variables, 0 duplicated canonical values | E2 green after replacing the undefined variables and literal values of `reports.css` by tokens | **PASS** |
| TC-004 | Report services | `src/infrastructure/reports-api.test.ts` | Strict validation of the response (UUIDs, enums, dates), filter validation, RFC 3339 dates, error mapping | Passed | **PASS** |
| TC-005 | Reports view | `src/ui/ReportsDashboard.test.tsx` | Filters, sorting, server paging, loading, error with retry, empty result; an old response does not replace a newer query | Passed | **PASS** |
| TC-006 | Navigation | `src/ui/App.test.tsx` | The "Reportes" entry opens the view and requests the report with `{}` filters, page 1, size 20 | Passed | **PASS** |

## Execution Output

```text
 Test Files  28 passed (28)
      Tests  133 passed (133)
```

```text
> npm run check:tokens
E2 en verde: 1 consumidores importan @sena/design-system sin tokens locales, referencias inexistentes ni valores canonicos duplicados.
```

## Not yet validated

- The reports against the real `actors-service` with a Bearer token issued by IAM, and the effective `ACT_REPORT_VIEW` permission in a deployed environment. The unit tests stub `fetch`; there is no E2E script in the repository.
- Backend: the author reports, on `develop` of `actors-service` without changes, 11 tests passing (`ReportsUseCaseImplTest`, `ReportsControllerSecurityTest`) and `ReportsPersistenceAdapterIT` not run (no Docker for Testcontainers). Not re-run here.
- The mockup of the screen is pending design ([#389](https://github.com/code-sena/design-software-docs/pull/389)).

## Recorded Defects

| BUG ID | Severity | Description | Status |
|---|---|---|:---:|
| — | P1 (fixed in `1689a70`) | `reports.css` used CSS variables that do not exist (`--muted`, `--border`, `--shadow`, `--danger`, `--text`) and literal values published as tokens; the E2 token check failed on the first version of the PR. | **RESOLVED** |

## References

- [Pull Request #10 in design-software-actors-mfe](https://github.com/code-sena/design-software-actors-mfe/pull/10)
- [Frontend story HU-ACT-027 in design-software-docs #381](https://github.com/code-sena/design-software-docs/issues/381)
- [Backend issue HU-ACT-011 in design-software-docs #195](https://github.com/code-sena/design-software-docs/issues/195)
- [Actors OpenAPI contract](../07-api/contracts/openapi/actors.yaml)
- [Quality testing strategy](./testing-strategy.md)
