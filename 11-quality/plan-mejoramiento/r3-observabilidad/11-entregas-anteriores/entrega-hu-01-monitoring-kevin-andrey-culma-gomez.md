# Entrega Develop HU-MON-001 / HU-01-monitoring

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

Fecha: 2026-10-13

Desarrollador: Kevin Andrey Culma Gomez

## Repositorios y ramas revisadas

| Repositorio | Rama | Estado |
| --- | --- | --- |
| `design-software-monitoring-service` | `hu-01-dev` | Modificado y subido |
| `design-software-monitoring-db` | `hu-09-dev` | Modificado y subido |
| `design-software-docs` | `main` | Revisado como fuente documental, sin cambios para esta HU |

La rama de `monitoring-service` se ajusto a `hu-01-dev` porque es la primera rama numerada en ese repositorio. En `monitoring-db` se uso `hu-09-dev` porque la numeracion existente llega hasta HU-08.

## Alcance implementado

La implementacion se realizo para HU-MON-001: modelo de datos y repositorios de monitoreo.

El objetivo principal fue reemplazar el skeleton de persistencia en `monitoring-service` por un repositorio SQLAlchemy funcional y complementar `monitoring-db` con migraciones versionadas para las garantias criticas del modelo:

- persistencia real de mediciones KPI;
- consulta de historicos KPI por ficha;
- particiones mensuales de `kpi_tracking`;
- comportamiento append-only para `kpi_tracking`;
- arco exclusivo de `generated_alert`;
- rollback versionado.

La documentacion fuente revisada fue:

- `design-software-docs/09-microservices/services/08-monitoring-service/data-model.md`
- `design-software-docs/05-architecture/decisions/records/ADR-004-status-parametrization-and-audit-standard.md`
- `design-software-docs/05-architecture/decisions/records/ADR-005-microservices-topology-and-transversal-capabilities.md`

## Cambios realizados

### 1. Repositorio SQLAlchemy real para KPI

Archivos:

- `design-software-monitoring-service/src/monitoring/adapter/outbound/persistence/repo.py`
- `design-software-monitoring-service/src/monitoring/application/port/outbound/repository.py`

Antes:

- `SqlAlchemyKpiRepository` era un skeleton.
- El metodo `save` no insertaba datos reales.
- No existia consulta del historico KPI desde persistencia.

Ahora:

- `SqlAlchemyKpiRepository` usa SQLAlchemy Core.
- Abre transacciones con `Session.begin()`.
- Resuelve catalogos por codigo (`kpi_type`, `kpi_status`).
- Crea `ficha_tracking` si no existe una fila para la ficha.
- Inserta mediciones reales en `monitoring.kpi_tracking`.
- Expone `list_by_ficha` para consultar historicos por `ficha_id`.
- Envuelve errores SQLAlchemy en `PersistenceError`.
- Reporta catalogos faltantes con `CatalogNotFound`.

Motivo:

- Cumplir AC-006.
- Eliminar el skeleton.
- Mantener arquitectura hexagonal: dominio y puertos no dependen de SQLAlchemy.

### 2. Dominio y puertos actualizados

Archivos:

- `design-software-monitoring-service/src/monitoring/domain/model/kpi.py`
- `design-software-monitoring-service/src/monitoring/domain/model/alert.py`
- `design-software-monitoring-service/src/monitoring/application/port/inbound/record_kpi.py`
- `design-software-monitoring-service/src/monitoring/application/usecase/record_kpi.py`

Cambios:

- `KpiMeasurement` ahora maneja `UUID`, `Decimal`, `threshold_value`, `status_code`, periodo e identificador persistido.
- Se agrego validacion de valores negativos.
- Se agrego `GeneratedAlertDraft` con validacion de arco exclusivo.
- `RecordKpiCommand` ahora recibe `threshold_value` y `status_code`.
- El caso de uso sigue siendo puro: construye dominio y delega al puerto de repositorio.

Motivo:

- Cumplir arquitectura hexagonal.
- Cumplir AC-004 a nivel de dominio.
- Permitir que el repositorio inserte datos suficientes para el schema real.

