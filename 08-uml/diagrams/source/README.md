# Fuentes de diagramas

> Estado: 🟡 En progreso | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

## Contexto

Este directorio contiene los archivos fuente editables de los diagramas UML del sistema **Horarios SENA**.

## Herramientas soportadas

- **PlantUML**: Archivos `.wsd` o `.puml`
- **Draw.io**: Archivos `.drawio`

## Reglas

1. Todo diagrama debe tener su fuente en este directorio.
2. La exportación debe estar en `../exports/` con el mismo nombre y extensión `.svg` o `.png`.
3. Usar nombres descriptivos: `<dominio>-<tipo>.<ext>` (ej: `scheduling-sequence.wsd`).

## Ejemplo de contenido

### Diagrama de secuencia (PlantUML)

```wsd
@startuml
actor "Coordinador" as C
participant "Frontend" as F
participant "API Gateway" as G
participant "Scheduling Service" as S
participant "Database" as DB

C -> F: Crear horario
F -> G: POST /api/v1/schedules
G -> S: Reenviar petición
S -> DB: Validar conflictos
DB --> S: Sin conflictos
S -> DB: Guardar horario
DB --> S: Horario guardado
S --> G: 201 Created
G --> F: 201 Created
F --> C: Mostrar éxito
@enduml