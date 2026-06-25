# Entidades y reglas de negocio

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Dominio

## Contexto

Este documento describe las entidades principales del dominio y las reglas de negocio que rigen su comportamiento. Las entidades se agrupan por módulo funcional y se detallan sus atributos clave y relaciones.

---

## Módulo 2 — Estructura Institucional

### Entidades

| Entidad | Descripción | Atributos clave |
|---------|-------------|-----------------|
| **Macroregión** | Región natural de Colombia (Andina, Caribe, Pacífica, Orinoquía, Amazonía) | `id`, `nombre`, `estado` |
| **Microregión** | Departamento o agrupación de departamentos dentro de una macroregión | `id`, `macroregion_id`, `nombre`, `estado` |
| **Departamento** | Departamento geográfico de Colombia | `id`, `microregion_id`, `nombre`, `estado` |
| **Municipio** | Municipio dentro de un departamento | `id`, `department_id`, `nombre`, `estado` |
| **Ubicación** | Dirección física con coordenadas geográficas | `id`, `municipality_id`, `dirección`, `latitud`, `longitud`, `estado` |
| **Centro de Formación** | Unidad principal encargada de la ejecución de procesos formativos | `id`, `microregion_id`, `codigo`, `nombre`, `tipo`, `estado` |
| **Unidad Institucional** | Sede, tecnoacademia o tecnoparque físico | `id`, `centro_id`, `location_id`, `unit_type_id`, `nombre`, `teléfono`, `estado` |
| **Asignación de Instructor** | Relación entre un instructor y una unidad institucional | `id`, `instructor_id`, `unit_id`, `fecha_inicio`, `fecha_fin`, `estado` |

### Reglas de negocio

- **RN-001:** Todo centro de formación debe pertenecer a una microregión.
- **RN-002:** Toda unidad institucional debe pertenecer a un centro de formación.
- **RN-003:** Una ubicación puede tener múltiples unidades institucionales.
- **RN-004:** El estado `INACTIVO` impide que la entidad sea utilizada en otros módulos.

---

## Módulo 3 — Infraestructura / Ambientes

### Entidades

| Entidad | Descripción | Atributos clave |
|---------|-------------|-----------------|
| **Ambiente** | Espacio físico o virtual donde se desarrolla la formación | `id`, `centro_id`, `sede_id`, `codigo`, `nombre`, `tipo`, `capacidad`, `estado` |
| **Recurso** | Equipo, mobiliario o herramienta asociada a un ambiente | `id`, `ambiente_id`, `codigo`, `nombre`, `marca`, `serial`, `cantidad`, `estado` |
| **Mantenimiento** | Actividad preventiva o correctiva sobre un ambiente o recurso | `id`, `ambiente_id`, `tipo`, `fecha`, `responsable`, `estado` |
| **Reserva** | Asignación temporal de un ambiente para una actividad | `id`, `ambiente_id`, `fecha_inicio`, `fecha_fin`, `motivo`, `estado` |
| **Disponibilidad** | Estado actual del ambiente (Disponible, Ocupado, Mantenimiento, Fuera de servicio) | `id`, `ambiente_id`, `estado`, `fecha_actualizacion` |

### Reglas de negocio

- **RN-005:** Un ambiente solo puede estar en un estado a la vez (Disponible, Ocupado, Mantenimiento, etc.).
- **RN-006:** Un ambiente en mantenimiento no puede ser asignado a horarios.
- **RN-007:** La capacidad del ambiente no puede ser superada por la cantidad de aprendices programados.
- **RN-008:** Los recursos en estado "Dañado" o "En mantenimiento" no pueden ser utilizados.

---

## Módulo 4 — Catálogos Base

### Entidades

| Entidad | Descripción | Atributos clave |
|---------|-------------|-----------------|
| **Catálogo** | Agrupación de valores de referencia (ej. Modalidades, Jornadas) | `id`, `codigo`, `nombre`, `descripción`, `activo` |
| **Detalle Catálogo** | Valor específico dentro de un catálogo (ej. Presencial, Virtual) | `id`, `catalogo_id`, `codigo`, `nombre`, `descripción`, `orden`, `vigencia_inicio`, `vigencia_fin`, `activo` |
| **Estado** | Estados utilizados en todo el sistema (Activo, Inactivo, Suspendido, etc.) | `id`, `codigo`, `nombre`, `descripción`, `color`, `activo` |
| **Parámetro** | Configuración global del sistema (ej. MAX_APRENDICES_FICHA = 35) | `id`, `modulo_id`, `codigo`, `nombre`, `valor`, `tipo_dato`, `editable`, `descripción` |

### Reglas de negocio

- **RN-009:** No pueden existir dos detalles con el mismo código dentro del mismo catálogo.
- **RN-010:** Los valores de catálogo con vigencia expirada no pueden ser utilizados.
- **RN-011:** Los parámetros marcados como `editable=false` no pueden ser modificados por usuarios no administradores.
- **RN-012:** Todo cambio en catálogos o parámetros debe quedar registrado en auditoría.

