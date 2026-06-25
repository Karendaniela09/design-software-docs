# Configuración del entorno local

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: DevOps

## Contexto

Este documento describe cómo levantar el sistema **Horarios SENA** en un entorno local de desarrollo utilizando Docker Compose. Con este método, cualquier desarrollador puede tener el sistema completo funcionando en su máquina en pocos minutos.

## Requisitos previos

- **Docker:** Versión 24.x o superior.
- **Docker Compose:** Versión 2.x o superior.
- **Git:** Para clonar el repositorio.
- **Puertos disponibles:** `5432` (PostgreSQL), `8080` (Backend), `3000` (Frontend).

## Paso 1: Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/horarios-sena.git
cd horarios-sena
Paso 2: Configurar variables de entorno
Crear un archivo .env en la raíz del proyecto basado en el ejemplo .env.example:

bash
cp .env.example .env
Editar el archivo .env con los valores apropiados:

env
# Base de datos
DB_PASSWORD=horarios_password
DB_USER=horarios_user
DB_NAME=horarios_db

# JWT
JWT_SECRET=tu_secreto_jwt_muy_seguro

# Backend
BACKEND_PORT=8080

# Frontend
FRONTEND_PORT=3000

# Logging
LOGGING_LEVEL=INFO
Paso 3: Levantar los contenedores
bash
docker compose up -d --build
Explicación del comando:

up: Levanta los contenedores.

-d: Ejecuta en segundo plano (detached).

--build: Reconstruye las imágenes si hay cambios.

Paso 4: Verificar que los servicios estén funcionando
Servicio	URL / Comando	Verificación
Backend	http://localhost:8080/actuator/health	Debe devolver {"status":"UP"}.
Frontend	http://localhost:3000	Debe cargar la aplicación React.
PostgreSQL	docker exec -it horarios-db psql -U horarios_user -d horarios_db	Debe conectarse a la base de datos.
Paso 5: Ejecutar migraciones de base de datos (Flyway)
Las migraciones se ejecutan automáticamente al iniciar el backend. Si necesitas ejecutarlas manualmente:

bash
docker compose exec backend ./mvnw flyway:migrate
Servicios incluidos en Docker Compose
Servicio	Imagen	Puerto	Dependencias
postgres	postgres:16-alpine	5432	-
backend	horarios-backend:latest	8080	postgres
frontend	horarios-frontend:latest	3000	backend
Comandos útiles
Comando	Descripción
docker compose up -d	Levanta los contenedores en segundo plano.
docker compose logs -f backend	Muestra los logs del backend en tiempo real.
docker compose ps	Lista los contenedores en ejecución.
docker compose exec backend bash	Accede a la terminal del contenedor backend.
docker compose down	Detiene y elimina todos los contenedores.
docker compose down -v	Detiene y elimina contenedores y volúmenes (incluye datos de BD).
Solución de problemas comunes
Error: port is already allocated
Algún puerto está ocupado. Cambiar los puertos en el archivo .env o detener el proceso que los usa.

Error: connection refused al conectar a PostgreSQL
Asegurarse de que el contenedor de PostgreSQL esté corriendo:

bash
docker compose ps postgres
Esperar unos segundos a que el servicio esté listo.

Error: Flyway migration failed
Verificar que el script de migración no tenga errores sintácticos. Revisar los logs del backend:

bash
docker compose logs backend | grep -i flyway
Estructura de archivos para el entorno local
text
/
├── docker-compose.yml          # Orquestación de servicios
├── .env                        # Variables de entorno (no subir a Git)
├── .env.example                # Ejemplo de variables de entorno
├── backend/
│   ├── Dockerfile              # Dockerfile para el backend
│   └── ...
├── frontend/
│   ├── Dockerfile              # Dockerfile para el frontend
│   └── ...
└── database/
    ├── init/
    │   └── init.sql            # Scripts de inicialización de la BD
    └── ...