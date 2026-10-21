# Sustentación R3 — Kevin Andrey Culma Gómez, ADSO 3145555

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

## Preparación y arranque

Ejecutar desde `C:\sena\Micro Horario`, con Docker Desktop activo:

```powershell
python -m venv design-software-monitoring-service/.venv
& design-software-monitoring-service/.venv/Scripts/python.exe -m pip install -r design-software-monitoring-service/requirements-runtime.lock
& design-software-monitoring-service/.venv/Scripts/python.exe -m pip install -e 'design-software-monitoring-service[dev]'
& design-software-docker-infra/scripts/up-monitoring-stack.ps1
npm ci --prefix design-software-web-shell
npm ci --prefix design-software-monitoring-mfe
npm exec --prefix design-software-web-shell -- playwright install chromium
```

El arranque crea la identidad RSA local y su token de ocho horas en una carpeta ignorada. Si ya existe la `.venv`, no es necesario recrearla. El script valida el proyecto aislado, aplica las migraciones oficiales y espera readiness. MFE y shell se ejecutan realmente en contenedores Node, con Federation; no se usa el BFF simulado. Los puertos de demostración son API/shell 15000, MFE 5108, Grafana 13000, Prometheus 19090, Tempo 13200, PostgreSQL 15439 y RabbitMQ 5679.

Para crear un KPI desde el navegador y guardar evidencia:

```powershell
Push-Location design-software-web-shell
node scripts/r3-e2e.mjs --headed
Pop-Location
& design-software-monitoring-service/.venv/Scripts/python.exe design-software-monitoring-service/scripts/collect_r3_evidence.py
```

`--headed` abre la prueba en una ventana visible durante un minuto. La identidad de prueba se entrega mediante sessionStorage sin imprimir el token. Para una sesión manual posterior, abrir DevTools en `http://localhost:15000`, copiar localmente el contenido de `design-software-docker-infra/local-monitoring/access-token.txt` en `sessionStorage.setItem('sena.access_token', '<token local>')` y recargar `/monitoring/seguimiento`. No incluir ese token en diapositivas, capturas ni Git.

Para ejecutar el flujo de negocio con RabbitMQ y PostgreSQL reales:

```powershell
& design-software-monitoring-service/.venv/Scripts/python.exe design-software-monitoring-service/scripts/test_r3_business.py
```

La entrada es un evento de prueba `academic.ficha.opened`, no una afirmación de que se ejecutó Academic Service. El worker real crea seguimiento, KPI, alerta y outbox; el script consulta la API, crea un plan, resuelve la alerta y verifica el resumen de KPI y el contador de alertas. Las integraciones con productores externos, Notification y Audit siguen sujetas a sus HU.

Para la alerta:

```powershell
& design-software-monitoring-service/.venv/Scripts/python.exe design-software-monitoring-service/scripts/test_r3_alert.py
```

Abre previamente `http://localhost:13000/d/monitoring-r3` y `/alerting/list`. El script genera solicitudes válidas, agrega `GET /api/v1/kpi-types?page=0` (HTTP 422), comprueba Firing en ambos motores y después mantiene solo tráfico válido hasta observar recuperación. Guarda estados y capturas reales. No cerrar el script durante la fase de recuperación. Si se interrumpe, dejar pasar la ventana y generar tráfico válido; el estado regresará al bajar el porcentaje a 5 % o menos.

## Guion de diez minutos

| Tiempo | Demostración y explicación |
|---|---|
| 0–1 | Presentarme, mencionar acta, dominio y los cuatro requisitos R3. Declarar qué se verificó y qué depende de otras HU |
| 1–2 | Mostrar el diagrama real. Distinguir HTTP, eventos, almacenamiento y recolección de señales |
| 2–4 | Ejecutar la creación de KPI desde el shell. Mostrar POST 201, encabezados W3C, fila PostgreSQL y `trace-summary.json`; abrir la traza en Tempo |
| 4–5 | Explicar Rate, Errors y Duration con consultas reales de `05-metricas/prometheus-panels.json` |
| 5–6 | Buscar en Loki `{service_name="monitoring-service"} |= "<correlation_id>"`; mostrar que el trace_id coincide |
| 6–8 | Mostrar dashboard y alerta. Iniciar el script de alerta al minuto 4, mientras se explican métricas y logs, para alcanzar Firing en vivo sin fingir tiempos |
| 8–9 | Mostrar pytest con PostgreSQL, Vitest, Playwright, códigos de salida y ADR |
| 9–10 | Explicar límites: identidad local firmada, HU externas abiertas y PR propios pendientes de revisión. Mostrar un cambio pequeño y su prueba |

