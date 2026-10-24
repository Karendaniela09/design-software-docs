# Integración de IAM DB con IAM Service (R3 / HU-INT-IAM-001)

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor original: Kevin-Stiven-Lopez-Amaya404 | Equipo: IAM / Calidad
> HU: [HU-INT-IAM-001](https://github.com/code-sena/design-software-docs/issues/290)

> Este informe se escribió en `design-software-iam-db` (`docs/integration/iam-service.md`, PR [iam-db#79](https://github.com/code-sena/design-software-iam-db/pull/79)). Los repositorios de código conservan solo código, así que se movió aquí sin cambiar su contenido técnico. El repositorio `iam-db` queda con el workflow de CI y el script de preflight, y su README remite a esta página.

Entrega del 21 de octubre de 2026 (Bogotá).

## Versiones contrastadas

| Componente | Versión |
|---|---|
| IAM DB | `develop`, base `a1e01a42692da77269568f0ef49b2e4d3d035fa3` |
| IAM Service | `7c837e0824263cef0aef89f807731adca839f25e`, [PR #43](https://github.com/code-sena/design-software-iam-service/pull/43) |
| PostgreSQL | 16 |
| Liquibase | 4.29 |

El changelog de entrada es `changelog/changelog-master.yaml`. Esta versión ya
incluye `identity.outbox`, sus índices/grants y las columnas de contraseña temporal
de `identity.user`. La [PR #74](https://github.com/code-sena/design-software-iam-db/pull/74)
de contraseña temporal e índice de recuperación está fusionada en `develop`.
Esta entrega añade verificación y automatización; conserva los changesets existentes.

## Corte de ramas y procedencia de las pruebas (24 de octubre de 2026)

La fila de IAM Service en la tabla anterior (`7c837e0824263cef0aef89f807731adca839f25e`) identifica el commit usado en la validación local descrita más abajo. Debe conservarse como procedencia histórica: esa ejecución no prueba por sí sola el candidato actual del servicio.

Puntas remotas observadas antes de mover este informe:

- IAM DB: `r3-iam-db-integration-dev` en `7fe2798cf5d5c90b6e51509e6dd052f1929f81b8`, basada en `develop` (`a1e01a42692da77269568f0ef49b2e4d3d035fa3`); PR [#79](https://github.com/code-sena/design-software-iam-db/pull/79) abierto. CI de DB aprobada en [run 39538261790](https://github.com/code-sena/design-software-iam-db/actions/runs/39538261790).
- IAM Service: `r3-observability-delivery-dev` en `5350e1495c7764a62cd47bc9e83063a7eeb68053`, basada en `develop` (`c7735cfc3135aad83091e2cfac5abe5809853c85`); PR [#43](https://github.com/code-sena/design-software-iam-service/pull/43) abierto.

La prueba local PostgreSQL de este documento valida el SHA de servicio fijado en la tabla, no la combinación actual de ramas. Para afirmar compatibilidad del candidato actual se requiere repetir el smoke DB/servicio y conservar su evidencia. Las migraciones de `develop` siguen intactas; el PR iam-db#79 solo agrega preflight y CI.

## Preparación del entorno

Desde el repositorio de infraestructura, con el checkout compatible de IAM DB
montado en la ruta de `liquibase-iam`:

```bash
docker compose --env-file .env.develop up postgres -d
docker compose --env-file .env.develop --profile tooling run --rm liquibase-iam validate
docker compose --env-file .env.develop --profile tooling run --rm liquibase-iam update
```

Configurar el usuario de aplicación y su pertenencia a `iam_writer` según el entorno.
El repositorio define grupos `NOLOGIN`; no incluye una contraseña de aplicación.
IAM Service recibe `IAM_DB_DSN`, `IAM_DB_USERNAME` e `IAM_DB_PASSWORD` por entorno
y conserva `ddl-auto: validate`, por lo que no crea los objetos faltantes.

Para verificar una base migrada, configurar las variables PostgreSQL habituales
(`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`) y ejecutar, desde la raíz
de `design-software-iam-db`:

```bash
psql --no-psqlrc -v ON_ERROR_STOP=1 -f scripts/verify-iam-integration.sql
```

El script usa una transacción de solo lectura. Comprueba tablas IAM, columnas y
tipos de contraseña temporal, índices de outbox/recuperación, seeds de administración
y auditoría, y permisos efectivos de los grupos reader/writer/admin. Rechaza un
reader con permisos de escritura. Termina con error cuando falta un requisito.
No crea cuentas ni valida las credenciales concretas del usuario de aplicación.

## Evidencia local del 20 de octubre de 2026

Se utilizó la base nueva `iam_delivery_20261021` dentro del contenedor aislado
`iam-r3-demo-20261020`, puerto local 55432. La base compartida no se modificó.

- El changelog oficial se aplicó desde cero: **37 changesets**, sin fallos.
- `liquibase validate` terminó sin errores de validación.
- Un segundo `update` mantuvo **37 changesets**, sin nuevas ejecuciones.
- El preflight de esta entrega aprobó el esquema completo y sus permisos de grupos.
- El mismo preflight rechazó la demo anterior `iam_demo` con el diagnóstico
  `Missing IAM table: identity.outbox`, sin modificarla.
- IAM Service ejecutó **54 pruebas PostgreSQL aprobadas**, sin errores ni fallos;
  una prueba de RabbitMQ se omitió por ausencia de broker. Incluyen login, auditoría,
  sesiones, recuperación, RBAC, overrides y administración de usuarios.
- El JAR construido desde el servicio respondió 200 en `/health`, `/ready` y
  `/actuator/prometheus` al conectarse a esta base. Se comprobó correlación HTTP
  y presencia de contadores/histogramas con `service="iam-service"`.

La evidencia detallada del servicio está en
[su registro de validación](https://github.com/code-sena/design-software-iam-service/blob/r3-observability-delivery-dev/docs/observability/validation.md).
Ese registro se moverá a esta carpeta cuando se resuelva iam-service#43.

## Validación automática

El workflow `IAM database integration` (`.github/workflows/ci.yml` de `design-software-iam-db`)
levanta PostgreSQL 16 desechable, valida el changelog, aplica la migración completa,
repite `update` y comprueba que el conteo de changesets no cambia. Finalmente ejecuta
el preflight de solo lectura. Las credenciales del workflow son exclusivas del servicio
efímero de CI.

Esta validación no acredita el recorrido desde el shell/MFE, los consumidores
RabbitMQ ni la ingesta de trazas/logs y alertas del entorno compartido. La HU de
integración completa sigue requiriendo esas pruebas y revisión del equipo.

## Puntos abiertos

- El workflow usa Liquibase 4.29 y `docker-infra` usa 4.33. Conviene alinear la versión.
- El mismo patrón (rebuild limpio, `update` idempotente y preflight de privilegios) puede generalizarse a los demás repositorios `-db`; es una decisión de arquitectura.
