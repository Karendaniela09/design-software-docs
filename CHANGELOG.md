# Changelog

## [Unreleased]

### Changed — pdf-renderer-worker (HU-DOC-004)

- `09-microservices/services/07-document-service/components/pdf-renderer-worker/contract.md` y `README.md`: alineados con la implementación. El worker consume `document-generation-queue`, publica `document.document.generated` y `document.version.created` en el topic `document-events`, es idempotente por `correlation_id` y aplica reintentos con backoff y DLQ `pdf-renderer.dlq`. Los eventos internos `document.render.*` del catálogo no se usan en esta implementación
- `events.md` del servicio: envelope estándar del catálogo (`event_id`, `event_type`, `payload`) en lugar del formato CloudEvents, payloads con identificadores UUID y dominios válidos, mensaje de la cola de generación y política de reintentos real
- `data-model.md`: `document_version.correlation_id` e índice único parcial (changeset `hu-doc-004-version-idempotency-974`)
- Pendiente de reconciliación: `document-lifecycle-worker/contract.md` conserva estados (`DRAFT`, `EMITIDO`) que ya no existen

### Fixed — Contrato OpenAPI de document-service (HU-DOC-002 / HU-DOC-003)

- `07-api/contracts/openapi/document.yaml`: restaurado como "Document Service API" (`/documents`, `/documents/generate`, `/documents/{id}`, `/download-url`, `/versions`, `/reports/document-status`). El commit `0ac94c6` lo había sobrescrito con el contenido de la API de plantillas, que sigue en `template.yaml`
- Alineado con la implementación: header `X-Correlation-Id`, `404 TEMPLATE_NOT_FOUND` y `503` en `generate`, `409 DOCUMENT_NOT_AVAILABLE` y `503 STORAGE_UNAVAILABLE` en `download-url`, `sort` permitido en el listado, `mime_type` nullable mientras el documento no tiene archivo, `owner_service` hasta 100 caracteres y acceso por scope (`GLOBAL` / `TRAINING_CENTER`)
- `09-microservices/services/07-document-service`: `data-model.md` (columna `training_center_id`, `storage_key` y `mime_type` nullable, índices), `events.md` (`correlation_id` en el mensaje de `document-generation-queue`) y `components/document-api/contract.md`

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
