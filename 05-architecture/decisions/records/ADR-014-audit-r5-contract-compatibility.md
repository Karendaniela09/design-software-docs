# ADR-014: Compatibilidad ejecutable de contratos del dominio de Auditoría

**Estado:** Aceptado  
**Fecha:** 2026-10-20  
**Autores:** Juan Pablo Gómez Perdomo  
**Equipos involucrados:** Arquitectura, QA, Auditoría, Frontend Platform

## Contexto

El dominio de Auditoría integra varios límites técnicos: `audit-mfe` consume la
API HTTP de `audit-query-api` y `audit-worker` consume envelopes canónicos por
AMQP. La funcionalidad puede estar correcta en una ejecución local y aun así
romperse si un proveedor elimina una ruta, cambia la forma de una respuesta o
publica un evento que el worker ya no puede interpretar.

Además, Auditoría es un sumidero append-only: no publica eventos de dominio
propios. Por eso su contrato más importante de mensajería es el evento que
acepta y persiste, no un evento que publique.

## Decisión

Se decide mantener contratos ejecutables y verificables para los tres acuerdos:

1. **HTTP:** `design-software-audit-service/api/openapi/audit.yaml` es la
   fuente canónica, única y ejecutable del contrato de `audit-query-api`.
   Este repositorio enlaza dicho artefacto en vez de conservar una copia.
   Los cambios se comparan semánticamente con `oasdiff`;
   eliminaciones o estrechamientos incompatibles bloquean el Pull Request.
2. **Consumidor/proveedor:** el contrato Pact entre `audit-mfe` y
   `audit-query-api` se conserva en el repositorio de código del servicio y se
   verifica contra el proveedor mediante `audit-contract-provider`.
3. **Eventos:** el envelope AMQP consumido se define en el JSON Schema del
   repositorio `design-software-audit-service`. El worker debe validarlo antes
   de persistir; los inválidos siguen el flujo de reintento/DLQ.

Los comandos de verificación son reproducibles localmente y se ejecutan como
checks de CI en los PR hacia `develop`. La documentación normativa y la
evidencia de R5 se mantienen en este repositorio de docs; los artefactos
ejecutables permanecen junto al servicio que los compila y ejecuta.

## Consecuencias

### Positivas

- Pact detecta respuestas HTTP incompatibles con el frontend antes de integrar.
- OpenAPI/oasdiff protege rutas, parámetros y respuestas; el gate exige `MINOR`
  para cambios compatibles en `paths`, `PATCH` para metadatos y rechaza
  cambios incompatibles.
- JSON Schema evita que un envelope inválido entre al histórico de auditoría.
- La evidencia queda centralizada en la documentación oficial del proyecto.
- La separación permite revisar arquitectura sin duplicar contratos ejecutables.

### Negativas / trade-offs

- Cada cambio de contrato requiere actualizar su evidencia y ejecutar más de una
  validación.
- Pact, oasdiff y las pruebas de esquema requieren herramientas disponibles en
  el entorno de CI.
- La compatibilidad del evento consumido no reemplaza la validación de dominio
  de cada productor.

### Riesgos

- La protección de rama debe marcar el check R5 como obligatorio; esa
  configuración administrativa queda fuera del código versionado.
- El contrato Pact debe actualizarse junto con los cambios intencionales de la
  API; una actualización automática sin revisión podría ocultar una ruptura.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Validar únicamente con pruebas unitarias | No verifica el acuerdo real entre repositorios. |
| Mantener contratos solo en el repositorio del servicio | La decisión y la evidencia transversal deben vivir en `design-software-docs`. |
| Usar snapshots sin semántica de compatibilidad | No diferencia una mejora compatible de la eliminación de una capacidad pública. |
| Publicar eventos propios desde `audit-service` | Convertiría al sumidero append-only en productor y puede crear dependencias circulares. |

## Referencias

- [Contrato OpenAPI canónico de Auditoría](https://github.com/code-sena/design-software-audit-service/blob/develop/api/openapi/audit.yaml)
- [Contrato del componente query API](../../../09-microservices/services/09-audit-service/components/audit-query-api/contract.md)
- [Evidencia R5 del dominio](../../../09-microservices/services/09-audit-service/r5-contract-compatibility.md)
- `design-software-audit-service/api/events/audit-consumed-event.schema.json`
- `design-software-audit-service/contracts/pact/audit-mfe-audit-query-api.json`
