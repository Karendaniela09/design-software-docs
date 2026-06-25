# Wireframes

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Producto / Frontend

## Contexto

Este documento contiene los wireframes de las pantallas principales del sistema **Horarios SENA**. Los wireframes son representaciones en baja fidelidad que muestran la estructura, los componentes y la jerarquía visual de cada pantalla.

Los diseños en alta fidelidad y los prototipos interactivos están disponibles en Figma.

## Pantallas principales

### 1. Dashboard (Coordinador)

**Propósito:** Vista general del sistema con resumen de horarios, ocupación de ambientes y alertas.

**Componentes:**
- Tarjeta de resumen: Total de horarios, instructores activos, ambientes disponibles.
- Tabla de próximos horarios (hoy / mañana).
- Gráfico de ocupación de ambientes (barras).
- Alertas de conflictos y observaciones pendientes.

**Acciones:**
- Ver todos los horarios.
- Crear nuevo horario.
- Gestionar instructores, ambientes, fichas.

---

### 2. Listado de Horarios

**Propósito:** Visualizar todos los horarios con filtros y paginación.

**Componentes:**
- Título: "Gestión de Horarios".
- Botón: "Crear Horario".
- Filtros: Instructor, Ambiente, Ficha, Fecha.
- Tabla de horarios (columnas: Fecha, Hora, Instructor, Ambiente, Ficha, Estado, Acciones).
- Paginación.

**Acciones por fila:**
- Ver detalle (icono o link).
- Cancelar (si no está ejecutado).
- Editar (si no está ejecutado).

---

### 3. Detalle de Horario

**Propósito:** Mostrar toda la información de un horario específico.

**Componentes:**
- Título: "Detalle del Horario".
- Información: Instructor, Ambiente, Ficha, Franja, Fecha, Estado.
- Observaciones: Listado de observaciones asociadas.
- Botón: "Agregar Observación".
- Botón: "Cancelar Horario" (si aplica).
- Botón: "Volver al listado".

---

### 4. Crear Horario

**Propósito:** Formulario para crear un nuevo horario con validación de conflictos.

**Componentes:**
- Título: "Crear Horario".
- Formulario:
  - Campo: Instructor (select o autocomplete).
  - Campo: Ambiente (select o autocomplete).
  - Campo: Ficha (select o autocomplete).
  - Campo: Franja Horaria (select).
  - Campo: Fecha (date picker).
  - Campo: Descripción (textarea opcional).
- Botón: "Guardar".
- Botón: "Cancelar".
- Mensaje de validación: "El instructor ya tiene un horario en esta franja" (rojo).

---

### 5. Listado de Instructores

**Propósito:** Visualizar todos los instructores con filtros.

**Componentes:**
- Título: "Gestión de Instructores".
- Botón: "Crear Instructor".
- Filtros: Nombre, Tipo (staff/contractor), Estado (activo/inactivo).
- Tabla: Nombre, Email, Tipo, Especialidades, Estado, Acciones.

---

### 6. Listado de Ambientes

**Propósito:** Visualizar todos los ambientes con filtros.

**Componentes:**
- Título: "Gestión de Ambientes".
- Botón: "Crear Ambiente".
- Filtros: Nombre, Tipo, Capacidad, Estado.
- Tabla: Nombre, Código, Capacidad, Ubicación, Estado, Acciones.

---

### 7. Listado de Observaciones

**Propósito:** Visualizar todas las observaciones con filtros.

**Componentes:**
- Título: "Gestión de Observaciones".
- Botón: "Crear Observación".
- Filtros: Horario, Instructor, Severidad, Estado.
- Tabla: Texto, Autor, Severidad, Fecha, Horario asociado, Estado.

---

### 8. Mi Horario (Instructor)

**Propósito:** Vista de horario semanal para el instructor.

**Componentes:**
- Título: "Mi Horario".
- Calendario semanal (vista de días y horas).
- Cada celda muestra: Ambiente, Ficha, Hora.
- Color: verde para disponible, azul para ocupado.

---

## Estados de interfaz

| Estado | Descripción | Componente |
|--------|-------------|------------|
| **Carga** | Datos cargando | Spinner o skeleton |
| **Vacío** | No hay datos para mostrar | Mensaje: "No hay elementos" |
| **Error** | Error al cargar | Alerta: "Error al cargar datos" + Reintentar |
| **Éxito** | Operación exitosa | Toast verde: "Horario creado exitosamente" |
| **Confirmación** | Eliminar o cancelar | Modal de confirmación |

---

## Enlace a Figma

Los diseños en alta fidelidad y el prototipo interactivo están disponibles en Figma:

[https://www.figma.com/make/...](https://www.figma.com/make/...)

---

## Plantilla de wireframes (para desarrollo)

### Estructura general de una pantalla de listado
