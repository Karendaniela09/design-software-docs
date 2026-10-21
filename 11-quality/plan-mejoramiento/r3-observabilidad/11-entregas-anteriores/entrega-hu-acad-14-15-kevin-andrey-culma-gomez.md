# Entrega Develop HU-ACAD-14 / HU-ACAD-15

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

Fecha: 2026-10-14

Desarrollador: Kevin Andrey Culma Gomez

## Repositorio y rama

| Repositorio | Rama origen | Rama destino | Commit | Estado |
| --- | --- | --- | --- | --- |
| `design-software-academic-management-service` | `hu-acad-12-dev` | `develop` | `aa01948` | Publicada y lista para PR |

No se requirieron cambios en repositorios de base de datos ni de contratos. Las tablas y los schemas OpenAPI necesarios ya existian.

## Alcance implementado

Se implementaron los reportes de solo lectura HU-ACAD-14 y HU-ACAD-15 dentro de `academic-management`.

### HU-ACAD-14 - Capacidad y estado de oferta por ficha

- Endpoint `GET /api/v1/reports/enrollment-by-ficha`.
- Proteccion mediante `ACADEMIC_FICHA_VIEW`.
- Filtros por `training_center_id`, `program_id`, `status`, `from` inclusivo y `to` exclusivo.
- Paginacion por `page` y `page_size` y ordenamiento controlado mediante `sort`.
- Proyeccion de `enrollment_ficha` con `program_code` y `program_name` obtenidos mediante join de solo lectura con `training_program`.
- Respuesta alineada con el schema congelado `EnrollmentByFichaReportItem`.

### HU-ACAD-15 - Avance temporal de fichas

- Endpoint `GET /api/v1/reports/ficha-progress`.
- Proteccion mediante `ACADEMIC_FICHA_VIEW`.
- Los mismos filtros, paginacion y alcance de HU-ACAD-14.
- Calculo derivado exclusivamente de `enrollment_ficha`.
- `days_elapsed` se calcula desde `start_date`; cuando existe `actual_end_date`, el calculo termina en esa fecha.
- `days_remaining` se calcula contra `expected_end_date` y queda en `null` cuando no existe fecha esperada o la ficha ya esta cerrada.
- `is_delayed` es `true` unicamente cuando la fecha actual supera `expected_end_date` y la ficha no esta en `COMPLETED` ni `CANCELLED`.
- Respuesta alineada con el schema congelado `FichaProgressReportItem`.

## Seguridad y scope

- Ambos endpoints requieren la autoridad `ACADEMIC_FICHA_VIEW`.
- Scope `GLOBAL`: permite consultar todos los centros, respetando los filtros enviados.
- Scope `TRAINING_CENTER`: fuerza el `training_center_id` del JWT.
- Si un usuario con scope `TRAINING_CENTER` intenta consultar otro centro, el reporte retorna una pagina vacia.
- No se habilitaron scopes de ficha propia porque el contrato no los declara para estos reportes.

## Arquitectura y observabilidad

- El caso de uso se encuentra en `academic-core`, sin dependencias de Spring, JPA o PostgreSQL.
- La consulta SQL y el join pertenecen al adaptador de persistencia.
- Las consultas estan marcadas como transacciones de solo lectura.
- Las columnas de ordenamiento se resuelven mediante listas permitidas para evitar SQL dinamico inseguro.
- El controlador usa la observacion `ficha.reports.controller`.
- El adaptador de persistencia usa la observacion `ficha.reports.persistence`.
- La configuracion existente de Micrometer/OpenTelemetry exporta las trazas mediante OTLP.

## Archivos principales

- `academic-core/src/main/java/co/sena/academic/application/port/in/QueryFichaReportsUseCase.java`
- `academic-core/src/main/java/co/sena/academic/application/port/out/FichaReportRepositoryPort.java`
- `academic-core/src/main/java/co/sena/academic/application/usecase/FichaReportService.java`
- `academic-adapters/src/main/java/co/sena/academic/adapter/in/rest/FichaReportController.java`
- `academic-adapters/src/main/java/co/sena/academic/adapter/in/rest/mapper/FichaReportRestMapper.java`
- `academic-adapters/src/main/java/co/sena/academic/adapter/out/persistence/FichaReportPersistenceAdapter.java`
- `academic-core/src/test/java/co/sena/academic/application/usecase/FichaReportServiceTest.java`
- `academic-adapters/src/test/java/co/sena/academic/adapter/in/rest/FichaReportControllerIT.java`

## Criterios de aceptacion

