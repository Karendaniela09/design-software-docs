# Informe de integración local — Training Environment

> Estado: 🟡 En revisión | Última actualización: 2026-10-20  
> Autor: Juan Sebastián González Horta (`jsgh1`) | Equipo: Training Environment

## Contexto

Comprobé el flujo de lectura y alta de mantenimiento desde el web-shell hasta PostgreSQL en un entorno local con la migración EXPAND/BACKFILL R6 aplicada.

## Prueba funcional

El web-shell cargó el microfrontend `trainingEnvironmentMfe` mediante Module Federation. La pantalla listó tres ambientes consultados desde la API Go: Taller de Soldadura, Aula 101 y Laboratorio de Redes.

Desde Aula 101 se registró un mantenimiento para el **16 de noviembre de 2026, 14:00–15:00**, con el motivo `PRUEBA_UI_R6_20261020 - Integración real web-shell Go PostgreSQL`. La consulta SQL posterior confirmó el registro, `reason = reason_detail`, `r6_sync = OK` y la existencia del evento `environment.maintenance.started` en el outbox local.

Las suites de frontend finalizaron con **83 pruebas MFE** y **106 del web-shell** aprobadas. Se verificó `remoteEntry.js` con HTTP 200 y 33 changesets aplicados a la copia aislada de PostgreSQL.

## Alcance

La sesión visible del shell fue de prueba y Go recibió un JWT de laboratorio. La tabla `outbox` se creó como infraestructura auxiliar de la prueba: no está incluida como migración oficial en el PR #134. Solo se verificaron el listado de ambientes y la creación de mantenimiento. Las correcciones locales del frontend utilizadas para el ejercicio no forman parte de este PR de base de datos.

El experimento acredita integración funcional local de ese recorrido; no certifica las demás HU ni un despliegue institucional.

## Evidencias

- [Resultados SQL del mantenimiento](evidencias/20261020_integracion_web_shell/03_verificacion_SQL.txt).
- [Resultados de validación](evidencias/20261020_integracion_web_shell/04_resultados_validacion.txt).
- [Capturas](../../../../assets/images/training-environment-r6/README.md).
- [Matriz de verificación](matriz-verificacion.md).
