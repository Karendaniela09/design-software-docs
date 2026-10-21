# Evidencia R6 — ejecución 19/10/2026 16:03 (Colombia)

Fuente original: `EVIDENCIAS_R6_V4_FINAL.zip`, proporcionado por el aprendiz.
SHA-256 del ZIP original: `90d7ec38f95e1d6ab0816adfb9593849a51924288594096d680ac9de30da523b`.

Se conservaron los contenidos de los registros; solo se agregó `.txt` al final de nombres `.log` porque el repositorio ignora `*.log`.

**Resultados:** cuatro bases temporales PostgreSQL 16 aprobadas en SQL y Liquibase, con compilación Docker de backend Go y lectura HTTP real *después* de la migración. `develop`, `qa`, `staging` y `main` aquí son nombres de laboratorios aislados, **no los ambientes oficiales**.

**No demostrado:** v1/v2 de Go ejecutándose conjuntamente, continuidad mientras se ejecuta la migración bajo tráfico, ni rollbacks en los cuatro ambientes oficiales.

Archivos de mayor interés: `RESULTADO_FINAL.txt`, `00-backend-build.log.txt`, `*.04-expand-backfill.liquibase.log.txt`, `*.05-dual-write.sql.log.txt`, `*.06-contract.liquibase.log.txt`, `*.08-contract-rb.liquibase.log.txt`, `*.10-expand-rb.liquibase.log.txt`, `*.api.maintenance.log.txt`.
