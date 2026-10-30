# ADR-031: Baseline de rutas durante la estabilización

**Estado:** PROPOSED
**Fecha:** 2026-10-30
**Autores:** Juan282007
**Equipos involucrados:** Arquitectura, backend, frontend, DevOps, QA

## Contexto

La estabilización de los diez microservicios y sus MFEs requiere un contrato de rutas consistente entre los servicios, el edge y las aplicaciones web. En el estado reportado hay respuestas 403, 502, 405 y HTML donde se esperaba JSON. Cambiar prefijos o métodos durante el diagnóstico sin una referencia común puede ocultar el destino equivocado, introducir rutas duplicadas o romper otros consumidores.

El contrato base del edge por dominio ya está definido en [ADR-022](./ADR-022-edge-routing-table-by-domain.md). DS-001 registra además diferencias de disponibilidad entre ambientes, hallazgos reportados por el operador y una discrepancia de horario del backlog. La información de disponibilidad no sustituye una prueba autenticada ni la revisión de logs.

## Decisión

Se propone congelar durante el ciclo de estabilización el formato público de rutas `/<dominio>/api/v1` establecido por ADR-022 y el origen del edge por ambiente establecido por ADR-007. Cada servicio conserva su ruta de health documentada y cada remote conserva `/mfe/<dominio>/`.

El congelamiento aplica a **contratos y configuración de enrutamiento**, no a la integración del trabajo: las ramas y PR siguen permitidos. Una modificación de prefijo, `servers` de OpenAPI, destino del edge, strip-prefix o ruta de remote debe:

1. explicar qué hallazgo reproducible la requiere;
2. identificar consumidores afectados y rutas antiguas/nuevas;
3. incluir verificación del método, código de respuesta y `Content-Type` esperados;
4. actualizar el mapa DS-001 y las pruebas o smoke relevantes en el mismo PR;
5. obtener revisión de Arquitectura y validación de QA según los gates del plan.

Se permiten correcciones compatibles que hagan que la implementación alcance el contrato existente, así como mitigaciones urgentes de seguridad/disponibilidad que no creen una nueva convención pública. Toda excepción se registra en el PR y se reconcilia en el mapa antes del cierre de estabilización.

La tabla de rutas por dominio de ADR-022 continúa como fuente de la topología del edge. Este ADR establece control de cambios para el ciclo de estabilización; no duplica ni reemplaza dicha tabla.

## Consecuencias

### Positivas

- El diagnóstico puede distinguir fallos de autorización, servicio upstream y fallback de SPA usando una misma ruta esperada.
- Un PR puede corregir despliegue/backend/frontend sin que cada cambio invente un prefijo nuevo.
- Los cambios excepcionales quedan trazables con evidencia y consumidores identificados.

### Negativas / Trade-offs

- Una incompatibilidad real no puede resolverse por cambio unilateral de ruta; requiere coordinación y actualización de consumidores.
- El mapa debe mantenerse en el mismo PR cuando cambie la topología o el contrato.

### Riesgos

- Interpretar “congelamiento” como prohibición de corregir rutas rotas puede prolongar un incidente. La regla permite correcciones compatibles y mitigaciones urgentes.
- Las rutas de la tabla no demuestran que todos los servicios estén desplegados ni que cada catálogo acepte la sesión actual; esos estados requieren smoke autenticado por ambiente.

## Alternativas consideradas

| Alternativa | Por qué no se elige |
|---|---|
| Congelar también cambios de implementación | Impediría reparar de forma segura los errores ya observados durante la estabilización. |
| Permitir que cada PR cambie libremente la base API | Deshace la convención de ADR-022 y vuelve ambiguos los resultados de integración. |
| Modificar ADR-022 para repetir la tabla | Duplicaría la decisión vigente y permitiría que dos tablas diverjan. |

## Referencias

- [ADR-007 — Edge gateway y convención de puertos](./ADR-007-edge-gateway-and-port-convention.md)
- [ADR-022 — Tabla de rutas del edge por dominio](./ADR-022-edge-routing-table-by-domain.md)
- [DS-001 — Baseline de arquitectura para estabilización](../../../15-project-control/ds-001-architecture-baseline.md)
