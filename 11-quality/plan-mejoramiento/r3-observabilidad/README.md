# Plan de mejoramiento R3 — Observabilidad de Monitoring

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

## Contexto

Documentación central de la entrega individual ADSO 3145555. Los repositorios de implementación conservan código, configuración y pruebas. Los originales completos de capturas, JSON y salidas de ejecución se guardan fuera de Git, en `C:\sena\Micro Horario\EVIDENCIAS-PLAN-MEJORAMIENTO-R3`.

## Contenido

- [Estado actual y PR de implementación](estado-actual.md).
- [Informe técnico breve con evidencias para la entrega](informe-tecnico-breve.md).
- [Informe técnico ampliado](informe-tecnico.md).
- [Capturas, métricas y salidas publicadas](evidencias-informe/README.md).
- [Matriz de criterios](matriz-final.md).

Las secciones numeradas conservan el material de la entrega y su evolución. El estado actual prevalece sobre las limitaciones descritas en documentos históricos. Las rutas de la matriz apuntan al archivo local completo. Para la entrega del informe breve se publica también una selección revisada de capturas, métricas y salidas, con procedencia y SHA-256.

## Reproducción local desde un checkout limpio

Se requiere acceso de lectura a los repositorios privados de `code-sena`, Git, Docker Desktop en modo Linux con Compose v2 y PowerShell, además de Node 22/npm para los scripts Playwright ejecutados en el host. Python debe cumplir el `pyproject.toml` de Monitoring; los contenedores frontend usan Node 22. No se necesita crear paquetes compartidos ni carpetas vacías a mano.

Los PR de implementación siguen **OPEN** en la consulta actual: todavía no hay una ejecución certificada desde sus ramas fusionadas. Para reproducir lo entregado antes del merge, clonar los siguientes commits de la entrega. Después de integrar los PR, repetir el procedimiento con los commits reales de `develop` (y `main` para docs), registrar sus SHA y ejecutar de nuevo las pruebas; no reutilizar este resultado como prueba de esas ramas.

Desde una carpeta nueva y vacía, ejecutar en PowerShell:

```powershell
$r3Sources = @{
    'design-software-docker-infra' = 'b8a99f08f8cd78a1f320a8bd505b0698d5b86a51'
    'design-software-monitoring-service' = '71a0778e9459080901ad24c70b3bff28e1f8b342'
    'design-software-monitoring-mfe' = '811be35abdcf406050c3ea10abc54fce43822f29'
    'design-software-web-shell' = '85b2c567bf428e1164424458fa5ac8b5760a87a0'
    'design-software-design-system' = 'e97afbdccd66de9c178d93db6e904eff2cbe31ca'
    'design-software-frontend-platform' = 'a227ada46f48480142b88e19eb2d2be939c415d3'
    'design-software-monitoring-db' = 'c118a04504354dad2de1db9fad89c49d2cdf0a4f'
    'design-software-iam-service' = '6987e0fa64628b5602969572d34a900f022ae891'
    'design-software-iam-db' = 'a1e01a42692da77269568f0ef49b2e4d3d035fa3'
    'design-software-reference-data-service' = '38bbbd54252745f2926d5ae71a48dae910449d63'
    'design-software-reference-data-db' = 'dede0c366440e8d22938d68d445878e62e16fe26'
    'design-software-academic-management-service' = '1d75bd2b32b1a11c6896125cde8f0208f7b0055a'
    'design-software-academic-management-db' = '7eb0e964927ce44c55cd6b10de4765902bb520fd'
    'design-software-actors-service' = '1348b45dc59de23bb7d56403d6936994bba9a6eb'
    'design-software-actors-db' = 'ac87ccccf928ac5348ebbf5df3a129f9cf483c02'
    'design-software-scheduling-service' = 'e806ab759d7b90e6e425921d3a2b56d4a725f982'
    'design-software-scheduling-db' = 'cd19f0986f3dbda257586f77231a1da5add48240'
    'design-software-notification-service' = '4094b1a2b3e0ba15f8ea82bec54b11f6fb7df8bf'
    'design-software-notification-db' = '5803c462e4164c4e1805c8bbc3188bcd5fd41d89'
    'design-software-audit-service' = '34674fc72051411311694908986552586ba196ab'
    'design-software-audit-db' = 'c5bd1f5b4aeca7c518f11bd1c21df60af131c1c0'
}
foreach ($entry in $r3Sources.GetEnumerator()) {
    git clone --no-checkout "https://github.com/code-sena/$($entry.Key).git" $entry.Key
    if ($LASTEXITCODE) { throw "No se pudo clonar $($entry.Key)" }
    git -C $entry.Key checkout --detach $entry.Value
    if ($LASTEXITCODE) { throw "No se pudo obtener el commit de $($entry.Key)" }
}
```

Todos los repositorios quedan como hermanos bajo la misma carpeta. En particular, **`design-software-design-system` y `design-software-frontend-platform` son repositorios reales y obligatorios**: `npm ci` resuelve dependencias `file:../...` de los `package.json` y locks del MFE y shell.

| Servicio Compose | Carpeta del host, relativa a docker-infra | Destino dentro del contenedor |
|---|---|---|
| monitoring-mfe | `../design-software-design-system` | `/workspace/design-software-design-system` |
| monitoring-shell | `../design-software-design-system` | `/workspace/design-software-design-system` |
| monitoring-shell | `../design-software-frontend-platform` | `/workspace/design-software-frontend-platform` |

