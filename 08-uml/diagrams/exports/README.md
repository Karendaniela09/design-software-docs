# Exportaciones de diagramas

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Documentación

## Contexto

Este directorio contiene las exportaciones de diagramas UML del sistema **Horarios SENA**. Todos los diagramas tienen su fuente editable en `../source/` y su exportación aquí en formato SVG (preferido) o PNG.

## Convenciones

- **Formato preferido:** SVG (escalable, editable con herramientas vectoriales).
- **Formato alternativo:** PNG (para capturas rápidas o documentación que no requiere edición).
- **Nomenclatura:** `<dominio>-<tipo>.svg` (ej. `schedule-sequence.svg`).
- **Registro:** Todos los diagramas deben estar registrados en [`../diagram-index.md`](../diagram-index.md).

## Diagramas disponibles

| Archivo | Tipo | Descripción | Fuente |
|---------|------|-------------|--------|
| `arquitectura-general.svg` | Componentes | Diagrama de componentes de la arquitectura general | `../source/arquitectura-general.wsd` |
| `dominios-microservicios.svg` | Componentes | Mapa de dominios y microservicios del sistema | `../source/dominios-microservicios.wsd` |
| `flujo-autenticacion.svg` | Secuencia | Secuencia de autenticación con JWT | `../source/flujo-autenticacion.wsd` |
| `creacion-horario.svg` | Secuencia | Secuencia de creación de horario con validación de conflictos | `../source/creacion-horario.wsd` |
| `ejecucion-sesion.svg` | Secuencia | Secuencia de ejecución de sesión de clase | `../source/ejecucion-sesion.wsd` |
| `modelo-datos-general.svg` | Clases | Modelo de datos general (entidades principales) | `../source/modelo-datos-general.wsd` |
| `modelo-datos-horarios.svg` | Clases | Modelo de datos del scheduling_schema | `../source/modelo-datos-horarios.wsd` |
| `casos-uso-coordinador.svg` | Casos de uso | Casos de uso del coordinador académico | `../source/casos-uso-coordinador.wsd` |
| `casos-uso-instructor.svg` | Casos de uso | Casos de uso del instructor | `../source/casos-uso-instructor.wsd` |
| `despliegue-docker.svg` | Despliegue | Topología de despliegue con Docker Compose | `../source/despliegue-docker.wsd` |
| `estados-horario.svg` | Estados | Diagrama de estados de un horario | `../source/estados-horario.wsd` |

## Cómo actualizar un diagrama

1. Editar la fuente en `../source/<nombre>.wsd` (PlantUML) o `../source/<nombre>.puml`.
2. Generar la exportación:
   - **PlantUML:** Usar PlantUML CLI o extensión de VS Code.
   - **Draw.io:** Exportar como SVG o PNG.
3. Guardar la exportación en esta carpeta con el mismo nombre.
4. Actualizar [`../diagram-index.md`](../diagram-index.md) si se agrega un nuevo diagrama.

## Ejemplo de comando para generar SVG con PlantUML

```bash
# Instalar PlantUML (si no está instalado)
# Usar Docker para generar SVG
docker run --rm -v $(pwd):/data plantuml/plantuml -tsvg /data/../source/arquitectura-general.wsd