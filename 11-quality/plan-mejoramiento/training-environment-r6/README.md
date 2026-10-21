# Training Environment — reto R6

> Estado: 🟡 En revisión | Última actualización: 2026-10-20  
> Autor: Juan Sebastián González Horta (`jsgh1`) | Equipo: Training Environment

## Contexto

Documenté la evolución de `training_environment.maintenance.reason` hacia `reason_detail`, con pruebas de migración, convivencia y rollback. El código ejecutable se mantiene en [Training Environment DB, PR #134](https://github.com/code-sena/design-software-training-environment-db/pull/134).

## Contenido

| Documento | Contenido |
|---|---|
| [ADR-017](../../../05-architecture/decisions/records/ADR-017-training-environment-r6-schema-evolution.md) | Justificación de EXPAND/BACKFILL/CONTRACT. |
| [Informe técnico](informe-tecnico-r6.md) | Migraciones, pruebas SQL y reversión. |
| [Informe de integración local](informe-integracion-local.md) | Web-shell, MFE, API Go y PostgreSQL. |
| [Matriz de verificación](matriz-verificacion.md) | Criterios R6, evidencias y límites. |
| [Evidencias](evidencias/README.md) | Salidas originales de las pruebas y capturas. |

## Referencias

- [PR #134: cambios R6 en la base de datos](https://github.com/code-sena/design-software-training-environment-db/pull/134).
- Acta 02 — Plan de mejoramiento ADSO 3145555.
