# Informe para QA y Arquitectura: conexion backend/frontend local

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

Fecha: 2026-10-14

## Resumen ejecutivo

Se dejo funcional la integracion local del shell web con el BFF y los MFEs principales del sistema de gestion de horarios. El objetivo fue pasar de un shell en modo mock/stub a una composicion local con remotes federados reales, consumo HTTP hacia el BFF local y pantallas navegables sin los bloqueos visibles que estaban impidiendo la demostracion.

Resultado validado:

- El shell levanta en `http://127.0.0.1:5000`.
- El BFF local levanta en `http://127.0.0.1:8080`.
- Los MFEs quedan disponibles en puertos `5101` a `5109`.
- Las pantallas revisadas de scheduling, fichas, monitoring y actores cargan contenido real dentro del shell.
- Se eliminaron los errores visibles `HTTP 404` en las pantallas detectadas.
- El MFE de actores ya no aparece como HTML sin estilos ni duplica el chrome principal cuando corre dentro del shell.
- Se publicaron ramas `fix/conection-backend-frontend` y PRs hacia `develop`.

Nota de alcance: esta solucion deja funcional la integracion local para validacion de QA y arquitectura. Algunos datos son respuestas locales de integracion servidas por el BFF mientras se conectan o completan los servicios de dominio reales. No debe interpretarse como certificacion de todos los backends productivos ni de todas las reglas de negocio finales.

## PRs abiertos

| Repositorio | PR | Base | Rama |
| --- | --- | --- | --- |
| design-software-web-bff | https://github.com/code-sena/design-software-web-bff/pull/1 | develop | fix/conection-backend-frontend |
| design-software-web-shell | https://github.com/code-sena/design-software-web-shell/pull/11 | develop | fix/conection-backend-frontend |
| design-software-actors-mfe | https://github.com/code-sena/design-software-actors-mfe/pull/7 | develop | fix/conection-backend-frontend |
| design-software-academic-management-mfe | https://github.com/code-sena/design-software-academic-management-mfe/pull/8 | develop | fix/conection-backend-frontend |
| design-software-audit-mfe | https://github.com/code-sena/design-software-audit-mfe/pull/4 | develop | fix/conection-backend-frontend |
| design-software-document-mfe | https://github.com/code-sena/design-software-document-mfe/pull/5 | develop | fix/conection-backend-frontend |
| design-software-monitoring-mfe | https://github.com/code-sena/design-software-monitoring-mfe/pull/6 | develop | fix/conection-backend-frontend |
| design-software-reference-data-mfe | https://github.com/code-sena/design-software-reference-data-mfe/pull/10 | develop | fix/conection-backend-frontend |
| design-software-scheduling-mfe | https://github.com/code-sena/design-software-scheduling-mfe/pull/7 | develop | fix/conection-backend-frontend |
| design-software-training-environment-mfe | https://github.com/code-sena/design-software-training-environment-mfe/pull/6 | develop | fix/conection-backend-frontend |
| design-software-docker-infra | https://github.com/code-sena/design-software-docker-infra/pull/38 | develop | fix/conection-backend-frontend |

## Estado funcional validado

### Rutas principales verificadas en el shell

| Ruta | Estado esperado | Resultado |
| --- | --- | --- |
| `/scheduling/horarios` | MFE real de scheduling montado y consumiendo franjas horarias | Funcional, muestra franjas horarias locales |
| `/academic-management/fichas` | MFE real de academic-management consultando fichas | Funcional, muestra fichas locales paginadas |
| `/monitoring/seguimiento` | MFE real de monitoring con `httpClient` entregado por shell | Funcional, muestra seguimiento de ficha |
| `/monitoring/indicadores` | MFE real de monitoring navegable desde shell | Funcional, carga vista de monitoring |
| `/actors/mi-disponibilidad` | MFE real de actors integrado visualmente al shell | Funcional, estilos aplicados y sin chrome duplicado |

### Endpoints locales expuestos por el BFF para integracion

El BFF local ahora cubre las rutas necesarias para que los MFEs consuman datos durante la composicion local:

- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`
- `GET /api/v1/health`
- `GET /api/v1/dashboard`
- `GET /api/v1/fichas`
- `GET /api/v1/fichas/{id}`
- `GET /time-slots`
- `POST /time-slots`
- `PUT /time-slots/{id}`
- `DELETE /time-slots/{id}`
- `GET /api/v1/kpi-types`
- `GET /api/v1/alert-types`
- `GET /api/v1/risk-levels`
- `GET /api/v1/kpi-statuses`
- `GET /api/v1/kpi-trackings`
- `POST /api/v1/kpi-trackings`
- `GET /api/v1/reports/kpi-summary`
- `GET /api/v1/reports/indicators`
- `GET /api/v1/ficha-trackings`
- `GET /api/v1/ficha-trackings/{id}`
- `GET /api/v1/ficha-trackings/{id}/tracking-sessions`
- `POST /api/v1/ficha-trackings/{id}/tracking-sessions`
- `GET /api/v1/generated-alerts`
- `PUT /api/v1/generated-alerts/{id}/resolve`
- `GET /api/v1/improvement-plans`
- `POST /api/v1/improvement-plans`

## Detalle por repositorio

### 1. design-software-web-bff

PR: https://github.com/code-sena/design-software-web-bff/pull/1

Commit: `8f4f9ea fix: add local integration endpoints`

Cambios realizados:

- Se agregaron respuestas locales de integracion para sesion, notificaciones, dashboard, scheduling, academic-management y monitoring.
- Se normalizo el router para aceptar rutas con y sin prefijo `/api/v1`, segun el contrato real que usan los MFEs.
- Se agrego soporte CORS local para que el shell en `localhost:5000` pueda consumir el BFF en `localhost:8080`.
- Se ampliaron metodos permitidos a `GET`, `POST`, `PUT`, `DELETE` y `OPTIONS`.
- Se agregaron respuestas `204` para operaciones sin contenido.
- Se agregaron datos de prueba consistentes para:
  - usuario local autenticado,
  - franjas horarias,
  - fichas,
  - catalogos KPI,
  - estados KPI,
  - seguimiento de fichas,
  - sesiones de seguimiento,
  - alertas generadas,
  - planes de mejoramiento.

Impacto:

- Evita que los MFEs caigan en pantallas de error por endpoints inexistentes durante la integracion local.
- Permite validar flujos UI completos sin depender todavia de todos los backends de dominio.
- Sirve como BFF local de composicion mientras se conectan los servicios reales.

Validacion:

- `npm run build`
- `GET http://127.0.0.1:5000/api/v1/fichas` respondio `200`.
- `GET http://127.0.0.1:5000/time-slots` respondio `200`.
- `GET http://127.0.0.1:5000/api/v1/ficha-trackings` respondio `200`.
- `GET http://127.0.0.1:5000/api/v1/generated-alerts` respondio `200`.

### 2. design-software-web-shell

PR: https://github.com/code-sena/design-software-web-shell/pull/11

Commit: `d91050f fix: connect shell to local backend and remotes`

Cambios realizados:

- Se cambio el ambiente local para consumir sesion por HTTP:
  - `VITE_SESSION_SOURCE=http`
  - `VITE_LOCAL_SESSION=true`
  - `VITE_REMOTE_SOURCE=federation`
  - `VITE_NOTIFICATION_SOURCE=http`
- Se permitio que el shell considere sesion valida en modo local aunque no exista token real persistido.
- Se redirecciona `/login` hacia `/` cuando ya hay sesion local valida.
- Se ajusto Module Federation para aceptar remotes tipo modulo con `{ name, type: 'module', entry }`.
- Se agrego lectura de variables de entorno en `vite.config.ts` para decidir entre stubs y federation real.
- Se agrego proxy de desarrollo:
  - `/api/v1` hacia `http://localhost:8080`
  - `/time-slots` hacia `http://localhost:8080`
- Se entrego un `httpClient` del shell al MFE de monitoring, tal como exige su contrato.
- Se entregaron catalogos y opciones de ficha minimas para que monitoring pueda operar en shell.

Impacto:

- El shell deja de ser solamente una vista de stubs y monta remotes reales en desarrollo local.
- Los MFEs consumen por HTTP a traves del shell/BFF local.
- Monitoring deja de mostrar el mensaje de configuracion: "El shell debe proporcionar el cliente HTTP".
- El flujo de navegacion se acerca a la arquitectura final: un shell principal con MFEs montados como contenido interno.

