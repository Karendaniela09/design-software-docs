# Informe técnico R6 — Migración TEXT a JSONB

**Proyecto:** Code-SENA  
**Reto:** R6 — EXPAND → BACKFILL → CONTRACT → ROLLBACK  
**Campo:** `monitoring.improvement_plan.specific_actions`  
**Responsable:** Nicolas Estid Ruiz Sastoque  
**Fecha de actualización:** 21 de octubre de 2026

## 1. Resumen ejecutivo

R6 implementa una migración progresiva de `TEXT` a `JSONB` para `monitoring.improvement_plan.specific_actions`, conservando compatibilidad durante la transición y separando CONTRACT en un changelog operativo independiente.

La implementación está distribuida entre cuatro repositorios:

- `design-software-monitoring-db`: changesets, SQL y rollbacks.
- `design-software-monitoring-service`: compatibilidad de persistencia, serialización y pruebas.
- `design-software-docker-infra`: servicio Liquibase con perfil `r6-contract`.
- `design-software-docs`: ADR, modelo de datos, decisiones y runbook.

El informe técnico ya no se mantiene dentro de `design-software-monitoring-db/docs`; esa copia fue eliminada por estar duplicada y desactualizada. La documentación oficial se conserva en `design-software-docs` y las evidencias personales en `docs/plan-mejoramiento-R6`.

## 2. Versiones y commits

| Repositorio | Rama | Commits R6 relacionados | Commit final |
|---|---|---:|---|
| `design-software-monitoring-db` | `hu-r6-nicolas-dev` | 3 | `c9bac2e` |
| `design-software-monitoring-service` | `hu-r6-nicolas-dev` | 2 | `90de34a` |
| `design-software-docker-infra` | `hu-r6-nicolas-dev` | 1 | `8f75bbd` |
| `design-software-docs` | `feat/r6-documentation` | 2 | `1d05bd2` |

### Commits DB

- `3dc359f`: implementación inicial EXPAND, BACKFILL, CONTRACT y ROLLBACK.
- `fe61fcf`: informe técnico anterior dentro del repositorio DB.
- `c9bac2e`: reconciliación de autor Liquibase y script de sincronización final.

### Commits Service

- `68f6edb`: compatibilidad TEXT/JSONB, router y pruebas de integración.
- `90de34a`: job CI para integraciones PostgreSQL R6 aisladas.

### Commit Infra

- `8f75bbd`: servicio Liquibase `liquibase-monitoring-contract` y perfil `r6-contract`.

### Commits Docs

- `0641156`: documentación R6, ADR y corrección de numeración.
- `1d05bd2`: bloqueos QA y procedimiento de corrección.

## 3. Implementación en Monitoring DB

### EXPAND

Changeset `r6-monitoring-expand-specific-actions-v2-991`:

- Agrega `specific_actions_v2 JSONB NULL`.
- Conserva `specific_actions TEXT NOT NULL`.
- Usa preconditions para validar la tabla y evitar duplicar la columna.
- Tiene rollback que elimina la columna v2.

Archivo principal: `01_ddl/04_alter/r6_expand_specific_actions_v2.sql`.

### BACKFILL

Changeset `r6-monitoring-backfill-specific-actions-v2-992`:

- Actualiza solo filas con `specific_actions_v2 IS NULL`.
- Conserva el TEXT original.
- Genera documentos con esta estructura:

```json
{
  "version": 1,
  "actions": [
    { "text": "valor original" }
  ]
}
```

La conversión conserva Unicode, comillas, caracteres especiales, texto vacío y saltos de línea como valores de cadena. La representación soportada contiene una única acción.

### Sincronización final

El archivo `01_ddl/04_alter/r6_sync_specific_actions_v2.sql` fue agregado en `c9bac2e`.

Características:

- Es transaccional e idempotente.
- Reporta discrepancias antes y después.
- Actualiza únicamente documentos JSONB compatibles con `version: 1` y una acción.
- No sobrescribe documentos nulos, malformados o de versiones no soportadas.
- Debe ejecutarse después de detener escritores antiguos y antes de CONTRACT.

### CONTRACT

Changeset `r6-monitoring-contract-specific-actions-v2-993`:

- Se ejecuta desde `changelog/changelog-contract.yaml`.
- Usa el contexto `r6-contract`.
- Verifica que no haya nulos, documentos inválidos ni diferencias TEXT/JSONB.
- Elimina la columna TEXT.
- Renombra `specific_actions_v2` a `specific_actions`.
- Establece `specific_actions JSONB NOT NULL`.

