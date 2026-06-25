# Alcance del proyecto

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Producto

## En alcance (MVP)

El MVP incluirá las siguientes funcionalidades:

### 1. Gestión institucional (Módulo 2)
- CRUD de macroregiones, microregiones, departamentos, municipios.
- CRUD de centros de formación y sedes (unidades institucionales).
- Asociación de ubicaciones (dirección, coordenadas).

### 2. Catálogos base (Módulo 4)
- Gestión de estados (Activo, Inactivo, Suspendido, Finalizado).
- Gestión de modalidades de formación (Presencial, Virtual, A Distancia, Mixta).
- Gestión de jornadas académicas (Mañana, Tarde, Noche, Fin de Semana).
- Gestión de tipos de formación (Titulada, Complementaria, Especialización Tecnológica, etc.).
- Gestión de líneas tecnológicas y redes de conocimiento.

### 3. Ambientes e infraestructura (Módulo 3)
- CRUD de ambientes de aprendizaje (código, nombre, tipo, ubicación, capacidad, estado).
- CRUD de inventario de recursos (equipos, mobiliario, estado, cantidad).
- Registro de disponibilidad y estados de ambientes.
- Registro de mantenimientos básicos.

### 4. Actores (Módulo 7)
- CRUD de instructores (nombre, email, tipo: planta/contratista, especialidades, estado).
- CRUD de aprendices (nombre, documento, email, ficha asociada, estado).
- CRUD de directivos y coordinadores.

### 5. Horarios y motor de asignación (Módulos 8 y 11) — **CORE DEL MVP**
- Definición de franjas horarias (día, hora inicio, hora fin).
- Asignación de: instructor + ambiente + ficha + franja horaria.
- **Validación automática de conflictos**:
  - Un instructor no puede estar en dos ambientes a la misma hora.
  - Un ambiente no puede tener dos fichas a la misma hora.
  - Una ficha no puede tener dos instructores a la misma hora.
- Consulta de disponibilidad de ambientes e instructores.

### 6. Observaciones e incidencias (Módulo 12)
- Registro de observaciones sobre un horario (ej. "Instructor ausente", "Ambiente dañado").
- Clasificación por severidad (Info, Warning, Critical).
- Seguimiento de estado (abierta, en proceso, resuelta).

### 7. Autenticación y seguridad (Módulo 1) — **MÍNIMO**
- Autenticación con JWT.
- Roles básicos: Coordinador, Instructor, Administrador.
- Control de acceso a endpoints por rol.

## Fuera de alcance (MVP)

- Integración en tiempo real con SOFIA Plus (se hará por lotes o manual en MVP).
- Gestión de proyectos formativos (fases, dependencias, entregables).
- Evaluación y calificación de proyectos formativos.
- Notificaciones avanzadas (email, SMS, push).
- Reportes complejos o dashboards analíticos.
- Aplicación móvil nativa (solo web responsive).
- Importación/exportación masiva de horarios (Excel/CSV) — manual en MVP.

## Supuestos

- Los datos de instructores, aprendices, fichas y programas se cargarán manualmente en el MVP (o se importarán desde SOFIA Plus mediante un proceso manual).
- Las reglas de negocio (ej. "un instructor no puede tener más de X horas semanales") se validarán en la capa de servicio, no en la base de datos.
- El sistema funcionará en línea (no se requiere operación offline).
- Los usuarios tendrán acceso a Internet y navegador actualizado.

## Restricciones

- El sistema **no** será una fuente oficial de matrícula, certificación o datos académicos. Es una herramienta de apoyo operativo.
- El sistema **no** reemplazará a SOFIA Plus ni a otros sistemas oficiales del SENA.
- El sistema debe cumplir con la normativa colombiana de protección de datos (Ley 1581 de 2012).
- La base de datos será PostgreSQL y los microservicios se desarrollarán en Java 21 con Spring Boot.

## Referencias

- [overview.md](./overview.md) — Descripción general del proyecto
- [glossary.md](./glossary.md) — Glosario de términos
- [ADR-0002: No reemplazo de SOFIA Plus](../05-architecture/decisions/records/ADR-0002-no-sofia-plus-replacement.md)