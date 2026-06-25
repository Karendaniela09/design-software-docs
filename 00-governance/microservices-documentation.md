
```markdown
# Documentación de microservicios

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

Este documento define cuándo y cómo registrar documentación de microservicios en el proyecto **Horarios SENA**. Los microservicios se implementan con **Spring Boot 3 + Java 21** y se comunican mediante REST APIs documentadas con **SpringDoc OpenAPI**.

## Regla crítica

No crear carpetas en `09-microservices/services/` hasta que el servicio exista en el repositorio de código o su creación esté formalmente aprobada por arquitectura.

No crear microservicios ficticios para llenar la estructura.

**Requisito de aprobación:** Todo servicio nuevo debe tener una ADR en `05-architecture/decisions/records/` o una decisión registrada en `15-project-control/open-questions.md` con estado RESUELTA antes de crear la carpeta en `09-microservices/services/`. Sin ese artefacto, el PR será rechazado.

## Ubicación

Cada servicio real se documenta en:

```text
09-microservices/services/<nombre-del-servicio>/
El nombre de la carpeta debe coincidir con el nombre del repositorio de código y con el nombre del artefacto en el pom.xml (para Spring Boot).

Flujo
1. Verificar catálogo
Abrir 09-microservices/service-catalog.md y confirmar que el servicio no exista.

2. Copiar plantilla
bash
cp -r 09-microservices/_template/ 09-microservices/services/<nombre-servicio>/
Ejemplo ilustrativo, no crear sin aprobación:

bash
cp -r 09-microservices/_template/ 09-microservices/services/scheduling-service/
3. Completar README del servicio
El README.md del servicio debe incluir:

Responsabilidad del servicio.

Bounded context.

Owner.

Repositorio de código (URL en GitHub).

Dependencias (qué otros servicios consume).

Enlaces a contrato API, modelo de datos, eventos y runbook.

4. Registrar en catálogo
Agregar fila en 09-microservices/service-catalog.md:

markdown
| scheduling-service | Motor de asignación de horarios | Equipo ADSO | [repo](https://github.com/...) | 🟡 |
5. Completar archivos mínimos
Archivo	Qué documentar
README.md	Responsabilidad, owner, dependencias y links
api-contract.md	Endpoints REST, request/response DTOs, códigos de error (usar SpringDoc OpenAPI)
data-model.md	Modelo transaccional propio del servicio (entidades JPA, tablas PostgreSQL)
events.md	Eventos publicados y consumidos (si usa mensajería)
runbook.md	Deploy, rollback, variables de entorno y troubleshooting
README.md y api-contract.md deben estar al menos en 🟡 antes del primer merge a main del código del servicio.

Commits
Usar Conventional Commits en inglés:

bash
git checkout -b feat/doc-service-scheduling
git add 09-microservices/services/scheduling-service/
git add 09-microservices/service-catalog.md
git commit -m "docs(09-microservices): register scheduling-service"
git push origin feat/doc-service-scheduling
Si se documentan varios servicios, usar un commit por microservicio cuando sea posible.

Contrato API
09-microservices/services/<servicio>/api-contract.md describe el contrato operativo del servicio (endpoints, ejemplos).

07-api/contracts/openapi/ almacena archivos OpenAPI formales (<servicio>.yaml) generados con SpringDoc.

Mantener enlaces cruzados entre ambos cuando aplique.

Tecnologías por servicio
Cada microservicio usará:

Java 21 LTS

Spring Boot 3 (Web, Data JPA, Security, Actuator)

PostgreSQL 16 (cada servicio con su propio esquema)

Flyway para migraciones

SpringDoc OpenAPI para documentación de API

SLF4J + Logback para logging