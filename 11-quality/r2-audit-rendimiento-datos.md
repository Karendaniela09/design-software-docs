# R2 — Rendimiento y datos de audit-service

> Estado: 🟢 Verificado | Última actualización: 2026-10-22
> Autor: Freinier Cardona | Equipo: Auditoría / ADSO 3145555

## Contexto

Este informe reúne la implementación y la evidencia reproducible del R2 del
plan de mejoramiento. La fuente ejecutable está repartida por responsabilidad:
`design-software-audit-service` contiene el escenario k6 y los scripts,
`design-software-audit-db` contiene la migración Liquibase y
`design-software-docker-infra` orquesta el entorno local. No se versionan
contraseñas, tokens, archivos `.env` ni resultados dependientes de una máquina.

## Alcance

Se evalúan exclusivamente los endpoints de lectura ya contratados:

- listado `GET /api/v1/audit-records`;
- detalle `GET /api/v1/audit-records/{id}`;
- exportación `GET /api/v1/audit-records/export`.

La prueba conserva IAM, `AUDIT_LOG_VIEW`, `AUDIT_EXPORT` y el alcance del
centro de formación. No agrega rutas, bypass de autenticación ni datos de
producción. La identidad usada el 2026-10-22 fue un `SYSTEM_ADMIN` local de
práctica creado únicamente en la base desechable. IAM emitió el JWT RS256 real
por `POST /api/v1/auth/login`, publicó su JWKS contractual y entregó
`AUDIT_LOG_VIEW:GLOBAL` y `AUDIT_EXPORT:GLOBAL`; no se fabricaron tokens.

## Entregables y trazabilidad

| Criterio R2 | Entrega versionada | Estado verificable |
|-------------|-------------------|--------------------|
| Carga k6: 50 VUs, 5 min, p95 < 300 ms, errores < 1 % | `design-software-audit-service/performance/k6/audit-query.js`, `scripts/run-r2-k6.ps1`, `performance/results/{before,after}` | Cumplido el 2026-10-22: `after` p95 46.46 ms, 0 % de errores, 235 611 iteraciones y 100 % de checks. |
| Tres `EXPLAIN (ANALYZE, BUFFERS)` antes y después | `performance/sql/r2-explain.sql`, `performance/sql/r2-seed.sql`, `scripts/run-r2-data.ps1` | Ejecutado en PostgreSQL 16 con fixture aislado de 200 002 filas. |
| Índices Liquibase con rollback | Changeset `r2-audit-performance-query-indexes` y SQL de rollback en `design-software-audit-db` | Rollback `rollback-count 1` probado y los tres índices quedaron ausentes. |
| Informe comparativo | Este documento y [ADR-015](../05-architecture/decisions/records/ADR-015-audit-r2-performance-data.md) | Resúmenes JSON y Markdown separados en `before/` y `after/`. |

## Validación del entorno

El 2026-10-21 se levantó un proyecto Compose aislado con PostgreSQL, RabbitMQ,
las 19 migraciones de audit-db, los roles técnicos y ambos procesos de
audit-service. Los endpoints internos `audit-query-api:8081/ready` y
`audit-worker:8082/ready` respondieron `200`; el worker mantuvo una conexión
activa con RabbitMQ. Esta comprobación no sustituye la prueba de carga ni
requiere credenciales de usuario IAM.

### Intento autenticado del 2026-10-21

Se ejecutó el arnés en el proyecto aislado `audit-r2-live` de Docker Desktop.
PostgreSQL quedó saludable, Liquibase de audit terminó al día y se verificó
el rollback/reaplicación del changeset R2. `audit-query-api:8081/ready` y
`audit-worker:8082/ready` devolvieron `200`.

La prueba se detuvo antes de k6 porque IAM no expuso JWKS (`000` al consultar
`/api/v1/auth/.well-known/jwks.json`). El primer arranque reveló que faltaba
el principal técnico local `design_software_app`; se creó exclusivamente en la
base temporal con el rol ya versionado `iam_admin`. El siguiente arranque falló
en `actorsActiveFichaClient` al resolver `E2E_IAM_MTLS_PASSWORD`. La imagen
reconstruida por Compose conservó ese placeholder, aunque no existe en el
checkout IAM inspeccionado, por lo que hay una discrepancia pendiente entre el
contexto efectivo de Compose y el checkout esperado.

