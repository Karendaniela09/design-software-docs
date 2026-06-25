# Normas de diseño de API

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Backend

## Contexto

Este documento define las convenciones para el diseño de las APIs REST del sistema **Horarios SENA**. Todas las APIs deben seguir estas normas para garantizar consistencia, mantenibilidad y una buena experiencia de desarrollo.

## Principios generales

- **RESTful:** Uso de recursos, métodos HTTP y códigos de estado estándar.
- **Stateless:** Cada petición contiene toda la información necesaria (JWT en header).
- **Versionado:** Las APIs se versionan para permitir evolución sin romper consumidores.
- **Documentadas:** Todas las APIs están documentadas con OpenAPI (SpringDoc).

## Nomenclatura

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| **Recursos** | Sustantivos en plural, inglés, `kebab-case` | `/api/v1/instructors`, `/api/v1/schedules` |
| **Parámetros de ruta** | `camelCase` | `/api/v1/instructors/{instructorId}` |
| **Parámetros de consulta** | `camelCase` | `?startDate=2026-06-01&endDate=2026-06-30` |
| **Campos en JSON** | `camelCase` | `{ "instructorId": "uuid", "fullName": "Juan Pérez" }` |

## Métodos HTTP

| Método | Uso | Ejemplo |
|--------|-----|---------|
| `GET` | Obtener recursos | `GET /api/v1/instructors/{id}` |
| `POST` | Crear recursos | `POST /api/v1/instructors` |
| `PUT` | Reemplazar recurso completo | `PUT /api/v1/instructors/{id}` |
| `PATCH` | Actualización parcial | `PATCH /api/v1/instructors/{id}` |
| `DELETE` | Eliminar recurso (soft-delete) | `DELETE /api/v1/instructors/{id}` |

## Códigos de estado HTTP

| Código | Significado | Uso |
|--------|-------------|-----|
| `200 OK` | Éxito en GET, PUT, PATCH | Operación completada correctamente. |
| `201 Created` | Éxito en POST | Recurso creado; retorna Location del nuevo recurso. |
| `204 No Content` | Éxito en DELETE | Eliminación exitosa sin contenido en respuesta. |
| `400 Bad Request` | Error de validación | Datos de entrada inválidos (DTO validation). |
| `401 Unauthorized` | No autenticado | Token JWT ausente o inválido. |
| `403 Forbidden` | No autorizado | El usuario no tiene permisos para la acción. |
| `404 Not Found` | Recurso no encontrado | El ID solicitado no existe. |
| `409 Conflict` | Conflicto de estado | Ej: instructor ya tiene horario en esa franja. |
| `500 Internal Server Error` | Error interno | Error inesperado (no expone stack trace). |

## Estructura de respuestas

### Respuesta exitosa (GET / listado)

```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "fullName": "Juan Pérez",
      "email": "juan.perez@example.com",
      "hireType": "STAFF",
      "isActive": true
    }
  ],
  "pagination": {
    "page": 0,
    "size": 20,
    "totalElements": 100,
    "totalPages": 5
  }
}