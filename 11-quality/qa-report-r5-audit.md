# Informe técnico - Auditoría E2E y R5

**Responsable:** Juan Pablo Gómez Perdomo  
**Ficha:** ADSO 3145555  
**Dominio:** Auditoría  
**Fecha de verificación:** 20 y 21 de octubre de 2026  
**Estado:** implementación validada localmente; R5 integrado en `develop` de `design-software-audit-service`.

## 1. Alcance implementado y verificado

El dominio de Auditoría registra acciones relevantes del sistema, las conserva
de forma inmutable y permite su consulta controlada por IAM.

| Capacidad implementada | Verificación realizada |
|---|---|
| Consumo de eventos AMQP | `audit-worker` consume desde `audit-events`, valida el envelope y persiste. |
| Registro append-only | Los eventos válidos se almacenan en PostgreSQL, esquema `audit`, sin operaciones funcionales de edición o borrado. |
| Idempotencia | Un `event_id` repetido no genera una segunda evidencia. |
| Retry y DLQ | Eventos inválidos o no procesables siguen el flujo retry/DLQ sin bloquear la cola principal. |
| Consulta | `audit-query-api` ofrece listado paginado, filtros, detalle y payload. |
| Exportación | CSV y JSON disponibles con la capability `AUDIT_EXPORT`. |
| Autorización | JWT/JWKS, `AUDIT_LOG_VIEW`, `AUDIT_EXPORT` y scopes `GLOBAL`/`TRAINING_CENTER`. |
| Interfaz | `audit-mfe` cargado en `web-shell` por la ruta `/audit/auditoria`. |

## 2. Enrutamiento validado

```text
Productor → RabbitMQ:5672 / audit-events → audit-worker → PostgreSQL:15432 / audit

Navegador → web-shell:5000 /audit/auditoria → audit-mfe → audit-query-api:18081
Navegador → /api/v1/* → Traefik:18080 /iam → IAM → JWT/JWKS/RBAC
```

El flujo comprobado utiliza mensajería real para la escritura, PostgreSQL para
conservar el histórico, IAM para autenticación y autorización, y el shell/MFE
para la consulta del usuario.

## 3. Repositorios y trazabilidad

