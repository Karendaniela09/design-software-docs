# ADR-018: Validación del estado de sesión al obtener el usuario actual en IAM

**Estado:** PROPOSED
**Fecha:** 2026-10-20
**Autora:** Natalia Chala Chala
**Equipos relacionados:** Backend IAM, Arquitectura y QA (revisión pendiente)
**Alcance:** `design-software-iam-service` — mejora de seguridad R4

> **Numeración:** ADR-018 continúa la secuencia vigente del índice institucional después de ADR-017.

---

## Contexto

El microservicio IAM emite tokens de acceso JWT firmados con RSA y administra registros persistidos de sesiones y tokens de actualización. Las decisiones existentes del módulo, en particular DEC-001 (JWT sin estado), DEC-003 (almacenamiento de hashes de tokens de actualización), DEC-004 (RBAC) y DEC-008 (JWKS), establecen el contexto de autenticación y autorización.

La validez criptográfica y temporal de un JWT no demuestra, por sí sola, que la sesión del usuario siga activa. Si una ruta IAM comprueba únicamente la firma y la expiración del JWT, podría aceptar un token después del cierre de sesión o de su revocación. Por ello, al resolver el usuario autenticado dentro de IAM, debe relacionarse el identificador de sesión `sid` del token con el registro persistido y su estado vigente.

La mejora local R4 refuerza el caso de uso `GetCurrentUser`. No convierte todos los JWT en tokens de referencia ni demuestra revocación inmediata en los microservicios que verifican JWT de forma independiente mediante JWKS.

El requisito relacionado es **OWASP ASVS 5.0.0, v5.0.0-7.4.1**, sobre terminación de sesiones. Su cobertura se considera **parcial**, ya que todavía faltan verificaciones de integración en la rama institucional actual y del comportamiento de los consumidores externos.

## Decisión

Se decide exigir **un token de acceso válido y una sesión persistida válida** antes de devolver la identidad autenticada en las operaciones IAM que utilizan `GetCurrentUser`.

El caso de uso deberá aplicar las siguientes comprobaciones en el backend de confianza:

1. Verificar el token de acceso con el verificador configurado; rechazar tokens inválidos, malformados, expirados o no admitidos.
2. Obtener la identidad de usuario y el identificador de sesión `sid` a partir de las afirmaciones verificadas del token.
3. Comprobar que exista una sesión persistida correspondiente a ese identificador.
4. Comprobar que la sesión pertenezca al usuario identificado por el token verificado.
5. Rechazar sesiones revocadas o vencidas en el instante de la validación.
6. Comprobar que la cuenta de usuario asociada continúe activa.
7. Solo después de estas comprobaciones, devolver la identidad y el contexto de acceso a la operación IAM que los solicita.

La implementación reutiliza la abstracción de sesiones `RefreshTokenRepository` y un `Clock` inyectado; sus dependencias se configuran mediante `UseCaseConfiguration`. Un estado de sesión inválido constituye un fallo de autenticación, no una resolución exitosa de identidad.

**Límite de la decisión:** esta comprobación protege las rutas IAM que efectivamente invocan `GetCurrentUser`. No debe presentarse como revocación automática de todas las rutas IAM ni de todos los microservicios consumidores de JWT sin verificar sus flujos específicos.

### Compatibilidad con decisiones IAM existentes

- **DEC-001 — JWT sin estado:** se conservan el formato JWT, la firma y la verificación criptográfica independiente. R4 agrega una comprobación de estado al resolver el usuario actual dentro de IAM, sin reemplazar la arquitectura general de validación local de JWT.
- **DEC-003 — Hash de tokens de actualización:** el registro persistido permite consultar revocación y expiración. Esta mejora no exige almacenar ni exponer el valor original de los tokens de actualización.
- **DEC-004 — RBAC:** autenticar a una persona no implica autorizar una operación. Los permisos por funcionalidad y alcance, la propiedad del recurso, las excepciones administrativas y las restricciones frente a IDOR requieren comprobaciones independientes.
- **DEC-008 — JWKS:** los consumidores externos pueden continuar validando firmas mediante claves públicas. La publicación de JWKS, por sí sola, no informa que una sesión fue revocada.

