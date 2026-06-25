# Dependencias del proyecto

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Gestión / Arquitectura

## Contexto

Este documento identifica las dependencias internas y externas del proyecto **Horarios SENA**. Las dependencias pueden ser técnicas, organizacionales o de infraestructura, y deben ser gestionadas para evitar retrasos en el desarrollo.

## Dependencias internas

| ID | Dependencia | Afecta a | Dueño | Estado | Fecha estimada |
|----|-------------|----------|-------|--------|----------------|
| DI-001 | Definición de modelo de datos completo | Backend, Base de datos | Equipo Arquitectura | ✅ Resuelta | 2026-06-24 |
| DI-002 | Definición de contratos API (OpenAPI) | Backend, Frontend | Equipo Backend | ✅ Resuelta | 2026-06-24 |
| DI-003 | Configuración de entorno de desarrollo (Docker) | Todo el equipo | Equipo DevOps | ✅ Resuelta | 2026-06-24 |
| DI-004 | Implementación del servicio de autenticación (IAM) | Todos los servicios | Equipo Backend | 🔴 Pendiente | 2026-07-15 |
| DI-005 | Implementación del servicio de horarios (scheduling) | Frontend, Reportes | Equipo Backend | 🔴 Pendiente | 2026-07-30 |

## Dependencias externas

| ID | Dependencia | Afecta a | Responsable | Estado | Fecha estimada |
|----|-------------|----------|-------------|--------|----------------|
| DE-001 | Acceso a datos de SOFIA Plus (fichas, programas, aprendices) | Integración | SENA (dirección) | 🔴 Pendiente | TBD |
| DE-002 | Acceso a datos de instructores y ambientes | Base de datos | Centro de formación | 🔴 Pendiente | TBD |
| DE-003 | Aprobación de arquitectura por parte del SENA | Todo el proyecto | SENA (arquitectura) | 🔴 Pendiente | TBD |
| DE-004 | Infraestructura para despliegue en producción | DevOps | SENA (IT) | 🔴 Pendiente | TBD |

## Dependencias técnicas

| ID | Dependencia | Afecta a | Estado | Notas |
|----|-------------|----------|--------|-------|
| DT-001 | PostgreSQL 16 | Base de datos | ✅ Resuelta | Usar versión 16-alpine. |
| DT-002 | Java 21 LTS | Backend | ✅ Resuelta | Usar OpenJDK 21. |
| DT-003 | Node.js 20 | Frontend | ✅ Resuelta | Usar LTS. |
| DT-004 | RabbitMQ | Notificaciones | 🔴 Pendiente | Configurar broker. |
| DT-005 | Redis | Cache (futuro) | 🔴 Pendiente | Evaluar necesidad. |

## Gestión de dependencias

1. **Identificar:** Todas las dependencias deben ser identificadas al inicio del proyecto.
2. **Asignar dueño:** Cada dependencia debe tener un responsable claro.
3. **Monitorear:** Revisar el estado de las dependencias en las reuniones de seguimiento.
4. **Comunicar:** Notificar a los stakeholders sobre dependencias críticas.

## Referencias

- [risks.md](./risks.md)
- [open-questions.md](./open-questions.md)
- [09-microservices/service-catalog.md](../09-microservices/service-catalog.md)