| Componente | Repositorio oficial | Fork individual | Directorio local usado |
|---|---|---|---|
| Servicio, worker y R5 | [code-sena/audit-service](https://github.com/code-sena/design-software-audit-service) | [Juan282007/audit-service](https://github.com/Juan282007/design-software-audit-service) | `C:\Users\juanp\Desktop\design-software-audit-service` |
| Base de datos | [code-sena/audit-db](https://github.com/code-sena/design-software-audit-db) | [Juan282007/audit-db](https://github.com/Juan282007/design-software-audit-db) | `C:\Users\juanp\Desktop\design-software-audit-db` |
| Microfrontend | [code-sena/audit-mfe](https://github.com/code-sena/design-software-audit-mfe) | [Juan282007/audit-mfe](https://github.com/Juan282007/design-software-audit-mfe) | `C:\Users\juanp\Desktop\design-software-audit-mfe` |
| Host de MFEs | [code-sena/web-shell](https://github.com/code-sena/design-software-web-shell) | [Juan282007/web-shell](https://github.com/Juan282007/design-software-web-shell) | `C:\Users\juanp\Desktop\design-software-web-shell` |
| Infraestructura | [code-sena/docker-infra](https://github.com/code-sena/design-software-docker-infra) | [Juan282007/docker-infra](https://github.com/Juan282007/design-software-docker-infra) | `C:\Users\juanp\Desktop\design-software-docker-infra` |
| IAM | [code-sena/iam-service](https://github.com/code-sena/design-software-iam-service) | [Juan282007/iam-service](https://github.com/Juan282007/design-software-iam-service) | `C:\Users\juanp\Desktop\design-software-iam-service` |
| Datos IAM | [code-sena/iam-db](https://github.com/code-sena/design-software-iam-db) | [Juan282007/iam-db](https://github.com/Juan282007/design-software-iam-db) | `C:\Users\juanp\Desktop\design-software-iam-db` |
| Documentación | [code-sena/docs](https://github.com/code-sena/design-software-docs) | [Juan282007/docs](https://github.com/Juan282007/design-software-docs) | `C:\Users\juanp\Desktop\design-software-docs` |

La implementación R5 se integró en la rama oficial `develop` mediante el
[PR #5](https://github.com/code-sena/design-software-audit-service/pull/5).
El fork de `Juan282007` y los directorios de Desktop respaldan la trazabilidad
individual y la reproducción local.

## 4. Implementación R5

| Criterio | Artefacto implementado | Resultado verificado |
|---|---|---|
| Pact proveedor | `contracts/pact/audit-mfe-audit-query-api.json` y `cmd/audit-contract-provider` | La interacción paginada respondió `200`, `Content-Type: application/json` y body compatible. |
| OpenAPI compatible | `api/openapi/audit.yaml` y `scripts/check-openapi-contract.sh` | `oasdiff` contra `origin/develop`: `No changes detected`. |
| Cambio incompatible bloqueado | `scripts/test-openapi-contract-gate.sh` | Quitar temporalmente `/audit-records` produjo `api-path-removed-without-deprecation` y exit `1`. |
| Schema de eventos | `api/events/audit-consumed-event.schema.json` | `TestCanonicalEventSchemaMatchesWorkerEnvelopeRules`: `PASS`. |
| Gate CI | `.github/workflows/r5-contract-gates.yml` | Check `R5 / contract compatibility` para PRs hacia `develop`. |

El ADR correspondiente es
[ADR-014](https://github.com/code-sena/design-software-docs/blob/docs/r5-audit-contract-compatibility/05-architecture/decisions/records/ADR-014-audit-r5-contract-compatibility.md).

## 5. Pruebas y resultados observados

| Verificación | Resultado |
|---|---|
| `go test ./...` en audit-service | Correcto. |
| Build de `audit-query-api`, `audit-worker` y `audit-contract-provider` | Correcto. |
| Contrato schema/worker | `PASS`. |
| `TestWorkerConsumesCanonicalEventE2E` | `PASS`. |
| `TestWorkerDeduplicatesAndRoutesInvalidEnvelopeE2E` | `PASS`. |
| Pact positivo | Estado, cabecera y body compatibles. |
| OpenAPI positivo | Sin cambios incompatibles. |
| OpenAPI negativo controlado | Fallo detectado correctamente, exit `1`. |
| IAM | `GET /iam/health` devolvió `UP`. |
| Audit API | `GET /api/v1/health` devolvió `status: ok`. |
| Mínimo privilegio de BD | Cuenta lectora permitió `SELECT` y rechazó `INSERT`. |
| audit-mfe | 43 pruebas aprobadas y build exitoso. |
| web-shell | 106 pruebas aprobadas y build exitoso. |
| Control de acceso | `200` autorizado, `401` sin token y `403` sin capability. |

## 6. Métricas de evidencia

| Indicador | Resultado |
|---|---:|
| Fronteras de contrato cubiertas | 3: HTTP/OpenAPI, Pact y evento AMQP/JSON Schema. |
| Gates negativos comprobados | 2: respuesta Pact incompatible y ruta OpenAPI eliminada temporalmente. |
| Pruebas de integración AMQP | 2 aprobadas. |
| Pruebas unitarias del MFE | 43 aprobadas. |
| Pruebas del web shell | 106 aprobadas. |
| Health checks confirmados | IAM y Audit API. |

## 7. Conclusión técnica

Auditoría quedó validada de extremo a extremo en local: un evento atraviesa
RabbitMQ, el worker lo valida y persiste sin duplicación, y un usuario
autorizado lo consulta o exporta desde el MFE integrado en el shell. R5 añade
controles ejecutables de compatibilidad para API, frontend y eventos, incluyendo
pruebas negativas que detectan cambios incompatibles antes de integrarlos.
