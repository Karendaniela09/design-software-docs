# [Nombre del Servicio]

> Estado: 🔴 Pendiente | Última actualización: YYYY-MM-DD
> Autor: [Nombre Apellido] | Equipo: [nombre del equipo]

## Responsabilidad

Una línea que describa qué hace este servicio.

**Ejemplo:** Gestiona la creación, actualización y validación de horarios académicos.

## Bounded context

Dominio al que pertenece este servicio dentro del sistema.

**Ejemplo:** Gestión de Horarios.

## Dependencias

| Servicio | Tipo | Motivo |
|----------|------|--------|
| `actors-service` | Síncrona (REST) | Para obtener datos de instructores y fichas. |
| `training-environment-service` | Síncrona (REST) | Para verificar disponibilidad de ambientes. |
| `academic-management-service` | Síncrona (REST) | Para validar competencias y programas. |
| `notification-service` | Asíncrona (Evento) | Para enviar notificaciones al instructor. |
| `audit-service` | Asíncrona (Evento) | Para registrar auditoría. |

## Links

| Recurso | Enlace |
|---------|--------|
| Repositorio de código | `https://github.com/...` |
| API Contract | [api-contract.md](./api-contract.md) |
| Data Model | [data-model.md](./data-model.md) |
| Eventos | [events.md](./events.md) |
| Runbook | [runbook.md](./runbook.md) |

## Estructura del servicio (Spring Boot)

```text
src/main/java/com/sena/horarios/<servicio>/
├── controller/         # Controladores REST
├── dto/                # Objetos de transferencia de datos
├── entity/             # Entidades JPA
├── repository/         # Repositorios JPA
├── service/            # Lógica de negocio
├── config/             # Configuraciones
├── exception/          # Excepciones personalizadas
└── utils/              # Utilidades