# ADR-R3 — Observabilidad verificable de Monitoring

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

Estado: implementada en la rama del reto, pendiente de revisión y fusión por el equipo. Fecha: 19 de octubre de 2026. Complementa el ADR-008 central; el repositorio del servicio no tenía directorio ADR propio.

## Contexto y problema

El Acta No. 02 exige producto ejecutable, trazas desde MFE hasta PostgreSQL, RED por endpoint, JSON con correlation_id y dashboard/alerta >5 %. Existía Collector + LGTM y OTel parcial; el shell consumía fixtures de un BFF, los exportadores no separaban rutas OTLP, faltaba instrumentación de navegador y no existía perfil Monitoring. No había evidencia E2E sin mocks. La API tenía defectos al serializar UUID y al devolver paginación contraria al contrato.

## Alternativas

| Alternativa | Evaluación |
|---|---|
| Extender OTel + Collector + Tempo/Prometheus/Loki/Grafana | Elegida: reutiliza ADR-008, infraestructura real y dependencias Python existentes; correlaciona las tres señales sin servicio propietario |
| Instalar Jaeger y un segundo colector | Aporta trazas, pero duplica la infraestructura existente y no resuelve métricas ni logs |
| Exponer métricas con prometheus-client independiente | Válida; añade otra API de instrumentación y endpoint cuando ya existe SDK OTel y exporter Prometheus del Collector |
| Instrumentar globalmente todos los fetch del navegador | Riesgo de capturar otras rutas, exportadores y tokens; el cliente HTTP inyectado permite instrumentar el límite real sin afectar otros dominios |
| Conservar fixtures del BFF para E2E | Rechazada: no demuestra persistencia, contexto ni servicios reales |

## Decisión e implementación

Se instrumenta explícitamente la fachada del cliente HTTP del MFE con SDK web OTel, sin parchear fetch global. Cada operación conserva su span hasta resolver o rechazar la promesa y transmite encabezados al shell. La exportación usa `/otlp/v1/traces` del mismo origen; no necesita CORS amplio ni origen comodín. Federation continúa usando la integración oficial del shell.

La API usa los instrumentadores FastAPI y SQLAlchemy, más middleware ASGI para el span de operación, métricas y logs. La instrumentación SQL se limita a SQLAlchemy `<2.1`, rango compatible con el instrumentador realmente instalado; `requirements-runtime.lock` fija las versiones ejecutadas. Cada exportador OTLP HTTP utiliza su sufijo `/v1/traces`, `/v1/metrics` o `/v1/logs`. El worker recibe contexto W3C AMQP y usa la misma instrumentación SQL real.

El encabezado W3C `traceparent` se inyecta mediante propagador oficial; FastAPI lo extrae. SQLAlchemy hereda el contexto activo. La evidencia no reconstruye identificadores: verifica el mismo trace_id y la cadena de padres del INSERT hasta el CLIENT del MFE.

RED usa `monitoring_http_requests_total` y `monitoring_http_duration_seconds_{bucket,sum,count}` exportados desde instrumentos OTel. Etiquetas: método, plantilla de ruta y código HTTP; las rutas no reconocidas usan `unmatched`. No hay UUID, correlaciones, query strings ni identidades como etiquetas. El histograma usa límites 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5 y 5 segundos. PromQL calcula p50/p95/p99 agregables; no se confunden medias con percentiles.

Los errores RED son explícitamente **HTTP 4xx y 5xx**. Una validación rechazada es error de cliente, no fallo de servidor. Health y readiness quedan fuera del porcentaje de la alerta. La ventana es un minuto, scrape 5 s, evaluación 10 s y condición sostenida 20 s. La comparación es estricta `>5`; recuperación `<=5`. Sin tráfico, el denominador se protege con `clamp_min` y el porcentaje resulta cero; no se exige un mínimo de tráfico. Grafana considera NoData OK y fallos de evaluación Error. La sonda independiente muestra disponibilidad real, porque `up` del Collector no demuestra salud de la API.

