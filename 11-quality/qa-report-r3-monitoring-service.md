# Technical Report — R3 Improvement Plan — Monitoring Observability

> Status: Under review | Last updated: 2026-10-20  
> Author: Kevin Andrey Culma Gómez | Team: Monitoring / ADSO 3145555

This document was migrated from the original submission. Screenshot and output paths are available in the local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3` folder. For the current cut, use the R3 index and `estado-actual.md`; historical results retain their original date and scope.

**Learner:** Kevin Andrey Culma Gómez  
**Training group:** ADSO 3145555  
**Domain:** Monitoring  
**Challenge:** R3 — Observability  
**Document cut-off:** October 20, 2026, America/Bogota

## 1. Introduction

This work addresses Acta No. 02 dated October 14, 2026. Observability was implemented and tested across the domain's real components. The report distinguishes verified local execution from institutional integration and user stories owned by other contributors. A configuration file, mock, or closed issue is not considered proof that the product works by itself.

## 2. Objectives

The objectives were to implement an observable path from Monitoring MFE to PostgreSQL; measure requests, errors, and duration by endpoint; correlate JSON logs; provision Grafana; and verify a real alert above 5 %. Commands, tests, evidence, and reproducible design decisions are included.

## 3. Initial state

The workspace contains 39 repositories. Monitoring Service uses Python/FastAPI, SQLAlchemy/psycopg, and RabbitMQ; the database is migrated with Liquibase; the MFE and shell use React/TypeScript and Module Federation. OTel and Collector + LGTM already existed but were only partially connected. The Monitoring Docker profile, browser instrumentation, explicit RED metrics, and the R3 dashboard/alert were missing. The local BFF returned fixtures instead of real persistence. PostgreSQL serialization and pagination errors were found, together with JWT authentication that decoded tokens without verifying their signature.

The detailed diagnosis and initial matrix are in [01-diagnostico](01-diagnostico/diagnostico.md). A previous local change to `design-software-iam-mfe/vite.config.ts` was kept outside these branches.

## 4. Part 1 — Product validation

The official `monitoring` profile was extended in `docker-infra` and executed under the isolated `ds-monitoring-r3` project. It includes PostgreSQL, RabbitMQ, API, worker, MFE, shell, proxy, and observability. The 24 official Monitoring migrations were applied successfully; subsequent executions reported them as already applied. No new migrations, volume cleanup, or changes to shared databases were performed.

The Playwright test loads the real MFE inside the shell, creates a KPI type, verifies HTTP 201, reloads the page, and confirms that the record remains present. An independent script queries the same row directly in PostgreSQL. An additional test attempts to create the same code, receives a real HTTP 409, keeps the form, and verifies the error spans. Network interceptors and mocks are not used.

The business test sends an input event identified as `r3-test-producer` to real RabbitMQ. The worker persists tracking, KPI, alert, and outbox data. The script queries the API, creates a plan, resolves the alert, checks the alert counter, and queries the KPI summary. This validates the local consumer and services, but not event emission from Academic Service, IAM login, Notification delivery, or external audit.

HU-MON-008 frontend (#225) is closed and belongs to another learner. HU-INT-MON-001 through HU-INT-MON-004 and several historical stories with duplicate codes remain open. The [remote inventory](03-parte-1/historias-y-pr.md) preserves numbers, owners, statuses, and dates. GitHub Projects could not be read because the `read:project` scope was unavailable; Issues and PRs were consulted without changing their status.

The later extension also verified local IAM login, Academic ficha creation, and browser-session persistence after reload. Actors and Scheduling chains were run with Notification, test SMTP, and Audit. These are separate tests with separate evidence and do not constitute one full-ecosystem UI test. The institutional IdP, external story closure, and execution on merged target branches remain outside the verified scope.

## 5. Part 2 — R3 observability

The MFE starts CLIENT spans and propagates W3C `traceparent` through the injected HTTP client. The shell preserves the headers, Nginx routes them, FastAPI extracts the parent, and SQLAlchemy instruments real operations. `collect_r3_evidence.py` verifies one `trace_id` and walks the INSERT parents back to the frontend span. It also checks a real PostgreSQL conflict trace.

OTel metrics are exported through the Collector to Prometheus: `monitoring_http_requests_total` and `monitoring_http_duration_seconds_{bucket,sum,count}`. Labels contain method, normalized route, and HTTP status; they do not contain UUIDs, query strings, or user identifiers. The histogram supports aggregatable p50/p95/p99 queries. Queries are in [promql.md](05-metricas/promql.md), with real responses in `prometheus-panels.json`.

JSON logs include UTC timestamp, level, service, message, `correlation_id`, `trace_id`, and `span_id`. HTTP completion adds method, route, status, duration, and error type. A `ContextVar` is cleared in `finally`, and concurrent tests verify request isolation. Incoming IDs are validated. Loki receives logs through OTLP and supports searching the browser operation's `correlation_id`. The Collector removes query text, complete URLs, and sensitive exception details from traces.

Grafana loads datasources, 12 panels, and a declarative rule. Eleven panels query Prometheus and one queries Loki; all Prometheus expressions were queried with real data. An independent probe checks readiness, including the PostgreSQL table and broker. Collector availability is not confused with API health.

The alert counts **4xx and 5xx**, excludes liveness/readiness, uses a one-minute window, evaluates every 10 seconds, and fires when the condition remains `>5` for 20 seconds. The denominator is protected; with no traffic, the percentage is zero. Grafana configures NoData as OK and evaluator errors as Error. The test uses valid requests and real 422 validations rather than a fake failure endpoint. Prometheus and Grafana reached Firing and returned to inactive/Normal. JSON files and screenshots of both states were preserved. The Firing dashboard shows approximately 20 % errors and is not a production or SLA measurement.

## 6. Final architecture

See the [Mermaid diagram and propagation model](02-arquitectura/arquitectura.md). The observed HTTP path is `web-shell/Monitoring MFE → Nginx → FastAPI → PostgreSQL`. Export goes to the Collector and then to Tempo, Prometheus, and Loki; Grafana queries those backends. The fixture-based BFF is outside the R3 path. No proxy spans or database operations are invented.

## 7. Implementation and files

| Repository | Main files and purpose |
|---|---|
| monitoring-service | `src/monitoring/observability.py` for ASGI, traces, RED, logs, and export; `auth.py` for JWT RS256/JWKS or public key; HTTP router for UUIDs, pagination, and permissions; readiness checks; API/worker composition roots; AMQP adapter; Dockerfile, lockfile, tests, and evidence scripts. |
| monitoring-mfe | `src/observability.ts` for request spans and propagation; instrumented HTTP client; real paginated catalog adapter; package lock and telemetry tests. |
| web-shell | `RemoteRoutes.tsx` for headers, token, and real catalogs; explicit R3 session source; Playwright scripts and screenshots. |
| docker-infra | `docker-compose.yml`, profile startup, Nginx and probe; privacy-aware Collector; Prometheus; Grafana datasources, dashboard, and alert. |

OTel + LGTM from ADR-008 was reused. PyJWT with cryptographic support and the web OTel SDK were added. Only the public key is mounted in the API; the private key and expiring token are ignored by Git. Grafana local Explore is available to the Editor role on `127.0.0.1`; this demonstration configuration must be reviewed before use in another environment.

## 8. Tests and procedure

Complete outputs and metadata are in `EVIDENCIAS-PLAN-MEJORAMIENTO-R3/08-pruebas/`, outside Git. The preserved final backend suite reports **34 passed, 7 warnings** (`domains-backend-tests.txt`, October 19, 21:42). The MFE (65 tests) and shell (106 tests) executions, builds, and lint results are previous results from October 19 and are not presented as a new final-PR execution. Unit tests using fakes remain classified as unit tests; E2E evidence comes from scripts against real containers.

Before running these commands, complete the [clean checkout and shared dependency mounts](README.md#reproducción-local-desde-un-checkout-limpio):

```powershell
# INFRA: official startup with migrations, local credentials, and signed identity
& design-software-docker-infra/scripts/up-monitoring-stack.ps1
# E2E: real browser, creation, and HTTP 409 conflict
Push-Location design-software-web-shell
node scripts/r3-e2e.mjs
Pop-Location
# COLLECT: verify parents, INSERT, PostgreSQL row, Loki, and Prometheus queries
& design-software-monitoring-service/.venv/Scripts/python.exe design-software-monitoring-service/scripts/collect_r3_evidence.py
# BUSINESS: broker, worker, tracking, KPI, alert, plan, and resolution
& design-software-monitoring-service/.venv/Scripts/python.exe design-software-monitoring-service/scripts/test_r3_business.py
# ALERT: traffic, Firing, screenshots, and real recovery
& design-software-monitoring-service/.venv/Scripts/python.exe design-software-monitoring-service/scripts/test_r3_alert.py
# VERIFY: Compose, promtool, DNS, deployed source, and provisioned dashboard
& design-software-monitoring-service/.venv/Scripts/python.exe design-software-monitoring-service/scripts/verify_r3_infra.py
```

The [defense guide](09-sustentacion/guia.md) includes installation, startup, tests, and demonstration. For the backend suite with the local database, run `.venv/Scripts/python.exe scripts/record_check.py --database backend-local -- .venv/Scripts/python.exe -m pytest -q` from monitoring-service; the harness loads the URL from the ignored file without printing the password.

The initial Actions failure caused by the missing private contract was corrected with an official SHA-256-pinned snapshot for independent checkout; the test was not disabled. Intermediate failures and corrections remain in [incidencias-corregidas.md](08-pruebas/incidencias-corregidas.md). Non-fatal SQL default and TestClient warnings remain. Retries are not presented as successful prior attempts.

## 9. Current results and limitations

The [final matrix](matriz-final.md) is the only current matrix for this dossier. It identifies the latest evidence for each criterion, its date, and its limits. A new E2E validation is not claimed merely because documentation was corrected.

| Preserved local scenario | Result | Evidence relative to the evidence root |
|---|---|---|
| Local IAM: login, profile, JWKS, 401/403 | Passed, Oct 19, 20:35 | `03-parte-1/iam-integration.json` |
| Academic → Monitoring | Passed, Oct 19, 20:36 | `03-parte-1/academic-integration.json` |
| Browser session and persistence after reload | Passed, Oct 19, 20:48 | `03-parte-1/main-flow-browser.json`, `main-flow-postgres.json` |
| Backend suite with PostgreSQL/RabbitMQ | 34 passed, 7 warnings | `08-pruebas/domains-backend-tests.txt` |
| Actors → Monitoring → Notification/SMTP → Audit | Passed, Oct 19, 22:50 | `03-parte-1/domains-integration.json` |
| Scheduling publication/cancellation and consumers | Passed, Oct 19, 22:54 | `03-parte-1/scheduling-integration.json` |

Limitations: the institutional IdP was not tested; external stories #322–#325 remain open; PRs were not merged at the time of the remote query; Actors and Scheduling checks were failing; personal practice of the defense guide remains pending; and no production deployment or benchmark was certified.

## 10. Stories, pull requests, and references

External stories HU-INT-MON-001 through HU-INT-MON-004 remain OPEN and are evaluated as PARTIAL. The report records the actual remote state without assuming that OPEN means draft or that a GitHub merge commit represents a completed integration.

See [estado-actual.md](estado-actual.md), [architecture](02-arquitectura/arquitectura.md), [final matrix](matriz-final.md), and [defense guide](09-sustentacion/guia.md). The complete original evidence remains in `EVIDENCIAS-PLAN-MEJORAMIENTO-R3/`. Previous documentation PR #330 was closed without merge and was replaced by the `fix/r3-observability` PR.