Ensayar una vez midiendo el tiempo en este equipo. La evaluación corre cada 10 s, requiere 20 s de condición sostenida y consulta un minuto; carga del equipo y exportación agregan retraso. No prometer activación instantánea. Dejar que la recuperación continúe al cerrar la explicación.

## Veinticinco preguntas y respuestas

1. **¿Qué es observabilidad?** Poder investigar el estado interno del sistema mediante señales producidas por su ejecución. Aquí observamos trazas, métricas y logs reales.
2. **¿Por qué no bastan logs?** Describen eventos concretos, pero no ofrecen solos tasas agregadas ni el árbol causal y los tiempos de una petición distribuida.
3. **¿Qué es OpenTelemetry?** El conjunto de APIs, SDK e instrumentadores que usamos para crear y exportar telemetría sin depender de un APM propietario.
4. **¿Qué representa un span?** Una operación con inicio, fin, atributos, estado y padre. El INSERT SQL y el POST HTTP tienen spans distintos.
5. **¿Qué es una traza distribuida?** El conjunto de spans relacionados de un mismo recorrido. En la evidencia participan monitoring-mfe y monitoring-service, incluida la operación PostgreSQL.
6. **¿Qué es trace_id?** Un identificador de 16 bytes compartido por todos los spans de la traza. Su valor real está en `04-tracing/trace-summary.json`.
7. **¿Qué es span_id?** Un identificador de 8 bytes para una operación dentro de la traza. El hijo guarda el identificador de su padre.
8. **¿Qué es traceparent?** El encabezado HTTP W3C con versión, trace ID, span padre y flags. Lo inyecta `src/observability.ts` del MFE.
9. **¿Qué establece W3C Trace Context?** El formato y las reglas de propagación de contexto entre componentes. Se utiliza el propagador oficial, no concatenación manual de trazas.
10. **¿Cómo viaja desde React al backend?** El MFE envuelve el cliente inyectado, inicia CLIENT e inyecta headers; el shell los conserva; Nginx los pasa y FastAPI extrae el padre.
11. **¿Cómo se relaciona con la base de datos?** SQLAlchemy ejecuta consultas reales con el contexto activo. El instrumentador crea el span SQL y hereda trace ID y padre.
12. **¿Qué es RED?** Rate es solicitudes por segundo; Errors, respuestas clasificadas como error; Duration, distribución temporal de solicitudes.
13. **¿Cómo se calcula la tasa de error?** Solicitudes 4xx/5xx divididas por todas las solicitudes de negocio, por 100, sobre la misma ventana. Liveness/readiness se excluyen de esta alerta.
14. **¿Qué hace Prometheus?** Obtiene series por scrape del Collector y de la sonda, conserva datos y evalúa consultas y reglas.
15. **¿Qué es PromQL?** Su lenguaje para calcular tasas, sumas y percentiles de histogramas. Las consultas aquí usan nombres realmente verificados.
16. **¿Qué hace Grafana?** Consulta Prometheus, Tempo y Loki; presenta paneles y evalúa la regla de alerta provisionada.
17. **¿Cómo se provisiona un dashboard?** El JSON vive en docker-infra y un proveedor YAML lo carga al iniciar Grafana. Se comprueba después de recrear el contenedor.
18. **¿Qué es correlation_id?** Un identificador de contexto de negocio/petición, distinto del trace ID. Se valida, devuelve y asocia a logs mediante ContextVar.
19. **¿Correlación y trazabilidad son lo mismo?** La correlación permite agrupar registros; la traza además conserva causalidad padre-hijo, operaciones y duraciones.
20. **¿Cómo dispara y recupera?** Más de 5 % durante 20 s, evaluado cada 10 s sobre un minuto. Con tráfico válido, la ventana se limpia y ambos motores vuelven a inactive/Normal.
21. **¿Qué es un ADR?** Un registro de contexto, alternativas, decisión, consecuencias y reversión. Este reto complementa ADR-008 con una decisión local verificable.
22. **¿Ventajas y costos?** Facilita localizar errores y latencia, pero consume CPU, memoria, red y almacenamiento. No medimos un benchmark y no inventamos cifras de overhead.
23. **¿Cómo evitamos datos sensibles?** No registramos cuerpos ni tokens; usamos rutas normalizadas y errores por tipo; el Collector elimina consultas textuales y detalles de excepciones. Solo se monta la clave pública.
24. **¿Qué archivos modifiqué?** Composition root, observability.py, auth.py, serialización/paginación y readiness en backend; cliente MFE y shell; Compose, reglas y dashboard; pruebas/scripts y documentación. El informe lista las rutas exactas.
25. **¿Cómo demostrar que funciona?** Ejecutar Playwright sobre los contenedores reales, recuperar la misma traza de Tempo, comprobar su cadena de padres y la fila PostgreSQL, consultar Loki y Prometheus y observar Firing y recuperación.

