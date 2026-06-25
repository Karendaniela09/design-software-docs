# Estrategia de autenticación y autorización

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Seguridad

## Contexto

El sistema **Horarios SENA** requiere autenticación y autorización para controlar el acceso a los recursos. Se implementa un mecanismo stateless basado en JWT (JSON Web Token) con Spring Security.

## Decisión arquitectónica

Se adopta **JWT (JSON Web Token) con Spring Security** como mecanismo de autenticación y autorización (ver ADR-002).

## Roles y permisos

| Rol | Descripción | Permisos principales |
|-----|-------------|----------------------|
| `ROLE_ADMIN` | Administrador del sistema | Todos los permisos (CRUD de todo). |
| `ROLE_COORDINADOR` | Coordinador académico | Crear/editar/eliminar horarios, gestionar instructores, ambientes y fichas. |
| `ROLE_INSTRUCTOR` | Instructor | Consultar su propio horario, registrar observaciones. |
| `ROLE_APRENDIZ` | Aprendiz (futuro) | Consultar su horario de clases. |

## Flujo de autenticación

1. El cliente envía credenciales (usuario/contraseña) al endpoint `/api/v1/auth/login`.
2. El backend valida las credenciales y genera un JWT con los roles del usuario.
3. El backend devuelve el JWT al cliente.
4. El cliente incluye el JWT en el header `Authorization: Bearer <token>` en cada petición.
5. El backend valida el JWT, extrae los roles y autoriza la petición.

## Endpoints de autenticación

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | Login con usuario/contraseña; devuelve JWT. |
| `/api/v1/auth/refresh` | POST | Refrescar token (si está cerca de expirar). |
| `/api/v1/auth/logout` | POST | Cerrar sesión (invalida token en servidor). |

### Ejemplo de solicitud de login

```json
POST /api/v1/auth/login
{
  "username": "coordinator_001",
  "password": "securePassword123"
}