### 3. API y composition root

Archivos:

- `design-software-monitoring-service/apps/api/main.py`
- `design-software-monitoring-service/src/monitoring/adapter/inbound/http/router.py`
- `design-software-monitoring-service/pyproject.toml`

Cambios:

- La API instancia `SqlAlchemyKpiRepository` desde `DATABASE_URL`.
- El endpoint de registro KPI acepta:
  - `ficha_id`
  - `kpi_code`
  - `value`
  - `threshold_value`
  - `status_code`
- La respuesta incluye `id`, `ficha_id`, `kpi_code`, `value` y `measured_at`.
- Se agrego dependencia `psycopg[binary]` para PostgreSQL.

Motivo:

- Conectar el caso de uso al adaptador real.
- Evitar datos en memoria.
- Permitir ejecucion contra PostgreSQL real.

### 4. Migracion versionada para particiones y append-only

Archivos:

- `design-software-monitoring-db/01_ddl/04_alter/990_hu_mon_001_kpi_partitions_append_only.sql`
- `design-software-monitoring-db/05_rollbacks/01_ddl/04_alter/990_hu_mon_001_kpi_partitions_append_only.rollback.sql`
- `design-software-monitoring-db/01_ddl/04_alter/changelog.yaml`

Cambios:

- Se agrego changeset `hu-mon-001-kpi-partitions-append-only-990`.
- Se crearon particiones mensuales:
  - `monitoring.kpi_tracking_2026_09`
  - `monitoring.kpi_tracking_2026_10`
  - `monitoring.kpi_tracking_2026_11`
  - `monitoring.kpi_tracking_2026_12`
- Se agrego funcion `monitoring.prevent_kpi_tracking_mutation()`.
- Se agregaron triggers para rechazar `UPDATE` y `DELETE` sobre `monitoring.kpi_tracking`.
- Se agrego constraint nombrada `ck_generated_alert_affected_actor_exclusive`.
- Se agrego rollback para remover constraint, triggers, funcion y particiones.

Motivo:

- Cumplir AC-001.
- Cumplir AC-002.
- Cumplir AC-004.
- Dejar evidencia versionada y reproducible.

### 5. Extension necesaria para UUID

Archivos:

- `design-software-monitoring-db/01_ddl/00_extensions/001_enable_uuid_extension.sql`
- `design-software-monitoring-db/05_rollbacks/01_ddl/00_extensions/001_enable_uuid_extension.rollback.sql`

Cambios:

- Se agrego `CREATE EXTENSION IF NOT EXISTS pgcrypto`.
- Se agrego rollback `DROP EXTENSION IF EXISTS pgcrypto`.

Motivo:

- Los scripts existentes usan `gen_random_uuid()`.
- `gen_random_uuid()` depende de `pgcrypto` en PostgreSQL.

### 6. Pruebas unitarias e integracion preparadas

Archivos:

- `design-software-monitoring-service/tests/test_record_kpi.py`
- `design-software-monitoring-service/tests/test_sqlalchemy_kpi_repository.py`

Cambios:

- Prueba unitaria del caso de uso `RecordKpi`.
- Prueba de dominio para rechazar doble entidad afectada en `GeneratedAlertDraft`.
- Prueba de integracion preparada para:
  - insertar KPI real;
  - consultar KPI por ficha;
  - validar calculo de asistencia esperado;
  - validar existencia de CHECK del arco exclusivo.
- Las pruebas de integracion se ejecutan solo si existe `MONITORING_TEST_DATABASE_URL`.

Motivo:

- Cumplir AC-007 sin forzar ejecucion contra una base local equivocada.
- Permitir que QA/CI ejecute las pruebas contra PostgreSQL real.

## Criterios revisados

### AC-001 Migraciones versionadas para schema y tablas

Estado: CUMPLE PARCIALMENTE / REQUIERE VALIDACION QA CON LIQUIBASE.

Evidencia de implementacion:

- `monitoring-db` ya contiene estructura Liquibase versionada.
- La HU agrega changeset nuevo:

```text
hu-mon-001-kpi-partitions-append-only-990
```

