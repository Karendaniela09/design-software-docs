# R5 — Compatibilidad de contratos de Auditoría

**Responsable:** Juan Pablo Gómez Perdomo  
**Servicio:** `audit-service`  
**Implementación:** `feat/r5-audit-contract-compatibility`

## Objetivo

R5 protege la comunicación entre Auditoría, su MFE y los servicios productores.
No es una historia funcional adicional: es una garantía para que cambios
posteriores no rompan el flujo E2E que ya funciona.

## Matriz de entregables

| Criterio R5 | Fuente ejecutable | Evidencia |
|---|---|---|
| Pact consumidor/proveedor | `contracts/pact/audit-mfe-audit-query-api.json` y `cmd/audit-contract-provider` en `design-software-audit-service` | Verificación de estado `200`, `Content-Type` y body compatible. |
| Bloqueo de Pact incompatible | `scripts/test-pact-provider-gate.sh` | Una copia temporal exige `201`; el proveedor real entrega `200` y Pact falla. |
| OpenAPI semántico | `design-software-audit-service/api/openapi/audit.yaml`, versión `1.1.0` | Fuente canónica única; esta documentación la enlaza sin mantener una copia. |
| Bloqueo de breaking change | `oasdiff breaking --fail-on ERR` | Al eliminar `/audit-records`, devuelve `api-path-removed-without-deprecation` y código `1`. |
| Evento canónico | `api/events/audit-consumed-event.schema.json` | El worker valida el envelope antes de persistir. |
| Prueba de alineación | `TestCanonicalEventSchemaMatchesWorkerEnvelopeRules` | El schema y las reglas de `ParseEnvelope` permanecen alineados. |
| Decisión arquitectónica | `ADR-014-audit-r5-contract-compatibility.md` | Define responsabilidades y consecuencias. |

## Interfaces protegidas

### API HTTP

El contrato de consulta define:

- `GET /audit-records` para listado paginado con cursor y filtros.
- `GET /audit-records/{id}` para detalle y payload.
- `GET /audit-records/export` para CSV o JSON con `AUDIT_EXPORT`.
- `GET /health` sin autenticación para liveness.

Las operaciones de negocio requieren JWT y las features `AUDIT_LOG_VIEW` o
`AUDIT_EXPORT`. El alcance `GLOBAL` o `TRAINING_CENTER` restringe los datos
visibles y no se considera una decisión exclusiva del frontend.

### Evento AMQP

El worker consume desde el exchange `audit-events`, valida el envelope y
persiste de manera append-only. Un `event_id` repetido se deduplica; un
envelope inválido se reintenta o se envía a la DLQ. Esta política protege la
integridad del histórico cuando RabbitMQ redelivera un mensaje.

## Verificación local reproducible

Desde `design-software-audit-service`:

```powershell
$cache = Join-Path $env:TEMP 'audit-go-build-r5'
$env:GOCACHE = $cache
go test ./...
go test ./internal/adapter/in/amqp `
  -run TestCanonicalEventSchemaMatchesWorkerEnvelopeRules `
  -count=1 -v
go build ./cmd/audit-query-api
go build ./cmd/audit-worker
go build ./cmd/audit-contract-provider
```

Los scripts del repositorio inician el proveedor y usan imágenes fijadas por digest:

```bash
bash scripts/verify-pact-provider.sh
bash scripts/test-pact-provider-gate.sh
```

Resultado esperado: la interacción paginada aparece como `OK` para status,
cabeceras y body.

Para OpenAPI, se compara la especificación candidata contra la de
`origin/develop`. Después, el gate valida el incremento semántico: cambios
compatibles bajo `paths` requieren `MINOR`; metadatos compatibles requieren
`PATCH`; una ruptura se rechaza, aun si se incrementa `MAJOR`.

```bash
git show origin/develop:api/openapi/audit.yaml > /tmp/audit-base.yaml
bash scripts/check-openapi-contract.sh /tmp/audit-base.yaml api/openapi/audit.yaml
bash scripts/test-openapi-contract-gate.sh api/openapi/audit.yaml
```

La comparación actual no debe reportar cambios incompatibles. Para demostrar
el gate, se copia temporalmente `audit.yaml`, se elimina `/audit-records` y se
repite el comando: debe fallar con código distinto de cero. El archivo mutado
no se commitea.

## Relación con E2E

R5 no sustituye la prueba E2E. E2E demuestra el recorrido
`RabbitMQ → audit-worker → PostgreSQL → audit-query-api → audit-mfe → shell`.
R5 demuestra que los contratos de cada frontera siguen siendo compatibles para
que ese recorrido pueda repetirse después de futuros cambios.

## Criterio de cierre

La implementación técnica está realizada y validada localmente. Para el cierre
formal del reto, el workflow `R5 / contract compatibility` debe estar marcado
como check obligatorio en la protección de `develop`. También se debe conservar
la evidencia de un PR de prueba bloqueado por el check y luego corregido; esta
es una configuración y evidencia administrativa posterior al código.

El workflow ejecuta en cada PR hacia `develop`: pruebas Go y JSON Schema,
Pact positivo, Pact negativo, `oasdiff`, validación semántica de versión y la
mutación negativa de OpenAPI. Las imágenes de Docker se fijan por digest para
que la validación sea reproducible.
