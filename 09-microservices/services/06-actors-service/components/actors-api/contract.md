<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: contrato de API OpenAPI 3.1
fase: diseño api-first
estado: accepted
dependencias_entrada: 09-microservices/services/06-actors-service/data-model.md, 07-api/guidelines.md, 07-api/contracts/openapi/_shared.yaml, 01-iam-service/rbac-design.md (features MOD_ACTORS)
consumidores_siguientes: backend actors-service, frontend, scheduling-service (disponibilidad de instructores), monitoring-service, pruebas de contrato
tldr: CRUD de instructores/aprendices/empresas con sub-recursos anidados (áreas, contratos, competencias, excepciones de disponibilidad, historial de fichas), dominio de seguimiento (etapa productiva, visitas, planes de mejoramiento) y dos reportes propios. La fuente de verdad es actors.yaml.
decisiones_clave: OpenAPI publicable en 07-api/contracts/openapi/actors.yaml; sub-recursos que no tienen sentido fuera de su padre (áreas, contratos, competencias, excepciones, ficha-enrollments, visitas) se anidan (guidelines §3); learner sin is_active usa enrollment_status=CANCELLED como soft delete; activity_log es solo lectura (append-only)
halts_registrados: ninguno
-->

# Contrato — actors-api

> Estado: 🟢 Aceptado | Última actualización: 2026-08-06
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Arquitectura

> **Fuente de verdad (normativa):** el spec OpenAPI 3.1 en
> [`07-api/contracts/openapi/actors.yaml`](../../../../../07-api/contracts/openapi/actors.yaml).
> Este documento es la **narrativa** que lo explica; ante cualquier diferencia, **manda el
> `actors.yaml`**. Convenciones transversales en
> [07-api/guidelines.md](../../../../../07-api/guidelines.md).

## Autenticación
Todos los endpoints requieren `Authorization: Bearer <JWT>` emitido por `iam-service`. La
autorización se resuelve por **feature + scope** (RBAC), features del módulo `MOD_ACTORS`
(ver [rbac-design.md](../../../01-iam-service/rbac-design.md)).

