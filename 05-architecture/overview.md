# Visión general de arquitectura

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

## Contexto

El sistema **Horarios SENA** es una plataforma de trazabilidad de ejecución formativa para los centros de formación del SENA. Permite gestionar horarios académicos, asignar instructores, ambientes y fichas, y validar conflictos en tiempo real. Está construido con una arquitectura de microservicios, siguiendo los principios de Clean Architecture y Arquitectura Hexagonal (Ports & Adapters).

## Principios arquitectónicos

| Principio | Descripción |
|-----------|-------------|
| **Clean Architecture** | Separación de capas: Domain, Application, Infrastructure, Transport. Las dependencias apuntan hacia adentro, aislando el dominio de los detalles externos. |
| **Database per Service** | Cada microservicio tiene su propia base de datos (PostgreSQL), sin compartir tablas con otros servicios, garantizando desacoplamiento y soberanía de datos. |
| **Event-Driven Communication** | Los microservicios se comunican asíncronamente mediante eventos (RabbitMQ/Kafka) para desacoplarlos y mejorar la resiliencia. |
| **API Gateway / BFF** | Un único punto de entrada para el frontend que enruta las peticiones a los microservicios correspondientes, simplificando la comunicación. |
| **Observabilidad** | Logs estructurados, métricas (Prometheus) y healthchecks para monitoreo y diagnóstico proactivo. |

## Diagrama de arquitectura de alto nivel (textual)

El sistema se compone de los siguientes elementos:

- **Frontend (React):** Aplicación SPA que consume APIs REST.
- **API Gateway (Spring Cloud Gateway / BFF):** Enruta las peticiones al microservicio correspondiente.
- **Microservicios:** Cada uno con su propia base de datos y responsabilidad de dominio.
- **PostgreSQL:** Cada microservicio tiene su propio esquema en una instancia compartida o separada.

**Flujo de comunicación:**

1. El usuario interactúa con el frontend.
2. El frontend envía peticiones HTTP al API Gateway.
3. El Gateway redirige la petición al microservicio correspondiente (IAM, Reference, Academic, Scheduling, Actors, etc.).
4. El microservicio procesa la lógica de negocio, consulta o persiste datos en su propia base de datos.
5. Si es necesario, el microservicio publica eventos que son consumidos por otros servicios para acciones asíncronas (notificaciones, auditoría, etc.).

## Componentes principales

### Backend (Spring Boot 3 + Java 21)

| Componente | Responsabilidad |
|------------|-----------------|
| **Controller** | Maneja peticiones HTTP, valida DTOs, devuelve respuestas estandarizadas. |
| **Service** | Contiene la lógica de negocio (casos de uso), orquesta repositorios y aplica reglas de negocio. |
| **Repository** | Abstrae el acceso a la base de datos mediante Spring Data JPA. |
| **Entity** | Representa las entidades de dominio mapeadas a la base de datos. |
| **DTO** | Objetos de transferencia de datos para las peticiones y respuestas de la API. |
| **Exception Handler** | Maneja errores globalmente y devuelve respuestas HTTP con códigos y mensajes adecuados. |

### Frontend (React 18)

| Componente | Responsabilidad |
|------------|-----------------|
| **App** | Composición y routing (sin lógica de negocio). |
| **Features** | Módulos autónomos por funcionalidad (horarios, instructores, ambientes, etc.). |
| **Components** | Componentes reutilizables (tablas, modales, botones, formularios). |
| **Services** | Clientes API para comunicarse con el backend (Axios). |
| **Hooks** | Hooks personalizados para lógica de estado y efectos secundarios. |

### Base de datos (PostgreSQL 16)

| Esquema | Propósito |
|---------|-----------|
| `iam_schema` | Usuarios, roles, permisos, tokens, sesiones. |
| `reference_schema` | Macroregiones, microregiones, departamentos, municipios, centros, sedes, catálogos, estados, parámetros. |
| `academic_schema` | Programas de formación, competencias, RAPs, fichas, oferta académica. |
| `scheduling_schema` | Horarios, franjas horarias, asignaciones, conflictos, sesiones de clase. |
| `actors_schema` | Instructores, aprendices, directivos, empresas, etapa productiva. |
| `audit_schema` | Auditoría append-only de todas las acciones críticas. |

## Estilo arquitectónico: Clean Architecture

El backend sigue Clean Architecture con las siguientes capas (de afuera hacia adentro):

1. **Transport (HTTP):** Controllers, DTOs, GlobalExceptionHandler. Depende de Application y Domain.
2. **Application (Use Cases):** Services con lógica de negocio, puertos (interfaces) para repositorios. Depende de Domain.
3. **Domain (Core):** Entities, Value Objects, Domain Services, Domain Events. No depende de nada (solo Java estándar).
4. **Infrastructure (Persistence):** Implementaciones concretas de repositorios (JPA/Hibernate), mapeo de entidades, configuración de base de datos. Depende de Domain y Application (implementa sus interfaces).

### Reglas de dependencia

- **Domain** no depende de nada (solo Java estándar).
- **Application** depende de Domain y de interfaces definidas en Infrastructure (puertos).
- **Transport** depende de Application y Domain.
- **Infrastructure** depende de Domain y Application (implementa las interfaces).

## Comunicación entre microservicios

| Tipo | Protocolo | Uso |
|------|-----------|-----|
| **Síncrona** | REST (HTTP/JSON) | Consultas de datos, operaciones CRUD inmediatas. |
| **Asíncrona** | Eventos (RabbitMQ / Kafka) | Notificaciones, auditoría, procesos largos y desacoplamiento de servicios. |

## Tecnologías

| Capa | Tecnología | Versión |
|------|------------|---------|
| Backend | Spring Boot | 3.2.x |
| Backend | Java | 21 LTS |
| Frontend | React | 18.x |
| Base de datos | PostgreSQL | 16.x |
| ORM | Spring Data JPA + Hibernate | - |
| Migraciones | Flyway | - |
| Documentación API | SpringDoc OpenAPI | 2.5.x |
| Logging | SLF4J + Logback | - |
| Pruebas | JUnit 5 + Mockito + Testcontainers | - |
| Contenedores | Docker + Docker Compose | - |
| CI/CD | GitHub Actions | - |

## Referencias

- [deployment.md](./deployment.md) — Topología de despliegue
- [cross-cutting.md](./cross-cutting.md) — Aspectos transversales
- [decisions/](./decisions/) — ADRs
- [09-microservices/service-catalog.md](../09-microservices/service-catalog.md)