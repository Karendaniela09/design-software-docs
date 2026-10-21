# Entrega Develop HU-MON-002 / HU-02-monitoring

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

Fecha: 2026-10-14

Desarrollador: Kevin Andrey Culma Gomez

## Repositorios y ramas revisadas

| Repositorio | Rama | Estado |
| --- | --- | --- |
| `design-software-monitoring-service` | `hu-02-dev` | Modificado para PR hacia `develop` |
| `design-software-docs` | `hu-05-dev` | Modificado para alinear RBAC con contrato |
| `design-software-monitoring-db` | `hu-09-dev` | Revisado como base de HU-MON-001, sin cambios nuevos para esta HU |

## Pull requests creados

| Repositorio | Rama origen | Rama destino | PR | Commit |
| --- | --- | --- | --- | --- |
| `design-software-monitoring-service` | `hu-02-dev` | `develop` | https://github.com/code-sena/design-software-monitoring-service/pull/3 | `3142579` |
| `design-software-docs` | `hu-05-dev` | `main` | https://github.com/code-sena/design-software-docs/pull/287 | `276610e` |

Antes de implementar se actualizaron las ramas padre del servicio:

- `develop`
- `qa`
- `staging`
- `main`

La rama `hu-02-dev` se creo sobre `hu-01-dev`, porque HU-MON-001 es bloqueante para HU-MON-002 y contiene el repositorio SQLAlchemy y el modelo persistente que esta historia debe reutilizar.

## Alcance implementado

La implementacion se realizo para HU-MON-002: completar `monitoring-api` segun el contrato OpenAPI.

El objetivo principal fue exponer la API REST de monitoreo bajo `/api/v1`, respetando `monitoring.yaml` como contrato autoritativo y reutilizando la persistencia de HU-MON-001.

Se implementaron:

- endpoints de salud;
- catálogos de KPI y alertas;
- catálogos de solo lectura `risk_level` y `kpi_status`;
- consulta de seguimientos de ficha;
- registro y consulta de sesiones de seguimiento;
- registro y consulta de KPI tracking;
- consulta y resolucion de alertas generadas;
- CRUD funcional de planes de mejoramiento;
- reportes propios de Monitoring;
- seguridad con Bearer JWT y features RBAC;
- envelope estandar de errores;
- pruebas de contrato HTTP.

## Documentacion fuente revisada

- `design-software-docs/07-api/contracts/openapi/monitoring.yaml`
- `design-software-docs/09-microservices/services/01-iam-service/rbac-design.md`
- `design-software-docs/09-microservices/services/08-monitoring-service/data-model.md`

## Cambios realizados

### 1. API FastAPI alineada al contrato

Archivos:

- `design-software-monitoring-service/apps/api/main.py`
- `design-software-monitoring-service/src/monitoring/adapter/inbound/http/router.py`

Cambios:

- El router se expone con prefijo `/api/v1`.
- `/health` queda disponible sin autenticacion.
- Se implementaron las rutas definidas en `monitoring.yaml`.
- Se elimino el endpoint legado `/kpis`; el registro de KPI queda en `POST /api/v1/kpi-trackings`.
- Los endpoints protegidos validan token Bearer y feature RBAC.
- La falta de token responde `401`.
- Los permisos insuficientes responden `403`.
- Los errores funcionales usan envelope con `error.code`, `error.message` y `error.details`.

### 2. Catálogos y soft delete

Archivo:

- `design-software-monitoring-service/src/monitoring/adapter/inbound/http/router.py`

Cambios:

- `kpi_type` y `alert_type` tienen CRUD completo.
- `DELETE` en catálogos aplica soft delete con `is_active = false`.
- Conflictos de codigo retornan `409` con `CATALOG_CODE_CONFLICT`.
- `risk_level` y `kpi_status` quedan como solo lectura.

### 3. Seguimiento de fichas y sesiones

Archivo:

- `design-software-monitoring-service/src/monitoring/adapter/inbound/http/router.py`

Cambios:

- `ficha_tracking` queda solo lectura por REST.
- Filtros por `ficha_id`, `assigned_instructor_id` y `overall_status`.
- `tracking_session` permite listar, crear y consultar detalle.
- La creacion valida `session_type`, conteos no negativos y porcentaje de avance entre 0 y 100.
- `attendance_percentage` se conserva como calculo de BD segun HU-MON-001.

