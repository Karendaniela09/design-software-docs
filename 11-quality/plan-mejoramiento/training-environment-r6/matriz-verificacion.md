# Matriz de verificación — Acta 02 R6

> Estado: 🟡 En revisión | Última actualización: 2026-10-20  
> Autor: Juan Sebastián González Horta (`jsgh1`) | Equipo: Training Environment

## Contexto

Resumen de las pruebas efectuadas sobre los changesets y el flujo de mantenimiento vinculados al [PR #134](https://github.com/code-sena/design-software-training-environment-db/pull/134).

## Resultados

| Requisito | Evidencia | Resultado |
|---|---|---|
| EXPAND/BACKFILL y CONTRACT | Liquibase 964, 965, changelog manual 966 | Verificado en laboratorio |
| Datos anteriores y backfill | Seeds, comparación `IS DISTINCT FROM` | Verificado |
| Compatibilidad de esquema | Escrituras SQL por ambas columnas, lecturas del Go existente | Verificado localmente |
| Rollback | Reversión de CONTRACT y EXPAND/BACKFILL | Verificado en cuatro bases Docker aisladas |
| Lectura desde web-shell | Tres ambientes consultados por API Go | Verificado localmente |
| Alta de mantenimiento | POST y consulta SQL del motivo | Verificado localmente |
| Cuatro ambientes institucionales | Infraestructura compartida oficial | No probado |
| Continuidad sin errores en despliegue real | Métricas con tráfico continuo y versiones definitivas del servicio | No medido |

## Verificación técnica final y observaciones de QA

La prueba del 19/10/2026 contiene registros verificables de **aplicación de CONTRACT, comprobación SQL, rollback de CONTRACT y datos preservados en 4/4 laboratorios locales**, pero utiliza la ruta histórica `r6/contract/changelog.yaml`. **Pendiente:** repetir la ejecución y el rollback desde `changelog/changelog-r6-contract.yaml` con el código final del PR DB #134. Hasta tener nuevos logs, el cierre de esa validación no debe marcarse como PASS.

- [Matriz de QA con enlaces a los cuatro laboratorios](matriz-qa-20261022.md).
- [Guía de reproducción y controles](README-VALIDACION-R6.md).

## Archivos de evidencia

Ver [el inventario](evidencias/README.md) y las carpetas `20261019_160331`, `20261019_181957`, `20261019_200331`, `20261019_213954` y `20261020_integracion_web_shell`. Los archivos conservan los resultados originales de los ensayos.

## Referencias

- [ADR-017](../../../05-architecture/decisions/records/ADR-017-training-environment-r6-schema-evolution.md).
- [Informe técnico](informe-tecnico-r6.md).
- [Informe de integración](informe-integracion-local.md).
