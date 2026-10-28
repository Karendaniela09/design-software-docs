# Evidencias QA de integración — 2026-10-27

| ID | Módulo | Error original | Solución / diagnóstico | Prueba | Resultado | Evidencia |
|---|---|---|---|---|---|---|
| INT-01 | Training Environments | HTML/JSON inválido y 405 al consultar disponibilidad y reservas | PR #11 usa la ruta de edge y cliente autenticado; elimina fallbacks de datos simulados. | Unitarias y build del commit `877a5d8`. | APROBADO | 83/83; build OK. |
| INT-02 | Training Environments | No se sabía si la ruta API llegaba al servicio. | La ruta pública contractual queda centralizada. | GET sin JWT a rutas de ambientes y tipos. | APROBADO | `401 application/json`, no HTML. |
| INT-03 | Monitoring | Catálogos, alertas, planes e indicadores devolvían 502. | El liveness `/health` y readiness `/ready` también devuelven 502; investigar upstream. | GET público a health, ready y kpi-types. | BLOQUEADO | 502 desde la VPS. |
| INT-04 | OTLP | POST `/otlp/v1/traces` devolvía 405. | La ruta publicada termina en Nginx SPA, no en OTLP collector. | GET, POST y OPTIONS contra endpoint público. | BLOQUEADO | GET 200 `text/html`; POST/OPTIONS 405 `text/html`. |
| INT-05 | Fichas académicas | 403 y mensaje de centro requerido. | La API mantiene scope de centro; el usuario de prueba necesita asignación institucional real y token renovado. | GET sin JWT y revisión de guards IAM/Academic. | PENDIENTE | Sin JWT: 401; no se dispone de sesión coordinador corregida. |
| INT-06 | Reference Data | La UI no conectaba catálogos/geografía. | El servicio está accesible y la API exige token + feature REF. | Health y macroregions sin JWT. | PENDIENTE | Health 200 JSON; macroregions 401 JSON. |
| INT-07 | Actors | Crear instructor mostró 405. | `develop` define `POST /actors/api/v1/instructors` tanto en MFE como API; validar imagen/proxy real. | Revisión de mappings y pruebas de integración existentes. | PENDIENTE | Inconsistencia con despliegue observada. |
| INT-08 | Scheduling | La pantalla recibió HTML como JSON. | El Shell actual ya inyecta `apiBaseUrl`, `activePage` y cliente autenticado. | Revisión de integración en `develop`. | PENDIENTE | Falta sesión desplegada para E2E. |

## Criterio de resultado

`APROBADO` se usa únicamente cuando se ejecutó la prueba indicada. `PENDIENTE` requiere sesión o despliegue. `BLOQUEADO` requiere acceso de infraestructura o un cambio efectivo del entorno publicado.