No se generó `k6-summary.json`, no se ejecutaron 50 VUs durante cinco minutos
y no se registran total de solicitudes, p95 ni tasa de errores. No se usaron
tokens fabricados, mocks ni bypass de autorización.

### Cierre autenticado del 2026-10-22

El bloqueo anterior se cerró en el proyecto Compose aislado `audit-r2-final`.
Se aplicaron las migraciones IAM reales y se creó una cuenta de práctica con
las features de Auditoría. Para el perfil `SYSTEM_ADMIN` se dejó vacía en el
runtime de prueba la integración opcional `active-ficha` con Actors, que el
contrato solo consulta para perfiles exclusivamente `LEARNER`. La clave RSA,
las contraseñas y el token fueron efímeros y no se imprimieron ni versionaron.

Las dos corridas usaron exactamente 50 VUs durante 5 minutos, el mismo fixture
de 200 002 filas y la misma mezcla de lista, detalle y exportación:

| Fase | p95 HTTP | Errores audit | Checks | Iteraciones | Resultado |
|------|----------|----------------|--------|-------------|-----------|
| `before` (sin los tres índices R2) | 1 487.17 ms | 0.00 % | 15 111 / 15 111 | 15 110 | No cumple p95 |
| `after` (con los tres índices R2) | 46.46 ms | 0.00 % | 235 612 / 235 612 | 235 611 | Cumple |

El p95 disminuyó 96.88 % y el volumen de iteraciones completadas aumentó 15.59
veces. En ambas fases todos los endpoints devolvieron 200, por lo que la mejora
no depende de omitir rutas ni de aceptar errores.

## Resultados de datos

Las mediciones se repitieron el 2026-10-22 en PostgreSQL 16 y un proyecto
Compose aislado. Son evidencia de planificación y selección de índices; deben
repetirse si cambian el motor, recursos Docker o la forma del fixture.

| Consulta representada | Antes | Después | Efecto observado |
|-----------------------|-------|---------|------------------|
| Listado por centro y tipo de evento | incremental sort; 0.373 ms | index scan ordenado; 0.703 ms | Ambos sub-milisegundo; el plan optimizado evita el sort principal y la diferencia puntual es ruido de ejecución. |
| Listado por servicio origen | parallel sequential scan + sort; 116.178 ms | index scan ordenado; 0.545 ms | 99.53 % menos tiempo; elimina scan completo y sort. |
| Exportación por centro (160 002 filas) | incremental sort; 236.239 ms | index scan ordenado; 129.685 ms | 45.10 % menos tiempo; elimina incremental sort. |

Después de `rollback-count 1`, la comprobación `to_regclass` devolvió
`t | t | t`: los tres índices R2 estaban ausentes. El script los reaplica y
finaliza actualizando el esquema completo para no dejar el entorno a medio
estado.

## Implementación técnica

La solución versionada mantiene separadas las responsabilidades y no modifica
el workflow R5:

1. `performance/k6/audit-query.js` define un escenario `constant-vus` de 50
   VUs durante 5 minutos. `setup()` inicia sesión por el endpoint contractual
   `POST /api/v1/auth/login`; no fabrica JWT ni desactiva seguridad.
2. El token permanece en memoria durante la carga. Las solicitudes cubren 70 %
   listado, 20 % detalle y 10 % exportación, todas con checks de HTTP 200.
3. Los thresholds ejecutables son `http_req_duration: p(95)<300` y
   `audit_request_errors: rate<0.01`. Además, la aceptación exige cero checks
   fallidos.
4. `scripts/run-r2-data.ps1` crea un proyecto Compose aislado, aplica el
   baseline, inserta 200 002 registros, captura tres planes
   `EXPLAIN (ANALYZE, BUFFERS)`, aplica el changeset R2, vuelve a capturar los
   planes y comprueba el rollback antes de dejar el esquema actualizado.
5. `scripts/run-r2-k6.ps1` invoca el servicio `audit-k6`, crea siempre
   `performance/results/before/` y `performance/results/after/`, guarda el JSON
   de la fase y produce `summary.md`.
