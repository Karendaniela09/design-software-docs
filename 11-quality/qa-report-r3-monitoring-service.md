# Informe técnico — Plan de Mejoramiento R3 — Observabilidad de Monitoring

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

**Aprendiz:** Kevin Andrey Culma Gómez
**Ficha:** ADSO 3145555
**Dominio:** Monitoring
**Reto:** R3 — Observabilidad
**Fecha del corte documental:** 20 de octubre de 2026, America/Bogota

## 1. Introducción

La intervención atiende el Acta No. 02 del 14 de octubre de 2026. Se implementó y probó observabilidad sobre los componentes reales del dominio. El trabajo distingue la ejecución local verificada de la integración institucional y las HU que dependen de otros colaboradores. No se considera que un archivo de configuración, un mock o un issue cerrado prueben por sí solos el funcionamiento del producto.

## 2. Objetivos

Implementar un recorrido observable desde Monitoring MFE hasta PostgreSQL; medir solicitudes, errores y duración por endpoint; correlacionar logs JSON; provisionar Grafana y comprobar una alerta real superior al 5 %. Entregar comandos, pruebas, evidencias y material para reproducir y defender las decisiones.

## 3. Estado inicial

El workspace contiene 39 repositorios. Monitoring Service utiliza Python/FastAPI, SQLAlchemy/psycopg y RabbitMQ; la base se migra con Liquibase; el MFE y shell usan React/TypeScript y Module Federation. Ya existían OTel y Collector + LGTM, parcialmente conectados. Faltaban perfil Docker Monitoring, instrumentación de navegador, RED explícito y dashboard/alerta R3. El BFF local devolvía fixtures, no persistencia real. Se encontraron errores de serialización y paginación al consultar PostgreSQL, además de autenticación que decodificaba JWT sin verificar su firma.

El diagnóstico detallado y la matriz inicial están en [01-diagnostico](01-diagnostico/diagnostico.md). Se conservó el cambio local previo de `design-software-iam-mfe/vite.config.ts` fuera de estas ramas.

## 4. Parte 1 — Producto

El perfil oficial `monitoring` se extendió en docker-infra y se ejecutó sobre el proyecto aislado `ds-monitoring-r3`. Incluye PostgreSQL, RabbitMQ, API, worker, MFE, shell, proxy y observabilidad. Las 24 migraciones oficiales de Monitoring se aplicaron correctamente; ejecuciones posteriores informaron que ya estaban aplicadas. No se hicieron migraciones nuevas, limpiezas de volúmenes ni cambios sobre bases compartidas.

La prueba Playwright carga el MFE real dentro del shell, crea un tipo de KPI, verifica HTTP 201, recarga la página y comprueba que el registro sigue presente. Un script independiente consulta esa fila directamente en PostgreSQL. La prueba adicional intenta crear el mismo código: obtiene HTTP 409 real, conserva el formulario y verifica spans de error. No usa interceptores ni mocks de red.

La prueba de negocio envía un evento de entrada identificado como `r3-test-producer` a RabbitMQ real. El worker persiste seguimiento, KPI, alerta y outbox. El script consulta la API, crea un plan, resuelve la alerta, comprueba el contador de alertas y consulta el resumen de KPI. Esta prueba valida el consumidor y los servicios locales, **no** la emisión del evento desde Academic Service, el login de IAM, la entrega de Notification ni la auditoría externa.

