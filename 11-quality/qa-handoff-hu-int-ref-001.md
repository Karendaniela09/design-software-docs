# MD DE DESARROLLO - HU-INT-REF-001: INTEGRACIÓN DE BD, IAM, MFE Y ENTORNO DE REFERENCE DATA

> Estado: 🟡 Entrega para revisión de QA | Última actualización: 2026-10-25
> Autora: Valery Sinaí Trujillo Quintero | Equipo: Reference Data

## 1. INFORMACIÓN GENERAL

| Campo | Información |
|---|---|
| **Historia de usuario** | HU-INT-REF-001 — Conectar BD, seguridad IAM, MFE y entorno de Reference Data |
| **Issue** | [code-sena/design-software-docs#294](https://github.com/code-sena/design-software-docs/issues/294) |
| **Prioridad** | Must |
| **Estado** | Implementación publicada en seis PRs; validación técnica local de los diez criterios realizada. Pendientes revisión independiente, resolución del check fallido del shell y promoción al entorno compartido. |
| **Ambiente validado** | DEV local aislado; proyecto Compose `macro-ref-int001-acceptance`. No equivale a una validación en QA ni en el `develop` compartido. |
| **Microservicios y componentes** | Reference Data API y MFE, IAM como dependencia, PostgreSQL, Frontend Platform, Web Shell y edge Traefik |
| **Capas** | Persistencia, migraciones, autenticación/autorización, frontend federado, configuración y pruebas de integración |
| **Desarrolladora** | Valery Sinaí Trujillo Quintero |
| **Fecha de actualización** | 25/10/2026 |
| **Rama de código** | `hu-int-ref-001-dev` en cada repositorio de código modificado |
| **Rama documental** | `docs/hu-int-ref-001-integration` |
| **Rama destino** | Código → `develop`; documentación → `main` |
| **Estado de publicación** | Seis ramas publicadas en `origin`; seis PRs abiertos y sin merge en la consulta de esta entrega. Sin aprobaciones registradas en esa consulta. |
| **Fuente canónica de la entrega** | Este documento en `design-software-docs/11-quality/qa-handoff-hu-int-ref-001.md`, incluido en [Docs PR #426](https://github.com/code-sena/design-software-docs/pull/426). El archivo entregado fuera de ese repositorio es una copia para revisión. |

### Repositorios, ramas, commits y PRs

| Repositorio modificado | Rama | Commit de entrega | PR | Destino |
|---|---|---|---|---|
| `design-software-frontend-platform` | `hu-int-ref-001-dev` | [`f589855`](https://github.com/code-sena/design-software-frontend-platform/commit/f5898551c44e33c35d7e00cb627119c6a1148713) | [PR #11](https://github.com/code-sena/design-software-frontend-platform/pull/11) | `develop` |
| `design-software-web-shell` | `hu-int-ref-001-dev` | [`d4c9178`](https://github.com/code-sena/design-software-web-shell/commit/d4c91781ed8f1857daf1f25416268758c2a9884b) | [PR #27](https://github.com/code-sena/design-software-web-shell/pull/27) | `develop` |
| `design-software-reference-data-mfe` | `hu-int-ref-001-dev` | [`00d6630`](https://github.com/code-sena/design-software-reference-data-mfe/commit/00d66302d0c51f65bd66c035501fd30b30acdc8f), sobre implementación [`c134e39`](https://github.com/code-sena/design-software-reference-data-mfe/commit/c134e39a39aab5577d6da9458a9e9f5b276e6e3a) | [PR #16](https://github.com/code-sena/design-software-reference-data-mfe/pull/16) | `develop` |
| `design-software-reference-data-service` | `hu-int-ref-001-dev` | [`f7070fc`](https://github.com/code-sena/design-software-reference-data-service/commit/f7070fcf26ce8602d648f9a6cb0da54c91e5f921) | [PR #29](https://github.com/code-sena/design-software-reference-data-service/pull/29) | `develop` |
| `design-software-docker-infra` | `hu-int-ref-001-dev` | [`f3b2917`](https://github.com/code-sena/design-software-docker-infra/commit/f3b29171408936145059bb01532b67e7ae16c445) | [PR #55](https://github.com/code-sena/design-software-docker-infra/pull/55) | `develop` |
| `design-software-docs` | `docs/hu-int-ref-001-integration` | Contrato [`0f385a8`](https://github.com/code-sena/design-software-docs/commit/0f385a82910360c0602faacf7a581fbd5110cfd2), evidencias [`80f414c`](https://github.com/code-sena/design-software-docs/commit/80f414c), metadatos [`b9e69d5`](https://github.com/code-sena/design-software-docs/commit/b9e69d50414819da114d8f326f51461e149c339b). El commit adicional de esta entrega se consulta en el PR. | [PR #426](https://github.com/code-sena/design-software-docs/pull/426) | `main` |

Todos los commits y los títulos/descripciones de los PRs de esta entrega están en inglés. La aprobación y el merge siguen el proceso del equipo; este documento no los acredita.

---

## 2. OBJETIVO Y ALCANCE UNIFICADO

Permitir que un usuario autorizado acceda al MFE real de Reference Data desde el shell, utilizando la sesión de IAM y operaciones persistidas en PostgreSQL conforme a sus permisos reales.

La entrega cubre el recorrido **navegador → shell → remote Reference Data → cliente autenticado → edge → API Go → PostgreSQL**. IAM emite los tokens y publica JWKS; Reference Data valida localmente el JWT y aplica los features/scopes exigidos por cada operación.

Se coordinaron seis repositorios, manteniendo cada cambio en su propietario. IAM Service, IAM DB y Reference Data DB se utilizaron como dependencias existentes y **no se modificaron** para esta HU. Tampoco se alteraron changesets ya aplicados.

La referencia funcional son las nueve tablas de negocio: seis de `institutional_structure` y tres de `parameterization`. Las tres tablas adicionales de mensajería R1 se conservan. La revisión de Outbox, retry/DLQ y caos de R1 no se presenta como una nueva entrega de esta HU.

---

## 3. CRITERIOS DE ACEPTACIÓN

| Criterio | Comprobación requerida para esta entrega |
|---|---|
| **CA1 — Migraciones** | Crear esquemas, nueve tablas de negocio, restricciones, índices, roles, grants y seeds de la revisión utilizada sobre una BD limpia; repetir el changelog sin duplicar ni cambiar datos. |
| **CA2 — Cuenta de aplicación** | Usar `REFERENCE_DATA_DATABASE_URL` con una cuenta no administradora que pueda asumir `reference_reader` y `reference_writer`. |
| **CA3 — URL pública** | Enrutar `/reference-data/api/v1/training-centers` hacia `/api/v1/training-centers` en Go, sin perder ni duplicar prefijos. |
| **CA4 — Federación y permisos** | Cargar `referenceDataMfe`, módulo `./App`, con permisos reales enviados por el shell; sin autorización basada en los permisos de demostración de `main.tsx`. |
| **CA5 — Cliente autenticado** | Utilizar Frontend Platform para Bearer y ciclo de sesión. Los props controlan presentación; el backend autoriza cada operación. |
| **CA6 — JWT/JWKS** | Verificar RS256, issuer, expiración y features/scopes mediante `IAM_JWT_ISSUER` e `IAM_JWKS_URL`, sin reconstruir roles ni consultar la BD de IAM. |
| **CA7 — Errores y separación de permisos** | Probar 401/403 y separación lectura/escritura para jerarquía, catálogos y parámetros; respetar `{error:{code,message,trace_id}}`. |
| **CA8 — Normalización de scopes** | Evitar que eliminar el sufijo de un claim convierta permisos restringidos en permisos globales. Revisar la política con QA/Arquitectura. |
| **CA9 — Contrato y tipos** | Generar los tipos del MFE desde los dos archivos OpenAPI fijados por revisión y hash; sustituir las proyecciones manuales utilizadas y actualizar README. |
| **CA10 — Sondas y lectura real** | Verificar liveness/readiness por el edge, dependencia de PostgreSQL y lectura real de datos desde navegador. |

---

## 4. EVIDENCIA EN EL CÓDIGO

### 4.1 Rutas públicas y cliente autenticado

- [Requester del MFE](https://github.com/code-sena/design-software-reference-data-mfe/blob/00d66302d0c51f65bd66c035501fd30b30acdc8f/src/adapter/out/http/referenceDataHttp.ts): agrega `/reference-data/api/v1` al utilizar el cliente inyectado.
- [Prueba del cliente real y training centers](https://github.com/code-sena/design-software-reference-data-mfe/blob/00d66302d0c51f65bd66c035501fd30b30acdc8f/tests/integration/AuthenticatedTrainingCenters.test.ts): comprueba exactamente un prefijo y Bearer.
- [Composición del shell](https://github.com/code-sena/design-software-web-shell/blob/d4c91781ed8f1857daf1f25416268758c2a9884b/src/shell/remote/RemoteRoutes.tsx): entrega identidad, cliente y permisos al remote.
- [Registro de rutas Go](https://github.com/code-sena/design-software-reference-data-service/blob/f7070fcf26ce8602d648f9a6cb0da54c91e5f921/cmd/reference-data-api/main.go): registra `/api/v1` y las sondas; configura DSN y seguridad.
- [Compose de integración](https://github.com/code-sena/design-software-docker-infra/blob/f3b29171408936145059bb01532b67e7ae16c445/validation/int-ref-001/compose.yml): utiliza la tabla canónica de Traefik y las imágenes estáticas del shell/MFE.

### 4.2 Seguridad y alcance

- [Permisos de sesión en Frontend Platform](https://github.com/code-sena/design-software-frontend-platform/blob/f5898551c44e33c35d7e00cb627119c6a1148713/src/session/session.ts): intersecta códigos de `/auth/me` con grants del JWT en memoria para presentación.
- [Pruebas de normalización](https://github.com/code-sena/design-software-frontend-platform/blob/f5898551c44e33c35d7e00cb627119c6a1148713/src/session/reference-permissions.test.ts): rechaza grants `REF_*` sin scope, restringidos o malformados.
- [Seguridad del backend](https://github.com/code-sena/design-software-reference-data-service/blob/f7070fcf26ce8602d648f9a6cb0da54c91e5f921/internal/adapter/in/http/security/security.go): valida JWT y exige `GLOBAL` para los features `REF_*`.
- [Matriz de features y errores](https://github.com/code-sena/design-software-reference-data-service/blob/f7070fcf26ce8602d648f9a6cb0da54c91e5f921/internal/adapter/in/http/security/reference_scope_test.go): cubre los seis features, tokens ausentes/inválidos, feature incorrecto, scope restringido y scope global.

La decodificación del JWT en frontend se utiliza únicamente para presentación. La firma, issuer, expiración y autorización efectiva se verifican en backend.

### 4.3 Tipos y contrato reproducible

- [Proveniencia y hashes del contrato](https://github.com/code-sena/design-software-reference-data-mfe/blob/00d66302d0c51f65bd66c035501fd30b30acdc8f/contracts/openapi/source.json).
- [Generador y comprobación sin modificar la salida](https://github.com/code-sena/design-software-reference-data-mfe/blob/00d66302d0c51f65bd66c035501fd30b30acdc8f/scripts/generate-reference-data-types.mjs).
- [Contrato documental fijado](https://github.com/code-sena/design-software-docs/blob/0f385a82910360c0602faacf7a581fbd5110cfd2/07-api/contracts/openapi/reference-data.yaml) y su [`_shared.yaml`](https://github.com/code-sena/design-software-docs/blob/0f385a82910360c0602faacf7a581fbd5110cfd2/07-api/contracts/openapi/_shared.yaml).

`check:types` comprueba hashes y regeneración. Se ejecuta en CI del MFE y en su build Docker. Las proyecciones de geografía y estructura institucional son aliases de los esquemas generados.

### 4.4 Persistencia, sondas y pruebas reales

- [Verificador SQL](https://github.com/code-sena/design-software-docker-infra/blob/f3b29171408936145059bb01532b67e7ae16c445/validation/int-ref-001/verify-db.sql): comprueba tablas, seeds acordados, índices, restricciones, roles y login no administrador.
- [Runner de aceptación](https://github.com/code-sena/design-software-docker-infra/blob/f3b29171408936145059bb01532b67e7ae16c445/validation/int-ref-001/run.ps1): ejecuta migraciones repetidas, prueba de navegador, comprobación SQL y caída/recuperación de BD.
- [Pruebas API/navegador](https://github.com/code-sena/design-software-web-shell/blob/d4c91781ed8f1857daf1f25416268758c2a9884b/e2e/reference-data-integration.spec.ts): requieren credenciales de prueba y fallan si faltan; no sustituyen servicios reales por mocks.
- [Sondas Go](https://github.com/code-sena/design-software-reference-data-service/blob/f7070fcf26ce8602d648f9a6cb0da54c91e5f921/internal/adapter/in/http/health/health.go): readiness verifica PostgreSQL; liveness es independiente.

---

## 5. EVIDENCIA Y ESTADO DE VALIDACIÓN

### Matriz de los diez criterios

| Criterio | Evidencia obtenida | Estado para QA |
|---|---|---|
| CA1 | BD nueva; 40 changesets IAM y 21 Reference Data. Segunda aplicación de Reference Data: cero cambios y mismo snapshot de esquema/datos. Nueve tablas de negocio y tres de R1 verificadas. | PASS local; reproducir en revisión. |
| CA2 | Login `hu020_reference` separado del dueño de migraciones; sin atributos administrativos. Membresías y `SET LOCAL ROLE` comprobados; escritura de prueba revertida. | PASS local. |
| CA3 | El navegador llamó la URL pública de training centers; edge y API Go respondieron. La prueba del cliente verifica prefijo único y Bearer. | PASS local. |
| CA4 | Shell y remote reales, sin stubs para Reference Data. Usuarios con escritura, solo lectura y alcance restringido mostraron controles diferentes. | PASS local. |
| CA5 | Peticiones autenticadas, ausencia de `sena.access_token` en storage, cookie de refresh y restauración de sesión tras recarga. | PASS local. |
| CA6 | JWT real de IAM aceptado; negativos de firma, algoritmo, issuer, expiración, claims y JWKS comprobados por suites Go. Caché/rotación JWKS cubiertas. | PASS local. |
| CA7 | 401 sin token/con token inválido; 403 en escrituras de cuenta lectora y en operaciones de cuenta restringida; escritura válida de los tres grupos; envelope comprobado. | PASS local. |
| CA8 | Grants `TRAINING_CENTER` reales no se convierten en permisos globales en API ni navegación. Política basada en matriz RBAC canónica. | PASS técnico; revisión de política pendiente. |
| CA9 | Contrato y `_shared.yaml` fijados a `0f385a8`; hashes, regeneración, aliases generados y build Docker aprobados. | PASS técnico; revisión canónica del contrato pendiente. |
| CA10 | Centro visible en navegador y confirmado por SQL; datos de catálogos/parámetros persistidos. BD detenida: readiness 503 y liveness 200; BD recuperada: readiness 200. | PASS local. |

### Pruebas ejecutadas

| Validación | Resultado registrado |
|---|---|
| Frontend Platform | 63 pruebas PASS; typecheck PASS. |
| Web Shell | 160 pruebas PASS; typecheck E2E y lint PASS. |
| Reference Data MFE | 75 pruebas PASS; typecheck, lint y `check:types` PASS. |
| Total frontend | **298 pruebas PASS**. |
| Reference Data Service | `go test ./...` PASS bajo condiciones locales; los casos de integración ajenos a esta HU conservan sus guardas de entorno. |
| Go aislado, `-count=1` | Paquetes de seguridad, health y API PASS. |
| Imágenes estáticas | Build de shell y MFE PASS; MFE verificó los tipos fijados. |
| Suite real API/navegador | **4 PASS, 0 FAIL, 0 SKIP**. |
| Persistencia y sondas | Comprobación SQL y caída/recuperación de PostgreSQL PASS. |
| Documentación | Lint OpenAPI: cero errores y tres advertencias no bloqueantes; enlaces y comprobación de datos personales PASS. |

La suite genérica de Go no se utiliza como evidencia de los casos R1 que pudieran omitirse por sus variables de entorno. Las cuatro pruebas de integración de esta HU sí se ejecutaron sin omisiones.

### Estado de CI consultado para la entrega

Consulta realizada: 25/10/26, 2:35:36 a. m. (Colombia).

Esta es una fotografía de los checks publicados en los SHA indicados; puede cambiar al recibir nuevos commits. Los enlaces permiten a QA consultar el estado vigente.

| PR | SHA consultado | Estado observado y enlace |
|---|---|---|
| Platform #11 | `f589855` | [`unit-and-types`: SUCCESS](https://github.com/code-sena/design-software-frontend-platform/actions/runs/40173098049/job/121107919767). |
| MFE #16 | `00d6630` | [`unit-types-and-build`: SUCCESS](https://github.com/code-sena/design-software-reference-data-mfe/actions/runs/40173100633/job/121107928026). |
| Docs #426 | `b9e69d5` | [`Validate docs`: SUCCESS](https://github.com/code-sena/design-software-docs/actions/runs/40173104719/job/121107957204); existió otra ejecución cancelada. El nuevo commit de esta entrega debe obtener su propia validación. |
| Shell #27 | `d4c9178` | [`Static checks and unit tests`: FAILURE](https://github.com/code-sena/design-software-web-shell/actions/runs/40173342700/job/121108683917). El job [de navegador](https://github.com/code-sena/design-software-web-shell/actions/runs/40173342700/job/121108684152) estaba en ejecución; el job de manifiesto desplegado fue omitido por su configuración. No se declara CI global aprobado. |
| Service #29 | `f7070fc` | Sin check-runs ni statuses publicados en la consulta. Esto no equivale a CI aprobado. |
| Infra #55 | `f3b2917` | Sin check-runs ni statuses publicados en la consulta. Esto no equivale a CI aprobado. |

**Pendiente visible:** revisar el log del fallo del shell, atender los errores que correspondan y repetir CI. Su consumidor requiere la API de Platform #11; debe integrarse esa dependencia antes del merge del shell. No se atribuye el fallo a una causa concreta sin revisar el log.

### Reproducción

Desde la raíz de `design-software-docker-infra`, con las ramas/revisiones relacionadas y las dependencias descritas en la guía:

```powershell
./validation/int-ref-001/run.ps1
```

El runner crea un proyecto nuevo y una BD aislada; prepara las credenciales en un archivo ignorado. Sus puertos de revisión son edge `18120`, IAM debug `18122` y PostgreSQL debug `15442`, en loopback. Deben comprobarse colisiones antes de ejecutar otro stack.

Resultado final local: `status=passed`, proyecto `macro-ref-int001-acceptance`, cuatro pruebas integradas aprobadas, cero omisiones. Evidencias detalladas locales: `validation/int-ref-001/evidence/` y `web-shell/test-results/`; estos directorios no se versionan. No se adjuntan contraseñas, cookies, JWT ni llaves privadas.

---

## 6. DECISIONES DE INTEGRACIÓN Y PUNTOS POR REVISAR

### Scopes

La matriz RBAC vigente asigna los seis features `REF_*` con scope `GLOBAL`. La implementación no interpreta `TRAINING_CENTER`, `AREA` ni scopes de propiedad como autorización global. Tampoco inventa filtros por centro: una política futura de ese alcance requerirá contrato y filtrado explícitos. QA/Arquitectura debe revisar esta interpretación de la matriz en los PRs.

### Prefijos y CORS

La URL pública es `/<dominio>/api/v1/...` bajo un mismo origen. Para este dominio: `/reference-data/api/v1/...`. Traefik elimina `/reference-data` una vez y Go conserva `/api/v1`. El MFE no duplica ese prefijo. Las rutas relativas son iguales en los ambientes desplegados; cambian origen HTTPS y secretos. No se requiere una excepción CORS para el flujo integrado de origen único.

### Contrato y 503

El MFE utiliza los dos archivos fijados del contrato documental en `0f385a8`. El contrato incluye `503 DEPENDENCY_UNAVAILABLE` cuando no se pueden obtener claves JWKS. Es diferente del 503 de readiness por indisponibilidad de dependencias. La incorporación del contrato y su revisión canónica se realizan en Docs #426.

### Límites

- La entrega no acredita despliegue ni migraciones en un entorno compartido.
- Los otros remotes no están desplegados en el stack aislado; sus reintentos de federación pueden retrasar carga/recarga. La prueba exige el montaje de Reference Data en un máximo de 30 segundos. No se presenta una validación de rendimiento global.
- La revisión de QA, Arquitectura y pares continúa pendiente; los PRs no estaban mergeados al preparar esta entrega.
- No se solicita cerrar la HU mientras el CI del shell y las revisiones requeridas sigan pendientes.

---

## 7. LÍMITES Y RESPONSABILIDADES POR REPOSITORIO

| Repositorio | Responsabilidad de esta entrega |
|---|---|
| Frontend Platform — [#11](https://github.com/code-sena/design-software-frontend-platform/pull/11) | Normalización sin ampliación de scopes, resolver de permisos de sesión y pruebas. |
| Web Shell — [#27](https://github.com/code-sena/design-software-web-shell/pull/27) | Aplicar los permisos al menú y al remote; pruebas API/navegador con configuración dedicada. |
| Reference Data MFE — [#16](https://github.com/code-sena/design-software-reference-data-mfe/pull/16) | Ruta autenticada correcta, tipos reproducibles, vista de lectura y controles de escritura. |
| Reference Data Service — [#29](https://github.com/code-sena/design-software-reference-data-service/pull/29) | Features/scopes en backend, separación 401/403 y matriz de pruebas. |
| Docker Infra — [#55](https://github.com/code-sena/design-software-docker-infra/pull/55) | BD y cuentas aisladas, runner de aceptación, migraciones repetidas, edge, persistencia y sondas. |
| Docs — [#426](https://github.com/code-sena/design-software-docs/pull/426) | Contrato, guía, evidencias y entrega a QA. |

Dependencias sin cambios propios en esta HU: Reference Data DB `5a366fe`, IAM DB `1768e47` e IAM Service `7358f6d`. Sus migraciones y comportamiento se ejercitaron en el entorno aislado. No corresponde crear un PR de esos repositorios sin cambios que lo justifiquen.

Orden de integración: revisar contrato/política y **mergear Platform #11 antes que Shell #27**; coordinar backend, MFE e infraestructura; después repetir la validación sobre el conjunto integrado y comprobar el entorno compartido.

---

## 8. DEFINITION OF READY / DONE

### DoR — entrega disponible para revisión

- [x] HU e issue identificadas, alcance y diez criterios relacionados.
- [x] Seis PRs publicados con ramas y commits trazables.
- [x] Contrato, URLs y política de scope disponibles para revisión.
- [x] Credenciales sintéticas generadas sin incluir secretos en Git.
- [x] Runner y evidencia local reproducible documentados.

### DoD técnico local

- [x] Migraciones sobre BD nueva y segunda aplicación sin cambios.
- [x] Cuenta no administradora y roles reader/writer comprobados.
- [x] Ruta pública, rewrite y remote reales comprobados.
- [x] Sesión IAM y cliente Bearer utilizados desde el navegador.
- [x] JWT/JWKS, 401/403 y envelope comprobados.
- [x] Lectura/escritura y scopes cubiertos para los tres grupos.
- [x] Tipos generados desde revisión/hashes fijados y README actualizados.
- [x] Readiness/liveness, persistencia y recuperación de BD comprobadas.
- [x] Cuatro pruebas reales aprobadas sin `Skip`.

### DoD de cierre — pendiente de QA y del proceso de integración

- [ ] Revisar y resolver el check fallido del shell; comprobar el resultado del job de navegador.
- [ ] Confirmar la revisión canónica del contrato y la política de alcance aplicable.
- [ ] Obtener revisión independiente y las aprobaciones requeridas por repositorio.
- [ ] Integrar Platform antes del consumidor Shell y comprobar CI sobre los HEAD resultantes.
- [ ] Repetir la validación sobre las versiones integradas en `develop`.
- [ ] Comprobar migraciones, usuarios de aplicación, URLs y sondas del entorno compartido correspondiente.
- [ ] Actualizar el estado de la HU conforme a las evidencias y aprobaciones finales.

---

## 9. TEXTO DE LOS PRS Y TRAZABILIDAD

Los PRs ya están publicados. Sus títulos y descripciones están en inglés:

| PR | English title |
|---|---|
| [Frontend Platform #11](https://github.com/code-sena/design-software-frontend-platform/pull/11) | `fix(session): preserve Reference Data scopes in navigation` |
| [Web Shell #27](https://github.com/code-sena/design-software-web-shell/pull/27) | `fix(shell): inject scope-safe Reference Data permissions` |
| [Reference Data MFE #16](https://github.com/code-sena/design-software-reference-data-mfe/pull/16) | `fix(reference-data): connect authenticated routes and generated contracts` |
| [Reference Data Service #29](https://github.com/code-sena/design-software-reference-data-service/pull/29) | `fix(reference-data): enforce global feature scopes for integration` |
| [Docker Infra #55](https://github.com/code-sena/design-software-docker-infra/pull/55) | `test(integration): validate HU-INT-REF-001 acceptance criteria` |
| [Docs #426](https://github.com/code-sena/design-software-docs/pull/426) | `docs(07-api): document HU-INT-REF-001 integration and acceptance evidence` |

Todos incluyen la relación:

```text
HU: code-sena/design-software-docs#294
```

Texto de alcance en inglés para la revisión coordinada:

> HU-INT-REF-001 connects the real Reference Data remote to its authenticated API and PostgreSQL through the canonical edge. The delivery preserves GLOBAL-only Reference Data scopes, pins reproducible OpenAPI inputs, verifies non-admin database access and exercises real IAM login, authorization, persistence and dependency recovery. Local acceptance tests passed; the shell CI failure, independent review and shared-environment promotion remain pending. Merge frontend-platform before the shell consumer.

---

## 10. CONCLUSIÓN

Se entrega a QA la implementación publicada en los seis PRs, con pruebas locales de los diez criterios y trazabilidad de código/contrato. La revisión debe concentrarse en la autorización GLOBAL, la ruta pública, la reproducibilidad de migraciones/tipos y el recorrido real de navegador a PostgreSQL.

**Estado de entrega: lista para revisión técnica, no aprobada ni cerrada.** El CI fallido del shell se declara expresamente; requiere atención y nueva comprobación, además de las revisiones y validación del entorno compartido. Las pruebas locales aprobadas no sustituyen esos pasos.

---

## 11. REFERENCIAS

- [Issue HU-INT-REF-001 — #294](https://github.com/code-sena/design-software-docs/issues/294).
- [Docs PR #426: contrato, guía, evidencias y entrega](https://github.com/code-sena/design-software-docs/pull/426).
- [Matriz canónica de evidencias](https://github.com/code-sena/design-software-docs/blob/b9e69d50414819da114d8f326f51461e149c339b/11-quality/reference-data-hu-int-ref-001-validation.md).
- [Guía de integración](https://github.com/code-sena/design-software-docs/blob/b9e69d50414819da114d8f326f51461e149c339b/10-devops/reference-data-int-ref-001.md).
- [Matriz RBAC de IAM](https://github.com/code-sena/design-software-docs/blob/b9e69d50414819da114d8f326f51461e149c339b/09-microservices/services/01-iam-service/rbac-design.md).
- [ADR-022: rutas del edge](https://github.com/code-sena/design-software-docs/blob/b9e69d50414819da114d8f326f51461e149c339b/05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md).
- [ADR-023: sesión propiedad del shell](https://github.com/code-sena/design-software-docs/blob/b9e69d50414819da114d8f326f51461e149c339b/05-architecture/decisions/records/ADR-023-web-shell-owns-login-and-session.md).
- [Platform PR #11](https://github.com/code-sena/design-software-frontend-platform/pull/11).
- [Shell PR #27](https://github.com/code-sena/design-software-web-shell/pull/27).
- [MFE PR #16](https://github.com/code-sena/design-software-reference-data-mfe/pull/16).
- [Service PR #29](https://github.com/code-sena/design-software-reference-data-service/pull/29).
- [Infra PR #55](https://github.com/code-sena/design-software-docker-infra/pull/55).
