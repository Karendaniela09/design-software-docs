# ADR-017: Evolución gradual del motivo de mantenimiento en Training Environment

**Estado:** PROPOSED  
**Fecha:** 2026-10-20  
**Autor:** Juan Sebastián González Horta (`jsgh1`)  
**Dominio:** Training Environment · PostgreSQL 16 · Liquibase

## Contexto

La tabla `training_environment.maintenance` almacena el motivo en `reason VARCHAR(255)`. El servicio Go publicado utiliza esa columna en sus lecturas y escrituras. Renombrarla o eliminarla directamente dejaría de ser compatible con ese consumidor.

Para el reto R6 del Acta 02 se necesitaba una migración incremental, con conservación de datos, compatibilidad durante la transición y reversión comprobable.

## Decisión

Adopté la secuencia **EXPAND → BACKFILL → CONTRACT**.

1. **EXPAND (964):** crear `reason_detail VARCHAR(255)` sin eliminar `reason`. Incorporar un trigger transitorio para sincronizar ambas columnas durante INSERT/UPDATE. Una escritura contradictoria se rechaza con SQLSTATE `23514`.
2. **BACKFILL (965):** copiar los motivos anteriores y comprobar equivalencia con `IS DISTINCT FROM`, que también contempla `NULL`.
3. **Compatibilidad:** mantener las consultas del servicio anterior y admitir escrituras por ambas columnas mientras se migra el consumidor.
4. **CONTRACT (966):** retirar `reason` mediante un changelog **manual e independiente**, después de actualizar los consumidores. Su rollback recupera la columna y los valores a partir de `reason_detail`.

EXPAND y BACKFILL están registrados en el changelog ordinario. CONTRACT no se incluye en `changelog-master.yaml` y no debe ejecutarse con el servicio Go actual.

## Alternativas consideradas

| Alternativa | Motivo del descarte |
|---|---|
| Renombrar `reason` directamente | Rompe las consultas existentes. |
| Eliminar `reason` junto con EXPAND | Impide ejecutar instancias antiguas durante una transición. |
| Resolver la compatibilidad solo en el backend | No cubre escrituras SQL directas ni garantiza el orden de actualización de consumidores. |
| Editar changesets históricos | Puede alterar los checksums registrados por Liquibase. |

## Consecuencias

La versión anterior del servicio puede continuar usando `reason` después de EXPAND/BACKFILL. El trigger agrega lógica temporal y la fase de CONTRACT requiere una decisión de despliegue independiente. Sobre grandes volúmenes, el backfill y el DDL requieren planificación y observación de bloqueos.

Las verificaciones locales probaron migraciones, sincronización y rollbacks en bases Docker aisladas, además de lecturas de la API Go. No constituyen una medición de cero interrupciones durante un despliegue institucional. Tampoco sustituyen la adaptación definitiva del backend para consumir exclusivamente `reason_detail`.

## Referencias

- [PR #134: implementación de la migración](https://github.com/code-sena/design-software-training-environment-db/pull/134).
- [Technical implementation report](../../../09-microservices/services/04-training-environment-service/r6-schema-evolution.md).
- [QA verification report](../../../11-quality/qa-report-r6-training-environment-db.md).
- Acta 02, ADSO 3145555, numeral 13 (R6).
