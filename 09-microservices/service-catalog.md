# Catálogo de servicios

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

## Contexto

Este documento contiene el catálogo de todos los microservicios del sistema **Horarios SENA**. Cada servicio está descrito con su responsabilidad, base de datos, owner y estado documental.

## Catálogo de servicios

| Servicio | Responsabilidad | Base de datos | Owner | Repositorio | Estado |
|----------|-----------------|---------------|-------|-------------|--------|
| **iam-service** | Autenticación, autorización, roles, permisos, sesiones y tokens. | `iam_db` | Equipo ADSO | [repo](https://github.com/...) | 🟡 |
| **reference-data-service** | Estructura institucional (macroregiones, microregiones, centros, sedes) y catálogos base (estados, modalidades, jornadas). | `ref_db` | Equipo ADSO | [repo](https://github.com/...) | 🟡 |
| **academic-management-service** | Programas de formación, competencias, RAPs, fichas y oferta académica. | `academic_db` | Equipo ADSO | [repo](https://github.com/...) | 🟡 |
| **training-environment-service** | Ambientes de aprendizaje, inventario, mantenimiento, reservas y disponibilidad. | `env_db` | Equipo ADSO | [repo](https://github.com/...) | 🟡 |
| **scheduling-service** | Horarios, franjas horarias, asignaciones, conflictos, sesiones de clase y validación en tiempo real. | `scheduling_db` | Equipo ADSO | [repo](https://github.com/...) | 🟡 |
| **actors-service** | Instructores, aprendices, directivos, empresas y etapa productiva. | `actors_db` | Equipo ADSO | [repo](https://github.com/...) | 🟡 |
| **document-service** | Documentos, plantillas, generación de PDFs y ciclo de vida documental. | `document_db` | Equipo ADSO | [repo](https://github.com/...) | 🟡 |
| **monitoring-service** | KPIs, alertas, notificaciones, sesiones de seguimiento y planes de mejora. | `monitoring_db` | Equipo ADSO | [repo](https://github.com/...) | 🟡 |
| **audit-service** | Auditoría append-only de todas las acciones críticas del sistema. | `audit_db` | Equipo ADSO | [repo](https://github.com/...) | 🟡 |

## Leyenda de estados

| Estado | Significado |
|--------|-------------|
| 🔴 Pendiente | Servicio planeado, sin documentación. |
| 🟡 En progreso | Documentación en desarrollo o código en desarrollo. |
| 🟢 Estable | Documentación y código completos, servicio en operación. |
| ⚫ Deprecado | Servicio obsoleto o reemplazado. |

## Dependencias entre servicios

| Servicio | Depende de | Tipo |
|----------|------------|------|
| `scheduling-service` | `actors-service` (instructores, fichas), `training-environment-service` (ambientes), `academic-management-service` (programas) | Síncrona (REST) |
| `academic-management-service` | `reference-data-service` (catálogos, centros) | Síncrona (REST) |
| `actors-service` | `reference-data-service` (centros, sedes) | Síncrona (REST) |
| `training-environment-service` | `reference-data-service` (centros, sedes, ubicaciones) | Síncrona (REST) |
| `monitoring-service` | `scheduling-service`, `actors-service`, `academic-management-service` | Asíncrona (Eventos) |
| `document-service` | `scheduling-service`, `actors-service` | Asíncrona (Eventos) |
| `audit-service` | Todos los servicios (eventos de auditoría) | Asíncrona (Eventos) |
| `iam-service` | `reference-data-service` (sedes para usuarios) | Síncrona (REST) |

## Patrones de comunicación

| Tipo | Protocolo | Uso |
|------|-----------|-----|
| **Síncrona** | REST (HTTP/JSON) | Consultas de datos, operaciones CRUD inmediatas. |
| **Asíncrona** | Eventos (RabbitMQ / Kafka) | Notificaciones, auditoría, procesos largos y desacoplamiento de servicios. |