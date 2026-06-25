# Changelog

## [Unreleased]

### Added
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

### Added (Fecha: 2026-06-24)

#### Documentación de todas las secciones del repositorio

**00-governance/** — Gobernanza y reglas del repositorio
- `README.md`: Índice de gobernanza
- `documentation-rules.md`: Reglas de documentación (naming, estructura, estados, diagramas)
- `git-conventions.md`: Convenciones de Git (ramas, commits, flujos)
- `microservices-documentation.md`: Reglas para documentar microservicios
- `security-rules.md`: Reglas de seguridad documental
- `definition-of-ready.md`: Criterios de ready para documentos
- `definition-of-done.md`: Criterios de done para documentos

**01-context/** — Contexto del proyecto
- `README.md`: Índice de contexto
- `overview.md`: Descripción general del proyecto
- `scope.md`: Alcance funcional y no funcional
- `glossary.md`: Glosario de términos del SENA y del sistema

**02-domain/** — Modelo de dominio
- `README.md`: Índice de dominio
- `domain-map.md`: Mapa de dominios y bounded contexts
- `entities-and-rules.md`: Entidades y reglas de negocio por módulo
- `domain-events.md`: Eventos de dominio

**03-product/** — Producto
- `README.md`: Índice de producto
- `vision.md`: Visión del producto, objetivos y propuesta de valor
- `roadmap.md`: Hitos, fases y evolución planificada
- `product-backlog.md`: Backlog priorizado de producto (25 HUs)

**04-requirements/** — Requisitos
- `README.md`: Índice de requisitos
- `functional.md`: 64 requisitos funcionales (RF-001 a RF-064)
- `non-functional.md`: 42 requisitos no funcionales (RNF-001 a RNF-042)
- `user-stories.md`: 40 historias de usuario (HU-001 a HU-040)
- `traceability-matrix.md`: Matriz de trazabilidad (90.6% cubierto)

**05-architecture/** — Arquitectura
- `README.md`: Índice de arquitectura
- `overview.md`: Visión general, principios, componentes, tecnologías
- `deployment.md`: Ambientes, Docker Compose, CI/CD, healthchecks, rollback
- `cross-cutting.md`: Seguridad, logging, auditoría, errores, validación, monitoreo
- `decisions/README.md`: Índice de ADRs
- `decisions/_template-adr.md`: Plantilla para ADRs
- `decisions/records/ADR-001-*.md`: Clean Architecture
- `decisions/records/ADR-002-*.md`: JWT + Spring Security
- `decisions/records/ADR-003-*.md`: Validación de conflictos en tiempo real
- `decisions/records/ADR-004-*.md`: Auditoría append-only
- `decisions/records/ADR-005-*.md`: Microservicios con base de datos por servicio
- `decisions/records/ADR-006-*.md`: Notificaciones por email asíncronas
- `decisions/records/ADR-007-*.md`: Generación de reportes asíncrona

**06-data/** — Datos
- `README.md`: Índice de datos
- `models.md`: Modelos conceptual, lógico y físico por esquema
- `data-dictionary.md`: Diccionario detallado de todas las tablas y campos
- `migration-strategy.md`: Estrategia con Flyway, ejemplos y buenas prácticas

**07-api/** — API
- `README.md`: Índice de API
- `guidelines.md`: Normas de diseño API
- `authentication.md`: Estrategia JWT + Spring Security
- `contracts/openapi/scheduling-service.yaml`: Contrato OpenAPI para Scheduling Service
- `contracts/openapi/README.md`: Índice de contratos

**08-uml/** — UML
- `README.md`: Índice de UML
- `diagram-index.md`: Índice de diagramas
- `diagrams/source/README.md`: Guía de fuentes editables
- `diagrams/exports/README.md`: Guía de exportaciones

**09-microservices/** — Microservicios
- `README.md`: Índice de microservicios
- `service-catalog.md`: Catálogo de 9 servicios
- `communication-patterns.md`: Patrones síncronos/asíncronos y resiliencia
- `_template/README.md`: Plantilla de servicio
- `_template/api-contract.md`: Plantilla de contrato API
- `_template/data-model.md`: Plantilla de modelo de datos
- `_template/events.md`: Plantilla de eventos
- `_template/runbook.md`: Plantilla de runbook
- `services/`: Carpeta para servicios reales (pendiente)

**10-devops/** — DevOps
- `README.md`: Índice de DevOps
- `local-setup.md`: Configuración del entorno local con Docker Compose
- `ci-cd.md`: Pipeline de CI/CD con GitHub Actions
- `environments.md`: Descripción de los 4 ambientes (dev, QA, staging, producción)

**11-quality/** — Calidad
- `README.md`: Índice de calidad
- `testing-strategy.md`: Estrategia de pruebas (unitaria, integración, aceptación)
- `code-review.md`: Flujo de revisión de código y checklist

**12-ux-ui/** — UX/UI
- `README.md`: Índice de UX/UI
- `design-system.md`: Sistema de diseño (colores, tipografía, componentes, espaciado)
- `navigation-map.md`: Mapa de navegación por rol
- `wireframes.md`: Wireframes de pantallas principales

**13-operations/** — Operaciones
- `README.md`: Índice de operaciones
- `observability.md`: Logs, métricas, alertas
- `incident-management.md`: Clasificación y respuesta de incidentes
- `backup-and-recovery.md`: Estrategia de backup y recuperación (RPO/RTO)

**14-training/** — Entrenamiento
- `README.md`: Índice de entrenamiento
- `user-manual.md`: Manual para coordinadores, instructores y aprendices
- `admin-manual.md`: Manual para administradores del sistema
- `technical-onboarding.md`: Guía de onboarding para nuevos desarrolladores

**15-project-control/** — Control de proyecto
- `README.md`: Índice de control de proyecto
- `technical-backlog.md`: Lista de tareas técnicas pendientes
- `risks.md`: Riesgos identificados y planes de mitigación
- `dependencies.md`: Dependencias internas, externas y técnicas
- `open-questions.md`: Preguntas abiertas y resueltas

**99-archive/** — Archivo
- `README.md`: Índice de archivo
- `deprecated/`: Documentos deprecados
- `old-decisions/`: Decisiones antiguas

### Changed
- `README.md` (raíz): Actualizados todos los estados de secciones a 🟢 Estable
- `CHANGELOG.md`: Agregada esta sección de cambios

---

## [Estructura inicial]

### Added
- Estructura inicial del repositorio de documentación