Validacion:

- `npm run build`
- Verificacion en navegador headless usando Chrome del sistema:
  - `/scheduling/horarios`: sin `HTTP 404` visible.
  - `/academic-management/fichas`: sin `HTTP 404` visible.
  - `/monitoring/seguimiento`: sin `HTTP 404` visible.
  - `/monitoring/indicadores`: carga pantalla real.
  - `/actors/mi-disponibilidad`: carga MFE con estilos.

### 3. design-software-actors-mfe

PR: https://github.com/code-sena/design-software-actors-mfe/pull/7

Commit: `5105cfc fix: expose actors mfe with shell styling`

Cambios realizados:

- Se agrego `@module-federation/vite` como dependencia.
- Se configuro Module Federation:
  - remote name: `actorsMfe`
  - expose: `./App`
  - output: `remoteEntry.js`
  - shared: `react` y `react-dom` como singletons.
- Se importo `styles.css` directamente desde el componente expuesto para que el remote cargue estilos cuando se monta desde el shell.
- Se agrego prop `basePath` para detectar ejecucion hospedada por shell.
- Se agrego clase `hosted-remote` cuando el MFE corre dentro del shell.
- Se oculto el topbar/sidebar internos del MFE en modo hospedado para evitar doble chrome.
- Se ajusto el layout para ocupar correctamente el area de contenido del shell.

Impacto:

- Corrige la pantalla visualmente rota de actores que aparecia como HTML sin estilos.
- Evita duplicar header y menu lateral dentro del shell.
- Mantiene compatibilidad con ejecucion standalone del MFE.

Validacion:

- `npm run build`
- `GET http://127.0.0.1:5106/remoteEntry.js` respondio `200`.
- `/actors/mi-disponibilidad` carga sin HTML pelado y sin chrome duplicado.

### 4. design-software-academic-management-mfe

PR: https://github.com/code-sena/design-software-academic-management-mfe/pull/8

Commit: `cb8ceec fix: disable federation dts generation`

Cambios realizados:

- Se desactivo la generacion de tipos DTS de Module Federation con `dts: false`.

Impacto:

- Evita fallos de arranque local por intentos de generar o descargar artefactos de tipos federados.
- Permite que el MFE se monte de forma estable desde el shell.

Validacion:

- El remote se levanto en el entorno local.
- `/academic-management/fichas` cargo dentro del shell y consumio `GET /api/v1/fichas`.

### 5. design-software-audit-mfe

PR: https://github.com/code-sena/design-software-audit-mfe/pull/4

Commit: `fdb5cb6 fix: stabilize audit federation build`

Cambios realizados:

- Se desactivo la generacion de tipos DTS de Module Federation con `dts: false`.
- Se agrego `package-lock.json` generado por instalacion local para reproducibilidad.

Impacto:

- Estabiliza el arranque del MFE en composicion local.
- Reduce errores por tipos federados no disponibles durante desarrollo.

Validacion:

- El remote fue levantado junto con el conjunto de MFEs locales.
- `remoteEntry.js` del grupo de MFEs respondio correctamente durante la verificacion de puertos.

### 6. design-software-document-mfe

PR: https://github.com/code-sena/design-software-document-mfe/pull/5

Commit: `d4acf17 fix: stabilize document federation build`

Cambios realizados:

- Se desactivo la generacion de tipos DTS de Module Federation con `dts: false`.
- Se agrego `package-lock.json` generado por instalacion local para reproducibilidad.

Impacto:

- Permite que el MFE de documentos se mantenga disponible como remote federado.
- Reduce fallos durante arranque local por dependencias o tipos federados.

Validacion:

- El remote se levanto dentro del conjunto local.
- La pantalla `/document` ya mostraba contenido funcional durante la verificacion manual.

### 7. design-software-monitoring-mfe

PR: https://github.com/code-sena/design-software-monitoring-mfe/pull/6

Commit: `bd7bbe6 fix: stabilize monitoring federation build`

Cambios realizados:

- Se desactivo la generacion de tipos DTS de Module Federation con `dts: false`.
- Se ajusto lockfile despues de instalacion local.

Impacto:

- El MFE de monitoring puede arrancar como remote federado sin fallar por generacion de tipos.
- Al combinarse con el cambio del shell, recibe `httpClient` y deja de quedar en estado de configuracion incompleta.

