# Informe técnico — evolución de esquema R6

> Estado: 🟡 En revisión | Última actualización: 2026-10-20  
> Autor: Juan Sebastián González Horta (`jsgh1`) | Equipo: Training Environment

## Contexto

Implementé la transición de `maintenance.reason` a `reason_detail` sobre PostgreSQL 16 utilizando Liquibase. El cambio permite conservar la columna anterior durante la adaptación del consumidor, completar datos históricos y contar con rollback.

## Implementación

| Etapa | Archivos en Training Environment DB |
|---|---|
| EXPAND | `01_ddl/04_alter/964_r6_maintenance_reason_expand.sql` |
| BACKFILL | `01_ddl/04_alter/965_r6_maintenance_reason_backfill.sql` |
| Rollbacks | `05_rollbacks/01_ddl/04_alter/964_*.rollback.sql` y `965_*.rollback.sql` |
| CONTRACT manual | `changelog/changelog-r6-contract.yaml`, `01_ddl/04_alter/966_r6_reason_contract.sql` y su rollback |

Los changesets 964 y 965 se registran desde el changelog principal. El 966 queda separado para su ejecución coordinada; no se promueve automáticamente mientras haya consumidores de `reason`.

## Validación realizada

**Datos y compatibilidad.** Se insertaron registros anteriores al cambio, incluyendo un motivo `NULL`. Después de EXPAND/BACKFILL se verificó la igualdad de las dos columnas. Las pruebas SQL escribieron tanto por `reason` como por `reason_detail` y comprobaron el rechazo de valores contradictorios.

**Cuatro bases Docker locales.** Ejecuté la migración y reversión sobre cuatro bases aisladas identificadas como `develop`, `qa`, `staging` y `main`. En las salidas se encuentran los resultados de Liquibase, las consultas PostgreSQL, CONTRACT y sus rollbacks. Los nombres identifican laboratorios, no despliegues institucionales.

**Servicio Go.** El backend existente se compiló y respondió a peticiones HTTP de mantenimiento sobre el esquema expandido. Las pruebas de escritura v1/v2 a nivel SQL y las peticiones con servicio Go están separadas en los registros de evidencia.

**Reversión.** Se probó la recuperación de `reason` después de CONTRACT y el rollback de EXPAND/BACKFILL, conservando los valores existentes. Los resultados y comandos ejecutados se adjuntan en [evidencias](evidencias/README.md).

## Alcance y riesgos

No se midió tiempo de indisponibilidad en un despliegue real con tráfico continuo. El backend Go publicado continúa utilizando `reason` y no se debe ejecutar CONTRACT contra ese consumidor. El cambio definitivo al nuevo campo requiere una versión coordinada del servicio y su correspondiente validación.

## Referencias

- [ADR-017](../../../05-architecture/decisions/records/ADR-017-training-environment-r6-schema-evolution.md).
- [Matriz de verificación](matriz-verificacion.md).
- [PR de implementación](https://github.com/code-sena/design-software-training-environment-db/pull/134).
