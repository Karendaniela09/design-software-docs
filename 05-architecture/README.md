# Arquitectura

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

## Contenido

Este directorio contiene la documentación arquitectónica del proyecto **Horarios SENA**. Aquí se definen los principios estructurales, las decisiones técnicas, los aspectos transversales y la estrategia de despliegue que guían el desarrollo del sistema.

## Archivos

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [overview.md](./overview.md) | Visión general de la arquitectura, componentes principales y principios de diseño. | 🟢 Estable |
| [deployment.md](./deployment.md) | Topología de despliegue, ambientes, Docker Compose, CI/CD y estrategia de rollback. | 🟢 Estable |
| [cross-cutting.md](./cross-cutting.md) | Aspectos transversales: seguridad, logging, auditoría, manejo de errores, validación y monitoreo. | 🟢 Estable |
| [decisions/](./decisions/) | Registro de Decisiones de Arquitectura (ADR) con contexto, decisión, consecuencias y alternativas. | 🟢 Estable |

## Principios arquitectónicos fundamentales

1. **Clean Architecture:** Separación estricta de capas (Domain, Application, Infrastructure, Transport) para mantener la lógica de negocio independiente de frameworks y bases de datos.
2. **Microservicios:** Cada dominio funcional se implementa como un microservicio autónomo, desplegable y escalable independientemente.
3. **Base de datos por servicio:** Cada microservicio posee su propio esquema en PostgreSQL, sin compartir tablas con otros servicios.
4. **Comunicación asíncrona:** Los microservicios se comunican mediante eventos para desacoplar procesos y mejorar la resiliencia.
5. **Observabilidad:** Logs estructurados, métricas y healthchecks para monitoreo y diagnóstico proactivo.

## Referencias

- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [02-domain/domain-map.md](../02-domain/domain-map.md)
- [09-microservices/service-catalog.md](../09-microservices/service-catalog.md)
- [04-requirements/traceability-matrix.md](../04-requirements/traceability-matrix.md)
- [00-governance/security-rules.md](../00-governance/security-rules.md)