Si se acepta esta decisión, deberá aclararse el alcance de la afirmación de DEC-001 sobre la imposibilidad de revocación inmediata de tokens de acceso: **las rutas IAM que consultan el estado persistido pueden rechazar sesiones revocadas; los consumidores que validan JWT sin consultar ese estado podrían aceptar un token vigente hasta su expiración o hasta implementar un mecanismo adicional**.

## Límites de seguridad y comportamiento esperado

| Escenario | Comportamiento esperado al consultar el usuario actual en IAM | Evidencia |
|---|---|---|
| JWT válido, sesión activa y vigente, propietario coincidente y usuario activo | Se puede devolver la identidad autenticada | Pruebas unitarias locales aprobadas |
| No existe la sesión correspondiente al `sid` | Se rechaza la autenticación | Prueba local aprobada |
| Sesión revocada | Se rechaza la autenticación | Prueba local aprobada |
| Sesión persistida expirada | Se rechaza la autenticación | Prueba local aprobada |
| Sesión perteneciente a otro usuario | Se rechaza la autenticación | Prueba local aprobada |
| JWT con firma inválida, expirado, sin firma o con contenido alterado | Se rechaza en la frontera de verificación JWT | Pruebas unitarias JWT pertinentes aprobadas |
| Reutilización de token después de cierre de sesión real con PostgreSQL | Se debe rechazar en las rutas IAM protegidas | **Pendiente de repetir en la rama institucional actual** |
| JWT de sesión revocada presentado a un servicio externo que valida JWKS sin consultar IAM | Requiere una política adicional de revocación | **No demostrado por esta decisión** |

## Consecuencias

### Positivas

- Impide que `GetCurrentUser` resuelva correctamente identidades asociadas a sesiones inexistentes, revocadas, vencidas o pertenecientes a otro usuario.
- Se alinea con la intención de ASVS v5.0.0-7.4.1 en las rutas IAM cubiertas, sin declarar cumplimiento global del requisito.
- Conserva el esquema de firmas JWT, la publicación JWKS y el almacenamiento de hashes de tokens de actualización.
- Utiliza las abstracciones existentes y un reloj inyectado para facilitar pruebas deterministas.

### Negativas y compromisos

- Agrega una consulta de persistencia al resolver el usuario actual en las rutas afectadas. La latencia y la disponibilidad de la base de datos pasan a influir en este flujo.
- Ante una falla de persistencia, la ruta protegida debe denegar el acceso; no debe regresar silenciosamente a validar solo la firma.
- Los servicios externos pueden seguir validando JWT de manera independiente, pero esa validación no ofrece necesariamente la misma garantía de revocación.

### Riesgos residuales y puntos pendientes

1. **Revocación en servicios consumidores:** los microservicios que solo verifican firmas mediante JWT/JWKS podrían aceptar tokens todavía vigentes cuya sesión IAM haya sido revocada. Es necesario definir una estrategia transversal: expiraciones cortas, introspección, avisos de revocación u otro mecanismo.
2. **Cobertura de rutas IAM:** auditar los controladores y filtros para determinar qué operaciones utilizan `GetCurrentUser` y cuáles requieren controles equivalentes.
3. **Pruebas con PostgreSQL:** repetir `SessionPostgresIT` y el flujo inicio de sesión → `/auth/me` → cierre de sesión → reutilización de `/auth/me`, junto con las regresiones de renovación, en una instancia PostgreSQL aislada y sobre la rama institucional actual.
4. **Credenciales de máquina a máquina:** verificar si estos tokens usan ciclos de vida, identificadores y mecanismos de revocación distintos a las sesiones de usuario.
5. **Autorización:** comprobar por separado la protección frente al acceso cruzado a sesiones, elusión de excepciones de alcance RBAC y escenarios IDOR.
6. **Controles operativos:** medir el costo de las consultas adicionales y comprobar el comportamiento ante fallas de BD; revisar TLS, secretos, rotación de claves y auditoría dentro de sus requisitos correspondientes.
7. **Integración continua:** la ejecución automatizada de pruebas de seguridad en GitHub Actions permanece **aplazada**. No se declara ninguna verificación de CI remoto.

