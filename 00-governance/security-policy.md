# Política de Seguridad y Gobierno de Repositorios

> Estado: 🟢 Estable | Última actualización: 2026-08-13
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) — Product Owner
> Proyecto: Sistema de Horarios SENA (`design-software`, org `code-sena`)
> Complementa: [git-conventions.md](./git-conventions.md) (mecánica de ramas) y
> [agile-conventions.md](./agile-conventions.md).

## 1. Introducción

Este documento establece la **Política de Seguridad, Control de Cambios y Gobierno
de Repositorios** del proyecto *Sistema de Horarios*.

La política controla de forma **formal** cómo se realizan, revisan, aprueban e
integran los cambios en los repositorios, evitando modificaciones directas sobre las
ramas principales y garantizando **responsabilidad, trazabilidad y revisión** antes de
incorporar cualquier cambio.

Se fundamenta en dos elementos:

1. **La jerarquía organizacional del proyecto** (organigrama de seguridad y roles).
2. **La protección técnica de las ramas en GitHub** (flujo obligatorio basado en
   ramas de trabajo y Pull Requests).

Las ramas **padre / protegidas** son:

```text
develop
qa
staging
main
```

A partir de esta política, estas ramas **no admiten `git push` directo**: todo cambio
entra por **Pull Request desde una rama hija**.

---

## 2. Objetivo general

Proteger los repositorios del proyecto mediante:

- Separación de responsabilidades.
- Control de permisos (mínimo privilegio).
- Protección de ramas.
- Uso obligatorio de Pull Requests.
- Revisión y aprobación de cambios antes de integrar.
- Trazabilidad de modificaciones.
- Prevención de cambios accidentales o no autorizados.
- Organización clara de responsables técnicos.

Todos los integrantes siguen desarrollando normalmente, pero bajo un procedimiento
controlado.

---

## 3. Alcance

Aplica a los repositorios del proyecto, en especial a los **nueve repositorios de
base de datos**:

```text
design-software-academic-management-db
design-software-actors-db
design-software-audit-db
design-software-document-db
design-software-iam-db
design-software-monitoring-db
design-software-reference-data-db
design-software-scheduling-db
design-software-training-environment-db
```

Y también a: `design-software-docs`, `design-software-docker-infra`,
`design-software-mockup`, y a los futuros repos de Backend, Frontend, API Gateway,
Infraestructura, Docker, Documentación, Automatizaciones y componentes transversales.

---

## 4. Principios de la política

### 4.1 Mínimo privilegio

Cada integrante tendrá solo los permisos necesarios para su responsabilidad:

```text
Product Owner      → Admin
Coordinadores      → Admin
Líderes            → Write
Desarrolladores    → Write
Consulta externa   → Read
```

### 4.2 Separación de responsabilidades

Quien realiza un cambio no controla todo el proceso. El flujo separa:

```text
Desarrollar → Revisar → Aprobar → Integrar
```

Así ningún integrante desarrolla, aprueba e integra un cambio crítico sin supervisión.

### 4.3 Trazabilidad

Todo cambio queda registrado mediante: rama de trabajo, commits, Pull Request, autor,
revisores, comentarios, aprobaciones e historial del merge. Esto permite responder:

```text
¿Quién realizó el cambio?   ¿Por qué se hizo?   ¿Quién lo revisó?
¿Quién lo aprobó?           ¿Cuándo se integró? ¿Qué archivos cambió?
```

### 4.4 Protección de ramas críticas

`develop`, `qa`, `staging` y `main` son **ramas protegidas**. Ningún desarrollador ni
líder técnico hace `git push` directo sobre ellas. Todo cambio pasa por Pull Request.

---

## 5. Estructura jerárquica

```text
                    Instructor Jesús Ariel
                       Product Owner  (ADMIN)
                             │
                             ▼
                Arquitectos / Coordinadores
                  Andrey y Juan Pablo  (ADMIN)
                             │
                   ┌─────────┴─────────┐
                   ▼                   ▼
             Líder Backend       Líder Frontend
            María y Daniel           Yohan
               (WRITE)              (WRITE)
                   └─────────┬─────────┘
                             ▼
                     Líderes Técnicos  (WRITE)
   Mariana · Natalia · Amaya · Nicolas · Acero
   Palma · Danna · Yerson · Freinnier
                             │
                             ▼
                    Equipos de Desarrollo  (WRITE)
```

Esta jerarquía determina **responsabilidades de seguridad y niveles de autorización**
dentro de los repositorios.

---

## 6. Roles y responsabilidades

