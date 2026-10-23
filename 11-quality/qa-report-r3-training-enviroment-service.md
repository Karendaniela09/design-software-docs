# Technical Report: R3 Observability Implementation in Training Environment

## Identification and control data

| Field | Information |
|---|---|
| **Responsible learner** | Emily Sharith Amézquita Saavedra |
| **Training group** | 3145555 |
| **Training program** | ADSO (Software Analysis and Development) — SENA |
| **Training project** | Design Software — SENA platform |
| **Instrumented microservice** | `training-environment-service` (training environment and reservation management) |
| **Submission type** | Individual improvement plan — R3: End-to-end observability |
| **Official rubric** | Acta 02, Section 10 |
| **Official pull request** | [PR #19](https://github.com/code-sena/design-software-training-environment-service/pull/19) |
| **Technical branch** | `feature/r3-observability` |
| **Related architecture decision** | [ADR-012: End-to-end Observability in Training Environment](../../../05-architecture/decisions/records/ADR-012-training-environment-r3-observability.md) |
| **Execution date** | October 18, 2026 |
| **Report version** | 2.0 — QA revalidation: official OpenTelemetry SDK, MFE → API → PostgreSQL tracing, and RED metrics |
| **Technical result** | **100% successful / PASS:** all rubric criteria implemented, QA blockers remediated, and automated tests validated |

## 1. Executive summary and QA finding resolution

As part of the ADSO improvement plan and in response to the QA revalidation of PR #19, the official **OpenTelemetry SDK** was fully integrated. The previous manual implementation was removed, and distributed tracing was extended from the Microfrontend (MFE), through the service, to PostgreSQL persistence operations.

### QA observation resolution matrix

| QA-observed component | Previous state | Solution implemented | Current state |
|---|---|---|:---:|
| **OpenTelemetry dependencies** | `go.mod` contained only `github.com/lib/pq`. | Added official dependencies: `go.opentelemetry.io/otel`, `otel/trace`, `otel/sdk`, `otel/exporters/otlp`, and `otel/exporters/stdout`. | **PASS** |
| **TracerProvider and OTel SDK** | No official TracerProvider or span exporters. | Implemented `internal/observability/tracer.go` with `sdktrace.NewTracerProvider`, OTLP gRPC and Stdout exporters, `ParentBased(AlwaysSample)` sampling, and graceful `Shutdown`. | **PASS** |
| **W3C tracing to PostgreSQL** | Spans were not exportable and the database was not instrumented. | Integrated `github.com/XSAM/otelsql`. PostgreSQL connections created by `observability.OpenTracedPostgresDB` create DB client spans as children of the HTTP span. | **PASS** |
| **Distributed trace continuity** | MFE → Service → DB continuity was not demonstrated. | `TestDistributedTracing_MFE_To_Service_To_Database` mathematically verifies that MFE, HTTP, and DB share the same `trace_id` with a strict parent-child hierarchy. | **PASS** |
| **Security and clean CI execution** | Tests contained hard-coded credentials. | Parameterized through `TEST_DATABASE_URL`, with a clean `t.Skip()` when the variable is absent, ensuring `go test ./...` remains green without network dependencies. | **PASS** |
| **Documentation centralization** | Documentation was stored in the microservice repository. | ADR-012 and this technical report are centralized in `design-software-docs` according to institutional architecture guidance. | **PASS** |

## 2. Implemented observability architecture

### 2.1 End-to-end distributed tracing (MFE → Service → PostgreSQL)

The distributed trace follows the W3C Trace Context Level 1 recommendation and OpenTelemetry semantic conventions:

```text
[ Microfrontend (React 18 / Vite) ]
       │ HTTP request with traceparent header
       ▼
┌────────────────────────────────────────────────────────────────────────┐
│ training-environment-service (HTTP server span)                        │
│ Trace ID:  4bf92f3577b34da6a3ce929d0e0e4736                           │
│ Span ID:   30255d55861dd138                                            │
│ Parent ID: 00f067aa0ba902b7 (MFE span)                                 │
│ Kind:      SERVER                                                      │
│ Attributes: http.method=GET, http.route=/training-environments          │
│                                                                        │
│   ├── Structured JSON log with trace_id and span_id                    │
│   └── PostgreSQL instrumented through otelsql (DB client span)          │
│       Same Trace ID; parent is the service HTTP span                   │
│       Kind: CLIENT; db.system=postgresql                               │
└────────────────────────────────────────────────────────────────────────┘
       │ HTTP/1.1 200 OK and propagated Traceparent
       ▼
[ MFE client / gateway ]
```

### 2.2 RED metrics at `/metrics`

Metrics are exposed using Prometheus text format 0.0.4:

1. **Rate:** `http_requests_total{method, path, status}`.
2. **Errors:** `http_requests_errors_total{method, path, status}` for HTTP status `>= 400`.
3. **Duration:** `http_request_duration_seconds_bucket{method, path, le}` with 11 latency buckets for P50, P90, P95, and P99 calculations.
4. **In-flight:** `http_requests_in_flight` for active concurrency.

### 2.3 Correlated structured JSON logs

Logs are implemented with `log/slog` and written to `stdout`. Each record includes `service.name`, `environment`, `correlation_id`, `trace_id`, `span_id`, `traceparent`, `http.method`, `http.route`, `http.status_code`, `http.duration_ms`, and `http.client_ip`.

## 3. Validation evidence and automated tests

### Evidence 1 — Docker Go runtime tests

The automated suite runs inside Docker with the OpenTelemetry SDK loaded:

```text
=== RUN   TestTraceContext_ParseTraceparent
--- PASS: TestTraceContext_ParseTraceparent (0.00s)
=== RUN   TestTraceContext_NewAndPropagation
--- PASS: TestTraceContext_NewAndPropagation (0.00s)
```

### Evidence 2 — Complete distributed trace verification

`TestDistributedTracing_MFE_To_Service_To_Database` executes a real SQL query through `OpenTracedPostgresDB()` and `otelsql`. It verifies automatic DB span creation, shared `trace_id`, parent-child hierarchy, and semantic database attributes.

```text
=== RUN   TestDistributedTracing_MFE_To_Service_To_Database
Total spans recorded: 3
Span: sql.conn.query, Kind=client, TraceID=4bf92f3577b34da6a3ce929d0e0e4736
Span: sql.rows, Kind=client, TraceID=4bf92f3577b34da6a3ce929d0e0e4736
Span: GET /training-environments, Kind=server, TraceID=4bf92f3577b34da6a3ce929d0e0e4736
Distributed Trace Verified Successfully
--- PASS: TestDistributedTracing_MFE_To_Service_To_Database ---
PASS
```

### Evidence 3 — `/metrics` and W3C propagation

An active service queried with a W3C `traceparent` header returned RED metrics and propagated correlation headers:

```text
http_requests_total{method="GET",path="/health",status="200"} 1
http_request_duration_seconds_bucket{method="GET",path="/health",le="0.005"} 1
HTTP/1.1 200 OK
Traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-838d77dd5db8ebeb-01
X-Correlation-Id: 4bf92f3577b34da6a3ce929d0e0e4736
X-Trace-Id: 4bf92f3577b34da6a3ce929d0e0e4736
```

### Evidence 4 — Observability infrastructure

Grafana and Prometheus were deployed with Docker Compose. The deployment exposed the configured Prometheus datasource, RED dashboard, and alert provisioning.

### Evidence 5 — Grafana RED dashboard and alert threshold

Grafana displays Rate, Error percentage, P50/P95/P99 latency, and an alert threshold at 5 %. Visual image links were intentionally removed from this centralized report because the referenced screenshots were not reliably viewable in the documentation repository. The executable test output and configuration references remain the source of evidence.

## 4. Technical equivalence: Go and Spring Boot

| Rubric concept | Go implementation | Java / Spring Boot equivalent |
|---|---|---|
| OpenTelemetry SDK | `go.opentelemetry.io/otel` + `sdktrace.NewTracerProvider` | `io.opentelemetry:opentelemetry-sdk` + OpenTelemetry Java Agent |
| W3C HTTP tracing | `internal/observability/middleware.go` with `otel.GetTextMapPropagator` | Micrometer OTel bridge + Spring Web filter |
| Database tracing | `github.com/XSAM/otelsql` and `OpenTracedPostgresDB` | OpenTelemetry JDBC or Spring Data JPA OTel driver |
| RED metrics | `internal/observability/metrics.go` | Spring Actuator + Prometheus registry |
| Metrics endpoint | `GET /metrics` | `GET /actuator/prometheus` |
| Structured logging | `log/slog` with correlation and trace IDs | Logstash Logback encoder with MDC |
| Grafana dashboard and alert | Provisioning as code with a 5 % alert | Equivalent Grafana/Prometheus provisioning |

## 5. Implementation files

```text
design-software-training-environment-service/
├── cmd/training-environment-api/main.go
├── internal/observability/
│   ├── tracer.go
│   ├── trace.go
│   ├── metrics.go
│   ├── logger.go
│   ├── middleware.go
│   └── observability_test.go
└── deploy/
    ├── docker-compose.observability.yml
    ├── prometheus/prometheus.yml
    └── grafana/
        ├── provisioning/
        ├── dashboards/training-environment-red-dashboard.json
        └── alerts/red-alerts.yml
```

The implementation uses OTel + LGTM from ADR-008, PyJWT-style cryptographic validation is not applicable here because this service is Go-based, and the Go dependency lock contains the verified OpenTelemetry and SQL instrumentation dependencies. The public key is mounted in the API; private keys and expiring tokens are ignored by Git.

---

*Technical revalidation report prepared and signed by:*  
**Emily Sharith Amézquita Saavedra**  
Training group ADSO 3145555 — SENA  
*Official implementation repository:* `code-sena/design-software-training-environment-service` (PR #19)  
*Official documentation repository:* `code-sena/design-software-docs`
