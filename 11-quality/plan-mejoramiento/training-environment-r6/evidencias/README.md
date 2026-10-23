# Evidencias de pruebas R6

> Estado: 🟡 En revisión | Última actualización: 2026-10-22  
> Autor: Juan Sebastián González Horta (`jsgh1`) | Equipo: Training Environment

## Contexto

Salidas originales de los ensayos del 19, 20 y 22 de octubre de 2026. Los nombres con hora corresponden a carpetas de ejecución locales. No se han convertido resultados de laboratorio en afirmaciones de despliegue institucional.

## Inventario

| Carpeta | Contenido |
|---|---|
| [validacion-ruta-final](validacion-ruta-final/README.md) | Ejecución final del 22/10: CONTRACT y rollback 4/4 desde changelog definitivo, 75 logs y hashes. |
| [20261019_160331](20261019_160331/README.md) | Cuatro bases, migración, CONTRACT y rollback. |
| [20261019_181957](20261019_181957/README.md) | Pruebas con servicio Go y convivencia de escrituras. |
| [20261019_200331](20261019_200331/README.md) | Verificación de rollback en cuatro bases Docker. |
| [20261019_213954](20261019_213954/README.md) | Pruebas de CONTRACT y restauración con v1/v2. |
| [20261020_integracion_web_shell](20261020_integracion_web_shell/README.md) | SQL y resultados de la integración local. |
| [pruebas-sql](pruebas-sql/README.md) | Copias de las cinco aserciones SQL del reto. |
| [contract-referencia](contract-referencia/README.md) | Referencia del CONTRACT originalmente ensayado. El código ejecutable permanece en ENV DB. |

## Trazabilidad para revisión de QA

La [matriz por ambiente](../matriz-qa-20261022.md) distingue los registros de CONTRACT/rollback con ruta antigua de la **nueva ejecución 4/4 con changelog definitivo**. Esta última tiene [índice y archivo integral verificado](validacion-ruta-final/README.md) y [guía de reproducción](../README-VALIDACION-R6.md). Los nuevos logs se recibieron tras una ejecución real; no se generaron resultados simulados.

## Capturas

- [Listado de ambientes](../../../../../assets/images/training-environment-r6/01-ambientes-web-shell.png).
- [Mantenimiento de Aula 101](../../../../../assets/images/training-environment-r6/02-mantenimiento-aula-101.png).

## Referencias

- [Informe técnico](../informe-tecnico-r6.md).
- [Matriz de verificación](../matriz-verificacion.md).