CONTRACT no se ejecuta durante el arranque convencional y requiere autorización, respaldo y validación operativa.

### ROLLBACK

El rollback de CONTRACT:

- Reconstruye `specific_actions TEXT NOT NULL` desde `actions[0].text`.
- Conserva `specific_actions_v2 JSONB NULL`.
- Mantiene los documentos JSONB compatibles.

No se garantiza reconstrucción completa para múltiples acciones, versiones futuras, campos adicionales o documentos JSONB no soportados.

## 4. Compatibilidad de Monitoring Service

El servicio contiene una capa de compatibilidad para los tres estados:

| Estado | Comportamiento |
|---|---|
| Antes de EXPAND | Lectura y escritura sobre TEXT |
| Durante EXPAND/BACKFILL | Coexistencia y sincronización TEXT/JSONB |
| Después de CONTRACT | Lectura y escritura sobre JSONB |

El contrato HTTP mantiene `specific_actions` como `string`. La migración del almacenamiento no cambia OpenAPI a `object` porque el backend continúa serializando el valor como texto.

Pruebas relacionadas:

- `tests/test_specific_actions_compat.py`.
- `tests/test_router_serialization.py`.
- `tests/test_r6_postgres_integration.py`.
- `tests/test_r6_http_postgres_integration.py`.
- `tests/test_monitoring_http_contract.py`.

El workflow CI para PostgreSQL aislado quedó preparado en el commit `90de34a`, pero su ejecución remota debe adjuntarse cuando exista el resultado del workflow. No se presenta como resultado aprobado en este informe.

## 5. Evidencias ejecutadas

Las evidencias completas están en:

[`docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6`](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6)

Se utilizaron cuatro bases PostgreSQL efímeras y aisladas, identificadas como DEV, QA, STAGING y PROD simulada. No fueron bases compartidas ni producción real.

### Identidad y esquema

Carpeta: [`01-liquibase-identidad`](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/01-liquibase-identidad)

Contiene una salida por ambiente con changesets, autor, tipos y nulabilidad antes de CONTRACT.

### Sincronización final

Carpeta: [`02-sincronizacion-final`](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/02-sincronizacion-final)

Las cuatro salidas reportan:

```text
discrepancies_before = 0
UPDATE 0
discrepancies_after = 0
discrepancias_finales = 0
```

### CONTRACT y ROLLBACK

Cada ambiente tiene cinco archivos de salida:

- `01-before-contract.txt`.
- `02-contract.txt`.
- `03-after-contract.txt`.
- `04-rollback.txt`.
- `05-after-rollback.txt`.

Carpetas:

- [`04-rollback-dev`](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/04-rollback-dev).
- [`04-rollback-qa`](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/04-rollback-qa).
- [`04-rollback-staging`](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/04-rollback-staging).
- [`04-rollback-prod-simulada`](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/04-rollback-prod-simulada).

Resultado observado después del rollback en cada base:

```text
specific_actions    TEXT NOT NULL
specific_actions_v2 JSONB NULL
planes              3
jsonb_poblados      3
inconsistencias     0
```

Los datos sintéticos incluyeron texto normal, Unicode y salto de línea. Los fingerprints normalizados de TEXT y JSONB coincidieron en los cuatro ambientes aislados.

## 6. Resultados históricos y resultados actuales

### Resultados históricos previamente comunicados

- Liquibase `validate`: correcto.
- Liquibase `update`: 26 changesets ejecutados.
- Integración SQL R6 con PostgreSQL real: 1 aprobada.
- Integración HTTP + PostgreSQL R6: 1 aprobada.
- Suite general Monitoring Service: 34 aprobadas y 8 omitidas.
- Ruff: aprobado.
- Compilación Python: satisfactoria.

### Validación ejecutada para las evidencias nuevas

- EXPAND/BACKFILL sobre cuatro bases efímeras.
- Sincronización final idempotente.
- CONTRACT con Liquibase 4.33.0.
- `rollback-count 1` con Liquibase 4.33.0.
- Consultas PostgreSQL de estructura, nulabilidad, conteos, equivalencia y fingerprints.
- Validación de enlaces Markdown: correcta.
- Eliminación posterior de los contenedores y red efímeros.

### Pendientes

