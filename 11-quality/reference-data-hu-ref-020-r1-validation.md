# Validación de HU-REF-020 y R1 — Reference Data

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Valery Sinai Trujillo Quintero | Equipo: Reference Data

## Contexto

Plan de pruebas sobre ramas originales de code-sena. La ejecución personal del 19 de octubre es antecedente y no acredita estos cambios en develop del macroproyecto. La documentación se preparó antes del código. Las secciones fechadas 20/10 conservan el antecedente local; la evidencia verificada del 24/10 actualiza publicación y CI. La adaptación local ya se ejecutó sobre las fuentes originales; los resultados siguientes no equivalen a aprobación ni merge.

## Contenido

### Evidencia verificada y límites de cierre — 2026-10-24

Corte de consulta GitHub: `2026-10-24T10:11:59.598326-05:00`. Una revisión conceptual favorable, un CI verde, la aceptación de un ADR y un merge son hechos distintos.

| Componente | HEAD consultado | Evidencia | Estado al corte |
|---|---|---|---|
| Frontend Platform | `af3bd3603903eb2f17a9321c9679cbe4d187ec97` | [CI #39861672279](https://github.com/code-sena/design-software-frontend-platform/actions/runs/39861672279), [PR #8](https://github.com/code-sena/design-software-frontend-platform/pull/8) | SUCCESS: 34 pruebas y typecheck |
| Web Shell | `e91a2c0b687e5ade246553eb05ea7bc837f908aa` | [CI #39862188250, intento 2](https://github.com/code-sena/design-software-web-shell/actions/runs/39862188250), [PR #17](https://github.com/code-sena/design-software-web-shell/pull/17) | SUCCESS en ambos jobs: 106 pruebas, tipos/lint/build, tres Chromium y R1 real. El PR vuelve a tener mergeable=false frente a develop; un nuevo HEAD exige CI completo nuevo |
| Reference Data MFE | `66502153590cee6d4cc14a277937fd778f00ffc7` | [CI #39862199586](https://github.com/code-sena/design-software-reference-data-mfe/actions/runs/39862199586), [PR #13](https://github.com/code-sena/design-software-reference-data-mfe/pull/13) | FAILURE en el control de acceso privado; las 71 pruebas solo tienen evidencia local |
| Reference Data DB | `be3d4810dd3f8602979722b8a132d779c7e9a192` | [PR #81](https://github.com/code-sena/design-software-reference-data-db/pull/81) | Migración formal publicada; PR abierto hacia develop |
| IAM DB | `361a1d7bc21063dafdccf18808976108acba5a12` | [PR #80](https://github.com/code-sena/design-software-iam-db/pull/80) | Fixture publicado; PR abierto hacia develop |
| Servicio e infraestructura | `068593f` / `02046c5` | [PR #26](https://github.com/code-sena/design-software-reference-data-service/pull/26), [PR #44](https://github.com/code-sena/design-software-docker-infra/pull/44) | Dependencias enlazadas; integración probada en el CI del shell, sin merge todavía |

Los siete PR de implementación siguen abiertos. El CI del shell construye las fuentes de sus dependencias y registra las revisiones usadas; no sustituye la suite unitaria propia del MFE ni certifica automáticamente otro SHA. No se acredita migración al develop compartido, despliegue productivo, aceptación arquitectónica ni Done·Dev por estos resultados.



### Identificación y gates

| Campo | Valor |
|---|---|
| HU | [HU-REF-020, docs#250](https://github.com/code-sena/design-software-docs/issues/250) |
| Reto | R1 individual de Reference Data; sin crear una HU paralela |
| Ejecución propia | PASS local sobre las ramas originales; 2026-10-20 |
| QA | Revalidación remitida a Arquitectura: HU/R1 funcionalmente aprobables; CI propio MFE pendiente y nuevos conflictos de integración |
| Arquitectura | ADR-020/021 PROPOSED; revisión pendiente |
| Integración original | Ocho PR publicados; sin merge al corte. Shell requiere resolver conflicto y revalidar su nuevo HEAD; docs se reconcilia en este PR |

### Casos obligatorios

| TC | Criterio | Prueba / pasos | Resultado esperado | Resultado original |
|---|---|---|---|---|
| REF-020-01 | E1/E2 | Reactor Maven raíz, JDK 21, migraciones y fixtures reales | IAM ready y datos reproducibles; sin ajustes ocultos | PASS local |
| REF-020-02 | E3/E4 | Login real, claims, firma/issuer/exp, GET/POST/PUT parámetros | Admin 200/201/200; aprendiz 403; JWT ausente/malformado/alterado 401 | PASS local |
| REF-020-03 | Flujo visual | Login por formulario; remote real; crear/editar parámetro y recargar; salir | Persistencia real, features de IAM, logout y token eliminado | PASS local |
| REF-020-04 | Permisos visuales/API | Login aprendiz; catálogo lectura; parámetros bloqueados y petición directa | UI restringida, API parámetros 403; sin JWT/ inválido 401 | PASS local |
| REF-R1-01 | Outbox | Commit negocio+evento y error de serialización controlado | Commit conjunto o rollback conjunto | PASS local |
| REF-R1-02 | Inbox | 12 entregas concurrentes; mismo ID diferente payload; fallo de proyección | 1 efecto; contenido distinto rechazado; rollback de inbox/efecto | PASS local |
| REF-R1-03 | Retry/DLQ | Fallo real, espera 1/2/4, DLQ y corrección/replay | 1 inicial+3 retries; mismo ID/cuerpo; efecto aplicado una vez | PASS local |
| REF-R1-04 | Caos desde UI | A con broker; detenerlo; B por formulario; reiniciar servicio; recuperar broker | A/B persistentes; 2 eventos originales, inbox 2, efectos 2 | PASS local |
| REF-R1-05 | Deduplicación tras caída | Republicar A/B con IDs persistidos; barrera FIFO extra | 2 efectos para 2 originales pese a 2 reenvíos; barrera excluida | PASS local |
| REF-INT-01 | Regresión/contratos | Tests de servicio y front, typecheck/lint/build y gate host/remote | Sin regresiones y compatible con ADR-009 | PASS local |

No aceptar Skip como evidencia de integración. R1 es entrega al menos una vez con efecto idempotente de la proyección, no garantía universal exactly-once. La prueba de broker solo opera el proyecto aislado y lo recupera en finally.

### Ejecución local del macroproyecto — 2026-10-20

Frontend/integración finalizado a las **16:39:22 Colombia (UTC−05:00)**. Proyecto Compose `macro-ref-r1`; código desde las siete ramas `hu-ref-020-r1-dev`, creadas desde `origin/develop`. La rama de docs es `docs/reference-data-r1-resilience-and-messaging`, desde `main`. Los cambios nuevos de código están todavía sin commit: los SHA siguientes identifican la base de revisión, no un commit final de entrega.

| Repositorio | SHA base | Validación propia |
|---|---|---|
| reference-data-service | `38bbbd5` | Integración JWT real, outbox/inbox, retries/DLQ/replay y regresión de aplicación Go |
| reference-data-db | `dede0c3` | Migraciones nuevas aplicadas con Liquibase; changesets históricos conservados |
| iam-db | `a1e01a4` | Migraciones y fixture de usuarios reproducibles en BD aislada |
| docker-infra | `996c664` | Runners y Compose ejecutados sobre fuentes originales |
| frontend-platform | `be8bd79` | Typecheck y 34 tests PASS, incluido error plano/anidado |
| reference-data-mfe | `723363c` | Build/typecheck, lint y 71 tests PASS, incluido aislamiento del cliente por Context |
| web-shell | `69b234a` | Build, lint, tipos E2E y 106 tests PASS; 3 casos Chromium reales PASS |

IAM Service (`6987e0f`), design-system (`f473ca6`) y web-bff (`52dd029`) se reutilizaron sin modificar. IAM se construyó desde el reactor Maven con JDK 21. El stack de validación usa PostgreSQL 16, Liquibase 4.33, RabbitMQ y Node 24 según los Compose versionados.

### Resultados de integración

| Suite | Resultado comprobado |
|---|---|
| JWT real (`TestHURef020ParametersWithRealIAMJWT`) | PASS: claims de IAM, admin GET/POST/PUT 200/201/200, aprendiz 403; JWT ausente, malformado o con firma alterada 401 |
| Outbox (`TestR1TransactionalOutbox`) | PASS: negocio y evento confirman juntos; fallo de serialización revierte ambos |
| Inbox/DLQ (`TestR1AtomicInboxAndDLQ`) | PASS: 12 entregas concurrentes producen 1 efecto; rechazo de contenido alterado; rollback; 1 intento inicial + retries 1/2/4; replay conserva ID/cuerpo |
| R1 completo (`validation/r1-reference/run.ps1`) | PASS: cinco tests obligatorios, incluida caída real del broker, reinicio del servicio y recuperación; sin omisiones |
| Navegador (`playwright.reference.config.ts`) | PASS: 3 casos Chromium, 0 fallos, 0 omitidos; login/edición/persistencia/logout, permisos y caos desde formularios |

La ejecución visual `A005BE8BD7C2` verificó **2 eventos originales, inbox 2, efectos 2, 2 reenvíos deliberados, 0 pérdidas y 0 efectos duplicados**; la barrera FIFO adicional no se cuenta como evento del escenario. R1 garantiza entrega al menos una vez y efecto idempotente para esta proyección. La suite completa de backend conserva además su propio `run_id` en el resultado local.

### Reproducción y evidencias

Desde el repositorio original docker-infra, con las fuentes de los siete repositorios en las ramas indicadas:

```powershell
./validation/frontend-reference/run.ps1
./validation/r1-reference/run.ps1
```

Con el backend preparado, la primera orden admite `-SkipBackendPreparation`. Ambos runners deben terminar con exit code 0 y `status: passed`; `prepared` no acredita pruebas. No ejecutar ambos a la vez: el escenario de caos opera el broker aislado.

| Acceso local aislado | Puerto |
|---|---|
| Shell | 5010 |
| Remote Reference Data | 5115 |
| IAM | 18102 |
| Reference Data | 18100 |
| PostgreSQL | 15440 |

El perfil autónomo HU-REF-020 reserva otros puertos (IAM 18112, Reference Data 18110, PostgreSQL 15441); esta evidencia corresponde al perfil conjunto `macro-ref-r1`. Son puertos de loopback para validación propia; no sustituyen el ingreso compartido de Traefik ni acreditan migraciones en el entorno de develop.

Los resultados crudos están excluidos de Git en docker-infra: `validation/frontend-reference/evidence/result.json`, `playwright-result.json`, `backend-hu-ref-020.log`, `backend-r1.log`, y `validation/r1-reference/evidence/` (migraciones, versiones y cinco logs de pruebas). Las capturas publicables se regeneraron capturando solo el remote, sin identidad ni controles de sesión del host, y se registraron en `assets/images/`. Los datos mostrados son fixtures sintéticas. No se añaden imágenes, ADR ni reportes a repositorios de código. No publicar `.env`, passwords, JWT, claves, HAR ni trazas de sesión.

### Correspondencia con el plan de mejoramiento

Asignación verificada en la página 13 del acta ADSO-3145555-Acta02: **HU-REF-020** (levantado E2E real Reference Data/IAM) y **R1** sobre Reference Data Service. El numeral 6 (p. 3) pide dominio levantado con perfil Docker, MFE dentro del shell y flujo sin mocks; el numeral 7 (p. 4) pide PR propio, ADR e informe con capturas, métricas y salidas de prueba; el numeral 8 (p. 4) define los cuatro criterios de R1. Esta evidencia cubre la ejecución local; los PR/merges y las aprobaciones permanecen pendientes.

| Requisito | Implementación / evidencia |
|---|---|
| E2E IAM + Reference Data y visual | Login real, JWT y features; parámetros persistentes desde remote dentro del shell |
| R1(a) Outbox transaccional | `parameterization.outbox_event`; negocio y evento en la misma transacción, con rollback comprobado |
| R1(b) Consumidor idempotente | `event_inbox` y proyección en la misma transacción antes de ACK; doce entregas concurrentes con un efecto |
| R1(c) Backoff, DLQ y replay manual | Retry 1/2/4 s, DLQ durable y comando `reference-data-replay`; prueba real de recuperación |
| R1(d) Caos automatizado | Broker detenido a mitad del flujo y servicio reiniciado; seis eventos recuperados y doce reenvíos sin pérdida ni efectos duplicados |
| ADR e informe | ADR-020/021 PROPOSED y este informe en docs; PR #340 publicado, pendiente de revisión/merge |

### Capturas saneadas y salidas de prueba

La ejecución adicional de las tres pruebas Chromium para generar capturas saneadas pasó sin fallos ni omisiones; identificador visual `MVH7RVVI`. Cada captura excluye el encabezado y la navegación del host que muestran la sesión.

- [HU-REF-020: parámetro creado, editado y persistido](../assets/images/reference-data-hu-ref-020-parameter.png).
- [HU-REF-020: lectura de catálogos y restricciones de aprendiz](../assets/images/reference-data-hu-ref-020-learner.png).
- [R1: catálogo persistente después de recuperar broker y servicio](../assets/images/reference-data-r1-recovered-catalog.png).

> **Pendiente de la autora:** captura propia del estado «escritura de catálogo durante caída de broker». La imagen que se había registrado para ese estado era idéntica byte a byte a la de «catálogo persistente después de recuperar» y no mostraba ningún indicador del broker, por lo que se retiró. Mientras no exista esa captura, el estado con el broker detenido se acredita con las aserciones HTTP/SQL/logs (`OUTBOX`, `RETRY/DLQ` y `CHAOS` de abajo), no con una imagen.

Fragmentos de salida reales, sin credenciales:

```text
E3 PASS: real IAM login; expected issuer, subject, expiry, roles and scoped features
E4 PASS: admin GET 200 / POST 201 / PUT 200; learner GET/POST/PUT 403; missing, malformed and modified-signature JWT 401
OUTBOX PASS: business row and event commit together; serialization failure rolls both back
INBOX PASS: 12 concurrent deliveries, 1 committed effect
RETRY/DLQ PASS: 1 initial attempt + retries at 1s/2s/4s; inbox rollback; manual replay preserved event_id and applied once
CHAOS PASS: 6 committed events, 6 published, 6 inbox records, 6 effects; broker stopped mid-flow and service restarted; 12 deliberate duplicates; lost=0 duplicated_effects=0
3 passed
```

Métricas de caos backend: `run_id=8e717aca0708`, originales=6, publicados=6, inbox=6, efectos=6, reenvíos=12, perdidos=0, efectos duplicados=0. La barrera de procesamiento queda fuera de esos conteos. Las capturas muestran el estado visual; los conteos se verifican automáticamente en PostgreSQL.

### Configuración del editor validada

Se corrigió TS5101 eliminando `baseUrl` del tsconfig del shell; los aliases conservan sus rutas relativas. `e2e/tsconfig.json` hereda la configuración Node de las pruebas. Validación con TypeScript 5.9.3 del proyecto y 6.0.3 de VS Code: cero errores en la configuración E2E; la configuración principal también pasa con 6.0.3 y el build del shell termina correctamente.

### Pendientes de integración

- Los siete PR de implementación y docs #340 ya están publicados; revisar y mergear dependencias, sin declarar develop integrado antes de ese paso.
- Administración debe configurar SHELL_DEPS_TOKEN para MFE #13 y QA debe comprobar su CI propio.
- Resolver el conflicto actual de shell #17 y repetir su workflow completo sobre el HEAD resultante.
- Obtener revisión independiente de QA y Arquitectura; ADR-020/021 continúan PROPOSED y este informe continúa 🟡.
- Aplicar y validar migraciones en el develop compartido conforme al proceso del equipo; después verificar los merges y completar SHA finales, enlaces y board/hu-log.

No asignar Done·Dev ni declarar cumplido el plazo de integración únicamente por esta ejecución local verde.

## Referencias

- [ADR-020](../05-architecture/decisions/records/ADR-020-reference-data-iam-e2e-integration.md), [ADR-021](../05-architecture/decisions/records/ADR-021-reference-data-resilient-messaging.md).
- [Plan de ejecución](../10-devops/reference-data-integration.md), [modelo](../09-microservices/services/02-reference-data-service/data-model.md), [trazabilidad](../04-requirements/traceability-matrix.md).
