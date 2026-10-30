# DS-001 — Baseline de arquitectura para estabilización

> Estado: En revisión arquitectónica
> Corte documental: 2026-10-30
> Responsable del entregable: `Juan282007`
> Repositorio: `design-software-docs`
> Vencimiento registrado en BACKLOG_DESIGN_SOFTWARE: 2026-10-30 14:00 COT

Este baseline reúne el inventario de servicios, las rutas públicas previstas, las dependencias conocidas y los riesgos de integración para la estabilización. Describe contratos y evidencia disponible; no certifica por sí solo despliegues ni respuestas de endpoints.

## Alcance y trazabilidad

El tablero asigna DS-001 a `Juan282007` y solicita una matriz de endpoints/entornos y riesgos, además de un inventario con responsable y hora. El plan maestro adjunto, §§9–10, contiene un inventario de 41 repositorios y una asignación de 33 entregas. Este documento toma de allí los responsables de seguimiento y los vencimientos; ser responsable de seguimiento no transfiere propiedad del código ni permisos del repositorio.

**Discrepancia de vencimiento:** el plan Markdown indica DS-001 para las 11:00 COT, mientras que la fila DS-001 de la hoja de backlog indica 14:00 COT. Se conserva 14:00 como dato del tablero consultado y se registra la diferencia para que Arquitectura la resuelva; no se altera ninguna fuente.

## Convención de rutas

De acuerdo con [ADR-022](../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md), el navegador usa el origen del edge del ambiente. Las llamadas de API usan `/<dominio>/api/v1`; los health checks conservan las rutas específicas de cada servicio. El edge también sirve los remotes en `/mfe/<dominio>/` y entrega el web-shell para las rutas de SPA restantes.

| Dominio | Base API pública | Backend principal | Health documentado / reportado |
|---|---|---|---|
| IAM | `/iam/api/v1` | `iam-api:8080` | `/iam/actuator/health` |
| Scheduling | `/scheduling/api/v1` | `scheduling-api:8080` | `/scheduling/actuator/health` |
| Academic Management | `/academic-management/api/v1` | `academic-api:8080` | `/academic-management/actuator/health` |
| Training Environment | `/training-environment/api/v1` | `training-api:8080` | `/training-environment/health` |
| Reference Data | `/reference-data/api/v1` | `reference-data-api` | `/reference-data/health` |
| Actors | `/actors/api/v1` | `actors-api:8080` | `/actors/actuator/health` |
| Document | `/document/api/v1` | `document-api:8080`; templates route to `document-template-api:8080` | `/document/health` |
| Monitoring | `/monitoring/api/v1` | `monitoring-api:8000` | `/monitoring/api/v1/health`, `/monitoring/api/v1/ready` |
| Audit | `/audit/api/v1` | `audit-query-api:8080` | `/audit/health` |
| Notification | `/notification/api/v1` | `notification-api:8080` | `/notification/health` |

`<dominio>` is the exact prefix shown in the table. The Document templates exception is `/document/api/v1/document-templates`; ADR-022 routes it to the template API. Internal container targets are configuration names, not public URLs.

## Rutas por entorno

La tabla de [10-devops/environments.md](../10-devops/environments.md) define los puertos de entrada del edge. Las URL de API se forman como `{origen del ambiente}{base API pública}`; no se registra un hostname público donde no hay evidencia verificable.

| Entorno | Origen local del edge | API pública resultante | Estado de aplicación en la documentación consultada |
|---|---|---|---|
| `develop` | `http://localhost:18080` | `http://localhost:18080/<dominio>/api/v1` | Capa de aplicación y edge configurados. El operador reportó el 2026-10-30 respuestas HTTP 200 en los diez health checks listados arriba. Esta revisión documental no repitió los probes. |
| `qa` | `http://localhost:18081` | `http://localhost:18081/<dominio>/api/v1` | La documentación de ambientes, actualizada el 2026-10-24, describe solo la capa de datos materializada; disponibilidad de APIs pendiente de confirmar. |
| `staging` | `http://localhost:18082` | `http://localhost:18082/<dominio>/api/v1` | La documentación de ambientes describe solo la capa de datos materializada; disponibilidad de APIs pendiente de confirmar. |
| `main` | `http://localhost:18083` | `http://localhost:18083/<dominio>/api/v1` | La documentación de ambientes describe solo la capa de datos materializada; no se infiere un despliegue de aplicación productivo. |

Los puertos de arriba son los publicados para ejecución local según ADR-007; no se deben confundir con dominios DNS de VPS. Los health checks reportados como 200 confirman disponibilidad básica observada por el operador, no autorización de catálogos ni funcionamiento funcional de cada pantalla.

## Inventario de APIs y responsables de seguimiento

