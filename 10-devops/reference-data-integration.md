# Plan de integración real de Reference Data — HU-REF-020 y R1

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Valery Sinai Trujillo Quintero | Equipo: Reference Data

## Contexto

Esta entrega adapta el trabajo individual a los repositorios originales del macroproyecto. El plazo comunicado es 2026-10-20 a las 18:00, Colombia. No basta una rama personal ni un PR pendiente para acreditar integración en develop. Los ADR/informes pertenecen exclusivamente a docs, que tiene flujo rama hija → PR → main.

## Contenido

### Secuencia y responsabilidad

1. Preparar docs desde `origin/main`: ADR-020/021, HU/trazabilidad, modelo/diccionario y criterios de prueba. Mantener estado en revisión, sin fingir aprobación.
2. Adaptar código desde `origin/develop` en cada repositorio afectado, preservando cambios de compañeros. No copiar ramas completas, README/PROCEDENCIA, ADR, informes ni capturas de las copias personales a los repositorios de código.
3. Aplicar nuevos changesets en la base de validación; comprobar primero backend, luego remote dentro del shell y caos.
4. Registrar SHA, comandos y resultados del macroproyecto en docs. Solicitar validación de QA/Arquitectura mediante el flujo autorizado; publicar PR originales y verificar su merge a develop con una cuenta con permisos.
5. No actualizar board/hu-log como Done·Dev sin pruebas, aprobación, migración al develop correspondiente y merge originales. Documentar diferencias entre ejecución aislada y ambiente compartido.

| Repositorio | Cambio previsto |
|---|---|
| reference-data-service | Alias HU-REF-020, pruebas reales, consumidor/inbox, retry/DLQ/replay e integración del worker |
| reference-data-db | DDL y grants nuevos de inbox/proyección, rollback y pruebas SQL; sin alterar changesets existentes |
| iam-db | Preparación de usuarios de prueba reproducibles y guardas de aislamiento; sin passwords fijas |
| docker-infra | Compose, scripts y verificadores aislados que apuntan a las fuentes del macroproyecto |
| frontend-platform | Login/identidad real y puerto HTTP tipado para el remote; sin dependencia de React |
| reference-data-mfe | Consumir fachada compartida mediante React Context por instancia; sin fetch de negocio directo ni tokens globales |
| web-shell | Entrada real de sesión, features/client inyectados y federación/configuración local del dominio |
| IAM Service, design-system y BFF | Reutilizar; modificar solo si las pruebas originales demuestran una necesidad concreta |

### Disposición local y variables

El macroproyecto separa los proyectos comunes de frontend (web-shell, frontend-platform, design-system) de `reference-data/` (servicios, MFE, database e infra). Los runners deben resolver estas rutas desde su propia ubicación y admitir variables de configuración; no versionar rutas absolutas de un computador. `WORKSPACE_ROOT` representa la raíz Reference Data; los paquetes comunes se localizan mediante una raíz frontend independiente. Las credenciales se generan localmente en archivos ignorados.

### Ejecución local validada

Con el código adaptado, desde la raíz de docker-infra:

```powershell
./validation/frontend-reference/run.ps1
```

El runner debe preparar el stack real, esperar endpoints, ejecutar integración Go y Chromium y fallar ante cualquier caso omitido/fallido. Con backend ya preparado, se admite `-SkipBackendPreparation`; `-PrepareOnly` levanta pantallas pero no acredita validación. El resultado `passed` solo se escribe tras todos los checks.

El perfil local de Reference Data mantiene red/volúmenes y proyecto Compose propios. La ejecución `macro-ref-r1` usa shell 5010, remote 5115, IAM 18102, Reference Data 18100 y PostgreSQL 15440; comprobar colisiones antes de arrancar y no detener servicios de compañeros. El acceso de debug es loopback; el despliegue general sigue ADR-007/Traefik.

Resultados locales: integración Go obligatoria y tres casos Chromium PASS; suite R1 completa PASS. Ver [evidencia y SHA base](../11-quality/reference-data-hu-ref-020-r1-validation.md). La ejecución local no acredita aprobación ni merge.

### Gobierno y evidencia actual (2026-10-24)

Los runners permanecen como herramientas versionadas de validación aislada, ya ejecutadas desde el CI del shell. Su permanencia como gate oficial del macroproyecto, mantenimiento y frecuencia de ejecución siguen propuestos a Arquitectura/DevOps en ADR-020. No se presume adopción transversal ni despliegue productivo.

Frontend Platform tiene CI propio aprobado; el shell tiene CI completo aprobado sobre e91a2c0, pero requiere resolver un conflicto posterior con develop y repetir CI si cambia el HEAD. El MFE tiene 71 pruebas locales; su CI propio sigue bloqueado por SHELL_DEPS_TOKEN. Ambos PR de DB ya existen. Ver [tabla de SHA, runs y dependencias](../11-quality/reference-data-hu-ref-020-r1-validation.md).

La custodia del secreto y el orden de integración están propuestos en ADR-020; ownership de inbox/proyección, retención y operación de RabbitMQ en ADR-021. Los responsables deben ajustar las referencias CI de ramas efímeras a revisiones/develop aprobados antes de borrar ramas ya integradas.

### Revisión y promoción

Un resultado técnico verde no reemplaza QA/Arquitectura ni su aprobación. La cuenta conectada se consulta antes de publicar: si solo tiene lectura en la organización, conservar rama/commits y preparar un parche o contribución revisable sin afirmar merge. La integración final requiere una cuenta autorizada; no forzar push, eludir protección ni reportar por Discord desde esta tarea.

## Referencias

- [ADR-020](../05-architecture/decisions/records/ADR-020-reference-data-iam-e2e-integration.md), [ADR-021](../05-architecture/decisions/records/ADR-021-reference-data-resilient-messaging.md).
- [DoD](../00-governance/definition-of-done.md), [Git](../00-governance/git-conventions.md), [criterios de prueba](../11-quality/reference-data-hu-ref-020-r1-validation.md).
