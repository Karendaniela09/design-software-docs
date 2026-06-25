# Aspectos transversales

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

## Contexto

Este documento describe los aspectos transversales del sistema **Horarios SENA**: seguridad, logging, auditoría, manejo de errores, validación y monitoreo. Estos aspectos aplican a todos los microservicios y capas del sistema, garantizando consistencia, trazabilidad y resiliencia.

---

## Seguridad

### Autenticación y Autorización

| Aspecto | Implementación |
|---------|----------------|
| **Autenticación** | JWT (JSON Web Token) generado por Spring Security. |
| **Autorización** | RBAC (Role-Based Access Control) con anotaciones `@PreAuthorize`. |
| **Roles** | `ROLE_COORDINADOR`, `ROLE_INSTRUCTOR`, `ROLE_ADMIN`. |
| **Permisos** | Ejemplo: `@PreAuthorize("hasRole('ADMIN') or hasRole('COORDINADOR')")`. |
| **Almacenamiento de contraseñas** | BCrypt (hash + salt). |

### Protección contra vulnerabilidades

| Vulnerabilidad | Medida de protección |
|----------------|----------------------|
| **SQL Injection** | Uso de JPA/Hibernate con parámetros bind (`@Query` con `?1`, `:name`). |
| **XSS (Cross-Site Scripting)** | Spring Security escapa la salida por defecto; validación de entrada. |
| **CSRF** | Deshabilitado para APIs REST (se usa JWT, no cookies de sesión). |
| **CORS** | Configuración restrictiva (solo orígenes autorizados). |
| **Exposición de errores** | `GlobalExceptionHandler` que no expone stack traces al cliente. |

---

## Logging

### Configuración

- **Framework:** SLF4J + Logback.
- **Niveles:** DEBUG (desarrollo), INFO (producción), WARN, ERROR.
- **Formato:** JSON estructurado (para facilitar la ingesta en herramientas de monitoreo como ELK o Datadog).

### Ejemplo de log estructurado

```json
{
  "timestamp": "2026-06-24T10:30:00.123Z",
  "level": "INFO",
  "service": "scheduling-service",
  "correlation_id": "abc-123-def",
  "user_id": "coordinator_001",
  "message": "Horario creado exitosamente",
  "schedule_id": "123e4567-e89b-12d3-a456-426614174000"
}