## Ejercicios de modificación en vivo

Realizar sobre una rama temporal creada desde los commits del reto, con el árbol limpio. Revisar siempre `git diff` y revertir únicamente las líneas del ejercicio. No ejecutar una restauración general sobre cambios de otros.

| # | Archivo exacto y fragmento actual | Cambio solicitado y razón | Cómo comprobar | Cómo revertir |
|---|---|---|---|---|
| 1 | `design-software-monitoring-service/src/monitoring/observability.py`: `span.set_attribute("correlation_id", correlation)` | Añadir `span.set_attribute("monitoring.domain", "monitoring")`; atributo fijo y seguro | Reconstruir API, ejecutar E2E y mirar atributos en Tempo | Quitar solo el atributo añadido |
| 2 | `design-software-monitoring-mfe/src/observability.ts`: `monitoring.ui ${request.method} ${route}` | Cambiar el prefijo por `monitoring.request`; enseña que el nombre describe la operación | `npm test -- tests/unit/observability.test.ts`, build y nueva traza | Restaurar el prefijo |
| 3 | `design-software-monitoring-service/src/monitoring/observability.py`: `logger.info("http_request_completed", extra=...)` | Agregar un campo fijo `"domain": "monitoring"` a la salida JSON y su lista permitida en JsonFormatter | Test de formato y búsqueda Loki de solicitud nueva | Retirar campo y prueba específica |
| 4 | `design-software-monitoring-service/src/monitoring/observability.py`: `boundaries=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]` | Añadir límite `0.075`; mejora resolución entre 50 y 100 ms | Reconstruir, generar tráfico, consultar bucket `le="0.075"` | Retirar límite y reiniciar API |
| 5 | `design-software-docker-infra/observability/grafana/alerting/monitoring.yaml`: `for: 20s`; también `observability/alerts.yml` | Cambiar ambos a `30s`; demostrar evaluación sostenida | Reiniciar Grafana/Prometheus y ejecutar test de alerta | Volver ambos a `20s` |
| 6 | `design-software-docker-infra/observability/grafana/dashboards/monitoring-r3.json`: consulta `histogram_quantile(0.95, ...)` | Duplicar panel p95 como p90, con ID y posición nuevos | Consultar primero la expresión en Prometheus y abrir panel | Retirar únicamente el panel añadido |
| 7 | `design-software-monitoring-service/src/monitoring/observability.py`: regex `[A-Za-z0-9._-]{1,64}` | Reducir máximo a 48; reforzar validación de IDs entrantes | Añadir prueba de ID de 49 caracteres y comprobar sustitución por UUID | Volver a 64 y retirar prueba del ejercicio |
| 8 | `design-software-monitoring-service/tests/test_r3_observability.py`: `trace_id = '11111111111111111111111111111111'` | Usar otro ID válido y añadir aserción de que backend no lo reemplaza | `pytest -q tests/test_r3_observability.py` | Restaurar fixture sin cambiar implementación |
| 9 | `design-software-docker-infra/observability/grafana/dashboards/monitoring-r3.json`: panel `Requests by endpoint` | Filtrar `http_method="POST"`; enfocar operaciones de escritura | Ejecutar creación desde el navegador y consultar panel | Quitar el filtro |
| 10 | `design-software-monitoring-service/scripts/test_r3_alert.py`: `traffic(invalid=True)` usa `?page=0` | Usar `?page_size=0`, otra validación real 422 | Verificar primero HTTP 422 y después ciclo de alerta | Restaurar parámetro original |

Para cambiar el **nombre** de una métrica, localizar todas sus referencias con `rg monitoring_http_requests` en service e infra, cambiar instrumento, PromQL, reglas, dashboard y pruebas como una sola intervención. No renombrar solo el productor: dejaría paneles sin datos. Este ejercicio requiere más revisión que agregar un atributo seguro.
