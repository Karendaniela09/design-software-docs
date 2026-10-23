# Evidencia ejecutada — CONTRACT desde la ruta final R6

> Corrida: `20261022_205431_503` | Fecha local: 22/10/2026 | Autor: `jsgh1`  
> Resultado observado: **PASS 4/4 — solo SQL/Liquibase en bases Docker efímeras**

## Paquete y procedencia

- [Descargar los 75 registros originales comprimidos](R6_20261022_205431_503_logs_completos.tar.xz) (`tar.xz`).
- [Resultado general](RESULTADO_FINAL.txt).
- [SHA-256 de scripts y commits utilizados](00-HASHES-Y-COMMITS.txt).
- Fuente del paquete: `EVIDENCIAS_R6_QA_FINAL.zip`, proporcionado después de ejecutar `VALIDAR_R6_QA_RUTA_FINAL_4_LABS_V3_LOGS.ps1` en Windows PowerShell.
- **SHA-256 ZIP original:** `c1de1ee36903b7bc98a09bd7e20615e5b4b7ed3aa3ff63088a5eb00cf115cb1f`.
- **SHA-256 `tar.xz` publicado:** `63d5bf50e0f5902bb737523c595f2e4454cda20294a1e54c7de0026bda2fb945`.
- Se compararon las **75 entradas** (ruta y bytes) del ZIP original y del `tar.xz`: coincidencia completa; el `tar.xz` es solo un formato alternativo para conservar íntegros los logs.

### Extraer en Windows

```powershell
tar -xJf .\R6_20261022_205431_503_logs_completos.tar.xz
```

Esto produce la carpeta `EVIDENCIAS_R6_RUTA_FINAL_20261022_205431_503`. Se recomienda revisar cada archivo de la secuencia y no basarse solamente en la etiqueta PASS.

## Revisión de cuatro laboratorios

| Log del paquete, por laboratorio | develop | qa | staging | main |
|---|---|---|---|---|
| `03-conteos-anteriores.txt` (filas, no nulos, nulos) | 4 / 3 / 1 | 4 / 3 / 1 | 4 / 3 / 1 | 4 / 3 / 1 |
| `04-expand-backfill.txt` (Liquibase 964+965) | PASS | PASS | PASS | PASS |
| `05-compatibilidad.txt` (SQL escrituras v1/v2, divergencia) | PASS | PASS | PASS | PASS |
| `05-conteos-expand.txt` (filas, detalle no nulo, divergencias) | 6 / 5 / 0 | 6 / 5 / 0 | 6 / 5 / 0 | 6 / 5 / 0 |
| `06-contract-ruta-final.txt` (changeset final 966) | PASS | PASS | PASS | PASS |
| `07-conteos-contract.txt` (filas, motivo no nulo) | 6 / 5 | 6 / 5 | 6 / 5 | 6 / 5 |
| `07-verificar-contract.txt` | PASS | PASS | PASS | PASS |
| `08-rollback-contract-ruta-final.txt` | PASS | PASS | PASS | PASS |
| `09-restauracion-trigger.txt` (función, trigger y SQL v1) | PASS | PASS | PASS | PASS |
| `09-verificar-rollback-contract.txt` | PASS | PASS | PASS | PASS |
| `10-rollback-expand-backfill.txt` | PASS | PASS | PASS | PASS |
| `11-verificar-rollback-total.txt` | PASS | PASS | PASS | PASS |

Los logs de CONTRACT registran explícitamente el changeset `changelog/changelog-r6-contract.yaml::r6-env-maintenance-reason-contract-v1::jsgh1`. Los de rollback registran ese mismo identificador, y los de rollback principal registran 965 y 964.

## Trazabilidad y límites

- ENV DB: `code-sena/design-software-training-environment-db` / `4640239879af14032abfcec10c0e641f20f607ff`.
- Docs al iniciar la ejecución: `59beebf62c02cfa8fa916fcb92928fe5f4dcbb29`.
- `develop`, `qa`, `staging`, `main` **son nombres de cuatro laboratorios Docker separados**; no equivalen a los entornos institucionales.
- `99-cleanup.txt` contiene mensajes de progreso de Docker tratados por PowerShell como `NativeCommandError`, pero también indica que el contenedor, volumen y red del proyecto correspondiente fueron eliminados. No hay base para afirmar una incidencia en Liquibase por estos mensajes.
- En la nueva ejecución **no se probó un binario Go v1/v2 por HTTP**; `SQL V1 OK` significa consultas SQL de compatibilidad, no una prueba HTTP.
- No se validó un despliegue real sin caída, outbox institucional ni entrega de una versión Go v2 institucional. CONTRACT debe permanecer separado del changelog principal.

## Vínculos

- [Matriz QA y comparación con pruebas de ruta antigua](../../matriz-qa-20261022.md).
- [README de reproducción](../../README-VALIDACION-R6.md).
- [PR ENV DB #134](https://github.com/code-sena/design-software-training-environment-db/pull/134).
- [PR Docs #337](https://github.com/code-sena/design-software-docs/pull/337).
