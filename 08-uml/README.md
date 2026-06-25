# UML

> Estado: 🟡 En progreso | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

## Contexto

Este directorio contiene los diagramas UML y de arquitectura visual del proyecto **Horarios SENA**. Todo diagrama debe tener fuente editable y exportación revisable.

## Convenciones

- **Fuentes:** En `diagrams/source/` con extensión `.wsd` (PlantUML), `.puml` o `.drawio`.
- **Exportaciones:** En `diagrams/exports/` con formato `.svg` preferido (también `.png`).
- **Nombre:** `<dominio>-<tipo>.<ext>` (ej: `scheduling-sequence.wsd`).
- **Registro:** Todo diagrama debe registrarse en [diagram-index.md](./diagram-index.md).

## Tipos de diagrama

| Tipo | Archivo fuente | Descripción |
|------|---------------|-------------|
| Casos de uso | `*-use-case.wsd` | Actores y funcionalidades del sistema. |
| Clases | `*-class.wsd` | Estructura estática del dominio. |
| Secuencia | `*-sequence.wsd` | Interacciones entre objetos en el tiempo. |
| Actividad | `*-activity.wsd` | Flujos de trabajo y procesos. |
| Estado | `*-state.wsd` | Ciclo de vida de una entidad. |
| Componentes | `*-component.wsd` | Estructura de componentes y dependencias. |
| Despliegue | `*-deployment.wsd` | Topología física de despliegue. |

## Archivos

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [diagram-index.md](./diagram-index.md) | Índice de fuentes y exportaciones de diagramas. | 🟡 En progreso |
| [diagrams/source/](./diagrams/source/) | Fuentes editables de diagramas. | 🟡 En progreso |
| [diagrams/exports/](./diagrams/exports/) | Exportaciones SVG o PNG. | 🟡 En progreso |

## Referencias

- [05-architecture/overview.md](../05-architecture/overview.md)
- [02-domain/domain-map.md](../02-domain/domain-map.md)