# Visión del producto

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Producto

## Contexto

La visión del producto define el propósito general del sistema y la dirección estratégica que guiará el desarrollo. Es el "norte" que mantiene al equipo alineado en torno a un objetivo común.

## Visión

> **"Construir una plataforma especializada en trazabilidad de ejecución formativa para el SENA, donde coordinadores, instructores y actores autorizados puedan conocer en tiempo real: qué estaba programado, qué se ejecutó realmente, qué evidencias se entregaron, qué avance tiene cada aprendiz y cada ficha, qué dependencias existen en los proyectos formativos, qué alertas o desviaciones aparecen, y qué soporte documental existe para auditoría y seguimiento."**

## Propuesta de valor

El sistema ofrece a los centros de formación del SENA:

| Beneficio | Descripción |
|-----------|-------------|
| **Programación conflict-free** | Validación automática de cruces (instructor, ambiente, ficha) en tiempo real. |
| **Reducción del tiempo de planificación** | Los coordinadores podrán crear horarios en minutos, no en horas. |
| **Visibilidad en tiempo real** | Consulta de disponibilidad de instructores, ambientes y fichas. |
| **Trazabilidad completa** | Registro de ejecución real de sesiones, observaciones y cambios. |
| **Soporte a proyectos formativos** | Gestión de fases, dependencias, entregables y evidencias. |
| **Alertas y monitoreo** | Detección temprana de riesgos (deserción, retrasos, conflictos). |
| **Auditoría y control** | Registro inmutable de todas las acciones críticas. |

## Objetivos estratégicos

### Objetivo 1: Eliminar conflictos de programación
**Meta:** El sistema **no debe permitir** que un instructor, ambiente o ficha sea asignado a dos bloques horarios que se solapen en el tiempo.

### Objetivo 2: Centralizar la información operativa
**Meta:** Todos los datos relevantes para la programación académica (estructura institucional, ambientes, actores, programas, horarios, proyectos) deben estar disponibles en una única plataforma.

### Objetivo 3: Proveer trazabilidad de ejecución
**Meta:** El sistema debe permitir comparar lo que se planeó con lo que realmente se ejecutó, registrando novedades, asistencias y desviaciones.

### Objetivo 4: Integrarse sin reemplazar sistemas oficiales
**Meta:** El sistema consume datos de SOFIA Plus y otros sistemas oficiales del SENA, pero **no los reemplaza**. Es una herramienta de apoyo operativo.

## Audiencia objetivo

| Perfil | Responsabilidad |
|--------|-----------------|
| **Coordinador Académico** | Planifica horarios, asigna recursos, gestiona incidencias y supervisa la ejecución. |
| **Instructor** | Consulta su horario, registra ejecución de sesiones y reporta novedades. |
| **Aprendiz** | Consulta su horario de clases y el avance de sus proyectos (futuro). |
| **Administrador** | Configura catálogos, gestiona usuarios y audita el sistema. |
| **Subdirector de Centro** | Supervisa indicadores de ocupación, uso de recursos y cumplimiento académico. |

## Factores críticos de éxito

- El sistema debe ser **intuitivo y fácil de usar** para que los coordinadores lo adopten rápidamente.
- Las validaciones de conflicto deben ser **en tiempo real** y **precisas**.
- La integración con SOFIA Plus debe ser **confiable** y **no disruptiva**.
- El sistema debe ser **escalable** para soportar múltiples centros y regionales.

## Referencias

- [roadmap.md](./roadmap.md) — Hitos y fases del producto
- [product-backlog.md](./product-backlog.md) — Backlog priorizado
- [01-context/overview.md](../01-context/overview.md) — Descripción general del proyecto
- [01-context/scope.md](../01-context/scope.md) — Alcance del MVP