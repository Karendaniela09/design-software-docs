# Microservicios

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

## Contenido

Este directorio contiene el catálogo y la documentación de los microservicios del sistema **Horarios SENA**. Cada microservicio es una unidad autónoma, desplegable e independiente con su propia base de datos y responsabilidad de dominio.

## Estructura de la carpeta

| Elemento | Descripción |
|----------|-------------|
| [service-catalog.md](./service-catalog.md) | Inventario de todos los microservicios, owners y estado documental. |
| [communication-patterns.md](./communication-patterns.md) | Patrones de comunicación síncrona y asíncrona entre servicios. |
| [_template/](./_template/) | Plantilla para documentar un servicio nuevo (no es un servicio real). |
| [services/](./services/) | Documentación específica por microservicio (cada servicio tiene su carpeta). |

## Catálogo de microservicios

| Servicio | Responsabilidad | Base de datos | Estado |
|----------|-----------------|---------------|--------|
| **iam-service** | Autenticación, autorización, roles, permisos, sesiones y tokens. | `iam_db` | 🟡 En progreso |
| **reference-data-service** | Estructura institucional (macroregiones, centros, sedes) y catálogos base. | `ref_db` | 🟡 En progreso |
| **academic-management-service** | Programas de formación, competencias, RAPs, fichas y oferta académica. | `academic_db` | 🟡 En progreso |
| **training-environment-service** | Ambientes de aprendizaje, inventario, mantenimiento, reservas y disponibilidad. | `env_db` | 🟡 En progreso |
| **scheduling-service** | Horarios, franjas horarias, asignaciones, conflictos y sesiones de clase. | `scheduling_db` | 🟡 En progreso |
| **actors-service** | Instructores, aprendices, directivos, empresas y etapa productiva. | `actors_db` | 🟡 En progreso |
| **document-service** | Documentos, plantillas, generación de PDFs y ciclo de vida documental. | `document_db` | 🟡 En progreso |
| **monitoring-service** | KPIs, alertas, notificaciones, sesiones de seguimiento y planes de mejora. | `monitoring_db` | 🟡 En progreso |
| **audit-service** | Auditoría append-only de todas las acciones críticas del sistema. | `audit_db` | 🟡 En progreso |

## Reglas de documentación

1. **No crear carpetas en `services/` hasta que el servicio exista en el repositorio de código** o su creación esté formalmente aprobada por arquitectura.
2. **Todo servicio debe tener una ADR** en `05-architecture/decisions/records/` antes de crear su carpeta.
3. **Cada servicio debe tener:** `README.md`, `api-contract.md`, `data-model.md`, `events.md` y `runbook.md`.
4. **Registrar el servicio en `service-catalog.md`** antes de crear la carpeta.

## Plantilla

Para crear un nuevo servicio, copiar la plantilla:

```bash
cp -r 09-microservices/_template/ 09-microservices/services/<nombre-servicio>/