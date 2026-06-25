# Roadmap del producto

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Producto

## Contexto

El roadmap define las fases de desarrollo del producto, los hitos clave y la evolución planificada. El enfoque es entregar valor de forma incremental, priorizando las funcionalidades que resuelven los problemas más críticos primero.

## Fases del producto

### Fase 1 — MVP (Mínimo Producto Viable)
**Duración estimada:** 4-6 semanas

**Objetivo:** Entregar un sistema funcional que permita la programación de horarios con validación de conflictos (instructor, ambiente, ficha).

| Entregable | Módulos involucrados | Criterio de aceptación |
|------------|----------------------|------------------------|
| Estructura institucional y catálogos | M2, M4 | CRUD de macroregiones, microregiones, centros, sedes. Catálogos de estados, jornadas, modalidades. |
| Gestión de ambientes y actores | M3, M7 | CRUD de ambientes (capacidad, ubicación). CRUD de instructores y aprendices (tipo, especialidades). |
| Motor de horarios | M8, M11 | Asignación de instructor + ambiente + ficha + franja horaria. Validación de cruces (no doble asignación). |
| Autenticación básica | M1 | Login con JWT. Roles: Coordinador, Instructor, Administrador. |
| Interfaz de usuario | Frontend | Vista de horarios por instructor/ambiente/ficha. Formularios de creación. |

**Criterio de éxito:** El sistema no permite asignar el mismo instructor, ambiente o ficha a dos bloques horarios que se solapen.

---

### Fase 2 — Extensión Académica
**Duración estimada:** 3-4 semanas

**Objetivo:** Agregar la gestión académica (programas, competencias, RAPs) y las observaciones/incidencias.

| Entregable | Módulos involucrados | Criterio de aceptación |
|------------|----------------------|------------------------|
| Programas y oferta | M5, M6 | CRUD de programas, competencias, RAPs. Relación programa → ficha. |
| Observaciones e incidencias | M12 | Registro de novedades (ej: "Instructor ausente", "Ambiente dañado") sobre horarios. |
| Mejoras en horarios | M8, M11 | Filtros avanzados de búsqueda. Vista de horarios por programa o competencia. |

**Criterio de éxito:** Los coordinadores pueden asociar horarios a competencias y registrar incidencias.

---

### Fase 3 — Proyectos Formativos y Monitoreo
**Duración estimada:** 4-5 semanas

**Objetivo:** Gestionar proyectos formativos, sus fases, dependencias, entregables y el monitoreo de avance.

| Entregable | Módulos involucrados | Criterio de aceptación |
|------------|----------------------|------------------------|
| Proyectos formativos | M9, M13 | Gestión de proyectos: fases, actividades, entregables, dependencias. |
| Coordinación y evaluación | M14 | Asignación de horas para revisión de proyectos. |
| Monitoreo y KPIs | M9 (parte) | Tableros de avance, alertas de riesgo y reportes básicos. |

**Criterio de éxito:** Los instructores pueden gestionar proyectos formativos y monitorear el avance de los aprendices.

---

### Fase 4 — Notificaciones, Trazabilidad y Reportes
**Duración estimada:** 2-3 semanas

**Objetivo:** Completar las funcionalidades transversales de notificaciones, auditoría y reportes avanzados.

| Entregable | Módulos involucrados | Criterio de aceptación |
|------------|----------------------|------------------------|
| Notificaciones | M15 | Alertas por email y en dashboard para cambios de horario, incidencias, etc. |
| Auditoría completa | M1 (parte) | Registro inmutable de todas las acciones críticas. |
| Reportes avanzados | M10 (parte) | Exportación a PDF/Excel de horarios, ocupación de ambientes, carga de instructores. |

**Criterio de éxito:** El sistema tiene trazabilidad completa y genera reportes operativos.

---

## Hitos clave

| Hito | Fecha estimada | Descripción |
|------|----------------|-------------|
| **Hito 1** | Fin de semana 4 | MVP funcional con horarios y validación de conflictos. |
| **Hito 2** | Fin de semana 8 | Extensión académica completa (programas, competencias, observaciones). |
| **Hito 3** | Fin de semana 13 | Proyectos formativos y monitoreo operativo. |
| **Hito 4** | Fin de semana 16 | Sistema completo con notificaciones, auditoría y reportes. |

## Dependencias externas

- **Disponibilidad de datos:** Se requiere acceso a los datos de SOFIA Plus (fichas, programas, aprendices) para pruebas de integración.
- **Aprobación de arquitectura:** La definición final de microservicios debe ser aprobada antes del desarrollo.
- **Infraestructura:** Se requiere un servidor o entorno Docker para despliegue.

## Referencias

- [vision.md](./vision.md) — Visión del producto
- [product-backlog.md](./product-backlog.md) — Backlog priorizado
- [01-context/scope.md](../01-context/scope.md) — Alcance del proyecto