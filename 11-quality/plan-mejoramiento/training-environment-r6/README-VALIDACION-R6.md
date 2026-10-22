# Procedimiento de reproducción — R6 Training Environment DB

> Fecha: 2026-10-22 · Autor: Juan Sebastián González Horta (`jsgh1`)  
> Estado: procedimiento publicado; **la ejecución del changelog reubicado queda pendiente de evidencia**.

Este procedimiento corresponde a la implementación del [PR DB #134](https://github.com/code-sena/design-software-training-environment-db/pull/134) y la documentación del [PR Docs #337](https://github.com/code-sena/design-software-docs/pull/337). **No ejecutar sobre bases compartidas, de QA institucional, staging o producción.**

## 1. Archivos que se prueban

| Etapa | Repositorio de origen | Ruta |
|---|---|---|
| EXPAND | Training Environment DB | `01_ddl/04_alter/964_r6_maintenance_reason_expand.sql` |
| BACKFILL | Training Environment DB | `01_ddl/04_alter/965_r6_maintenance_reason_backfill.sql` |
| CONTRACT | Training Environment DB | `01_ddl/04_alter/966_r6_reason_contract.sql` |
| Changelog CONTRACT **definitivo** | Training Environment DB | `changelog/changelog-r6-contract.yaml` |
| Rollback CONTRACT | Training Environment DB | `05_rollbacks/01_ddl/04_alter/966_r6_reason_contract.rollback.sql` |
| Rollbacks 964/965 | Training Environment DB | `05_rollbacks/01_ddl/04_alter/` |
| SQL de pruebas | Docs | [`evidencias/pruebas-sql/`](evidencias/pruebas-sql/README.md) |

El changeset `r6-env-maintenance-reason-contract-v1` está aislado. **No introducir CONTRACT en el changelog principal.** Las rutas SQL de la versión final se resuelven respecto al changelog mediante `relativeToChangelogFile: true`.

## 2. Preparación del laboratorio (Windows / PowerShell)

Requisitos locales: Docker Desktop con Docker Compose, Go 1.26.x, PowerShell 5.1+, red para obtener las imágenes y un clon local de **ambos repositorios**. El procedimiento probado anteriormente empleó el Compose del proyecto `design-software-docker-infra`; crear un proyecto distinto y un `.env` temporal para no usar sus volúmenes.

En dos carpetas locales independientes, poner al día las ramas; **no usar `git reset --hard` ni descartar cambios locales**:

```powershell
git -C "E:\Nueva carpeta\training-env-db-r6" fetch origin feat/r6-training-db
git -C "E:\Nueva carpeta\training-env-db-r6" switch feat/r6-training-db
git -C "E:\Nueva carpeta\training-env-db-r6" status --short
git -C "E:\Nueva carpeta\training-env-db-r6" log -1 --format="%H"

git -C "E:\Nueva carpeta\INTEGRACION_ENV\design-software-docs" fetch origin feat/r6-training-db
git -C "E:\Nueva carpeta\INTEGRACION_ENV\design-software-docs" switch feat/r6-training-db
git -C "E:\Nueva carpeta\INTEGRACION_ENV\design-software-docs" status --short
git -C "E:\Nueva carpeta\INTEGRACION_ENV\design-software-docs" log -1 --format="%H"
```

Si las ramas ya existían localmente pero están atrasadas, realizar un **fast-forward** solo después de inspeccionar `status`. Registrar los SHA impresos y confirmar que se está probando el código del PR.

## 3. Secuencia reproducible

1. Crear una base PostgreSQL 16 **nueva, desechable**, usando un proyecto Compose de nombre único y su propio volumen.
2. Copiar los archivos del repositorio DB a un directorio temporal. Excluir `.git` y archivos auxiliares que no pertenezcan a la rama.
3. En **esa copia temporal exclusivamente**, retirar del `01_ddl/changelog.yaml` los cambiosets R6 para ejecutar el baseline histórico. Ejecutar Liquibase y registrar los changesets previos.
4. Ejecutar [`01_seed_legacy.sql`](evidencias/pruebas-sql/01_seed_legacy.sql) antes de EXPAND, incluyendo el motivo nulo, y registrar `count(*)`, `count(reason)` y el número de motivos nulos.
5. Restaurar en la copia temporal el changelog completo y ejecutar los changesets 964/965. Verificar ambos campos con [`02_verify_expand.sql`](evidencias/pruebas-sql/02_verify_expand.sql); comprobar igualdad, escrituras v1/v2 y rechazo del conflicto.
6. Ejecutar desde la raíz de la copia temporal el **changelog final** con Liquibase, sin cambiar al changelog antiguo:
   ```text
   liquibase --search-path=/workspace \
     --changeLogFile=changelog/changelog-r6-contract.yaml \
     --url=jdbc:postgresql://postgres:5432/<DB_AISLADA> \
     --username=<USUARIO_LAB> --password=<CLAVE_LAB> update
   ```
   La invocación anterior es orientativa **dentro del contenedor Liquibase** configurado con las credenciales efímeras. No pegar valores reales en documentación ni registros públicos.
7. Ejecutar [`03_verify_contract.sql`](evidencias/pruebas-sql/03_verify_contract.sql): `reason` debe desaparecer, `reason_detail` conservar datos y admitir escrituras nuevas. Registrar `count(*)` y motivos no nulos.
8. Con ese mismo changelog y sobre la misma **base efímera**, ejecutar `rollbackCount 1` y luego [`04_verify_contract_rollback.sql`](evidencias/pruebas-sql/04_verify_contract_rollback.sql). Confirmar que reaparecieron `reason`, el trigger `trg_r6_sync_maintenance_reason` y la función `fn_r6_sync_maintenance_reason`.
9. Probar nuevamente un INSERT o UPDATE escribiendo `reason` y comprobar que se refleja en `reason_detail`. Si el servicio Go v1 está disponible en el laboratorio, ejecutar y registrar GET/POST después de la reversión.
10. Ejecutar `rollbackCount 2` **contra el changelog principal** para revertir BACKFILL y EXPAND; ejecutar [`05_verify_expand_rollback.sql`](evidencias/pruebas-sql/05_verify_expand_rollback.sql). Comprobar que sigue `reason` con los motivos de prueba y no existe `reason_detail`.
11. Exportar logs, SHA-256 de los scripts, SHA de los repositorios, versión Docker/Liquibase, recuentos y `RESULTADO_FINAL.txt`. Limpiar **únicamente** el proyecto Compose desechable y su volumen. Preservar logs de cualquier fallo.

**IMPORTANTE:** los pasos 6 y 8 no se ejecutaron desde esta revisión. Se publican para su ejecución controlada; no equivalen a un resultado PASS.

## 4. Consultas de control

Después de EXPAND/BACKFILL:

```sql
SELECT COUNT(*) AS filas,
       COUNT(reason) AS reason_no_nulos,
       COUNT(reason_detail) AS reason_detail_no_nulos,
       COUNT(*) FILTER (WHERE reason IS DISTINCT FROM reason_detail) AS divergencias
FROM training_environment.maintenance;
```

Después de CONTRACT:

```sql
SELECT COUNT(*) AS filas,
       COUNT(reason_detail) AS motivos_no_nulos
FROM training_environment.maintenance;
```

Tras rollback CONTRACT, el control de existencia de trigger y función:

```sql
SELECT EXISTS (
  SELECT 1 FROM pg_trigger t
  JOIN pg_class c ON c.oid = t.tgrelid
  JOIN pg_namespace n ON n.oid = c.relnamespace
  WHERE n.nspname = 'training_environment'
    AND c.relname = 'maintenance'
    AND t.tgname = 'trg_r6_sync_maintenance_reason'
    AND NOT t.tgisinternal
) AS trigger_restaurado,
EXISTS (
  SELECT 1 FROM pg_proc p
  JOIN pg_namespace n ON n.oid = p.pronamespace
  WHERE n.nspname = 'training_environment'
    AND p.proname = 'fn_r6_sync_maintenance_reason'
) AS funcion_restaurada;
```

## 5. Evidencia y criterios de aceptación

| Prueba | Esperado |
|---|---|
| Migración principal | 964 y 965 completados |
| BACKFILL | Divergencias = 0 |
| CONTR​ACT definitivo | 966 aplicado desde `changelog/changelog-r6-contract.yaml` |
| Validación CONTRACT | `reason` ausente y `reason_detail` sin pérdida |
| Rollback CONTRACT | `reason`, función y trigger restaurados |
| Escritura v1 después de rollback | Inserción/actualización satisfactoria y sincronizada |
| Rollback de EXPAND/BACKFILL | `reason_detail` ausente, datos preservados |
| Integridad | Logs y hashes asociados al mismo commit |
| Separación | Sin cambios en bases existentes ni contenedores ajenos |

Guardar la nueva evidencia bajo `evidencias/validacion-ruta-final/` **solo después de ejecutar el laboratorio**. La [matriz específica de QA](matriz-qa-20261022.md) distingue las pruebas ya completadas con la ruta antigua de las pendientes con la ruta definitiva.

## 6. Dependencias de despliegue y límites

- Go v1 consume `reason`; Go v2 fue una variante de laboratorio. La migración definitiva del consumidor debe coordinarse en otro trabajo y no se incluye en DB #134.
- CONTRACT **no debe ejecutarse mientras haya consumidores que dependan de `reason`**. Validar instancias, planes de rollback y aprobación del responsable del dominio antes de habilitarlo en un ambiente compartido.
- `outbox` fue creada solo como fixture de integración HTTP local, no como migración oficial DB.
- La prueba local de compatibilidad no equivale a disponibilidad de producción ni a IAM institucional.

## 7. Referencias

- [ADR-016 — evolución del esquema](../../../05-architecture/decisions/records/ADR-016-training-environment-r6-schema-evolution.md)
- [Matriz de QA por ambiente](matriz-qa-20261022.md)
- [Evidencias anteriores](evidencias/20261019_160331/README.md)
- [PR ENV DB #134](https://github.com/code-sena/design-software-training-environment-db/pull/134)
