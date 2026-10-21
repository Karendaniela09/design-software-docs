# ADR-012: Observabilidad Integral en Training Environment — OpenTelemetry (W3C Trace Context), Métricas RED, Logs Estructurados Correlacionados e Instrumentación de PostgreSQL

**Estado:** ACCEPTED (2026-10-18)
**Fecha:** 2026-10-18
**Autores:** Emily Sharith Amézquita Saavedra (ADSO Ficha 3145555)
**Equipos involucrados:** Arquitectura, Backend (`training-environment-service`), QA

---

## Contexto

Dentro del Macroproyecto Design Software — plataforma SENA (ADSO Ficha 3145555), el microservicio `training-environment-service` gestiona los ambientes de formación, reglas de disponibilidad semanal, bloqueos por mantenimiento y reservas de aulas y talleres.

Al operar en una arquitectura de microservicios distribuida con frontend federado (Microfrontend en React 18 / Vite), pasarelas de enlace (Traefik / Reverse Proxy), servicios de autorización (IAM) y persistencia relacional (PostgreSQL 17), se requiere cumplir rigurosamente con los estándares transversales de observabilidad definidos en el [ADR-008](./ADR-008-observability-opentelemetry.md) y los requerimientos del Acta No. 02-2026 (Numeral 10, Reto R3 de Observabilidad):
1. **Trazabilidad Distribuida End-to-End (MFE → Servicio → Base de Datos):** La transacción originada en el cliente debe mantener un único identificador (`trace_id`) que se preserve al ingresar por el middleware HTTP y continúe de forma jerárquica hasta la capa de persistencia en PostgreSQL (`otelsql`).
2. **Adopción del SDK Oficial de OpenTelemetry:** Integrar el ecosistema estándar `go.opentelemetry.io/otel`, configurando `TracerProvider`, exportadores OTLP/Stdout, propagadores globales W3C (`propagation.TraceContext`) y registro de spans exportables.
3. **Métricas RED por Endpoint (Rate, Errors, Duration):** Exposición de contadores e histogramas percentilados en formato nativo de Prometheus en `/metrics`.
4. **Logs Estructurados en JSON:** Con correlación unificada mediante `correlation_id`, `trace_id` y `span_id`.
5. **Grafana y Alertas como Código:** Provisión declarativa del tablero de control RED y regla de alerta ante tasa de error $> 5\%$.

---

## Decisión

Se decide implementar una solución de observabilidad integral y estandarizada en Go para `training-environment-service` basada en el SDK oficial de OpenTelemetry y buenas prácticas cloud-native:

### 1. SDK Oficial de OpenTelemetry y TracerProvider
- **Dependencias Estándar:**
  - `go.opentelemetry.io/otel`: Interfaz y núcleo global.
  - `go.opentelemetry.io/otel/trace`: Creación y contexto de spans.
  - `go.opentelemetry.io/otel/sdk/trace`: `TracerProvider`, procesadores (`BatchSpanProcessor`, `SimpleSpanProcessor`) y muestreo `ParentBased(AlwaysSample)`.
  - `go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc`: Exportador gRPC nativo hacia Tempo o Colectores OpenTelemetry.
  - `go.opentelemetry.io/otel/exporters/stdout/stdouttrace`: Exportador de salida estándar para depuración y verificación.
  - `go.opentelemetry.io/otel/propagation`: Propagadores compuestos de `TraceContext` y `Baggage`.
- **Propagación W3C Bidireccional:**
  - El middleware HTTP extrae la cabecera `traceparent` entrante del MFE mediante `otel.GetTextMapPropagator().Extract()`.
  - Inicia un Server Span con atributos semánticos HTTP (`http.method`, `http.target`, `http.client_ip`, `http.user_agent`, `http.status_code`).
  - Inyecta la cabecera de traza en la respuesta HTTP mediante `otel.GetTextMapPropagator().Inject()`, devolviendo también `Traceparent`, `X-Correlation-Id` y `X-Trace-Id`.

### 2. Instrumentación de Base de Datos PostgreSQL (MFE → Servicio → PostgreSQL)
- **Librería de Instrumentación:** Se adopta `github.com/XSAM/otelsql`, el estándar oficial para instrumentar la interfaz `database/sql` de Go con OpenTelemetry.
- **Creación de Spans de Base de Datos:**
  - La conexión se abre mediante `observability.OpenTracedPostgresDB(dbURL)`, que encapsula el driver `postgres` (`github.com/lib/pq`) bajo un proxy instrumentado con atributos `db.system=postgresql`.
  - Todas las operaciones ejecutadas por los repositorios (`QueryContext`, `ExecContext`, transacciones) reciben el `ctx context.Context` enriquecido por el middleware HTTP.
  - `otelsql` genera automáticamente spans de tipo **Client** como hijos directos del span del servidor HTTP, conservando de forma estricta el mismo `trace_id` y registrando el `db.statement` y latencia de cada consulta SQL.
  - Se registra además la recolección automática de métricas de rendimiento del pool de conexiones con `otelsql.RegisterDBStatsMetrics`.

