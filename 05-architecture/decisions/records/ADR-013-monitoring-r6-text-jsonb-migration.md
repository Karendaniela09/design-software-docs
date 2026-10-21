# ADR-013: Migración progresiva de TEXT a JSONB en planes de mejoramiento de Monitoring

**Estado:** PROPOSED (pendiente de aprobación)
**Fecha:** 2026-10-20
**Autor:** Nicolas Estid Ruiz Sastoque
**Equipos involucrados:** Arquitectura, Backend (monitoring-service), Base de datos (monitoring-db), DevOps

---

## Contexto

El microservicio `monitoring-service` gestiona planes de mejoramiento asociados al seguimiento académico de las fichas de formación de Code-SENA.

La tabla `monitoring.improvement_plan` contiene el campo `specific_actions`, responsable de almacenar las acciones específicas de un plan de mejoramiento.

Originalmente, este campo utiliza el tipo `TEXT` de PostgreSQL. Aunque permite almacenar descripciones, no proporciona una estructura interna para representar acciones de forma versionada y extensible.

El Reto R6 plantea evolucionar dicho campo a `JSONB`, conservando los datos existentes y manteniendo la compatibilidad funcional del servicio.

La conversión directa de TEXT a JSONB presenta varios riesgos:

- Pérdida de información durante la transformación de datos.
- Incompatibilidad entre versiones del backend y de PostgreSQL.
- Interrupciones durante despliegues independientes.
- Diferencias entre valores antiguos y nuevos.
- Dificultades para revertir cambios destructivos.
- Alteraciones involuntarias del contrato HTTP.

Por ello, se requiere una estrategia que permita introducir el nuevo formato gradualmente, verificar la integridad y ejecutar la eliminación del formato anterior únicamente después de cumplir condiciones de seguridad.

## Decisión

Se adopta el patrón **Expand and Contract**, mediante las fases **EXPAND → BACKFILL → CONTRACT → ROLLBACK**, coordinando cambios en tres repositorios oficiales.

### 1. EXPAND: ampliación del esquema

Se agrega la columna `specific_actions_v2` de tipo `JSONB`, conservando `specific_actions` de tipo `TEXT`.

Durante esta etapa ambas columnas coexisten.

```sql
ALTER TABLE monitoring.improvement_plan
ADD COLUMN specific_actions_v2 JSONB;
```

La nueva columna permite introducir el formato estructurado sin retirar inmediatamente la representación utilizada por las versiones anteriores del servicio.

La migración utiliza precondiciones de Liquibase que comprueban el estado esperado del esquema.

El changeset real es `r6-monitoring-expand-specific-actions-v2-991`. Sus precondiciones exigen que exista `monitoring.improvement_plan.specific_actions` y que todavía no exista `specific_actions_v2`; si fallan, Liquibase detiene el changelog (`HALT`). El rollback ejecuta `r6_expand_specific_actions_v2.rollback.sql` y elimina la columna v2 si existe.

### 2. BACKFILL: transformación de registros existentes

Los valores existentes se trasladan a una representación JSONB versionada:

```json
{
  "version": 1,
  "actions": [
    {
      "text": "Realizar seguimiento académico semanal."
    }
  ]
}
```

La transformación implementada utiliza funciones nativas de PostgreSQL:

```sql
UPDATE monitoring.improvement_plan
SET specific_actions_v2 = jsonb_build_object(
    'version', 1,
    'actions', jsonb_build_array(
        jsonb_build_object('text', specific_actions)
    )
)
WHERE specific_actions_v2 IS NULL;
```

La estructura mantiene el contenido textual original dentro de `actions[0].text`.

El uso de `jsonb_build_object` y `jsonb_build_array` permite construir documentos JSONB sin concatenar manualmente cadenas.

La equivalencia de contenido se verifica mediante la expresión:

```sql
specific_actions =
specific_actions_v2->'actions'->0->>'text'
```

BACKFILL procesa los registros que cumplen su condición de actualización. No garantiza por sí solo la sincronización de las escrituras realizadas posteriormente.

El changeset real es `r6-monitoring-backfill-specific-actions-v2-992`. Exige que existan ambas columnas, actualiza únicamente filas con `specific_actions_v2 IS NULL` y conserva `specific_actions` sin modificar. La construcción JSONB evita concatenación manual, por lo que el texto vacío, Unicode, saltos de línea y comillas se almacenan como valor de cadena; no hay lógica que divida un texto en varias acciones. Su rollback (`r6_backfill_specific_actions_v2.rollback.sql`) extrae `actions[0].text` hacia TEXT, pero no valida por sí mismo que el documento tenga la forma esperada.

### 3. Compatibilidad de Monitoring Service

Se implementa una capa de compatibilidad de persistencia en:

`src/monitoring/adapter/outbound/persistence/specific_actions_compat.py`

