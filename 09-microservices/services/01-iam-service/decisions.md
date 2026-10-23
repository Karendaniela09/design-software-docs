# Decisions — IAM Service

**Estado:** 🟢 Estable
**Fecha:** 2026-06-20

---

## Indice

| ID | Titulo | Estado |
|----|--------|--------|
| DEC-001 | JWT stateless para autenticacion | 🟢 Estable |
| DEC-002 | Bcrypt con cost factor 12 para hashing de contrasenas | 🟢 Estable |
| DEC-003 | Refresh token almacenado como hash SHA-256 | 🟢 Estable |
| DEC-004 | Modelo RBAC role→feature→scope | 🟢 Estable |
| DEC-005 | Campo actor_id polimorfico sin FK entre servicios | 🟢 Estable |
| DEC-006 | Tabla audit_login local sin publicacion al audit-service | 🟢 Estable |
| DEC-007 | Separacion de first_name y last_name en lugar de full_name | 🟢 Estable |
| DEC-008 | Distribucion de clave publica via JWKS, sin secreto compartido | 🟢 Estable |

---

### DEC-001: JWT stateless para autenticacion

**Decision:** Se utiliza JWT (JSON Web Token) stateless para la autenticacion de usuarios en lugar de sesiones basadas en servidor.

**Contexto:** El sistema de microservicios requiere un mecanismo de autenticacion que pueda escalar horizontalmente sin coordinacion entre instancias. Multiples servicios necesitan verificar identidades de forma independiente sin consultar un estado centralizado en cada peticion. Las features del usuario (roles, scopes) se pre-calculan al momento del login y se embeben en el payload del JWT para evitar llamadas adicionales a IAM por cada request downstream.

**Alternativas consideradas:**
- **Sesiones en servidor con Redis centralizado:** Requieren almacenamiento compartido entre instancias. Introduce dependencia de estado y latencia adicional en cada verificacion. Apropiado para monolitos pero introduce acoplamiento innecesario en microservicios.
- **Opaque tokens con introspection endpoint:** Cada servicio deberia llamar al IAM para validar el token en cada peticion. Crea un cuello de botella y punto unico de fallo critico; si IAM esta caido, ninguna peticion puede autenticarse.

**Consecuencias:**
- Los tokens son autoverificables: cualquier servicio puede validar la firma sin contactar al IAM en cada peticion.
- El access token debe tener expiracion corta (recomendado 15 min) para limitar la ventana de exposicion ante compromisos de token.
- La revocacion inmediata de access tokens activos no es posible sin una lista de revocacion (blacklist), lo cual se acepta como trade-off conocido para evitar estado centralizado.
- El JWT se re-emite al usar el refresh token; si los roles del usuario cambian, el cambio efectivo tarda hasta la proxima emision de token.
- Los refresh tokens gestionan la renovacion de sesion de forma segura sin reautenticacion constante del usuario.

---

### DEC-002: Bcrypt con cost factor 12 para hashing de contrasenas

**Decision:** Las contrasenas de usuarios se hashean utilizando bcrypt con un cost factor de 12.

**Contexto:** El almacenamiento de contrasenas requiere un algoritmo disenado especificamente para ser computacionalmente costoso y resistente a ataques de fuerza bruta con hardware moderno (GPU, ASIC). El cost factor debe balancear seguridad contra latencia aceptable en operaciones de login.

**Alternativas consideradas:**
- **MD5 / SHA-256 simples:** Algoritmos de proposito general, no disenados para contrasenas. Extremadamente rapidos para ataques en GPU. Descartados por ser inseguros para este caso.
- **Cost factor 10 (default bcrypt):** Mas rapido pero ofrece menor resistencia con hardware moderno. Acceptable para sistemas de baja sensibilidad, insuficiente para un sistema IAM.
- **Cost factor 14+:** Aumenta la seguridad pero incrementa la latencia de login a niveles que degradan la experiencia de usuario (>1 segundo por verificacion en hardware promedio de servidor).
- **Argon2id:** Alternativa moderna y recomendada por OWASP, con mejor resistencia a ataques en GPU. Se descarto por menor madurez en el ecosistema de librerias disponibles en el stack Node/Python del proyecto y la necesidad de estandarizar con dependencias existentes.

**Consecuencias:**
- El cost factor 12 proporciona aproximadamente 250-400ms por operacion de hash en hardware de servidor tipico, aceptable para login interactivo pero costoso para ataques masivos.
- El cost factor esta embebido en el hash almacenado, lo que permite ajustarlo en el futuro sin migrar contrasenas existentes (las cuentas existentes re-hashean al siguiente login exitoso).
- Las operaciones de autenticacion masiva (bulk import, seed de datos de prueba) deben tener en cuenta el tiempo de procesamiento por volumen.

