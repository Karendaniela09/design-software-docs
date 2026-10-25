# Decisions — Reference Data Service

**Estado:** 🟢 Estable
**Fecha:** 2026-06-20

---

## Indice

| ID | Titulo | Estado |
|----|--------|--------|
| DEC-001 | Caching de catalogos con Redis TTL 24h en consumidores | 🟢 Estable |
| DEC-002 | Patron catalog/catalog_detail para catalogos dinamicos | 🟢 Estable |
| DEC-003 | training_shift y training_modality como ENUMs locales en academic-service | 🟢 Estable |
| DEC-004 | Jerarquia institucional como arbol simple sin closure table | 🟢 Estable |
| DEC-005 | Tabla parameter para valores de configuracion del sistema | 🟢 Estable |
| DEC-006 | Alcance GLOBAL exclusivo para los features REF_* | 🟢 Estable |

---

### DEC-001: Caching de catalogos con Redis TTL 24h en consumidores

**Decision:** Los catalogos gestionados por reference-data-service son cacheados por los servicios consumidores en sus instancias de Redis con un TTL de 24 horas. El propio reference-data-service no implementa cache interno.

**Contexto:** Los catalogos (tipos de documento, departamentos, municipios, niveles de formacion, etc.) son datos de baja volatilidad que son leidos frecuentemente por todos los servicios del sistema. Sin cache, cada validacion o lookup generaria una llamada de red al reference-data-service, creando un cuello de botella y una dependencia de disponibilidad critica.

**Alternativas consideradas:**
- **Cache en reference-data-service (cache centralizado):** Un cache en el proveedor reduciria la carga de base de datos pero no eliminaria las llamadas de red entre servicios. Cada request de cualquier consumidor seguiria llegando al reference-data-service.
- **Cache de larga duracion sin TTL (invalidacion manual):** Elimina latencia de expiracion pero requiere un mecanismo de invalidacion explicito (webhook, evento) ante cualquier cambio en catalogo. Compleja de operar correctamente.
- **Cache en consumidores con TTL corto (minutos):** Reduce el problema del dato desactualizado pero genera mayor trafico hacia reference-data-service y mayor latencia por cache misses frecuentes.
- **Cache en consumidores con TTL 24h (decision adoptada):** Los catalogos cambian raramente (tipicamente por deploys o mantenimientos programados). Un TTL de 24h es aceptable dado que los cambios en catalogo no son urgentes y pueden planificarse.

**Consecuencias:**
- Los servicios consumidores deben implementar su propia logica de cache y manejar el patron cache-aside al momento de inicializar.
- Un cambio en catalogo puede tardar hasta 24 horas en propagarse a todos los consumidores sin intervencion manual; esto es aceptable para el tipo de datos gestionados.
- En caso de cambio urgente, los administradores pueden invalidar el cache manualmente en cada servicio o reiniciar instancias.
- reference-data-service tiene baja carga en estado estable; los picos de carga ocurren al expirar el TTL de multiples consumidores de forma simultanea (thundering herd), lo cual debe considerarse en el dimensionamiento.

---

### DEC-002: Patron catalog/catalog_detail para catalogos dinamicos

**Decision:** Los catalogos del sistema se modelan con dos tablas: `catalog` (definicion del tipo de catalogo) y `catalog_detail` (valores individuales del catalogo). Esto permite gestionar catalogos dinamicos sin hardcodear ENUMs en el codigo de cada servicio.

**Contexto:** El sistema tiene multiples listas de valores controlados: tipos de documento de identidad, departamentos y municipios, programas de formacion, estados de ficha, entre otros. Sin un modelo centralizado, cada servicio definiria sus propios ENUMs o tablas de lookup independientes, generando inconsistencias y duplicacion de datos entre servicios.

**Alternativas consideradas:**
- **ENUMs hardcodeados en cada servicio:** Simple de implementar por servicio pero genera duplicacion masiva. Un cambio en los valores validos (nuevo tipo de documento, nuevo departamento) requiere modificar y redesplegar todos los servicios afectados de forma coordinada.
- **Una tabla plana por tipo de catalogo:** Cada catalogo es una tabla independiente (tabla `document_types`, tabla `departments`, etc.). Mas semanticamente explicito pero genera proliferacion de tablas, complejidad de migraciones y un API diferente para cada tipo de catalogo.
- **catalog + catalog_detail (decision adoptada):** Un modelo generico que puede albergar cualquier tipo de catalogo. Los valores son administrables en runtime por personal autorizado sin requirir deploy. El API de consulta es uniforme para todos los tipos de catalogo.

