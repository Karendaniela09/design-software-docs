
```markdown
# Runbook - [Nombre del Servicio]

> Estado: 🔴 Pendiente | Última actualización: YYYY-MM-DD
> Autor: [Nombre Apellido] | Equipo: [nombre del equipo]

## Contexto

Este documento contiene el runbook de operaciones del servicio **[Nombre del Servicio]** . Describe cómo desplegar, monitorear, diagnosticar y recuperar el servicio en caso de fallo. Está dirigido al equipo de operaciones y DevOps.

## Despliegue

### Requisitos previos

- Docker y Docker Compose instalados.
- Acceso al repositorio de código.
- Variables de entorno configuradas (ver `.env.example`).

### Comando de despliegue

```bash
# Levantar el servicio
docker compose up -d [servicio]

# Verificar que el servicio esté corriendo
docker compose ps [servicio]
Variables de entorno requeridas
Variable	Descripción	Obligatoria	Valor por defecto
DB_HOST	Host de la base de datos	Sí	localhost
DB_PORT	Puerto de la base de datos	Sí	5432
DB_NAME	Nombre de la base de datos	Sí	-
DB_USER	Usuario de la base de datos	Sí	-
DB_PASSWORD	Contraseña de la base de datos	Sí	-
RABBITMQ_HOST	Host del broker de mensajes	No	localhost
RABBITMQ_PORT	Puerto del broker de mensajes	No	5672
JWT_SECRET	Secreto para JWT	Sí	-
Healthcheck
Endpoint
text
GET /actuator/health
Respuesta exitosa
json
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP"
    },
    "rabbitmq": {
      "status": "UP"
    }
  }
}
Respuesta de error
json
{
  "status": "DOWN",
  "components": {
    "db": {
      "status": "DOWN",
      "details": {
        "error": "Connection refused"
      }
    }
  }
}
Logs
Ubicación de logs
Docker: docker compose logs -f [servicio]

Archivo (local): logs/[servicio].log

Entornos productivos: Centralizado en ELK / Datadog.

Niveles de log
Nivel	Uso
DEBUG	Información detallada para desarrollo (solo en dev).
INFO	Eventos importantes (creación, actualización).
WARN	Situaciones anormales que no impiden la operación.
ERROR	Errores que requieren atención.
Comandos útiles para logs
bash
# Ver logs en tiempo real
docker compose logs -f [servicio]

# Ver logs de las últimas 100 líneas
docker compose logs --tail=100 [servicio]

# Ver logs con timestamp
docker compose logs -t [servicio]
Troubleshooting
Problema 1: El servicio no inicia
Síntomas:

El contenedor está en estado exited o restarting.

Los logs muestran errores de conexión a la base de datos.

Posibles causas y soluciones:

Causa	Solución
Base de datos no disponible	Verificar que el contenedor de PostgreSQL esté corriendo: docker compose ps postgres
Variables de entorno incorrectas	Revisar el archivo .env y verificar que DB_HOST apunte al contenedor correcto.
Puerto ocupado	Cambiar el puerto en application.yml o .env.
Comandos de diagnóstico:

bash
# Ver logs del servicio
docker compose logs [servicio]

# Verificar conexión a la base de datos
docker compose exec [servicio] curl -f http://localhost:8080/actuator/health
Problema 2: Conflictos de horario no se detectan correctamente
Síntomas:

El sistema permite guardar horarios conflictivos.

El usuario no recibe mensaje de error.

Posibles causas y soluciones:

Causa	Solución
Índices en la base de datos no están creados	Ejecutar las migraciones de Flyway: docker compose exec backend ./mvnw flyway:migrate
Lógica de validación desactivada	Verificar que el ScheduleService esté llamando a los métodos de validación.
Consulta JPA incorrecta	Revisar la consulta en el repositorio y verificar el @Query.
Comandos de diagnóstico:

bash
# Verificar índices en la base de datos
docker compose exec postgres psql -U horarios_user -d horarios_db -c "\di"

# Ver logs de validación
docker compose logs [servicio] | grep -i conflict
Problema 3: Alto tiempo de respuesta
Síntomas:

Las peticiones tardan más de 2 segundos.

El usuario experimenta lentitud.

Posibles causas y soluciones:

Causa	Solución
Consultas a base de datos sin índices	Crear índices para las consultas más frecuentes.
Carga alta de peticiones	Escalar horizontalmente: docker compose up -d --scale [servicio]=2.
Timeouts incorrectos	Verificar la configuración de timeouts en application.yml.
Comandos de diagnóstico:

bash
# Verificar uso de CPU y memoria
docker stats [servicio]

# Verificar tiempo de respuesta de endpoints
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8080/api/v1/[recurso]
Rollback
Cuándo hacer rollback
Error crítico en producción que afecta a los usuarios.

Degradación severa del rendimiento.

Inconsistencia de datos detectada.

Procedimiento de rollback
bash
# 1. Detener el servicio
docker compose down [servicio]

# 2. Restaurar la versión anterior de la imagen
docker tag [servicio]:[version-anterior] [servicio]:latest

# 3. Re-iniciar el servicio
docker compose up -d [servicio]

# 4. Verificar que el servicio esté funcionando
docker compose ps [servicio]
Tiempo estimado: 5-10 minutos.

Métricas clave
Métrica	Descripción	Umbral de alerta
http_requests_total	Total de peticiones HTTP por endpoint.	N/A
http_requests_duration_seconds	Tiempo de respuesta (p95).	> 3s
http_errors_total	Total de errores HTTP (5xx).	> 5%
jvm_memory_used_bytes	Memoria usada por la JVM.	> 80%