- Resultado del workflow CI del servicio.
- Repetición en ambientes operativos autorizados.
- Evidencia de respaldo restaurado.
- Validación con múltiples acciones o versiones JSONB futuras.

## 7. Cumplimiento R6

| Requisito | Evidencia | Estado |
|---|---|---|
| R6(a) EXPAND/CONTRACT | Changesets, preconditions, changelog independiente y logs Liquibase | Cumplido en bases aisladas; pendiente promoción operativa |
| R6(b) Datos y BACKFILL | Tres planes sintéticos por base, backfill y sincronización final | Cumplido en bases aisladas |
| R6(c) Compatibilidad | Adaptador TEXT/JSONB, serialización HTTP y pruebas preparadas | Parcial hasta ejecutar CI y ambientes autorizados |
| R6(d) ROLLBACK en cuatro ambientes | Cuatro ciclos CONTRACT → ROLLBACK documentados | Cumplido para bases efímeras; pendiente validación operacional |

## 8. Trazabilidad incorporada en este informe

### 8.1 Trazabilidad de los requisitos R6

| Requisito | Evidencia incorporada | Resultado |
|---|---|---|
| R6(a) EXPAND/CONTRACT sobre tabla real | Changesets 991, 992 y 993, preconditions, SQL y logs Liquibase | Cumplido en las cuatro bases aisladas; pendiente promoción operativa |
| R6(b) Datos de prueba y BACKFILL | Tres planes sintéticos por base, documento JSONB generado y sincronización final | Cumplido en las bases aisladas |
| R6(c) Compatibilidad de versiones | Adaptador TEXT/JSONB, doble escritura, serialización HTTP y pruebas del servicio | Parcial hasta ejecutar CI y validar ambientes operativos |
| R6(d) ROLLBACK en cuatro ambientes | CONTRACT → `rollback-count 1`, consultas PostgreSQL y fingerprints por ambiente | Cumplido en cuatro bases efímeras; pendiente validación operacional |

### 8.2 Resultados por ambiente

| Ambiente | Base | Resultado CONTRACT | Resultado ROLLBACK | Verificación final |
|---|---|---|---|---|
| DEV | `r6_dev_db` | Ejecutado correctamente. `specific_actions` pasó a `JSONB NOT NULL`. 3 planes y 3 documentos JSONB. | Ejecutado correctamente con `rollback-count 1`. | `specific_actions TEXT NOT NULL`; `specific_actions_v2 JSONB NULL`; 3 planes; 3 JSONB conservados; 0 inconsistencias. Fingerprint: `a65ed94bf0bc33bbddc036be663bc1e4`. |
| QA | `r6_qa_db` | Ejecutado correctamente. `specific_actions` pasó a `JSONB NOT NULL`. 3 planes y 3 documentos JSONB. | Ejecutado correctamente con `rollback-count 1`. | `specific_actions TEXT NOT NULL`; `specific_actions_v2 JSONB NULL`; 3 planes; 3 JSONB conservados; 0 inconsistencias. Fingerprint: `a65ed94bf0bc33bbddc036be663bc1e4`. |
| STAGING | `r6_staging_db` | Ejecutado correctamente. `specific_actions` pasó a `JSONB NOT NULL`. 3 planes y 3 documentos JSONB. | Ejecutado correctamente con `rollback-count 1`. | `specific_actions TEXT NOT NULL`; `specific_actions_v2 JSONB NULL`; 3 planes; 3 JSONB conservados; 0 inconsistencias. Fingerprint: `a65ed94bf0bc33bbddc036be663bc1e4`. |
| PROD simulada | `r6_prod_sim_db` | Ejecutado correctamente. `specific_actions` pasó a `JSONB NOT NULL`. 3 planes y 3 documentos JSONB. | Ejecutado correctamente con `rollback-count 1`. | `specific_actions TEXT NOT NULL`; `specific_actions_v2 JSONB NULL`; 3 planes; 3 JSONB conservados; 0 inconsistencias. Fingerprint: `a65ed94bf0bc33bbddc036be663bc1e4`. |

### Lectura del cuadro