6. k6 incluye el retorno de `setup()` en `setup_data`; el script elimina esa
   propiedad antes de conservar la evidencia para que el Bearer token no quede
   versionado.

“Sin pasar credenciales al comando” significa que el correo y la contraseña de
la identidad de práctica se leen desde el `.env` local ignorado por Git. No
significa acceso anónimo: IAM, JWKS, issuer, features y los permisos
`AUDIT_LOG_VIEW`/`AUDIT_EXPORT` siguen siendo obligatorios. La automatización
existente no crea usuarios IAM ni genera credenciales; esa preparación pertenece
al entorno de prueba y debe usar únicamente datos de práctica.

## Ejecución exacta

Requisitos: Docker Desktop, Windows PowerShell 5.1 o PowerShell 7, los
repositorios hermanos y una identidad IAM de práctica con `AUDIT_LOG_VIEW` y
`AUDIT_EXPORT`. Desde la raíz del workspace, cree archivos locales a partir de
las plantillas; no los versione:

```powershell
Copy-Item .\design-software-audit-service\.env.example `
  .\design-software-audit-service\.env
Copy-Item .\design-software-audit-service\.env.worker.example `
  .\design-software-audit-service\.env.worker
Copy-Item .\docker-infra\design-software-docker-infra\.env.example `
  .\docker-infra\design-software-docker-infra\.env
```

Complete los placeholders de infraestructura y los valores
`AUDIT_LOAD_EMAIL`/`AUDIT_LOAD_PASSWORD` con la cuenta desechable. El JWT no se
configura ni se guarda: `setup()` lo obtiene mediante IAM.

Desde `design-software-audit-service`, prepare fixture, planes y rollback:

```powershell
.\scripts\run-r2-data.ps1 `
  -InfraDirectory ..\docker-infra\design-software-docker-infra `
  -EnvFile ..\docker-infra\design-software-docker-infra\.env `
  -ProjectName audit-r2
```

Con IAM, PostgreSQL, sus migraciones y `audit-query-api` activos, capture ambas
fases. `before` se ejecuta sin los tres índices R2 y `after` después de aplicar
el changeset:

```powershell
.\scripts\run-r2-k6.ps1 -Phase before `
  -InfraDirectory ..\docker-infra\design-software-docker-infra `
  -EnvFile ..\docker-infra\design-software-docker-infra\.env `
  -ProjectName audit-r2

.\scripts\run-r2-k6.ps1 -Phase after `
  -InfraDirectory ..\docker-infra\design-software-docker-infra `
  -EnvFile ..\docker-infra\design-software-docker-infra\.env `
  -ProjectName audit-r2
```

Al terminar, elimine exclusivamente el proyecto aislado y sus volúmenes:

```powershell
docker compose --project-name audit-r2 `
  --env-file ..\docker-infra\design-software-docker-infra\.env `
  -f ..\docker-infra\design-software-docker-infra\docker-compose.yml `
  down -v --remove-orphans
