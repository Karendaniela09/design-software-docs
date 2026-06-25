
```markdown
# Seguridad documental

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Seguridad

Este repositorio puede ser consultado por varios equipos. La documentación debe usar ejemplos seguros y evitar exposición de información sensible. Adicionalmente, el sistema maneja datos personales (PII) de aprendices, instructores y personal administrativo, por lo que se deben seguir estrictas reglas de protección.

## No publicar

- Credenciales, contraseñas, tokens o llaves privadas.
- Certificados, archivos `.env`, `.pem`, `.key`, `.p12` o `.pfx`.
- Datos personales reales de aprendices, instructores, administradores o usuarios.
- Correos reales, teléfonos, números de documento o identificadores personales.
- Capturas de pantalla con sesiones abiertas o datos operativos reales.
- URLs internas privadas, IPs, nombres de host o rutas de red sensibles.
- Procedimientos que permitan saltarse controles de seguridad.

## Usar en ejemplos

| Caso | Valor seguro |
|------|--------------|
| Correo | `usuario@example.com` |
| Token | `TOKEN_DE_EJEMPLO` |
| URL | `https://example.com/api` |
| Servicio | `sena-horarios-service` |
| Documento | `1234567890` solo si se aclara que es ficticio |

## Antes de subir capturas

- Revisar que no haya nombres reales.
- Ocultar correos, documentos, tokens y sesiones.
- Confirmar que la captura aporta valor documental.
- Guardar la imagen en `assets/images/` y referenciarla desde el documento.

## Si se detecta una fuga

1. No crear más commits con el secreto o dato sensible.
2. Avisar al responsable del repositorio y al equipo de seguridad o arquitectura.
3. Rotar la credencial si aplica.
4. Abrir un PR que reemplace el contenido por un ejemplo seguro.
5. Evaluar limpieza de historial si el dato quedó versionado.

## Contacto de seguridad

En caso de fuga confirmada o sospecha de exposición de datos sensibles:

| Rol | Handle / Canal |
|-----|---------------|
| Responsable del repositorio | `@equipo-arquitectura` |
| Equipo de arquitectura | `@equipo-arquitectura` → Canal de comunicación del equipo |
| Equipo de seguridad | `@equipo-seguridad` (si existe) |

Ante una credencial comprometida: **rotar primero, avisar después**. No esperar confirmación para rotar.

## Checklist

- [ ] No hay credenciales ni tokens.
- [ ] No hay datos personales reales.
- [ ] No hay URLs internas privadas.
- [ ] No hay capturas con sesiones o datos reales.
- [ ] Los ejemplos usan valores ficticios.

## Medidas de seguridad en el sistema

Además de la seguridad documental, el sistema implementa:

- **Autenticación:** JWT con Spring Security.
- **Autorización:** RBAC (Roles: Coordinador, Instructor, Administrador).
- **Cifrado de PII:** En reposo usando PostgreSQL (`pgcrypto`) o a nivel de aplicación con Spring Security.
- **Auditoría:** Tabla `audit_log` append-only para todas las operaciones críticas.
- **Protección contra inyección SQL:** Uso de JPA/Hibernate con parámetros bind.
- **Sanitización de errores:** `GlobalExceptionHandler` para no exponer stack traces.

## Referencias

- [documentation-rules.md](./documentation-rules.md)
- [git-conventions.md](./git-conventions.md)
- [definition-of-ready.md](./definition-of-ready.md)
- [definition-of-done.md](./definition-of-done.md)