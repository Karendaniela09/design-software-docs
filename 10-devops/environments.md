# Ambientes del sistema

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: DevOps

## Contexto

El sistema **Horarios SENA** cuenta con cuatro ambientes (entornos) que permiten gestionar el ciclo de vida del desarrollo, desde la codificación hasta la producción. Cada ambiente tiene un propósito específico y reglas de uso definidas.

## Ambientes

| Ambiente | Propósito | Rama | URL (ejemplo) | Acceso |
|----------|-----------|------|---------------|--------|
| **Desarrollo (dev)** | Desarrollo y pruebas unitarias | `dev` | `http://dev.horarios.sena.local` | Equipo de desarrollo |
| **QA** | Pruebas funcionales y de integración | `qa` | `http://qa.horarios.sena.local` | QA, Desarrollo |
| **Staging** | Validación final antes de producción | `staging` | `https://staging.horarios.sena.edu.co` | Stakeholders, Producto |
| **Producción (main)** | Entorno productivo | `main` | `https://horarios.sena.edu.co` | Usuarios finales |

## Flujo de promoción entre ambientes

```text
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Developer  │───▶│    QA        │───▶│   Staging    │───▶│  Producción  │
│   (dev)      │    │    (qa)      │    │   (staging)  │    │   (main)     │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
   Desarrollo          Pruebas           Pre-producción      Producción
   local / dev         Funcionales       Validación final    Usuarios reales