### 3. Métricas RED (Rate, Errors, Duration) con Exportación Prometheus
- **Rate (Tasa):** Métrica de tipo contador `http_requests_total{method, path, status}` que contabiliza el volumen de transacciones.
- **Errors (Errores):** Contador `http_requests_errors_total{method, path, status}` para respuestas con código de estado HTTP $\ge 400$.
- **Duration (Duración):** Histograma `http_request_duration_seconds{method, path}` con 11 buckets normalizados (`0.005s` a `10s`) para cálculo de percentiles P50, P90, P95 y P99.
- **Sanitización de Etiquetas:** Parametrización automática de identificadores dinámicos UUID a `{id}` para prevenir explosión de cardinalidad en Prometheus.
- **Endpoint Estándar:** Expuesto públicamente en `GET /metrics` bajo formato estándar de Prometheus 0.0.4.

### 4. Logs Estructurados en JSON con Correlación Unificada
- Se adopta `log/slog` direccionado a `stdout`.
- Cada registro incluye: `service.name`, `service.version`, `environment`, `correlation_id`, `trace_id`, `span_id`, `traceparent`, `http.method`, `http.route`, `http.status_code`, `http.duration_ms`, `http.client_ip`.
- Nivel dinámico: `INFO` para 2xx/3xx, `WARN` para 4xx y `ERROR` para 5xx.

### 5. Grafana y Alertas como Código
- Tablero aprovisionado en `deploy/grafana/dashboards/training-environment-red-dashboard.json`.
- Regla de alerta en `deploy/grafana/alerts/red-alerts.yml` ante tasa de error $> 5\%$.
- Stack Docker Compose integrado (`deploy/docker-compose.observability.yml`) con Prometheus y Grafana.

---

## Diagrama de Trazabilidad Distribuida Unificada

```text
[ Microfrontend (MFE React 18 / Vite) ]
       │
       │ traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
       ▼
┌────────────────────────────────────────────────────────────────────────┐
│ training-environment-service (HTTP Server Span)                        │
│ Trace ID:  4bf92f3577b34da6a3ce929d0e0e4736                           │
│ Span ID:   30255d55861dd138                                            │
│ Parent ID: 00f067aa0ba902b7 (Span del MFE)                             │
│ Kind:      SERVER                                                      │
│ Atributos: http.method=GET, http.route=/training-environments          │
│                                                                        │
│   ├── Log Estructurado JSON:                                           │
│   │   {"msg":"HTTP request completed","trace_id":"...","span_id":"..."}│
│   │                                                                    │
│   └── Repositorio PostgreSQL instrumentado vía otelsql (DB Client Span)│
│       Trace ID:  4bf92f3577b34da6a3ce929d0e0e4736 (¡MISMO TRACE ID!)  │
│       Span ID:   58b1f9abdd21fb00                                      │
│       Parent ID: 30255d55861dd138 (Span HTTP del Servicio)             │
│       Kind:      CLIENT                                                │
│       Atributos: db.system=postgresql, db.statement=SELECT ...         │
└────────────────────────────────────────────────────────────────────────┘
       │
       │ HTTP/1.1 200 OK
       │ Traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-30255d55861dd138-01
       │ X-Correlation-Id: 4bf92f3577b34da6a3ce929d0e0e4736
       ▼
[ Cliente MFE / Pasarela ]
```

---

## Consecuencias

### Positivas
- **Trazabilidad E2E completa:** Un único `trace_id` recorre desde el MFE hasta las consultas SQL en PostgreSQL.
- **Alineación Arquitectónica Polyglot:** Cumple cabalmente con el [ADR-008](./ADR-008-observability-opentelemetry.md).
- **Aprobación de Revalidación QA:** Resuelve al 100% las observaciones emitidas sobre el PR #19 con pruebas automatizadas que verifican spans y jerarquías padre-hijo.
- **Provisión como Código:** Tableros RED y alertas provisionados declarativamente sin intervención manual en Grafana.

### Negativas / Trade-offs
- Sobrecarga mínima de serialización de spans OTel y mantenimiento de histogramas en memoria.
- Requiere infraestructura de monitoreo (Prometheus/Grafana o Collector LGTM) en cada entorno.

### Riesgos
- Explosión de cardinalidad de métricas si se filtran IDs dinámicos no parametrizados (mitigado con regex para sustituir UUIDs por `{id}`).
- Saturación de salida estándar con logs JSON de alto volumen (mitigado con muestreo OTel y niveles de log adecuados).

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Implementación manual de cabeceras sin SDK OTel | Rechazada por QA: no exporta spans a backends estándar (Tempo/Jaeger), no es interoperable ni auditable bajo estándares W3C oficiales. |
| Librerías APM propietarias (Datadog, New Relic) | Descartadas por política institucional SENA (vendor lock-in, costos de licenciamiento). |
| Instrumentación SQL manual en cada consulta | Alta propensión al error humano, duplicación masiva de código boilerplate. `otelsql` resuelve la instrumentación de forma transparente a nivel de driver `database/sql`. |

## Referencias

- [ADR-008: Observabilidad — OpenTelemetry + Grafana (LGTM)](./ADR-008-observability-opentelemetry.md)
- [09-microservices/services/04-training-environment-service/README.md](../../../09-microservices/services/04-training-environment-service/README.md)
- [PR #19 en code-sena/design-software-training-environment-service](https://github.com/code-sena/design-software-training-environment-service/pull/19)
- [Informe técnico Reto R3](../../../09-microservices/services/04-training-environment-service/informe-tecnico-r3.md)
