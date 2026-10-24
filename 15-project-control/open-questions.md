# Preguntas abiertas

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Arquitectura / Gestión

## Flujo de resolución

1. **Registrar:** cualquier equipo puede agregar una pregunta abierta con estado `ABIERTA`.
2. **Asignar:** el equipo de arquitectura o gestión asigna un responsable y una fecha límite de respuesta.
3. **Resolver:** el responsable responde y cambia el estado a `RESUELTA`.
4. **Escalar si aplica:** si la resolución genera una decisión técnica relevante, crear un ADR en `05-architecture/decisions/records/`. Si afecta requisitos, actualizar `04-requirements/`.
5. **Cerrar:** preguntas resueltas se mantienen en el historial (no eliminar). Mover a sección `## Resueltas` cuando el registro sea largo.

## Formato de registro

| # | Pregunta | Área | Responsable | Fecha límite | Estado | Resolución / ADR |
|---|----------|------|-------------|--------------|--------|------------------|

## Estados válidos

| Estado | Significado |
|--------|-------------|
| `ABIERTA` | Sin respuesta aún |
| `EN REVISIÓN` | Responsable asignado, trabajando en ella |
| `RESUELTA` | Tiene respuesta, puede generar ADR o actualización |
| `CANCELADA` | Ya no aplica (indicar por qué) |

---

## Preguntas abiertas

Registro central de los puntos abiertos (PA-NN) del producto. Origen: [03-product/vision.md](../03-product/vision.md) §8 (PA-01…PA-04) y [03-product/roadmap.md](../03-product/roadmap.md) (PA-03). Al resolverse, mover a `## Resueltas` y —si aplica— generar el ADR correspondiente.

| # | Pregunta | Área | Responsable | Fecha límite | Estado | Resolución / ADR |
|---|----------|------|-------------|--------------|--------|------------------|
| PA-01 | ¿El coordinador puede modificar un horario `PUBLISHED` directamente, o siempre debe crear una nueva versión? *(supuesto actual: siempre nueva versión — RN-SCH-01)* | Producto / Arquitectura | Producto | Antes de construir `scheduling-service` (Fase 2 / D) | ABIERTA | — |
| PA-02 | ¿Los instructores contratistas tienen un límite de horas distinto al de planta? *(supuesto: sí — RN-ACT-01)* | Producto / Normativa | Producto | Antes de `actors-service` (Fase 1 / C) | ABIERTA | — |
| PA-03 | ¿Se requiere integración con SOFIA Plus en el MVP o en fases posteriores? *(supuesto: fases posteriores)*. Si se adelanta, `academic-management` (EPC-04) debe incorporar el ACL correspondiente. | Producto / Sponsor | Sponsor | Confirmar antes de cerrar alcance MVP | ABIERTA | — |
| PA-04 | ¿Un aprendiz puede estar matriculado en más de una ficha activa a la vez? | Producto / Dominio | Producto | Antes de `actors-service` (Fase 1 / C) | ABIERTA | — |

### Reference Data — revalidación HU-REF-020/R1 (2026-10-24)

Preguntas propuestas a Arquitectura; responsables nominales por asignar por el equipo. La implementación y sus pruebas no cambian estos registros a RESUELTA.

| # | Pregunta | Área | Responsable | Fecha límite | Estado | Resolución / ADR |
|---|---|---|---|---|---|---|
| PA-REF-01 | ¿Se ratifican los límites IAM/shell/cliente compartido/MFE/backend y el mecanismo de acceso privado de CI? | Arquitectura / Frontend / Seguridad | Por asignar por Arquitectura | Antes de aceptar ADR-020 y cerrar CI del MFE | ABIERTA | [ADR-020](../05-architecture/decisions/records/ADR-020-reference-data-iam-e2e-integration.md) |
| PA-REF-02 | ¿Los runners de Infra serán soporte versionado de validación o gate CI oficial? Definir mantenimiento y frecuencia. | Arquitectura / DevOps | Por asignar por Arquitectura | Antes de adopción transversal | ABIERTA | [ADR-020](../05-architecture/decisions/records/ADR-020-reference-data-iam-e2e-integration.md) |
| PA-REF-03 | ¿Se ratifica que inbox/proyección pertenecen a Reference Data y permanecen mientras exista el consumidor? | Arquitectura / Datos | Por asignar por Arquitectura | Antes de aceptar ADR-021 | ABIERTA | [ADR-021](../05-architecture/decisions/records/ADR-021-reference-data-resilient-messaging.md) |
| PA-REF-04 | ¿Qué ventana de retención/replay, archivo y reconstrucción permite limpiar datos sin reabrir duplicados? | Datos / Operación | Por asignar por Arquitectura | Antes de habilitar limpieza automática | ABIERTA | [ADR-021](../05-architecture/decisions/records/ADR-021-reference-data-resilient-messaging.md) |
| PA-REF-05 | ¿Quién opera topología RabbitMQ, controles de cambio, DLQ y replay autorizado? | Plataforma / Reference Data | Por asignar por Arquitectura | Antes de operar en ambiente compartido | ABIERTA | [ADR-021](../05-architecture/decisions/records/ADR-021-reference-data-resilient-messaging.md) |
| PA-REF-06 | ¿Se aprueba el orden DB/IAM DB → servicio/plataforma → MFE/Infra → shell y la actualización de refs CI antes de borrar ramas? | Integración / QA | Por asignar por Arquitectura | Antes de los merges coordinados | ABIERTA | [ADR-020](../05-architecture/decisions/records/ADR-020-reference-data-iam-e2e-integration.md) |

---

## Resueltas

| # | Pregunta | Área | Resolución | ADR / Doc relacionado |
|---|----------|------|------------|-----------------------|
