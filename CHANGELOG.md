# Changelog

## [Unreleased]

### Changed — Security and event delivery documentation (HU-IAM-010, HU-IAM-018, HU-DOC-002, HU-DOC-008)

- Add IAM issuer/key-rotation and refresh-cookie security notes, including the still-open cross-service audience policy (T-09).
- Document Document outbox/inbox delivery, dispatcher operation, confirmed DLQ replay, and correct renderer idempotency details.
- Link Document event payloads to the companion shared-contracts schema proposal.

### Changed — Scheduling API and emitted-event contracts (HU-SCH-007, HU-SCH-010, HU-INT-SCH-004)

- `07-api/contracts/openapi/scheduling.yaml`: version 1.1.0 reflects the implemented `/health` and `/ready` endpoints.
- `09-microservices/services/05-scheduling-service/events.md`: add `schedule.created` and `schedule.validated`, align published event envelopes/payloads with `ScheduleEvents` and `OutboxRelay`, and correct the retry/DLQ description to current outbox behavior.
- Keep the unimplemented `scheduling.conflict.detected` event explicitly marked pending producer verification.

### Changed — Integración de Reference Data: alcance GLOBAL y entorno reproducible (HU-INT-REF-001)

- `07-api/contracts/openapi/reference-data.yaml`: declara `x-reference-scope: GLOBAL` y la respuesta `503 DEPENDENCY_UNAVAILABLE` (claves JWKS de IAM no disponibles) en las operaciones protegidas, con la respuesta reutilizable `DependencyUnavailable`.
- `09-microservices/services/02-reference-data-service/decisions.md` (DEC-006) y `components/reference-data-api/contract.md`: los seis features `REF_*` se exigen solo con alcance `GLOBAL`; un grant más estrecho responde `403`. Coincide con la matriz de `rbac-design.md` y con los seeds de `iam-db`; sin ADR nuevo.
- `10-devops/reference-data-int-ref-001.md`, `11-quality/reference-data-hu-int-ref-001-validation.md` y `11-quality/qa-handoff-hu-int-ref-001.md`: guía de integración (rutas públicas del edge, base de datos, JWT/JWKS), evidencia de los diez criterios y entrega a QA. El ejecutor reproducible vive en `docker-infra/validation/int-ref-001`.
- Trabajo: HU-INT-REF-001 (docs#294) con docs#426, frontend-platform#11, web-shell#27, reference-data-mfe#16, reference-data-service#29 y docker-infra#55.

### Added — Decisiones y evidencia de document-mfe (HU-DOC-011)

- `09-microservices/services/07-document-service/decisions.md`: filas 06 a 09 con las decisiones internas del front end (estado en hooks sobre puertos de salida, errores con reintento y sin listas vacías falsas, sesión y base `/document/api/v1` por el `httpClient` que inyecta el shell, permisos de la sesión con el backend como autoridad). Sin ADR nuevo: salen de ADR-022 y ADR-023.
- `11-quality/test-evidence-document-mfe-acta-01.md` (y su fila en `11-quality/README.md`): evidencia de pruebas, cobertura, tokens y presupuesto de bundle sobre el head final de document-mfe#9; E2E, accesibilidad, Lighthouse y Pact quedan como pendientes de re-ejecución.

### Changed — Sesión y login del shell (HU-SHELL-010)

- `10-devops/frontend-images.md`: la imagen del shell usa IAM real por defecto (la sesión genérica solo existe en el servidor de desarrollo) y `/login` es del shell; nueva sección "Shell en desarrollo" con el proxy único hacia el edge (`VITE_EDGE_ORIGIN`) y el ciclo de sesión de ADR-023 (access token en memoria, refresh con cookie `HttpOnly`, `httpClient` inyectado a los remotes). Se corrigen dos "Límites conocidos" que ya no son ciertos.

### Changed — Cierre de ficha por aprobación de RAP y contrato de Academic R4 (ADR-030, 2026-10-24)

- `05-architecture/decisions/records/ADR-030-academic-ficha-lifecycle-preconditions.md` (ACCEPTED por el dueño). Fija:
  - una ficha pasa de `PRODUCTIVE_STAGE` a `COMPLETED` solo si cada aprendiz activo tiene aprobado el 100 % de los RAP activos del programa; no hay nota numérica, y una ficha sin aprendices activos no se puede completar (RN-ACAD-07 en `02-domain/entities-and-rules.md`);
  - `EXECUTION` → `PRODUCTIVE_STAGE` no tiene condición de horas ejecutadas; el reporte de ejecución de scheduling queda como evidencia informativa;
  - `DELETE /fichas/{id}` se mantiene como alias de la transición a `CANCELLED` (borrado lógico, mismas validaciones; la justificación `cancellation_notes` va en el cuerpo);
  - el juicio por RAP vive en `actors-service` (`actors_learners.learner_rap_assessment`) y academic consulta la cobertura con un token M2M por audiencia.
- Cambios incompatibles aceptados antes de v1 en `07-api/contracts/openapi/academic-management.yaml` y en `design-software-shared-contracts` (`openapi/academic-management.yaml`):
  - `FichaUpdate` exige `row_version` y ya no lleva `actual_end_date` (que sigue en `FichaStatusChange`);
  - `PATCH /fichas/{id}/status` agrega `cancellation_notes` (obligatoria solo para `CANCELLED`) y la respuesta `503`.
- Contratos nuevos aditivos: `actors.yaml` (`PUT /fichas/{fichaId}/learners/{learnerId}/rap-assessments/{learningOutcomeId}` y `POST /internal/fichas/{fichaId}/rap-assessments/coverage`) e `iam.yaml` (`POST /auth/token` con `audience` opcional; si falta se lee como `actors-service`).
- Datos: `06-actors-service/data-model.md` y `06-data/data-dictionary.md` (tabla `learner_rap_assessment`); RBAC: `ACT_LEARNER_RAP_ASSESSMENT_MANAGE` y `ACT_INTERNAL_FICHA_RAP_COVERAGE` en `rbac-design.md`.
- Trabajo: HU-ACAD-11 (docs#171), HU-ACT-029 (docs#391) y, como seguimiento, HU-ACT-031 (docs#419, juicio del instructor).

### Changed — Catálogos de solo lectura de Monitoring paginados

- `07-api/contracts/openapi/monitoring.yaml` y `09-microservices/services/08-monitoring-service/components/monitoring-api/contract.md`: `GET /risk-levels` y `GET /kpi-statuses` documentan la lista paginada estándar `{ data, pagination }` con `page` y `page_size` (`07-api/guidelines.md` §6), que es lo que `monitoring-service` ya responde. Antes el contrato decía "arreglo plano".
- Efecto en consumidores: ninguno que no esté ya cubierto. `monitoring-mfe` acepta el arreglo y el sobre durante la transición (monitoring-mfe#11). El espejo en `design-software-shared-contracts` (`openapi/monitoring.yaml`) lleva el mismo cambio.

### Added — Correlación de peticiones y métricas Prometheus de iam-service (HU-IAM-021)

- `09-microservices/services/01-iam-service/runbook.md`: observabilidad con `X-Correlation-Id`, `trace_id` en los errores, `GET /actuator/prometheus`, comprobación manual, construcción con el wrapper de Maven y alcance de la verificación. La nota «Métricas: fuera de alcance» deja de aplicar
- `09-microservices/services/01-iam-service/decisions.md`: decisión de correlación y métricas (sin ADR propio)
- `09-microservices/services/01-iam-service/components/iam-api/contract.md`: cabecera transversal `X-Correlation-Id` (cambio aditivo) y endpoint operativo de métricas, que no se enruta por el edge
- La documentación que vivía en `docs/observability/` del repositorio `design-software-iam-service` (PR #43) se traslada aquí; allí solo queda un enlace en el README

### Added — Imágenes del frontend servidas por el edge (HU-SHELL-011)

- `10-devops/frontend-images.md`: cómo se construyen y se sirven las 10 imágenes estáticas del frontend (web-shell y los 9 MFE). Documenta:
  - la imagen nginx en el puerto 8080 que el edge alcanza como `web-shell-static` y `<dominio>-mfe-static`;
  - la base `/mfe/<dominio>/` de cada MFE, solo en `vite build`;
  - el manifest de remotes de mismo origen, idéntico en `qa`, `staging` y `main`, y el de `develop` con los puertos 5101–5109;
  - los contextos de build con nombre (`--build-context`) para los hermanos `design-system` y `frontend-platform`;
  - la verificación local y los límites conocidos (sesión del shell: HU-SHELL-010; servicios de compose: `docker-infra`).
- `10-devops/README.md`: índice actualizado.

### Changed — Refresh token en cookie `HttpOnly` (HU-IAM-018)

- `07-api/contracts/openapi/iam.yaml`, `07-api/authentication.md` y `09-microservices/services/01-iam-service/components/iam-api/contract.md`: concretan ADR-023 §6. **Cambio de contrato incompatible**, decidido por ese ADR:
  - `POST /auth/login` entrega el refresh token solo en `Set-Cookie` (`refresh_token`, `HttpOnly; Secure; SameSite=Strict; Path=/iam/api/v1/auth`) y el cuerpo ya no trae `refresh_token`;
  - `POST /auth/refresh` no tiene cuerpo: lee la cookie y devuelve un access token nuevo. Sin cookie responde 401 `TOKEN_INVALID`;
  - `POST /auth/logout` revoca la sesión y borra la cookie (`Max-Age=0`);
  - el esquema `RefreshRequest` desaparece y `TokenResponse` pierde `refresh_token`.
- `09-microservices/services/01-iam-service/runbook.md`: variable `IAM_REFRESH_COOKIE_PATH` (default `/iam/api/v1/auth`, la ruta pública del edge).
- `08-uml/diagrams/source/login-jwt.md` y `12-ux-ui/mockup-ddd/flows/01-auth.md`: la respuesta de login ya no muestra `refresh_token` en el cuerpo.
- El mismo cambio va en `design-software-shared-contracts` (`openapi/iam.yaml`) y en la copia fijada de `design-software-iam-service`.

### Changed — Revalidación arquitectónica HU-REF-020/R1 (2026-10-24)

- Reconciliado main en la rama del PR #340 conservando los ADR, índices e informes de los otros dominios. Las propuestas de Reference Data antes citadas como ADR-012/013 pasan a ADR-020/021: los números anteriores ya están ocupados en main. Historial y equivalencia documentados; estados PROPOSED sin alterar decisiones ajenas.
- ADR-020: responsabilidades de sesión/cliente/features, custodia de dependencias privadas CI, alcance real de runners y orden de integración propuesto. ADR-021: ownership/permanencia de inbox/proyección/grants, operación de RabbitMQ, replay y retención/reconstrucción sin purgas no aprobadas.
- Evidencia sincronizada por HEAD y enlaces: CI propio Frontend Platform SUCCESS; CI completo shell SUCCESS en e91a2c0, con conflicto posterior que exige revalidar si cambia HEAD; MFE con 71 tests locales y CI propio bloqueado por SHELL_DEPS_TOKEN. DB #81 e IAM DB #80 publicados; PR originales aún abiertos.
- Referencias de HU/modelos/eventos/runbook y matrices alineadas con ADR-020/021. Seis preguntas de gobernanza quedan ABIERTAS, sin imponer aceptación, responsables nominales, plazos de retención ni política de producción.


### Added — HU-REF-020 y R1 de Reference Data (docs-first, 2026-10-20)

- Integración con main: conservar documentación de Monitoring/Document y renumerar los ADR propios a ADR-020/021 (antes ADR-012/013, números ya ocupados en main) para evitar duplicidad con los ADR existentes.

- Evidencia local contra los numerales 6/7/8 del acta: tres capturas saneadas en assets/images (falta la captura del estado con broker caído, pendiente de la autora), métricas de seis eventos/doce reenvíos y fragmentos de salida de pruebas; indexadas desde Calidad y README.

- ADR-020/021 PROPOSED: integración real IAM/web-shell mediante fachada y React Context, inbox transaccional, retry 1/2/4, DLQ y replay.
- Historia/trazabilidad docs#250, modelo/diccionario con changesets nuevos de inbox/proyección y grants mínimos, eventos/runbook y planes de DevOps/Calidad.
- Código adaptado en siete ramas locales desde develop; ejecución propia PASS con IAM real, migraciones, R1 completo y tres escenarios Chromium. QA/Arquitectura y PR/merge originales siguen pendientes por permisos de escritura. No se acredita Done·Dev por las copias personales ni se duplican ADR/informes en repositorios de código.

### Added — Decisiones D1, D2 y D3 de la ruta de cierre

- `05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md` (D3, ACCEPTED). Fija:
  - un solo origen por ambiente, el edge;
  - tres familias de rutas con prioridad: `/<dominio>/api/` al servicio, `/mfe/<dominio>/` a los remotes y el resto al shell;
  - la tabla de los 10 dominios, versionada como proveedor de archivo de Traefik;
  - la base de API relativa en los MFE y el retiro de los proxies por micro del shell;
  - el mismo código, imágenes, tabla y manifest en los 4 ambientes: solo cambian los datos y los valores del ambiente.
  Concreta ADR-007 §4 y ajusta su §1.
- `05-architecture/decisions/records/ADR-023-web-shell-owns-login-and-session.md` (D2, ACCEPTED). Fija:
  - el login y la sesión son del web-shell, con `/login` fuera de `AppShell`;
  - `frontend-platform` como único cliente de sesión;
  - los remotes reciben el cliente HTTP por `remote-props` y no hacen login;
  - el almacenamiento es igual en los 4 ambientes desde `develop`: access token en memoria y refresh token en cookie `HttpOnly`, `Secure`, `SameSite=Strict`. Esto exige que iam-service emita la cookie y saque el `refresh_token` del cuerpo, un cambio de contrato.
- `00-governance/git-conventions.md`, nueva sección "Revisión y aprobación de PR" (D1). Registra:
  - lo que exige el ruleset `protect-parent-branches` y los 9 repos sin ruleset activo;
  - los aprobadores: los arquitectos `Andrey31072` y `Juan282007`, y delivery `MariaOyola`. Bastan 2 aprobaciones, y en los repos con `CODEOWNERS` al menos una tiene que ser de un arquitecto;
  - 2 desarrolladores del dominio como revisión no bloqueante;
  - el bypass del dueño;
  - la verificación de la regla de oro (docs → backlog → código) antes de aprobar.
- Índices de ADR actualizados y nota en ADR-007.

### Changed — ADR-001 aceptado (RabbitMQ como broker de mensajes)

- `05-architecture/decisions/records/ADR-001-message-broker.md`: pasa de PROPOSED a ACCEPTED (2026-10-24), aprobado por el dueño del proyecto. Motivos: 9 de 10 servicios ya usan RabbitMQ, la infraestructura solo tiene RabbitMQ y el volumen de eventos es bajo. Se actualiza el registro en `05-architecture/decisions/README.md`.

### Changed — Tabla de rutas del edge y perfiles de dominio (HU-SHELL-009)

- `10-devops/local-setup.md`: sección "Edge: tabla de rutas por dominio" (las tres familias con su prioridad, los 10 dominios con su servicio y puerto, qué cambia respecto del enrutado por labels, los servicios del frontend que define el perfil `edge`, qué da por supuesto de HU-ACT-020, cómo verificar con `scripts/edge-smoke.sh` y cómo agregar un dominio); perfiles `academic`, `reference` y `training` con sus dependencias (HU-ACAD-019, HU-REF-031, HU-ENV-020); tabla de perfiles completada con `actors`, `scheduling`, `document`, `audit` y `monitoring`; el perfil `edge` pasa a traer `traefik`, `web-shell-static` y los 9 `<dominio>-mfe-static` (variable `FRONTEND_REPOS_DIR`); el gotcha del socket de Docker Desktop queda resuelto por el proveedor de archivo.
- `10-devops/environments.md`: "Estado real" de `develop` actualizado (10 dominios detrás del edge con una sola tabla de archivo, igual en los 4 ambientes) y enlace a la sección nueva.
- `10-devops/frontend-images.md`: la sección de compose ya no dice que los servicios `*-static` faltan en `docker-infra`; remite a `docker-compose.yml` (perfil `edge`).

### Added — CI del repo docs (HU-SHELL-013)

- `.github/workflows/docs-ci.yml`: workflow que corre en cada PR hacia `main` y valida solo lo que cambia el PR: (1) título del PR con Conventional Commits (`docs|fix|chore|refactor`), (2) enlaces relativos de los `.md` agregados o modificados, (3) unicidad de número de ADR, incluido el choque con ADR de otros PR abiertos (caso ADR-020), (4) números de documento de identidad en las líneas agregadas (el número se enmascara en el reporte) y (5) lint OpenAPI de `07-api/contracts/openapi/*.yaml` con `redocly.yaml`, que falla solo por errores nuevos. No usa secretos
- `scripts/ci/`: scripts Python (biblioteca estándar) que ejecuta el workflow y que se pueden correr en local; incluye `README.md`. Es una carpeta raíz nueva autorizada por la HU
- `10-devops/ci-cd.md`: controles de Conventional Commits (título del PR) y validación de documentación marcados como implementados, con una fila por control nuevo. Siguen sin ser obligatorios: marcar el check como requerido en el ruleset lo decide el dueño (D7)

### Fixed — Lecciones del golden template Python (monitoring-service#1, HU-MON-F1)

- `05-architecture/decisions/records/ADR-006-polyglot-stack-strategy.md` (rev. 3): el árbol Python usa `inbound/` y `outbound/` en lugar de `in/` y `out/`, porque `in` es palabra reservada de Python (`SyntaxError` al importar). Es una corrección de nombres de directorio; no cambia la decisión ni se crea un ADR.
- `10-devops/local-setup.md`, `04-requirements/non-functional.md` (NFR-OBS-06), `11-quality/code-review.md` y el runbook de monitoring: en Python el protocolo OTLP lo decide el exportador que se importa (`grpc` → `:4317`, `http` → `:4318` con `/v1/<señal>`); `monitoring` usa `http/protobuf` en `:4318`.

### Changed — pdf-renderer-worker (HU-DOC-004)

- `09-microservices/services/07-document-service/components/pdf-renderer-worker/contract.md` y `README.md`: alineados con la implementación. El worker consume `document-generation-queue`, publica `document.document.generated` y `document.version.created` en el topic `document-events`, es idempotente por `correlation_id` y aplica reintentos con backoff y DLQ `pdf-renderer.dlq`. Los eventos internos `document.render.*` del catálogo no se usan en esta implementación
- `events.md` del servicio: envelope estándar del catálogo (`event_id`, `event_type`, `payload`) en lugar del formato CloudEvents, payloads con identificadores UUID y dominios válidos, mensaje de la cola de generación y política de reintentos real
- `data-model.md`: `document_version.correlation_id` e índice único parcial (changeset `hu-doc-004-version-idempotency-974`)
- Pendiente de reconciliación: `document-lifecycle-worker/contract.md` conserva estados (`DRAFT`, `EMITIDO`) que ya no existen

### Changed — Contrato de sesiones de IAM (R4)

- `07-api/contracts/openapi/iam.yaml`, `09-microservices/services/01-iam-service/components/iam-api/contract.md` y `rbac-design.md`: alineados con la regla implementada y probada en iam-service#44. Consultar y revocar sesiones propias no exige ningún feature RBAC. Las sesiones ajenas solo las gestiona un administrador global (`SYSTEM_ADMIN` sin centro de formación): `IDENTITY_USER_VIEW` efectivo para consultar e `IDENTITY_USER_MANAGE` efectivo para revocar. Cambio solo de texto: no cambian rutas, parámetros, esquemas ni códigos de respuesta
- `x-required-feature` se retira de `GET` y `DELETE /users/{id}/sessions…` porque el requisito ya no es uniforme; la regla condicional queda en la `description` de cada operación
- `12-ux-ui/mockup-ddd/flows/05-administrador.md`: feature de la revocación de sesión actualizado
- `09-microservices/services/01-iam-service/decisions.md`: DEC-009 registra la regla (sin ADR propio; ADR-018 cubre la validación del estado de sesión, no este reparto)
- Pendiente: `shared-contracts` y la copia fijada de `iam-service` conservan el texto anterior hasta su siguiente sincronización

### Fixed — Contrato OpenAPI de document-service (HU-DOC-002 / HU-DOC-003)

- `07-api/contracts/openapi/document.yaml`: restaurado como "Document Service API" (`/documents`, `/documents/generate`, `/documents/{id}`, `/download-url`, `/versions`, `/reports/document-status`). El commit `0ac94c6` lo había sobrescrito con el contenido de la API de plantillas, que sigue en `template.yaml`
- Alineado con la implementación: header `X-Correlation-Id`, `404 TEMPLATE_NOT_FOUND` y `503` en `generate`, `409 DOCUMENT_NOT_AVAILABLE` y `503 STORAGE_UNAVAILABLE` en `download-url`, `sort` permitido en el listado, `mime_type` nullable mientras el documento no tiene archivo, `owner_service` hasta 100 caracteres y acceso por scope (`GLOBAL` / `TRAINING_CENTER`)
- `09-microservices/services/07-document-service`: `data-model.md` (columna `training_center_id`, `storage_key` y `mime_type` nullable, índices), `events.md` (`correlation_id` en el mensaje de `document-generation-queue`) y `components/document-api/contract.md`

### Added — Imagen del alert-worker de monitoring (HU-INT-MON-004)

- `09-microservices/services/08-monitoring-service/runbook.md`: sección "Imágenes de contenedor" con el Dockerfile de cada deployable (`deploy/Dockerfile.api`, `deploy/Dockerfile.worker`), el proceso que ejecuta cada uno, los modos `consumer` y `relay` del worker y la base común (`python:3.11-slim` con `requirements-runtime.lock`).

### Added — Rendimiento de Scheduling para R2

- `05-architecture/decisions/records/ADR-027-scheduling-r2-performance.md` (PROPOSED): decisión de conservar los dos índices parciales de lectura, la compresión JSON y `open-in-view=false`, con la evidencia resumida.
- `11-quality/qa-report-r2-scheduling-service.md`: resultados k6, ranking SQL, planes antes/después a escala pequeña y a escala realista (480 120 sesiones), rollback y SHA-256 de las salidas originales retiradas del repositorio.
- `09-microservices/services/05-scheduling-service/data-model.md`: los dos índices R2 en «Índices relevantes».

### Added — Estándar transversal de estados parametrizables y auditoría (ADR-004)

**Estándar autoritativo:**
- `06-data/modeling-conventions.md`: fuente única de las convenciones transversales. Define (1) los tres conceptos de estado separados — ciclo de vida del registro / estado de negocio parametrizable / enum técnico cerrado; (2) el patrón genérico `status_category` + `status` + `status_transition` por servicio; (3) el estándar de auditoría completo; (4) el mapeo de qué migra al catálogo vs qué queda como CHECK; (5) seeds por servicio
- `05-architecture/decisions/records/ADR-004-status-parametrization-and-audit-standard.md`: ratifica las 3 decisiones (patrón por servicio, solo estados de negocio, auditoría completa con soft delete)

**Entidad padre parametrizable de estados:**
- `status_category` (parametriza cualquier tipo de estado del servicio) + `status` (valores con is_initial/is_terminal/orden/color) + `status_transition` (transiciones gobernadas ligadas a features de RBAC). Patrón replicado por bounded context (DB-por-servicio)

**Estándar de auditoría completo (resuelve brecha de `_by` y soft delete):**
- Toda tabla transaccional: `created_at`/`created_by`, `updated_at`/`updated_by`, `deleted_at`/`deleted_by` (soft delete), `is_active`, `row_version`
- Actor de sistema reservado `SYSTEM_ACTOR_ID = 00000000-0000-0000-0000-000000000000` para acciones automáticas
- Append-only (`audit_record`, `audit_login`, `activity_log`): solo timestamp de inserción

**Separación ciclo de vida del registro vs estado de negocio:**
- `is_active` + `deleted_at` = estado técnico del registro (habilitado/deshabilitado/eliminado)
- `status_id` → catálogo = estado de negocio (DRAFT/PUBLISHED…), ejes ortogonales

### Changed
- Bloque "Convenciones de modelado (transversales)" actualizado en los 9 `services/*/data-model.md`: incorpora el estándar de estados y auditoría + puntero a `modeling-conventions.md`
- `06-data/models.md`: nueva sección "Estándar transversal" con entidades `Status_Category`/`Status`/`Status_Transition` y columnas de auditoría
- `05-architecture/overview.md` y `decisions/README.md`: ADR-004 añadido al índice

---

### Added — Cierre de brechas: threat model, ADRs, dominio y contexto

**Seguridad (A04 / A12):**
- `05-architecture/security-threat-model.md`: modelo STRIDE completo con clasificación de activos, superficie de ataque, 26 amenazas por categoría (S/T/R/I/D/E) con controles, mapeo OWASP Top 10 2021, cumplimiento Ley 1581/2012 y acciones pendientes priorizadas

**Decisiones de arquitectura (A06):**
- `05-architecture/decisions/records/ADR-001-message-broker.md`: selección de RabbitMQ con análisis de Kafka/SQS/Redis Streams descartados
- `05-architecture/decisions/records/ADR-002-scheduling-read-models.md`: read models por eventos para bajar scheduling de 3 a 1 dependencia síncrona; verificación síncrona puntual pre-publicación
- `05-architecture/decisions/records/ADR-003-object-storage.md`: MinIO (DEV/QA) + S3 (PROD) tras adaptador único compatible S3
- `05-architecture/decisions/README.md`: tabla de registro de ADRs poblada
- `05-architecture/overview.md`: índice de ADRs enlazado a los archivos reales

**Dominio (A06 / A05):**
- `02-domain/domain-map.md`: context map DDD con clasificación CORE/SUPPORTING/GENERIC, patrones de relación (OHS, CS, Conformist, ACL, Published Language), Anti-Corruption Layers y mapeo de lenguaje ubicuo
- `02-domain/domain-events.md`: vista de negocio de los 28 eventos (qué los dispara, qué estado cambian), flujo del caso de uso central y garantías de entrega

**Requisitos (A05 / A04):**
- `04-requirements/non-functional.md`: 9 categorías de NFR (rendimiento, disponibilidad, escalabilidad, seguridad, mantenibilidad, observabilidad, usabilidad, portabilidad, recuperación) con métricas verificables y trazabilidad NFR→arquitectura

**Contexto (entendimiento fundacional):**
- `01-context/overview.md`: contexto institucional SENA, programa ADSO, problema, objetivos y referencias normativas
- `01-context/scope.md`: alcance MVP, fuera de alcance, supuestos y restricciones técnicas/normativas/operativas
- `01-context/glossary.md`: glosario completo dominio↔técnico (términos SENA, técnicos y estados clave)

### Fixed — HALT-DB-NAMING en eventos (contratos de integración)
- `09-microservices/event-catalog.md`: topics de español a inglés (`iam.usuario.created`→`iam.user.created`, `scheduling.sesion_clase.created`→`scheduling.class_session.created`, etc.)
- `09-microservices/services/09-audit-service/components/audit-worker/contract.md`: `registro_auditoria`→`audit_record`, `usuario_id`→`user_id`

---

### Added — Pantallas pendientes de actors-mfe en el inventario de UX

- `12-ux-ui/mockup-ddd/screen-inventory.md`: sección "Pantallas pendientes de diseñar" con cuatro pantallas de `actors-mfe` que ya tienen HU `[FRONTEND]` en el tablero (HU-ACT-025 a HU-ACT-028) y backend terminado, pero no tienen mockup. No cuentan en el total de 53.

### Added — Profundización de seguridad, reglas de negocio y prerequisitos de fases

**RBAC completo en `iam-service`:**
- `01-iam-service/rbac-design.md`: diseño completo de roles (7 roles SENA), módulos (10), features (~50), scopes (7 tipos) y matriz de permisos completa. Reemplaza el modelo plano `resource+action`
- `01-iam-service/data-model.md`: expandido con `Module`, `Feature`, `RoleFeature`, `UserRole`, `UserScopeOverride`, `RefreshToken`, `PasswordResetRequest`, `AuditLogin`. Incluye marcación PII y políticas de retención
- `01-iam-service/decisions.md`: 8 decisiones documentadas (RBAC por feature, JWT pre-calculado, audit_login en iam_db, etc.)
- `01-iam-service/components/iam-api/contract.md`: API completa con endpoints de sesiones, overrides de scope, módulos/features y todos los códigos de error
- `01-iam-service/README.md`: entidades actualizadas con el modelo RBAC expandido

**Artefactos de fases previas (prerequisitos del ecosistema):**
- `03-product/discovery-brief.md`: hallazgos por dominio M1-M9, KPIs base, restricciones técnicas y preguntas abiertas
- `03-product/problem-framing.md`: definición del problema, análisis 5 Whys, mapa de impacto, criterios de éxito funcionales y no funcionales
- `05-architecture/pattern-guide.md`: patrón DDD + Hexagonal por microservicio, estructura de capas, reglas de dependencia, SOLID, checklist de PR
- `05-architecture/overview.md`: arquitectura C4 nivel 2 de los 9 servicios, flujos principales, contratos, NFRs, ADR index
- `06-data/models.md`: modelo lógico global (A10) con todas las entidades de los 9 bounded contexts, PII marking, retención, patrones de acceso y referencias cruzadas

**Actores — entidades del M7 que faltaban:**
- `06-actors-service/data-model.md`: agregadas `InstructorAvailabilityException` (bloqueos no-recurrentes), `ActorImprovementPlan` (plan individual separado del plan de ficha), `ActivityLog` (bitácora append-only), `CompanyVisit` con campo de evaluación de desempeño, campos PII marcados

**Monitoring — catálogos configurables (M9):**
- `08-monitoring-service/data-model.md`: agregadas `AlertType` (configurable en runtime, con 6 alertas pre-configuradas según normativa SENA) y `RiskLevel` (5 niveles con colores para UI). Expandida `GeneratedAlert` con `triggered_value`, `threshold_value` y campos de resolución. `ImprovementPlan` con `title`, `specific_actions` y `completion_notes`

**Reglas de negocio del dominio:**
- `02-domain/entities-and-rules.md`: 34 reglas de negocio organizadas por módulo (M1-M9), basadas en Acuerdo 00003/2012, Decreto 249/2004, Circular 1-2014 SENA. Incluye tablas de transiciones de estado, umbrales de alerta y restricciones regulatorias

**Estrategia de autenticación:**
- `07-api/authentication.md`: estructura completa del JWT con claims de features pre-calculados, flujo de autenticación, algoritmo de verificación por servicio, tabla de aplicación de scope en queries, configuración de seguridad RS256, errores estándar y roadmap de seguridad

**Matrices y catálogos actualizados:**
- `09-microservices/data-ownership-matrix.md`: entidades expandidas (64 total) incluyendo nuevas entidades de IAM, actors y monitoring

### Fixed — Naming HALT-DB-NAMING en todos los data-model.md
- `services/01-iam-service/data-model.md`: `usuario→user`, `rol→role`, `permiso→permission`
- `services/02-reference-data-service/data-model.md`: `departamento→department`, `centro_formacion→training_center`, `catalogo→catalog`
- `services/03-academic-management-service/data-model.md`: `programa_formacion→training_program`, `ficha_caracterizacion→enrollment_ficha`
- `services/04-training-environment-service/data-model.md`: `ambiente→environment`, `disponibilidad_ambiente→availability_rule`
- `services/05-scheduling-service/data-model.md`: `horario→schedule`, `sesion_clase→class_session`, `conflicto_detectado→scheduling_conflict`
- `services/06-actors-service/data-model.md`: `instructor→Instructor`, `aprendiz→learner`, `etapa_productiva→productive_stage`
- `services/07-document-service/data-model.md`: `documento→document`, `plantilla_documento→document_template`
- `services/08-monitoring-service/data-model.md`: `seguimiento_kpi→kpi_tracking`, `alerta_generada→generated_alert`
- `services/09-audit-service/data-model.md`: `registro_auditoria→audit_record`, `entidad_tipo→entity_type`

---

### Added — 09-microservices: estructura completa de 9 microservicios

**Plantillas reestructuradas (`_template/`):**
- `_template/service/README.md`: plantilla de bounded context con entidades, dependencias y componentes
- `_template/service/data-model.md`: plantilla de modelo de datos con referencias externas e índices
- `_template/service/events.md`: plantilla de eventos publicados/consumidos con envelope estándar
- `_template/service/runbook.md`: plantilla de runbook con healthcheck, alertas y escalamiento
- `_template/service/decisions.md`: plantilla de decisiones internas del bounded context
- `_template/component/README.md`: plantilla de componente con tipo, responsabilidad y variables de entorno
- `_template/component/contract.md`: plantilla de contrato para -api, -worker y -workflow

**Archivos deprecados (`_template/` raíz):** `api-contract.md`, `data-model.md`, `events.md`, `runbook.md` → marcados ⚫ Deprecado

**Nuevos archivos raíz en `09-microservices/`:**
- `dependency-map.md`: mapa de dependencias síncronas y asíncronas; regla de máximo 2 deps síncronas por servicio
- `data-ownership-matrix.md`: propietario único de cada entidad de dominio (52 entidades mapeadas)
- `event-catalog.md`: catálogo centralizado de eventos por publicador (28 eventos documentados)
- `service-boundary-rules.md`: 15 reglas de frontera de servicios y antipatrones a evitar
- `service-readiness-checklist.md`: criterios de madurez en 4 niveles (doc → dev → qa → prod)
- `storage-and-documents.md`: estrategia de almacenamiento por servicio; object storage y caché

**9 microservicios creados en `services/`:**
- `01-iam-service/`: M1 — 5 archivos + `components/iam-api/` (README + contract)
- `02-reference-data-service/`: M2+M4 — 5 archivos + `components/reference-data-api/`
- `03-academic-management-service/`: M5+M6 — 5 archivos + `components/academic-management-api/`
- `04-training-environment-service/`: M3 — 5 archivos + `components/training-environment-api/`
- `05-scheduling-service/`: M8 — 5 archivos + `components/` (schedules-api, scheduling-engine-workflow, conflict-validator-worker)
- `06-actors-service/`: M7 — 5 archivos + `components/actors-api/`
- `07-document-service/`: transversal — 6 archivos (incl. storage-adapters.md) + `components/` (document-api, template-api, pdf-renderer-worker, document-lifecycle-worker)
- `08-monitoring-service/`: M9 — 5 archivos + `components/` (monitoring-api, alert-worker, notification-worker)
- `09-audit-service/`: transversal — 5 archivos + `components/audit-worker/`

**Total archivos creados en esta sesión: 87**

### Updated
- `09-microservices/README.md`: tabla completa con 9 servicios, 8 archivos raíz y referencias a plantillas
- `09-microservices/service-catalog.md`: 9 servicios con módulo de origen, owner y estado

---

### Added — Templates de documentación (28 plantillas compatibles con ecosistema agentico)

**01-context/**
- `_template-project-profile.md`: perfil del proyecto con dimensiones de complejidad, microservicios y trackers
- `_template-scope-declaration.md`: declaración de alcance con MVP, roles, supuestos y criterios de éxito

**03-product/**
- `_template-discovery-brief.md`: discovery brief con problema, resultado esperado y hallazgos
- `_template-problem-framing.md`: problem framing con definición del problema, 5 Whys y criterios de éxito
- `_template-prd.md`: PRD con épicas EPC-NNN, features FEA-NNN, HUs, ACs y NFRs
- `_template-backlog.md`: backlog priorizado con MoSCoW, mapa de dependencias y resumen por release

**04-requirements/**
- `_template-nfr.md`: requisitos no funcionales (rendimiento, disponibilidad, seguridad, mantenibilidad, observabilidad)

**05-architecture/**
- `_template-architecture.md`: arquitectura con componentes, flujos, contratos, NFRs y decisiones
- `_template-pattern-guide.md`: guía de patrones con capas, reglas de dependencia y bounded contexts
- `_template-security-threat-model.md`: modelo de amenazas STRIDE con controles y datos PII

**06-data/**
- `_template-data-model.md`: modelo de datos con entidades DDD, relaciones, patrones de acceso y privacidad
- `_template-db-design.md`: diseño físico de BD con esquema, índices, FKs, migraciones y RTO/RPO
- `_template-data-migration-plan.md`: plan de migración con mapeo, pasos, validaciones y rollback

**07-api/**
- `_template-api-contract.md`: contrato REST con autenticación, endpoints CRUD, rate limiting y versionado

**10-devops/**
- `_template-deployment-plan.md`: plan de despliegue con componentes, pasos, verificación y rollback
- `_template-release-checklist.md`: checklist de release con gates de código, QA, seguridad e infraestructura
- `_template-rollback-plan.md`: plan de rollback con criterios de activación y procedimientos por componente

**11-quality/**
- `_template-qa-report.md`: reporte de QA con cobertura, defectos, HUs y gate de calidad
- `_template-test-evidence.md`: evidencia de pruebas con casos TC-NNN y trazabilidad AC-HU-TC

**12-ux-ui/**
- `_template-ux-flows.md`: flujos UX con actores, happy path, caminos de error y diagramas
- `_template-ui-spec.md`: spec de UI con pantallas, componentes, estados y accesibilidad
- `_template-design-system.md`: design system con paleta, tipografía, espaciado y componentes

**13-operations/**
- `_template-runbook.md`: runbook operativo con alertas, diagnóstico, procedimientos y escalamiento
- `_template-observability.md`: observabilidad con logs estructurados, métricas RED/USE, trazas y alertas
- `_template-sla-slo-sli.md`: SLA/SLO/SLI con objetivos por servicio, error budget y políticas
- `_template-incident-postmortem.md`: postmortem con línea de tiempo, causa raíz, impacto y acciones

**15-project-control/**
- `_template-risk-register.md`: registro de riesgos con categorías, bloqueantes, resueltos y aceptados
- `_template-sprint-plan.md`: plan de sprint con HUs comprometidas, trazabilidad QA y DoD

### Fixed
- `README.md`: agregado enlace a `agile-conventions.md` en la sección de documentos de gobierno

### Added — Naming y convenciones
- `00-governance/agile-conventions.md`: naming de épicas, iteraciones y HUs; estatus fijos; integración con trackers externos
- `04-requirements/_template-hu.md`: plantilla estándar para documentar historias de usuario
- `00-governance/microservices-documentation.md`: sección de naming con patrón `<proyecto>-<contexto>-<sufijo>` y tabla de sufijos estándar
- `.github/CODEOWNERS`: regla catch-all `*` para archivos sin owner específico
- `00-governance/git-conventions.md`: sección de hotfix en main con flujo y cherry-pick a qa/dev
- `00-governance/security-rules.md`: sección de contacto de seguridad con placeholder de handles
- `.github/pull_request_template.md`: sección de rama destino (dev / qa / main) al inicio del template

### Fixed
- `00-governance/documentation-rules.md`: estado ⚫ Deprecado ahora tiene criterio de decisión por tabla (sustituido / reestructurado / ADR)
- `00-governance/definition-of-ready.md`: criterio "alcance mínimo acordado" reemplazado por criterio verificable (secciones Contexto y Contenido con texto real)
- `00-governance/definition-of-done.md`: criterio "afecta a varios equipos" reemplazado por condición concreta (gobernanza, estructura, contratos compartidos)
- `00-governance/microservices-documentation.md`: agregado requisito de ADR o decisión registrada antes de crear carpeta de servicio nuevo
- `06-data/README.md`: agregada nota de diferenciación con modelos transaccionales en `09-microservices/`

### Added (sesión anterior)
- `.github/CODEOWNERS`: ownership de revisión por sección del repositorio
- `05-architecture/decisions/_template-adr.md`: template standalone para crear ADRs
- `15-project-control/open-questions.md`: flujo de registro y resolución de preguntas abiertas
- `00-governance/git-conventions.md`: reglas de ramas, ambientes, releases y commits
- `00-governance/microservices-documentation.md`: flujo para documentar microservicios reales
- `00-governance/security-rules.md`: reglas contra fugas de información sensible

### Fixed
- `05-architecture/decisions/README.md`: aclarada política de ADRs deprecadas (permanecen en `records/`, no se mueven)
- `CONTRIBUTING.md`: corregida instrucción contradictoria sobre mover ADRs a `99-archive/`
- `.github/pull_request_template.md`: añadidos criterios de Definition of Ready y Done al checklist
- `09-microservices/_template/README.md`: identificado claramente como plantilla (no documento pendiente)

### Improved
- `07-api/README.md`: añadida regla de contrato canónico vs contrato de implementación
- `00-governance/documentation-rules.md`: añadida tabla de dónde van recursos visuales (`assets/` vs `08-uml/`)
- `02-domain/README.md`: añadida nota de diferenciación con `06-data/`
- `06-data/README.md`: añadida nota de diferenciación con `02-domain/`
- `14-training/README.md`: añadida tabla de audiencias y orientación para equipo de soporte
- `README.md`: añadidos CHANGELOG y CODEOWNERS a documentos de gobierno
- `CONTRIBUTING.md`: reducido a hub operativo con enlaces a reglas especializadas
- `00-governance/documentation-rules.md`: enfocado en reglas documentales, índices y diagramas

### Changed — Modelo de datos de actors: excepción de disponibilidad y outbox

- `09-microservices/services/06-actors-service/data-model.md`: `instructor_availability_exception` documenta las columnas del changeset 970 (`status`, `support_document_id`, `reviewed_by`, `reviewed_at`, `decision_reason`) y la migración R6 del estado al catálogo (`status_id`; expand, backfill y contract; HU-ACT-023). La sección `company_visit_outbox` pasa a ser el **único outbox** de actors, con las columnas de estado de entrega de HU-ACT-022 (changeset `hu-act-022-outbox-delivery-state-960`); se descarta la tabla paralela `outbox_event` que proponía `design-software-actors-db#66`.
- `09-microservices/services/06-actors-service/decisions.md`: fila 10 con la decisión de un solo outbox por servicio (columnas aditivas sobre `company_visit_outbox`, un solo despachador por RabbitMQ), fila 11 con la regla de que el contract va en un changelog aparte y fila 13 con las decisiones de observabilidad de HU-ACT-024 (antes una nota de diseño local en `design-software-actors-service#34`); fila 12 con la decisión de HU-ACT-028: el plan de mejoramiento individual (`actors-mfe`) y el de ficha (`monitoring-mfe`) son dos conceptos, y el edge los distingue por el prefijo de dominio de ADR-022.
- `09-microservices/services/06-actors-service/{events,README,runbook}.md` y `10-devops/runtime-configuration-map.md`: actors publica por **RabbitMQ** (exchange `actors-events`, ADR-001; HU-ACT-021) y no por Kafka. `events.md` documenta `actors.instructor.availability_changed`, la política de entrega del outbox (al menos una vez, back-off de 1/4/16/64 s, estado `DEAD`, reproducción) y la deuda de alineación del payload; el runbook reemplaza las variables y comandos de Kafka por los de RabbitMQ y agrega el procedimiento de eventos pendientes o muertos; la configuración pasa de `KAFKA_BOOTSTRAP_SERVERS` a `SPRING_RABBITMQ_*`, `ACTORS_OUTBOX_ENABLED` y `ACTORS_EVENTS_EXCHANGE` (mismo nombre en los 4 ambientes).

### Changed — Runbook de observabilidad de actors y servicio del contract R6

- `09-microservices/services/06-actors-service/runbook.md`: alerta `ActorsHighErrorRate` y procedimiento «Tasa de error alta en actors-service» (puerto de gestión 8081, tablero `actors-r3`, trazas, logs JSON por `correlation_id`). Cierra el DoR de runbook de HU-ACT-024.
- `09-microservices/services/06-actors-service/data-model.md`: el contrato R6 se ejecuta con el servicio `liquibase-actors-contract` de `docker-infra`.

---

## [Estructura inicial]

### Added
- Estructura inicial del repositorio de documentación

## 2026-10-20 — Centralización documental R3

Se trasladan desde Monitoring, Actors y Scheduling las guías R3, junto con las adiciones documentales de Notification y los informes públicos de entrega que estaban en el workspace. Se registra ADR-010. Las evidencias de ejecución quedan únicamente en la carpeta raíz local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`; la guía de práctica personal permanece privada.

## 2026-10-20 — Correcciones QA de R3

Se corrige la referencia canónica de ADR-010, se documentan los repositorios compartidos y sus montajes frontend con commits reproducibles, y se elimina la matriz duplicada del informe. La matriz distingue las últimas evidencias por criterio de un arranque aún pendiente desde ramas fusionadas; conserva PARCIAL en HU externas y práctica personal. Se registran números, estados, heads y checks reales de los PR. La rama documental pasa a `fix/r3-observability`.

## 2026-10-20 — Informe técnico breve de entrega R3

Se añade el informe breve con enlace a ADR-010 y una selección de capturas originales, métricas, logs y salidas de pruebas verificadas por SHA-256. Los originales completos permanecen en la carpeta raíz de evidencias. Se corrige el SHA del corte documental anterior señalado por QA, sin declarar nuevas pruebas ni fusiones.
