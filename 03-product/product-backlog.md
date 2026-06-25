# Product Backlog

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Producto

## Contexto

El product backlog contiene todas las funcionalidades que se construirán en el sistema, priorizadas por su valor de negocio y dependencias técnicas. Cada ítem incluye una historia de usuario y sus criterios de aceptación.

## Prioridades

| Prioridad | Significado |
|-----------|-------------|
| **P0 (Crítica)** | Imprescindible para el MVP. El sistema no funciona sin esto. |
| **P1 (Alta)** | Muy importante, pero puede esperar a la Fase 2. |
| **P2 (Media)** | Valor añadido, para Fase 3 o posterior. |
| **P3 (Baja)** | Deseable, pero no crítico. |

---

## Backlog por fase

### 🔴 FASE 1 — MVP (P0)

| ID | Historia de Usuario | Prioridad | Criterios de Aceptación |
|----|---------------------|-----------|-------------------------|
| **HU-001** | Como administrador, quiero crear y listar macroregiones, microregiones, departamentos y municipios. | P0 | 1. Puedo crear una macroregión con nombre.<br>2. Puedo crear una microregión asociada a una macroregión.<br>3. Puedo crear un departamento y municipio.<br>4. Los listados muestran jerarquía. |
| **HU-002** | Como administrador, quiero crear y listar centros de formación y sedes (unidades institucionales). | P0 | 1. Puedo crear un centro de formación asociado a una microregión.<br>2. Puedo crear una sede asociada a un centro.<br>3. Puedo asignar ubicación (dirección, coordenadas).<br>4. Los estados (Activo/Inactivo) son funcionales. |
| **HU-003** | Como administrador, quiero gestionar catálogos base (modalidades, jornadas, estados, tipos de formación). | P0 | 1. Puedo crear un catálogo (ej. Modalidades).<br>2. Puedo agregar detalles (ej. Presencial, Virtual).<br>3. Los detalles tienen vigencia (fecha inicio/fin).<br>4. No se permiten códigos duplicados. |
| **HU-004** | Como administrador, quiero crear y listar ambientes de aprendizaje. | P0 | 1. Puedo crear un ambiente con código, nombre, tipo, capacidad, ubicación.<br>2. Puedo asociar el ambiente a un centro y sede.<br>3. Puedo cambiar el estado (Disponible, Mantenimiento, etc.). |
| **HU-005** | Como administrador, quiero crear y listar instructores. | P0 | 1. Puedo crear un instructor con nombre, email, tipo (planta/contratista).<br>2. Puedo asignar especialidades.<br>3. El instructor tiene estado (Activo/Inactivo). |
| **HU-006** | Como administrador, quiero crear y listar aprendices y fichas. | P0 | 1. Puedo crear una ficha con código, programa, jornada.<br>2. Puedo matricular un aprendiz en una ficha.<br>3. El aprendiz tiene estado (Activo, Retirado, etc.). |
| **HU-007** | Como coordinador, quiero crear y listar franjas horarias. | P0 | 1. Puedo definir una franja con día, hora inicio y hora fin.<br>2. La franja está activa para ser usada en horarios. |
| **HU-008** | Como coordinador, quiero asignar un horario: instructor + ambiente + ficha + franja horaria. | P0 | 1. Puedo seleccionar instructor, ambiente, ficha y franja.<br>2. El sistema **valida** que no haya conflicto (instructor, ambiente, ficha).<br>3. Si hay conflicto, muestra mensaje de error y no guarda.<br>4. El horario tiene estado (Programado, Cancelado, Ejecutado). |
| **HU-009** | Como coordinador, quiero consultar horarios por instructor, ambiente o ficha. | P0 | 1. Puedo filtrar horarios por instructor.<br>2. Puedo filtrar horarios por ambiente.<br>3. Puedo filtrar horarios por ficha.<br>4. Los resultados se muestran en tabla o calendario. |
| **HU-010** | Como usuario, quiero iniciar sesión con usuario y contraseña. | P0 | 1. Puedo ingresar usuario y contraseña.<br>2. Si son correctos, obtengo un token JWT.<br>3. Si son incorrectos, muestra error.<br>4. El token expira después de 8 horas. |
| **HU-011** | Como administrador, quiero asignar roles a usuarios. | P0 | 1. Puedo asignar rol (Coordinador, Instructor, Administrador).<br>2. Cada rol tiene permisos específicos. |

---

### 🟡 FASE 2 — Extensión Académica (P1)