**Consecuencias:**
- El API de reference-data-service expone endpoints uniformes: `GET /catalogs/{catalog_code}/details` para cualquier tipo de catalogo.
- Agregar un nuevo tipo de catalogo es una operacion de datos (INSERT en `catalog` y sus `catalog_detail`), no un cambio de codigo.
- Los servicios consumidores deben referenciar los valores del catalogo por `catalog_detail_id` (integer FK) o por `code` (string estable), nunca por el texto del label que puede cambiar.
- La validacion de valores debe realizarse contra el catalogo en tiempo de escritura; los valores invalidos deben rechazarse con un error claro.

---

### DEC-003: training_shift y training_modality como ENUMs locales en academic-service

**Decision:** Los campos `training_shift` (jornada) y `training_modality` (modalidad de formacion) se implementan como ENUMs locales en academic-service en lugar de referencias a catalog_detail en reference-data-service.

**Contexto:** Durante la creacion de una ficha de formacion, el proceso debe ser completamente autonomo respecto a la disponibilidad de reference-data-service. Estos dos campos tienen un conjunto de valores que en la practica es estable, bien definido y directamente ligado a la logica de negocio de academic-service (afectan reglas de horarios, validaciones de instructores, etc.).

**Alternativas consideradas:**
- **training_shift y training_modality como catalog_detail (catalogo dinamico):** Centraliza la definicion en reference-data-service. Sin embargo, introduce una dependencia de sincronizacion critica: si reference-data-service no esta disponible o su cache ha expirado durante la creacion de una ficha, el proceso falla. Los valores de estos campos ademas son referenciados en logica de negocio compleja dentro de academic-service, lo cual hace que los ENUMs sean parte del modelo del dominio, no solo etiquetas de UI.
- **ENUMs locales en academic-service (decision adoptada):** Mantiene la autonomia del servicio para operaciones criticas de escritura. Los valores son parte del contrato del dominio de academic-service y no deben poder modificarse en runtime sin revision de impacto en logica de negocio.

**Consecuencias:**
- academic-service puede crear fichas de forma completamente autonoma, sin depender de reference-data-service en tiempo de escritura.
- Un cambio en los valores validos de jornada o modalidad requiere un cambio de codigo y deploy de academic-service; esto es aceptable dado que tales cambios implican revision de logica de negocio.
- Los ENUMs locales deben estar documentados en el contrato del servicio para que otros servicios que consuman fichas entiendan los valores posibles.
- Esta decision crea una excepcion explicita al patron general de catalog_detail; debe documentarse para evitar que futuros desarrolladores migren estos campos al catalogo dinamico sin entender el motivo.

---

### DEC-004: Jerarquia institucional como arbol simple sin closure table

**Decision:** La jerarquia de la estructura institucional (macroregion → regional → centro de formacion → sede, con profundidad maxima de 6 niveles) se modela como un arbol simple con referencia al nodo padre (`parent_id`), sin implementar closure table ni nested sets.

**Contexto:** La estructura institucional del sistema tiene una jerarquia geografica/organizacional de hasta 6 niveles de profundidad. Las consultas tipicas son: obtener los hijos directos de un nodo, navegar del nodo hoja hasta la raiz, y obtener todos los descendientes de un nodo para filtrar datos por region.