Los montajes ya están declarados en `design-software-docker-infra/docker-compose.yml`; no hay que crearlos mediante `docker run`. También se monta el repositorio del MFE o shell en `/workspace/<nombre-del-repo>`. Las rutas del host se resuelven respecto del archivo Compose. `BACKEND_REPOS_DIR` permite reubicar contextos backend/migraciones, pero **no cambia** estos bind mounts frontend: este procedimiento exige la estructura de repositorios hermanos indicada. Un directorio vacío creado automáticamente por Docker no sustituye al checkout del paquete.

Antes del arranque, comprobar los archivos de ambos paquetes y preparar el entorno Python:

```powershell
$r3Required = @(
    'design-software-design-system/package.json',
    'design-software-design-system/src/index.ts',
    'design-software-design-system/src/tokens/tokens.generated.css',
    'design-software-frontend-platform/package.json',
    'design-software-frontend-platform/src/index.ts'
)
foreach ($file in $r3Required) {
    if (!(Test-Path -LiteralPath $file -PathType Leaf)) { throw "Falta el checkout requerido: $file" }
}
python -m venv design-software-monitoring-service/.venv
& design-software-monitoring-service/.venv/Scripts/python.exe -m pip install -e './design-software-monitoring-service[dev]'
if ($LASTEXITCODE) { throw 'No se pudieron instalar las dependencias de Monitoring' }

# Los scripts generan el entorno aislado R3 y cambian el directorio de trabajo.
$r3Workspace = (Get-Location).Path
try {
    & (Join-Path $r3Workspace 'design-software-docker-infra/scripts/up-monitoring-stack.ps1')
    & (Join-Path $r3Workspace 'design-software-docker-infra/scripts/up-monitoring-integration.ps1') -WithDomains -WithObservability
} finally {
    Set-Location -LiteralPath $r3Workspace
}
```

El bloque anterior restaura la raíz del checkout después de ejecutar los scripts de docker-infra. Esperar la salud de Actors y Scheduling antes de probar dominios. Los scripts generan únicamente archivos de ejecución locales en `docker-infra/local-monitoring/` y `.env.monitoring-r3`; no se copian credenciales de otra máquina. Mantener la memoria necesaria para los servicios: en máquinas pequeñas se pueden separar las fases de integración y captura, sin borrar volúmenes.

Antes de ejecutar el navegador en el host, instalar las dependencias del shell y Chromium. Los `node_modules` del contenedor viven en un volumen Docker y no sustituyen los del host:

```powershell
Push-Location design-software-web-shell
try {
    npm.cmd ci --no-audit --no-fund
    if ($LASTEXITCODE) { throw 'Fallo npm ci del shell' }
    npx.cmd playwright install chromium
    if ($LASTEXITCODE) { throw 'Fallo la instalacion de Chromium' }
} finally {
    Pop-Location
}
```

Desde la raíz del checkout, la secuencia de validación es:

```powershell
$r3Python = './design-software-monitoring-service/.venv/Scripts/python.exe'
& $r3Python design-software-monitoring-service/scripts/test_r3_iam.py
if ($LASTEXITCODE) { throw 'Fallo test_r3_iam' }
& $r3Python design-software-monitoring-service/scripts/test_r3_academic.py
if ($LASTEXITCODE) { throw 'Fallo test_r3_academic' }
Push-Location design-software-web-shell
try {
    node scripts/r3-main-flow.mjs
    if ($LASTEXITCODE) { throw 'Fallo r3-main-flow' }
} finally {
    Pop-Location
}
& $r3Python design-software-monitoring-service/scripts/test_r3_domains.py
if ($LASTEXITCODE) { throw 'Fallo test_r3_domains' }
& $r3Python design-software-monitoring-service/scripts/test_r3_scheduling.py
if ($LASTEXITCODE) { throw 'Fallo test_r3_scheduling' }
& $r3Python design-software-monitoring-service/scripts/test_r3_backend.py
if ($LASTEXITCODE) { throw 'Fallo test_r3_backend' }
```

Cada fallo debe resolverse y registrarse antes de continuar; los scripts devuelven código distinto de cero cuando falla una aserción. Para telemetría, alerta y capturas adicionales, seguir el [informe técnico, sección 8](informe-tecnico.md#8-pruebas-y-procedimiento). Las pruebas de dominio no reemplazan esas verificaciones.

El resultado de una ejecución nueva se guarda en `EVIDENCIAS-PLAN-MEJORAMIENTO-R3/` junto a los repositorios, fuera de Git. Conservar fecha, comandos, códigos de salida y heads utilizados. La documentación y las capturas anteriores son evidencia histórica, no una ejecución del checkout recién creado.

## Referencias

- [ADR de observabilidad R3](../../../05-architecture/decisions/records/ADR-010-monitoring-r3-observability.md).

## Índice de archivos

- [01-diagnostico](01-diagnostico/README.md).
- [02-arquitectura](02-arquitectura/README.md).
- [03-parte-1](03-parte-1/README.md).
- [04-tracing](04-tracing/README.md).
- [05-metricas](05-metricas/README.md).
- [08-pruebas](08-pruebas/README.md).
- [09-sustentacion](09-sustentacion/README.md).
- [10-integraciones](10-integraciones/README.md).
- [11-entregas-anteriores](11-entregas-anteriores/README.md).