- **CONTRACT:** eliminó la columna TEXT, renombró la columna JSONB y dejó `specific_actions JSONB NOT NULL`.
- **ROLLBACK:** reconstruyó el campo TEXT y conservó el documento JSONB en `specific_actions_v2` como columna nullable.
- **3 planes:** cada base aislada recibió exactamente tres registros sintéticos.
- **3 JSONB conservados:** cada uno de los tres planes mantuvo su documento JSONB después del rollback.
- **0 inconsistencias:** el texto reconstruido coincidió con `specific_actions_v2->'actions'->0->>'text'`.
- **Fingerprint:** es la huella de los textos normalizados; coincide entre la columna TEXT y la representación JSONB.

Las salidas completas de Liquibase y PostgreSQL se conservaron como anexos en las carpetas de evidencia, pero los resultados importantes quedan escritos directamente en este informe para que no sea necesario abrirlas.

### 8.3 Correcciones QA aplicadas

| Hallazgo | Corrección incorporada |
|---|---|
| Identidad de changesets | Se alinearon los autores R6 del repositorio DB con el historial esperado (`codex`) en `c9bac2e`. |
| Rollback con nulabilidad incorrecta | Se ejecutó el changeset versionado y se comprobó `specific_actions_v2 JSONB NULL` después de `rollback-count 1`. |
| Secuencia no demostrada | Se conservaron salidas separadas de pre-CONTRACT, CONTRACT, post-CONTRACT, rollback y verificación final. |
| Divergencias antes de CONTRACT | Se ejecutó `r6_sync_specific_actions_v2.sql` en los cuatro ambientes aislados; las discrepancias finales fueron cero. |
| Documentación duplicada | Se eliminó `design-software-monitoring-db/docs/informe-tecnico-r6.md`; la documentación oficial permanece en `design-software-docs`. |
| CI opt-in | Se agregó el job PostgreSQL aislado al workflow del servicio; el resultado remoto queda pendiente de adjuntar. |

### 8.4 Archivos y logs de evidencia

La evidencia se encuentra en las carpetas siguientes y está enlazada directamente desde este informe:

- [Identidad Liquibase](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/01-liquibase-identidad).
- [Sincronización final](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/02-sincronizacion-final).
- [Rollback DEV](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/04-rollback-dev).
- [Rollback QA](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/04-rollback-qa).
- [Rollback STAGING](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/04-rollback-staging).
- [Rollback PROD simulada](docs/plan-mejoramiento-R6/evidencias/correcciones-qa-r6/04-rollback-prod-simulada).

No se incluyen como requisito otros documentos Markdown de entrega; este informe contiene directamente la explicación, la trazabilidad y los resultados.

### 8.5 Salidas incorporadas dentro de este informe

Esta sección reproduce las salidas esenciales de los archivos de evidencia para que la revisión pueda realizarse sin abrir documentos adicionales.

#### Identidad Liquibase y estado pre-CONTRACT

En los cuatro ambientes se ejecutaron los changesets sobre el commit DB `c9bac2e`. Los resultados fueron:

```text
CHANGESET                                           AUTHOR  FILENAME                         EXECUTED
r6-monitoring-expand-specific-actions-v2-991       codex   01_ddl/04_alter/changelog.yaml  EXECUTED
r6-monitoring-backfill-specific-actions-v2-992     codex   01_ddl/04_alter/changelog.yaml  EXECUTED

SCHEMA
specific_actions    text    NO
specific_actions_v2 jsonb   YES
```

| Ambiente | Base | Fecha UTC de captura | Planes antes de cargar datos | JSONB nulos | Diferencias |
|---|---|---|---:|---:|---:|
| DEV | `r6_dev_db` | `2026-10-21T04:41:05.6606673Z` | 0 | 0 | 0 |
| QA | `r6_qa_db` | `2026-10-21T04:41:05.9385184Z` | 0 | 0 | 0 |
| STAGING | `r6_staging_db` | `2026-10-21T04:41:05.9081676Z` | 0 | 0 | 0 |
| PROD simulada | `r6_prod_sim_db` | `2026-10-21T04:41:04.0598543Z` | 0 | 0 | 0 |

#### Sincronización final

La salida real de `r6_sync_specific_actions_v2.sql` fue equivalente en los cuatro ambientes:

```text
BEGIN
discrepancies_before
                    0
UPDATE 0
discrepancies_after
                   0
COMMIT
discrepancias_finales=0
```

Capturas: DEV `2026-10-21T04:47:25.2740769Z`, QA `2026-10-21T04:47:25.6475271Z`, STAGING `2026-10-21T04:47:26.0161614Z` y PROD simulada `2026-10-21T04:47:26.3616574Z`.

