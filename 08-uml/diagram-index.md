# Índice de diagramas

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

## Contexto

Este documento contiene el índice de todos los diagramas UML y de arquitectura del sistema **Horarios SENA**. Cada diagrama está vinculado a su fuente editable y su exportación.

## Lista de diagramas

| Diagrama | Tipo | Descripción | Fuente | Exportación | Estado |
|----------|------|-------------|--------|-------------|--------|
| **Diagramas de arquitectura** |
| Arquitectura general | Componentes | Componentes principales del sistema y sus relaciones. | `diagrams/source/architecture-component.wsd` | `diagrams/exports/architecture-component.svg` | 🟡 Pendiente |
| Microservicios | Despliegue | Topología de microservicios y bases de datos. | `diagrams/source/microservices-deployment.wsd` | `diagrams/exports/microservices-deployment.svg` | 🟡 Pendiente |
| **Diagramas de dominio** |
| Entidades de dominio | Clases | Entidades principales del sistema (M2, M3, M4, M5, M7, M8, M9, M1). | `diagrams/source/domain-entities-class.wsd` | `diagrams/exports/domain-entities-class.svg` | 🟡 Pendiente |
| Reglas de negocio | Actividad | Flujo de validación de conflictos de horario. | `diagrams/source/conflict-validation-activity.wsd` | `diagrams/exports/conflict-validation-activity.svg` | 🟡 Pendiente |
| **Diagramas de flujo** |
| Autenticación | Secuencia | Flujo de autenticación JWT. | `diagrams/source/auth-sequence.wsd` | `diagrams/exports/auth-sequence.svg` | 🟡 Pendiente |
| Creación de horario | Secuencia | Secuencia de creación de horario con validación de conflictos. | `diagrams/source/schedule-creation-sequence.wsd` | `diagrams/exports/schedule-creation-sequence.svg` | 🟡 Pendiente |
| **Diagramas de base de datos** |
| Modelo relacional | Entidad-Relación | Modelo de datos de todos los esquemas. | `diagrams/source/database-er.wsd` | `diagrams/exports/database-er.svg` | 🟡 Pendiente |
| **Diagramas de despliegue** |
| Docker Compose | Despliegue | Contenedores y servicios con Docker Compose. | `diagrams/source/deployment-docker.wsd` | `diagrams/exports/deployment-docker.svg` | 🟡 Pendiente |
| **Diagramas de UI** |
| Navegación | Componentes | Mapa de navegación del frontend. | `diagrams/source/navigation-map.wsd` | `diagrams/exports/navigation-map.svg` | 🟡 Pendiente |

## Resumen de estado

| Estado | Cantidad |
|--------|----------|
| 🟢 Exportado | 0 |
| 🟡 Pendiente | 9 |
| 🔴 No iniciado | 0 |

## Convenciones de nomenclatura

- **Fuente:** `<dominio>-<tipo>.wsd` (ej. `scheduling-sequence.wsd`).
- **Exportación:** `<dominio>-<tipo>.svg` (ej. `scheduling-sequence.svg`).

## Referencias

- [README.md](./README.md)
- [diagrams/source/](./diagrams/source/)
- [diagrams/exports/](./diagrams/exports/)