Esta adaptación permite que el backend opere durante la evolución del esquema.

Se distinguen tres estados:

| Estado                 | Esquema                              | Comportamiento esperado                                 |
| ---------------------- | ------------------------------------ | ------------------------------------------------------- |
| Antes de EXPAND        | `specific_actions TEXT`            | Lectura y escritura sobre TEXT                          |
| Durante la transición | TEXT y `specific_actions_v2 JSONB` | Compatibilidad y sincronización entre representaciones |
| Después de CONTRACT   | `specific_actions JSONB`           | Operaciones adaptadas al formato JSONB                  |

La compatibilidad del almacenamiento no implica modificar el contrato público.

El estado se detecta inspeccionando el catálogo de PostgreSQL: `has_v2_column()` busca `specific_actions_v2` y `uses_jsonb_contract()` comprueba si la columna principal es JSONB. Antes de EXPAND se opera solo sobre TEXT; durante la transición se escribe TEXT y, si existe v2, se escribe también el documento JSONB; después de CONTRACT se enlaza `specific_actions` como JSONB y ya no se intenta escribir una v2 inexistente. Si el documento JSONB no coincide con el formato soportado, `decode_specific_actions()` no devuelve un error HTTP: para un objeto no reconocible lo convierte a su representación textual de Python. Esto es una limitación pendiente, no una validación de esquema completa.

El contrato OpenAPI conserva `specific_actions` como `string` en los esquemas de creación, actualización y respuesta.

De esta manera, los consumidores HTTP pueden continuar utilizando la representación textual existente, mientras el backend transforma los datos internamente.

### 4. CONTRACT: consolidación del nuevo formato

Una vez verificada la equivalencia de los datos y la compatibilidad de la aplicación, se permite completar la migración.

La operación elimina la columna TEXT original y renombra la columna JSONB:

```sql
ALTER TABLE monitoring.improvement_plan
DROP COLUMN specific_actions;

ALTER TABLE monitoring.improvement_plan
RENAME COLUMN specific_actions_v2 TO specific_actions;

ALTER TABLE monitoring.improvement_plan
ALTER COLUMN specific_actions SET NOT NULL;
```

El esquema final utiliza `specific_actions JSONB NOT NULL`.

**CONTRACT constituye una operación potencialmente destructiva y no se ejecuta automáticamente.**

La migración permanece en el changelog independiente:

`changelog/changelog-contract.yaml`

Su ejecución requiere comprobar previamente:

1. Que EXPAND y BACKFILL se hayan aplicado correctamente.
2. Que no existan valores JSONB pendientes o inconsistentes.
3. Que el contenido recuperado de JSONB coincida con el valor TEXT original.
4. Que la versión compatible de Monitoring Service esté desplegada.
5. Que no permanezcan escritores antiguos que actualicen únicamente TEXT.
6. Que exista un respaldo recuperable de PostgreSQL.
7. Que el procedimiento de reversión sea aplicable al estado real de los datos.
8. Que la ejecución esté autorizada por los responsables técnicos.

Las precondiciones SQL no sustituyen las verificaciones operativas del servicio.

El changeset real es `r6-monitoring-contract-specific-actions-v2-993`, con contexto `r6-contract`. Su `sqlCheck` bloquea la ejecución cuando hay `NULL`, tipos JSONB distintos de objeto, `version` distinta de `1`, `actions` que no sea un arreglo de longitud uno, un elemento sin `text` de tipo string o una diferencia con TEXT. SQL no puede demostrar por sí solo que no existan escritores antiguos, que el respaldo sea recuperable, que la versión desplegada del servicio sea la correcta o que la base de destino sea la autorizada.

### 5. ROLLBACK: recuperación controlada

Se incorporan scripts de rollback para las etapas de migración.

El rollback de CONTRACT reconstruye la representación TEXT utilizando el contenido disponible en JSONB.

El procedimiento restaura `specific_actions` como TEXT y conserva la representación JSONB bajo `specific_actions_v2`.

Esta reversión depende de que los datos continúen utilizando una estructura compatible con la extracción de `actions[0].text`.

Por tanto, **no se garantiza una reversión sin pérdida para documentos JSONB arbitrarios**, especialmente si posteriormente se almacenan múltiples acciones o estructuras distintas.

La reversión debe validarse contra el estado real de los datos antes de ejecutarse en entornos compartidos.

### 6. Gestión mediante Liquibase y Docker Infra

Las fases EXPAND y BACKFILL están integradas al changelog principal de Monitoring DB.

CONTRACT utiliza un changelog independiente y un servicio Docker Compose específico:

`liquibase-monitoring-contract`

Este servicio pertenece al perfil:

`r6-contract`

La separación permite preparar una ejecución explícita y coordinada de CONTRACT, sin incluirla en las migraciones habituales.