```

## Identificación y lectura de resultados

| Ruta | Contenido y uso |
|------|-----------------|
| `performance/results/after/k6-summary.json` | Métricas k6 estructuradas de la última ejecución optimizada. Está sanitizado y no contiene `setup_data`, JWT ni credenciales. |
| `performance/results/after/summary.md` | Resumen humano con VUs, duración, iteraciones, p95, errores, checks y `PASS`/`FAIL`. Es la primera evidencia que debe revisar QA. |
| `performance/results/before/k6-summary.json` | Línea base real de 50 VUs/5 min tomada con los índices R2 retirados. |
| `performance/results/before/summary.md` | Resumen humano de la línea base; su `FAIL` de p95 es esperado y demuestra la necesidad del cambio. |
| `performance/results/explain-before.txt` | Tres planes SQL antes de aplicar los índices. |
| `performance/results/explain-after.txt` | Los mismos tres planes después de aplicar los índices. |
| `performance/results/rollback-verification.txt` | Resultado `t | t | t` que demuestra la ausencia de los tres índices tras rollback. |
| `performance/results/seed.txt` | Confirmación del volumen de datos insertado. |

La aceptación automática de `after` exige p95 `< 300 ms`, tasa de
`audit_request_errors < 0.01` y cero checks fallidos. Un archivo existente no
prueba una ejecución nueva: debe revisarse la salida del comando, su exit code
y la actualización de los archivos `after`.

## Repositorios involucrados

| Repositorio | Uso en el flujo | Modificación de esta entrega |
|-------------|-----------------|------------------------------|
| `design-software-audit-service` | Escenario k6, datos SQL, sanitización, README y resultados. | Sí: README actualizado; los scripts y resultados ya estaban versionados en la rama R2. |
| `design-software-docs` | Informe técnico y ADR de R2. | Sí: este informe detallado. |
| `design-software-audit-db` | Changeset de tres índices y rollback ya versionados en la rama R2. | No se requirió un cambio nuevo. |
| `design-software-docker-infra` | Compose para PostgreSQL, Liquibase, IAM, query-api y k6. | No se requirió un cambio nuevo. |
| `design-software-iam-service` | Login real, emisión JWT y JWKS. | No modificado. |
| `design-software-iam-db` | Esquema, roles y features contractuales. | No modificado. |

El workflow R5 tampoco fue modificado. La ejecución remota #4 del PR de
audit-service terminó en `success` después de publicar la evidencia anterior.

## Puntos ciegos y límites de la evidencia

- Es una prueba local en un solo Docker Desktop; no incorpora balanceador,
  latencia entre hosts, límites de nube, TLS externo ni ruido de producción.
- El fixture tiene 200 002 filas y una distribución controlada. Un volumen o
  cardinalidad diferentes requieren repetir k6 y los `EXPLAIN`.
- Se mide la API de lectura (lista, detalle y exportación); no se prueba el
  throughput de ingestión de `audit-worker` ni RabbitMQ durante esta carga.
- La identidad de aceptación usa scope `GLOBAL`. La corrección del filtrado
  `TRAINING_CENTER` está cubierta por implementación y planes, pero no por una
  segunda corrida k6 específica de ese scope.
- La integración IAM→Actors para `ficha_id` no se ejecuta porque el usuario de
  práctica no es `LEARNER`; este R2 no demuestra ese flujo mTLS.
- PostgreSQL puede conservar páginas calientes en caché. La comparación
  before/after mantiene el mismo host, dataset y mezcla para reducir el sesgo,
  pero no equivale a una prueba de almacenamiento frío.
- El p95 agregado incluye los tres endpoints y una única llamada de login del
  `setup`; no publica percentiles independientes por endpoint. Los checks sí
  prueban cada ruta por separado.
- `responseType: none` evita retener cuerpos en memoria de k6, pero la API sí
  produce y transfiere la respuesta; la cifra de bytes recibidos lo confirma.
- La automatización no aprovisiona una cuenta IAM. El ejecutor debe preparar
  una identidad descartable compatible con el contrato y mantener sus valores
  solamente en archivos `.env` locales ignorados por Git.
- `before` y `after` son invocaciones separadas. Para una comparación nueva se
  deben retirar los índices en el proyecto aislado, ejecutar `before`, aplicar
  el changeset y después ejecutar `after`.
- Un readiness `200`, una compilación o un `EXPLAIN` aislado no sustituyen la
  corrida k6 de 50 VUs/5 minutos. La aceptación se basa en el resumen k6 y su
  código de salida.

## Estado de aceptación

| AC | Estado | Evidencia |
|----|--------|-----------|
| 50 VUs por cinco minutos | Cumplido | Ambas corridas ejecutaron 50 VUs durante 5 minutos. |
| p95 < 300 ms y errores < 1 % | Cumplido | `after`: p95 46.46 ms y 0.00 % de errores con IAM real. |
| Tres planes antes y después | Cumplido | Tabla de resultados y script reproducible. |
| Changeset y rollback probado | Cumplido | Changeset, rollback SQL y verificación de ausencia de los tres índices. |
| Informe antes y después | Cumplido | Este informe conserva cifras, alcance y limitación de la carga. |

## Referencias

- [ADR-015 — Rendimiento reproducible de las consultas de Auditoría](../05-architecture/decisions/records/ADR-015-audit-r2-performance-data.md)
- [Ficha técnica de audit-service](../09-microservices/services/09-audit-service/README.md)
- `design-software-audit-service/.env.example`
- `design-software-audit-service/.env.worker.example`
- `design-software-docker-infra/.env.example`