### 4. KPI tracking

Archivo:

- `design-software-monitoring-service/src/monitoring/adapter/inbound/http/router.py`

Cambios:

- Se implemento `GET /api/v1/kpi-trackings`.
- Se implemento `POST /api/v1/kpi-trackings`.
- Se implemento `GET /api/v1/kpi-trackings/{id}`.
- La paginacion usa cursor para colecciones de crecimiento continuo.
- Los filtros cubren ficha, tipo, estado y rango de fechas.

### 5. Alertas generadas y planes de mejoramiento

Archivo:

- `design-software-monitoring-service/src/monitoring/adapter/inbound/http/router.py`

Cambios:

- `generated_alert` permite listar, consultar detalle y resolver.
- Resolver una alerta ya resuelta es idempotente.
- `improvement_plan` permite crear, listar, consultar y actualizar.
- Se validan transiciones:
  - `PENDING -> IN_PROGRESS`
  - `IN_PROGRESS -> COMPLETED`
  - `IN_PROGRESS -> CANCELLED`
- Transiciones invalidas retornan `409` con `INVALID_STATE_TRANSITION`.

### 6. Reportes propios de Monitoring

Archivo:

- `design-software-monitoring-service/src/monitoring/adapter/inbound/http/router.py`

Cambios:

- `GET /api/v1/reports/kpi-summary` calcula la ultima medicion por ficha y tipo de KPI.
- `GET /api/v1/reports/indicators` agrega fichas por estado y nivel de riesgo.
- Los reportes consultan solo tablas del dominio Monitoring.
- Las referencias externas se mantienen como UUID.

### 7. Metadata SQLAlchemy ampliada

Archivo:

- `design-software-monitoring-service/src/monitoring/adapter/outbound/persistence/repo.py`

Cambios:

- Se agregaron tablas y columnas necesarias para los endpoints REST.
- Se expuso `session_factory` para reutilizar transacciones desde el adaptador HTTP.
- Se mantuvo el dominio sin dependencias de SQLAlchemy.

### 8. RBAC alineado con OpenAPI

Archivo:

- `design-software-docs/09-microservices/services/01-iam-service/rbac-design.md`

Cambios:

- Se agrego `MON_CATALOG_MANAGE`.
- Se agrego `MON_REPORT_VIEW`.
- Ambos features quedaron registrados en la tabla de `MOD_MONITORING` y en la matriz de permisos.

Motivo:

- `monitoring.yaml` ya exigia esos features mediante `x-required-feature`.
- El documento RBAC no los tenia registrados.

## Criterios de aceptacion revisados

### AC-001 Endpoints bajo `/api/v1`

Estado: IMPLEMENTADO.

Evidencia:

- `apps/api/main.py`
- `tests/test_monitoring_http_contract.py`

Prueba:

```powershell
python -m pytest -q
```

### AC-002 CRUD de catálogos segun reglas

Estado: IMPLEMENTADO.

Evidencia:

- `src/monitoring/adapter/inbound/http/router.py`

Incluye:

- CRUD completo para `kpi_type`.
- CRUD completo para `alert_type`.
- Soft delete con `is_active = false`.
- `risk_level` y `kpi_status` solo lectura.

### AC-003 `ficha_tracking` solo lectura con filtros

Estado: IMPLEMENTADO.

Evidencia:

- `GET /api/v1/ficha-trackings`
- `GET /api/v1/ficha-trackings/{id}`

Filtros:

- `ficha_id`
- `assigned_instructor_id`
- `overall_status`

### AC-004 `tracking_session`

Estado: IMPLEMENTADO.

Evidencia:

- `GET /api/v1/ficha-trackings/{id}/tracking-sessions`
- `POST /api/v1/ficha-trackings/{id}/tracking-sessions`
- `GET /api/v1/ficha-trackings/{id}/tracking-sessions/{session_id}`

Validaciones:

- `session_type` permitido.
- Conteos no negativos.
- `curriculum_progress_percentage` entre 0 y 100.

### AC-005 `kpi_tracking`

Estado: IMPLEMENTADO.

Evidencia:

- `GET /api/v1/kpi-trackings`
- `POST /api/v1/kpi-trackings`
- `GET /api/v1/kpi-trackings/{id}`

Nota:

- `monitoring.yaml` define `POST /kpi-trackings`; por eso se elimino el endpoint legado `/kpis`.

