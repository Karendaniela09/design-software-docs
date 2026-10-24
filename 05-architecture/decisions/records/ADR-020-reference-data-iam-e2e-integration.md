# ADR-020: Integración E2E real entre Reference Data, IAM y web-shell

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Valery Sinai Trujillo Quintero | Equipo: Reference Data

**Estado de la decisión:** PROPOSED, pendiente de revisión de Arquitectura.
**Fecha:** 2026-10-20
**Autores:** Valery Sinai Trujillo Quintero
**Equipos involucrados:** Reference Data, IAM, Frontend, DevOps, QA y Arquitectura.
**Trazabilidad de numeración:** propuesta anteriormente citada como ADR-012 de Reference Data en el PR #340; renumerada a ADR-020 al reconciliar el registro de main. No se altera el ADR-012 aceptado de Training Environment.

## Contexto

[HU-REF-020, docs#250](https://github.com/code-sena/design-software-docs/issues/250) exige levantar IAM con JDK/reactor/migraciones correctos, datos de seguridad reproducibles, un JWT real y operaciones protegidas de Reference Data. La entrega debe funcionar desde el microfrontend dentro del shell y conservar los límites por repositorio. La base HU-REF-019 ya aporta middleware JWT/JWKS, endpoints y outbox; esos componentes no se presentan como nuevos.

La validación previa en repositorios personales es un antecedente, no evidencia de integración en `code-sena/develop`. Las ejecuciones posteriores sobre las ramas del macroproyecto se relacionan en la evidencia verificada de este ADR; su éxito no acredita merges pendientes. El BFF descargado durante la validación inicial utilizaba una identidad fija de desarrollo y no se usó para acreditar autenticación real. ADR-009 exige fachada HTTP compartida e inyección por React Context; una implementación que lea tokens directamente desde el MFE o use un proveedor global mutable no satisface esa regla.

## Decisión

Se decide reproducir el recorrido navegador → web-shell → microfrontend Reference Data → API protegida con un JWT emitido y verificado por IAM real, sin mocks para el flujo evaluado.

1. **Docs primero:** decisiones, criterios y modelo viven en este repositorio. Los repositorios `-service`, `-db`, `-mfe`, `frontend-platform` e infra reciben código, pruebas/configuración y enlaces de PR al SSOT; no copias de ADR ni informes de esta entrega.
2. **IAM:** compilar el reactor raíz con Maven y JDK 21, aplicar los changelogs oficiales y ejecutar la API con validación de esquema. No modificar IAM Service si su implementación actual ya satisface el contrato. Las fixtures de seguridad pertenecen a `iam-db/test/hu-ref-020`, usan contraseñas generadas por el runner y recibidas por entorno, y están restringidas a la base aislada de validación, nunca a las cuentas del ambiente compartido.
3. **Seguridad:** Reference Data conserva verificación RS256, JWKS/kid, issuer, subject y expiración, además del feature requerido por endpoint. No aceptar `alg=none`, desactivar firmas ni ampliar roles para hacer pasar la prueba. Los sufijos de scope se pueden normalizar para visibilidad de UI, pero el servicio sigue siendo la autoridad y no se afirma implementar filtrado de recursos por scope en esta HU.
4. **Sesión:** frontend-platform contiene el cliente IAM. El shell conserva el access token en su proveedor de sesión, consulta `/auth/me` y entrega los permisos reales al remote. Se permite una entrada de login real en el shell para la validación donde IAM MFE no esté desplegado; no reemplaza las pantallas administrativas de IAM ni utiliza la identidad fija del BFF. No se persisten contraseña ni refresh token y no se añade renovación automática.
5. **Fachada y contexto:** el shell inyecta un puerto HTTP respaldado por `HttpClient` de frontend-platform; Reference Data lo distribuye mediante un React Context propio del MFE. Sus hooks y adaptadores consumen ese puerto por instancia. No se añade un getter global de tokens, un fetch de negocio directo ni almacenamiento de credenciales dentro del MFE. El paquete frontend-platform permanece TypeScript sin React.
6. **Rutas y despliegue:** el manifiesto de remotes selecciona el remote real del dominio; los no desplegados muestran estado no disponible. El perfil local de integración en docker-infra enruta el API de IAM y traduce el prefijo del navegador hacia las rutas internas del API Go. Estos proxies locales no sustituyen Traefik ni modifican el routing de otros dominios del ambiente compartido.
7. **Aislamiento de pruebas:** PostgreSQL, IAM, Reference Data y RabbitMQ se levantan en un proyecto Compose independiente con credenciales generadas, volúmenes propios y puertos de depuración solo en loopback. Es una validación local controlada conforme a la excepción de debug de ADR-007; no es una promoción a QA/staging/main ni evidencia de migraciones ejecutadas en la BD develop compartida. Cualquier aplicación al entorno compartido requiere el proceso del equipo de datos.
8. **Integración:** código en ramas hijas de `origin/develop`, documentación en rama hija de `origin/main`. No marcar Done·Dev hasta tests sobre el macroproyecto, revisión, merge de PR originales y sincronización de board/hu-log por responsables autorizados.

## Responsabilidades y límites de confianza propuestos

Esta asignación por rol debe ser ratificada por Arquitectura; no constituye nombramiento de personas ni concesión de permisos.

| Responsabilidad | Propietario propuesto | Límite verificable |
|---|---|---|
| Identidad, firma y claims del JWT, /auth/me | Equipo IAM | IAM autentica y emite; Reference Data no administra identidades de IAM |
| Login, almacenamiento de access token y logout | Equipo del web-shell | El host usa sessionStorage mediante su proveedor; no persiste contraseña ni refresh token y limpia el token al salir |
| Cliente IAM y transporte HTTP reutilizable | Equipo Frontend Platform | TypeScript sin React; adjunta Bearer y conserva estado/cuerpo de error |
| Consumo del puerto HTTP y permisos de presentación | Equipo Reference Data MFE | Context por instancia; no almacena tokens ni sustituye autorización del backend |
| Firma/issuer/exp y autorización por endpoint | Equipo Reference Data Service | Es la autoridad de acceso al recurso; normalizar features para UI no amplía permisos |
| Migraciones y fixture de prueba | Equipos propietarios de cada DB, coordinados con Datos | Reference Data DB no modifica IAM; el fixture IAM solo opera la base aislada |
| CI, credenciales de dependencias y entorno aislado | Administradores/DevOps con responsables frontend | No traslada el token de CI a la sesión del usuario; no modifica el ambiente compartido |

## Acceso a dependencias privadas y custodia de CI

El workflow del MFE descarga frontend-platform y design-system privados. Requiere `SHELL_DEPS_TOKEN` como secreto de Actions, visible para ese repositorio, con lectura del contenido de esas dos dependencias. No precisa escritura en ellas. El token de CI no es el JWT de IAM ni debe llegar a las variables VITE, bundles, logs o artefactos de la aplicación.

Se propone que Administración/DevOps gestione el secreto, su alcance por repositorio, vencimiento/rotación y revocación; Frontend mantiene la declaración de dependencias y QA verifica el run sobre el HEAD. Arquitectura debe ratificar el mecanismo institucional de credencial y designar al custodio; no se impone aquí una cuenta personal ni se presume aprobación de un token existente.

Al corte, el MFE no tiene el secreto configurado. Configurarlo no acredita PASS: después deben aprobar checkout, npm ci, typecheck, lint, build, las 71 pruebas y JUnit. La existencia del mismo nombre de secreto en shell no lo comparte automáticamente con MFE.

## Runners: uso actual y decisión de permanencia pendiente

| Herramienta en docker-infra | Uso implementado | Decisión que falta ratificar |
|---|---|---|
| validation/hu-ref-020/run.ps1 y compose.yml | Preparación/verificación aislada IAM/Reference Data | Responsable de mantenimiento y alcance de soporte |
| validation/frontend-reference/run.ps1 | Flujo real con tres escenarios Chromium; invocado desde CI del shell | Si será gate oficial de integración y qué PR/cambios lo disparan |
| validation/r1-reference/run.ps1 | Prueba real de outbox/inbox/retry/DLQ/caos; invocada desde CI del shell | Frecuencia, recursos y responsable de diagnosticar fallos |

La propuesta es conservarlos como herramientas versionadas de validación y soporte de integración reproducible, ya usadas en CI; no declararlos por este ADR un despliegue productivo ni una política CI/CD transversal aprobada. El proyecto Compose aislado, credenciales locales generadas y no versionadas, y puertos loopback siguen siendo obligatorios para caos. El proveedor CI ejecuta los runners en secuencia y solo publica resúmenes saneados; nunca archivos .env, JWT, claves, HAR o trazas de sesión.

## Orden de integración propuesto

1. Revisar/aplicar Reference Data DB #81 e IAM DB #80 según el proceso de Datos; comprobar migraciones y el fixture en sus ámbitos correspondientes.
2. Integrar Frontend Platform #8 antes de sus consumidores y Reference Data Service #26 coordinado con su DB. No arrancar el consumidor R1 en un ambiente sin inbox/proyección.
3. Integrar MFE #13 tras su CI propio aprobado y el contrato de Frontend Platform; integrar Infra #44 con todas las fuentes/fixtures requeridos disponibles.
4. Resolver el conflicto actual del shell #17 y ejecutar su workflow completo sobre el nuevo HEAD; integrar el host cuando sus dependencias y evidencias estén listas.
5. Revisar las dos propuestas ADR y fusionar docs #340 hacia main; registrar evidencia y estado del board por responsables autorizados.

Hoy los workflows consumen varias ramas hu-ref-020-r1-dev en repositorios distintos. No borrarlas mientras dependan de ellas los jobs. Tras los merges, los responsables deben ajustar esas referencias a develop o revisiones aprobadas, y revalidar antes de retirar las ramas. Este documento propone el orden; no ejecuta merges ni modifica workflows.

## Trazabilidad de la revalidación y decisión pendiente

| Punto solicitado | Respuesta documental | Quién debe cerrar |
|---|---|---|
| Sesión, cliente compartido e integración IAM/Reference Data/shell | Tabla de responsabilidades y decisión 3/4/5 | Arquitectura ratifica límites |
| Estrategia de dependencias privadas frontend | Custodia y alcance de SHELL_DEPS_TOKEN, separado de JWT | Administración configura; QA revalida; Arquitectura ratifica mecanismo |
| Permanencia de runners | Uso actual separado de propuesta de soporte/gate oficial | Arquitectura y DevOps |
| Orden de integración y conflictos | Secuencia propuesta; evidencia por SHA; conflicto actual del shell explícito | Responsables de repositorios y QA |

Los puntos de gobernanza se registran como PA-REF-01, PA-REF-02 y PA-REF-06 en [preguntas abiertas](../../../15-project-control/open-questions.md).

No se cambia el estado PROPOSED. Antes de ACCEPTED, Arquitectura debe decidir estos puntos y registrar su revisión. El cierre técnico exige CI propio del MFE aprobado y CI completo del shell sobre cualquier HEAD posterior; el cierre de integración exige los merges autorizados.

## Evidencia verificada y límites de cierre — 2026-10-24

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

## Consecuencias

### Positivas

- Autenticación y autorización verificables desde la interfaz y por API negativa.
- Cambios de IAM, Reference Data, datos e infraestructura permanecen en sus repositorios responsables.
- Contexto por instancia evita mezclar clientes/sesiones entre montajes del remote y conserva ADR-009.
- La demostración de integración puede repetirse sin depender de un JDK incorrecto del host o secretos versionados.

### Negativas / Trade-offs

- Compilar Java y descargar imágenes requiere preparación previa; la primera ejecución puede exceder el tiempo de sustentación.
- La entrada de login local del shell es un punto de composición adicional, no un IAM MFE completo.
- El token tiene expiración real; sin renovación en esta entrega debe iniciarse sesión nuevamente al vencer.

### Riesgos

- Una prueba aislada no acredita automáticamente la integración en el entorno compartido: separar estados y conservar SHA/PR/evidencias.
- No colisionar con perfiles/puertos de compañeros; no detener contenedores ajenos ni cambiar variables globales del macroproyecto.
- Los permisos de la cuenta que publica y las revisiones de QA/Arquitectura son externos a la ejecución técnica; no simular aprobación ni cerrar issues anticipadamente.

## Alternativas consideradas

| Alternativa | Por qué se descarta |
|---|---|
| Sesión fija del BFF o token inventado | No valida IAM, firma ni permisos reales |
| Copiar toda la rama personal sobre develop | Puede borrar cambios recientes de compañeros y trasladar documentación fuera del SSOT |
| Getter de token mutable global dentro del remote | No respeta contexto por instancia ni la fachada de ADR-009 |
| Cambiar IAM dentro de Reference Data | Mezcla responsabilidades y oculta requisitos de esquema/usuarios |
| Exponer APIs como despliegue productivo paralelo | El edge canónico es Traefik, según ADR-007 |

## Referencias

- [ADR-005: topología](./ADR-005-microservices-topology-and-transversal-capabilities.md), [ADR-007: edge](./ADR-007-edge-gateway-and-port-convention.md), [ADR-009: frontend](./ADR-009-frontend-framework-and-build-strategy.md).
- [Historia y criterios](../../../04-requirements/user-stories.md), [trazabilidad](../../../04-requirements/traceability-matrix.md).
- [Plan de integración](../../../10-devops/reference-data-integration.md), [matriz de validación](../../../11-quality/reference-data-hu-ref-020-r1-validation.md).
- [DoD](../../../00-governance/definition-of-done.md), [docs-touchpoints](../../../00-governance/docs-touchpoints-matrix.md).
