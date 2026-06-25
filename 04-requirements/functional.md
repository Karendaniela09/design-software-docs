# Requisitos no funcionales

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

## Contexto

Este documento lista los requisitos no funcionales del sistema **Horarios SENA**. Estos requisitos definen atributos de calidad, seguridad, rendimiento, disponibilidad y operación que el sistema debe cumplir.

## Convención de identificadores

- **RNF-XXX:** Requisito No Funcional
- **Prioridad:** Alta (A), Media (M), Baja (B)

---

## Arquitectura y calidad del código

| ID | Requisito | Prioridad | Verificación |
|----|-----------|-----------|--------------|
| RNF-001 | El sistema debe seguir una arquitectura limpia (Clean Architecture) con separación de capas: domain, application, infrastructure, transport. | A | Revisión de código y estructura de carpetas. |
| RNF-002 | El sistema debe estar dividido en microservicios independientes, cada uno con su propia base de datos. | A | Verificación de la arquitectura de microservicios. |
| RNF-003 | El código debe cumplir con los estándares de codificación definidos en `coding-standards.md` (Java 21, Spring Boot). | A | Revisiones de código automáticas y manuales. |
| RNF-004 | Ningún archivo fuente debe exceder las 300 líneas (excepto archivos generados automáticamente). | M | Análisis estático con herramientas como SonarQube. |

---

## Seguridad

| ID | Requisito | Prioridad | Verificación |
|----|-----------|-----------|--------------|
| RNF-005 | Todas las comunicaciones entre frontend y backend deben usar HTTPS. | A | Verificación de configuración de TLS/SSL. |
| RNF-006 | El sistema debe usar JWT para autenticación y autorización. | A | Pruebas de autenticación. |
| RNF-007 | Los roles y permisos deben estar definidos y validados en cada endpoint. | A | Pruebas de autorización para cada rol. |
| RNF-008 | Las contraseñas de los usuarios deben almacenarse usando un algoritmo de hash seguro (BCrypt). | A | Revisión de implementación de hash. |
| RNF-009 | Los campos de PII (nombre, email, documento) deben estar cifrados en reposo (PostgreSQL pgcrypto o aplicación). | A | Verificación de cifrado en la base de datos. |
| RNF-010 | Los errores internos del servidor no deben exponer stack traces al cliente. | A | Pruebas de respuesta de errores 500. |
| RNF-011 | Todas las acciones críticas (crear, modificar, eliminar) deben registrarse en auditoría (tabla `audit_log`). | A | Verificación de logs de auditoría. |
| RNF-012 | El sistema debe prevenir inyección SQL usando JPA/Hibernate con parámetros bind. | A | Revisión de código y pruebas de seguridad. |
| RNF-013 | El sistema debe tener CORS configurado de forma restrictiva (solo orígenes autorizados). | A | Verificación de configuración de CORS. |
| RNF-014 | Los tokens JWT deben expirar después de 8 horas. | A | Pruebas de expiración de tokens. |

---

## Rendimiento y escalabilidad

| ID | Requisito | Prioridad | Verificación |
|----|-----------|-----------|--------------|
| RNF-015 | El tiempo de respuesta de las APIs debe ser inferior a 2 segundos en condiciones normales de carga. | A | Pruebas de carga con herramientas como JMeter. |
| RNF-016 | La validación de conflictos de horario debe ejecutarse en menos de 500 ms. | A | Pruebas de rendimiento específicas para el motor de horarios. |
| RNF-017 | El sistema debe soportar al menos 1000 usuarios concurrentes en operación normal. | M | Pruebas de escalabilidad. |
| RNF-018 | El sistema debe estar diseñado para escalar horizontalmente (múltiples instancias de microservicios). | M | Revisión de arquitectura y configuración. |

---

## Base de datos

| ID | Requisito | Prioridad | Verificación |
|----|-----------|-----------|--------------|
| RNF-019 | El sistema debe usar PostgreSQL 16 o superior como motor de base de datos. | A | Verificación de versión en entorno de desarrollo/producción. |
| RNF-020 | Cada microservicio debe tener su propio esquema de base de datos. | A | Verificación de separación de datos. |
| RNF-021 | Los índices necesarios para las consultas más frecuentes deben estar creados (ej. `schedule.instructor_id`, `schedule.start_time`). | A | Revisión de scripts de migración (Flyway). |
| RNF-022 | Las migraciones de base de datos deben gestionarse con Flyway y ser idempotentes. | A | Verificación de ejecución de migraciones. |
| RNF-023 | Se deben realizar backups diarios de la base de datos (RPO: 24 horas). | M | Verificación de política de backups. |

