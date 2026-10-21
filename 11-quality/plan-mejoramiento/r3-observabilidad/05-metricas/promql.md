# RED y consultas verificables

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

Los instrumentos OTel `monitoring_http_requests` y `monitoring_http_duration` se exportan como contador `monitoring_http_requests_total` e histograma `monitoring_http_duration_seconds_bucket`, `_count` y `_sum`. La unidad del instrumento es `s`. Etiquetas: `http_method`, `http_route` normalizada y `http_status_code`. Las rutas no registradas son `unmatched`; no se usan UUID ni query strings como etiquetas.

**Solicitudes por segundo:**
```promql
sum(rate(monitoring_http_requests_total{http_route!~".*/(health|ready)"}[1m]))
```

**Rate por endpoint:**
```promql
sum by (http_route, http_method)(rate(monitoring_http_requests_total[1m]))
```

**Errores por segundo y por endpoint:**
```promql
sum by (http_route)(rate(monitoring_http_requests_total{http_status_code=~"4..|5.."}[1m]))
```

**Porcentaje de error:**
```promql
100 * (sum(rate(monitoring_http_requests_total{http_route!~".*/(health|ready)",http_status_code=~"4..|5.."}[1m])) or vector(0))
 / clamp_min((sum(rate(monitoring_http_requests_total{http_route!~".*/(health|ready)"}[1m])) or vector(0)), 0.000001)
```

**p95 por endpoint:**
```promql
histogram_quantile(0.95, sum by (le,http_route)(rate(monitoring_http_duration_seconds_bucket[1m])))
```

**p99 por endpoint:**
```promql
histogram_quantile(0.99, sum by (le,http_route)(rate(monitoring_http_duration_seconds_bucket[1m])))
```

Los percentiles son aproximaciones de histograma, no tiempos exactos de una solicitud. Si no hay observaciones nuevas pueden ser NaN: ejecutar tráfico real, esperar dos scrapes y consultar de nuevo; no sustituirlos por métricas inventadas. El dashboard muestra datos históricos de las pruebas de arranque y de carga, incluidos errores reales corregidos durante la implementación.

La alerta cuenta 4xx y 5xx. El 422 controlado procede de una validación real de paginación y se describe como error de cliente. No se presenta como 5xx. La condición `>5` exige 20 segundos, ventana de un minuto y evaluación cada 10 segundos; scrape cada 5 segundos. Sin datos, el porcentaje queda en cero y Grafana configura NoData como OK. Los fallos del motor se clasifican como Error, no como recuperación. No se aplica mínimo de tráfico.

La sonda Blackbox llama `/api/v1/ready`: `probe_success{job="monitoring-health"}` verifica API, tabla de catálogos y broker. `up{job="otel-collector"}` solo prueba el endpoint del colector.

`prometheus-panels.json` conserva las respuestas reales de todas las expresiones de los 11 paneles Prometheus; el panel restante usa Loki. Reproducir con `scripts/collect_r3_evidence.py` después de `r3-e2e.mjs` y generar tráfico con `test_r3_alert.py` si se desean tasas y percentiles activos.
