# Guía de onboarding técnico

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Desarrollo / DevOps

## Contexto

Esta guía está dirigida a nuevos integrantes del equipo técnico del proyecto **Horarios SENA**. Aquí se explica cómo configurar el entorno de desarrollo, las herramientas necesarias y los procesos de trabajo del equipo.

## Stack tecnológico

| Capa | Tecnología | Versión |
|------|------------|---------|
| Backend | Spring Boot | 3.2.x |
| Backend | Java | 21 LTS |
| Frontend | React | 18.x |
| Base de datos | PostgreSQL | 16.x |
| ORM | Spring Data JPA + Hibernate | - |
| Migraciones | Flyway | - |
| Contenedores | Docker + Docker Compose | - |
| CI/CD | GitHub Actions | - |

## Herramientas necesarias

| Herramienta | Propósito | Enlace de descarga |
|-------------|-----------|-------------------|
| **Java 21** | Desarrollo del backend | https://adoptium.net/ |
| **IntelliJ IDEA** | IDE para backend | https://www.jetbrains.com/idea/ |
| **Visual Studio Code** | IDE para frontend | https://code.visualstudio.com/ |
| **Node.js 20** | Desarrollo del frontend | https://nodejs.org/ |
| **Docker Desktop** | Contenedores y orquestación | https://www.docker.com/products/docker-desktop/ |
| **Git** | Control de versiones | https://git-scm.com/ |
| **Postman** | Pruebas de API | https://www.postman.com/ |

## Configuración del entorno de desarrollo

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/horarios-sena.git
cd horarios-sena