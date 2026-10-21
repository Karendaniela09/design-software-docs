# Estado de la entrega local R3 — corte de QA

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

## Contexto

El archivo completo de evidencias de ejecución es local, bajo `EVIDENCIAS-PLAN-MEJORAMIENTO-R3/` en la raíz del workspace. Las rutas de esta matriz son relativas a esa carpeta salvo los enlaces a documentos.

Se usa la **última ejecución disponible de cada criterio**, con fecha y alcance explícitos. No se combinan intentos anteriores fallidos para fabricar un resultado aprobado. Una consulta de GitHub o una revisión documental no cuentan como una nueva ejecución E2E. Las observaciones de telemetría del 19 de octubre se conservan con esa fecha: no certifican una repetición con los heads actuales ni un arranque desde ramas fusionadas. La última suite backend y las últimas pruebas de dominios son las salidas concretas indicadas abajo.

## Últimas ejecuciones

Consultar la [matriz final](matriz-final.md) y la sección 9 del [informe técnico](informe-tecnico.md). La última suite backend informa 34 passed; el último escenario Scheduling conserva status=passed. No se ejecutó nuevamente el stack completo durante esta corrección documental.

## HU externas

| HU externa | Issue | Estado remoto | Evaluación del plan |
|---|---|---|---|
| HU-INT-MON-001 | [#322](https://github.com/code-sena/design-software-docs/issues/322) | OPEN | PARCIAL |
| HU-INT-MON-002 | [#323](https://github.com/code-sena/design-software-docs/issues/323) | OPEN | PARCIAL |
| HU-INT-MON-003 | [#324](https://github.com/code-sena/design-software-docs/issues/324) | OPEN | PARCIAL |
| HU-INT-MON-004 | [#325](https://github.com/code-sena/design-software-docs/issues/325) | OPEN | PARCIAL |

## Pull Requests

Consulta: `2026-10-20T17:05:38-05:00`; identidad autenticada: `Andrey31072`.

| Repositorio | PR | Estado real | Borrador | Rama de origen | Head consultado |
|---|---|---|---|---|---|
| monitoring-service | [#6](https://github.com/code-sena/design-software-monitoring-service/pull/6) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `71a0778e9459` |
| monitoring-mfe | [#8](https://github.com/code-sena/design-software-monitoring-mfe/pull/8) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `811be35abdcf` |
| web-shell | [#14](https://github.com/code-sena/design-software-web-shell/pull/14) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `85b2c567bf42` |
| docker-infra | [#39](https://github.com/code-sena/design-software-docker-infra/pull/39) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `b8a99f08f8cd` |
| academic-management-service | [#17](https://github.com/code-sena/design-software-academic-management-service/pull/17) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `1d75bd2b32b1` |
| actors-db | [#65](https://github.com/code-sena/design-software-actors-db/pull/65) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `ac87ccccf928` |
| actors-service | [#28](https://github.com/code-sena/design-software-actors-service/pull/28) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `1348b45dc59d` |
| scheduling-service | [#16](https://github.com/code-sena/design-software-scheduling-service/pull/16) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `e806ab759d7b` |
| notification-service | [#11](https://github.com/code-sena/design-software-notification-service/pull/11) | OPEN | No | `hu-kevin-culma-r3-observabilidad` | `4094b1a2b3e0` |
| docs | [#331](https://github.com/code-sena/design-software-docs/pull/331) | OPEN | Sí | `fix/r3-observability` | `f0737d75dabd` |

## Checks del head consultado

| Repositorio | Check | Resultado | Enlace |
|---|---|---|---|
| monitoring-service | test | completed: success | [Actions](https://github.com/code-sena/design-software-monitoring-service/actions/runs/39496316883/job/118882172458) |
| monitoring-mfe | — | Sin check-runs publicados en este head; no implica aprobado | — |
| web-shell | — | Sin check-runs publicados en este head; no implica aprobado | — |
| docker-infra | — | Sin check-runs publicados en este head; no implica aprobado | — |
| academic-management-service | — | Sin check-runs publicados en este head; no implica aprobado | — |
| actors-db | — | Sin check-runs publicados en este head; no implica aprobado | — |
| actors-service | verify | completed: failure | [Actions](https://github.com/code-sena/design-software-actors-service/actions/runs/39496330630/job/118882249597) |
| actors-service | Maven test and verify | completed: failure | [Actions](https://github.com/code-sena/design-software-actors-service/actions/runs/39496330648/job/118882220858) |
| scheduling-service | build | completed: failure | [Actions](https://github.com/code-sena/design-software-scheduling-service/actions/runs/39496338860/job/118882249170) |
| scheduling-service | build | completed: failure | [Actions](https://github.com/code-sena/design-software-scheduling-service/actions/runs/39496331481/job/118882223297) |
| notification-service | — | Sin check-runs publicados en este head; no implica aprobado | — |
| docs | — | Sin check-runs publicados en este head; no implica aprobado | — |

## Pendientes

- Acceso y validación del IdP institucional.
- HU externas OPEN y checks fallidos de Actors/Scheduling.
- Repetición del arranque limpio y provisionamiento sobre las ramas efectivamente fusionadas.
- Práctica personal de sustentación y ejercicios. La guía privada permanece fuera de los repositorios.
- Los PR se mantienen sin fusionar por instrucción del usuario.

## Referencias

- [Procedimiento con repositorios compartidos](README.md#reproducción-local-desde-un-checkout-limpio).
- [Matriz final](matriz-final.md).

PR documental anterior: [#330](https://github.com/code-sena/design-software-docs/pull/330), **CLOSED**, sin fusionar; sustituido por el PR de `fix/r3-observability`.

Selección de evidencias para la entrega: [informe técnico breve](informe-tecnico-breve.md). Los SHA de la tabla corresponden al corte anterior a esta publicación documental.
