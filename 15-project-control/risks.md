# Riesgos del proyecto

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Gestión / Arquitectura

## Contexto

Este documento identifica los riesgos del proyecto **Horarios SENA**, evalúa su impacto y probabilidad, y define los planes de mitigación. Los riesgos se clasifican por categoría y se revisan periódicamente.

## Matriz de riesgos

| ID | Riesgo | Categoría | Impacto | Probabilidad | Nivel | Mitigación |
|----|--------|-----------|---------|--------------|-------|------------|
| R-001 | Resistencia al cambio por parte de los coordinadores | Organizacional | Alto | Media | Alto | Capacitación temprana, UI intuitiva, demostraciones piloto. |
| R-002 | Calidad de datos base (datos incorrectos desde SOFIA Plus) | Datos | Alto | Media | Alto | Validaciones en la capa de servicio, mapeo controlado. |
| R-003 | Variabilidad de patrones de franjas horarias | Dominio | Medio | Media | Medio | Modelo de franjas flexible (horas configurables). |
| R-004 | Sobrecarga de observaciones sin sistema de clasificación | Operacional | Medio | Baja | Bajo | Clasificación por severidad y estado, filtros de búsqueda. |
| R-005 | "Forzar guardado" ignorando advertencias de conflicto | Negocio | Alto | Baja | Alto | Regla de negocio: nunca permitir guardado con conflicto. |
| R-006 | Fallo en integración con SOFIA Plus | Técnico | Alto | Baja | Medio | Plan de contingencia, carga manual de datos. |
| R-007 | Rendimiento de consultas de conflicto en alta concurrencia | Técnico | Alto | Media | Alto | Índices compuestos, optimización de consultas. |
| R-008 | Cambios en normativa SENA durante el desarrollo | Normativo | Medio | Baja | Bajo | Módulo de parametrización flexible. |
| R-009 | Falta de documentación para los usuarios finales | Organizacional | Medio | Media | Medio | Manuales de usuario y videos tutoriales. |
| R-010 | Rotación del equipo de desarrollo | Organizacional | Medio | Baja | Bajo | Documentación completa, onboarding estructurado. |

## Plan de mitigación detallado

### R-001: Resistencia al cambio

- Capacitar a los coordinadores en el uso del sistema antes del lanzamiento.
- Realizar demostraciones piloto con usuarios clave.
- Diseñar una UI intuitiva con flujos guiados.

### R-002: Calidad de datos base

- Implementar validaciones en la capa de servicio.
- Establecer controles de integridad (unicidad, tipos de datos).
- Definir un proceso de limpieza de datos inicial.

### R-007: Rendimiento de consultas de conflicto

- Crear índices compuestos en la tabla `schedule`.
- Optimizar consultas JPA.
- Considerar cache para consultas frecuentes.

## Referencias

- [dependencies.md](./dependencies.md)
- [open-questions.md](./open-questions.md)
- [04-requirements/traceability-matrix.md](../04-requirements/traceability-matrix.md)