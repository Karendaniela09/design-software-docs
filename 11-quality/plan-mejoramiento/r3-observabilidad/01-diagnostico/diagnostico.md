# Diagnóstico inicial — 19 de octubre de 2026

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

Inspección del workspace `C:/sena/Micro Horario`. Se encontraron 39 repositorios; todos estaban sincronizados con sus ramas remotas actuales antes de iniciar este reto. El cambio previo en `design-software-iam-mfe/vite.config.ts` (`dts: false`) se conserva fuera del alcance. No había contenedores activos al consultar `docker ps`.

| Componente | Tecnología encontrada | Estado inicial y dependencias |
|---|---|---|
| monitoring-service | Python >=3.11, FastAPI >=0.115, SQLAlchemy >=2, psycopg3, Pika, pytest, Ruff | develop `1c84fd3`; API y worker existentes; OTEL parcial, sin Dockerfile; requiere PostgreSQL y RabbitMQ para readiness |
| monitoring-db | PostgreSQL 16, Liquibase, SQL y changelog YAML | develop `c118a04`; catálogos, seguimiento, KPIs particionados, alertas y outbox; migraciones todavía sin ejecutar en el entorno R3 |
| monitoring-mfe | React 18, TypeScript 5, Vite 8, Module Federation, Vitest | rama inicial fix/conection-backend-frontend `bd7bbe6`; develop remoto contiene además adopción de tokens; cliente HTTP inyectado por shell |
| web-shell | React 18, Vite 7, Federation, frontend-platform, Playwright | rama inicial fix/conection-backend-frontend `d91050f`; datos de Monitoring y contexto de usuario escritos como fixtures; HTTP dirigido al BFF local |
| docker-infra | Compose, PostgreSQL, RabbitMQ, Collector 0.109, Tempo 2.6, Prometheus 2.54, Grafana 11.2, Loki 3.2 | rama inicial fix/conection-backend-frontend `7e7fb1f`; perfil monitoring inexistente; perfil observability disponible; sin dashboard/alerta R3 |
| web-bff | Node/TypeScript, servidor HTTP nativo | rama fix/conection-backend-frontend `8f4f9ea`; devuelve arrays en memoria para Monitoring; no demuestra persistencia |
| docs | Markdown, OpenAPI, ADR-008 | main `e1d9b06`; contrato Monitoring y runbook actualizados; no tiene develop |

Se crearon ramas `hu-kevin-culma-r3-observabilidad` desde `origin/develop` en service, MFE, shell e infraestructura. Se preservan ramas protegidas; no se modifican commits ajenos. Base de datos y documentación central se inspeccionan sin modificarlas salvo necesidad demostrada.

Hallazgos: exportadores OTLP de señales diferentes compartían una URL sin sufijo; logs omitían campos HTTP aunque el middleware los enviaba; correlation_id entrante no se validaba; contexto de correlación no alcanzaba logs internos; faltaban spans del navegador y métricas RED explícitas. El composition root utilizaba decodificación JWT sin verificar firma. Los catálogos cerrados del backend son paginados, mientras que el adaptador MFE esperaba arrays. La prueba denominada `test_monitoring_e2e.py` utiliza repositorio y API falsos: se considera prueba unitaria de orquestación, no evidencia E2E real.

| Criterio | Estado inicial | Componente | Acción requerida | Evidencia prevista |
|---|---|---|---|---|
| P1-A | PENDIENTE | infra/db/service/mfe | perfil oficial, migraciones, inicio y readiness | Compose ps, logs, SQL |
| P1-B | PARCIAL | shell/mfe | dirigir cliente al backend, quitar fixtures | captura y prueba Playwright |
| P1-C | PENDIENTE | todo el flujo | creación desde interfaz y consulta PostgreSQL | HTTP, fila persistida, captura |
| P1-D | PENDIENTE | docs/GitHub | consultar HU y PR reales | consulta remota con estado y fecha |
| R3-A1/A2/A3/A4 | PARCIAL | mfe/service/db/Tempo | spans frontend, contexto W3C y exportación correcta | misma traza con span SQL |
| R3-B1/B2/B3 | PENDIENTE | service/Collector/Prometheus | contador e histograma por ruta | consultas y tráfico real |
| R3-C1/C2/C3 | PARCIAL | service/Loki | JSON completo, validación y contexto concurrente | tests, logs reales correlacionados |
| R3-D1/D2/D3/D4 | PENDIENTE | infra/Grafana | dashboard y alerta declarativos; disparo y recuperación | API y capturas |
| ADR/informe/guía | PENDIENTE | service/docs | describir exclusivamente implementación validada | archivos finales y matriz |

Riesgos: login IAM depende de componentes y TLS externos al dominio; se debe distinguir la identidad firmada del entorno de pruebas de una validación del login institucional. Las migraciones usan nombres globales de roles y requieren un PostgreSQL aislado. Las dependencias tenían rangos abiertos: validar versiones realmente resueltas y conservar locks. GitHub CLI no estaba instalado inicialmente; acceso a tablero y publicación deben comprobarse. No se atribuye HU-MON-008 a Kevin ni se cierran HU por documentación.

Archivos previstos: observability.py, composition root API, verificación JWT, Dockerfile; cliente MFE e instrumentación; cliente y sesión shell; Compose, scripts de inicio, dashboard/datasources/alertas; pruebas y evidencias. Pruebas disponibles: pytest unitario y PostgreSQL condicionado a variable de entorno; Vitest MFE y shell; Playwright shell. Las pruebas reales nuevas se ejecutarán sobre el proyecto Compose `ds-monitoring-r3`, sin mocks ni modificaciones de bases compartidas.