Archivos:

```text
01_ddl/04_alter/990_hu_mon_001_kpi_partitions_append_only.sql
05_rollbacks/01_ddl/04_alter/990_hu_mon_001_kpi_partitions_append_only.rollback.sql
```

Validacion pendiente:

```powershell
docker compose --profile tooling run --rm liquibase-monitoring update
docker compose --profile tooling run --rm liquibase-monitoring rollbackCount 1
```

### AC-002 `kpi_tracking` particionada por `measured_at` y append-only

Estado: IMPLEMENTADO.

Evidencia:

```sql
CREATE TABLE IF NOT EXISTS monitoring.kpi_tracking_2026_10
    PARTITION OF monitoring.kpi_tracking
    FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');
```

Append-only:

```sql
CREATE TRIGGER trg_kpi_tracking_prevent_update
    BEFORE UPDATE ON monitoring.kpi_tracking
    FOR EACH ROW
    EXECUTE FUNCTION monitoring.prevent_kpi_tracking_mutation();

CREATE TRIGGER trg_kpi_tracking_prevent_delete
    BEFORE DELETE ON monitoring.kpi_tracking
    FOR EACH ROW
    EXECUTE FUNCTION monitoring.prevent_kpi_tracking_mutation();
```

Validacion QA esperada:

- Insertar medicion KPI.
- Intentar `UPDATE`.
- Intentar `DELETE`.
- Ambos deben fallar.

### AC-003 `attendance_percentage` calculado correctamente

Estado: CUBIERTO POR MODELO EXISTENTE / REQUIERE VALIDACION QA EN BD.

Evidencia en schema existente:

```sql
attendance_percentage DECIMAL(5,2)
    GENERATED ALWAYS AS (
        CASE
            WHEN total_learners > 0
            THEN ROUND(CAST(attendance_count AS DECIMAL(10,4)) / total_learners * 100, 2)
            ELSE NULL
        END
    ) STORED
```

Validacion QA esperada:

- `attendance_count=20`, `total_learners=25` debe calcular `80.00`.
- `total_learners=0` debe devolver `NULL` y no dividir por cero.

### AC-004 Arco exclusivo de `generated_alert`

Estado: IMPLEMENTADO EN DOMINIO Y BD.

Evidencia dominio:

```text
GeneratedAlertDraft rechaza affected_learner_id y affected_instructor_id simultaneos.
```

Evidencia BD:

```sql
CONSTRAINT ck_generated_alert_affected_actor_exclusive
CHECK (affected_learner_id IS NULL OR affected_instructor_id IS NULL)
```

Validacion QA esperada:

- Insertar alerta con ambos campos poblados debe fallar.
- Insertar alerta con uno solo o ninguno debe pasar si cumple las demas FK/campos obligatorios.

### AC-005 Catalogos sembrados

Estado: YA EXISTENTE EN `monitoring-db` / REQUIERE VALIDACION QA.

Evidencia encontrada en el repo:

```text
02_dml/00_inserts/001_seed_kpi_type.sql
02_dml/00_inserts/002_seed_risk_level.sql
02_dml/00_inserts/003_seed_kpi_status.sql
02_dml/00_inserts/004_seed_alert_type.sql
```

Catalogos esperados:

- `kpi_type`
- `alert_type`
- `risk_level`
- `kpi_status`

Validacion QA esperada:

```sql
SELECT code FROM monitoring.kpi_type ORDER BY code;
SELECT code FROM monitoring.alert_type ORDER BY code;
SELECT code FROM monitoring.risk_level ORDER BY priority_order;
SELECT code FROM monitoring.kpi_status ORDER BY code;
```

### AC-006 `SqlAlchemyKpiRepository` funcional

Estado: IMPLEMENTADO.

Evidencia:

- `save()` inserta en `monitoring.kpi_tracking`.
- `list_by_ficha()` consulta historico real por `ficha_id`.
- Usa transacciones.
- Maneja errores de persistencia.
- No usa datos en memoria.

Archivo principal:

```text
design-software-monitoring-service/src/monitoring/adapter/outbound/persistence/repo.py
```