### AC-006 `generated_alert`

Estado: IMPLEMENTADO.

Evidencia:

- `GET /api/v1/generated-alerts`
- `GET /api/v1/generated-alerts/{id}`
- `PUT /api/v1/generated-alerts/{id}/resolve`

Regla:

- La doble resolucion es idempotente.

### AC-007 `improvement_plan`

Estado: IMPLEMENTADO.

Evidencia:

- `POST /api/v1/improvement-plans`
- `GET /api/v1/improvement-plans`
- `GET /api/v1/improvement-plans/{id}`
- `PUT /api/v1/improvement-plans/{id}`

Transiciones invalidas:

- Retornan `409 INVALID_STATE_TRANSITION`.

### AC-008 Reportes propios del dominio

Estado: IMPLEMENTADO.

Evidencia:

- `GET /api/v1/reports/kpi-summary`
- `GET /api/v1/reports/indicators`

Restriccion:

- No consultan otros servicios.
- Solo usan tablas propias de Monitoring.

### AC-009 Seguridad JWT y RBAC

Estado: IMPLEMENTADO.

Evidencia:

- Dependencia `auth()` en `router.py`.
- Pruebas de `401` y `403` en `tests/test_monitoring_http_contract.py`.
- `rbac-design.md` alineado con `MON_CATALOG_MANAGE` y `MON_REPORT_VIEW`.

### AC-010 Errores estandar

Estado: IMPLEMENTADO.

Evidencia:

- `error_body()`
- `_http_error()`

Codigos cubiertos:

- `CATALOG_CODE_CONFLICT`
- `INVALID_STATE_TRANSITION`
- `UNAUTHORIZED`
- `FORBIDDEN`
- `NOT_FOUND`
- `BAD_REQUEST`
- `SERVICE_UNAVAILABLE`

### AC-011 Paginacion

Estado: IMPLEMENTADO.

Evidencia:

- `_page()` para catálogos, planes y reportes.
- `_cursor()` para colecciones de crecimiento continuo.

### AC-012 Pruebas de contrato y HTTP

Estado: IMPLEMENTADO.

Evidencia:

- `tests/test_monitoring_http_contract.py`

## Verificaciones ejecutadas

### Pruebas automatizadas

Comando:

```powershell
python -m pytest -q
```

Resultado:

```text
6 passed, 3 skipped
```

Observacion:

- Las 3 pruebas omitidas son integraciones PostgreSQL existentes que requieren `MONITORING_TEST_DATABASE_URL`.

### Compilacion Python

Comando:

```powershell
python -m compileall apps src tests
```

Resultado:

```text
PASS
```

### Validacion de whitespace

Comando:

```powershell
git diff --check
```

Resultado:

```text
PASS
```

## Discrepancias resueltas

### `POST /kpi-trackings` vs `/kpis`

Decision aplicada:

- Se conserva `POST /api/v1/kpi-trackings` porque existe en `monitoring.yaml`.
- Se elimina `/api/v1/kpis` para no exponer rutas fuera del contrato.

### Features RBAC faltantes

Decision aplicada:

- Se agregan `MON_CATALOG_MANAGE` y `MON_REPORT_VIEW` a `rbac-design.md`.
- El servicio mantiene los features declarados por `monitoring.yaml`.

## Pendientes para QA

- Ejecutar pruebas de integracion con PostgreSQL real configurando `MONITORING_TEST_DATABASE_URL`.
- Validar que la BD de HU-MON-001 este aplicada antes de probar la API.
- Probar flujos HTTP con token real emitido por IAM.
- Validar que `MON_CATALOG_MANAGE` y `MON_REPORT_VIEW` existan en la semilla/configuracion real de IAM cuando se integren ambientes.

## Resultado QA sugerido

Estado: LISTO PARA PR HACIA `develop` Y VALIDACION TECNICA.

Ramas:

- `design-software-monitoring-service` -> `hu-02-dev`
- `design-software-docs` -> `hu-05-dev`

QA y arquitectura deben validar:

- cumplimiento de rutas contra `monitoring.yaml`;
- seguridad `401` y `403`;
- permisos RBAC nuevos;
- CRUD de catalogos;
- registro y consulta de KPI;
- sesiones de seguimiento;
- resolucion idempotente de alertas;
- transiciones de planes de mejoramiento;
- reportes calculados solo desde tablas de Monitoring.
