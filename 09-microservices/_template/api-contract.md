# API Contract - [Nombre del Servicio]

> Estado: 🔴 Pendiente | Última actualización: YYYY-MM-DD
> Autor: [Nombre Apellido] | Equipo: [nombre del equipo]

## Contexto

Este documento define el contrato API del servicio **[Nombre del Servicio]**. Describe los endpoints, métodos HTTP, parámetros, request/response DTOs y códigos de error.

## Base URL
/api/v1/[recurso]

text

## Autenticación

Todas las peticiones deben incluir un token JWT en el header:
Authorization: Bearer <token>

text

## Endpoints

### 1. Obtener todos los recursos

```http
GET /api/v1/[recurso]
Parámetros de consulta (query params):

Parámetro	Tipo	Descripción	Obligatorio
page	integer	Número de página (0-indexed)	No (default: 0)
size	integer	Tamaño de página	No (default: 20)
sort	string	Campo de ordenamiento	No
filter	string	Filtro de búsqueda	No
Respuesta exitosa (200 OK):

json
{
  "data": [
    {
      "id": "uuid",
      "field1": "value1",
      "field2": "value2",
      "createdAt": "2026-06-24T10:30:00Z",
      "updatedAt": "2026-06-24T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 0,
    "size": 20,
    "totalElements": 100,
    "totalPages": 5
  }
}
2. Obtener un recurso por ID
http
GET /api/v1/[recurso]/{id}
Parámetros de ruta:

Parámetro	Tipo	Descripción
id	UUID	Identificador del recurso
Respuesta exitosa (200 OK):

json
{
  "id": "uuid",
  "field1": "value1",
  "field2": "value2",
  "createdAt": "2026-06-24T10:30:00Z",
  "updatedAt": "2026-06-24T10:30:00Z"
}
Respuesta de error (404 Not Found):

json
{
  "code": "NOT_FOUND",
  "message": "Recurso no encontrado",
  "timestamp": "2026-06-24T10:30:00Z"
}
3. Crear un recurso
http
POST /api/v1/[recurso]
Request Body:

json
{
  "field1": "value1",
  "field2": "value2"
}
Respuesta exitosa (201 Created):

json
{
  "id": "uuid",
  "field1": "value1",
  "field2": "value2",
  "createdAt": "2026-06-24T10:30:00Z"
}
Respuesta de error (400 Bad Request):

json
{
  "code": "VALIDATION_ERROR",
  "message": "Campo 'field1' es obligatorio",
  "timestamp": "2026-06-24T10:30:00Z"
}
4. Actualizar un recurso
http
PUT /api/v1/[recurso]/{id}
Parámetros de ruta:

Parámetro	Tipo	Descripción
id	UUID	Identificador del recurso
Request Body:

json
{
  "field1": "new_value1",
  "field2": "new_value2"
}
Respuesta exitosa (200 OK):

json
{
  "id": "uuid",
  "field1": "new_value1",
  "field2": "new_value2",
  "updatedAt": "2026-06-24T10:30:00Z"
}
5. Eliminar un recurso (soft-delete)
http
DELETE /api/v1/[recurso]/{id}
Parámetros de ruta:

Parámetro	Tipo	Descripción
id	UUID	Identificador del recurso
Respuesta exitosa (204 No Content):

Sin cuerpo de respuesta.

Respuesta de error (404 Not Found):

json
{
  "code": "NOT_FOUND",
  "message": "Recurso no encontrado",
  "timestamp": "2026-06-24T10:30:00Z"
}
Códigos de error
Código	Descripción	HTTP Status
VALIDATION_ERROR	Error de validación de datos	400
UNAUTHORIZED	No autenticado	401
FORBIDDEN	No autorizado	403
NOT_FOUND	Recurso no encontrado	404
CONFLICT_ERROR	Conflicto de estado (ej. horario solapado)	409
INTERNAL_ERROR	Error interno del servidor	500