---

## Disponibilidad y recuperación

| ID | Requisito | Prioridad | Verificación |
|----|-----------|-----------|--------------|
| RNF-024 | El sistema debe tener un healthcheck endpoint (`/actuator/health`) que verifique la conexión a la base de datos y otros servicios. | A | Pruebas de healthcheck en Docker Compose. |
| RNF-025 | El tiempo máximo de inactividad planificada (RTO) debe ser inferior a 4 horas. | M | Plan de recuperación documentado. |
| RNF-026 | En caso de fallo, el sistema debe poder restaurarse desde el último backup (RPO: 24 horas). | M | Pruebas de restauración. |

---

## Usabilidad y experiencia de usuario

| ID | Requisito | Prioridad | Verificación |
|----|-----------|-----------|--------------|
| RNF-027 | La interfaz de usuario debe estar en español. | A | Revisión de textos y etiquetas en el frontend. |
| RNF-028 | La interfaz debe ser responsiva (soportar dispositivos móviles, tablets y escritorio). | A | Pruebas en diferentes tamaños de pantalla. |
| RNF-029 | Los mensajes de error deben ser claros y orientados al usuario (no técnicos). | A | Pruebas de validación de formularios. |
| RNF-030 | La aplicación debe cargarse en menos de 3 segundos en condiciones normales. | M | Pruebas de rendimiento del frontend. |

---

## Mantenibilidad y documentación

| ID | Requisito | Prioridad | Verificación |
|----|-----------|-----------|--------------|
| RNF-031 | La API debe estar documentada con OpenAPI (Swagger) usando SpringDoc. | A | Verificación de acceso a `/swagger-ui.html`. |
| RNF-032 | Todo el código debe estar comentado en inglés (cuando sea necesario). | M | Revisión de código. |
| RNF-033 | El repositorio de documentación debe mantenerse actualizado con la estructura definida en `CONTRIBUTING.md`. | A | Revisión de PRs. |

---

## Pruebas

| ID | Requisito | Prioridad | Verificación |
|----|-----------|-----------|--------------|
| RNF-034 | El sistema debe incluir pruebas unitarias para la capa de dominio y servicios (JUnit 5 + Mockito). | A | Ejecución de `mvn test`. |
| RNF-035 | El sistema debe incluir pruebas de integración con Testcontainers para la capa de repositorios. | A | Ejecución de pruebas de integración. |
| RNF-036 | La cobertura de código debe ser al menos del 80% en la capa de servicio y dominio (medida con JaCoCo). | A | Verificación de informes de JaCoCo. |
| RNF-037 | Se deben ejecutar pruebas de aceptación para los flujos críticos (ej. creación de horario con conflicto). | A | Pruebas automáticas y manuales. |
| RNF-038 | El sistema debe pasar las pruebas de seguridad (OWASP Top 10) antes del despliegue. | A | Reporte de AppSec. |

---

## Despliegue y operación

| ID | Requisito | Prioridad | Verificación |
|----|-----------|-----------|--------------|
| RNF-039 | El sistema debe desplegarse usando Docker Compose (3 servicios: backend, frontend, base de datos). | A | Ejecución de `docker compose up`. |
| RNF-040 | Las variables de entorno deben configurarse en un archivo `.env` (ejemplo en `.env.example`). | A | Verificación de archivos de configuración. |
| RNF-041 | El sistema debe tener logs estructurados (SLF4J + Logback) con niveles (DEBUG, INFO, WARN, ERROR). | A | Verificación de logs en entorno de desarrollo. |
| RNF-042 | El sistema debe incluir un plan de despliegue y rollback documentado. | M | Revisión de `deployment-plan.md` y `rollback-plan.md`. |

---

## Referencias

- [functional.md](./functional.md) — Requisitos funcionales
- [user-stories.md](./user-stories.md) — Historias de usuario
- [traceability-matrix.md](./traceability-matrix.md) — Matriz de trazabilidad
- [05-architecture/](../05-architecture/) — Arquitectura del sistema
- [10-devops/](../10-devops/) — Despliegue y operación