### 6.1 Product Owner — Instructor Jesús Ariel — `Admin`

Nivel superior de gobierno. Aprueba lineamientos y la política de seguridad; supervisa
el cumplimiento; participa en decisiones críticas; autoriza modificaciones de
arquitectura o seguridad de alto impacto; interviene en situaciones excepcionales;
desarrolla funcionalidades cuando lo requiera. No interviene en cada cambio cotidiano,
pero conserva autoridad para intervenir ante cambios críticos.

### 6.2 Arquitectos / Coordinadores — Andrey Gómez, Juan Pablo — `Admin`

Principales responsables de administrar técnicamente la política:

- Administrar repositorios, permisos, miembros y equipos.
- Configurar reglas de protección de ramas y `CODEOWNERS`.
- Revisar/aprobar/rechazar Pull Requests críticos.
- Realizar merges hacia ramas protegidas cuando corresponda.
- Mantener la estructura de ramas y las configuraciones sensibles.
- Verificar el cumplimiento de la política y resolver excepciones.
- Desarrollar funcionalidades del sistema.

Actúan como **control administrativo y de seguridad**.

### 6.3 Líder Backend — María, Daniel — `Write`

Supervisan arquitectura backend; revisan cambios que afecten múltiples microservicios;
validan estándares; revisan riesgos de seguridad backend; coordinan decisiones entre
equipos; escalan a coordinadores; acompañan a líderes técnicos; desarrollan
funcionalidades; verifican compatibilidad entre servicios. **No** administran reglas de
protección.

### 6.4 Líder Frontend — Yohan — `Write`

Supervisa arquitectura frontend; verifica estándares; revisa seguridad del lado
cliente; coordina decisiones transversales; identifica riesgos; acompaña a
desarrolladores; desarrolla funcionalidades; escala a coordinadores. **No** puede
saltarse las reglas de ramas protegidas.

### 6.5 Líderes técnicos — `Write`

Mariana, Natalia, Amaya, Nicolas, Acero, Palma, Danna, Yerson, Freinnier. Cada uno
responsable del repositorio/microservicio asignado:

- Supervisar al equipo de desarrollo; revisar Pull Requests.
- Verificar buenas prácticas, estructura y calidad; detectar errores antes de integrar.
- Verificar uso correcto de ramas; solicitar modificaciones; resolver observaciones.
- Escalar riesgos a líderes de arquitectura o coordinadores; desarrollar funcionalidades.

**Restricciones:** no pueden hacer push directo a ramas protegidas, ni modificar reglas
de protección, ni saltarse el PR, ni deshabilitar controles, ni integrar sus propios
cambios sin las aprobaciones correspondientes.

### 6.6 Equipos de Desarrollo — `Write`

Pueden: crear ramas, desarrollar, commitear, subir sus ramas, abrir PRs, corregir
observaciones y actualizar sus ramas. **No** pueden hacer push directo a
`develop/qa/staging/main` ni modificar las reglas de protección.

---

## 7. Matriz de permisos

| Acción | Product Owner | Coordinadores | Líderes | Desarrolladores |
|--------|:---:|:---:|:---:|:---:|
| Consultar repositorio | ✅ | ✅ | ✅ | ✅ |
| Crear ramas | ✅ | ✅ | ✅ | ✅ |
| Realizar commits | ✅ | ✅ | ✅ | ✅ |
| Crear Pull Request | ✅ | ✅ | ✅ | ✅ |
| Revisar PR | ✅ | ✅ | ✅ | Según política |
| Aprobar PR | ✅ | ✅ | ✅ Técnico | No como aprobación administrativa |
| Promover entre ambientes (cherry-pick / release) | ✅ | ✅ | ✅ | ❌ |
| Administrar repositorio | ✅ | ✅ | ❌ | ❌ |
| Modificar protección de ramas | ✅ | ✅ | ❌ | ❌ |
| Administrar permisos | ✅ | ✅ | ❌ | ❌ |
| Push directo a ramas protegidas | Restringido | Restringido | ❌ | ❌ |
| Realizar cambios mediante PR | ✅ | ✅ | ✅ | ✅ |
| Saltarse reglas de seguridad | Solo emergencia controlada | Solo emergencia controlada | ❌ | ❌ |

---

## 8. Controles de seguridad

- **Pull Request obligatorio** — todo cambio se integra vía PR.
- **Aprobaciones mínimas** — idealmente aprobación **técnica** + aprobación
  **administrativa** antes del merge (*Four Eyes Principle*).
