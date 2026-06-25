# API

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Backend

## Contenido

Este directorio contiene las normas de diseño de las APIs del sistema **Horarios SENA**, la estrategia de autenticación y autorización, y los contratos OpenAPI formalizados.

## Archivos

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [guidelines.md](./guidelines.md) | Convenciones de diseño de APIs REST (nombrado, versionado, HTTP, errores). | 🟢 Estable |
| [authentication.md](./authentication.md) | Estrategia de autenticación y autorización (JWT + Spring Security). | 🟢 Estable |
| [contracts/openapi/](./contracts/openapi/) | Contratos OpenAPI validados y publicables por microservicio. | 🟢 Estable |

## Dónde va cada contrato

| Tipo de contrato | Dónde vive | Cuándo se usa |
|-----------------|------------|---------------|
| Contrato de implementación (borrador, en evolución) | `09-microservices/services/<svc>/api-contract.md` | Durante el desarrollo del servicio. |
| Contrato OpenAPI publicable (estable, revisado) | `07-api/contracts/openapi/<svc>.yaml` | Cuando el contrato es estable y puede compartirse con consumidores externos. |

**Regla:** el contrato en `07-api/contracts/openapi/` es la versión aprobada por arquitectura. Si hay diferencia entre ambos, el de `07-api/` tiene precedencia para consumidores externos.

## Tecnologías

| Aspecto | Tecnología |
|---------|------------|
| Documentación de API | SpringDoc OpenAPI 3 (OpenAPI 3.0) |
| Formato de contratos | YAML / JSON |
| Generación automática | `springdoc-openapi-starter-webmvc-ui` |
| UI de documentación | Swagger UI (`/swagger-ui.html`) |

## Referencias

- [05-architecture/overview.md](../05-architecture/overview.md)
- [05-architecture/cross-cutting.md](../05-architecture/cross-cutting.md)
- [09-microservices/](../09-microservices/)