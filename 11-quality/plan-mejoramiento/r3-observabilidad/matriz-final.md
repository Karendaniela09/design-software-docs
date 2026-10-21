# Matriz final de cumplimiento — corte de QA del 20 de octubre de 2026

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

## Criterio de evaluación

Las evidencias de ejecución son locales, bajo `EVIDENCIAS-PLAN-MEJORAMIENTO-R3/` en la raíz del workspace. Las rutas de esta matriz son relativas a esa carpeta salvo los enlaces a documentos.

Se usa la **última ejecución disponible de cada criterio**, con fecha y alcance explícitos. No se combinan intentos anteriores fallidos para fabricar un resultado aprobado. Una consulta de GitHub o una revisión documental no cuentan como una nueva ejecución E2E. Las observaciones de telemetría del 19 de octubre se conservan con esa fecha: no certifican una repetición con los heads actuales ni un arranque desde ramas fusionadas. La última suite backend y las últimas pruebas de dominios son las salidas concretas indicadas abajo.

## Última evidencia por criterio

| Criterio | Estado | Última evidencia (hora de Bogotá) | Alcance y límite |
|---|---|---|---|
| P1-A: arranque reproducible desde ramas fusionadas | PARCIAL | 19 oct., 17:22; `03-parte-1/infra-verification.json` | El arranque local anterior pasó. Las dependencias compartidas ya están documentadas; no se ha ejecutado un checkout limpio de las ramas fusionadas y los PR siguen OPEN. |
| P1-B: MFE dentro del shell | CUMPLIDO Y VERIFICADO | 19 oct., 20:48; `03-parte-1/main-flow-browser.json`, `main-flow-reloaded.png` | Último navegador aprobado: `08-pruebas/main-flow-bogota.json`, exit_code=0. Sesión creada y abierta tras recargar; no equivale a validar todas las HU. |
| P1-C: integración completa e identidad institucional | PARCIAL | 19 oct., 22:50/22:54; `03-parte-1/domains-integration.json`, `scheduling-integration.json` | Cadenas locales Actors/Scheduling→Monitoring→Notification/Audit aprobadas. IdP institucional sin acceso; referencias aisladas de pruebas no certifican Training Environment. |
| P1-D: HU externas y cierre de integración | PARCIAL | 20 oct.; `03-parte-1/qa-remote-state.json` | Issues #322–#325 OPEN. Ningún PR de implementación está fusionado; publicar cambios no cierra estas HU. |
| R3-A1: traza MFE→servicio | CUMPLIDO Y VERIFICADO | 19 oct., 16:55; `04-tracing/trace-summary.json`, `tempo-trace.json` | Traza 1541ef6e05e37e0356b570c7b2c37b5c: ocho spans; parent_chain_verified=true. Alcance: la operación de catálogo capturada. |
| R3-A2: span CLIENT web | CUMPLIDO Y VERIFICADO | 19 oct., 16:55; `04-tracing/trace-summary.json` | monitoring-mfe tiene SPAN_KIND_CLIENT; no se atribuye esa captura a una sesión posterior. |
| R3-A3: llegada a PostgreSQL | CUMPLIDO Y VERIFICADO | 19 oct., 16:55/16:56; `04-tracing/trace-summary.json`, `03-parte-1/postgres-persisted-row.json` | INSERT y fila persistida del mismo escenario; duración individual, no benchmark. |
| R3-A4: propagación W3C | CUMPLIDO Y VERIFICADO | 19 oct., 16:53/16:55; `04-tracing/browser-traceparent.json`, `trace-summary.json` | Encabezado del navegador y padre del servidor comprobados en la última captura de trazas. |
| R3-B1: tasa por endpoint | CUMPLIDO Y VERIFICADO | 19 oct., 16:56; `05-metricas/prometheus-panels.json` | Última colección de métricas; consultas con datos reales, no medición de producción. |
| R3-B2: errores HTTP | CUMPLIDO Y VERIFICADO | 19 oct., 16:56; `05-metricas/prometheus-panels.json` | Consultas de 4xx/5xx en esa ejecución; no declara la tasa actual del sistema. |
| R3-B3: p50/p95/p99 | CUMPLIDO Y VERIFICADO | 19 oct., 16:56; `05-metricas/prometheus-panels.json` | Percentiles del histograma sobre la ventana observada; no benchmark ni SLA. |
| R3-C1: logs JSON | CUMPLIDO Y VERIFICADO | 19 oct., 16:56; `06-logs/correlated-logs.json` | Logs de la operación capturada, con trace_id/span_id. |
| R3-C2: correlation_id independiente | CUMPLIDO Y VERIFICADO | 19 oct., 16:56; `06-logs/correlated-logs.json` | El identificador de correlación se distingue del trace_id en esa captura. |
| R3-C3: aislamiento y consulta correlacionada | CUMPLIDO Y VERIFICADO | 19 oct., 21:42; `08-pruebas/domains-backend-tests.txt`; captura Loki 16:56: `06-logs/loki-query.json` | Última suite local: 34 passed, 7 warnings; incluye aislamiento concurrente. Loki corresponde a la última captura de telemetría, no a la ejecución de dominios posterior. |
| R3-D1: dashboard con datos | CUMPLIDO Y VERIFICADO | 19 oct., 16:51/16:56; `07-grafana/dashboard-firing.png`, `05-metricas/prometheus-panels.json` | Última captura y colección del dashboard de doce paneles. |
| R3-D2: persistencia del provisionamiento actual | PARCIAL | 19 oct., 17:22; `03-parte-1/infra-verification.json` | Comprobado en el entorno de esa fecha. Falta repetir recreación/arranque limpio sobre el conjunto final de ramas fusionadas. |
| R3-D3: regla de error superior al 5 % | CUMPLIDO Y VERIFICADO | 19 oct., 16:50; `07-grafana/alert-firing.json` | Prometheus y Grafana en Firing con la regla evaluada; alcance local de esa prueba. |
| R3-D4: disparo y recuperación | CUMPLIDO Y VERIFICADO | 19 oct., 16:50–16:52; `07-grafana/alert-firing.json`, `alert-recovered.json` | Último ciclo de alerta aprobado: `08-pruebas/alert-cycle-final.json`, exit_code=0. |
| Entrega: PR publicado | CUMPLIDO Y VERIFICADO | 20 oct.; `03-parte-1/qa-remote-state.json` | Publicación comprobada; los números, estados y ramas reales se registran abajo. No significa aprobación ni fusión. |
| Entrega: ADR | CUMPLIDO Y VERIFICADO | [`05-architecture/decisions/records/ADR-010-monitoring-r3-observability.md`](../../../05-architecture/decisions/records/ADR-010-monitoring-r3-observability.md) | Ruta canónica dentro de design-software-docs; validada por la revisión documental de QA. |
| Entrega: informe | CUMPLIDO Y VERIFICADO | [informe-tecnico.md](informe-tecnico.md) | Actualizado con alcance, evidencias y estados remotos; sin una segunda matriz contradictoria. |
| Entrega: capturas reales | CUMPLIDO Y VERIFICADO | 19 oct.; `03-parte-1/main-flow-reloaded.png`, `04-tracing/tempo-trace.png`, `07-grafana/dashboard-firing.png` | Capturas originales conservadas fuera de Git; no se sustituyen por imágenes generadas. |
| Entrega: métricas reales | CUMPLIDO Y VERIFICADO | 19 oct., 16:56; `05-metricas/prometheus-panels.json` | Últimas respuestas guardadas; no representa una consulta nueva de Prometheus. |
| Entrega: salidas de pruebas | CUMPLIDO Y VERIFICADO | 19 oct., 21:42/22:54; `08-pruebas/domains-backend-tests.txt`, `03-parte-1/scheduling-integration.json` | 34 pruebas backend y la última cadena Scheduling aprobadas. Se mantienen salidas fallidas anteriores; CI tiene fallos pendientes. |
| Entrega: sustentación personal | PARCIAL | [Guía](09-sustentacion/guia.md) | Guía preparada. No existe evidencia de que el aprendiz ya haya practicado o presentado la sustentación. |
| Entrega: ejercicios personales | PARCIAL | [Guía](09-sustentacion/guia.md) | Diez ejercicios documentados; ejecución personal pendiente, no se marca completa por escribirlos. |

