# Informe de validación integrada R1 — Academic Management

> Estado: 🟡 En progreso | Última actualización: 2026-10-20
> Autor: Jhon Camilo Suaza Sanchez | Equipo: Academic Management

## Contexto

Este informe registra la validación local de las ramas feature/r1-end-to-end-camilo-suaza. El entorno aislado camilo-r1-validation integró PostgreSQL, RabbitMQ, IAM, Reference Data, Academic API, Academic MFE y Web Shell.

> Alcance de la evidencia (2026-10-24): lo validado para el producto es el backend de R1 (outbox, confirmación del broker, recibo idempotente, DLQ y reproceso, rollback), que se entrega en `academic-management-db` (tabla `processed_event`) y `academic-management-service`. El recorrido por el Shell y el MFE usó un prototipo que pasaba `accessToken` por props y proxies fijos; ese enfoque quedó superado por [ADR-022](../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md) y [ADR-023](../05-architecture/decisions/records/ADR-023-web-shell-owns-login-and-session.md) (el Shell es dueño del login y entrega un `httpClient` a los remotes), y sus PR de frontend se cerraron. El perfil Docker usado para la prueba lo reemplaza el perfil `academic` de la tabla de rutas del edge (HU-SHELL-009).

## Resultado ejecutivo

Se aplicaron las migraciones oficiales de Reference Data (18 cambios), IAM (37) y Academic Management (31). IAM emitió un JWT real; Reference Data validó ese token y confirmó el centro activo; Academic API validó la firma mediante JWKS; el Shell entregó el token al MFE y el MFE consultó la API real.

Con RabbitMQ detenido, POST /api/v1/fichas creó la ficha R1-REAL-1986a0cf con HTTP 201. PostgreSQL conservó la ficha 6f812026-094a-476c-9907-ec8742a621f6 y el evento pendiente academic.ficha.opened con event_id 4c02425d-a9d4-4ee4-b546-9cbf5053c428. Se reinició Academic API mientras el broker seguía detenido. Al recuperar RabbitMQ, el evento quedó publicado, sin marca de DLQ, y con un único recibo. Una segunda entrega conservó el total en uno.

Una prueba adicional provocó un fallo controlado al guardar el evento en outbox. El POST devolvió 500 y se observaron cero filas tanto para la ficha como para el evento, confirmando el rollback. El elemento temporal se eliminó al finalizar.

## Matriz de requisitos

| Requisito | Evidencia local | Estado |
| --- | --- | --- |
| Parte 1, 6(a): DB, microservicio y MFE | Migraciones, API y MFE ejecutados con el perfil académico | Validado localmente |
| Parte 1, 6(b): MFE en Web Shell | Playwright abrió /academic-management/ y montó el remote | Validado localmente |
| Parte 1, 6(c): flujo sin mocks | IAM, JWKS, Reference Data, Academic API, PostgreSQL, RabbitMQ y MFE reales | Validado para fichas |
| Parte 1, 6(d): HU con PR fusionados | Los PR de backend se fusionan a `develop` por el flujo del proyecto; los de frontend se cerraron (ADR-023) | Ver «PR relacionados» |
| R1, 8(a): outbox transaccional | POST 201 con ficha y evento; rollback forzado con cero filas | Validado localmente |
| R1, 8(b): consumidor idempotente | Doble entrega del mismo event_id; processed_event=1 | Validado localmente |
| R1, 8(c): backoff, DLQ y reproceso | DLQ 1; reproceso autorizado: DLQ 0 y un recibo | Validado localmente |
| R1, 8(d): caos | Ficha con broker detenido, API reiniciada, recuperación y duplicado descartado | Validado localmente |

## Pruebas ejecutadas

Los scripts reproducibles están en design-software-academic-management-service/scripts:

- verify-r1-real-business-e2e.ps1
- verify-r1.ps1
- verify-r1-outbox-rollback.ps1

| Verificación | Resultado |
| --- | --- |
| Caos desde operación real | R1 REAL E2E APROBADO; publicado=t, recibos=1, duplicado=1 |
| Idempotencia, DLQ y reproceso | DLQ 1 → 0; processed_event=1 |
| Rollback transaccional | POST 500; fichas=0; outbox=0 |
| Shell con servicios reales | Playwright 1/1 |
| Regresión E2E Shell | Playwright 4/4 |
| Servicio | Maven 54 pruebas |
| Academic MFE | Vitest 85 pruebas y build Docker |
| Web Shell | Vitest 106 pruebas, typecheck y build |

La evidencia visual se centraliza en [la captura del Shell y la ficha](../assets/images/academic-r1-shell-ficha.png). El repositorio del micro conserva únicamente código, configuración, pruebas y scripts ejecutables.

## Componentes verificados

FichaController.create delimita la transacción; FichaService.create guarda la ficha y emite academic.ficha.opened; OutboxFichaEventPublisher y AcademicOutboxWriter guardan el evento. AcademicOutboxRelay espera confirmación del broker, reintenta y enruta a DLQ. AcademicR1EventConsumer registra el recibo único. AcademicDlqReprocessor y DlqController implementan el reproceso autorizado. La decisión se encuentra en [ADR-025](../05-architecture/decisions/records/ADR-025-academic-resilient-messaging.md).

En frontend, el prototipo definía `accessToken` en frontend-platform, el Web Shell lo entregaba al remote y Academic MFE lo enviaba como Bearer. Ese camino no entra al producto (ADR-023). La validación de autenticación vigente es la del login real del Shell.

## PR relacionados

| Repositorio | Estado |
| --- | --- |
| academic-management-service | PR #18 (outbox, confirmación, DLQ, reproceso y consumidor de referencia) |
| academic-management-db | PR #134 (tabla `processed_event`) |
| frontend-platform, academic-management-mfe, web-shell | PR #7, #13 y #16 cerrados: usaban `accessToken` por props (superado por ADR-023) |
| docker-infra | PR #41 cerrado: el perfil `academic` lo aporta HU-SHELL-009 (ADR-022) |
| docs | PR de esta documentación |

## Alcance

El resultado prueba localmente el recorrido académico de fichas y R1 A/B/C/D con las ramas combinadas, con el consumidor R1 encendido (`ACADEMIC_R1_CONSUMER_ENABLED=true`), que en el servicio viene apagado por defecto. No prueba todos los dominios ni producción. El recorrido por el Shell se repite contra el login real del Shell y el `httpClient` inyectado cuando existan esas piezas (ADR-023). El cambio pequeño en vivo se reserva para la sustentación.

## Referencias

- [ADR-025](../05-architecture/decisions/records/ADR-025-academic-resilient-messaging.md)
- code-sena/design-software-academic-management-service
- code-sena/design-software-docker-infra
