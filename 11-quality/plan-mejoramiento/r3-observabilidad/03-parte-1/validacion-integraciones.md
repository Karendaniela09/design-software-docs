# Validación adicional de integración

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

Fecha local: 19 de octubre de 2026, America/Bogota.

## Estado comprobado

- IAM real local: login y `/auth/me`, JWKS, acceso autorizado 200, firma alterada 401, ausencia de token 401 y usuario sin roles 403. Evidencia: `iam-integration.json` y `../08-pruebas/iam-real-confirmed.*`.
- Academic y Reference Data reales: la solicitud crea una ficha y publica `academic.ficha.opened` desde su outbox transaccional. El worker de Monitoring la consume y persiste el seguimiento. Evidencia aprobada: `academic-integration.json` y `../08-pruebas/academic-relay-fixed.*`.
- Se corrigió el arranque del relay en [Academic PR #17](https://github.com/code-sena/design-software-academic-management-service/pull/17). La prueba `AcademicOutboxRelayContextTest` pasó con la autoconfiguración real de Rabbit (1 ejecutada, 0 fallos). La primera descarga por Maven falló; se conserva esa salida y la ejecución posterior aprobada en `../08-pruebas/academic-relay-context-build.*`.
- El MFE dentro del shell usa login y `/auth/me` reales de IAM y el selector de fichas real de Academic. Se registró una sesión HTTP 201 con asistencia 27/30 (90 %) y se volvió a abrir su detalle tras recargar. `main-flow-browser.json` tiene `status=passed`, solicitudes y ausencia de errores JavaScript. Capturas reales: `main-flow-created.png` y `main-flow-reloaded.png`.
- La captura real de Tempo Explore ya existe en `../04-tracing/tempo-trace.png` y fue inspeccionada visualmente.

## Identidad y configuración

Se utiliza una cuenta de prueba en la base aislada `monitoring_r3`, con rol SYSTEM_ADMIN del catálogo oficial. Las credenciales se generan localmente y permanecen en `local-monitoring/`, ignorado por Git. No se usa una cuenta institucional ni se prueba el IdP del SENA.

El evento de apertura de Academic no asigna un instructor. El seguimiento conserva el actor de sistema `00000000-0000-0000-0000-000000000000` y la sesión del administrador se registra a su nombre según la regla actual del MFE. Esto no valida una asignación de instructor obtenida desde Actors, ni debe presentarse como seguimiento realizado por un instructor institucional.

El seed oficial define `MON_TRACKING_SESSION_VIEW` pero no lo asigna a SYSTEM_ADMIN. Para esta cuenta de prueba se registra un override explícito mediante el modelo RBAC real. IAM calcula el permiso y firma el token; no se inventa el claim ni se relaja la autorización de Monitoring. La corrección del seed institucional sigue siendo responsabilidad de la configuración de IAM.

Monitoring conserva el requisito de audiencia `monitoring` en el perfil R3 original. Solo el perfil de integración configura `JWT_AUDIENCE` vacío para el contrato actual de usuario IAM, que no emite `aud`. Se siguen verificando firma RS256, emisor, expiración y sujeto. Un token con audiencia inesperada sigue rechazándose.

Reference Data solo permite JWKS por HTTP en loopback. El perfil local comparte el namespace de red de IAM y usa `localhost`; no desactiva la política de transporte. Su API se expone sin `/api/v1` a Academic, según las rutas reales del servicio.

## Reproducción

Requiere las ramas R3 de Monitoring, shell, infraestructura y Academic. Los PR se dejan abiertos por instrucción del usuario; no se fusionan.

Desde la raíz del workspace, después de preparar la `.venv` según la guía:

```powershell
& .\design-software-docker-infra\scripts\up-monitoring-stack.ps1
& .\design-software-docker-infra\scripts\up-monitoring-integration.ps1
& .\design-software-monitoring-service\.venv\Scripts\python.exe .\design-software-monitoring-service\scripts\test_r3_academic.py
Push-Location .\design-software-web-shell
node scripts/r3-main-flow.mjs
Pop-Location
```

El arranque de integración construye los servicios secuencialmente para reducir presión de memoria. `-WithObservability` agrega LGTM al flujo integrado. En una máquina de 8 GB conviene no compilar mientras se ejecutan todos los servicios.

La prueba del navegador fija localhost a IPv4 y espera el montaje real del MFE en lugar de depender de DOMContentLoaded durante la carga de Federation. Se conserva el intento fallido por 502 y el selector inicial demasiado estricto. Nginx ahora resuelve también el shell por DNS Docker después de recrearlo. No se interceptan respuestas ni se simulan servicios en esta prueba.

Para reproducir la regresión del relay desde Academic:

```powershell
docker build -f deploy/Dockerfile.r3-test .
```

GitHub Actions del backend aprobó el commit `0335eb5`: [ejecución 39355155160](https://github.com/code-sena/design-software-monitoring-service/actions/runs/39355155160). Ejecutó 23 pruebas y omitió las cuatro de PostgreSQL, que sí pasaron en la suite local de 27 pruebas. Evidencia: `../08-pruebas/github-ci-iam.json`.

Para volver a la demostración R3 con identidad local de ocho horas:

```powershell
Push-Location .\design-software-docker-infra
docker compose --env-file .env.monitoring-r3 -f docker-compose.yml -f docker-compose.monitoring-integration.yml --profile monitoring stop iam-integration academic-integration reference-integration
Pop-Location
& .\design-software-docker-infra\scripts\up-monitoring-stack.ps1
```

No se borran datos, volúmenes ni logs.

## Límites pendientes

Notification usa actualmente `NewStubRecipientResolver` en su worker. No se considera una validación de resolución real de destinatarios. La cadena de notificación y auditoría, los productores de Scheduling y Actors y el IdP institucional no están cubiertos por este recorrido. Las HU de integración correspondientes siguen abiertas; no se cierran con resultados de pruebas locales parciales.