## Alternativas consideradas

| Alternativa | Evaluación |
|---|---|
| Validar únicamente firma y expiración del JWT | Mantiene la autenticación completamente sin estado, pero no impide la reutilización inmediata de un token contra la ruta IAM protegida tras revocar su sesión. No seleccionada para este flujo. |
| Mantener una lista de JWT denegados | Permite bloquear tokens individuales, pero introduce un nuevo ciclo de vida de estado, persistencia, limpieza y consistencia de caché. No se incorpora en este ajuste R4. |
| Sustituir todos los tokens de acceso por tokens opacos con introspección centralizada | Ofrece un punto común para consultar revocaciones, a costa de mayor acoplamiento, carga y dependencia de disponibilidad entre servicios. Fuera del alcance actual. |
| Consultar la sesión persistida desde `GetCurrentUser` | Reutiliza el modelo existente, limita el cambio de código y admite pruebas negativas locales. **Alternativa seleccionada** para las rutas IAM afectadas. |

## Validación y evidencias

**Verificado localmente** en la rama institucional `feat/r4-security-improvements`, commit `b5dd5af271`:

- Ejecución completa de pruebas unitarias Maven: **180 aprobadas**, **0 fallidas**, **0 errores** y **0 omitidas**. No se presentan como 180 pruebas de seguridad.
- **20 casos negativos de seguridad revisados y aprobados**, incluidos dentro del total de 180 pruebas, relativos a JWT, autenticación, sesiones y rutas de autorización seleccionadas.
- `GetCurrentUserTest`: **8 de 8 pruebas aprobadas**, incluidos los casos de sesión inexistente, revocada, expirada o con propietario incorrecto.
- Dos pruebas adicionales de regresión JWT comprueban el rechazo de tokens sin firma (`alg: none`) y de contenido alterado.
- Documentación y evidencias locales, todavía no publicadas en este repositorio: `IAM-R4-SECURITY-DOCS/02-checklist-owasp-asvs-l1.md`, `03-stride-threat-model-r4.md`, `04-negative-security-test-matrix-r4.md` y `evidence/iam-r4-unit-tests-step-225.log`.

**No se presenta como evidencia de integración de la rama actual:** existen reportes anteriores de `SessionPostgresIT` y de flujos HTTP/PostgreSQL ejecutados en otra copia de trabajo. Deben repetirse sobre la rama institucional actual antes de afirmar cobertura de integración R4. La ejecución de CI sigue pendiente de autorización.

## Reversión

Ante una regresión confirmada, el código R4 deberá revertirse mediante el flujo Git revisado institucionalmente. Revertir la guarda de sesión elimina esta comprobación adicional y reintroduce el riesgo de reutilización de sesiones documentado; **no** constituye una alternativa equivalente desde el punto de vista de seguridad. Esta decisión específica no incorpora una nueva migración de esquema de base de datos.

## Referencias

- [Decisiones del módulo IAM (DEC-001, DEC-003, DEC-004, DEC-008)](../../../09-microservices/services/01-iam-service/decisions.md)
- [Documentación del microservicio IAM](../../../09-microservices/services/01-iam-service/README.md)
- [Registro institucional de ADR](../README.md)
- OWASP ASVS 5.0.0, requisito `v5.0.0-7.4.1`.
- Implementación IAM: `iam-core/src/main/java/co/sena/iam/application/usecase/GetCurrentUser.java`.
- Configuración IAM: `iam-api/src/main/java/co/sena/iam/api/config/UseCaseConfiguration.java`.
- Pruebas unitarias: `iam-core/src/test/java/co/sena/iam/application/usecase/GetCurrentUserTest.java`.
- Integración pendiente de repetición: `iam-api/src/test/java/co/sena/iam/api/SessionPostgresIT.java`.

---

> **Nota de revisión:** la aceptación de este ADR y la aclaración formal de las decisiones existentes requieren revisión de Arquitectura. Este documento propuesto no modifica ni aprueba ninguna decisión DEC o ADR anterior.
