# Gestión de incidentes

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: DevOps / Arquitectura

## Contexto

Este documento define el proceso de gestión de incidentes del sistema **Horarios SENA**. Un incidente es cualquier evento que interrumpe o degrada la operación normal del sistema.

## Clasificación de incidentes

### Severidad

| Severidad | Descripción | Tiempo de respuesta | Ejemplo |
|-----------|-------------|---------------------|---------|
| **Crítica** | Servicio no disponible o datos perdidos. | 30 minutos | El sistema no responde, base de datos caída. |
| **Alta** | Servicio degradado o funcionalidad crítica falla. | 2 horas | No se pueden crear horarios. |
| **Media** | Funcionalidad no crítica falla. | 1 día | Los reportes no se generan correctamente. |
| **Baja** | Problema estético o error menor. | 3 días | Error de ortografía en la interfaz. |

---

## Flujo de gestión de incidentes

1. **Detección:**
   - El incidente es detectado por alertas automáticas (Prometheus, logs, etc.).
   - Reportado por un usuario (correo, llamada, ticket).

2. **Registro:**
   - Se crea un ticket en el sistema de seguimiento (Jira, GitHub Issues).
   - Se asigna un ID único.

3. **Clasificación:**
   - Se asigna la severidad.
   - Se prioriza según el impacto en el negocio.

4. **Resolución:**
   - El equipo de desarrollo o DevOps trabaja en la solución.
   - Se aplican parches, se reinician servicios, se revierten cambios.

5. **Verificación:**
   - Se confirma que la solución funciona.
   - Se realizan pruebas de integración.

6. **Comunicación:**
   - Se notifica a los stakeholders (producto, usuarios afectados).
   - Se actualiza el estado del incidente.

7. **Cierre:**
   - Se cierra el ticket.
   - Se documenta la lección aprendida.
   - Se actualiza el runbook si es necesario.

---

## Plantilla de incidente

```markdown
# Incidente: [Título breve]

- **ID:** INC-XXX
- **Fecha:** YYYY-MM-DD HH:MM
- **Severidad:** Crítica / Alta / Media / Baja
- **Reportado por:** [Nombre]
- **Estado:** Abierto / En progreso / Resuelto / Cerrado
- **Servicio afectado:** [backend / frontend / base de datos / ...]

## Descripción

[Descripción del incidente y su impacto en los usuarios]

## Cronología

- **HH:MM** - Incidente detectado.
- **HH:MM** - Equipo notificado.
- **HH:MM** - Diagnóstico iniciado.
- **HH:MM** - Solución aplicada.
- **HH:MM** - Servicio restaurado.

## Causa raíz

[Descripción de la causa que originó el incidente]

## Solución aplicada

[Descripción de la solución aplicada para resolver el incidente]

## Acciones preventivas

- [Acción 1 - Ejemplo: Mejorar la monitorización]
- [Acción 2 - Ejemplo: Actualizar documentación]

## Referencias

- [Enlace a logs / métricas]
- [Enlace a PR / commit de la solución]