| Criterio | Estado | Evidencia |
| --- | --- | --- |
| Exponer `GET /reports/enrollment-by-ficha` | Implementado | `FichaReportController.enrollmentByFicha` |
| Proyectar capacidad, estado, codigo y nombre del programa | Implementado | `FichaReportPersistenceAdapter.findEnrollmentByFicha` |
| Aplicar filtros y paginacion | Implementado | Controlador, caso de uso y adaptador |
| Aplicar `ACADEMIC_FICHA_VIEW` y scope de centro | Implementado | `@PreAuthorize`, `FichaAccessContextResolver`, `FichaReportService` |
| Exponer `GET /reports/ficha-progress` | Implementado | `FichaReportController.fichaProgress` |
| Calcular dias transcurridos y restantes | Implementado | `FichaReportService.toProgressItem` |
| Detectar ficha retrasada no terminal | Implementado | `FichaReportService.toProgressItem` |
| Mantener valores nullable cuando no existe `expected_end_date` | Implementado | Caso de uso, DTO y pruebas |
| Usar schemas OpenAPI congelados | Verificado | `EnrollmentByFichaReportItem`, `FichaProgressReportItem` |
| Instrumentar trazas OpenTelemetry | Implementado | Observaciones de controlador y persistencia |

## Pruebas

### Suite unitaria

```powershell
mvn -q -pl academic-adapters -am test
```

Resultado: `PASS`.

Incluye pruebas deterministas para:

- ficha a tiempo;
- ficha retrasada;
- ficha sin `expected_end_date`;
- ficha terminal con `actual_end_date`;
- aislamiento del scope `TRAINING_CENTER`.

### Empaquetado

```powershell
mvn -q -pl academic-management-api -am package -DskipTests
```

Resultado: `PASS`.

### Integracion con PostgreSQL real

```powershell
mvn -q -pl academic-adapters -am verify
```

Resultado local: `BLOCKED BY LOCAL ENVIRONMENT`.

Testcontainers no encontro un daemon Docker disponible. `FichaReportControllerIT` queda preparado para ejecutarse en CI o QA con PostgreSQL 16 y cubre:

- multiples fichas y programas;
- proyeccion exacta de HU-ACAD-14;
- filtros, rango inclusivo/exclusivo y paginacion;
- scope `TRAINING_CENTER`;
- fichas a tiempo, retrasadas y sin fecha esperada;
- respuestas `401` y `403`.

## Pull request

| Repositorio | PR | Destino |
| --- | --- | --- |
| `design-software-academic-management-service` | [Crear PR hacia develop](https://github.com/code-sena/design-software-academic-management-service/compare/develop...hu-acad-12-dev?quick_pull=1) | `develop` |

La rama esta publicada. La creacion automatica del PR quedo bloqueada en la estacion local porque no hay navegador, GitHub CLI ni token de GitHub disponibles.

## Descripcion del PR en ingles

### Title

`feat(academic-management): add enrollment and ficha progress reports`

### Summary

This PR implements HU-ACAD-14 and HU-ACAD-15 in `academic-management-service`.

- Adds `GET /api/v1/reports/enrollment-by-ficha` with training center, program, status, date range, pagination, and sorting filters.
- Adds `GET /api/v1/reports/ficha-progress` with elapsed days, nullable remaining days, and delayed-ficha detection.
- Enforces the `ACADEMIC_FICHA_VIEW` feature and the `GLOBAL` / `TRAINING_CENTER` access scopes.
- Keeps reporting inside the Academic domain and uses read-only persistence projections.
- Adds Micrometer/OpenTelemetry observations for the report controller and persistence adapter.

### Acceptance criteria

- HU-ACAD-14 returns the frozen `EnrollmentByFichaReportItem` projection, including program code and name from `training_program`.
- HU-ACAD-14 supports all contract filters, offset pagination, and center-scoped access.
- HU-ACAD-15 returns the frozen `FichaProgressReportItem` projection.
- HU-ACAD-15 covers on-time, delayed, terminal, and missing `expected_end_date` scenarios.
- `days_remaining` remains `null` when the expected end date is unavailable or the ficha is terminal.
- A ficha is delayed only after `expected_end_date` and while it is not `COMPLETED` or `CANCELLED`.
- Both endpoints require `ACADEMIC_FICHA_VIEW` and return `401`/`403` according to the platform security configuration.

### Validation

- Unit tests: passed.
- Application packaging: passed.
- Integration tests are implemented with PostgreSQL 16 and Testcontainers.
- Local integration execution is blocked because Docker is not available on the workstation; CI/QA must run `mvn -q -pl academic-adapters -am verify` with Docker enabled.
- `git diff --check`: passed.

### Notes for reviewers

- No database migration is required.
- No OpenAPI route or schema was modified; the implementation follows the already frozen contract.
- The source branch is `hu-acad-12-dev` and the only allowed target for this PR is `develop`.

## Validaciones solicitadas a QA y arquitectura

- Ejecutar `mvn -q -pl academic-adapters -am verify` con Docker habilitado.
- Validar las proyecciones contra PostgreSQL con multiples programas y centros.
- Confirmar que `to` sea exclusivo y `from` inclusivo sobre `start_date`.
- Confirmar aislamiento por `training_center_id` para tokens con scope `TRAINING_CENTER`.
- Revisar trazas `ficha.reports.controller` y `ficha.reports.persistence` en el collector OpenTelemetry.
- Confirmar que el PR solo tenga como destino `develop`.
