## Lenguaje ubicuo por dominio

El lenguaje ubicuo es el conjunto de términos que todos los equipos (desarrollo, producto, negocio) utilizan para referirse a los conceptos del sistema. Estos términos deben ser consistentes en todo el código, la documentación y las conversaciones.

---

### Gestión Institucional

| Término | Descripción breve |
|---------|-------------------|
| **Macroregión** | Región natural de Colombia (Andina, Caribe, Pacífica, Orinoquía, Amazonía) |
| **Microregión** | Departamento o agrupación de departamentos dentro de una macroregión |
| **Departamento** | División político-administrativa de Colombia |
| **Municipio** | División administrativa dentro de un departamento |
| **Centro de Formación** | Unidad principal donde se ejecutan los procesos formativos |
| **Sede** | Unidad institucional física (edificio, tecnoacademia, tecnoparque) |
| **Unidad Institucional** | Entidad física donde se desarrollan actividades académicas |
| **Ubicación** | Dirección física con coordenadas geográficas |
| **Catálogo** | Agrupación de valores de referencia (ej. modalidades, jornadas) |
| **Estado** | Valor que define el ciclo de vida de un registro (Activo, Inactivo, etc.) |
| **Parámetro** | Configuración global del sistema (ej. capacidad máxima) |
| **Jornada** | Período del día en que se imparte formación (Mañana, Tarde, Noche) |
| **Modalidad** | Forma de ofrecer un programa (Presencial, Virtual, A Distancia, Mixta) |

---

### Gestión Académica

| Término | Descripción breve |
|---------|-------------------|
| **Programa de Formación** | Oferta educativa con código, nombre, nivel y diseño curricular |
| **Competencia** | Capacidad técnica o transversal que el aprendiz debe desarrollar |
| **RAP** | Resultado de Aprendizaje — logro medible al finalizar una competencia |
| **Línea Tecnológica** | Nivel más alto de la jerarquía de conocimiento del SENA |
| **Red Tecnológica** | Agrupación técnica intermedia dentro de una línea tecnológica |
| **Red de Conocimiento** | Agrupación disciplinar que contiene programas de formación |
| **Ficha** | Grupo de aprendices que cursan un mismo programa y jornada |
| **Oferta** | Programas disponibles en un centro de formación |
| **Tipo de Formación** | Clasificación: Titulada, Complementaria, Especialización Tecnológica |
| **Diseño Curricular** | Estructura de competencias, RAPs y horas de un programa |

---

### Gestión de Recursos

| Término | Descripción breve |
|---------|-------------------|
| **Ambiente** | Espacio físico o virtual donde se desarrolla la formación |
| **Inventario** | Conjunto de recursos disponibles en un ambiente |
| **Recurso** | Equipo, mobiliario o herramienta (computador, proyector, silla) |
| **Mantenimiento** | Actividad preventiva o correctiva sobre ambientes o recursos |
| **Reserva** | Asignación temporal de un ambiente para una actividad |
| **Disponibilidad** | Estado actual del ambiente (Disponible, Ocupado, Mantenimiento) |
| **Instructor** | Persona que orienta la formación (planta o contratista) |
| **Aprendiz** | Persona que recibe formación en una ficha |
| **Directivo** | Persona con rol de coordinación o dirección |
| **Empresa** | Entidad donde el aprendiz realiza la etapa productiva |
| **Etapa Productiva** | Período de práctica del aprendiz en una empresa |

---

### Gestión de Horarios

| Término | Descripción breve |
|---------|-------------------|
| **Horario** | Asignación de instructor + ambiente + ficha + franja horaria |
| **Franja Horaria** | Bloque de tiempo definido por día, hora inicio y hora fin |
| **Asignación** | Registro histórico de una asignación de horario |
| **Sesión de Clase** | Ejecución real de una sesión de formación |
| **Conflicto** | Cruce de horario (instructor, ambiente o ficha en dos lugares a la vez) |
| **Observación** | Registro de novedades sobre un horario (ej. "Instructor ausente") |
| **Incidencia** | Problema reportado que afecta la ejecución del horario |

---

### Gestión de Proyectos Formativos

| Término | Descripción breve |
|---------|-------------------|
| **Proyecto Formativo** | Proyecto que integra competencias y RAPs en un contexto real |
| **Fase** | Etapa del proyecto (Análisis, Diseño, Construcción, Pruebas) |
| **Actividad** | Tarea específica dentro de una fase |
| **Entregable** | Producto o resultado de una actividad |
| **Evidencia** | Soporte digital de un entregable (PDF, imagen, código) |
| **Dependencia** | Relación entre fases (una fase depende de otra) |
| **Hito** | Punto de control importante en el avance del proyecto |

---

### Transversales / Soporte

| Término | Descripción breve |
|---------|-------------------|
| **Usuario** | Persona con acceso al sistema (Coordinador, Instructor, Administrador) |
| **Rol** | Conjunto de permisos (COORDINADOR, INSTRUCTOR, ADMINISTRADOR) |
| **Permiso** | Acción específica que puede realizar un rol |
| **Token** | JWT generado para autenticación |
| **Sesión** | Registro de login de un usuario |
| **Auditoría** | Registro inmutable de todas las acciones críticas |
| **Notificación** | Mensaje enviado a un usuario (email, app, dashboard) |
| **Alerta** | Notificación de alto impacto (ej. conflicto de horario crítico) |

---

## Referencias

- [entities-and-rules.md](./entities-and-rules.md) — Detalle de entidades y reglas de negocio
- [domain-events.md](./domain-events.md) — Eventos de dominio
- [09-microservices/service-catalog.md](../09-microservices/service-catalog.md) — Catálogo de microservicios
- [01-context/glossary.md](../01-context/glossary.md) — Glosario general del proyecto