Los logs JSON tienen servicio configurable, timestamp UTC, nivel, mensaje, trace_id/span_id y correlation_id; la finalización agrega método, ruta, estado y duración. El contexto se limpia incluso ante excepciones. El Collector conserva la operación SQL pero elimina consultas textuales y detalles de excepciones; no se registran tokens. Loki centraliza la salida y permite buscar por correlación. Grafana incluye campos derivados para abrir Tempo.

Datasources, dashboard y reglas de Grafana y Prometheus están versionados en docker-infra. La doble evaluación permite comprobar estados con API pública de lectura y mostrar la alerta en Grafana. La prueba usa GET válidos y `page=0` (422) en el entorno aislado; no hay endpoint de fallo ni interrupción deliberada de servicios.

## Seguridad, rendimiento y consecuencias

La composición de la API verifica JWT RS256 con issuer, audience y expiración. Soporta JWKS real y una clave pública montada para el entorno local. Sin configuración falla cerrada; los JWT sin firma se limitan a fixtures unitarios inyectados explícitamente. El perfil R3 no demuestra el login institucional de IAM. No monta clave privada en contenedores ni versiona tokens. El script solo admite el proyecto `ds-monitoring-r3`, con volúmenes separados y sin limpieza destructiva.

Costos: spans adicionales por petición, exportación en lotes, memoria para histogramas y operación de seis componentes de observabilidad/proxy. El muestreo de la demostración es completo para poder inspeccionar solicitudes; el volumen y retención deben revisarse antes de producción. La sonda verifica DB y broker cada 5 s, costo aceptable en demostración pero ajustable para operación continua. No se midió un benchmark de overhead; no se afirma una mejora de rendimiento.

Riesgos restantes: otras HU de integración siguen abiertas; las notificaciones, auditoría y productores externos requieren validación propia. Un ambiente sin tráfico puede mostrar tasas cero; los scripts generan tráfico real. Los rangos antiguos sin lock resolvían versiones incompatibles. Algunas pruebas existentes se llamaban E2E pero usaban falsos; no se usan como prueba de producto.

## Validación y reversión

Consultar `EVIDENCIAS-PLAN-MEJORAMIENTO-R3/08-pruebas/` para comandos, fechas y códigos de salida; `04-tracing/trace-summary.json` demuestra padres y SQL; `03-parte-1/postgres-persisted-row.json` contiene la fila real; `07-grafana/alert-firing.json` y `alert-recovered.json` contienen estados observados. La matriz final distingue integración externa y fusión de PR pendientes.

Reversión: revertir los commits propios por repositorio después de revisión, detener únicamente los servicios del proyecto R3 si ya no se usan y conservar volúmenes para auditoría. No borrar datos ni usar `down -v`. Los cambios no requieren nuevas migraciones; el esquema procede de changelogs oficiales ya existentes. Retirar el perfil local y las reglas R3 no altera otros dominios.

## Referencias

- [OTel Web SDK](https://open-telemetry.github.io/opentelemetry-js/modules/_opentelemetry_sdk-trace-web.html).
- [Transform Processor del Collector](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/transformprocessor/README.md).
- [Provisionamiento de alertas Grafana](https://grafana.com/docs/grafana/latest/alerting/set-up/provision-alerting-resources/file-provisioning/).
- ADR-008 del repositorio design-software-docs y contrato `07-api/contracts/openapi/monitoring.yaml`.


## Integracion con IAM real local

El perfil adicional usa JWKS del servicio IAM y permite configurar audiencia vacia porque su token de usuario no contiene aud. El perfil R3 original conserva audiencia monitoring. La verificacion RS256, emisor, exp y sub sigue obligatoria, y una audiencia inesperada se rechaza. La prueba real incluye 200 autorizado, 401 por firma alterada y 403 para usuario sin rol. Ver 03-parte-1/validacion-integraciones.md en el expediente R3. Los PR se mantienen abiertos por instruccion del usuario.
