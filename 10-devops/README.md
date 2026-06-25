# DevOps

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: DevOps / Arquitectura

## Contenido

Este directorio contiene la documentación relacionada con la infraestructura, el entorno de desarrollo, el pipeline de CI/CD y los ambientes del sistema **Horarios SENA**. Aquí se definen cómo levantar el sistema localmente, cómo se despliega en los diferentes ambientes y cómo se gestiona la integración continua.

## Archivos

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [local-setup.md](./local-setup.md) | Guía para levantar el entorno de desarrollo local con Docker Compose. | 🟢 Estable |
| [ci-cd.md](./ci-cd.md) | Pipeline de integración y despliegue continuo con GitHub Actions. | 🟢 Estable |
| [environments.md](./environments.md) | Descripción de los ambientes: desarrollo, QA, staging y producción. | 🟢 Estable |

## Tecnologías

| Herramienta | Versión | Propósito |
|-------------|---------|-----------|
| Docker | 24.x | Contenerización de servicios. |
| Docker Compose | 2.x | Orquestación local de contenedores. |
| GitHub Actions | - | Pipeline de CI/CD. |
| PostgreSQL | 16.x | Base de datos del sistema. |
| Java | 21 LTS | Backend. |
| React | 18.x | Frontend. |
| Flyway | - | Migraciones de base de datos. |

## Estructura de archivos para DevOps

```text
/
├── docker-compose.yml          # Orquestación de servicios
├── .env.example                # Ejemplo de variables de entorno
├── .github/
│   └── workflows/
│       ├── ci.yml              # Pipeline de integración continua
│       └── cd.yml              # Pipeline de despliegue continuo
├── backend/
│   ├── Dockerfile              # Dockerfile para el backend
│   └── ...
├── frontend/
│   ├── Dockerfile              # Dockerfile para el frontend
│   └── ...
└── database/
    ├── Dockerfile              # Dockerfile para la base de datos (opcional)
    ├── init/
    │   └── init.sql            # Scripts de inicialización
    └── ...