# reference-data-service

> Estado: 🟡 Revisión | Última actualización: 2026-10-24
> Autor: Kevin Andrey Culma (Arquitecto) | Equipo: Arquitectura.

| Campo | Valor |
|---|---|
| Módulo | M2 + M4 |
| App repo | `design-software-reference-data-service` |
| DB repo | `design-software-reference-data-db` |
| Stack | Go |
| Deployables | reference-data-api |
| Estado observado | Implementado con API HTTP, seguridad JWT/JWKS y publicación AMQP opcional. |

## Responsabilidad

Jerarquía institucional, centros de formación, unidades institucionales, catálogos y parámetros.

## Persistencia

- Esquemas: institutional_structure, parameterization
- Tablas: institutional_structure.department, institutional_structure.institutional_unit, institutional_structure.macroregion, institutional_structure.microregion, institutional_structure.municipality, institutional_structure.training_center, parameterization.catalog, parameterization.catalog_detail, parameterization.parameter

## API detectada

Todas las rutas del contrato (`servers: /api/v1`, ver [`reference-data.yaml`](../../../07-api/contracts/openapi/reference-data.yaml) y [contract.md](./components/reference-data-api/contract.md)) se sirven bajo `/api/v1`. Las rutas sin ese prefijo responden 404. Por el edge se publican como `/reference-data/api/v1/...` (ADR-022 §3).

| Metodo | Ruta | Fuente |
|---|---|---|
| GET | `/api/v1/health` | `.\design-software-reference-data-service\cmd\reference-data-api\main.go` |
| GET | `/api/v1/health/live` | `.\design-software-reference-data-service\cmd\reference-data-api\main.go` |
| GET | `/api/v1/health/ready` | `.\design-software-reference-data-service\cmd\reference-data-api\main.go` |
| GET | `/health`, `/health/live`, `/health/ready` | Mismos handlers en la raíz, para sondas de contenedor y scripts locales; no los enruta el edge. |

## Configuración

- `HU_REF_018_ADMIN_EMAIL`
- `HU_REF_018_ADMIN_PASSWORD`
- `HU_REF_018_IAM_BASE_URL`
- `HU_REF_018_LEARNER_EMAIL`
- `HU_REF_018_LEARNER_PASSWORD`
- `IAM_JWKS_URL`
- `IAM_JWT_ISSUER`
- `MESSAGE_BROKER_URL`
- `OTEL_EXPORTER_OTLP_ENDPOINT`
- `OTEL_EXPORTER_OTLP_INSECURE`
- `PORT`
- `REFERENCE_DATA_AMQP_URL`
- `REFERENCE_DATA_DATABASE_URL`
- `REFERENCE_DATA_JWKS_HTTP_ALLOWED_HOSTS`
- `REFERENCE_DATA_TEST_DSN`

`IAM_JWKS_URL` debe ser `https` o `http` hacia loopback. Para validar el JWKS de IAM por la red interna (por ejemplo `http://iam-api:8080/api/v1/auth/.well-known/jwks.json` desde el contenedor propio del servicio), `REFERENCE_DATA_JWKS_HTTP_ALLOWED_HOSTS` lista, separados por comas, los hosts exactos que pueden usar `http` (sin esquema, puerto ni comodines; ejemplo: `iam-api`). Vacía, conserva el comportamiento estricto. No relaja la validación de firma, emisor, expiración ni `kid`. Es el mismo artefacto en los 4 ambientes: solo cambia el valor inyectado (ADR-022 §6).

## Notas

Servicio base para catálogos consumidos por otros dominios.

## Integración HU-REF-020 y reto R1 — docs primero

Esta adaptación está en revisión; no se declara Done·Dev antes de los PR originales y las validaciones. Se reutilizan las pantallas, seguridad y outbox de la base existente. IAM conserva su esquema/usuarios y su propio servicio; los ajustes de seguridad de pruebas pertenecen a iam-db, no al micro de Reference Data.

- [ADR-020: integración real](../../../05-architecture/decisions/records/ADR-020-reference-data-iam-e2e-integration.md).
- [ADR-021: resiliencia](../../../05-architecture/decisions/records/ADR-021-reference-data-resilient-messaging.md).
- [Modelo y changesets de R1](./data-model.md), [eventos](./events.md), [runbook](./runbook.md).
- [Plan de ejecución](../../../10-devops/reference-data-integration.md), [criterios y evidencia](../../../11-quality/reference-data-hu-ref-020-r1-validation.md).

Los ADR/informes viven solo en docs; los PR de código los referencian sin duplicarlos.