Los responsables y vencimientos de entregas se copian del backlog compartido el 2026-10-30. `—` significa que el backlog no asigna una entrega DS específica a ese repositorio en la fila identificada; no significa que no tenga mantenedor.

| Servicio | Repositorio de servicio | Repositorio DB | Responsable de seguimiento | Entrega DS relacionada y vencimiento (COT) |
|---|---|---|---|---|
| IAM | [`design-software-iam-service`](https://github.com/code-sena/design-software-iam-service) | [`design-software-iam-db`](https://github.com/code-sena/design-software-iam-db) | `joseale879` | DS-011 — 2026-10-30 16:00 |
| Reference Data | [`design-software-reference-data-service`](https://github.com/code-sena/design-software-reference-data-service) | [`design-software-reference-data-db`](https://github.com/code-sena/design-software-reference-data-db) | `STIVENPM` | DS-014 — 2026-11-01 14:00 |
| Academic Management | [`design-software-academic-management-service`](https://github.com/code-sena/design-software-academic-management-service) | [`design-software-academic-management-db`](https://github.com/code-sena/design-software-academic-management-db) | `STIVENPM` | DS-013 — 2026-10-31 18:00 |
| Training Environment | [`design-software-training-environment-service`](https://github.com/code-sena/design-software-training-environment-service) | [`design-software-training-environment-db`](https://github.com/code-sena/design-software-training-environment-db) | `Juan282007` | Smoke/no-regresión; sin hora DS individual |
| Scheduling | [`design-software-scheduling-service`](https://github.com/code-sena/design-software-scheduling-service) | [`design-software-scheduling-db`](https://github.com/code-sena/design-software-scheduling-db) | `Juan282007` | Smoke/no-regresión; sin hora DS individual |
| Actors | [`design-software-actors-service`](https://github.com/code-sena/design-software-actors-service) | [`design-software-actors-db`](https://github.com/code-sena/design-software-actors-db) | `Juan282007` | Smoke/no-regresión; sin hora DS individual |
| Document | [`design-software-document-service`](https://github.com/code-sena/design-software-document-service) | [`design-software-document-db`](https://github.com/code-sena/design-software-document-db) | `joseale879` | DS-012 — 2026-10-31 18:00 |
| Monitoring | [`design-software-monitoring-service`](https://github.com/code-sena/design-software-monitoring-service) | [`design-software-monitoring-db`](https://github.com/code-sena/design-software-monitoring-db) | `daniel2004-lsd` | DS-009 — 2026-10-30 14:00; DS-010 — 2026-10-31 17:00 |
| Audit | [`design-software-audit-service`](https://github.com/code-sena/design-software-audit-service) | [`design-software-audit-db`](https://github.com/code-sena/design-software-audit-db) | `Juan282007` | Sin cambios previstos salvo regresión; sin hora DS individual |
| Notification | [`design-software-notification-service`](https://github.com/code-sena/design-software-notification-service) | [`design-software-notification-db`](https://github.com/code-sena/design-software-notification-db) | `Juan282007` | Validación de no-regresión; sin hora DS individual |

Otros repositorios transversales y sus responsables de seguimiento están en el inventario de 41 repositorios del plan maestro; DS-001 no cambia sus asignaciones.

## Dependencias conocidas

La clasificación distingue HTTP síncrono de mensajería asíncrona. La matriz refleja las dependencias registradas en [09-microservices/dependency-map.md](../09-microservices/dependency-map.md) y debe verificarse contra la configuración y los logs del despliegue antes de tratarla como prueba de ejecución.

| Tipo | Origen | Destino(s) | Propósito |
|---|---|---|---|
| HTTP síncrono | Academic Management | Reference Data, Actors | Consultas institucionales y validación de ownership/alcance de fichas |
| HTTP síncrono | Actors | Academic Management | Consultas de ficha y competencias |
| HTTP síncrono | Scheduling | Academic Management | Validación de ficha/programa |
| HTTP síncrono | Training Environment | Reference Data | Referencia institucional y centros |
| Autenticación | IAM | Servicios protegidos | Emisión JWKS/JWT; cada servicio verifica issuer, audience y permisos según su configuración |
| AMQP/eventos | IAM, Reference Data, Academic Management, Training Environment, Actors, Scheduling, Monitoring, Notification | Principalmente Audit; además Monitoring, Actors, Scheduling, Document y Notification según productor | Auditoría y propagación de eventos de dominio; revisar bindings/consumidores en cada servicio |

La autenticación con IAM es dependencia transversal, no dependencia de negocio. La presencia de una flecha en el mapa conceptual tampoco demuestra que un listener o binding esté desplegado.

## Hallazgos y riesgos al corte

La evidencia operativa de esta sección proviene de las capturas y datos compartidos por el usuario en el contexto de DS-001. No se accedió a logs de VPS ni se hicieron llamadas autenticadas durante esta tarea.

| Severidad | Área | Hallazgo observado/reportado | Verificación o dueño de seguimiento |
|---|---|---|---|
| S1/S2 por confirmar | Academic Management — Fichas | `GET /academic-management/api/v1/fichas` devolvió 403; la UI reportó `training_center_id is required for TRAINING_CENTER`. Riesgo de claim/contexto institucional incompleto o asignación sintética no provisionada. | DS-013, `STIVENPM`; IAM DS-011, `joseale879`. Validar usuario, rol, centro y token real sin ampliar permisos. |
| S2 | Monitoring | Health/readiness reportados 200, pero endpoints de catálogos, alertas y KPI devolvieron 502 desde el MFE. | DS-009/DS-010, `daniel2004-lsd`; contrastar upstream Traefik, servicio, DB y logs de app. |
| S2 | Scheduling | Pantalla de franjas mostró `Unexpected token '<'` al parsear HTML como JSON, indicio de ruta/fallback incorrecto o respuesta no API. | Seguimiento de Scheduling y shell/infra; validar request exacta y destino tras strip-prefix. |
| S2 | Reference Data | Health reportado 200; la UI no pudo cargar catálogos. El usuario reportó que las rutas de catálogo exigen autenticación y no se comprobaron con una sesión válida. | DS-014, `STIVENPM`; probar sesión con permisos esperados y respuesta JSON. |
| S2 | Actors | Alta de instructor devolvió 405. | `Juan282007` (seguimiento Actors en el plan); comparar método HTTP, ruta pública y mapping backend. |
| S2 | Training Environment | La pantalla de tipos/inventario mostró respuesta HTML o JSON inválido; no se confirmó la ruta y método del backend en sesión real. | `Juan282007` (smoke de no-regresión); inspeccionar router, métodos permitidos y tipo de contenido. |
| S2 | Monitoring / OTLP | `POST /otlp/v1/traces` devolvió 405; el log de Audit muestra errores del exporter por dirección de destino ausente. | DS-007 de OTel/infra y propietario del servicio correspondiente; diferenciar rutas HTTP y gRPC, configuración exporter y collector. |
| S2 | Integración de ambientes | Los puertos de QA, staging y main están definidos, pero la documentación consultada no acredita que allí estén desplegadas las APIs. | DevOps debe aportar evidencia de despliegue/probes por ambiente. |
| S3 de gobernanza | Documentación | Hay contradicción heredada: `05-architecture/README.md` describe 9 servicios y solo capa de datos, mientras el catálogo enumera 10 y el mapa de despliegue describe perfiles de aplicación en develop. | Arquitectura; actualizar las vistas generales tras confirmar la fuente técnica de cada afirmación. |
| S3 de gobernanza | Horario DS-001 | Plan Markdown: 11:00; hoja: 14:00 COT. | `Juan282007` resuelve discrepancia con quien mantiene el backlog antes de cerrar el registro. |

No se marca ningún riesgo como resuelto por una respuesta de health. Los 403/502/405/HTML son hallazgos que deben cerrarse con evidencia de request, configuración y logs relevantes.

## Congelamiento propuesto

[ADR-031 — Baseline de rutas y cambios durante la estabilización](../05-architecture/decisions/records/ADR-031-stabilization-routing-baseline.md) propone congelar el contrato de prefijos documentado en este mapa, con excepción de correcciones necesarias para restaurar compatibilidad y seguridad. El ADR permanece **PROPOSED** hasta revisión de Arquitectura; este documento no presume aceptación institucional.

## Fuentes y límites

- [ADR-007 — Edge gateway y convención de puertos](../05-architecture/decisions/records/ADR-007-edge-gateway-and-port-convention.md).
- [ADR-022 — Tabla de rutas del edge por dominio](../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md).
- [Ambientes y puertos](../10-devops/environments.md).
- [Catálogo de servicios](../09-microservices/service-catalog.md) y [mapa de dependencias](../09-microservices/dependency-map.md).
- Hoja de backlog consultada: [BACKLOG_DESIGN_SOFTWARE_5_JORNADAS_30_OCT_AL_03_NOV_2026](https://docs.google.com/spreadsheets/d/1Hv8iMnhRXNlWwGCOanXFMXsqourU0Qs-HcbYZ1q5snY/edit?gid=189681333#gid=189681333), pestaña `BACKLOG_DESIGN_SOFTWARE_5_JORNADAS_30_OCT_AL_03_NOV_2026`, fila DS-001.

Este baseline es una fotografía documental de planificación y evidencia reportada, no una certificación independiente de las 41 ramas/revisiones, la topología viva de la VPS, los permisos de la cuenta sintética ni la disponibilidad funcional de los 10 MFEs.
