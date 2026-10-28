# DevOps

> Estado: 🟡 Revisión | Última actualización: 2026-10-07
> Autor: Kevin Andrey Culma (Arquitecto) | Equipo: Arquitectura.

Índice de la sección de DevOps del sistema de Gestión de Horarios SENA. Cubre cómo se levanta el entorno local, cómo se validan y promueven los cambios, y qué ambientes existen.

## Estado real

El estado difiere **por ambiente**:

- **`develop`** ya corre **capa de aplicación**, no solo datos: hay **perfiles de aplicación en docker-compose** que levantan dos microservicios por perfil sobre la BD compartida — `iam-api` (Java/Spring) y `notification` (api + worker, Go) — apuntando a **PostgreSQL 16** `design-software-develop` (`:15432`). El **edge Traefik** enruta `/iam/*` con `StripPrefix` (ADR-007) y hay un **stack de observabilidad vivo**: OTel Collector → Tempo/Grafana para trazas E2E cross-servicio (ADR-008). El bring-up local de estos perfiles vive en [local-setup.md](./local-setup.md); la observabilidad es HU-IAM-011 y el deploy local E2E con trazas en Tempo es HU-IAM-012.
- **`qa` / `staging` / `main`** siguen materializando **solo la capa de datos** (PostgreSQL 16 + runners de Liquibase por módulo que aplican los changelogs de cada repo `*-db`). Los perfiles de aplicación **no** están promovidos a estos ambientes todavía.

Las páginas marcan lo implementado frente a lo previsto, distinguiendo por ambiente.

## Archivos

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [local-setup.md](./local-setup.md) | Levantar Postgres, aplicar changelogs por módulo y hacer bring-up de los perfiles de aplicación (`iam`, `notification`) + observabilidad en local | 🟡 |
| [ci-cd.md](./ci-cd.md) | Pipeline previsto: validación de changelogs, PR checks, Conventional Commits y promoción por ramas (implementado vs pendiente) | 🟡 |
| [environments.md](./environments.md) | Los 4 ambientes (`develop`/`qa`/`staging`/`main`), variables por `.env.<ambiente>` y advertencia de secretos | 🟡 |
| [frontend-images.md](./frontend-images.md) | Las 10 imágenes estáticas del frontend (shell y 9 MFE) que sirve el edge: cómo se construyen, qué sirven y cómo se verifican | 🟡 |
| [runtime-configuration-map.md](./runtime-configuration-map.md) | Mapa de variables de configuración runtime detectadas por repositorio | 🟡 |
| [REPORTE-DOCKER-Y-DESPLIEGUE-2026-10-27.md](./REPORTE-DOCKER-Y-DESPLIEGUE-2026-10-27.md) | Evidencia de rutas publicadas, diagnóstico de proxy y pasos seguros de inspección de la VPS | 🟡 |

## Plantillas

| Plantilla | Descripción |
|-----------|-------------|
| [_template-deployment-plan.md](./_template-deployment-plan.md) | Plan de despliegue: componentes, pasos, verificación y rollback |
| [_template-release-checklist.md](./_template-release-checklist.md) | Checklist de release: gates de código, QA, seguridad e infraestructura |
| [_template-rollback-plan.md](./_template-rollback-plan.md) | Plan de rollback: criterios de activación y procedimientos por componente |

## Cómo se relaciona

- La **estrategia de migraciones** (orden, seeds idempotentes, rollbacks, tags) vive en [06-data/migration-strategy.md](../06-data/migration-strategy.md).
- La **topología de despliegue** (qué corre y dónde) está en [05-architecture/deployment.md](../05-architecture/deployment.md).
- El **flujo de ramas y Conventional Commits** que gobierna la promoción está en [00-governance/git-conventions.md](../00-governance/git-conventions.md).
- El **riesgo de secretos versionados** en `.env.*` se detalla en [05-architecture/security-threat-model.md](../05-architecture/security-threat-model.md) §Secretos.

## Integración Reference Data

- [reference-data-integration.md](./reference-data-integration.md): secuencia docs-first, repositorios responsables y ejecución/revisión de HU-REF-020 y R1 en el macroproyecto; en revisión.

- [HU-INT-REF-001 integration](./reference-data-int-ref-001.md): canonical contract, GLOBAL scope policy, public URLs and isolated acceptance runner; in review.
