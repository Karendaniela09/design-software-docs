# Cierre de la ampliación local

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

19 de octubre de 2026, America/Bogota.

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Token emitido por IAM local, perfil y JWKS | Aprobado; 200 autorizado, firma inválida 401, usuario sin rol 403 | iam-integration.json |
| Ficha creada por Academic usando Reference Data real | HTTP 201 | academic-integration.json |
| Outbox de Academic publicado y recibido por Monitoring | Seguimiento persistido | academic-integration.json |
| Sesión registrada en el MFE y consultada tras recargar | HTTP 201; asistencia 27/30 = 90 %; fecha de Bogotá | main-flow-browser.json |
| Verificación independiente de esa sesión en PostgreSQL | Aprobado | main-flow-postgres.json |
| Tempo Explore | Captura real inspeccionada, ocho spans hasta INSERT | ../04-tracing/tempo-trace.png |
| Regresión de arranque del relay Academic | 1 ejecutada, 0 fallos | ../08-pruebas/academic-relay-context-build.txt |
| Suite backend local con PostgreSQL | 27 aprobadas | ../08-pruebas/backend-full-flow.txt |
| Suite shell / build / lint | 106 aprobadas; build y lint aprobados | ../08-pruebas/shell-integration-* |
| CI del backend 0335eb5 | 23 aprobadas, 4 omitidas que sí pasaron localmente | ../08-pruebas/github-ci-iam.json |

Los intentos fallidos también permanecen en `08-pruebas`. El último navegador aprobado es `main-flow-bogota.*`; `main-flow-browser.*` de esa carpeta registra un intento anterior fallido. La evidencia aprobada del navegador está en este directorio: `main-flow-browser.json`.

PR abiertos, sin fusionar:

- [Monitoring service #6](https://github.com/code-sena/design-software-monitoring-service/pull/6): integración JWT y paginación, commit `0335eb5` más cierre documental posterior.
- [Monitoring MFE #8](https://github.com/code-sena/design-software-monitoring-mfe/pull/8): instrumentación, commit `811be35`.
- [Shell #14](https://github.com/code-sena/design-software-web-shell/pull/14): selector Academic y prueba del flujo, commit `9ccfebf`.
- [Infra #39](https://github.com/code-sena/design-software-docker-infra/pull/39): perfil integrado y DNS Nginx, commit `79e6b84`.
- [Academic #17](https://github.com/code-sena/design-software-academic-management-service/pull/17): relay y regresión, commit `1d75bd2`.

Permanecen pendientes el IdP institucional, la asignación real del instructor desde Actors, los productores de Scheduling/Actors y la entrega completa Notification/Audit. El worker actual de Notification usa un resolvedor de destinatarios de prueba. No se declara el producto completo terminado ni se cierran HU ajenas con estas pruebas.

El entorno integrado se ejecutó con once contenedores principales. LGTM se detuvo durante la ampliación para reducir presión de memoria en un equipo de 8 GB; las evidencias R3 de trazas, RED, logs, alerta y recuperación ya estaban verificadas y guardadas. `up-monitoring-integration.ps1 -WithObservability` permite añadirlo; la guía explica cómo volver al perfil R3 original.