- **CODEOWNERS** — `.github/CODEOWNERS` define los revisores responsables por ruta;
  para cambios administrativos o críticos, el equipo responsable participa en la
  revisión.
- **Branch Protection / Rulesets** — las ramas críticas se protegen con las opciones de
  GitHub: sin push directo, sin force-push, sin borrado, revisión requerida.
- **Sin push directo** — se prohíbe `git push origin {develop|qa|staging|main}` para
  quien no tenga autorización administrativa excepcional.
- **Conversaciones resueltas** — las observaciones de los revisores deben resolverse
  antes del merge.

---

## 9. Flujo de trabajo del desarrollador (hacia `develop`)

```bash
# 1. Partir de develop actualizado
git checkout develop
git pull origin develop

# 2. Crear rama de trabajo (hija de develop)
git checkout -b hu-02-dev            # convención: hu-<NN>-dev

# 3. Trabajar y commitear (Conventional Commits, en inglés)
git add <archivos>
git commit -m "feat(iam): add login screen and validations"

# 4. Subir SOLO la rama de trabajo (no es protegida)
git push -u origin hu-02-dev
```

Evitar mensajes como `cambios`, `prueba`, `fix`, `cosas`. Preferir descriptivos:
`feat(scheduling): add availability validations`.

Luego abrir el **Pull Request** `hu-02-dev → develop` documentando el cambio.

### Revisión y corrección

El **líder técnico** revisa código, estructura, cumplimiento de la HU, buenas
prácticas, impactos, calidad, conflictos y compatibilidad, y marca `Approve` o
`Request changes`. Si pide cambios, el desarrollador corrige **en la misma rama**:

```bash
git checkout hu-02-dev
git add <archivos>
git commit -m "fix(iam): correct validations from review"
git push
```

GitHub actualiza el PR automáticamente (no se crea otro). Tras la revisión técnica, el
**Instructor o un coordinador** hace la revisión administrativa (reglas, impacto,
riesgos, aprobaciones) y se realiza el **merge a `develop`**. La rama de trabajo puede
eliminarse después del merge.

---

## 10. Flujo de promoción entre ambientes (rama hija por ambiente)

> ⚠️ **Regla de oro (crítica).** Las ramas padre **NO se fusionan entre sí**. Está
> **PROHIBIDO** hacer PR o `merge` directo `develop→qa`, `qa→staging`, `staging→main` o
> `develop→main`, y está prohibido `merge -X theirs/ours` para "igualar" ambientes: eso
> puede **perder cambios propios** de cada ambiente (ya ocurrió, marcado como error
> grave). Cada cambio viaja a cada ambiente por **su propia rama hija**, creada **desde
> ese ambiente**, y hace PR hacia **su propio** padre.

```text
Rama HU (hu-NN-dev, desde develop)      ─PR→  develop
Rama HU (hu-NN-qa, desde qa)            ─PR→  qa        (trae el cambio con merge/cherry-pick de hu-NN-dev)
Rama HU (hu-NN-staging, desde staging)  ─PR→  staging   (trae el cambio con merge/cherry-pick de hu-NN-qa)
release/<iteracion> (desde main)        ─PR→  main       (aglomera las HUs validadas en staging)
```

Ejemplo — llevar una HU ya integrada en `develop` hacia `qa`:

```bash
git checkout qa
git pull origin qa
git checkout -b hu-02-qa               # rama hija DESDE qa
git merge origin/hu-02-dev            # o: git cherry-pick <sha1> <sha2>
git push -u origin hu-02-qa
# → abrir PR hu-02-qa → qa
```

Igual para `staging` (`hu-02-staging` desde `staging`). El **release se corta desde
`main`** en una rama `release/<iteracion>` que aglomera las HUs validadas, y hace PR a
`main`. Ver el detalle canónico en [git-conventions.md](./git-conventions.md).

### ¿Quién promueve entre ambientes? (rol reservado)

> 🔒 La **promoción entre ambientes** —crear la rama hija del ambiente destino y traer el
> cambio con `merge`/`cherry-pick`, más el `release/<it>` hacia `main`— es **tarea
> reservada a Líderes técnicos, Arquitectos/Coordinadores y Product Owner.**
> Los **desarrolladores solo trabajan `hu-NN-dev → develop`**; no promueven a
> `qa/staging/main` ni ejecutan cherry-picks de promoción.

**Sobre `cherry-pick`:** es un **camino posible pero NO el flujo principal**. El flujo
recomendado para features es **rama hija por ambiente** (merge de la HU completa). El
`cherry-pick` se usa **solo en casos puntuales** (llevar commits específicos, no toda la
HU) y por los roles autorizados, porque **mal usado puede perder trazabilidad o duplicar
cambios**. Los `hotfix/*` sí pueden propagarse a cada padre por rama hija + cherry-pick,
igualmente a cargo de los roles autorizados.

