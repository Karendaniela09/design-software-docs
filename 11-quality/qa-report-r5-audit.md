# Technical Report — E2E Audit and R5

**Owner:** Juan Pablo Gómez Perdomo  
**Training group:** ADSO 3145555  
**Domain:** Audit  
**Verification date:** October 20–21, 2026  
**Status:** implementation validated locally; R5 integrated into `develop` of `design-software-audit-service`.

## 1. Implemented and verified scope

The Audit domain records relevant system actions, preserves them immutably, and provides controlled access through IAM.

| Implemented capability | Verification performed |
|---|---|
| AMQP event consumption | `audit-worker` consumes from `audit-events`, validates the envelope, and persists it. |
| Append-only records | Valid events are stored in PostgreSQL under the `audit` schema, with no functional edit or delete operations. |
| Idempotency | Repeated `event_id` values do not create a second record. |
| Retry and DLQ | Invalid or unprocessable events follow the retry/DLQ flow without blocking the main queue. |
| Query | `audit-query-api` provides pagination, filters, detail, and payload access. |
| Export | CSV and JSON are available through the `AUDIT_EXPORT` capability. |
| Authorization | JWT/JWKS, `AUDIT_LOG_VIEW`, `AUDIT_EXPORT`, and `GLOBAL`/`TRAINING_CENTER` scopes. |
| User interface | `audit-mfe` is loaded in `web-shell` through `/audit/auditoria`. |

## 2. Validated routing

```text
Producer → RabbitMQ:5672 / audit-events → audit-worker → PostgreSQL:15432 / audit

Browser → web-shell:5000 /audit/auditoria → audit-mfe → audit-query-api:18081
Browser → /api/v1/* → Traefik:18080 /iam → IAM → JWT/JWKS/RBAC
```

The verified flow uses real messaging for writes, PostgreSQL for historical storage, IAM for authentication and authorization, and the shell/MFE for user queries.

## 3. Repositories and traceability

| Component | Official repository | Individual fork | Local directory used |
|---|---|---|---|
| Service, worker, and R5 | [code-sena/audit-service](https://github.com/code-sena/design-software-audit-service) | [Juan282007/audit-service](https://github.com/Juan282007/design-software-audit-service) | `C:\Users\juanp\Desktop\design-software-audit-service` |
| Database | [code-sena/audit-db](https://github.com/code-sena/design-software-audit-db) | [Juan282007/audit-db](https://github.com/Juan282007/design-software-audit-db) | `C:\Users\juanp\Desktop\design-software-audit-db` |
| Microfrontend | [code-sena/audit-mfe](https://github.com/code-sena/design-software-audit-mfe) | [Juan282007/audit-mfe](https://github.com/Juan282007/design-software-audit-mfe) | `C:\Users\juanp\Desktop\design-software-audit-mfe` |
| MFE host | [code-sena/web-shell](https://github.com/code-sena/design-software-web-shell) | [Juan282007/web-shell](https://github.com/Juan282007/design-software-web-shell) | `C:\Users\juanp\Desktop\design-software-web-shell` |
| Infrastructure | [code-sena/docker-infra](https://github.com/code-sena/design-software-docker-infra) | [Juan282007/docker-infra](https://github.com/Juan282007/design-software-docker-infra) | `C:\Users\juanp\Desktop\design-software-docker-infra` |
| IAM | [code-sena/iam-service](https://github.com/code-sena/design-software-iam-service) | [Juan282007/iam-service](https://github.com/Juan282007/design-software-iam-service) | `C:\Users\juanp\Desktop\design-software-iam-service` |
| IAM data | [code-sena/iam-db](https://github.com/code-sena/design-software-iam-db) | [Juan282007/iam-db](https://github.com/Juan282007/design-software-iam-db) | `C:\Users\juanp\Desktop\design-software-iam-db` |
| Documentation | [code-sena/docs](https://github.com/code-sena/design-software-docs) | [Juan282007/docs](https://github.com/Juan282007/design-software-docs) | `C:\Users\juanp\Desktop\design-software-docs` |

R5 was integrated into the official `develop` branch through [PR #5](https://github.com/code-sena/design-software-audit-service/pull/5). The fork and Desktop directories provide individual traceability and local reproduction support.

## 4. R5 implementation

| Criterion | Implemented artifact | Verified result |
|---|---|---|
| Provider Pact | `contracts/pact/audit-mfe-audit-query-api.json` and `cmd/audit-contract-provider` | The paginated interaction returned `200`, `Content-Type: application/json`, and a compatible body. |
| OpenAPI compatibility | `api/openapi/audit.yaml` and `scripts/check-openapi-contract.sh` | `oasdiff` against `origin/develop`: `No changes detected`. |
| Breaking-change gate | `scripts/test-openapi-contract-gate.sh` | Temporarily removing `/audit-records` produced `api-path-removed-without-deprecation` and exit code `1`. |
| Event schema | `api/events/audit-consumed-event.schema.json` | `TestCanonicalEventSchemaMatchesWorkerEnvelopeRules`: `PASS`. |
| CI gate | `.github/workflows/r5-contract-gates.yml` | `R5 / contract compatibility` check for pull requests targeting `develop`. |

The corresponding ADR is [ADR-014](https://github.com/code-sena/design-software-docs/blob/docs/r5-audit-contract-compatibility/05-architecture/decisions/records/ADR-014-audit-r5-contract-compatibility.md).

## 5. Tests and observed results

| Verification | Result |
|---|---|
| `go test ./...` in audit-service | Passed. |
| Build of `audit-query-api`, `audit-worker`, and `audit-contract-provider` | Passed. |
| Schema/worker contract | `PASS`. |
| `TestWorkerConsumesCanonicalEventE2E` | `PASS`. |
| `TestWorkerDeduplicatesAndRoutesInvalidEnvelopeE2E` | `PASS`. |
| Positive Pact | Status, headers, and body compatible. |
| Positive OpenAPI check | No breaking changes. |
| Controlled negative OpenAPI check | Breaking change detected correctly, exit code `1`. |
| IAM | `GET /iam/health` returned `UP`. |
| Audit API | `GET /api/v1/health` returned `status: ok`. |
| Database least privilege | Reader account allowed `SELECT` and rejected `INSERT`. |
| audit-mfe | 43 tests passed and build succeeded. |
| web-shell | 106 tests passed and build succeeded. |
| Access control | `200` when authorized, `401` without a token, and `403` without the capability. |

## 6. Evidence metrics

| Indicator | Result |
|---|---:|
| Contract boundaries covered | 3: HTTP/OpenAPI, Pact, and AMQP event/JSON Schema. |
| Negative gates verified | 2: incompatible Pact response and temporarily removed OpenAPI route. |
| AMQP integration tests | 2 passed. |
| MFE unit tests | 43 passed. |
| Web shell tests | 106 passed. |
| Confirmed health checks | IAM and Audit API. |

## 7. Technical conclusion

The Audit domain was validated end to end locally: an event travels through RabbitMQ, the worker validates and persists it without duplication, and an authorized user queries or exports it from the MFE integrated into the shell. R5 adds executable compatibility controls for the API, frontend, and events, including negative tests that detect breaking changes before integration.
