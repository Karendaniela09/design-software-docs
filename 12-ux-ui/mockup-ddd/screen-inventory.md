<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: inventario maestro de pantallas del mockup (2 lentes: experiencia y build/MFE)
fase: diseño (UX/UI)
estado: draft
dependencias_entrada: mockup-ddd/flows/*.md; micro-frontends.md
consumidores_siguientes: generación del mockup (por pantalla), construcción del frontend (por MFE)
tldr: Índice único de las ~53 pantallas/modales, mapeadas a su MFE dueño, rol y estado de generación. Doble lente: por flujo (experiencia) y por micro-frontend (build).
decisiones_clave: la unidad de experiencia es el flujo; la unidad de build es el MFE; el detalle por pantalla (endpoint/HU/tabla) vive en flows/*.md
halts_registrados: ninguno
-->

# Inventario maestro de pantallas del mockup

> **ESTADO: PRELIMINAR (v0).** 53 pantallas/modales. El detalle de cada una (endpoints, campos,
> layout, PROMPT STITCH, HU) está en su archivo de `flows/`. Aquí: el índice + MFE dueño + estado.

**Leyenda estado:** ✅ generado (mockup hecho) · ⬜ pendiente de generar.

## Lente 1 — por FLUJO (experiencia)

### 01-auth (transversal)
| # | Pantalla | Rol | MFE | Estado |
|---|---|---|---|:--:|
| 1 | Login | anónimo | iam-mfe | ✅ |
| 2 | Recuperar contraseña | anónimo | iam-mfe | ✅ |
| 3 | Nueva contraseña (reset) | anónimo | iam-mfe | ✅ |
| 4 | App Shell (marco por rol) | todos | shell-host | ✅ |
| 5 | Panel de notificaciones (campana) | todos | shell-host + notification-service | 🟡 Bloqueado: falta GET /notifications |
| 6 | Estados globales (403/404/500/sesión) | todos | shell-host | ✅ |

### 02-coordinador (núcleo)
| # | Pantalla | Tipo | MFE | Estado |
|---|---|---|---|:--:|
| 1 | Dashboard / Inicio | pantalla | shell-host + scheduling + academic | ✅ |
| 2 | Horarios (lista) | lista | scheduling-mfe | ✅ |
| 3 | Detalle de horario | detalle | scheduling-mfe | ✅ |
| 4 | Crear / editar horario | form | scheduling-mfe | ✅ |
| 5 | Modal: Agregar/editar sesión | modal | scheduling-mfe | ✅ |
| 6 | Modal: Confirmar publicación | modal | scheduling-mfe | ✅ |
| 7 | Panel de conflictos | lista | scheduling-mfe | ✅ |
| 8 | Modal: Resolver conflicto | modal | scheduling-mfe | ✅ |
| 9 | Disponibilidad | consulta | environment-mfe + actors-mfe | ✅ |
| 10 | Detalle de ambiente / disponibilidad | detalle | environment-mfe | ✅ |
| 11 | Fichas | lista | academic-mfe | ✅ |
| 12 | Detalle de ficha | detalle | academic-mfe | ✅ |

### 03-instructor
| # | Pantalla | Tipo | MFE | Estado |
|---|---|---|---|:--:|
| 1 | Mi horario (semana) | calendario | scheduling-mfe | ✅ |
| 2 | Detalle de sesión | detalle | scheduling-mfe | ✅ |
| 3 | Mi disponibilidad | lista | actors-mfe | ✅ |
| 4 | Modal: Crear excepción de disponibilidad | modal/form | actors-mfe | ✅ |
| 5 | Seguimiento de ficha | lista | monitoring-mfe | ✅ |
| 6 | Form: Registrar seguimiento | form | monitoring-mfe | ✅ |

### 04-aprendiz (mobile-first)
| # | Pantalla | Tipo | MFE | Estado |
|---|---|---|---|:--:|
| 1 | Mi horario (semana) | calendario | scheduling-mfe | ✅ |
| 2 | Notificaciones | lista | shell-host + notification-service | 🟡 Bloqueado: falta GET /notifications |
| 3 | Detalle de clase/sesión | detalle | scheduling-mfe | ✅ |
| 4 | Detalle de notificación | detalle | shell-host + notification-service | ✅ |

### 05-administrador
| # | Pantalla | Tipo | MFE | Estado |
|---|---|---|---|:--:|
| 1 | Panel de indicadores (KPIs) | dashboard | monitoring-mfe | ✅ |
| 2 | Drill-down de KPI | detalle | monitoring-mfe | ✅ |
| 3 | Administración — Usuarios | lista | iam-mfe | ✅ |
| 4 | Form: Crear/editar usuario | form | iam-mfe | ✅ |
| 5 | Detalle de usuario | detalle | iam-mfe | ✅ |
| 6 | Modal: Asignar/revocar rol | modal | iam-mfe | ✅ |
| 7 | Administración — Datos de referencia | lista | reference-mfe | ✅ |
| 8 | Form: Editar catálogo/valor/parámetro | form | reference-mfe | ✅ |

### 06-backoffice
| # | Pantalla | Tipo | MFE | Estado |
|---|---|---|---|:--:|
| 1 | Documentos | lista | document-mfe | ✅ |
| 2 | Plantillas de documento | lista | document-mfe | ✅ |
| 3 | Auditoría | lista | audit-mfe | ✅ |
| 4 | Parametrización / catálogos | lista | reference-mfe | ✅ |
| 5 | Detalle de documento + versiones | detalle | document-mfe | ✅ |
| 6 | Modal: Generar documento | modal/form | document-mfe | ✅ |
| 7 | Editor / Preview de plantilla | editor | document-mfe | ✅ |
| 8 | Modal: Detalle de auditoría | modal | audit-mfe | ✅ |
| 9 | Formularios CRUD catálogos/parámetros | form | reference-mfe | ✅ |

### 07-parametrización (director + soporte)
> Configuración de catálogos y datos maestros que los flujos operativos exigen como prerequisito
> (currículo → fichas; jornadas → horarios; tipos de ambiente → ambientes; catálogos → KPIs;
> máquina de estados de actores; geografía institucional; roles/permisos RBAC).

| # | Pantalla | Rol | MFE | Estado |
|---|---|---|---|:--:|
| 1 | Hub de parametrización | director + soporte | reference-mfe (shell) | ✅ |
| 2 | Currículo académico | director + soporte | academic-mfe | ✅ |
| 3 | Jornadas / franjas horarias | director + soporte | scheduling-mfe | ✅ |
| 4 | Tipos de ambiente e inventario | director + soporte | environment-mfe | ✅ |
| 5 | Catálogos de monitoreo (KPI/alertas) | director + soporte | monitoring-mfe | ✅ |
| 6 | Estados de actores | director + soporte | actors-mfe | ✅ |
| 7 | Geografía institucional | director + soporte | reference-mfe | ✅ |
| 8 | RBAC — roles y permisos | director + soporte | iam-mfe | ✅ |

## Lente 2 — por MICRO-FRONTEND (build)

| MFE | # pantallas (dueño/compone) | Pantallas |
|---|:--:|---|
| **shell-host** | 4 | App Shell, Panel de notificaciones, Estados globales, Dashboard (compone) |
| **iam-mfe** | 8 | Login, Recuperar, Nueva contraseña, Usuarios, Crear/editar usuario, Detalle usuario, Asignar rol, Param: RBAC roles/permisos |
| **scheduling-mfe** | ~12 | Horarios, Detalle horario, Crear/editar, Modal sesión, Confirmar publicación, Panel conflictos, Resolver conflicto, Mi horario (instr/aprendiz), Detalle sesión/clase, Param: Jornadas/franjas |
| **academic-mfe** | 3 | Fichas, Detalle de ficha, Param: Currículo académico |
| **environment-mfe** | 3 | Disponibilidad (ambientes), Detalle de ambiente, Param: Tipos de ambiente e inventario |
| **actors-mfe** | 4 | Disponibilidad (instructores), Mi disponibilidad, Crear excepción, Param: Estados de actores |
| **document-mfe** | 5 | Documentos, Plantillas, Detalle+versiones, Generar, Editor plantilla |
| **monitoring-mfe** | 5 | KPIs, Drill-down, Seguimiento, Registrar seguimiento, Param: Catálogos de monitoreo |
| **audit-mfe** | 2 | Auditoría, Detalle de auditoría |
| **reference-mfe** | 6 | Datos de referencia, Editar catálogo, Parametrización, CRUD catálogos, Param: Hub de parametrización, Param: Geografía institucional |

> Totales: **53 pantallas/modales**, **10 unidades de build** (9 MFE de dominio + shell-host).
> Generadas hasta ahora: **53**. Pendientes de diseñar: **4** (ver la sección siguiente).

## Pantallas pendientes de diseñar (HU en el tablero)

Las cuatro pantallas siguientes de `actors-mfe` ya tienen HU `[FRONTEND]` en el tablero y su backend terminado, pero **no tienen mockup**: no cuentan en el total de 53. Quedan referenciadas aquí para cumplir el DoR de cada HU (pantalla listada); su mockup (detalle en `flows/`) se completa en una iteración de diseño posterior y no bloquea el merge del código.

| # | Pantalla | Rol | MFE | HU | Backend | Estado |
|---|---|---|---|---|---|:--:|
| 1 | Bitácora de actividad (pestaña del perfil de instructor y de aprendiz) | coordinador + soporte | actors-mfe | HU-ACT-025 (docs#379) | HU-ACT-005 (docs#189) | ⬜ |
| 2 | Aprendices activos por ficha | coordinador + instructor | actors-mfe | HU-ACT-026 (docs#380) | HU-ACT-012 (docs#196) | ⬜ |
| 3 | Reportes de seguimiento (seguimiento de aprendices y carga de instructores) | coordinador académico + instructor de seguimiento | actors-mfe | HU-ACT-027 (docs#381) | HU-ACT-011 (docs#195) | ⬜ |
| 4 | Planes de mejoramiento de instructor y aprendiz (plan individual del actor; el plan de ficha es de `monitoring-mfe`, HU-MON-008) | coordinador + instructor de seguimiento | actors-mfe | HU-ACT-028 (docs#382) | HU-ACT-010 (docs#194) | ⬜ |

## Prioridad de generación (MVP primero)
1. Completar **Coordinador** (núcleo): Crear/editar horario → Panel de conflictos → Resolver conflicto → Disponibilidad → Fichas.
2. **Instructor** y **Aprendiz** (consumo del horario).
3. **Administrador** y **back-office**.