La activación del perfil no constituye autorización suficiente para ejecutar la operación destructiva. Deben verificarse el comando de ejecución, la base de destino, las variables de entorno y las condiciones anteriores.

## Consecuencias

### Positivas

- Permite evolucionar el esquema gradualmente sin retirar inmediatamente TEXT.
- Conserva una representación original durante la transición.
- Ofrece una estructura JSONB versionada.
- Mantiene el contrato HTTP existente.
- Facilita la comprobación de equivalencia entre representaciones.
- Separa la operación destructiva del despliegue habitual.
- Utiliza Liquibase para versionar las migraciones.
- Incorpora mecanismos de reversión para el formato soportado.

### Negativas / Trade-offs

- Durante la transición se mantienen dos representaciones del mismo dato.
- El backend requiere lógica adicional de compatibilidad.
- Se necesita coordinación entre despliegues de base de datos y aplicación.
- BACKFILL no reemplaza la sincronización de escrituras posteriores.
- CONTRACT exige validaciones operativas adicionales.
- La evolución futura del documento JSONB puede requerir nuevos cambios de persistencia y rollback.

### Riesgos

**Divergencia de datos:** un escritor antiguo puede modificar TEXT sin actualizar JSONB. Se requiere verificar la sincronización antes de CONTRACT.

**Pérdida de información:** retirar TEXT sin validar la equivalencia puede eliminar contenido que no haya sido migrado.

**Incompatibilidad de versiones:** desplegar CONTRACT antes de actualizar todos los escritores puede provocar errores en las operaciones del servicio.

**Rollback limitado:** el procedimiento actual reconstruye una representación textual basada en `actions[0].text`, por lo que debe revisarse si cambia el formato del documento JSONB.

**Ejecución accidental:** CONTRACT podría ejecutarse sobre una base incorrecta si no se controla expresamente el entorno, las credenciales y el comando Liquibase.

## Alternativas consideradas

| Alternativa                                | Evaluación                                                                                                                           |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| Convertir TEXT directamente a JSONB        | Descartada: requiere adaptar simultáneamente almacenamiento y aplicación, con mayor riesgo de incompatibilidad                      |
| Crear una tabla adicional para acciones    | Descartada para R6: supone un rediseño más amplio del dominio, relaciones y consultas                                               |
| Mantener TEXT indefinidamente              | Descartada: no cumple el objetivo de introducir una representación JSONB estructurada                                                |
| EXPAND → BACKFILL → CONTRACT → ROLLBACK | **Seleccionada:** permite transición progresiva, verificación de integridad y ejecución separada de operaciones destructivas |

## Validación

El repositorio conserva resultados registrados de una verificación previa en un entorno local con PostgreSQL temporal y aislado; esta auditoría documental no volvió a ejecutar esas pruebas.

### Evidencia y alcance de la validación

Los siguientes resultados son **resultados registrados previamente en el entorno local R6**, no ejecuciones realizadas durante esta auditoría documental: Liquibase `validate` correcto, `update` con 26 changesets, una prueba de integración SQL R6 aprobada, una prueba HTTP + PostgreSQL R6 aprobada, suite general de Monitoring Service con 34 aprobadas y 8 omitidas, Ruff aprobado y compilación Python satisfactoria.

La inspección estática realizada en esta tarea confirmó los archivos, changesets, SQL, adaptador, endpoints, pruebas preparadas y la configuración declarativa de Compose. No se ejecutaron migraciones, CONTRACT, rollbacks ni pruebas de integración, porque la tarea documental prohíbe operaciones destructivas y los tests R6 requieren variables explícitas y una base local desechable.

### Infraestructura

En esta auditoría se ejecutó una validación declarativa de Docker Compose con el perfil `r6-contract`, sin errores de configuración estructural.

Se observaron advertencias correspondientes a variables de entorno no definidas en la sesión local.

No se considera demostrado un despliegue productivo de CONTRACT por el hecho de haber validado Docker Compose.

### Limitaciones de las evidencias

Los resultados corresponden al entorno temporal utilizado para las pruebas R6.

Las verificaciones de integración continua y las aprobaciones de los Pull Requests constituyen controles independientes que deben completarse antes de la integración oficial.

## Condiciones de despliegue y reversión

La secuencia operativa recomendada es:

1. Verificar respaldos y estado inicial.
2. Aplicar EXPAND.
3. Desplegar la versión del backend compatible con ambas representaciones.
4. Ejecutar BACKFILL y comprobar los registros.
5. Mantener la sincronización entre TEXT y JSONB.
6. Confirmar que no existan escritores antiguos.
7. Verificar la equivalencia y completitud de los datos.
8. Autorizar y ejecutar CONTRACT mediante su changelog independiente.
9. Realizar verificaciones posteriores del backend y PostgreSQL.
10. Mantener disponible el procedimiento de rollback y restauración.

