# Mapa actualizado de dependencias

> Estado: 🟡 Revisión | Última actualización: 2026-10-07
> Autor: Kevin Andrey Culma (Arquitecto) | Equipo: Arquitectura.

> Este mapa registra dependencias de diseño/configuración, no prueba que todos los listeners, bindings o llamadas estén activos en el runtime. Para los riesgos y el estado reportado por ambiente al 2026-10-30, véase el [baseline DS-001](../15-project-control/ds-001-architecture-baseline.md).

## Criterio

- `sync`: llamada HTTP directa necesaria para resolver una operación de negocio.
- `async`: publicación/consumo de eventos por broker AMQP/RabbitMQ u outbox.
- `auth`: validación JWT/JWKS con IAM. No cuenta como dependencia de negocio.

## Dependencias síncronas observadas/configuradas

| Origen | Destino | Motivo | Evidencia |
|---|---|---|---|
| `academic-management-service` | `reference-data-service` | Validar/consultar centros, catálogos o estructura de referencia. | `REFERENCE_DATA_BASE_URL` |
| `academic-management-service` | `actors-service` | Validar ownership/alcance de fichas. | `ACTORS_SERVICE_BASE_URL` |
| `actors-service` | `academic-management-service` | Consultas de ficha/competencias para actores. | `ACADEMIC_MANAGEMENT_BASE_URL` |
| `scheduling-service` | `academic-management-service` | Validación de ficha/programa al construir horario. | Contrato de arquitectura vigente |
| `training-environment-service` | `reference-data-service` | Referencia institucional/centros para ambientes. | Dependencia de dominio vigente |

## Dependencias asíncronas principales

| Origen | Destino/consumidor | Canal | Propósito |
|---|---|---|---|
| `iam-service` | `audit-service`, `actors-service` | Outbox/RabbitMQ | Eventos de identidad, roles y sesiones. |
| `reference-data-service` | `audit-service` y consumidores de catálogo | AMQP opcional | Cambios en centros/catálogos/parámetros. |
| `academic-management-service` | `audit-service`, `monitoring-service`, `actors-service`, `notification-service` | RabbitMQ | Cambios de fichas, programas y eventos académicos. |
| `training-environment-service` | `audit-service`, `scheduling-service` | Eventos de dominio | Cambios de ambientes, disponibilidad, mantenimiento y reservas. |
| `actors-service` | `audit-service`, `monitoring-service`, `scheduling-service` | Eventos de dominio | Cambios de instructor/aprendiz/empresa y disponibilidad. |
| `scheduling-service` | `audit-service`, `monitoring-service`, `actors-service`, `document-service`, `notification-service` | Outbox/RabbitMQ | Validación/publicación de horarios y sesiones. |
| `monitoring-service` | `audit-service`, `notification-service` | Eventos de alerta | Alertas detectadas y solicitudes de notificación. |
| `notification-service` | `audit-service` | Eventos de notificación | Resultado de entrega EMAIL/IN_APP. |

## Diagrama Mermaid

``mermaid
graph TD
    IAM[iam-service]
    REF[reference-data-service]
    ACAD[academic-management-service]
    ENV[training-environment-service]
    ACT[actors-service]
    SCH[scheduling-service]
    DOC[document-service]
    MON[monitoring-service]
    AUD[audit-service]
    NOT[notification-service]

    ACAD -->|sync| REF
    ACAD -->|sync| ACT
    ACT -->|sync| ACAD
    SCH -->|sync| ACAD
    ENV -->|sync| REF

    IAM -.->|async| AUD
    REF -.->|async| AUD
    ACAD -.->|async| AUD
    ACAD -.->|async| MON
    ACAD -.->|async| NOT
    ENV -.->|async| AUD
    ENV -.->|async| SCH
    ACT -.->|async| AUD
    ACT -.->|async| MON
    ACT -.->|async| SCH
    SCH -.->|async| AUD
    SCH -.->|async| MON
    SCH -.->|async| DOC
    SCH -.->|async| NOT
    DOC -.->|async| AUD
    MON -.->|async| AUD
    MON -.->|async| NOT
    NOT -.->|async| AUD

    REF -.->|auth| IAM
    ACAD -.->|auth| IAM
    ENV -.->|auth| IAM
    ACT -.->|auth| IAM
    SCH -.->|auth| IAM
    DOC -.->|auth| IAM
    MON -.->|auth| IAM
    NOT -.->|auth| IAM
``