| ID | Historia de Usuario | Prioridad | Criterios de Aceptación |
|----|---------------------|-----------|-------------------------|
| **HU-012** | Como administrador, quiero crear y listar líneas tecnológicas, redes tecnológicas y redes de conocimiento. | P1 | 1. Puedo crear una línea tecnológica.<br>2. Puedo crear una red tecnológica asociada a una línea.<br>3. Puedo crear una red de conocimiento asociada a una red tecnológica.<br>4. La jerarquía se respeta. |
| **HU-013** | Como administrador, quiero crear y listar programas de formación. | P1 | 1. Puedo crear un programa con código, nombre, tipo, modalidad, duración.<br>2. Puedo asociar el programa a una red de conocimiento.<br>3. El campo `a_la_medida` solo aplica para Complementaria.<br>4. El programa tiene vigencia (fecha inicio/fin). |
| **HU-014** | Como administrador, quiero crear y listar competencias y RAPs. | P1 | 1. Puedo crear una competencia con código, nombre, horas totales.<br>2. Puedo crear un RAP asociado a una competencia.<br>3. Un RAP es único en el catálogo maestro.<br>4. Puedo asociar competencias a programas (con horas específicas). |
| **HU-015** | Como coordinador, quiero registrar observaciones en un horario. | P1 | 1. Puedo agregar una observación a un horario.<br>2. La observación tiene texto, autor y severidad (Info, Warning, Critical).<br>3. La observación tiene estado (Abierta, En proceso, Resuelta). |
| **HU-016** | Como coordinador, quiero cancelar un horario. | P1 | 1. Puedo cambiar el estado de un horario a "Cancelado".<br>2. La cancelación queda registrada con motivo y responsable. |
| **HU-017** | Como instructor, quiero consultar mi horario asignado. | P1 | 1. Puedo ver mi horario semanal.<br>2. Puedo ver los detalles de cada sesión (ambiente, ficha, franja). |

---

### 🟢 FASE 3 — Proyectos Formativos (P2)

| ID | Historia de Usuario | Prioridad | Criterios de Aceptación |
|----|---------------------|-----------|-------------------------|
| **HU-018** | Como coordinador, quiero crear un proyecto formativo. | P2 | 1. Puedo crear un proyecto con nombre, objetivo, fechas.<br>2. Puedo asociar el proyecto a una ficha y programa.<br>3. El proyecto tiene estado (Planeación, Ejecución, Evaluación, Finalizado). |
| **HU-019** | Como coordinador, quiero definir fases y actividades de un proyecto. | P2 | 1. Puedo agregar fases a un proyecto (ej. Análisis, Diseño).<br>2. Puedo agregar actividades a una fase.<br>3. Puedo definir dependencias entre fases. |
| **HU-020** | Como instructor, quiero gestionar entregables y evidencias de un proyecto. | P2 | 1. Puedo crear entregables para una actividad.<br>2. Puedo subir evidencias (archivos) a un entregable.<br>3. Puedo aprobar o rechazar un entregable.<br>4. No se puede aprobar sin evidencia. |
| **HU-021** | Como coordinador, quiero monitorear el avance de los proyectos formativos. | P2 | 1. Puedo ver un tablero con el avance de cada proyecto.<br>2. Puedo ver el avance por aprendiz.<br>3. Puedo ver alertas de riesgo (retrasos, dependencias bloqueadas). |
| **HU-022** | Como coordinador, quiero asignar horas para revisión de proyectos. | P2 | 1. Puedo asignar un espacio horario para revisión de proyectos.<br>2. La revisión no afecta los horarios regulares. |

---

### ⚪ FASE 4 — Transversales (P3)

| ID | Historia de Usuario | Prioridad | Criterios de Aceptación |
|----|---------------------|-----------|-------------------------|
| **HU-023** | Como administrador, quiero generar reportes en PDF/Excel de horarios, ocupación y carga de instructores. | P3 | 1. Puedo exportar horarios por instructor/ambiente/ficha a PDF.<br>2. Puedo exportar reporte de ocupación de ambientes.<br>3. Puedo exportar carga horaria de instructores. |
| **HU-024** | Como usuario, quiero recibir notificaciones de cambios en mi horario. | P3 | 1. Recibo email cuando se me asigna un horario.<br>2. Recibo email cuando se cancela un horario mío.<br>3. Recibo alertas en el dashboard. |
| **HU-025** | Como administrador, quiero ver el historial de cambios (auditoría) de cualquier entidad. | P3 | 1. Puedo ver quién creó/modificó/eliminó un registro.<br>2. Puedo ver la fecha y hora de la acción.<br>3. Puedo ver el valor anterior y el nuevo valor. |

---

## Resumen de prioridades

| Prioridad | Número de HUs | Fase |
|-----------|---------------|------|
| P0 | 11 | MVP (Fase 1) |
| P1 | 6 | Extensión Académica (Fase 2) |
| P2 | 5 | Proyectos Formativos (Fase 3) |
| P3 | 3 | Transversales (Fase 4) |
| **Total** | **25** | |

---

## Referencias

- [vision.md](./vision.md) — Visión del producto
- [roadmap.md](./roadmap.md) — Hitos y fases
- [04-requirements/user-stories.md](../04-requirements/user-stories.md) — Detalle de historias de usuario
- [01-context/scope.md](../01-context/scope.md) — Alcance del proyecto