## HU externas

| HU externa | Issue | Estado remoto | Evaluación del plan |
|---|---|---|---|
| HU-INT-MON-001 | [#322](https://github.com/code-sena/design-software-docs/issues/322) | OPEN | PARCIAL |
| HU-INT-MON-002 | [#323](https://github.com/code-sena/design-software-docs/issues/323) | OPEN | PARCIAL |
| HU-INT-MON-003 | [#324](https://github.com/code-sena/design-software-docs/issues/324) | OPEN | PARCIAL |
| HU-INT-MON-004 | [#325](https://github.com/code-sena/design-software-docs/issues/325) | OPEN | PARCIAL |

Consulta remota: `2026-10-20T17:05:38-05:00`. El resultado local favorable no cambia el estado de estas HU.

## PR consultados

| Repositorio | PR | Estado real | Borrador | Rama de origen | Head consultado |
|---|---|---|---|---|---|
| monitoring-service | [#6](https://github.com/code-sena/design-software-monitoring-service/pull/6) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `71a0778e9459` |
| monitoring-mfe | [#8](https://github.com/code-sena/design-software-monitoring-mfe/pull/8) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `811be35abdcf` |
| web-shell | [#14](https://github.com/code-sena/design-software-web-shell/pull/14) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `85b2c567bf42` |
| docker-infra | [#39](https://github.com/code-sena/design-software-docker-infra/pull/39) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `b8a99f08f8cd` |
| academic-management-service | [#17](https://github.com/code-sena/design-software-academic-management-service/pull/17) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `1d75bd2b32b1` |
| actors-db | [#65](https://github.com/code-sena/design-software-actors-db/pull/65) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `ac87ccccf928` |
| actors-service | [#28](https://github.com/code-sena/design-software-actors-service/pull/28) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `1348b45dc59d` |
| scheduling-service | [#16](https://github.com/code-sena/design-software-scheduling-service/pull/16) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `e806ab759d7b` |
| notification-service | [#11](https://github.com/code-sena/design-software-notification-service/pull/11) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `4094b1a2b3e0` |
| docs | [#331](https://github.com/code-sena/design-software-docs/pull/331) | OPEN | Sí | `fix/r3-observability` | `f0737d75dabd` |

OPEN, CLOSED y MERGED se toman de GitHub; se comprueba `merged_at` y no se interpreta `merge_commit_sha` de un PR abierto como una fusión. La rama documental vigente es `fix/r3-observability`; el PR anterior se conserva como histórico cerrado, sin fusionar.

## Referencias

- [Procedimiento reproducible y dependencias compartidas](README.md#reproducción-local-desde-un-checkout-limpio).
- [Estado y CI](estado-actual.md).

PR documental anterior: [#330](https://github.com/code-sena/design-software-docs/pull/330), **CLOSED**, sin fusionar; sustituido por el PR de `fix/r3-observability`.