> **Ecualización = contenido, no historial.** Que los 4 ambientes queden "iguales"
> significa **mismo árbol de archivos desplegado**, no mismo historial. Con rama hija
> por ambiente el mismo cambio llega con **SHA distinto** → el historial diverge (normal
> y correcto). **Nunca** se fuerza igualdad de SHAs con `reset --hard` o `merge -X theirs`.

### Función de cada rama

| Rama | Rol | Recibe de |
|------|-----|-----------|
| `develop` | Primer nivel de integración | ramas `hu-NN-dev` |
| `qa` | Validación de calidad | ramas `hu-NN-qa` (cambio traído de `develop`) |
| `staging` | Preproducción / validación final | ramas `hu-NN-staging` (cambio traído de `qa`) |
| `main` | Versión estable / producción | ramas `release/<iteracion>` |

---

## 11. Actualizar una rama de trabajo cuando el padre avanza

Si `develop` recibió cambios mientras trabajabas, actualiza **tu rama personal**:

```bash
git fetch origin
git rebase origin/develop
git push --force-with-lease         # solo sobre TU rama de trabajo, nunca sobre padres
```

**Nunca** `force push` sobre `develop`, `qa`, `staging` ni `main`.

---

## 12. Excepciones (hotfix)

Ante incidente grave, falla de producción, vulnerabilidad crítica o corrupción de
datos, se usa una rama `hotfix/*` (o `fix/*` en docs) creada **desde `main`**. El cambio
**sigue requiriendo Pull Request**:

```text
hotfix/<descripcion>  ─PR→  main
```

Después, el mismo fix se **propaga** a `staging`, `qa` y `develop` por rama hija +
cherry-pick (nunca fusionando padres entre sí), para evitar divergencias.

---

## 13. Estado de aplicación

La org `code-sena` está en **GitHub Team** (beneficio educativo, plan verificado
`team`), lo que habilita protección de ramas server-side en repos privados.

- ✅ **PROTECCIÓN ACTIVA en los 12 repos** `design-software-*` (2026-08-13): ruleset
  `protect-parent-branches` con `enforcement: active` sobre `main/develop/qa/staging`:
  - **Sin push directo** — PR obligatorio con **2 aprobaciones** mínimas (técnica + administrativa).
  - **Sin force-push** (`non_fast_forward`) y **sin borrado** de rama.
  - **Conversaciones (review threads) resueltas** antes del merge.
- 🔜 **Pendiente (capa organizacional):** `CODEOWNERS` reales por repo (hoy con
  placeholders / nombres de pila; faltan handles de GitHub y mapeo líder-técnico→repo) y
  ajuste fino de teams/permisos (Read/Write/Admin) según el organigrama.

Sube el nº de aprobaciones a 2 exportando `REQUIRED_APPROVALS=2` antes de correr el
script de rollout `delivery/utils/protect-parent-branches.sh`, que crea o actualiza el ruleset
en los 12 repos. Ese script pertenece al workspace de entrega y no está versionado en este repo.

---

## 14. Política resumida

1. `main`, `staging`, `qa` y `develop` son ramas protegidas.
2. No se permite push directo a estas ramas.
3. Todo desarrollo se realiza en una rama independiente.
4. Cada cambio ingresa mediante Pull Request.
5. Los líderes técnicos revisan los cambios de sus equipos.
6. Los coordinadores administran las reglas y controles.
7. Los cambios críticos requieren supervisión administrativa.
8. Los comentarios pendientes se resuelven antes del merge.
9. Los permisos siguen el principio de mínimo privilegio.
10. La promoción se realiza por **rama hija por ambiente** (nunca padre→padre):
    `hu-NN-dev→develop`, `hu-NN-qa→qa`, `hu-NN-staging→staging`,
    `release/<it>→main`.

---

## 15. Conclusión

La política establece una estructura donde cada persona tiene el nivel de acceso
adecuado a su responsabilidad, combinando el modelo organizacional
(Product Owner → Coordinadores → Líderes → Equipos) con controles técnicos
(ramas protegidas + Pull Requests + CODEOWNERS + aprobaciones + revisión técnica +
trazabilidad). El resultado: **mayor seguridad, organización, control, trazabilidad y
calidad**, con los desarrolladores trabajando con autonomía en sus ramas y el
liderazgo conservando la revisión y el gobierno necesarios.
