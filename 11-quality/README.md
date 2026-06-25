# Calidad

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / QA

## Contenido

Este directorio contiene la documentación relacionada con la calidad del sistema **Horarios SENA**. Aquí se definen la estrategia de pruebas, el flujo de revisión de código y los criterios de calidad que deben cumplir todos los entregables.

## Archivos

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [testing-strategy.md](./testing-strategy.md) | Estrategia de pruebas por nivel (unitarias, integración, aceptación) y herramientas. | 🟢 Estable |
| [code-review.md](./code-review.md) | Criterios y flujo para las revisiones de código (Pull Requests). | 🟢 Estable |

## Principios de calidad

1. **Todo código debe tener pruebas:** La cobertura mínima es del 80% en la capa de servicio y dominio.
2. **Las pruebas deben ser automatizadas:** Se ejecutan en el pipeline de CI/CD.
3. **Las revisiones de código son obligatorias:** Todo cambio debe pasar por Pull Request y ser aprobado por al menos un revisor.
4. **La calidad se mide:** Se utilizan herramientas como JaCoCo, SonarQube y OWASP Dependency Check.

## Tecnologías de calidad

| Herramienta | Propósito |
|-------------|-----------|
| **JUnit 5** | Pruebas unitarias en backend. |
| **Mockito** | Mocking de dependencias en pruebas unitarias. |
| **Testcontainers** | Pruebas de integración con contenedores reales (PostgreSQL). |
| **JaCoCo** | Medición de cobertura de código. |
| **SonarQube** | Análisis estático de código (futuro). |
| **OWASP Dependency Check** | Análisis de vulnerabilidades en dependencias. |
| **Jest / React Testing Library** | Pruebas unitarias en frontend. |

## Referencias

- [04-requirements/traceability-matrix.md](../04-requirements/traceability-matrix.md)
- [10-devops/ci-cd.md](../10-devops/ci-cd.md)
- [05-architecture/overview.md](../05-architecture/overview.md)