---

## Módulo 5 — Programas de Formación

### Entidades

| Entidad | Descripción | Atributos clave |
|---------|-------------|-----------------|
| **Línea Tecnológica** | Nivel macro de la jerarquía SENA | `id`, `codigo`, `nombre`, `descripción`, `estado` |
| **Red Tecnológica** | Agrupación intermedia dentro de una línea | `id`, `linea_id`, `codigo`, `nombre`, `descripción`, `estado` |
| **Red de Conocimiento** | Agrupación disciplinar que contiene programas | `id`, `red_tecnologica_id`, `codigo`, `nombre`, `descripción`, `estado` |
| **Programa de Formación** | Oferta educativa con diseño curricular aprobado | `id`, `red_conocimiento_id`, `tipo_formacion_id`, `modalidad_id`, `codigo`, `nombre`, `version`, `duracion_horas`, `a_la_medida`, `vigencia_inicio`, `vigencia_fin`, `estado` |
| **Competencia** | Capacidad técnica o transversal que el aprendiz debe desarrollar | `id`, `tipo_competencia_id`, `codigo`, `nombre`, `descripción`, `horas_totales`, `estado` |
| **Resultado de Aprendizaje (RAP)** | Logro medible al finalizar una competencia | `id`, `tipo_resultado_id`, `codigo`, `nombre`, `descripción`, `estado` |
| **ProgramaCompetencia** | Relación entre programa y competencia (con horas específicas) | `id`, `programa_id`, `competencia_id`, `orden_malla`, `horas_en_programa`, `estado` |
| **CompetenciaResultado** | Relación entre competencia y RAP (con orden y horas) | `id`, `competencia_id`, `resultado_id`, `orden_resultado`, `horas_resultado`, `estado` |

### Reglas de negocio

- **RN-013:** Un programa de formación **Titulado** no puede ser `a_la_medida` (solo aplica para Complementaria).
- **RN-014:** Un instructor está habilitado por **competencia completa**, no por RAP individual.
- **RN-015:** Los RAPs son únicos en el catálogo maestro (no se duplican).
- **RN-016:** La competencia asignada a un bloque horario debe pertenecer al programa de la ficha.
- **RN-017:** La jerarquía Línea → Red Tecnológica → Red de Conocimiento → Programa debe respetarse.

---

## Módulo 7 — Actores

### Entidades

| Entidad | Descripción | Atributos clave |
|---------|-------------|-----------------|
| **Instructor** | Persona que orienta la formación. Puede ser planta o contratista. | `id`, `nombre`, `email`, `tipo` (planta/contratista), `especialidades`, `estado` |
| **Aprendiz** | Persona que recibe formación. Está matriculado en una ficha. | `id`, `nombre`, `documento`, `email`, `ficha_id`, `estado` |
| **Directivo** | Persona con rol de coordinación o dirección. | `id`, `nombre`, `email`, `rol`, `centro_id`, `estado` |
| **Empresa** | Empresa donde el aprendiz realiza etapa productiva. | `id`, `nombre`, `nit`, `dirección`, `contacto`, `estado` |
| **Etapa Productiva** | Período de práctica del aprendiz en una empresa. | `id`, `aprendiz_id`, `empresa_id`, `fecha_inicio`, `fecha_fin`, `estado` |

### Reglas de negocio

- **RN-018:** Un instructor debe tener al menos una especialidad registrada.
- **RN-019:** Un instructor en estado `INACTIVO` no puede ser asignado a horarios.
- **RN-020:** Un aprendiz debe estar matriculado en una ficha para aparecer en horarios.
- **RN-021:** Solo los instructores con habilitación en una competencia pueden ser asignados a bloques de esa competencia.

---

## Módulo 8 — Horarios y Módulo 11 — Motor de Asignación

### Entidades

| Entidad | Descripción | Atributos clave |
|---------|-------------|-----------------|
| **Franja Horaria** | Bloque de tiempo definido por día, hora inicio y hora fin. | `id`, `dia_semana`, `hora_inicio`, `hora_fin`, `activo` |
| **Horario** | Asignación de instructor + ambiente + ficha + franja horaria. | `id`, `instructor_id`, `ambiente_id`, `ficha_id`, `franja_id`, `fecha`, `estado` (programado, cancelado, ejecutado) |
| **Asignación** | Registro histórico de asignaciones (para trazabilidad). | `id`, `horario_id`, `instructor_id`, `ambiente_id`, `ficha_id`, `fecha_asignacion`, `responsable` |
| **Conflicto** | Detección de cruces de horario (instructor, ambiente o ficha). | `id`, `horario_id`, `tipo_conflicto` (instructor, ambiente, ficha), `descripción`, `fecha_detección` |
| **Sesión de Clase** | Ejecución real de una sesión de formación. | `id`, `horario_id`, `fecha_ejecucion`, `hora_inicio_real`, `hora_fin_real`, `estado` (realizada, cancelada, pendiente) |

### Reglas de negocio (CRÍTICAS)

