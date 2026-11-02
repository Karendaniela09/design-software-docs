<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: arquitectura de micro-frontends (capa "por debajo" del mockup)
fase: diseño (UX/UI + arquitectura frontend)
estado: draft
dependencias_entrada: 09-microservices/service-catalog.md; 07-api/contracts/openapi/*.yaml; mockup-ddd/flows/*.md; 12-ux-ui/navigation-map.md
consumidores_siguientes: construcción del mockup completo; luego el frontend real (micro-frontends)
tldr: La experiencia se organiza por rol/funcionalidad (flows), pero POR DEBAJO el frontend se construye como un micro-frontend por dominio (espejo de los 9 microservicios) más un app-shell host que compone. Este doc mapea dominio→micro-frontend→pantallas y cómo los flujos componen varios MFE.
decisiones_clave: 1 micro-frontend por dominio (9) + 1 app-shell host; los flujos por rol son composiciones; cada MFE consume SU openapi.yaml; composición cross-dominio vía shell/read-models (BFF)
halts_registrados: ninguno
-->

# Arquitectura de Micro-Frontends (la capa "por debajo" del mockup)

> **ESTADO: PRELIMINAR (v0)** — mapa de arquitectura frontend que sostiene los flujos.

## Principio (dos ejes que coexisten)

| Eje | Se organiza por | Artefacto |
|---|---|---|
| **Experiencia** (lo que ve el usuario) | **rol / funcionalidad** | `flows/*.md` (Coordinador, Instructor, …) |
| **Construcción** (cómo se implementa) | **dominio** | **un micro-frontend por microservicio** + **app-shell host** |

Un **flujo por rol** NO es un módulo de código: es una **composición** de pantallas/widgets
provistos por **varios micro-frontends**. Espeja el backend: 9 microservicios (dominio) →
9 micro-frontends (dominio) → compuestos en experiencias por rol.

## Componentes de la arquitectura

- **`shell-host`** (contenedor / orquestador): app shell (barra superior, notificaciones, menú de
  usuario), **navegación por rol** (derivada de `GET /auth/me.features` + `actor_type` + RBAC, agrupada en secciones; ver [visual-spec.md](../visual-spec.md) §4 y HU-SHELL-019), enrutamiento,
  sesión/JWT, tema/design-system, estados globales (offline). **No** contiene lógica de dominio.
- **Un micro-frontend (MFE) por dominio**, dueño de las pantallas/componentes de SU dominio y que
  consume **su** `openapi.yaml`. Se montan dentro del shell según la ruta/rol.

> **Topología de despliegue (ADR-005).** El patrón es **hosts + remotes vía Module Federation**:
> - **Remotes** = los 9 MFE de dominio (responsive, deploy independiente). Slug **canónico** = el del
>   servicio: `reference-data-mfe`, `academic-management-mfe`, `training-environment-mfe` (renombrados
>   desde los cortos previos), más `iam/scheduling/actors/document/monitoring/audit`-mfe.
> - **Hosts** (agregadores que embeben los remotes): `web-shell` (fase 1) y `mobile-shell` (fase 2).
>   `shell-host` de este documento se materializa como estos hosts por experiencia.
> - **BFF por experiencia**: `web-bff` + `mobile-bff` (no un BFF único). Camino:
>   `cliente → gateway → BFF → servicios`.
> - **Notificaciones** = chrome global del host (campana/panel/inbox), consumiendo `notification-service`;
>   **no** hay `notification-mfe`.
>
> Las carpetas del mockup (`academic/`, `environment/`, `reference/`, …) conservan su nombre corto por
> ser artefacto ya construido; el mapeo a los repos reales usa el slug canónico de arriba.

## Mapa dominio → micro-frontend → pantallas (dueño) → microservicio

| Micro-frontend | Microservicio (backend) | Pantallas/componentes que posee | Flujos donde aparece |
|---|---|---|---|
| **shell-host** | — (usa iam para sesión) | App shell, nav por rol, notificaciones (contenedor), páginas de error/offline | todos |
| **iam-mfe** | iam-service | Login, Recuperar/Nueva contraseña, Administración de **Usuarios/roles** | 01-auth, 05-administrador |
| **scheduling-mfe** | scheduling-service | **Horarios (lista)**, **Crear/editar horario**, **Panel de conflictos**, vistas **Mi horario** (semana) | 02-coordinador, 03-instructor, 04-aprendiz |
| **academic-management-mfe** | academic-management-service | **Fichas** (lista/consulta), programas/competencias | 02-coordinador |
| **training-environment-mfe** | training-environment-service | **Disponibilidad de ambientes**, gestión de ambientes/reservas | 02-coordinador |
| **actors-mfe** | actors-service | Instructores/aprendices, **Mi disponibilidad** (instructor) | 02-coordinador, 03-instructor |
| **document-mfe** | document-service | **Documentos**, **Plantillas de documento** | 06-backoffice |
| **monitoring-mfe** | monitoring-service | **Panel de indicadores (KPIs)**, **Seguimiento de ficha** | 05-administrador, 03-instructor, 04-aprendiz |
| **audit-mfe** | audit-service | **Auditoría** (traza) | 06-backoffice |
| **reference-data-mfe** | reference-data-service | **Parametrización / catálogos**, **Datos de referencia** (regionales/centros/sedes) | 05-administrador, 06-backoffice |

## Parametrización (07 · director + soporte): pantalla nueva por MFE

Las pantallas de parametrización configuran los catálogos y datos maestros que los flujos operativos
exigen como prerequisito. Cada MFE afectado suma **una** pantalla de parametrización:

| Micro-frontend | Pantalla de parametrización que suma | Prerequisito que habilita |
|---|---|---|
| **reference-data-mfe** | **Hub de parametrización** (`/admin/parametrizacion`, montado por el shell) + **Geografía institucional** | punto de entrada; regionales/centros/sedes |
| **academic-management-mfe** | **Currículo académico** | currículo → fichas |
| **scheduling-mfe** | **Jornadas / franjas horarias** | franjas → horarios |
| **training-environment-mfe** | **Tipos de ambiente e inventario** | tipos de ambiente → ambientes |
| **monitoring-mfe** | **Catálogos de monitoreo (KPI/alertas)** | catálogos → KPIs |
| **actors-mfe** | **Estados de actores** | máquina de estados de actores |
| **iam-mfe** | **RBAC — roles y permisos** | roles/permisos RBAC |

## Realización en el mockup

El mockup adoptado (`mockups/app/`) realiza esta arquitectura **1:1** como SPA con hash-router:

- **`shell/`** = `shell-host`: router (`app.js`), `routes.js`, `screens.js`, `shell.js` — marco,
  navegación por rol, guards RBAC y estados globales. No contiene lógica de dominio.
- **Una carpeta por dominio**, cada una dueña de su `screens.js`:
  `iam/ scheduling/ academic/ environment/ actors/ document/ monitoring/ audit/ reference/`.
- **`assets/` compartido** (un solo set de tokens/componentes: `tokens.css`, `components.css`,
  `app.css`, `components.js`, `icons.js`) — ningún dominio redefine tokens.
- **`tools/validate-routes.js`** valida la cobertura ruta↔pantalla (**53/53**).

## Cómo un flujo compone varios micro-frontends

Ejemplo — **Dashboard del Coordinador** (una sola pantalla, varios MFE):
```
shell-host (marco + nav + saludo)
├─ scheduling-mfe   → widget "Conflictos pendientes" + widget "Horarios en borrador"
├─ academic-management-mfe     → KPI "Fichas activas"
└─ (navegación)     → "Crear horario" abre una pantalla de scheduling-mfe
```
La composición cross-dominio (juntar datos de varios MFE en una pantalla) se resuelve con:
- **Composición en el shell** (el host monta widgets de cada MFE), y/o
- una capa **BFF / read-model** que agrega los datos que una pantalla necesita de varios dominios
  (ver `discovery-findings.md` — nombres de instructor/ambiente/competencia viven en otros dominios;
  referencias por UUID sin FK física, patrón de microservicios).

## Reglas de la arquitectura

1. **Cada MFE consume SOLO su `openapi.yaml`.** No llama directo a la BD ni a otro dominio; los
   datos de otro dominio llegan vía su MFE (composición) o vía BFF/read-model.
2. **El shell-host no tiene lógica de dominio** (solo marco, sesión, nav, tema).
3. **Design-system compartido** (tokens/componentes base) entre todos los MFE para coherencia
   visual (ver `12-ux-ui/design-system.md`). Un MFE no redefine tokens.
4. **Contract-first:** el MFE se construye contra el contrato (no contra el mockup — el frontend
   real jamás conoce el mockup; ver `README.md`).
5. **Trazabilidad:** cada pantalla del flujo declara su **MFE dueño** además de `HU → endpoint →
   tabla` (se agrega el campo "MFE" al header de cada pantalla en la maduración del spec).

## Relación con el resto del spec

- Los **flujos** (`flows/*.md`) siguen siendo la unidad de **experiencia** (y de generación de
  mockup por Stitch/GPT).
- Este documento es la unidad de **arquitectura de construcción** (qué MFE posee qué pantalla).
- La **maduración del spec** conecta ambos: cada pantalla del flujo apunta a su MFE dueño, y el
  inventario de pantallas/componentes se agrupa por MFE para la fase de construcción del frontend.
