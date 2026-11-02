<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: mapa de rutas (sitemap) + matriz de visibilidad RBAC del mockup
fase: diseño (UX/UI)
estado: draft
dependencias_entrada: mockup-ddd/flows/*.md (Ruta/Rol por pantalla); micro-frontends.md; 09-microservices/services/01-iam-service/rbac-design.md
consumidores_siguientes: enrutamiento del frontend (shell-host), guards RBAC, generación del mockup
tldr: Árbol de rutas por rol (ruta → pantalla → MFE → guard) y matriz rol × área de visibilidad. Los modales no tienen ruta propia (estado de UI).
decisiones_clave: rutas públicas vs autenticadas; áreas por rol; modales sin URL; estados globales transversales
halts_registrados: ninguno
-->

# Sitemap (mapa de rutas) + Visibilidad RBAC

> **ESTADO: PRELIMINAR (v0).** Rutas derivadas de los `flows/*.md`. Los **modales** no tienen ruta
> propia (se abren por estado de UI sobre su ruta padre). Guard = rol/feature exigido (RBAC).

> **Implementación en el mockup:** estas rutas se realizan como **hash-routes** con query params de
> revisión: `?as=<rol>` (rol activo), `?state=loading|empty|error` y `?offline=1` (estados de
> revisión), `?modal=…` (modales — sin ruta propia, como ya se indica), `?overlay=notifications`
> (panel de notificaciones), y los estados globales en `#/system-states?variant=403|404|500|session`.
> El **inventario maestro** de pantallas está en `#/inventory` (también `review.html`).

## Árbol de rutas

### Público (anónimo) — `iam-mfe`
```
/login                      → Login (01-auth P1)
/forgot-password            → Recuperar contraseña (01-auth P2)
/reset-password?token=…     → Nueva contraseña (01-auth P3)
```

### Autenticado — `shell-host` (marco común, nav por rol desde /auth/me.features + actor_type, HU-SHELL-019)
```
/                           → landing según rol (redirige)
· overlay notificaciones    → Panel de notificaciones (01-auth P5)  [campana del top bar]
· 403 / 404 / 500 / sesión  → Estados globales (01-auth P6)         [reemplaza el área de contenido]
```

### Coordinador (`COORDINATOR`, scope TRAINING_CENTER)
```
/                           → Dashboard/Inicio (02 P1)      [compone scheduling+academic]
/horarios                   → Horarios lista (02 P2)         · scheduling-mfe
/horarios/nuevo             → Crear horario (02 P4)          · scheduling-mfe
/horarios/:id               → Detalle/editar horario (02 P3/P4) · scheduling-mfe
   ├ modal agregar sesión (02 P5) · modal confirmar publicación (02 P6)
/horarios/:id/conflictos    → Panel de conflictos (02 P7)    · scheduling-mfe
   └ modal resolver conflicto (02 P8)
/disponibilidad             → Disponibilidad (02 P9)         · environment-mfe + actors-mfe
/disponibilidad/ambientes/:id → Detalle de ambiente (02 P10) · environment-mfe
/fichas                     → Fichas (02 P11)                · academic-mfe
/fichas/:id                 → Detalle de ficha (02 P12)      · academic-mfe
```

### Instructor (`INSTRUCTOR`)
```
/instructor/mi-horario      → Mi horario semana (03 P1)      · scheduling-mfe
   └ panel Detalle de sesión (03 P2)
/instructor/mi-disponibilidad → Mi disponibilidad (03 P3)    · actors-mfe
   └ modal Crear excepción (03 P4)
/instructor/seguimiento     → Seguimiento de ficha (03 P5)   · monitoring-mfe
   └ form Registrar seguimiento (03 P6)
```

### Aprendiz (`LEARNER`) — mobile-first
```
/mi-horario                 → Mi horario semana (04 P1)      · scheduling-mfe
/mi-horario/sesiones/:id    → Detalle de clase (04 P3)       · scheduling-mfe
/notificaciones             → Notificaciones (04 P2)         · shell-host + notification-service (bloqueado)
/notificaciones/:id         → Detalle de notificación (04 P4) · shell-host + notification-service
```

### Administrador de Centro / Director (`CENTER_DIRECTOR` / `ADMIN`)
```
/admin/indicadores          → KPIs (05 P1)                   · monitoring-mfe
/admin/indicadores/:ft/:kpi → Drill-down de KPI (05 P2)      · monitoring-mfe
/admin/usuarios             → Usuarios (05 P3)               · iam-mfe
/admin/usuarios/:id         → Detalle de usuario (05 P5)     · iam-mfe
   ├ modal Crear/editar usuario (05 P4) · modal Asignar/revocar rol (05 P6)
/admin/datos-referencia     → Datos de referencia (05 P7, solo-lectura para Director)
   └ modal Editar (05 P8)                                    · reference-mfe
/admin/parametrizacion      → Hub de parametrización (07 P1) · reference (shell)
/admin/parametrizacion/curriculo  → Currículo académico (07 P2)      · academic-mfe
/admin/parametrizacion/jornadas   → Jornadas / franjas horarias (07 P3) · scheduling-mfe
/admin/parametrizacion/ambientes  → Tipos de ambiente e inventario (07 P4) · environment-mfe
/admin/parametrizacion/monitoreo  → Catálogos de monitoreo (07 P5)   · monitoring-mfe
/admin/parametrizacion/estados    → Estados de actores (07 P6)       · actors-mfe
/admin/parametrizacion/geografia  → Geografía institucional (07 P7)  · reference-mfe
/admin/parametrizacion/rbac       → RBAC — roles y permisos (07 P8)  · iam-mfe
```
> Las rutas `/admin/parametrizacion/*` son visibles para Director y Soporte (director + support).

### Back-office (`ADMIN_STAFF` / `SYSTEM_ADMIN`)
```
/backoffice/documentos      → Documentos (06 P1)             · document-mfe
   └ modal Generar documento (06 P6)
/backoffice/documentos/:id  → Detalle documento + versiones (06 P5) · document-mfe
/backoffice/documentos/plantillas       → Plantillas (06 P2) · document-mfe
/backoffice/documentos/plantillas/:id/editar → Editor/preview (06 P7) · document-mfe
/backoffice/auditoria       → Auditoría (06 P3)              · audit-mfe
   └ modal Detalle de auditoría (06 P8)
/backoffice/parametrizacion → Parametrización (06 P4)        · reference-mfe
   └ modales CRUD catálogos/parámetros (06 P9)
```

## Matriz de visibilidad RBAC (rol × área)

✅ ve/entra · 👁 solo lectura · — no visible

| Área | Coordinador | Instructor | Aprendiz | Director | ADMIN_STAFF/SYS_ADMIN |
|---|:--:|:--:|:--:|:--:|:--:|
| Horarios (crear/editar/publicar) | ✅ | — | — | 👁 | — |
| Panel de conflictos | ✅ | — | — | 👁 | — |
| Disponibilidad (ambientes/instructores) | ✅ | — | — | 👁 | — |
| Fichas | ✅ | — | — | 👁 | — |
| Mi horario | — | ✅ | ✅ | — | — |
| Mi disponibilidad | — | ✅ | — | — | — |
| Seguimiento de ficha | — | ✅ | — | 👁 | — |
| Notificaciones | ✅ | ✅ | ✅ | ✅ | ✅ |
| Indicadores (KPIs) | 👁 | — | — | ✅ | — |
| Usuarios/roles | — | — | — | ✅ | ✅ |
| Datos de referencia | — | — | — | 👁 | ✅ |
| Documentos/Plantillas | — | — | — | — | ✅ |
| Auditoría | — | — | — | — | ✅ |
| Parametrización | — | — | — | — | ✅ |

> El guard exacto por endpoint usa `x-required-feature` (RBAC feature+scope de iam). La UI **oculta**
> lo no permitido (no "controles deshabilitados escondidos", conforme al design-system §1). El acceso
> directo por URL a un área no permitida → **403** ([Estados globales](flows/01-auth.md)).

## Convención de build (ruta → registro en el MFE)

> El mockup adoptado es un **SPA con router por hash** (no un archivo por pantalla). Cada ruta se
> **registra en el `screens.js` de su dominio** y el `shell/` la monta según rol/RBAC. La navegación
> usa `#/<ruta>?as=<rol>`; **prohibido `href="#"`** para navegar (solo válido en toggles JS). Los
> **modales** no tienen ruta propia: se abren como estado sobre su ruta padre vía `?modal=<nombre>`.

| Ruta (hash) | MFE dueño (`mockups/app/<dominio>/screens.js`) |
|---|---|
| `#/login` · `#/forgot-password` · `#/reset-password` | `iam` |
| `#/system-states?variant=403\|404\|500\|session` | `shell` |
| `#/` (Coordinador, dashboard) | `shell` (compone `scheduling`+`academic`) |
| `#/horarios` · `#/horarios/nuevo` · `#/horarios/:id` · `#/horarios/:id/conflictos` | `scheduling` |
| `#/disponibilidad` · `#/disponibilidad/ambientes/:id` | `environment` (+`actors`) |
| `#/fichas` · `#/fichas/:id` | `academic` |
| `#/instructor/mi-horario` · `#/instructor/mi-disponibilidad` · `#/instructor/seguimiento` | `scheduling` · `actors` · `monitoring` |
| `#/mi-horario` · `#/mi-horario/sesiones/:id` · `#/notificaciones` · `#/notificaciones/:id` | `scheduling` · `monitoring` |
| `#/admin/indicadores` · `#/admin/indicadores/:ft/:kpi` · `#/admin/usuarios` · `#/admin/usuarios/:id` · `#/admin/datos-referencia` | `monitoring` · `iam` · `reference` |
| `#/backoffice/documentos` · `/:id` · `/plantillas` · `/plantillas/:id/editar` · `#/backoffice/auditoria` · `#/backoffice/parametrizacion` | `document` · `audit` · `reference` |
| `#/admin/parametrizacion` (hub) · `#/admin/parametrizacion/geografia` | `reference` (shell monta el hub) |
| `#/admin/parametrizacion/curriculo` | `academic` |
| `#/admin/parametrizacion/jornadas` | `scheduling` |
| `#/admin/parametrizacion/ambientes` | `environment` |
| `#/admin/parametrizacion/monitoreo` | `monitoring` |
| `#/admin/parametrizacion/estados` | `actors` |
| `#/admin/parametrizacion/rbac` | `iam` |

**Modales (estado `?modal=…`, sin ruta propia):** agregar/editar sesión, confirmar publicación,
resolver conflicto (coordinator); crear excepción, registrar seguimiento (instructor); crear/editar
usuario, asignar rol (admin); generar documento, detalle de auditoría, CRUD catálogos (back-office).

> La tabla completa **ruta → pantalla → rol → MFE** (53 filas) vive en
> [`mockups/app/README.md`](mockups/app/README.md); la cobertura se valida con
> `node mockups/app/tools/validate-routes.js` (53/53).