Excepción interna servicio-a-servicio: los endpoints bajo
`/internal/learners/**` se protegen exclusivamente con **mTLS** entre servicios y no usan
Bearer JWT ni features RBAC. Diseño del mTLS interno (lista de CN por llamante y familia de
rutas, códigos de fallo): [security.md §3.5](../../security.md#35-internal-mtls-design-hu-act-492).

## Base URL
`/api/v1`

## Endpoints (derivados del modelo real)

### Empresas
CRUD completo, soft delete vía `is_active`.

| Método | Path | Descripción | Feature |
|--------|------|-------------|---------|
| `GET/POST` | `/companies` | Listar (filtros `nit`, `city_id`, `is_active`) / registrar empresa | `ACT_COMPANY_VIEW` / `ACT_COMPANY_MANAGE` |
| `GET/PUT/PATCH/DELETE` | `/companies/{id}` | Detalle / reemplazar / actualizar parcial / desactivar | `ACT_COMPANY_VIEW` / `ACT_COMPANY_MANAGE` |

### Instructores
`instructor_area`, `instructor_contract`, `competency_assignment` e
`instructor_availability_exception` se anidan bajo `/instructors/{id}` porque no tienen
sentido fuera de su instructor (guidelines §3).

| Método | Path | Descripción | Feature |
|--------|------|-------------|---------|
| `GET/POST` | `/instructors` | Listar (filtros `document_number`, `area`, `training_center_id`, `is_active`) / crear | `ACT_INSTRUCTOR_VIEW` / `ACT_INSTRUCTOR_MANAGE` |
| `GET/PUT/PATCH/DELETE` | `/instructors/{id}` | Detalle / reemplazar / actualizar parcial / desactivar | `ACT_INSTRUCTOR_VIEW` / `ACT_INSTRUCTOR_MANAGE` |
| `GET/POST` | `/instructors/{id}/areas` | Áreas tecnológicas / asignar área | `ACT_INSTRUCTOR_VIEW` / `ACT_INSTRUCTOR_MANAGE` |
| `DELETE` | `/instructors/{id}/areas/{area_id}` | Retirar área (soft delete) | `ACT_INSTRUCTOR_MANAGE` |
| `GET/POST` | `/instructors/{id}/contracts` | Historial de contratos / registrar contrato (cierra el vigente anterior) | `ACT_INSTRUCTOR_VIEW` / `ACT_INSTRUCTOR_MANAGE` |
| `GET/PUT` | `/instructors/{id}/contracts/{contract_id}` | Detalle / actualizar (p. ej. cerrar con `end_date`) | `ACT_INSTRUCTOR_VIEW` / `ACT_INSTRUCTOR_MANAGE` |
| `GET/POST` | `/instructors/{id}/competencies` | Competencias asignadas / asignar competencia | `ACT_INSTRUCTOR_VIEW` / `ACT_INSTRUCTOR_MANAGE` |
| `DELETE` | `/instructors/{id}/competencies/{competency_assignment_id}` | Revocar competencia (soft delete) | `ACT_INSTRUCTOR_MANAGE` |
| `GET/POST` | `/instructors/{id}/availability-exceptions` | Excepciones de disponibilidad (filtros `from`, `to`) / registrar bloqueo | `ACT_INSTRUCTOR_VIEW` / `ACT_INSTRUCTOR_MANAGE` |
| `DELETE` | `/instructors/{id}/availability-exceptions/{exception_id}` | Eliminar excepción | `ACT_INSTRUCTOR_MANAGE` |
| `GET` | `/instructors/{id}/activity-log` | Bitácora funcional (solo lectura, paginación por cursor) | `ACT_INSTRUCTOR_VIEW` |
| `GET` | `/instructors/{id}/fichas` | Fichas asignadas al instructor (HU-ACT-033); el instructor solo la suya; el aprendiz recibe 403 | `ACT_INSTRUCTOR_VIEW` |
| `GET/POST` | `/fichas/{fichaId}/instructors` | Instructores de una ficha (con `InstructorSummary`; el aprendiz solo la propia) / asignar instructor (`competency_id` opcional) | `ACT_INSTRUCTOR_VIEW` / `ACT_INSTRUCTOR_FICHA_ASSIGN` |
| `DELETE` | `/fichas/{fichaId}/instructors/{assignmentId}` | Retirar la asignación (borrado lógico) | `ACT_INSTRUCTOR_FICHA_ASSIGN` |

`GET /instructors` y `GET /instructors/{id}` devuelven `InstructorSummary` (sin correo, teléfono ni documento) al aprendiz, y solo para los instructores asignados a su ficha.

Registrar o eliminar una excepción de disponibilidad dispara el evento
`actors.instructor.availability_changed` (insumo del motor de horarios).

### Aprendices
`learner_ficha_enrollment` se anida bajo `/learners/{id}` (historial de traslados entre
fichas, no tiene sentido fuera del aprendiz).

| Método | Path | Descripción | Feature |
|--------|------|-------------|---------|
| `GET/POST` | `/learners` | Listar (filtros `document_number`, `ficha_id`, `enrollment_status`) / crear | `ACT_LEARNER_VIEW` / `ACT_LEARNER_MANAGE` |
| `GET/PUT/PATCH/DELETE` | `/learners/{id}` | Detalle / reemplazar / actualizar parcial / desvincular | `ACT_LEARNER_VIEW` / `ACT_LEARNER_MANAGE` |
| `GET/POST` | `/learners/{id}/ficha-enrollments` | Historial de fichas / inscribir o trasladar (cierra la inscripción vigente) | `ACT_LEARNER_VIEW` / `ACT_LEARNER_MANAGE` |
| `GET` | `/learners/{id}/activity-log` | Bitácora funcional (solo lectura, paginación por cursor) | `ACT_LEARNER_VIEW` |

`learner` no tiene columna `is_active` en el modelo de datos: `DELETE /learners/{id}` es un
soft delete implementado como `enrollment_status = CANCELLED`. Crear una inscripción de
ficha dispara `actors.learner.enrolled`.

### Endpoints internos de aprendices

| Método | Path | Descripción | Seguridad |
|--------|------|-------------|-----------|
| `GET` | `/internal/learners/by-user/{user_id}/active-ficha` | Resuelve la ficha activa de un aprendiz activo a partir del `user_id` de IAM. Retorna `200` con `learner_id` y `ficha_id`, `204` si no tiene ficha activa, `404` si no existe perfil activo de aprendiz, `409` si hay más de una ficha activa y `500` ante error técnico controlado. | mTLS |
| `GET` | `/internal/fichas/{ficha_id}/active-learners/count` | Cuenta las matrículas activas de una ficha para Academic Management. | Bearer JWT + `ACT_INTERNAL_FICHA_LEARNER_COUNT` |

### Endpoints internos de operación

Las rutas de operación requieren `ACT_INSTRUCTOR_MANAGE` y no deben publicarse a usuarios finales en el edge.

| Método | Path | Resultado |
|--------|------|-----------|
| `GET` | `/ops/actors/outbox/status` | Conteo de filas del outbox por estado. |
| `POST` | `/ops/actors/outbox/{eventId}/replay` | Reintenta un evento del outbox en estado `DEAD`; retorna `202` o `404`. |
| `POST` | `/ops/actors/iam-dlq/replay-one` | Reintenta un mensaje IAM de la DLQ; disponible cuando el consumidor IAM está habilitado. |

### Seguimiento (tracking)
`company_visit` se anida bajo `/productive-stages/{id}` (la visita solo existe en el
contexto de una etapa productiva). `actor_improvement_plan` es top-level porque referencia
un instructor **o** un aprendiz (arco exclusivo), no un único padre.

| Método | Path | Descripción | Feature |
|--------|------|-------------|---------|
| `GET/POST` | `/productive-stages` | Listar (filtros `learner_id`, `company_id`, `status`) / registrar inicio de etapa | `ACT_TRACKING_VIEW` / `ACT_TRACKING_MANAGE` |
| `GET/PUT` | `/productive-stages/{id}` | Detalle / actualizar avance, cierre o interrupción | `ACT_TRACKING_VIEW` / `ACT_TRACKING_MANAGE` |
| `POST` | `/productive-stages/{id}/visits` | Registra una visita de seguimiento | `ACT_PRODUCTIVE_STAGE_MANAGE` |
| `GET/POST` | `/improvement-plans` | Listar (filtros `instructor_id`, `learner_id`, `status`) / crear plan | `ACT_TRACKING_VIEW` / `ACT_TRACKING_MANAGE` |
| `GET/PUT` | `/improvement-plans/{id}` | Detalle / actualizar avance o cierre | `ACT_TRACKING_VIEW` / `ACT_TRACKING_MANAGE` |

Ni `productive_stage`, `company_visit` ni `actor_improvement_plan` exponen `DELETE`: son
registros históricos/regulatorios que se cierran vía cambio de `status`, nunca se borran.

## Paginación
Listados de recursos y reportes: `?page=&page_size=&sort=` (offset, guidelines §6) →
respuesta envuelta `{ "data": [...], "pagination": {"page","page_size","total_items","total_pages"} }`.
Las bitácoras (`activity-log`) usan paginación por **cursor** (`?cursor=&limit=`) por ser
colecciones append-only de crecimiento continuo.

## Ejemplo de respuesta (instructor)
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "document_type": "CC",
  "document_number": "1020304050",
  "first_name": "Laura",
  "last_name": "Ramírez",
  "full_name": "Laura Ramírez",
  "email": "laura.ramirez@sena.edu.co",
  "phone": null,
  "default_max_hours_per_week": 40.0,
  "is_active": true,
  "created_at": "2026-06-20T09:00:00Z",
  "updated_at": "2026-06-20T09:00:00Z"
}
```

## Reportes (dominio propio)

### `GET /reports/learner-tracking`

Seguimiento de aprendices por ficha, etapa y estado de inscripción. Cruza `learner`,
`learner_ficha_enrollment` (inscripción vigente) y `productive_stage` (si el aprendiz está
en etapa productiva). **Solo lectura**, paginación por **offset** (población acotada).

- **Feature requerido:** `ACT_REPORT_VIEW`.
- **Filtros:** `ficha_id`, `enrollment_status`, `from`, `to` (rango de `enrollment_date`).
- **Inventario:** Usuarios: coordinación académica, instructores de seguimiento ·
  Frecuencia: on-demand · Formato: JSON · Fuente: `actors_parameterization.learner`,
  `learner_ficha_enrollment`, `productive_stage`.

### `GET /reports/instructor-load`

Capacidad y disponibilidad de instructores. Cruza `instructor` (límite por defecto),
`instructor_contract` (límite vigente), `instructor_area`, `competency_assignment` y
`instructor_availability_exception` en el rango consultado. No incluye horas efectivamente
asignadas (eso vive en `scheduling-service`). **Solo lectura**, paginación por **offset**.

- **Feature requerido:** `ACT_REPORT_VIEW`.
- **Filtros:** `training_center_id`, `area`, `from`, `to` (rango para excepciones de disponibilidad).
- **Inventario:** Usuarios: coordinación, `scheduling-service` (consumo batch) ·
  Frecuencia: on-demand · Formato: JSON · Fuente: `actors_parameterization.instructor`,
  `instructor_contract`, `instructor_area`, `competency_assignment`,
  `instructor_availability_exception`.

## Formato de error estándar
Aplica el **envelope estándar de la plataforma** ([guidelines §7](../../../../../07-api/guidelines.md) /
`_shared.yaml#/components/schemas/Error`):

```json
{
  "error": {
    "code": "EXCLUSIVE_ARC_VIOLATION",
    "message": "El plan de mejoramiento debe referenciar exactamente un instructor o un aprendiz.",
    "details": [
      { "field": "instructor_id", "issue": "EXACTLY_ONE_OF_INSTRUCTOR_LEARNER_REQUIRED" }
    ],
    "trace_id": "uuid-v4"
  }
}
```

## Eventos publicados
`actors.instructor.availability_changed`, `actors.learner.enrolled`. Ver
[event-catalog.md](../../../../event-catalog.md).