---

### DEC-003: Refresh token almacenado como hash SHA-256

**Decision:** Los refresh tokens se almacenan en la base de datos como su digest SHA-256 en lugar del valor en texto plano.

**Contexto:** Los refresh tokens son credenciales de larga duracion (dias o semanas) que permiten obtener nuevos access tokens. Si la base de datos es comprometida, los refresh tokens expuestos en texto plano permitirian a un atacante suplantar sesiones activas de todos los usuarios sin conocer sus contrasenas.

**Alternativas consideradas:**
- **Texto plano:** Simple de implementar pero expone todas las sesiones activas ante cualquier dump de base de datos. Riesgo inaceptable para credenciales de larga duracion.
- **Cifrado simetrico (AES):** Reversible por diseno, lo cual no aporta ventaja de seguridad real sobre texto plano si la clave de cifrado se compromete junto con la base de datos en el mismo entorno.
- **Bcrypt para refresh tokens:** Excesivamente costoso computacionalmente para tokens que no tienen valor semantico humano. SHA-256 es suficiente porque los refresh tokens son cadenas aleatorias de alta entropia (no derivadas de palabras del diccionario), lo que hace que la inversion del hash sea computacionalmente inviable en tiempo util.

**Consecuencias:**
- El valor del token enviado al cliente nunca puede recuperarse desde la base de datos; solo puede verificarse.
- La validacion consiste en hashear el token recibido y comparar con el hash almacenado en tiempo constante.
- Ante un compromiso de base de datos, los hashes SHA-256 de tokens aleatorios de alta entropia no son reversibles en tiempo util.
- La rotacion de refresh tokens (invalidar el anterior al emitir uno nuevo) sigue siendo posible y se recomienda como practica defensiva.

---

### DEC-004: Modelo RBAC role→feature→scope

**Decision:** El modelo de control de acceso basado en roles (RBAC) sigue la jerarquia role→feature→scope en lugar de un modelo simple role→permission o resource+action plano.

**Contexto:** El sistema maneja multiples funcionalidades (fichas, horarios, documentos, reportes) con operaciones granulares por funcionalidad. Un modelo plano de role→permission generaria una explosion combinatoria de permisos dificil de administrar a medida que el sistema crece y se agregan modulos.

**Alternativas consideradas:**
- **Role→permission (RBAC simple plano):** Lista plana de permisos por rol. Facil de implementar inicialmente pero se vuelve inmanejable con docenas de funcionalidades y operaciones. La asignacion de permisos ad-hoc es propensa a errores administrativos.
- **Resource+Action plano:** Similar al anterior. Permite granularidad pero pierde el agrupamiento logico por modulo/vista, dificultando la administracion y auditoria.
- **ABAC (Attribute-Based Access Control):** Modelo muy flexible basado en atributos del sujeto, objeto y entorno. Demasiado complejo para los requisitos actuales; introduce overhead significativo en evaluacion de politicas y en la herramienta de administracion.
- **Role→feature→scope:** Agrupa los permisos por funcionalidad del sistema (feature) y tipo de operacion (scope: read, write, delete, admin). Permite administrar el acceso a nivel de funcionalidad completa o a nivel de operacion especifica dentro de ella.

**Consecuencias:**
- El JWT incluye la estructura de features y scopes por rol, permitiendo a los servicios consumidores evaluar permisos sin consultar IAM en cada peticion.
- Los modulos y features son datos de solo lectura en runtime; cambios en el catalogo de features requieren un deploy, no una operacion administrativa, para evitar que un admin rompa accidentalmente la arquitectura del sistema.
- Agregar nuevas funcionalidades al sistema solo requiere definir la feature y sus scopes validos; los roles existentes pueden extenderse sin rediseno del modelo.
- Los guards en los servicios verifican pares (feature, scope) recibidos en el JWT, manteniendo un contrato claro y verificable.

---

### DEC-005: Campo actor_id polimorfico sin FK entre servicios

**Decision:** El campo `actor_id` en la entidad `user` es un identificador polimorfico que referencia entidades en otros servicios (instructor, coordinador, aprendiz, etc.) sin una clave foranea de base de datos entre servicios.

**Contexto:** Un usuario del sistema IAM puede corresponder a distintos tipos de actores definidos en otros microservicios. En una arquitectura de microservicios, cada servicio es propietario exclusivo de su base de datos; la integridad referencial entre bases de datos de distintos servicios no puede ni debe garantizarse mediante FK a nivel de motor de base de datos.