- **RN-022:** Un instructor no puede estar asignado a dos horarios que se solapen en el tiempo.
- **RN-023:** Un ambiente no puede estar asignado a dos horarios que se solapen en el tiempo.
- **RN-024:** Una ficha no puede tener dos horarios que se solapen en el tiempo.
- **RN-025:** No se pueden asignar horarios a instructores, ambientes o fichas en estado `INACTIVO`.
- **RN-026:** Los cambios retroactivos en horarios requieren aprobación de coordinación.
- **RN-027:** Una sesión de clase ya ejecutada no puede ser modificada (solo se puede añadir observación).

---

## Módulo 9 — Proyectos Formativos y Monitoreo

### Entidades (resumen)

| Entidad | Descripción | Atributos clave |
|---------|-------------|-----------------|
| **Proyecto Formativo** | Proyecto que integra competencias y RAPs en un contexto real. | `id`, `programa_id`, `ficha_id`, `nombre`, `objetivo_general`, `fecha_inicio`, `fecha_fin`, `estado` |
| **Fase** | Etapa del proyecto (Análisis, Diseño, Construcción, Pruebas, Implantación, Evaluación). | `id`, `proyecto_id`, `nombre`, `orden`, `descripción`, `fecha_inicio`, `fecha_fin` |
| **Actividad** | Tarea específica dentro de una fase. | `id`, `fase_id`, `nombre`, `descripción`, `fecha_limite`, `estado` |
| **Entregable** | Producto o resultado de una actividad. | `id`, `actividad_id`, `nombre`, `descripción`, `url_evidencia`, `estado` (pendiente, entregado, aprobado) |
| **Evidencia** | Soporte digital de un entregable. | `id`, `entregable_id`, `tipo` (conocimiento, desempeño, producto), `url`, `fecha_subida` |
| **Dependencia** | Relación entre fases (una fase depende de otra). | `id`, `fase_origen_id`, `fase_destino_id`, `tipo` |

### Reglas de negocio

- **RN-028:** Una fase solo puede iniciarse si sus dependencias han sido completadas.
- **RN-029:** Un entregable no puede ser aprobado sin evidencia asociada.
- **RN-030:** El avance del proyecto se calcula como porcentaje de fases/actividades completadas sobre el total.

---

## Módulo 1 — Seguridad y Acceso (Transversal)

### Entidades

| Entidad | Descripción | Atributos clave |
|---------|-------------|-----------------|
| **Usuario** | Persona con acceso al sistema (Coordinador, Instructor, Administrador). | `id`, `nombre`, `email`, `password_hash`, `activo` |
| **Rol** | Conjunto de permisos (COORDINADOR, INSTRUCTOR, ADMINISTRADOR). | `id`, `nombre`, `descripción` |
| **Permiso** | Acción específica que puede realizar un rol (ej. CREAR_HORARIO). | `id`, `nombre`, `descripción` |
| **Sesión** | Registro de login de un usuario. | `id`, `usuario_id`, `fecha_inicio`, `fecha_fin`, `ip_origen` |
| **Token** | JWT generado para autenticación. | `id`, `usuario_id`, `token`, `fecha_expiracion`, `revocado` |

### Reglas de negocio

- **RN-031:** Solo usuarios autenticados pueden acceder al sistema.
- **RN-032:** Cada usuario tiene al menos un rol asignado.
- **RN-033:** Los permisos se asignan a roles, no a usuarios individuales.
- **RN-034:** Los tokens JWT expiran después de 8 horas y deben renovarse.
- **RN-035:** Todas las acciones críticas (crear, modificar, eliminar) se registran en auditoría.

---

## Resumen de reglas de negocio críticas (para el motor de horarios)

| ID | Regla | Afecta a |
|----|-------|----------|
| RN-022 | Un instructor no puede estar asignado a dos horarios que se solapen en el tiempo. | Horarios |
| RN-023 | Un ambiente no puede estar asignado a dos horarios que se solapen en el tiempo. | Horarios |
| RN-024 | Una ficha no puede tener dos horarios que se solapen en el tiempo. | Horarios |
| RN-025 | No se pueden asignar horarios a instructores, ambientes o fichas inactivos. | Horarios |
| RN-027 | Una sesión de clase ya ejecutada no puede ser modificada. | Ejecución |
| RN-006 | Un ambiente en mantenimiento no puede ser asignado a horarios. | Ambientes |
| RN-019 | Un instructor en estado INACTIVO no puede ser asignado a horarios. | Actores |
| RN-016 | La competencia asignada a un bloque horario debe pertenecer al programa de la ficha. | Académico |
| RN-013 | Un programa Titulado no puede ser `a_la_medida`. | Programas |
| RN-014 | Un instructor está habilitado por competencia completa, no por RAP. | Programas |

---

## Referencias

- [domain-map.md](./domain-map.md)
- [domain-events.md](./domain-events.md)
- [01-context/glossary.md](../01-context/glossary.md)
- [09-microservices/](../09-microservices/)