La HU-MON-008 frontend (#225) figura cerrada y corresponde a otro aprendiz; se comprobaron los PR anteriores y sus ramas destino. Continúan abiertas HU-INT-MON-001 a 004 y varias HU históricas con códigos repetidos. El [inventario remoto](03-parte-1/historias-y-pr.md) conserva números, responsables, estados y fechas. GitHub Projects no pudo leerse por falta del scope `read:project`; se consultaron Issues y PR sin modificar sus estados.

La ampliación posterior sí verificó login IAM local, creación de ficha por Academic y una sesión del MFE persistida tras recargar. También se ejecutaron las cadenas de Actors y Scheduling con Notification, SMTP de pruebas y Audit. Estas son pruebas distintas con evidencias separadas; no constituyen una sola prueba UI de todo el ecosistema. Continúan pendientes el IdP institucional, el cierre de las HU externas y la reproducción sobre ramas fusionadas.

## 5. Parte 2 — R3

El MFE inicia spans CLIENT y propaga W3C `traceparent` mediante el cliente HTTP inyectado. El shell conserva los encabezados; Nginx los enruta; FastAPI extrae el padre y SQLAlchemy instrumenta operaciones reales. `collect_r3_evidence.py` verifica un mismo trace_id y recorre los padres del INSERT hasta el span frontend. También comprueba una traza de error de un conflicto real de PostgreSQL.

Las métricas OTel se exportan por Collector a Prometheus: `monitoring_http_requests_total` y `monitoring_http_duration_seconds_{bucket,sum,count}`. Sus etiquetas contienen método, ruta normalizada y estado HTTP. No contienen UUID, query strings ni identificadores de usuario. El histograma permite p50/p95/p99 agregables. Las consultas están en [promql.md](05-metricas/promql.md), con respuestas reales en `prometheus-panels.json`.

Los logs JSON incluyen timestamp UTC, nivel, servicio, mensaje, correlation_id, trace_id y span_id. La finalización HTTP agrega método, ruta, estado, duración y tipo de error. Un ContextVar se limpia en finally; las pruebas concurrentes verifican que cada petición conserve su identificador. Los IDs entrantes se validan. Loki recibe los logs mediante OTLP y permite buscar el mismo correlation_id de la operación del navegador. El Collector elimina consultas textuales, URLs completas y detalles sensibles de excepciones de las trazas.

Grafana carga datasources, 12 paneles y una regla declarativa. Once paneles consultan Prometheus y uno Loki; todas las expresiones Prometheus se consultaron con datos reales. Una sonda independiente comprueba readiness, incluida tabla PostgreSQL y broker. No se confunde disponibilidad del Collector con salud de la API.

La alerta cuenta **4xx y 5xx**, excluye liveness/readiness, usa ventana de un minuto, evaluación cada 10 s y condición `>5` sostenida 20 s. Se protege el denominador; sin tráfico el porcentaje es cero. Grafana configura NoData OK y errores del evaluador como Error. La prueba usa solicitudes válidas y validaciones reales 422, sin endpoint de fallos. Prometheus y Grafana alcanzaron Firing y regresaron a inactive/Normal. Se guardaron JSON y capturas de ambos estados. La captura del dashboard en Firing muestra aproximadamente 20 % de errores; no representa una medición de producción ni un SLA.

## 6. Arquitectura final

Ver [diagrama Mermaid y propagación](02-arquitectura/arquitectura.md). El recorrido HTTP observado es `web-shell/Monitoring MFE → Nginx → FastAPI → PostgreSQL`. La exportación va al Collector y luego a Tempo, Prometheus y Loki; Grafana consulta esos backends. El BFF con fixtures queda fuera del recorrido R3. No se inventan spans del proxy ni operaciones de base de datos.

## 7. Implementación y archivos

| Repositorio | Archivos principales y propósito |
|---|---|
| monitoring-service | `src/monitoring/observability.py`: ASGI, trazas, RED, logs y exportación; `auth.py`: JWT RS256/JWKS o clave pública; `adapter/inbound/http/router.py`: UUID, paginación y permisos; `readiness.py`: comprobar catálogo real; composition roots API/worker y adaptador AMQP; Dockerfile y lock; pruebas y scripts reales |
| monitoring-mfe | `src/observability.ts`: span por solicitud y propagación; App y contratos HTTP: cliente instrumentado; adaptador de catálogos: respuesta real paginada; package-lock y pruebas de telemetría |
| web-shell | `RemoteRoutes.tsx`: headers, token y catálogos reales; fuente de sesión R3 explícita para pruebas; scripts Playwright y capturas |
| docker-infra | `docker-compose.yml`, inicio de perfil, Nginx y sonda; Collector con privacidad; Prometheus; datasources, dashboard y alertas Grafana |

Se reutilizó OTel + LGTM del ADR-008. Se agregó PyJWT con soporte criptográfico y SDK web OTel. El lock Python fija las dependencias runtime verificadas, incluida SQLAlchemy 2.0.55 compatible con su instrumentador. El lock npm conserva las versiones web resueltas. Solo se monta la clave pública en la API; la clave privada y el token expirable quedan ignorados por Git. Grafana local permite Explore con rol Editor y escucha en 127.0.0.1; esa configuración de demostración debe revisarse antes de usar otro entorno.

## 8. Pruebas y procedimiento

Las salidas completas y sus metadatos están en `EVIDENCIAS-PLAN-MEJORAMIENTO-R3/08-pruebas/`, fuera de Git. La última suite backend local conservada informa **34 passed, 7 warnings** (`domains-backend-tests.txt`, 19 de octubre, 21:42). Las ejecuciones del MFE (65 pruebas) y shell (106), sus builds y lint son resultados previos del 19 de octubre; no se presentan como una nueva ejecución del conjunto final de PR. Las pruebas unitarias existentes que usan falsos siguen clasificadas como unitarias; la evidencia E2E proviene de los scripts contra contenedores reales.

Antes de estos comandos, completar el [checkout limpio y los montajes de dependencias compartidas](README.md#reproducción-local-desde-un-checkout-limpio). Los scripts viven en los repositorios de implementación; sus resultados se escriben en la carpeta raíz de evidencias.

Comandos desde la raíz del workspace:

```powershell
# INFRA: inicio oficial con migraciones, credenciales locales e identidad firmada
& design-software-docker-infra/scripts/up-monitoring-stack.ps1
# E2E: navegador real, alta y conflicto 409
Push-Location design-software-web-shell
node scripts/r3-e2e.mjs
Pop-Location
# COLLECT: verificar padres, INSERT, fila PostgreSQL, Loki y consultas Prometheus
& design-software-monitoring-service/.venv/Scripts/python.exe design-software-monitoring-service/scripts/collect_r3_evidence.py
# BUSINESS: broker, worker, seguimiento, KPI, alerta, plan y resolución
& design-software-monitoring-service/.venv/Scripts/python.exe design-software-monitoring-service/scripts/test_r3_business.py
# ALERT: tráfico, Firing, capturas y recuperación real
& design-software-monitoring-service/.venv/Scripts/python.exe design-software-monitoring-service/scripts/test_r3_alert.py
# VERIFY: Compose, promtool, DNS, fuente desplegada y dashboard provisionado
& design-software-monitoring-service/.venv/Scripts/python.exe design-software-monitoring-service/scripts/verify_r3_infra.py
```

La [guía de sustentación](09-sustentacion/guia.md) incluye instalación, arranque, pruebas y demostración. Para la suite backend con la base local, desde monitoring-service ejecutar `.venv/Scripts/python.exe scripts/record_check.py --database backend-local -- .venv/Scripts/python.exe -m pytest -q`; el harness carga la URL desde el archivo ignorado sin imprimir la contraseña.

El fallo inicial de Actions por ausencia del contrato privado se corrigió con una instantánea oficial fijada y verificada por SHA-256 para checkout independiente; la prueba no se desactivó. Se conservaron fallos intermedios y las correcciones en [incidencias-corregidas.md](08-pruebas/incidencias-corregidas.md). Persisten advertencias no fatales de defaults SQL y TestClient. Los reintentos no se presentan como si los intentos previos hubieran pasado.

## 9. Resultados y matriz vigente

La [matriz final](matriz-final.md) es la única matriz vigente de este dossier. Identifica la última evidencia disponible por criterio, su fecha y sus límites. No se declara una nueva validación E2E por haber corregido documentación.

| Último escenario local conservado | Resultado | Evidencia relativa a la carpeta raíz de evidencias |
|---|---|---|
| IAM local: login, perfil, JWKS, 401/403 | Aprobado, 19 oct. 20:35 | `03-parte-1/iam-integration.json` |
| Academic → Monitoring | Aprobado, 19 oct. 20:36 | `03-parte-1/academic-integration.json` |
| Sesión del navegador y persistencia tras recargar | Aprobado, 19 oct. 20:48 | `03-parte-1/main-flow-browser.json`, `main-flow-postgres.json`; `08-pruebas/main-flow-bogota.json` tiene exit_code=0 |
| Suite backend con PostgreSQL/RabbitMQ | 34 passed, 7 warnings, 19 oct. 21:42 | `08-pruebas/domains-backend-tests.txt` |
| Actors → Monitoring → Notification/SMTP → Audit | Aprobado, 19 oct. 22:50 | `03-parte-1/domains-integration.json` |
| Scheduling: publicación/cancelación y consumidores | Aprobado, 19 oct. 22:54 | `03-parte-1/scheduling-integration.json` |

La última traza de catálogo conservada es `1541ef6e05e37e0356b570c7b2c37b5c`, ocho spans, capturada el 19 de octubre a las 16:55. La captura de Tempo Explore se obtuvo a las 18:15. El INSERT duró 6.414150 ms en esa operación individual; no es un benchmark ni una medición de la prueba de dominios posterior. El último ciclo de alerta terminó a las 16:52 con recuperación. Las pruebas posteriores de dominios no vuelven a demostrar por sí mismas trazas, percentiles ni alertas Grafana.

## 10. HU y Pull Requests

Consulta remota: `2026-10-20T17:05:38-05:00`.

| HU externa | Issue | Estado remoto | Evaluación del plan |
|---|---|---|---|
| HU-INT-MON-001 | [#322](https://github.com/code-sena/design-software-docs/issues/322) | OPEN | PARCIAL |
| HU-INT-MON-002 | [#323](https://github.com/code-sena/design-software-docs/issues/323) | OPEN | PARCIAL |
| HU-INT-MON-003 | [#324](https://github.com/code-sena/design-software-docs/issues/324) | OPEN | PARCIAL |
| HU-INT-MON-004 | [#325](https://github.com/code-sena/design-software-docs/issues/325) | OPEN | PARCIAL |

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

La publicación de un PR y una prueba local aprobada no equivalen al cierre de una HU externa. Se registra la rama y el estado real, sin asumir que OPEN significa borrador o que un merge commit calculado por GitHub representa una fusión.

## 11. Limitaciones y pendientes

- El IdP institucional no se probó por falta de acceso. IAM local sí fue verificado; la cuenta aislada usa permisos de prueba documentados.
- Los escenarios de Actors y Scheduling usan identidades, matrículas y referencias aisladas según los scripts. No certifican disponibilidad de Training Environment ni todos los alcances de instructor por ficha.
- Las HU externas #322–#325 siguen OPEN: su evaluación permanece PARCIAL.
- Los PR no están fusionados en la consulta actual. Falta repetir el arranque limpio sobre las ramas destino después de su integración; P1-A y la verificación del provisionamiento final permanecen PARCIAL.
- CI de Monitoring aprueba el head consultado; Actors y Scheduling presentan checks fallidos. Sus enlaces y heads están en [estado-actual.md](estado-actual.md). Una ejecución local favorable no sustituye esos checks.
- La guía de sustentación y los diez ejercicios están preparados; su práctica personal sigue pendiente y se marca PARCIAL.
- MFE y shell se ejecutaron en desarrollo con Federation local. No se certifica un despliegue de producción ni se ha medido overhead mediante benchmark.

## 12. Referencias

- ADR canónico: [`05-architecture/decisions/records/ADR-010-monitoring-r3-observability.md`](../../../05-architecture/decisions/records/ADR-010-monitoring-r3-observability.md).
- [Matriz final](matriz-final.md), [estado actual](estado-actual.md) y [procedimiento de checkout y montajes](README.md#reproducción-local-desde-un-checkout-limpio).
- [Arquitectura](02-arquitectura/arquitectura.md) y [guía de sustentación](09-sustentacion/guia.md).
- Archivo completo de evidencias originales en `EVIDENCIAS-PLAN-MEJORAMIENTO-R3/`; el informe breve adjunta una selección revisada en este repositorio.

PR documental anterior: [#330](https://github.com/code-sena/design-software-docs/pull/330), **CLOSED**, sin fusionar; sustituido por el PR de `fix/r3-observability`.

Versión breve para entrega, con evidencia incluida en el repositorio: [informe-tecnico-breve.md](informe-tecnico-breve.md).