**Alternativas consideradas:**
- **FK directa a tabla compartida:** Requeriria una base de datos compartida o esquema compartido, rompiendo el principio de autonomia de datos por servicio. Introduce acoplamiento estructural inaceptable que impide el despliegue independiente.
- **Tabla de mapeo centralizada en IAM:** IAM almacenaria copias de los IDs de actores de otros servicios. Crea responsabilidad de datos que no pertenece al dominio de IAM y genera dependencias de sincronizacion.
- **actor_id + actor_type polimorficos (decision adoptada):** IAM almacena el ID y el tipo del actor. La consistencia se garantiza a nivel de aplicacion: el evento `iam.user.created` es consumido por actors-service para crear el perfil del actor correspondiente.

**Consecuencias:**
- La consistencia entre `user.actor_id` y la existencia real del actor en el servicio correspondiente se mantiene mediante logica de aplicacion y eventos de dominio, no por FK de base de datos.
- No existe validacion automatica de integridad referencial en la capa de persistencia; las inconsistencias deben detectarse en pruebas de integracion.
- La arquitectura mantiene la autonomia de despliegue: IAM puede operar aunque actors-service este temporalmente caido.
- Las consultas que requieren datos del actor deben realizarse mediante llamadas al servicio correspondiente o mediante datos desnormalizados incluidos en el JWT.

---

### DEC-006: Tabla audit_login local sin publicacion al audit-service

**Decision:** Los eventos de autenticacion (intentos exitosos y fallidos) se registran en una tabla `audit_login` local dentro de `iam_db` y no se publican como eventos al audit-service centralizado ni al broker de mensajes.

**Contexto:** El proceso de autenticacion maneja datos altamente sensibles: credenciales intentadas, IPs de origen, user agents, patrones de acceso fallido. Publicar estos eventos a un bus de mensajes o al audit-service implicaria transmitir informacion sensible fuera del perimetro controlado de IAM, con riesgo de exposicion a consumidores no autorizados.

**Alternativas consideradas:**
- **Publicar eventos al audit-service via broker:** Centraliza todos los logs de auditoria del sistema pero los eventos de autenticacion contendrian informacion sensible que no debe circular por el bus de eventos. Ademas, si el broker esta caido en el momento de un intento de autenticacion, el evento se perderia, creando gaps en el log de seguridad.
- **Publicar eventos sanitizados (sin credenciales):** Reduce el riesgo pero la fragmentacion entre el log local detallado y el bus complica la correlacion de incidentes de seguridad. La informacion minima util para auditoria de seguridad sigue siendo sensible (IP, patron de intentos fallidos).
- **audit_login local (decision adoptada):** Mantiene los datos de autenticacion dentro del perimetro de IAM. El registro es sincrono con la operacion de autenticacion, garantizando que nunca se pierde un evento por fallo del broker.

**Consecuencias:**
- Los datos de autenticacion nunca salen del servicio IAM, reduciendo la superficie de exposicion de informacion sensible.
- El audit-service no tiene visibilidad de eventos de autenticacion; esto es intencional y aceptado como parte del diseno de seguridad.
- Las consultas de auditoria de seguridad (deteccion de fuerza bruta, analisis de accesos sospechosos, reportes de sesiones) se realizan directamente consultando el IAM service.
- La tabla `audit_login` requiere politica de retencion y archivado definida para controlar el crecimiento del volumen de datos a largo plazo.

---

### DEC-007: Separacion de first_name y last_name en lugar de full_name

**Decision:** El nombre del usuario se almacena en dos campos separados `first_name` y `last_name` en lugar de un unico campo `full_name`.

**Contexto:** El sistema necesita presentar nombres de usuario en diferentes formatos segun el contexto: nombre completo en reportes formales, solo nombre de pila en interfaces conversacionales, apellido primero en listas ordenadas, iniciales en avatares generados automaticamente. Un campo unico `full_name` no permite estos usos sin logica de parsing fragil y dependiente del idioma.

**Alternativas consideradas:**
- **full_name unico:** Simple de capturar en formularios pero impide ordenamiento por apellido, generacion de iniciales confiable, y formatos de saludo personalizados. El parsing de "Juan Carlos Lopez Mendez" para extraer nombre vs apellido es ambiguo y culturalmente dependiente.
- **Estructura completa (first_name, middle_name, last_name, second_last_name):** Mas precisa para nombres hispanos compuestos. Se descarto por complejidad adicional en formularios y porque los casos de uso identificados no requieren ese nivel de granularidad en la version actual.
- **first_name + last_name (decision adoptada):** Separacion minima que cubre todos los casos de uso identificados: ordenamiento por apellido, saludos personalizados por nombre, generacion de iniciales, formatos de visualizacion flexibles.

**Consecuencias:**
- Los formularios de registro deben capturar nombre y apellido en campos separados; no se acepta campo unico con split automatico.
- La capa de presentacion construye el nombre completo concatenando ambos campos segun el formato requerido por el contexto.
- Nombres de una sola palabra o nombres culturalmente distintos pueden requerir manejo especial en `last_name`; se acepta como caso borde menor en el contexto del sistema.
- El ordenamiento en consultas SQL puede usar `ORDER BY last_name, first_name` directamente sin logica adicional de aplicacion.

