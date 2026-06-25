# Preguntas abiertas

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Gestión / Arquitectura

## Contexto

Este documento contiene las preguntas abiertas del proyecto **Horarios SENA**. Son decisiones que aún no han sido tomadas y que requieren aclaración por parte del instructor, el product owner u otros stakeholders.

## Flujo de resolución

1. **Registrar:** Cualquier equipo puede agregar una pregunta con estado `ABIERTA`.
2. **Asignar:** Se asigna un responsable y una fecha límite.
3. **Resolver:** El responsable responde y cambia el estado a `RESUELTA`.
4. **Escalar:** Si la resolución genera una decisión técnica, se crea un ADR en `05-architecture/decisions/records/`.
5. **Cerrar:** Las preguntas resueltas se mantienen en el historial.

## Preguntas abiertas

| # | Pregunta | Área | Responsable | Fecha límite | Estado | Resolución / ADR |
|---|----------|------|-------------|--------------|--------|------------------|
| Q1 | ¿La integración con SOFIA Plus es en tiempo real o por lotes? | Integración | Equipo Arquitectura | 2026-07-15 | 🔴 ABIERTA | - |
| Q2 | ¿Qué datos se sincronizan desde SOFIA Plus? ¿Solo fichas y aprendices, o también programas y competencias? | Integración | Equipo Arquitectura | 2026-07-15 | 🔴 ABIERTA | - |
| Q3 | ¿El sistema debe tener una vista de "calendario" (drag & drop) o solo tabla? | UX/UI | Equipo Producto | 2026-07-15 | 🔴 ABIERTA | - |
| Q4 | ¿Qué roles específicos deben existir? (Coordinador, Instructor, Aprendiz, Administrador) | Seguridad | Equipo Producto | 2026-07-01 | ✅ RESUELTA | Ver ADR-002 |
| Q5 | ¿Los horarios se crean manualmente o se importan desde un archivo (Excel)? | Funcional | Equipo Producto | 2026-07-01 | ✅ RESUELTA | Manual en MVP |
| Q6 | ¿Qué reportes son obligatorios en el MVP? | Funcional | Equipo Producto | 2026-07-15 | 🔴 ABIERTA | - |
| Q7 | ¿Se requiere operación offline o solo en línea? | Funcional | Equipo Producto | 2026-07-15 | 🔴 ABIERTA | - |
| Q8 | ¿Qué SLA espera coordinación para carga de horarios, trazas y reportes? | Operacional | Equipo Producto | 2026-07-15 | 🔴 ABIERTA | - |
| Q9 | ¿Qué métricas son indicadores oficiales y cuáles son solo analítica interna? | Monitoreo | Equipo Producto | 2026-07-15 | 🔴 ABIERTA | - |
| Q10 | ¿Qué reglas internas SENA no están en documentación pública y deben entregarse como insumo? | Normativo | Equipo Producto | 2026-07-15 | 🔴 ABIERTA | - |

## Preguntas resueltas

| # | Pregunta | Área | Resolución | ADR / Doc relacionado |
|---|----------|------|------------|-----------------------|
| Q4 | ¿Qué roles específicos deben existir? | Seguridad | Se definen 4 roles: Coordinador, Instructor, Aprendiz, Administrador. | ADR-002 |
| Q5 | ¿Los horarios se crean manualmente o se importan? | Funcional | Manual en el MVP. Importación en fases posteriores. | - |

## Referencias

- [risks.md](./risks.md)
- [dependencies.md](./dependencies.md)
- [05-architecture/decisions/README.md](../05-architecture/decisions/README.md)