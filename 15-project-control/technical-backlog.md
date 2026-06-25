# Technical Backlog

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Desarrollo

## Contexto

Este documento contiene la lista de tareas técnicas pendientes y la deuda técnica documentada del sistema **Horarios SENA**. El backlog técnico se diferencia del backlog de producto en que está enfocado en mejoras técnicas, infraestructura, calidad de código y refactorizaciones.

## Backlog técnico

| ID | Tarea | Prioridad | Área | Estado | Estimación |
|----|-------|-----------|------|--------|------------|
| TB-001 | Implementar autenticación con JWT y Spring Security | Alta | Seguridad | ✅ Completado | 8h |
| TB-002 | Configurar migraciones con Flyway | Alta | Base de datos | ✅ Completado | 4h |
| TB-003 | Configurar Docker Compose para entorno local | Alta | DevOps | ✅ Completado | 6h |
| TB-004 | Implementar validación de conflictos de horario | Alta | Backend | ✅ Completado | 12h |
| TB-005 | Documentar APIs con OpenAPI (SpringDoc) | Media | Documentación | ✅ Completado | 4h |
| TB-006 | Configurar pipeline CI/CD con GitHub Actions | Media | DevOps | ✅ Completado | 8h |
| TB-007 | Implementar auditoría append-only (tabla audit_log) | Media | Backend | ✅ Completado | 6h |
| TB-008 | Configurar monitoreo con Prometheus y Grafana | Baja | DevOps | 🔴 Pendiente | 10h |
| TB-009 | Implementar pruebas de carga con JMeter | Baja | Calidad | 🔴 Pendiente | 8h |
| TB-010 | Configurar SonarQube para análisis estático | Baja | Calidad | 🔴 Pendiente | 6h |
| TB-011 | Implementar sistema de notificaciones con RabbitMQ | Media | Backend | 🔴 Pendiente | 12h |
| TB-012 | Optimizar consultas de conflicto con índices compuestos | Alta | Base de datos | ✅ Completado | 4h |
| TB-013 | Implementar cache con Redis para consultas frecuentes | Baja | Backend | 🔴 Pendiente | 10h |
| TB-014 | Refactorizar controladores para usar DTOs consistentes | Media | Backend | ✅ Completado | 6h |
| TB-015 | Agregar pruebas de integración con Testcontainers | Alta | Calidad | ✅ Completado | 8h |
| TB-016 | Configurar healthchecks para todos los servicios | Alta | DevOps | ✅ Completado | 4h |
| TB-017 | Implementar logging estructurado (JSON) | Media | Backend | ✅ Completado | 4h |
| TB-018 | Crear scripts de backup y restauración de BD | Media | DevOps | ✅ Completado | 6h |
| TB-019 | Implementar generación de reportes asíncronos (PDF/Excel) | Baja | Backend | 🔴 Pendiente | 16h |
| TB-020 | Configurar CORS restrictivo por ambiente | Alta | Backend | ✅ Completado | 2h |

## Deuda técnica documentada

| ID | Descripción | Severidad | Plan de acción |
|----|-------------|-----------|----------------|
| TD-001 | Algunos controladores tienen lógica de validación repetida | Baja | Refactorizar en un validador común. |
| TD-002 | Las consultas de conflictos usan múltiples joins que pueden optimizarse | Media | Revisar y optimizar con índices compuestos. |
| TD-003 | No se usa un patrón de repositorio genérico en algunas entidades | Baja | Estandarizar el uso de repositorios. |

## Referencias

- [risks.md](./risks.md)
- [dependencies.md](./dependencies.md)
- [03-product/product-backlog.md](../03-product/product-backlog.md)