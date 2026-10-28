# Correcciones aplicadas de integración — 2026-10-27

## Cambio implementado

| Problema | Causa confirmada | Solución | Repositorio / rama | Commit / PR | Estado |
|---|---|---|---|---|---|
| HTML inválido, 405 y rutas no autenticadas en Training Environments | El remote usaba rutas relativas (`/training-environments`, `/reservations`, etc.) que caían en el fallback del Web Shell. | Se centralizó `/training-environment/api/v1`; todos los adaptadores aceptan el `httpClient` autenticado del Shell; se actualizó el proxy Vite; se quitaron fallbacks de datos simulados que ocultaban errores. | `design-software-training-environment-mfe` / `fix/training-environment-api-integration-clean` | `877a5d8` / [PR #11](https://github.com/code-sena/design-software-training-environment-mfe/pull/11) | Abierto a `develop`, sin merge |

## Archivos principales

- `src/App.tsx`: crea puertos estables con el transporte del Shell y los inyecta en gestión, disponibilidad, reservas, tipos, mantenimiento y reporte.
- `src/adapter/out/apiBase.ts`: define el único prefijo público de la API.
- `src/adapter/out/*ApiAdapter.ts`: usa el cliente autenticado cuando está disponible y conserva el modo standalone sin exponer tokens.
- `src/application/useTrainingEnvironments.ts`, `useAvailabilityRules.ts`, `useMaintenance.ts`: presentan errores reales; ya no fabrican éxito con fixtures.
- `src/contracts/remote-props.ts`: documenta la mínima interfaz de transporte que recibe el remote.
- `vite.config.ts`: alinea el proxy local con `/training-environment/api`.

## Validación ejecutada

| Prueba | Resultado |
|---|---|
| `npm.cmd test` en el commit exacto `877a5d8` | 83/83 pruebas aprobadas |
| `npm.cmd run build` en el commit exacto `877a5d8` | Aprobado |
| Prueba unitaria añadida | Verifica que el adapter usa el cliente autenticado y `/training-environment/api/v1/environment-types`, sin `fetch` directo |
| Sonda pública sin JWT a `/training-environment/api/v1/training-environments` | `401 application/json` — llega a API, no al fallback HTML |
| Sonda pública sin JWT a `/training-environment/api/v1/environment-types` | `401 application/json` — llega a API, no al fallback HTML |

## Cambios deliberadamente no realizados

- No se cambió el contrato, los métodos HTTP ni controles de autorización del servicio.
- No se modificó `develop`, `main`, la configuración publicada de Hostinger ni bases de datos.
- No se ajustó Monitoring/OTLP sin logs de los contenedores responsables: hacerlo sería especulativo.

## Siguiente validación obligatoria después del despliegue

Con una sesión real autorizada desde el Shell, comprobar disponibilidad, reservas, tipos de ambiente, mantenimiento y reporte de utilización. La red debe producir solicitudes a `/training-environment/api/v1/...`, y ninguna respuesta HTML debe ser interpretada como JSON.