**Alternativas consideradas:**
- **Closure table:** Almacena todas las relaciones ancestro-descendiente de forma explicita, permitiendo consultas de subarboles en O(1). Tiene overhead de almacenamiento (O(n*d) filas donde d es la profundidad) y complejidad de mantenimiento en inserts/deletes. Justificado cuando la profundidad es variable e ilimitada o cuando hay consultas frecuentes de subarboles completos.
- **Nested sets (Celko's model):** Excelente para lecturas de subarboles pero extremadamente costoso para inserts y updates (requiere recalcular left/right de todos los nodos afectados). Descartado por la frecuencia esperada de cambios en la estructura institucional.
- **Arbol simple con parent_id (decision adoptada):** Modelo mas simple y directo. Con profundidad maxima de 6 niveles, las consultas recursivas (CTE en PostgreSQL) son eficientes y el numero de joins necesarios es acotado y predecible.

**Consecuencias:**
- Las consultas de subarboles completos utilizan CTEs recursivos en PostgreSQL (`WITH RECURSIVE`), disponibles de forma nativa y con buen rendimiento para profundidades menores a 10 niveles.
- El rendimiento es aceptable dado que la jerarquia tiene profundidad maxima conocida y acotada (6 niveles) y el volumen de nodos es bajo (cientos, no millones).
- Si en el futuro la profundidad aumenta significativamente o el volumen de nodos crece ordenes de magnitud, la migracion a closure table debe reconsiderarse.
- Los cambios en la estructura (mover un nodo de subregion, renombrar un centro) son operaciones simples de UPDATE sobre el `parent_id`.

---

### DEC-005: Tabla parameter para valores de configuracion del sistema

**Decision:** Los valores de configuracion del sistema (limites, parametros operacionales, constantes de negocio ajustables) se almacenan en una tabla `parameter` en reference-data-service en lugar de variables de entorno o archivos de configuracion.

**Contexto:** El sistema tiene valores de configuracion que deben poder ajustarse en produccion sin requerir un redespliegue (numero maximo de aprendices por ficha, porcentaje minimo de asistencia, periodos de vigencia, etc.). Las variables de entorno requieren reinicio del servicio para aplicarse y no son auditables ni versionables de forma sencilla.

**Alternativas consideradas:**
- **Variables de entorno:** Estandar para configuracion de aplicaciones en arquitecturas cloud-native (12-factor app). Sin embargo, los cambios requieren reinicio del servicio y no tienen historial de cambios visible. Adecuados para configuracion de infraestructura (conexiones, credenciales) pero no para parametros de negocio que cambian en runtime.
- **Archivos de configuracion (config.yaml, .env):** Similar a variables de entorno en cuanto a la necesidad de reinicio. Ademas, en arquitecturas de microservicios con multiples instancias, sincronizar archivos de configuracion entre instancias es complejo.
- **Feature flags service externo:** Solucion completa para configuracion dinamica y A/B testing. Sobre-ingenieria para el volumen y complejidad de parametros del sistema actual.
- **Tabla parameter (decision adoptada):** Permite modificar valores de configuracion de negocio en runtime mediante operaciones administrativas. Los cambios son auditables (timestamp, usuario que modifico). Los servicios consumidores leen los parametros al iniciar o los cachean con TTL corto.

**Consecuencias:**
- Los parametros de negocio pueden ajustarse por administradores del sistema sin intervenir en el proceso de despliegue.
- Los cambios en parametros son auditables: se puede saber quien cambio que valor y cuando.
- Los servicios consumidores deben definir una estrategia de lectura: leer al iniciar (requiere reinicio para actualizar) o cachear con TTL corto (permite actualizacion sin reinicio pero con latencia).
- La tabla `parameter` debe distinguirse claramente de la configuracion de infraestructura (conexiones, credenciales) que debe seguir en variables de entorno por razones de seguridad.
- Los parametros con impacto critico en logica de negocio deben tener validaciones de rango/tipo para prevenir valores incorrectos ingresados por error administrativo.

---

### DEC-006: Alcance GLOBAL exclusivo para los features REF_*

**Decision:** Los seis features del modulo `MOD_REFERENCE` (`REF_HIERARCHY_VIEW`/`MANAGE`, `REF_CATALOG_VIEW`/`MANAGE`, `REF_PARAMETER_VIEW`/`MANAGE`) se exigen unicamente con alcance `GLOBAL`. Un grant del mismo feature con un alcance mas estrecho (`TRAINING_CENTER`, `AREA`, de propiedad) o sin alcance se rechaza con `403` y nunca se ensancha a global. Cuando no se pueden obtener las claves JWKS de IAM, las operaciones protegidas responden `503 DEPENDENCY_UNAVAILABLE`.

**Contexto:** La matriz RBAC de IAM ([rbac-design.md](../01-iam-service/rbac-design.md), `MOD_REFERENCE`) concede los seis features solo con `GLOBAL`, y los seeds de `iam-db` lo respetan. El middleware aceptaba cualquier alcance conocido para el codigo exacto del feature, de modo que un grant de centro operaba como global. La HU-INT-REF-001 ([docs#294](https://github.com/code-sena/design-software-docs/issues/294)) cerro esa brecha. Ninguna operacion de referencia esta definida por centro, asi que no hay un filtro de datos que aplicar.

**Alternativas consideradas:**
- **Filtrar por centro con `training_center_id` del token:** descartada. Exige un contrato y un filtrado de datos que hoy no existen, y los datos de referencia (jerarquia, catalogos, parametros) son compartidos por todos los centros.
- **Ignorar el alcance (comportamiento anterior):** descartada. Convierte un permiso restringido en global.
- **Rechazar todo alcance distinto de GLOBAL (decision adoptada):** falla cerrado y coincide con la matriz de IAM.

**Consecuencias:**
- La presentacion aplica la misma regla. `/auth/me` entrega codigos sin alcance; `@sena/frontend-platform` los cruza con los grants `CODE:SCOPE_TYPE` del JWT en memoria y solo `REF_*:GLOBAL` se vuelve permiso de navegacion para el remote. Esa lectura del JWT solo decide que se muestra: la firma RS256, el emisor, la expiracion y el alcance los verifica el backend en cada operacion.
- Si un rol futuro necesita datos de referencia por centro, primero hacen falta un contrato y una decision nuevos; solo despues se pueden conceder alcances estrechos en IAM.
- El contrato (`reference-data.yaml`) declara `x-reference-scope: GLOBAL` y la respuesta `503` en las operaciones protegidas. Guia de integracion: [reference-data-int-ref-001.md](../../../10-devops/reference-data-int-ref-001.md).
