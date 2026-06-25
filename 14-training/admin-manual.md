# Manual de administrador

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Soporte / Operaciones

## Contexto

Este manual está dirigido a los administradores del sistema **Horarios SENA**. Aquí se explica cómo gestionar usuarios, roles, catálogos y parámetros del sistema.

## ¿Qué hace un administrador?

El administrador es responsable de:
- Gestionar usuarios y roles.
- Configurar catálogos (modalidades, jornadas, estados).
- Configurar parámetros globales del sistema.
- Supervisar la auditoría del sistema.
- Gestionar backups y recuperación.

---

## 1. Gestión de usuarios

### Crear un usuario

1. En el menú lateral, hacer clic en **"Gestión de Usuarios"**.
2. Hacer clic en **"Crear Usuario"**.
3. Completar el formulario:
   - **Nombre de usuario:** Obligatorio, único.
   - **Email:** Obligatorio, único.
   - **Contraseña:** Generar una contraseña segura.
   - **Roles:** Asignar uno o más roles (Coordinador, Instructor, Administrador).
4. Hacer clic en **"Guardar"**.
5. El usuario recibirá un correo con sus credenciales.

### Editar un usuario

1. En el listado de usuarios, buscar el usuario deseado.
2. Hacer clic en el ícono de "Editar".
3. Modificar los campos necesarios.
4. Hacer clic en **"Guardar"**.

### Desactivar un usuario

1. En el listado de usuarios, buscar el usuario deseado.
2. Hacer clic en el ícono de "Desactivar".
3. Confirmar la acción.
4. El usuario no podrá iniciar sesión hasta ser reactivado.

---

## 2. Gestión de catálogos

### ¿Qué son los catálogos?

Los catálogos son listas de valores predefinidos que se utilizan en todo el sistema. Ejemplos:
- Modalidades de formación (Presencial, Virtual, Mixta).
- Jornadas académicas (Mañana, Tarde, Noche).
- Estados (Activo, Inactivo, Suspendido).
- Tipos de formación (Titulada, Complementaria).

### Crear un catálogo

1. En el menú lateral, hacer clic en **"Configuración > Catálogos"**.
2. Hacer clic en **"Crear Catálogo"**.
3. Completar el formulario:
   - **Código:** Identificador único (ej. `MOD`).
   - **Nombre:** Nombre del catálogo (ej. "Modalidades").
   - **Descripción:** Explicación del catálogo.
4. Hacer clic en **"Guardar"**.

### Agregar un detalle al catálogo

1. En el listado de catálogos, hacer clic en el nombre del catálogo.
2. Hacer clic en **"Agregar Detalle"**.
3. Completar el formulario:
   - **Código:** Identificador único (ej. `PRE`).
   - **Nombre:** Nombre del detalle (ej. "Presencial").
   - **Descripción:** Explicación del detalle.
   - **Orden de visualización:** Número para ordenar.
4. Hacer clic en **"Guardar"**.

### Desactivar un detalle

1. En el detalle del catálogo, buscar el elemento deseado.
2. Hacer clic en el ícono de "Desactivar".
3. Confirmar la acción.

---

## 3. Gestión de parámetros

### ¿Qué son los parámetros?

Los parámetros son configuraciones globales del sistema que pueden ajustarse sin modificar el código. Ejemplos:
- `MAX_APRENDICES_FICHA = 35`
- `MAX_HORAS_INSTRUCTOR = 40`
- `AUTOGUARDADO_CANVAS = TRUE`

### Editar un parámetro

1. En el menú lateral, hacer clic en **"Configuración > Parámetros"**.
2. Buscar el parámetro deseado.
3. Hacer clic en el ícono de "Editar".
4. Modificar el valor.
5. Hacer clic en **"Guardar"**.

### Crear un parámetro

1. En el menú lateral, hacer clic en **"Configuración > Parámetros"**.
2. Hacer clic en **"Crear Parámetro"**.
3. Completar el formulario:
   - **Código:** Identificador único (ej. `MAX_APRENDICES`).
   - **Nombre:** Nombre del parámetro.
   - **Valor:** Valor a configurar.
   - **Tipo de dato:** String, Integer, Boolean, Date.
4. Hacer clic en **"Guardar"**.

---

## 4. Auditoría

### Consultar logs de auditoría

1. En el menú lateral, hacer clic en **"Auditoría"**.
2. Usar filtros para buscar por:
   - Usuario.
   - Fecha.
   - Tipo de acción (CREATE, UPDATE, DELETE).
   - Entidad afectada.
3. La tabla mostrará los registros de auditoría.

### Interpretar un registro de auditoría

| Campo | Descripción |
|-------|-------------|
| `Usuario` | Quién realizó la acción. |
| `Acción` | CREATE, UPDATE, DELETE, LOGIN, LOGOUT. |
| `Entidad` | Tabla afectada (ej. INSTRUCTOR, SCHEDULE). |
| `ID` | Identificador del registro afectado. |
| `Valor anterior` | JSON con el valor antes del cambio. |
| `Valor nuevo` | JSON con el valor después del cambio. |
| `Fecha` | Cuándo ocurrió. |
| `IP` | Dirección IP desde donde se realizó la acción. |

---

## 5. Gestión de backups

### Verificar backups

1. En el servidor, verificar la carpeta de backups: `/backups/postgres/`.
2. Confirmar que los backups se están generando diariamente.
3. Verificar que el tamaño de los archivos es razonable.

### Restaurar un backup (desde consola)

```bash
# Detener servicios
docker compose down

# Restaurar base de datos
docker compose exec -T postgres pg_restore -U horarios_user -d horarios_db /backups/postgres/horarios_db_20260624.dump

# Reiniciar servicios
docker compose up -d