#### DEV — CONTRACT, ROLLBACK y verificación final

```text
Base: r6_dev_db
CONTRACT: Liquibase command 'update' was executed successfully.
POST-CONTRACT:
specific_actions=jsonb,nullable=NO
planes=3,jsonb_documents=3
Fingerprint JSONB: 54fb5f68fe128405dc6fb9834bafc151
ROLLBACK: Liquibase command 'rollback-count' was executed successfully.
POST-ROLLBACK:
specific_actions=text,nullable=NO
specific_actions_v2=jsonb,nullable=YES
planes=3,jsonb_poblados=3,inconsistencias=0
Fingerprint TEXT: a65ed94bf0bc33bbddc036be663bc1e4
Fingerprint JSONB normalizado: a65ed94bf0bc33bbddc036be663bc1e4
```

Datos conservados:

```json
{"id":"00000000-0000-0000-0000-000000000101","text":"Seguimiento académico"}
{"id":"00000000-0000-0000-0000-000000000102","text":"Evaluación técnica ✅"}
{"id":"00000000-0000-0000-0000-000000000103","text":"Revisión de evidencias.\nCorrección de errores."}
```

#### QA — CONTRACT, ROLLBACK y verificación final

```text
Base: r6_qa_db
CONTRACT: Liquibase command 'update' was executed successfully.
POST-CONTRACT: specific_actions=jsonb,nullable=NO; planes=3; jsonb_documents=3
ROLLBACK: Liquibase command 'rollback-count' was executed successfully.
POST-ROLLBACK:
specific_actions=text,nullable=NO
specific_actions_v2=jsonb,nullable=YES
planes=3,jsonb_poblados=3,inconsistencias=0
Fingerprint TEXT = Fingerprint JSONB normalizado:
a65ed94bf0bc33bbddc036be663bc1e4
```

#### STAGING — CONTRACT, ROLLBACK y verificación final

```text
Base: r6_staging_db
CONTRACT: Liquibase command 'update' was executed successfully.
POST-CONTRACT: specific_actions=jsonb,nullable=NO; planes=3; jsonb_documents=3
ROLLBACK: Liquibase command 'rollback-count' was executed successfully.
POST-ROLLBACK:
specific_actions=text,nullable=NO
specific_actions_v2=jsonb,nullable=YES
planes=3,jsonb_poblados=3,inconsistencias=0
Fingerprint TEXT = Fingerprint JSONB normalizado:
a65ed94bf0bc33bbddc036be663bc1e4
```

#### PROD simulada — CONTRACT, ROLLBACK y verificación final

```text
Base: r6_prod_sim_db
CONTRACT: Liquibase command 'update' was executed successfully.
POST-CONTRACT: specific_actions=jsonb,nullable=NO; planes=3; jsonb_documents=3
ROLLBACK: Liquibase command 'rollback-count' was executed successfully.
POST-ROLLBACK:
specific_actions=text,nullable=NO
specific_actions_v2=jsonb,nullable=YES
planes=3,jsonb_poblados=3,inconsistencias=0
Fingerprint TEXT = Fingerprint JSONB normalizado:
a65ed94bf0bc33bbddc036be663bc1e4
```

#### Interpretación de las salidas

- Antes de CONTRACT coexistían TEXT y JSONB; los tres planes tenían documentos JSONB válidos.
- CONTRACT dejó `specific_actions` como JSONB `NOT NULL`.
- ROLLBACK reconstruyó TEXT y dejó `specific_actions_v2` como JSONB nullable.
- Los tres textos originales se conservaron, incluyendo Unicode y salto de línea.
- La comparación final reportó cero inconsistencias en cada ambiente.
- Las bases fueron efímeras y aisladas; no representan bases operativas reales.

## 9. Referencias técnicas

- [PR DB #62](https://github.com/code-sena/design-software-monitoring-db/pull/62).
- [PR Service #8](https://github.com/code-sena/design-software-monitoring-service/pull/8).
- [PR Infra #43](https://github.com/code-sena/design-software-docker-infra/pull/43).

## 10. Declaración de alcance

Este informe refleja la implementación y las evidencias disponibles al 21 de octubre de 2026. No afirma pruebas, despliegues o resultados que no estén respaldados por los logs enlazados. Las evidencias nuevas cubren tres registros sintéticos por base, una versión JSONB y una acción por documento; no se extienden a más condiciones.
