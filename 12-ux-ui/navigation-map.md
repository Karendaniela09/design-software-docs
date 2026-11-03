# Mapa de Navegación

> Estado: 🟡 En progreso | Última actualización: 2026-08-01
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: UX-UI

Estructura de navegación **prevista** de la plataforma SENA — Gestión de Horarios, organizada por rol de negocio.

> **Estado real del proyecto:** aún **no existe aplicación**; hoy solo está construida la capa de datos. Este mapa describe la **jerarquía de navegación planificada** derivada de los flujos de negocio y el alcance del MVP. Las **pantallas concretas están pendientes** de la fase de diseño (ver [wireframes.md](./wireframes.md)); aquí no se documenta ninguna pantalla como si ya existiera.

## Roles y punto de entrada

Roles definidos en IAM: `COORDINATOR`, `INSTRUCTOR`, `LEARNER`, `ADMIN` ([discovery M1](../03-product/discovery-brief.md)). Tras autenticarse (`POST /auth/login` → JWT), cada rol aterriza en un espacio distinto. Una misma cuenta ve **solo** la navegación de su rol.

## Áreas de navegación por rol (previstas)

### Coordinador Académico (rol central del MVP)

Responsable de crear, validar y publicar horarios. Navegación prevista:

- **Inicio / resumen** — fichas activas del centro, horarios en borrador, conflictos pendientes.
- **Horarios**
  - Lista de horarios por ficha y estado (BORRADOR / EN_REVISIÓN / PUBLICADO).
  - Crear / editar horario → agregar sesiones (ficha + instructor + ambiente + franja + fecha).
  - Validar conflictos → panel de conflictos.
  - Publicar / versionar.
- **Ambientes** (antes "Disponibilidad") — consulta de ambientes e instructores disponibles por franja.
- **Fichas** — consulta de fichas del centro y su programa.

### Instructor

Consulta su carga y (en evolución) su disponibilidad.

- **Mi horario** — vista semanal de sus sesiones de clase.
- **Mi disponibilidad** — gestión de franjas disponibles (según alcance por fase).
- **Seguimiento** — registro de sesiones de seguimiento de ficha (asistencia, avance).

### Aprendiz

Consulta de su horario vigente.

- **Mi horario** — vista semanal de clases de su ficha.
- **Notificaciones** — avisos de cambios de horario.

### Administrador de Centro

Visibilidad y métricas.

- **Panel de indicadores** — utilización de ambientes, carga de instructores, KPIs de seguimiento ([discovery M9](../03-product/discovery-brief.md)).
- **Administración** — gestión de datos de referencia y usuarios del centro (según permisos).

## Diagrama de navegación previsto (alto nivel)

```
                         [ Login / Autenticación ]
                                    │ JWT (rol)
        ┌───────────────┬───────────┴───────────┬────────────────┐
        ▼               ▼                       ▼                ▼
   COORDINADOR      INSTRUCTOR              APRENDIZ           ADMIN
   ───────────      ──────────              ────────          ─────
   Inicio           Mi horario              Mi horario        Indicadores
   Horarios ─┐      Mi disponibilidad       Notificaciones    Administración
   Ambientes │      Seguimiento
   Fichas    │
             └─▶ Crear → Sesiones → Validar (conflictos) → Publicar → Versionar
```

## Reglas de navegación

1. **Segmentación por rol:** el JWT determina las áreas visibles; no se muestran rutas fuera del rol. Desde HU-SHELL-019 el menú del shell se deriva de `me.features` (feature requerido por ítem) y de `me.actor_type` para los ítems personales "Mi …", y se agrupa en secciones; ya no se deriva de `me.modules` (criterio E2 de HU-001, reemplazado). Detalle y tabla por ítem en [visual-spec.md](./visual-spec.md) §4.
2. **El estado guía el flujo:** desde un horario en BORRADOR se llega a Validar y Publicar; un PUBLICADO es de solo lectura y ofrece "crear nueva versión".
3. **Rutas críticas cortas:** el flujo Crear → Validar → Publicar es el camino principal del coordinador y debe minimizar saltos.
4. **Ámbito por centro:** el coordinador opera dentro de su centro de formación ([discovery M2](../03-product/discovery-brief.md)).

## Pendiente (fase de diseño de la app)

- [ ] Definir el árbol de rutas/URLs concreto.
- [ ] Especificar breadcrumbs y navegación secundaria por área.
- [ ] Validar el mapa con usuarios reales (coordinadores) antes de wireframear.

## Referencias

- [wireframes.md](./wireframes.md) · [design-system.md](./design-system.md)
- [discovery-brief.md](../03-product/discovery-brief.md) · [overview.md (flujos)](../05-architecture/overview.md#flujos-principales)