Validacion:

- `/monitoring/seguimiento` carga seguimiento de ficha sin `HTTP 404` visible.
- `/monitoring/indicadores` carga la experiencia real del MFE.

### 8. design-software-reference-data-mfe

PR: https://github.com/code-sena/design-software-reference-data-mfe/pull/10

Commit: `fbfc445 fix: disable federation dts generation`

Cambios realizados:

- Se desactivo la generacion de tipos DTS de Module Federation con `dts: false`.

Impacto:

- Estabiliza el remote en desarrollo local.
- Permite que reference-data participe en la composicion federada sin errores de tipos remotos.

Validacion:

- El remote se levanto dentro del conjunto local de MFEs.
- La pantalla de parametrizacion de datos de referencia se visualizo en el shell.

### 9. design-software-scheduling-mfe

PR: https://github.com/code-sena/design-software-scheduling-mfe/pull/7

Commit: `1e15457 fix: disable scheduling federation dts generation`

Cambios realizados:

- Se reemplazo la configuracion pesada de generacion de tipos remotos por `dts: false`.

Impacto:

- Evita bloqueos y ruido en consola durante arranque local del remote.
- Permite que scheduling se monte desde el shell y consuma el endpoint local `/time-slots`.

Validacion:

- `/scheduling/horarios` carga dentro del shell.
- Se muestran tres franjas horarias:
  - Lunes manana, 07:00 a 12:00, jornada diurna.
  - Lunes tarde, 13:00 a 18:00, jornada diurna.
  - Martes noche, 18:00 a 22:00, jornada nocturna.
- No queda `HTTP 404` visible en la pantalla.

### 10. design-software-training-environment-mfe

PR: https://github.com/code-sena/design-software-training-environment-mfe/pull/6

Commit: `2501f26 fix: stabilize training environment federation build`

Cambios realizados:

- Se desactivo la generacion de tipos DTS de Module Federation con `dts: false`.
- Se ajusto lockfile despues de instalacion local.

Impacto:

- Permite levantar el MFE de ambientes dentro del set federado local.
- Reduce fallos en el arranque por tipos remotos.

Validacion:

- El remote se levanto junto con los demas MFEs.
- La pantalla de disponibilidad/ambientes ya era navegable en el shell durante la validacion manual.

## Cambio adicional de infraestructura

### design-software-docker-infra

PR: https://github.com/code-sena/design-software-docker-infra/pull/38

Commit: `7e7fb1f fix: align docker infra local integration paths`

Cambios realizados:

- Se ajustaron defaults de rutas de repositorios en `.env.example`:
  - `DB_REPOS_DIR=..`
  - `BACKEND_REPOS_DIR=..`
- Se actualizaron los volumenes de Liquibase en `docker-compose.yml` para resolver los repos `*-db` desde el workspace local.
- Se actualizaron contextos de build de servicios backend para resolverlos desde el workspace local.
- Se agrego `IAM_JWKS_URI=http://iam-api:8080/api/v1/auth/.well-known/jwks.json` en `.env.example`.
- Se removio la validacion temprana de `POSTGRES_DB` en `up-scheduling-stack.ps1`, conservando validaciones de usuarios.

Impacto:

- La composicion Docker queda alineada con la estructura real de `C:\sena\Micro Horario`, donde los repos viven como carpetas hermanas.
- Reduce configuracion manual para levantar infraestructura local.
- Agrega configuracion necesaria para que servicios que validan JWT puedan resolver JWKS localmente.

Validacion:

- `docker compose --env-file .env.example config --quiet`

## Consideraciones para QA

### Ambiente local esperado

Servicios esperados al momento de prueba:

- Shell: `http://127.0.0.1:5000`
- BFF: `http://127.0.0.1:8080`
- MFEs: puertos `5101` a `5109`

Puertos usados por MFEs:

- `5101`: IAM MFE
- `5102`: Scheduling MFE
- `5103`: Academic Management MFE
- `5104`: Training Environment MFE
- `5105`: Reference Data MFE
- `5106`: Actors MFE
- `5107`: Monitoring MFE
- `5108`: Document MFE
- `5109`: Audit MFE

### Escenarios sugeridos de prueba

