# Topología de despliegue

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: DevOps / Arquitectura

## Contexto

Este documento describe la topología de despliegue del sistema **Horarios SENA**, incluyendo los ambientes, la configuración de contenedores, el flujo de CI/CD, healthchecks y la estrategia de rollback.

## Ambientes

| Ambiente | Propósito | Rama | URL (ejemplo) |
|----------|-----------|------|---------------|
| **Desarrollo (dev)** | Desarrollo y pruebas unitarias | `dev` | `http://dev.sena-horarios.local` |
| **QA** | Pruebas funcionales y de integración | `qa` | `http://qa.sena-horarios.local` |
| **Staging** | Validación final antes de producción | `staging` | `http://staging.sena-horarios.local` |
| **Producción (main)** | Entorno productivo | `main` | `https://horarios.sena.edu.co` |

## Arquitectura de despliegue (Docker Compose)

El sistema se despliega como un conjunto de contenedores orquestados con Docker Compose. En entornos productivos se recomienda usar Kubernetes u orquestadores similares.

### Servicios en Docker Compose

| Servicio | Imagen | Puerto | Dependencias |
|----------|--------|--------|--------------|
| `postgres` | `postgres:16-alpine` | 5432 | - |
| `backend` | `horarios-backend:latest` | 8080 | `postgres` |
| `frontend` | `horarios-frontend:latest` | 3000 | `backend` |
| `nginx` (opcional) | `nginx:alpine` | 80, 443 | `backend`, `frontend` |

### Estructura de archivos

```text
/root/project/
├── docker-compose.yml
├── .env
├── backend/
│   ├── Dockerfile
│   └── ...
├── frontend/
│   ├── Dockerfile
│   └── ...
└── database/
    ├── Dockerfile
    ├── init/
    └── ...