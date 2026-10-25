# HU-INT-REF-001: Reference Data integration

> Status: In review | Last updated: 2026-10-25
> Author/team: Reference Data team

Status: implementation candidate, pending independent review and promotion.
Issue: [docs#294](https://github.com/code-sena/design-software-docs/issues/294).

## Context

Connect the existing Reference Data database, IAM session, remote and edge without broadening permissions. This document defines the contract and environment used to validate docs#294.

## Content

### Contract and authorization baseline

The contract for this delivery is `07-api/contracts/openapi/reference-data.yaml` and its relative `_shared.yaml` in this repository. The delivery starts from docs revision `a0eeb96c4db2bf67c1c599fe4016d95566dddcff` and adds an explicit 503 `DEPENDENCY_UNAVAILABLE` response to protected operations when signing keys cannot be obtained. The MFE vendors these two build inputs with SHA-256 hashes and records the exact source commit in `contracts/openapi/source.json`. Its `check:types` command rejects modified inputs or stale output. This is a pinned build artifact, not a second authority for editing the API.

The existing IAM RBAC matrix (`09-microservices/services/01-iam-service/rbac-design.md`, MOD_REFERENCE) grants all six Reference Data features with **GLOBAL** scope:

| Resource group | Read | Write | Supported scope |
|---|---|---|---|
| Institutional hierarchy, centers and units | REF_HIERARCHY_VIEW | REF_HIERARCHY_MANAGE | GLOBAL |
| Catalogs and catalog details | REF_CATALOG_VIEW | REF_CATALOG_MANAGE | GLOBAL |
| Parameters | REF_PARAMETER_VIEW | REF_PARAMETER_MANAGE | GLOBAL |

The API accepts `CODE:GLOBAL` for the exact required feature. `TRAINING_CENTER`, `AREA`, ownership scopes and missing scopes do not grant global access. This delivery does not invent a center-filtering policy. Introducing center-scoped reference operations requires a new explicit contract and data-filtering implementation first. Roles are issued by IAM; Reference Data neither reconstructs role grants nor queries IAM's database.

IAM's `/auth/me` returns bare feature codes, while the access JWT carries `CODE:SCOPE_TYPE`. The platform computes Reference Data presentation permissions by intersecting `/auth/me` codes with GLOBAL grants from the in-memory token. JWT payload decoding in the browser is only for presentation: backend RS256 signature, issuer, expiration and scoped feature checks remain authoritative. A missing, malformed or unsupported grant fails closed. The shell passes only the authenticated HTTP port, identity and presentation permissions to the remote. It does not pass the token or import standalone demonstration permissions.

## Public paths and environments

The same relative paths apply in develop, qa, staging and main; only each deployment's HTTPS origin and secrets differ (ADR-022/023).

| Purpose | Public URL path | Upstream path |
|---|---|---|
| Training centers | `/reference-data/api/v1/training-centers` | `/api/v1/training-centers` |
| IAM session | `/iam/api/v1/auth/{login,refresh,me,logout}` | `/api/v1/auth/{login,refresh,me,logout}` |
| Remote entry | `/mfe/reference-data/remoteEntry.js` | `/remoteEntry.js` on the static MFE |
| Shell route | `/reference-data` | shell `index.html` fallback |
| Liveness | `/reference-data/api/v1/health/live` | `/api/v1/health/live` |
| Readiness | `/reference-data/api/v1/health/ready` | `/api/v1/health/ready` |

The canonical `docker-infra/traefik/dynamic.yml` removes `/reference-data` once for API requests and `/mfe/reference-data` once for MFE assets. Go registers `/api/v1` once. The MFE adds `/reference-data/api/v1` once when using the origin-wide platform client. Query strings are preserved. Development proxying forwards domain API and MFE paths to the edge without another rewrite. All browser calls use one origin; integrated operation requires no cross-origin CORS exception.

The local validation origin is `http://localhost:18120`, an isolated loopback environment. It uses the production shell/MFE static images, the canonical edge table and real IAM/PostgreSQL. The refresh cookie remains HttpOnly, Secure, SameSite=Strict with Path `/iam/api/v1/auth`; localhost browser behavior is verified by the test rather than changing cookie attributes.

## Database and runtime configuration

Apply the pinned Reference Data changelog after IAM migrations in the isolated shared validation database. The existing schema contains nine business tables (six institutional, three parameterization) plus three R1 messaging tables. Do not remove the messaging migrations to match the phrase "nine tables". The agreed seed currently creates hierarchy/unit data; empty catalog, catalog-detail and parameter tables are valid until application data is created.

Liquibase applies migrations using the migration owner. The API connects using `REFERENCE_DATA_DATABASE_URL` with a separate non-admin login that can assume `reference_reader` and `reference_writer`; it does not use the migration owner. Read and write transactions use `SET LOCAL ROLE`. The verifier checks role attributes, memberships, grants, constraints, indexes, seeds, a rolled-back writer transaction and a schema/data snapshot unchanged by a second migration.

`IAM_JWT_ISSUER` and `IAM_JWKS_URL` must match IAM. HTTP JWKS hosts require explicit `REFERENCE_DATA_JWKS_HTTP_ALLOWED_HOSTS` when using a private Compose hostname. Cached JWKS download is key discovery, not per-request token introspection. Missing/invalid JWTs return 401; insufficient feature or scope returns 403. Shared errors use `{error:{code,message,trace_id}}`. Readiness checks PostgreSQL with a bounded ping; stopping the DB must yield readiness 503 while liveness remains 200.

## Reproducible validation

From `docker-infra`, with Docker Compose/BuildKit, PowerShell 7, Node and the shell's Playwright dependencies installed:

```powershell
./validation/int-ref-001/run.ps1
```

The runner creates a fresh named project, generated ignored credentials and a private database volume. It refuses an existing project unless explicitly resumed. It never resets another project or database. It builds shell/MFE images with named frontend dependency contexts, starts real IAM and Reference Data, runs four API/browser tests with no skips, checks persisted rows through SQL and tests DB outage/recovery. A failed or prepared-only run cannot produce a passed result. Secrets and raw test outputs remain ignored; only sanitized results belong in the quality report.

Current runner ports: edge 18120, IAM debug 18122, PostgreSQL debug 15442, all loopback. Check availability before running another project concurrently. Cache volumes contain dependency caches only; data and signing-key volumes belong to the isolated project.

Review and merge the platform dependency before the shell consumer. Code branches target develop; this documentation branch targets main. Local success is not evidence of shared-environment migration, independent approval, merge or production readiness.

## References

- [HU-INT-REF-001](https://github.com/code-sena/design-software-docs/issues/294).
- [Authentication](../07-api/authentication.md).
- [Git conventions](../00-governance/git-conventions.md).