---

### DEC-008: Distribucion de clave publica via JWKS, sin secreto compartido

**Decision:** La clave publica RSA usada para verificar localmente los access token (RS256) se
distribuye a traves de un endpoint JWKS estandar (`GET /api/v1/auth/.well-known/jwks.json`,
RFC 7517), publicado por el propio iam-service y sin autenticacion. La rotacion se soporta
publicando dos entradas simultaneas (clave actual + clave saliente, cada una con su `kid`
propio) durante la ventana de transicion, en vez de gestionar un secreto compartido fuera de
banda.

**Contexto:** DEC-001 establece que el edge y los servicios downstream verifican el JWT
localmente sin llamar a IAM en cada peticion (ver [authentication.md](../../../07-api/authentication.md)).
Eso requiere que la clave publica de verificacion llegue a cada verificador (Traefik en el
edge, ADR-007, y cada `-api` de dominio) de forma que (a) no dependa de coordinacion manual de
despliegue entre servicios y (b) permita rotar la clave de firma sin downtime ni caida masiva
de tokens validos.

**Alternativas consideradas:**
- **Secreto compartido gestionado por configuracion (la misma clave publica como variable de
  entorno en cada servicio consumidor):** Funciona, pero cada rotacion exige actualizar y
  redesplegar N servicios en el orden correcto (o coordinar una ventana de doble clave a mano
  vía config), y el secreto vive duplicado en tantos lugares como consumidores. Descartado
  como mecanismo primario porque reintroduce el problema de coordinacion entre despliegues
  independientes que DEC-001 buscaba evitar; es aceptable solo como *fallback* cuando un
  consumidor no puede resolver HTTP hacia iam en tiempo de arranque (ver Consecuencias).
- **mTLS entre iam y cada consumidor para servir la clave punto a punto:** Anade una PKI
  operativa completa (certificados por servicio, rotacion de los certificados mismos) para un
  problema que JWKS ya resuelve como estandar sin infraestructura adicional. Sobre-ingenieria
  para el tamano actual del sistema.
- **JWKS estandar, sin autenticacion, con soporte de `kid` para rotacion (decision adoptada):**
  Cada verificador simplemente hace `GET` al endpoint (con cache local por TTL) y resuelve la
  clave por `kid` del header del token. Es el mecanismo que las librerias JWT de todos los
  stacks del sistema (ADR-006, polyglot) ya soportan de fabrica, sin codigo custom de
  distribucion de secretos.

**Consecuencias:**
- El endpoint JWKS es publico (sin `Authorization`): un verificador no puede depender de un
  token valido para obtener la clave con la que validarlo. No expone informacion sensible: solo
  la mitad publica de la clave de firma.
- La rotacion es: generar el par nuevo, desplegar iam-service con `IAM_JWT_PRIVATE_KEY`/`IAM_JWT_KEY_ID`
  nuevos y `IAM_JWT_PREVIOUS_PUBLIC_KEY`/`IAM_JWT_PREVIOUS_KEY_ID` apuntando al par saliente;
  ambas claves quedan publicadas en JWKS durante la ventana de transicion. Pasado el TTL del
  access token (15 min) desde el corte, se retira la clave saliente de la configuracion. No
  requiere redespliegue de los servicios consumidores.
- Cadencia de rotacion: trimestral (ver tabla de configuracion de seguridad en
  [authentication.md](../../../07-api/authentication.md)), o inmediata ante sospecha de
  compromiso de la clave privada.
- Cada verificador debe cachear el JWKS (por `kid`) en vez de resolverlo en cada request, para
  no convertir el endpoint en un punto de fallo sincrono equivalente a llamar a IAM por
  peticion — el mismo problema que DEC-001 evita para la verificacion del token en si.
- Si un consumidor no puede alcanzar el endpoint HTTP de iam en su entorno (p. ej. una rotacion
  de infraestructura donde el descubrimiento de servicios aun no esta disponible), el secreto
  compartido por configuracion sigue disponible como mecanismo de respaldo manual, gestionado
  por config (no hardcodeado), documentado pero no es el camino primario.

---

## Seguridad IAM R4: decisión arquitectónica propuesta

- [ADR-018: Validación del estado de sesión al obtener el usuario actual](../../../05-architecture/decisions/records/ADR-018-iam-session-revocation-r4.md) — **PROPOSED**.
- Alcance: rutas de IAM que invocan `GetCurrentUser`; la revocación inmediata en servicios que verifican JWT/JWKS sin consultar IAM sigue sin demostrarse.