En la implementación versionada de R6, EXPAND y BACKFILL forman parte del changelog principal. La ejecución de ese changelog debe coordinarse con la versión compatible del backend, especialmente en entornos con escrituras concurrentes.

### Cumplimiento del Reto R6

| Requisito | Evidencia revisada | Estado | Pendiente |
|---|---|---|---|
| (a) EXPAND/CONTRACT sobre tabla real | Changesets `991` y `993`, SQL de EXPAND/CONTRACT, precondiciones y changelog separado | Cumplido | Ejecutar la promoción controlada según el ambiente objetivo. |
| (b) Datos de prueba y BACKFILL | `tests/test_r6_postgres_integration.py` y `tests/test_r6_http_postgres_integration.py` contienen datos y aserciones de BACKFILL; los tests son opt-in | Parcial | Registrar una ejecución reproducible con PostgreSQL y su resultado en el ambiente que corresponda. |
| (c) Compatibilidad de versiones | Capa `specific_actions_compat.py`, CRUD HTTP y prueba de integración HTTP durante transición y después de CONTRACT | Parcial | Confirmar la ejecución en el pipeline/ambientes oficiales; la auditoría local no los ejecutó. |
| (d) ROLLBACK en DEV, QA, STAGING y PROD simulada | Scripts de rollback y pruebas automatizadas preparadas; no se encontraron registros verificables de las cuatro ejecuciones | Pendiente | Ejecutar y conservar evidencia separada por ambiente, sin usar bases compartidas para pruebas destructivas. |

La afirmación general del README de `monitoring-db` sobre verificaciones en cuatro ambientes no aporta por sí sola una evidencia R6 trazable por ambiente, changeset y resultado; por ello no se eleva el requisito (d) a Cumplido.

## Referencias

- [ADR-004: Parametrización de estados y estándar de auditoría](ADR-004-status-parametrization-and-audit-standard.md).
- [Monitoring DB — PR #62](https://github.com/code-sena/design-software-monitoring-db/pull/62), commit de referencia `3dc359f`.
- [Monitoring Service — PR #8](https://github.com/code-sena/design-software-monitoring-service/pull/8), commit de referencia `68f6edb`.
- [Docker Infra — PR #43](https://github.com/code-sena/design-software-docker-infra/pull/43), commit de referencia `8f75bbd`.
- Modelo de datos: `../../../09-microservices/services/08-monitoring-service/data-model.md`.
- Decisiones internas de Monitoring: `../../../09-microservices/services/08-monitoring-service/decisions.md`.
- Runbook de Monitoring: `../../../09-microservices/services/08-monitoring-service/runbook.md`.
- Contrato OpenAPI: `../../../07-api/contracts/openapi/monitoring.yaml`.

---

**Estado de la decisión:** cambios solicitados por QA; no aprobada todavía. La implementación R6 tiene commits locales de corrección en `design-software-monitoring-db` (`c9bac2e`) y `design-software-monitoring-service` (`90de34a`), pero requiere ejecutar las validaciones aisladas antes de solicitar aprobación.

## Revisión QA del 20 de octubre de 2026

La revisión QA identificó cuatro condiciones que deben resolverse antes de autorizar CONTRACT o declarar R6(d) cumplido:

1. La identidad histórica de los changesets 991, 992 y 993 debe coincidir con `DATABASECHANGELOG`; el código de corrección alinea el autor con `codex`, pero `validate`, `status` y `update` deben ejecutarse sobre una copia aislada con historial previo.
2. Las evidencias multiambiente muestran `specific_actions_v2 JSONB NOT NULL` después del rollback, mientras el SQL versionado espera `JSONB NULL`. La ejecución debe repetirse con el commit exacto y conservar comando, fecha, base, historial y huellas de datos.
3. BACKFILL no corrige JSONB no nulo desactualizado por escritores antiguos. El commit DB incorpora `r6_sync_specific_actions_v2.sql`, un procedimiento operativo idempotente y limitado al formato `version: 1` con una única acción; debe ejecutarse con escritores antiguos detenidos y con cero divergencias antes de CONTRACT.
4. El Service incorpora en `90de34a` un job CI con PostgreSQL efímero y reportes JUnit para separar las integraciones HTTP/SQL de las pruebas unitarias; la ejecución del workflow sigue pendiente.

Las evidencias históricas se conservan y no se presentan como validación oficial de QA. La PROD simulada no equivale a producción real. No se autoriza CONTRACT sobre ambientes compartidos sin respaldo recuperable, autorización operativa y evidencia reproducible.

La aceptación de este ADR no autoriza automáticamente la ejecución de CONTRACT sobre bases de datos compartidas o de producción.
