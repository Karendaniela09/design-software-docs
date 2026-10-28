# Auditoría de errores de integración — 2026-10-27

> Estado: **PARCIALMENTE CORREGIDO**. Esta auditoría distingue el código revisado y las pruebas ejecutadas del estado aún desplegado en `srv2093837.hstgr.cloud`.

## Objetivo y alcance

Investigar los fallos observados desde el Web Shell de Gestión de Horarios: fichas académicas, Training Environments, Monitoring, OTLP, Reference Data, Scheduling y Actors. Se revisaron las ramas remotas `develop` y los repositorios presentes en el equipo; no se modificó ninguna rama protegida ni se desplegó producción.

## Flujo identificado

```text
Browser → Web Shell → remote MFE → Traefik (/dominio/api/v1) → servicio → PostgreSQL / RabbitMQ
```

El Web Shell entrega a los remotes un cliente HTTP de sesión. Ese cliente añade la autorización, renueva una sesión una vez ante un 401 y no expone el JWT al remote (ADR-023). Las rutas públicas por dominio se definen en Traefik (ADR-022).

## Repositorios auditados

| Repositorio | Componente | Base auditada | Hallazgo relevante | Estado |
|---|---|---|---|---|
| `design-software-web-shell` | Shell | `develop` | Ya inyecta `httpClient` a remotes, incluido Training Environments. | Validado por código |
| `design-software-training-environment-mfe` | MFE | `develop` | Llamaba rutas relativas sin prefijo ni cliente de sesión. | Corregido en PR #11 |
| `design-software-training-environment-service` | API Go | `develop` | Contrato real bajo `/api/v1/training-environments`; rutas sin prefijo no son API. | Validado por código y sonda pública |
| `design-software-monitoring-mfe` | MFE | `develop` | Usa `/monitoring/api/v1`; no se encontró una ruta MFE que explique el 502. | Bloqueado por upstream desplegado |
| `design-software-monitoring-service` | API FastAPI | `develop` | Expone `/api/v1/health`, `/ready` y catálogos. | Bloqueado por contenedor/upstream desplegado |
| `design-software-docker-infra` | Compose/Traefik/OTel | `develop` | Declara rutas `/monitoring/api/` y `/otlp/v1/traces`. | Código no coincide con proxy publicado |
| `design-software-academic-management-service` | API Java | `develop` | Protege fichas por contexto de centro. | Requiere asignación real de centro y token nuevo |
| `design-software-reference-data-service` | API Go | `develop` | Catálogos y jerarquía requieren JWT y permisos REF. | Alcanzable; requiere sesión autorizada |
| `design-software-actors-mfe` / `actors-service` | MFE/API Java | `develop` | Ambos definen `POST /actors/api/v1/instructors`. | El 405 corresponde a despliegue/proxy antiguo |
| `design-software-scheduling-mfe` / `scheduling-service` | MFE/API Java | `develop` | Shell ya transmite `activePage`, `apiBaseUrl` y cliente autenticado. | Falta prueba con sesión publicada |
| `design-software-iam-service` | IAM | `develop` | La validación de roles scoped exige `training_center_id`. | Seguridad correcta; datos de cuenta pendientes |

## Errores reproducidos y causas confirmadas

| Área | Evidencia | Causa confirmada | Conclusión |
|---|---|---|---|
| OTLP | `GET /otlp/v1/traces` respondió `200 text/html`; `POST` y `OPTIONS` respondieron `405 text/html`. | La VPS publicada lleva esas solicitudes al fallback HTML de Nginx, no al receptor OTLP. | Falta desplegar o corregir el proxy efectivo de la VPS. |
| Monitoring | `GET /monitoring/api/v1/health`, `/ready` y `/kpi-types` respondieron `502`. | El upstream `monitoring-api` no está disponible desde el proxy publicado. El 502 en liveness descarta que sea sólo autorización de catálogos. | Inspeccionar contenedor, logs, red y configuración efectiva antes de cambiar código. |
| Training Environments | En el código MFE se hallaron llamadas como `/training-environments` y `/reservations`. | El MFE alcanzaba el fallback SPA, que devuelve HTML, porque omitía `/training-environment/api/v1` y no usaba el cliente del Shell. | Corregido en PR #11. |
| Fichas académicas | La pantalla mostró `training_center_id is required for TRAINING_CENTER`; la sonda sin JWT responde `401`. | La cuenta coordinadora publicada carece de asignación institucional completa o usa un token emitido antes de asignarla. | No se debe inventar un centro ni debilitar el guard; un administrador debe asignar el centro real y renovar sesión. |
| Reference Data | `/reference-data/health` respondió `200 application/json`; `/api/v1/macroregions` respondió `401 application/json`. | El servicio está alcanzable y exige autenticación/feature REF, como el contrato. | Validar con un token autorizado, no quitar seguridad. |
| Actors | Código de MFE y API mapea `POST /actors/api/v1/instructors`. | La respuesta 405 observada no corresponde al `develop` auditado. | Confirmar imagen/proxy desplegado antes de modificar el contrato. |

## Hipótesis descartadas

- No se atribuyó el 502 de Monitoring al MFE: el endpoint de salud, sin dependencia de la pantalla, también falla.
- No se trató el 401 de Academic Management o Reference Data como evidencia de servicio roto: ambos servicios responden por rutas API y mantienen controles de acceso.
- No se cambió el método HTTP de Training Environments a ciegas: el contrato usa rutas plurales bajo `/api/v1` y los handlers declaran métodos específicos.
- No se introdujeron datos fijos ni centros de formación simulados para ocultar la falta de contexto institucional.

## Riesgos y dependencias

1. El Hostinger/VPS publicado no refleja de forma verificable el `develop` auditado: Monitoring y OTLP siguen atendidos por una configuración efectiva distinta.
2. La corrección del MFE de Training Environments requiere la imagen del remote actualizada en el despliegue para hacerse visible.
3. Las verificaciones funcionales de fichas, Reference Data y Scheduling requieren una sesión real con roles, features y `training_center_id` coherentes.
4. La captura de logs de `audit-worker` mostró timeouts del exporter OTLP; debe tratarse como señal de observabilidad y no como prueba de causa raíz de Monitoring sin revisar los logs de `monitoring-api`.

