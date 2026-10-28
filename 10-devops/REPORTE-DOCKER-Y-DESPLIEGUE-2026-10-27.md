# Reporte Docker y despliegue — 2026-10-27

> Estado del despliegue publicado: **BLOQUEADO PARA APROBACIÓN FUNCIONAL**. No se realizaron reinicios, reconstrucciones ni cambios productivos durante esta auditoría.

## Configuración auditada

La rama `develop` de `design-software-docker-infra` declara:

- Traefik como edge en el puerto interno 80, con `/monitoring/api/` hacia `monitoring-api:8000`.
- `/otlp/v1/traces` hacia `otel-collector:4318`, reescrito a `/v1/traces`.
- `monitoring-api` con PostgreSQL, RabbitMQ, healthcheck en `/api/v1/health` y perfil `monitoring`.
- API Training Environments en `training-api:8080`, expuesta como `/training-environment/api/`.
- API Reference Data en `reference-data-api:8080`, expuesta como `/reference-data/api/`.

## Sondas al servidor publicado

| Ruta | Resultado | Lectura |
|---|---|---|
| `/monitoring/api/v1/health` | 502 | Upstream Monitoring inaccesible desde el proxy. |
| `/monitoring/api/v1/ready` | 502 | Igual que health; no es un fallo de permisos de UI. |
| `/monitoring/api/v1/kpi-types` | 502 | Catálogo bloqueado por mismo upstream. |
| `GET /otlp/v1/traces` | 200 `text/html` | Ruta cae en fallback web, no en collector. |
| `POST /otlp/v1/traces` | 405 `text/html` | Nginx/fallback publicado no permite el método; no llegó a collector. |
| `OPTIONS /otlp/v1/traces` | 405 `text/html` | Preflight tampoco llega al receptor. |
| `/training-environment/health` | 200 JSON | Servicio accesible. |
| `/training-environment/api/v1/training-environments` sin JWT | 401 JSON | Edge y servicio responden por ruta correcta. |
| `/reference-data/health` | 200 JSON | Servicio accesible. |
| `/reference-data/api/v1/macroregions` sin JWT | 401 JSON | Edge y guard de autenticación operativos. |
| `/academic-management/actuator/health` | 200 JSON | Servicio accesible. |
| `/academic-management/api/v1/fichas` sin JWT | 401 | Endpoint protegido, no prueba de éxito funcional. |

## Causa probable y acciones obligatorias en la VPS

La evidencia es compatible con un despliegue cuyo proxy/stack no corresponde al `develop` auditado. Para confirmar la causa sin riesgo se requiere, en la misma composición que sirve `srv2093837.hstgr.cloud`:

1. Identificar el compose, proyecto Docker y proxy frontal que realmente publica el host.
2. Ejecutar `docker compose ps` y `docker ps -a`; registrar estado y health de `traefik`, `monitoring-api`, `otel-collector`, `postgres` y `rabbitmq`.
3. Revisar `docker compose logs --tail=200 monitoring-api traefik otel-collector`, sin publicar secretos.
4. Ejecutar `docker compose config` y contrastar la tabla efectiva de rutas con `traefik/dynamic.yml` de `develop`.
5. Desde Traefik, probar `http://monitoring-api:8000/api/v1/health`; desde el collector, comprobar receptor HTTP 4318.
6. Sólo después de la inspección, actualizar el compose/imágenes y realizar el despliegue autorizado.

## Riesgos de despliegue

- No reiniciar todos los servicios a la vez: Monitoring depende de PostgreSQL y RabbitMQ.
- No desactivar OTLP para ocultar el 405; si el collector no existe, su deshabilitación debe ser explícita por variable y documentada.
- No agregar `training_center_id` fijo ni quitar guards para resolver fichas académicas.
- Antes de validar interfaces, asignar a la cuenta coordinadora el centro real y emitir un token nuevo.

## Estado final de esta auditoría

La corrección del MFE de Training Environments está disponible para revisión. Monitoring y OTLP permanecen bloqueados hasta revisar el runtime de la VPS y desplegar configuración/imágenes consistentes. Las APIs Academic Management y Reference Data son alcanzables, pero requieren una sesión autorizada para validación funcional completa.
