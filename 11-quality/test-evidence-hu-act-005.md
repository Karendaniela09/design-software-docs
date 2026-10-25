# Test Evidence — Horarios SENA — [HU-ACT-005 / Sprint 04]

> Status: 🟡 In progress (the visual validation against the real backend with Bearer/IAM authentication is still pending) | Last update: 2026-10-24
> Author: Laura Vanessa Pérez Perdomo (`@vanessaperdomo`) | Team: QA / Actors MFE

## Identification

| Field | Value |
|---|---|
| User Story / Sprint | HU-ACT-005 / Sprint 04 (Improvement Plan — Acta 01-2026) |
| Component | `actors-mfe` (`design-software-actors-mfe`) |
| Pull Request | [code-sena/design-software-actors-mfe#12](https://github.com/code-sena/design-software-actors-mfe/pull/12) |
| Evaluated HEAD Commit | [`e3642c3`](https://github.com/code-sena/design-software-actors-mfe/commit/e3642c3077b59b610dc3e8b78635ee39165813b0) (adds the session token to the activity log requests on top of the `develop` merge [`69613f7`](https://github.com/code-sena/design-software-actors-mfe/commit/69613f7); QA fixes verified in [`40aaa35`](https://github.com/code-sena/design-software-actors-mfe/commit/40aaa35f7862096ef58e7d80ad1f9d3b8c1282c5)) |
| Tester | Laura Vanessa Pérez Perdomo (`@vanessaperdomo`) |
| Environment | dev / local (`http://localhost:5106`) |
| Execution date | 2026-10-24 (Updated post QA review) |
| Related backend | `actors-service` (Java / Spring Boot / OpenAPI `actors.yaml`) |
| Frontend user story | [HU-ACT-025](https://github.com/code-sena/design-software-docs/issues/379) |

---

## Validation Context and Scope

This evidence certifies the functional, technical, and HTTP integration validation of the **Activity Log Timeline** component in `actors-mfe` for instructors and learners, in compliance with the Improvement Plan commitments (Acta 01-2026, Items 8 and 9) and linked to backend user story [#189](https://github.com/code-sena/design-software-docs/issues/189).

---

## Executed Test Cases

| TC ID | AC ID | Description | Precondition | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|:---:|
| TC-001 | AC-001 | Full Vitest unit test suite | Dependencies installed in `actors-mfe` | 1. Run `npm test` at the microfrontend root. | 23 test files and 108 tests green (99 tests at commit `40aaa35`; 106 after merging `develop` post PRs #14/#16 at `69613f7`; 108 at `e3642c3`, with the 2 tests of the `Authorization` header). | 23 files passed, 108 tests passed in 69.31 s (clean `npm ci`, commit `e3642c3`). | **PASS** |
| TC-002 | AC-002 | Canonical design token validation (Criterion E2) | Clean `hu-005-dev` branch | 1. Run `npm run check:tokens`. | 0 local tokens, 100% canonical `@sena/design-system`. | E2 green with no broken references. | **PASS** |
| TC-003 | AC-003 | HTTP API client integration (`activity-log-api`) | `actors-service` backend or HTTP mock | 1. Run `npx vitest run src/infrastructure/activity-log-api.test.ts`. | 7 tests passing: 3 of the mock client and 4 of the HTTP client (session token sent as `Authorization: Bearer`, no header without a token, URL and cursor query, `ApiError` on 403). | 7 passed in 4.43 s (commit `e3642c3`). | **PASS** |
| TC-004 | AC-004 | Clean TypeScript compilation and production build | Vite Module Federation configuration | 1. Run `npm run build`. | Clean `tsc -b` and `dist/remoteEntry.js` generated without type errors. | Build succeeded in 55.76 s (`remoteEntry.js` 23.88 kB, commit `e3642c3`). | **PASS** |
| TC-005 | AC-005 | Activity log in instructor detail modal | Dev server running (`localhost:5106`) | 1. Go to `#instructores`.<br>2. Open instructor detail.<br>3. Click the "Bitácora" tab. | Vertical chronological timeline with institutional badges, change diffs (`INACTIVE ➔ ACTIVE`), and `es-CO` date format. | Timeline rendered with institutional date format and visual diffs. | **PASS** |
| TC-006 | AC-006 | Activity log in learner detail modal | Dev server running (`localhost:5106`) | 1. Go to `/aprendices`.<br>2. Open learner detail.<br>3. Click the "Bitácora" tab. | Enrollment and training-stage events rendered without style collisions with other tabs. | Timeline rendered cleanly without modal interference. | **PASS** |
| TC-007 | AC-007 | Real-time reactive search with 300 ms debounce | Activity log open with records | 1. Type a term in the search box (e.g. `"ACTIVO"` or `"CONTRATO"`). | Smooth debounced filtering with 300 ms delay without full reloads. | Real-time debounced filtering verified with timer simulation. | **PASS** |
| TC-008 | AC-008 | Event type filter | Activity log open with mixed events | 1. Open event type menu.<br>2. Select `STATUS_CHANGED`. | Only records matching the selected category are displayed. | Filtered list shows only the selected category. | **PASS** |
| TC-009 | AC-009 | Incremental cursor pagination (append-only) | Dataset larger than the limit (`has_more: true`) | 1. Click "Cargar más actividades". | `cursor={next_cursor}` query param sent to backend; new items appended without losing scroll position. | New records appended preserving reading position. | **PASS** |
| TC-010 | AC-010 | Resilience, async states, and zero hardcoded data | HTTP client connected | 1. Inspect requests in DevTools Network.<br>2. Simulate loading and 4xx/5xx error states. | Animated skeleton while loading, empty state when no data, retry panel on API errors. | Skeleton UI during fetch and resilient handling with institutional alerts. | **PASS** |

---

## Execution Output: HTTP Integration Test against `actors-service` Contract

Execution of the HTTP client integration suite in `src/infrastructure/activity-log-api.test.ts`:

```text
 Test Files  1 passed (1)
      Tests  7 passed (7)
   Start at  18:33:23
   Duration  4.43s
```

The 7 tests are: `returns paginated activity log entries for demo instructor`, `returns next page when cursor is provided`, `returns fallback log for unknown learner` (mock client); `sends the session access token as a Bearer header`, `does not send an Authorization header when there is no session token`, `fetches instructor activity log using correct URL and cursor query`, `throws ApiError with message when server returns 403 Forbidden` (HTTP client).

## Execution Output: Global Unit Test Suite (Post QA Fixes & Develop Merge)

Evaluated over HEAD commit `e3642c3` (verified at commit `40aaa35` with 99 tests and at `69613f7` with 106 tests):

```text
 Test Files  23 passed (23)
      Tests  108 passed (108)
   Start at  18:29:40
   Duration  69.31s
```

> **Note on test count evolution:** The initial submission documented 97 tests. Following the QA audit (`REVISION_QA_HU_ACT_005_RESULTADO.md`), two new automated unit tests were incorporated to verify the 300 ms debounce behavior (`useActivityLog > debounces filterText search by 300ms before recalculating visible items`) and the pagination button copy (`ActivityLogTimeline Component > renders "Cargar más actividades" button when more items are available`), bringing the total verified suite to 99 tests (commit `40aaa35`). Subsequently, after merging `develop` (incorporating PRs #14 and #16), the suite grew to 106 tests across 23 files (commit `69613f7`). Finally, commit `e3642c3` fixes the HTTP client so that the activity log requests carry the session token (`Authorization: Bearer`, the same helper that `develop` uses after PR #14); without it the real backend answers 401. Its two tests bring the suite to 108 tests across 23 files, with zero regressions.

## Execution Output: Token & Zero-Hardcode Verification

```text
> npm run check:tokens
E2 en verde: 1 consumidores importan @sena/design-system sin tokens locales, referencias inexistentes ni valores canonicos duplicados.

> node ../design-software-design-system/scripts/check-no-hardcode.mjs
E4 en verde: ningun componente hardcodea color ni espaciado.
```

## Execution Output: Production Build (Module Federation)

```text
> npm run build
✓ built in 55.76s
dist/remoteEntry.js  23.88 kB
```

### Independent re-run (2026-10-24)

The unit tests, the type check, the build and the token check were repeated by the project owner on `e3642c3`, from a clean `npm ci`, with `design-software-design-system` and `design-software-frontend-platform` at `develop` as sibling folders: `tsc -p tsconfig.app.json --noEmit` without errors, `npm test` 23 files and 108 tests passed, `npm run check:tokens` E2 green, `npm run build` succeeded.

### Not yet validated

The visual validation of the timeline against the real `actors-service` with a Bearer token issued by IAM has not been recorded. TC-005 and TC-006 were run by the author in the development server; the unit tests cover the `Authorization` header, but not the full flow. QA records that validation when the stack with IAM and actors is available; this document stays 🟡 until then.

---

## Recorded Defects

| BUG ID | TC ID | Severity | Description | Evidence | Status |
|--------|-------|----------|-------------|----------|:------:|
| — | — | — | **0 blocking defects (P0)** and **0 major defects (P1)**. The feature meets all acceptance criteria. | Test execution logs above | **RESOLVED** |

---

## Traceability

| HU ID | AC ID | TC ID | Status |
|-------|-------|-------|:------:|
| HU-ACT-005 | AC-001 | TC-001 | **PASS** |
| HU-ACT-005 | AC-002 | TC-002 | **PASS** |
| HU-ACT-005 | AC-003 | TC-003 | **PASS** |
| HU-ACT-005 | AC-004 | TC-004 | **PASS** |
| HU-ACT-005 | AC-005 | TC-005 | **PASS** |
| HU-ACT-005 | AC-006 | TC-006 | **PASS** |
| HU-ACT-005 | AC-007 | TC-007 | **PASS** |
| HU-ACT-005 | AC-008 | TC-008 | **PASS** |
| HU-ACT-005 | AC-009 | TC-009 | **PASS** |
| HU-ACT-005 | AC-010 | TC-010 | **PASS** |

---

## RBAC Security and Real HTTP Mode Validation (`ACT_ACTIVITY_LOG_VIEW`)

### 1. Authority Definition and RBAC Seed

- **Institutional permission:** `ACT_ACTIVITY_LOG_VIEW` ("View actor activity log", `READ` level).
- **IAM registration:** Documented in [09-microservices/services/01-iam-service/rbac-design.md](../09-microservices/services/01-iam-service/rbac-design.md).
- **OpenAPI contract:** Specified in [07-api/contracts/openapi/actors.yaml](../07-api/contracts/openapi/actors.yaml) with `x-required-feature: ACT_ACTIVITY_LOG_VIEW` on all activity log operations (`/api/v1/instructors/{id}/activity-log` and `/api/v1/learners/{id}/activity-log`).

### 2. Verified HTTP Behavior Matrix

| Authorization Scenario | Header / Authority | Endpoint | Expected HTTP Code | System Behavior |
|---|---|---|:---:|---|
| **Authorized user** | `Bearer <token>` with `ACT_ACTIVITY_LOG_VIEW` | `GET /api/v1/instructors/{id}/activity-log` | **200 OK** | Returns JSON payload with `data` (chronological list) and cursor metadata (`has_more`, `next_cursor`, `limit`). |
| **Authorized user** | `Bearer <token>` with `ACT_ACTIVITY_LOG_VIEW` | `GET /api/v1/learners/{id}/activity-log` | **200 OK** | Returns learner event payload with cursor pagination. |
| **Unauthorized user** | `Bearer <token>` without `ACT_ACTIVITY_LOG_VIEW` | `GET /api/v1/instructors/{id}/activity-log` | **403 Forbidden** | Access denied. Frontend intercepts via `ApiError` and shows a warning banner with retry. |
| **Unauthenticated** | No `Authorization` header | `GET /api/v1/instructors/{id}/activity-log` | **401 Unauthorized** | Immediate rejection at the gateway / security filter. |

### 3. Backend and Frontend Code Traceability

- **Backend (`actors-service`):** Protected by declarative controller annotation:

  ```java
  @PreAuthorize("hasAuthority('ACT_ACTIVITY_LOG_VIEW')")
  @GetMapping("/instructors/{id}/activity-log")
  ```

  Validated in `ActivityLogControllerIT.java` (`shouldFindInstructorActivityLogViaHttp`, `shouldFindLearnerActivityLogViaHttp`, `shouldReturn403WithoutCorrectRole`, `shouldReturn401WithoutAuth`).

- **Frontend (`actors-mfe`):** The `httpActivityLogApi` client propagates session headers and maps 403 Forbidden to a typed `ApiError`:

  ```typescript
  // src/infrastructure/activity-log-api.test.ts
  it('throws ApiError with message when server returns 403 Forbidden')
  ```

---

## References

- [Pull Request #12 in actors-mfe](https://github.com/code-sena/design-software-actors-mfe/pull/12)
- [Backend issue HU-ACT-005 in design-software-docs #189](https://github.com/code-sena/design-software-docs/issues/189)
- [Actors OpenAPI contract](../07-api/contracts/openapi/actors.yaml)
- [IAM RBAC design](../09-microservices/services/01-iam-service/rbac-design.md)
- [Quality testing strategy](./testing-strategy.md)
- [Git conventions](../00-governance/git-conventions.md)
