# Manual de usuario

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Producto / Soporte

## Contexto

Este manual está dirigido a los usuarios finales del sistema **Horarios SENA**: coordinadores académicos, instructores y aprendices. Aquí se explica cómo utilizar las funcionalidades principales del sistema de acuerdo con el rol de cada usuario.

## ¿Qué es Horarios SENA?

Horarios SENA es una plataforma que permite gestionar la programación académica de los centros de formación del SENA. Permite asignar instructores, ambientes y fichas a bloques horarios, validando automáticamente conflictos para evitar cruces.

## Roles y permisos

| Rol | Responsabilidad |
|-----|-----------------|
| **Coordinador Académico** | Crear y gestionar horarios, asignar instructores, ambientes y fichas, registrar observaciones, gestionar catálogos. |
| **Instructor** | Consultar su horario asignado, registrar observaciones y novedades. |
| **Aprendiz** | Consultar su horario de clases (futuro). |

---

## Guía para Coordinadores Académicos

### 1. Iniciar sesión

1. Abrir el navegador y acceder a la URL del sistema.
2. Ingresar usuario y contraseña proporcionados.
3. Hacer clic en "Iniciar sesión".
4. Serás redirigido al panel de control (Dashboard).

### 2. Gestionar horarios

#### Crear un horario

1. En el menú lateral, hacer clic en **"Gestión de Horarios"**.
2. Hacer clic en el botón **"Crear Horario"**.
3. Completar el formulario:
   - **Instructor:** Seleccionar de la lista desplegable.
   - **Ambiente:** Seleccionar de la lista desplegable.
   - **Ficha:** Seleccionar de la lista desplegable.
   - **Franja Horaria:** Seleccionar día y hora.
   - **Fecha:** Seleccionar la fecha.
   - **Descripción (opcional):** Agregar notas.
4. Hacer clic en **"Guardar"**.
5. El sistema validará automáticamente si hay conflictos:
   - Si no hay conflictos, el horario se guarda.
   - Si hay conflictos, se mostrará un mensaje de error y deberás ajustar la selección.

#### Consultar horarios

1. En el menú lateral, hacer clic en **"Gestión de Horarios"**.
2. Usar los filtros para buscar por:
   - Instructor.
   - Ambiente.
   - Ficha.
   - Rango de fechas.
3. La tabla mostrará los resultados.
4. Hacer clic en el ícono de "Ver detalle" para ver información completa del horario.

#### Cancelar un horario

1. En el listado de horarios, buscar el horario deseado.
2. Hacer clic en el ícono de "Cancelar" (ícono de tachón).
3. Confirmar la cancelación en el modal.
4. El estado del horario cambiará a "Cancelado".

### 3. Gestionar instructores

1. En el menú lateral, hacer clic en **"Gestión de Instructores"**.
2. Hacer clic en **"Crear Instructor"**.
3. Completar el formulario:
   - **Nombre completo:** Obligatorio.
   - **Email:** Obligatorio, debe ser único.
   - **Tipo de contrato:** Staff (planta) o Contractor (contratista).
   - **Especialidades:** Seleccionar una o más áreas de especialidad.
   - **Estado:** Activo o Inactivo.
4. Hacer clic en **"Guardar"**.

### 4. Gestionar ambientes

1. En el menú lateral, hacer clic en **"Gestión de Ambientes"**.
2. Hacer clic en **"Crear Ambiente"**.
3. Completar el formulario:
   - **Nombre:** Obligatorio.
   - **Código:** Identificador único.
   - **Capacidad:** Número máximo de aprendices.
   - **Ubicación:** Sede, bloque, piso.
   - **Estado:** Disponible, Mantenimiento, Fuera de servicio.
4. Hacer clic en **"Guardar"**.

### 5. Registrar observaciones

1. En el detalle de un horario, hacer clic en **"Agregar Observación"**.
2. Completar el formulario:
   - **Texto:** Descripción de la observación.
   - **Severidad:** Info, Warning, Critical.
3. Hacer clic en **"Guardar"**.

---

## Guía para Instructores

### 1. Iniciar sesión

1. Abrir el navegador y acceder a la URL del sistema.
2. Ingresar usuario y contraseña.
3. Hacer clic en **"Iniciar sesión"**.
4. Serás redirigido a tu panel de control.

### 2. Consultar mi horario

1. En el menú lateral, hacer clic en **"Mi Horario"**.
2. Se mostrará una vista semanal con tus clases asignadas.
3. Cada clase muestra:
   - Ambiente.
   - Ficha.
   - Hora de inicio y fin.
4. Hacer clic en una clase para ver detalles.

### 3. Registrar observaciones (si aplica)

1. En el detalle de una clase, hacer clic en **"Agregar Observación"**.
2. Completar el formulario y guardar.

---

## Guía para Aprendices (futuro)

### 1. Iniciar sesión

1. Abrir el navegador y acceder a la URL del sistema.
2. Ingresar usuario y contraseña.
3. Hacer clic en **"Iniciar sesión"**.

### 2. Consultar mi horario

1. En el menú lateral, hacer clic en **"Mi Horario"**.
2. Se mostrará una vista semanal con tus clases asignadas.

---

## Solución de problemas comunes

| Problema | Posible solución |
|----------|------------------|
| No puedo iniciar sesión | Verificar usuario y contraseña. Si persiste, contactar al administrador. |
| No encuentro un horario | Usar los filtros de búsqueda para refinar la consulta. |
| Error al crear horario | Verificar que no haya conflictos con otro horario. |
| El sistema se ve mal en el celular | Usar un navegador actualizado. La interfaz es responsiva. |

## Referencias

- [admin-manual.md](./admin-manual.md) — Para administradores.
- [technical-onboarding.md](./technical-onboarding.md) — Para desarrolladores.
- [12-ux-ui/navigation-map.md](../12-ux-ui/navigation-map.md) — Mapa de navegación.