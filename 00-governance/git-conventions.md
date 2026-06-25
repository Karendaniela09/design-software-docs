# Convenciones de Git

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

Este repositorio usa ramas protegidas, Pull Requests y Conventional Commits para mantener trazabilidad documental.

## Ramas protegidas (4 ramas principales)

`main`, `dev`, `qa` y `staging` representan los ambientes del proyecto y **no se trabajan directamente**.

| Rama | Propósito | Regla |
|------|-----------|-------|
| `dev` | Integración de trabajo en desarrollo | Recibe PRs desde ramas hijas (`feature/*`, `hu-*`) |
| `qa` | Validación funcional y técnica | Recibe PRs o cherry-picks aprobados desde `dev` |
| `staging` | Entorno de pre-producción / validación final | Recibe PRs desde `qa` una vez aprobada |
| `main` | Producción / documentación estable | Recibe solo PRs desde `staging` o `release/*` |

## Flujo de trabajo con 4 ramas

feature/hu-01 → dev → qa → staging → main


1. **Desarrollo:** Se trabaja en ramas `feature/*` o `hu-*` basadas en `dev`.
2. **Integración:** Se hace PR a `dev` y se prueba.
3. **QA:** Se hace PR a `qa` para pruebas de calidad.
4. **Pre-producción:** Se hace PR a `staging` para validación final.
5. **Producción:** Se hace PR a `main` (solo desde `staging` o `release/*`).

## Ramas documentales

| Tipo de rama | Cuándo usarla | Ejemplo | Tipo de commit |
|--------------|---------------|---------|----------------|
| `feat` | Documento nuevo | `feat/doc-api-guidelines` | `docs` |
| `fix` | Corrección de contenido | `fix/doc-scope` | `fix` |
| `chore` | Reorganización o renombrado | `chore/doc-move-adr-003` | `chore` |
| `docs` | Actualización de documento existente | `docs/doc-service-catalog` | `docs` |

## Ramas por historia de usuario

| Caso | Rama base | Formato | Ejemplo |
|------|-----------|---------|---------|
| Desarrollo de HU | `dev` | `hu-<numero>-dev` | `hu-01-dev` |
| Ajuste o validación QA | `qa` | `hu-<numero>-qa` | `hu-01-qa` |
| Validación en Staging | `staging` | `hu-<numero>-staging` | `hu-01-staging` |
| Release de iteración | `main` | `release/<iteracion>` | `release/iteration-01` |

## Flujo hacia dev

```bash
git checkout dev
git pull origin dev
git checkout -b hu-01-dev

git add <archivos>
git commit -m "docs(04-requirements): add scheduling availability user story"
git push origin hu-01-dev

Abrir PR de hu-01-dev hacia dev.

y haci con las otras ramas de historia de usuario, siguiendo el flujo de trabajo establecido.
```
