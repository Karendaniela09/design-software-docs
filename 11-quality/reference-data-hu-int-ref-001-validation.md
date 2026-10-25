# HU-INT-REF-001 acceptance evidence

> Status: In review | Last updated: 2026-10-25
> Author/team: Reference Data team

Date: 2026-10-25 (America/Bogota).
Status: local technical validation passed; independent review, shared-environment migration and PR promotion remain pending.
Issue: [docs#294](https://github.com/code-sena/design-software-docs/issues/294).
Specification: [integration guide](../10-devops/reference-data-int-ref-001.md).

## Context

Record reproducible local technical evidence for the ten acceptance criteria without claiming independent approval or promotion.

## Content

### Tested revisions

| Repository | Revision | Branch |
|---|---|---|
| frontend-platform | f5898551c44e33c35d7e00cb627119c6a1148713 | hu-int-ref-001-dev |
| web-shell | d4c91781ed8f1857daf1f25416268758c2a9884b | hu-int-ref-001-dev |
| reference-data-mfe | 00d66302d0c51f65bd66c035501fd30b30acdc8f | hu-int-ref-001-dev |
| reference-data-service | f7070fcf26ce8602d648f9a6cb0da54c91e5f921 | hu-int-ref-001-dev |
| docker-infra | f3b29171408936145059bb01532b67e7ae16c445 | hu-int-ref-001-dev |
| reference-data-db (unchanged dependency) | 5a366feba3c033e216f93930e0863a828346f56e | develop |
| iam-db (unchanged dependency) | 1768e4776f95fd0fd2e71069b6e6738aab04ed8b | develop |
| iam-service (unchanged dependency) | 7358f6d6f25326cd7571e24cf5f2d097c745b0e7 | develop |
| docs contract source | 0f385a82910360c0602faacf7a581fbd5110cfd2 | docs/hu-int-ref-001-integration |

The tested MFE runtime code corresponds to functional commit c134e39a39aab5577d6da9458a9e9f5b276e6e3a. Follow-up commit 00d6630 changes only the Git line-ending policy, not application code. The final Git attributes enforce LF for the pinned input hashes on Windows and Linux.

## Ten-criterion matrix

| Criterion | Local result | Evidence |
|---|---|---|
| 1. Clean database and repeatable migrations | PASS | A new Compose project created a fresh PostgreSQL data volume. IAM applied 40 changesets and Reference Data applied 21. A second Reference Data update applied zero changesets; schema and data dumps were identical. SQL checked the nine business tables, constraints, indexes, grants and agreed hierarchy seeds. Three existing R1 tables were preserved. |
| 2. Non-admin application login | PASS | API DSN uses hu020_reference, separate from validation_owner. SQL rejected superuser/create-role/create-db/replication/bypass-RLS attributes, checked both role memberships and executed SET LOCAL ROLE reader plus a rolled-back writer transaction. |
| 3. Public URL and rewrite | PASS | The real MFE called /reference-data/api/v1/training-centers through the canonical Traefik table. The browser assertion rejected root-level resource requests. The shared-client integration test asserts exactly one domain/API prefix and a Bearer header. |
| 4. Real remote and IAM permissions | PASS | Production shell/MFE images, same-origin manifest, referenceDataMfe ./App and the actual data-mfe="reference-data" element were exercised. Read/write and restricted-scope accounts produced different controls. Standalone main.tsx permissions were not imported by the shell. |
| 5. Authenticated platform client | PASS | Browser login used real IAM; real API requests used the injected client. Browser storage contained no sena.access_token. The refresh cookie was HttpOnly/Secure/SameSite=Strict with Path /iam/api/v1/auth. Reload restored the session through refresh and me. |
| 6. JWT and JWKS verification | PASS | Real IAM tokens were accepted; malformed tokens were rejected. Go security tests cover RS256, signature mismatch, wrong issuer, missing/expired claims, future nbf, key rotation/cache/unknown-kid cooldown and unavailable JWKS. The isolated Go unit suite passed without external fixtures. Reference Data contains no IAM database lookup or role reconstruction. |
| 7. Read/write separation and errors | PASS | For hierarchy, catalogs and parameters: missing/invalid Bearer returned 401; a real IAM read-only account read successfully and received 403 on writes; a restricted-scope account received 403; ADMIN_STAFF created a row in each group. Shared error assertions checked error.code, message and trace_id. Go middleware tests additionally cover all six features. |
| 8. Scope-preserving normalization | PASS | The canonical IAM matrix specifies GLOBAL for all six REF features. A synthetic IAM role issued TRAINING_CENTER grants: backend requests were denied and the browser did not show global controls. Platform tests reject bare/narrow/malformed REF grants and intersect scoped token grants with IAM identity codes. |
| 9. Reproducible generated types | PASS | Both OpenAPI inputs are pinned to docs commit 0f385a8 with SHA-256 hashes. Geography and institutional DTOs are generated aliases rather than manual copies. check:types passed locally and inside the MFE Docker build; CI also runs it. README instructions were updated. |
| 10. Probes and browser-to-database proof | PASS | The browser displayed the center created through the public API; a direct SQL assertion confirmed that center and the new catalog/parameter rows in PostgreSQL. Stopping PostgreSQL made public readiness return 503 while public liveness stayed 200. Restarting it restored readiness 200. |

## Executed checks

| Check | Result |
|---|---|
| frontend-platform npm test -- --maxWorkers=2 | 7 files, 63 tests passed |
| frontend-platform typecheck | Passed |
| reference-data-mfe npm test | 17 files, 75 tests passed |
| reference-data-mfe typecheck, lint, check:types | Passed |
| web-shell npm test -- --maxWorkers=2 | 18 files, 160 tests passed |
| web-shell typecheck:e2e and lint | Passed |
| web-shell generic Playwright collection | 4 generic specs collected; the mandatory real integration suite is separate |
| reference-data-service go test ./... | Passed; unrelated integration cases retain their existing environment guards |
| Isolated Go security/health/API package suite, count=1 | All three packages passed |
| Production shell and MFE Docker builds | Passed; MFE build also checked contract hashes and regenerated-type equality |
| Dedicated real API/browser suite | 4 passed, 0 failed, 0 skipped |
| Docs OpenAPI CI script against main | Passed: 0 errors, 3 non-blocking warnings |
| Docs relative links and personal-data checks | Passed |

The generic Go command is not presented as proof of its unrelated R1 chaos cases. The dedicated integration suite uses mandatory credentials and does not permit skipped tests. No mocks substitute IAM, PostgreSQL, the edge or Reference Data in that suite.

## Reproduction and sanitized result

Final fresh project: `macro-ref-int001-acceptance`. Loopback origin: `http://localhost:18120`.

```powershell
# From docker-infra; the default creates a new isolated project.
./validation/int-ref-001/run.ps1
```

The final acceptance run passed after creating a new database. The isolated Go package suite was also executed directly with the same Compose configuration; the saved runner now invokes that suite automatically. Dependency caches are reusable, but database/signing-key volumes are project-specific.

Sanitized final result: status=passed, criteria=1..10, integrated tests=4, skipped=0. Local detailed artifacts are ignored under validation/int-ref-001/evidence and web-shell/test-results. Generated passwords and tokens are not included in this report or Git. The runner leaves the isolated services available for review and preserves data volumes.

## Review limits and merge order

This is technical evidence from the isolated macroproject checkout, not independent QA/Architecture approval or evidence of migrations in shared develop. No PR was published or merged during this implementation. Review the docs contract and GLOBAL-only policy, merge frontend-platform before its shell consumer, then coordinate the remaining code/infra delivery and shared-environment validation.

Other domain remotes are intentionally absent from this isolated stack. Federation retries their failed entries and can delay initial/reload rendering; the integration test uses a bounded 30-second remote-mount expectation. Reference Data loads and session restoration succeeds despite those missing remotes. No performance claim or full-macroproject deployment claim is made.

## References

- [HU-INT-REF-001](https://github.com/code-sena/design-software-docs/issues/294).
- [Authentication](../07-api/authentication.md).
- [Git conventions](../00-governance/git-conventions.md).