### AC-007 Pruebas unitarias e integracion

Estado: PREPARADO / EJECUCION PENDIENTE EN ENTORNO CON PYTHON Y POSTGRESQL.

Evidencia:

```text
tests/test_record_kpi.py
tests/test_sqlalchemy_kpi_repository.py
```

Comandos sugeridos:

```powershell
python -m unittest discover -s tests -v

$env:MONITORING_TEST_DATABASE_URL="<postgres_url>"
python -m unittest discover -s tests -v
```

## Verificaciones ejecutadas

### 1. Validacion de whitespace service

Comando:

```powershell
git diff --check
```

Repositorio:

```text
design-software-monitoring-service
```

Resultado:

```text
PASS
```

Observacion:

Git informo conversion futura LF -> CRLF en archivos nuevos, sin errores de diff.

### 2. Validacion de whitespace db

Comando:

```powershell
git diff --check
```

Repositorio:

```text
design-software-monitoring-db
```

Resultado:

```text
PASS
```

### 3. Commit y push service

Comando ejecutado:

```powershell
git push -u origin hu-01-dev
```

Resultado:

```text
24eecde feat(monitoring): implement kpi persistence repository
branch 'hu-01-dev' set up to track 'origin/hu-01-dev'
```

Rama remota:

```text
origin/hu-01-dev
```

### 4. Commit y push db

Comando ejecutado:

```powershell
git push -u origin hu-09-dev
```

Resultado:

```text
09fa58d feat(monitoring-db): add kpi tracking persistence migrations
branch 'hu-09-dev' set up to track 'origin/hu-09-dev'
```

Rama remota:

```text
origin/hu-09-dev
```

### 5. Pruebas Python

Comando intentado:

```powershell
python -m unittest discover -s tests -v
```

Resultado:

```text
No ejecutado por limitacion del entorno local.
python.exe apunta al alias de Microsoft Store y devuelve:
"El sistema no tiene acceso al archivo"
```

Comando alterno intentado:

```powershell
py -m unittest discover -s tests -v
```

Resultado:

```text
No ejecutado: launcher py no instalado.
```

## Evidencia de ramas publicadas

```text
design-software-monitoring-service
Rama: hu-01-dev
Commit: 24eecde feat(monitoring): implement kpi persistence repository
URL PR sugerida por GitHub:
https://github.com/code-sena/design-software-monitoring-service/pull/new/hu-01-dev
```

```text
design-software-monitoring-db
Rama: hu-09-dev
Commit: 09fa58d feat(monitoring-db): add kpi tracking persistence migrations
URL PR sugerida por GitHub:
https://github.com/code-sena/design-software-monitoring-db/pull/new/hu-09-dev
```

## Observaciones tecnicas

- `sent_notification` no fue reintroducida ni usada por esta HU.
- En `monitoring-db` existe historial previo que crea `sent_notification`, pero tambien existe un changeset posterior que la elimina por ADR-005.
- Esta HU no modifica `design-software-docs`; solo toma `data-model.md`, ADR-004 y ADR-005 como fuente de validacion.
- La ejecucion de pruebas automatizadas queda pendiente para un entorno con Python 3.11+ y PostgreSQL disponible.
- La validacion Liquibase completa debe hacerse en QA/CI contra PostgreSQL real.

## Resultado QA sugerido

Estado: LISTO PARA PR HACIA `develop` Y VALIDACION TECNICA.

Los cambios necesarios para iniciar la validacion de HU-MON-001 quedaron implementados y subidos en:

- `design-software-monitoring-service` -> `hu-01-dev`
- `design-software-monitoring-db` -> `hu-09-dev`

QA y arquitectura deben validar:

- aplicacion Liquibase desde cero e incremental;
- rollback del changeset `990`;
- insercion real con `SqlAlchemyKpiRepository`;
- consulta real por ficha;
- append-only de `kpi_tracking`;
- calculo de `attendance_percentage`;
- arco exclusivo de `generated_alert`;
- seeds de catalogos;
- ausencia de dependencia sobre `sent_notification`.
