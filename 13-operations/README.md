# Operaciones

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: DevOps / Arquitectura

## Contenido

Este directorio contiene la documentación relacionada con la operación del sistema **Horarios SENA**. Aquí se definen las estrategias de observabilidad, la gestión de incidentes y los procedimientos de backup y recuperación.

## Archivos

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [observability.md](./observability.md) | Métricas, logs, trazas, alertas y tableros de monitoreo. | 🟢 Estable |
| [incident-management.md](./incident-management.md) | Clasificación, respuesta y comunicación de incidentes. | 🟢 Estable |
| [backup-and-recovery.md](./backup-and-recovery.md) | Backups, restauración, RPO/RTO y pruebas de recuperación. | 🟢 Estable |

## Principios de operación

1. **Visibilidad:** Todo el sistema debe ser observable (logs, métricas, trazas).
2. **Proactividad:** Las alertas deben permitir detectar problemas antes de que impacten a los usuarios.
3. **Resiliencia:** El sistema debe recuperarse automáticamente de fallos cuando sea posible.
4. **Disponibilidad:** El sistema debe estar disponible el 99.9% del tiempo en producción.
5. **Recuperación:** Los backups deben permitir restaurar el sistema en menos de 4 horas (RTO).

## Roles de operación

| Rol | Responsabilidad |
|-----|-----------------|
| **DevOps** | Configuración y mantenimiento de infraestructura, monitoreo, backups. |
| **Desarrolladores** | Responder incidentes relacionados con el código, aplicar fixes. |
| **Arquitectura** | Definir estrategias de operación, revisar alertas y planes de recuperación. |

## Referencias

- [10-devops/environments.md](../10-devops/environments.md)
- [10-devops/ci-cd.md](../10-devops/ci-cd.md)
- [05-architecture/deployment.md](../05-architecture/deployment.md)