1. Ingresar a `http://127.0.0.1:5000`.
2. Verificar que no quede pantalla blanca en `/login`; si hay sesion local, debe redirigir al inicio.
3. Navegar a `Horarios`.
4. Confirmar que `/scheduling/horarios` muestra franjas horarias y no `HTTP 404`.
5. Navegar a `Fichas`.
6. Confirmar que `/academic-management/fichas` muestra registros y paginacion.
7. Navegar a `Seguimiento`.
8. Confirmar que monitoring no muestra el mensaje de cliente HTTP faltante.
9. Navegar a `Indicadores`.
10. Confirmar que el MFE de monitoring carga dentro del shell.
11. Navegar a `Mi disponibilidad (instructor)` o ruta de actores.
12. Confirmar que la pantalla de actores se ve estilizada y sin header/sidebar duplicados.
13. Verificar que el menu lateral y topbar pertenecen al shell, no a cada MFE.

### Criterios de aceptacion para esta entrega

- El shell monta remotes federados reales cuando `VITE_REMOTE_SOURCE=federation`.
- El shell consume sesion por HTTP contra el BFF local.
- Las rutas principales no quedan bloqueadas por errores visibles `HTTP 404`.
- Monitoring recibe `httpClient` desde el shell.
- Actors MFE carga estilos al ejecutarse como remote.
- Los MFEs se visualizan como modulos dentro de un sistema unificado.
- Docker infra valida su configuracion con `.env.example`.

## Consideraciones para arquitectura

### Decision de integracion aplicada

El shell se mantiene como host principal y unico chrome de navegacion. Los MFEs deben renderizar contenido de dominio dentro del area central. Cuando un MFE tambien tiene chrome propio para modo standalone, debe detectar el modo hospedado y ocultar ese chrome para evitar duplicidad visual.

### Datos locales del BFF

El BFF local fue usado como fachada temporal para desbloquear validaciones de UI y composicion. Esto permite a QA validar comportamiento visual, enrutamiento, contratos basicos de consumo y montaje de remotes mientras los backends reales se completan o se conectan al entorno.

### Riesgos pendientes

- Algunos endpoints siguen siendo datos locales de integracion, no respuestas de servicios productivos.
- Faltan pruebas end-to-end automatizadas completas para todos los dominios.
- Algunos remotes muestran advertencia de React por import de `createRoot` desde `react-dom`; no bloquea la demo, pero conviene corregirlo en una limpieza posterior.
- Se debe revisar si los lockfiles nuevos en audit/document deben permanecer como politica de reproducibilidad o si esos repos prefieren no versionarlos.

## Evidencia de validacion ejecutada

Comandos ejecutados:

```bash
npm run build
```

Repos donde se ejecuto build directamente:

- `design-software-web-bff`
- `design-software-web-shell`
- `design-software-actors-mfe`

Verificaciones HTTP:

```bash
GET http://127.0.0.1:5000/api/v1/time-slots -> 200
GET http://127.0.0.1:5000/api/v1/fichas -> 200
GET http://127.0.0.1:5000/api/v1/kpi-types -> 200
GET http://127.0.0.1:5106/remoteEntry.js -> 200
GET http://127.0.0.1:5000/api/v1/ficha-trackings -> 200
GET http://127.0.0.1:5000/time-slots -> 200
GET http://127.0.0.1:5000/api/v1/generated-alerts -> 200
```

Validacion Docker:

```bash
docker compose --env-file .env.example config --quiet
```

Verificaciones UI con navegador:

- `/scheduling/horarios`: contenido real de scheduling, sin `HTTP 404` visible.
- `/academic-management/fichas`: lista de fichas, sin `HTTP 404` visible.
- `/monitoring/seguimiento`: seguimiento de ficha, sin `HTTP 404` visible.
- `/monitoring/indicadores`: pantalla real de monitoring.
- `/actors/mi-disponibilidad`: MFE estilizado e integrado al shell.

## Conclusion

La integracion local quedo funcional para que QA y arquitectura puedan validar el shell como host de MFEs reales, el consumo HTTP hacia el BFF local y las pantallas clave sin errores visibles de montaje o consumo. La arquitectura final esperada es un sistema unificado: shell con topbar/sidebar comunes y MFEs renderizados como contenido interno, no como aplicaciones visualmente independientes duplicadas.
