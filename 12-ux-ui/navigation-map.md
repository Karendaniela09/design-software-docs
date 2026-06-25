# Mapa de navegación

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Producto / Frontend

## Contexto

Este documento define el mapa de navegación del sistema **Horarios SENA**. Describe la estructura de pantallas, la jerarquía de navegación y el flujo entre las diferentes secciones del sistema.

## Estructura de navegación

### Usuario: Coordinador Académico

```text
Dashboard
├── Gestión de Horarios
│   ├── Listado de Horarios
│   ├── Crear Horario
│   ├── Detalle de Horario
│   └── Cancelar Horario
├── Gestión de Instructores
│   ├── Listado de Instructores
│   ├── Crear Instructor
│   └── Detalle de Instructor
├── Gestión de Ambientes
│   ├── Listado de Ambientes
│   ├── Crear Ambiente
│   └── Detalle de Ambiente
├── Gestión de Fichas
│   ├── Listado de Fichas
│   ├── Crear Ficha
│   └── Detalle de Ficha
├── Gestión de Observaciones
│   ├── Listado de Observaciones
│   └── Crear Observación
├── Reportes
│   ├── Reporte de Horarios
│   ├── Reporte de Ocupación
│   └── Reporte de Carga de Instructores
└── Configuración
    ├── Catálogos
    ├── Parámetros
    └── Usuarios

### Usuario: Instructor
Dashboard
├── Mi Horario
│   ├── Vista Semanal
│   └── Detalle de Sesión
├── Mis Observaciones
│   ├── Listado de Observaciones
│   └── Crear Observación
└── Mi Perfil
    ├── Ver Perfil
    └── Editar Perfil

### Usuario: Administrador
text
Dashboard
├── Gestión de Usuarios
│   ├── Listado de Usuarios
│   ├── Crear Usuario
│   └── Asignar Roles
├── Gestión de Catálogos
│   ├── Listado de Catálogos
│   ├── Crear Catálogo
│   └── Gestionar Detalles
├── Auditoría
│   ├── Historial de Cambios
│   └── Logs de Acceso
└── Configuración del Sistema
    ├── Parámetros Globales
    └── Configuración de Notificaciones

