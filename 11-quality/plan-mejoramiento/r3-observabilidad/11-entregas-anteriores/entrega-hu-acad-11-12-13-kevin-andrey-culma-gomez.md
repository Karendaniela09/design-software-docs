# Entrega Develop HU-ACAD-11 / HU-ACAD-12 / HU-ACAD-13

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

Fecha: 2026-10-14

Desarrollador: Kevin Andrey Culma Gomez

## Repositorios y ramas

| Repositorio | Rama origen | Rama destino | Estado |
| --- | --- | --- | --- |
| `design-software-academic-management-service` | `hu-acad-11-dev` | `develop` | Listo para PR |
| `design-software-academic-management-db` | `hu-acad-11-dev` | `develop` | Listo para PR |

## Alcance implementado

Se implementaron HU-ACAD-11, HU-ACAD-12 y HU-ACAD-13 para `academic-management`.

- `PATCH /api/v1/fichas/{id}/status` cambia el estado de la ficha usando la maquina de estados.
- `DELETE /api/v1/fichas/{id}` reutiliza el mismo caso de uso interno y cancela la ficha con estado `CANCELLED`.
- La baja no elimina fisicamente registros ni usa columna `deleted_at`.
- La cancelacion requiere feature `ACADEMIC_FICHA_STATUS` y rol `CENTER_DIRECTOR`.
- Estados terminales `COMPLETED` y `CANCELLED` responden `409 ACAD_TERMINAL_STATUS`.
- Las validaciones de negocio ocurren antes de persistir y antes de publicar eventos.
- Los eventos se escriben en `academic_management.outbox` dentro de la misma transaccion de negocio.
- El relay publica eventos hacia RabbitMQ/AMQP en el topic exchange `academic-events`.
- Se configura DLQ `academic-events.dlq` con retencion de 7 dias y reintentos `1s -> 4s -> 16s`.

## Eventos cubiertos

| Evento | Consumidores esperados |
| --- | --- |
| `academic.program.created` | `audit-service` |
| `academic.ficha.opened` | `audit-service`, `monitoring-service` |
| `academic.ficha.closed` | `audit-service`, `monitoring-service` |
| `academic.competency.updated` | `audit-service`, `actors-service` |

Todos usan el envelope canonico:

- `event_id`
- `event_type`
- `version`
- `timestamp`
- `source_service = academic-management-service`
- `payload`
- `correlation_id` opcional

No se usan campos obsoletos: `schema_version`, `occurred_at`, `data` ni `source_port`.

## Cambios principales

### Servicio

Archivos destacados:

- `academic-core/src/main/java/co/sena/academic/application/port/in/ChangeFichaStatusUseCase.java`
- `academic-core/src/main/java/co/sena/academic/application/usecase/FichaService.java`
- `academic-core/src/main/java/co/sena/academic/domain/model/Ficha.java`
- `academic-adapters/src/main/java/co/sena/academic/adapter/in/rest/FichaController.java`
- `academic-adapters/src/main/java/co/sena/academic/adapter/out/event/AcademicOutboxRelay.java`
- `academic-adapters/src/main/java/co/sena/academic/adapter/out/event/AcademicOutboxWriter.java`
- `academic-management-api/src/main/resources/application.yml`

### Base de datos

Archivos destacados:

- `01_ddl/03_tables/008_create_table_outbox.sql`
- `05_rollbacks/01_ddl/03_tables/008_create_table_outbox.rollback.sql`
- `01_ddl/03_tables/000-changelog.yaml`

## Criterios de aceptacion

| Criterio | Estado | Evidencia |
| --- | --- | --- |
| Baja de ficha como `CANCELLED` | Implementado | `FichaService`, `FichaController` |
| `DELETE /fichas/{id}` reutiliza caso de uso | Implementado | `ChangeFichaStatusUseCase` usado por `PATCH` y `DELETE` |
| Sin borrado fisico ni `deleted_at` | Implementado | Solo transicion de estado |
| Feature real `ACADEMIC_FICHA_STATUS` | Implementado | `FichaController` |
| Restriccion `CENTER_DIRECTOR` para cancelacion | Implementado | `FichaController`, `FichaService` |
| Estados terminales devuelven `409 ACAD_TERMINAL_STATUS` | Implementado | `FichaExceptionHandler`, pruebas |
| No publicar eventos ante validaciones fallidas | Implementado | `FichaService`, `FichaControllerIT` |
| Eventos canonicos publicados por outbox | Implementado | `AcademicOutboxWriter`, `AcademicOutboxRelay` |
| Tabla outbox versionada | Implementado | repo DB, changeset `008-create-table-outbox` |
| Reintentos y DLQ | Implementado | `AcademicOutboxRelay`, `AcademicEventsRabbitConfiguration` |

## Verificaciones ejecutadas

```powershell
mvn -q -pl academic-adapters -am test -DskipITs
```

Resultado:

```text
PASS
```

```powershell
mvn -q -pl academic-adapters -am package -DskipTests
```

Resultado:

```text
PASS
```

```powershell
mvn -q -pl academic-adapters -am verify
```

Resultado:

```text
BLOCKED BY LOCAL ENVIRONMENT
```

Motivo: Testcontainers no encontro un entorno Docker valido en la maquina local. Las pruebas de integracion contra Postgres quedan listas para ejecutarse en ambiente con Docker activo.

```powershell
git diff --check
```

Resultado:

```text
PASS
```

## Pull requests

Pendiente de completar con URLs tras crear los PR:

| Repositorio | PR |
| --- | --- |
| `design-software-academic-management-service` | Pendiente |
| `design-software-academic-management-db` | Pendiente |

## Notas para QA y arquitectura

- Validar `PATCH /api/v1/fichas/{id}/status` hacia `CANCELLED`.
- Validar que `DELETE /api/v1/fichas/{id}` produzca el mismo resultado y evento `academic.ficha.closed`.
- Validar que fichas `COMPLETED` o `CANCELLED` respondan `409`.
- Validar que errores `422` no creen filas en outbox.
- Validar publicacion real del relay contra RabbitMQ y DLQ.
- Validar que el payload respete el envelope canonico y los enums reales `DAY/NIGHT/MIXED` e `IN_PERSON/VIRTUAL/HYBRID`.
