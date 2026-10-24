# Scripts de CI del repo docs

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: DevOps

## Contexto

Scripts que ejecuta el workflow [`docs-ci.yml`](../../.github/workflows/docs-ci.yml) en cada Pull Request hacia `main` (HU-SHELL-013). Automatizan los errores mecánicos de revisión para que los aprobadores se concentren en el contenido. El respaldo documental y el estado de cada control están en [10-devops/ci-cd.md](../../10-devops/ci-cd.md).

**Principio:** cada control mira solo **lo que cambia el PR** (diff contra la base). Así la deuda que ya existe en `main` no hace fallar PRs ajenos.

Solo usan la biblioteca estándar de Python 3 (el lint OpenAPI además necesita Node.js para `npx`). No requieren secretos.

## Contenido

| Script | Qué controla | Falla cuando |
|--------|--------------|--------------|
| `check_pr_title.py` | Título del PR (se lee de `PR_TITLE`; con squash es el commit que llega a `main`) | No cumple `<type>(<scope>): <description>` con type `docs`, `fix`, `chore` o `refactor` (scope opcional) |
| `check_links.py` | Enlaces relativos de los `.md` agregados, modificados o renombrados | Un enlace apunta a un archivo o carpeta que no existe en el árbol del PR. Se ignoran enlaces externos, anclas `#...` y bloques de código. Los enlaces que ya estaban rotos en la versión base del archivo se reportan como advertencia |
| `check_adr.py` | Unicidad del número de ADR en `05-architecture/decisions/records/` | Dos ADR con el mismo número en el árbol del PR, un ADR nuevo con un número que ya existe en `main`, o un ADR nuevo con un número que también agrega un PR abierto más antiguo |
| `check_pii.py` | Líneas **agregadas** del diff | Aparece `CC`, `C.C.`, `cédula` o `cedula` seguido de 6 a 10 dígitos. El número se enmascara en el reporte y nunca se imprime |
| `check_openapi.py` | Contratos `07-api/contracts/openapi/*.yaml` tocados por el PR | `@redocly/cli@1 lint` (con [`redocly.yaml`](../../redocly.yaml)) produce errores **nuevos** respecto a la versión base. Si cambia `_shared.yaml` o `redocly.yaml` se revisan todos los contratos. Las advertencias no bloquean |

`_common.py` es una biblioteca compartida (git, reporte de errores); no se ejecuta directamente.

### Regla de unicidad entre PRs abiertos

`main` tiene los ADR numerados sin repeticiones, pero varios PRs abiertos pueden reclamar el mismo número a la vez (caso ADR-020). Eso no se ve mirando solo `main`, por lo que `check_adr.py` consulta con `gh` los PRs abiertos hacia la misma rama base y compara los archivos que agregan. **Gana el PR más antiguo** (menor número): los PRs posteriores que reclamen el mismo número fallan hasta renumerar su ADR; el más antiguo no queda bloqueado. Usa el `GITHUB_TOKEN` del workflow con permisos de solo lectura. Si la API no responde, esa regla se omite con una advertencia y las otras dos siguen activas.

## Ejecución local

Desde la raíz del repo, con la rama de trabajo como `HEAD` y `main` actualizada:

```bash
git fetch origin main

PR_TITLE="docs(10-devops): add docs validation workflow" python scripts/ci/check_pr_title.py
python scripts/ci/check_links.py   --base origin/main --head HEAD
python scripts/ci/check_adr.py     --base origin/main --head HEAD --pr <numero-del-pr> --repo code-sena/design-software-docs
python scripts/ci/check_pii.py     --base origin/main --head HEAD
python scripts/ci/check_openapi.py --base origin/main --head HEAD
```

- `check_adr.py` con `--pr` y `--repo` necesita `gh` autenticado; sin ellos solo aplica las reglas contra `main`. Para pruebas sin red acepta `--open-prs-json <archivo>`.
- `check_pii.py --staged` revisa los cambios en el índice (para probar sin hacer commit).
- `check_links.py --all` recorre todos los `.md` del árbol y sirve para medir la deuda existente.
- Todos los scripts devuelven código de salida distinto de cero cuando hay errores.

## Límites conocidos

- **Datos personales:** es una heurística por patrón; no detecta otros identificadores (teléfonos, correos) ni números escritos sin la palabra clave. No sustituye la revisión humana ni [security-rules.md](../../00-governance/security-rules.md).
- **Enlaces:** valida que el destino exista, no que exista el ancla `#...`. Solo revisa los archivos que cambia el PR: renombrar o borrar un documento no revisa los enlaces que le apuntan desde archivos no modificados.
- **OpenAPI:** la primera ejecución de `npx` descarga Redocly (1 a 3 minutos).
- Que el check sea **obligatorio** para mergear lo decide el dueño del repo en el ruleset; este workflow no lo configura.

## Referencias

- [10-devops/ci-cd.md](../../10-devops/ci-cd.md) — controles del pipeline y su estado
- [00-governance/git-conventions.md](../../00-governance/git-conventions.md) — ramas, PRs y Conventional Commits
- [00-governance/documentation-rules.md](../../00-governance/documentation-rules.md) — reglas de contenido
- [`docs-ci.yml`](../../.github/workflows/docs-ci.yml) — workflow
