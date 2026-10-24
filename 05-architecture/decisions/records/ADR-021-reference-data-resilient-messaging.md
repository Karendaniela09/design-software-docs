# ADR-021: Mensajería resiliente e inbox idempotente de Reference Data

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Valery Sinai Trujillo Quintero | Equipo: Reference Data

**Estado de la decisión:** PROPOSED, pendiente de revisión de Arquitectura.
**Fecha:** 2026-10-20
**Autores:** Valery Sinai Trujillo Quintero
**Equipos involucrados:** Reference Data, Datos, DevOps, QA y Arquitectura.
**Trazabilidad de numeración:** propuesta anteriormente citada como ADR-013 de Reference Data en el PR #340; renumerada a ADR-021 al reconciliar main. El ADR-013 de Monitoring conserva su identidad y contenido.

## Contexto

El reto individual R1 exige outbox transaccional, consumidor con deduplicación, reintentos exponenciales, DLQ con reprocesamiento manual y caos con caída real de broker más reinicio del servicio. El outbox de HU-REF-019 ya existe en `parameterization.outbox_event`; se reutiliza su transacción de negocio, sin acreditar la base previa como código nuevo.

El relay y el consumidor tienen ventanas de fallo diferentes: una publicación puede ser reentregada, y el proceso puede caer después de aplicar un efecto pero antes de emitir ACK. Guardar solo el ID sin el efecto en la misma transacción pierde trabajo; aplicar el efecto sin deduplicación lo duplica. La DLQ histórica tiene retención de siete días y no debe reconfigurarse destructivamente para consumidores existentes.

## Decisión

Se decide entregar al menos una vez y aplicar un efecto idempotente por `(consumer_name, event_id)` mediante una inbox transaccional en el esquema de Reference Data.

1. **Publicación persistida:** el relay reutiliza `event_id`, payload y fecha original del outbox en todos los reintentos/reinicios; utiliza publisher confirms. Si fallan la ruta normal y la DLQ, la fila permanece pendiente/fallida para recuperación. `published` acredita entrega al broker/DLQ, no ejecución exitosa del consumidor.
2. **Efecto real y acotado:** el consumidor `reference-data.projection.v1` actualiza `parameterization.event_projection`, un read model operativo de eventos de catálogo y centro. No vuelve a insertar el catálogo ni se presenta como implementación de audit-service/scheduling-service.
3. **Atomicidad:** insertar inbox y actualizar proyección en una misma transacción PostgreSQL antes del ACK. Una inserción repetida con el mismo contenido no incrementa `applied_events`; el mismo ID con contenido diferente se rechaza. El hash SHA-256 se calcula sobre tipo de evento y JSON compactado; no es firma ni canonicalización semántica completa.
4. **Modelo nuevo:** changesets nuevos `r1-reference-inbox-projection-001` y `r1-reference-inbox-projection-grants-001`; no alterar checksums históricos. Claves técnicas compuestas, UUID para evento/agregado, JSONB para payload, TIMESTAMPTZ UTC y contador positivo. `reference_writer` recibe SELECT/INSERT de inbox y SELECT/INSERT/UPDATE de proyección; `reference_reader`, solo SELECT de proyección. El borrado de inbox queda fuera del flujo de aplicación para no reabrir duplicados.
5. **Consumidor:** ACK manual, QoS 1, reconexión y validación del envelope. Antes del ACK del mensaje original, confirmar cualquier transferencia a retry/DLQ; si no se confirma, NACK/requeue y reconectar.
6. **Topología de R1:** cola quorum `reference-data.projection`; colas quorum de retry `reference-data.projection.retry.1000`, `.2000`, `.4000`, con TTL 1/2/4 s, `x-overflow=reject-publish` y dead-lettering `at-least-once`; DLQ durable `reference-data.projection.dlq` sin expiración automática, exchange `reference-data.projection.dlx`. Mantener la DLQ histórica `reference-data-events.dlq` para compatibilidad sin redefinir sus argumentos. Los reintentos del publicador también usan 1/2/4 s.
7. **Replay:** comando operativo acotado (`cmd/reference-data-replay`, límite 1..1000, default 10), conserva cuerpo y MessageID, reinicia la cabecera de intentos y confirma la publicación antes del ACK de la DLQ. Se ejecuta después de corregir la causa; no necesita una pantalla administrativa nueva.
8. **Verificación obligatoria:** rollback de negocio+outbox, doce entregas concurrentes con un efecto, rollback de inbox ante fallo de la proyección, retry 1/2/4/DLQ/replay real y caos automatizado. Desde el navegador, crear A, detener broker, crear B, reiniciar el servicio con el broker detenido, recuperar broker y comprobar dos originales con dos efectos. Reenviar ambos manteniendo IDs; una barrera FIFO posterior permite medir después del procesamiento. La barrera no entra en esos conteos.
9. **Estado de la entrega:** resultados locales anteriores no sustituyen una ejecución sobre los SHA del macroproyecto. No marcar aceptado, aprobado o Done·Dev hasta revisión y merge originales. ADR/informe/evidencias permanecen en docs; los repositorios de código reciben solo implementación y pruebas/configuración.

## Ownership y permanencia propuestos

Arquitectura debe ratificar este reparto por rol. La implementación es de Reference Data; no se atribuye a IAM, audit-service ni a un consumidor de otro dominio.

| Activo | Propietario funcional/técnico propuesto | Responsabilidad operativa propuesta |
|---|---|---|
| parameterization.outbox_event y relay | Equipo Reference Data Service; esquema en Reference Data DB | Servicio publica con identidad persistida; Datos aplica changesets y rollback autorizado |
| parameterization.event_inbox | Equipo Reference Data, para reference-data.projection.v1 | Servicio inserta/deduplica; Datos administra esquema/permisos; no tiene limpieza automática aprobada |
| parameterization.event_projection | Equipo Reference Data; read model operativo de eventos de catálogo/centro | Servicio actualiza en la misma transacción que inbox; no es fuente maestra ni auditoría transversal |
| Grants y rollback | Equipo propietario de Reference Data DB con Datos | Versionar cambios; revisar mínimo privilegio; no ejecutar rollback destructivo sin coordinar consumidor/replay |
| Colas, exchanges y vhost/credenciales RabbitMQ | Plataforma/DevOps, con topología versionada por Reference Data | Operar broker, capacidad, persistencia y políticas; coordinar cambios incompatibles |
| Diagnóstico de mensajes y replay | Responsable operativo por designar, con equipo Reference Data | Corregir causa, autorizar lote limitado, ejecutar y verificar el efecto; QA conserva evidencia |

Se propone mantener inbox y proyección como estructuras técnicas permanentes mientras exista este consumidor, no como fixtures temporales de la demostración. Su aceptación definitiva corresponde a Arquitectura y Datos. No se crean rutas de lectura de negocio nuevas ni un acuerdo de servicio transversal por esta propuesta.

## Retención, reconstrucción y rollback

No se introduce una caducidad arbitraria: la ventana máxima de reentrega/replay, conservación de outbox/DLQ, volumen previsto y recuperación requerida deben acordarse antes de aprobar purga o archivo. Eliminar una clave de inbox permite volver a aplicar un evento antiguo; eliminar la proyección no es seguro sin definir la fuente completa y el procedimiento de reconstrucción.

Hasta esa decisión no hay un job de limpieza aprobado ni privilegio DELETE de inbox para la aplicación. La DLQ nueva no expira automáticamente; ello exige seguimiento de capacidad, no supone almacenamiento infinito. El TTL de la DLQ heredada sigue sin alterarse.

Una reconstrucción debe indicar si conserva inbox o usa otra versión de consumidor y cómo obtiene la historia completa, evitando mezclar estado previo y eventos reproducidos. La estrategia concreta, los plazos de retención y los umbrales operativos siguen ABIERTOS; no se afirma que ya haya automatización de archivo o reconstrucción.

El rollback de las dos estructuras elimina memoria de deduplicación y efectos: en un ambiente compartido requiere detener consumidores, preservar evidencia/datos según el plan aprobado y coordinar cualquier replay. El 22/10 se verificó con Liquibase aplicación, rollback de los dos changesets R1 y reaplicación en una base nueva aislada; no se revirtió la base de demostración ni develop compartido.

## Topología y responsabilidades de recuperación

La declaración de las colas de proyección está versionada en [internal/adapter/out/messaging/consumer.go](https://github.com/code-sena/design-software-reference-data-service/blob/068593f715cfd3647e2b506aa17b64c3e5a9b95f/internal/adapter/out/messaging/consumer.go). Las colas/retry/DLQ descritas en la decisión 6 son las implementadas; el broker es operado por Plataforma/DevOps y la semántica de sus mensajes corresponde a Reference Data. Cambiar argumentos incompatibles de una cola existente requiere un plan explícito; no se elimina ni redeclara destructivamente la cola heredada para hacer pasar una prueba.

El flujo operativo propuesto es: observar el fallo, identificar/corregir su causa, autorizar un lote de replay, ejecutarlo conservando ID/cuerpo, verificar confirmaciones y efectos, y registrar el resultado. El publicador confirma antes de liberar el mensaje de DLQ. No se autorizan reenvíos ilimitados ni cambios manuales de event_id para saltar la deduplicación.

El comando [cmd/reference-data-replay/main.go](https://github.com/code-sena/design-software-reference-data-service/blob/068593f715cfd3647e2b506aa17b64c3e5a9b95f/cmd/reference-data-replay/main.go) limita el lote (1..1000, predeterminado 10). La designación de quién puede operarlo, los permisos de broker y los procedimientos de escalamiento deben ser ratificados por Arquitectura/Plataforma; describir el comando no otorga acceso a usuarios.

## Evidencia y dependencia de integración

- Esquema/permisos/rollback: [PR #81](https://github.com/code-sena/design-software-reference-data-db/pull/81), HEAD `be3d4810dd3f8602979722b8a132d779c7e9a192`; migración formalmente publicada, pendiente de merge.
- Implementación: [PR #26](https://github.com/code-sena/design-software-reference-data-service/pull/26), HEAD `068593f715cfd3647e2b506aa17b64c3e5a9b95f`; no integrar el consumidor sin las tablas y grants de ese PR de DB.
- Pruebas: [internal/adapter/out/messaging/r1_integration_test.go](https://github.com/code-sena/design-software-reference-data-service/blob/068593f715cfd3647e2b506aa17b64c3e5a9b95f/internal/adapter/out/messaging/r1_integration_test.go); atomicidad, deduplicación concurrente, rechazo de ID/contenido distinto, retries/DLQ/replay y caos real.
- [CI del shell #39862188250, intento 2](https://github.com/code-sena/design-software-web-shell/actions/runs/39862188250): ambos jobs SUCCESS sobre `e91a2c0b687e5ade246553eb05ea7bc837f908aa`, con suite completa R1 y tres Chromium. El run registra las revisiones de las dependencias. No se certifica con él un HEAD futuro del shell ni las 71 pruebas del MFE.
- Métricas locales verificadas el 22/10: seis eventos originales, doce reenvíos deliberados, cero pérdidas y cero efectos duplicados; escenario UI separado con dos originales/dos reenvíos. No sumar ambos escenarios como una única muestra ni contar la barrera FIFO.

La política de integración por dependencias y los estados CI actuales se mantienen en [ADR-020](./ADR-020-reference-data-iam-e2e-integration.md) y [la matriz de Calidad](../../../11-quality/reference-data-hu-ref-020-r1-validation.md). Al corte 2026-10-24, el MFE conserva CI propio bloqueado por acceso privado y shell tiene conflicto con develop pese al run previo aprobado.

## Trazabilidad de las decisiones pendientes de Arquitectura

| Punto de revalidación | Respuesta de esta propuesta | Pendiente de ratificación |
|---|---|---|
| Ownership/permanencia de inbox y proyección | Estructuras técnicas de Reference Data, cambios en su DB | Confirmar responsables y permanencia |
| Grants asociados | Mínimo privilegio explícito en decisión 4 y PR DB #81 | Aceptación por Datos/Arquitectura |
| Topología y responsabilidades RabbitMQ | Topología versionada, semántica de dominio y operación de Plataforma separadas | Designar custodios, capacidad y controles de cambios |
| Retención/replay | Sin purga automática que rompa deduplicación; replay limitado y posterior a corregir causa | Aprobar ventana, archivo/reconstrucción, operador y permisos |
| Integración DB/Service/Infra/Shell | Dependencias enlazadas y pruebas por SHA | Revisar/mergear en orden; revalidar cambios de HEAD |

Los puntos de ownership, retención y operación quedan registrados como PA-REF-03, PA-REF-04 y PA-REF-05 en [preguntas abiertas](../../../15-project-control/open-questions.md).

El ADR sigue PROPOSED. Las pruebas técnicas no sustituyen la aceptación del modelo ni autorizan merges, rollback o replay en ambientes compartidos.

## Consecuencias

### Positivas

- El negocio puede confirmar su transacción durante la indisponibilidad de RabbitMQ.
- Reinicio y reentrega no repiten el efecto confirmado de la proyección.
- La DLQ conserva el mensaje para diagnóstico y replay explícito.

### Negativas / Trade-offs

- Inbox, proyección, outbox y DLQ ocupan almacenamiento; no se elimina deduplicación sin definir una política de replay/retención compatible.
- QoS 1 y una barrera FIFO simplifican la prueba local; no establecen orden total entre consumidores distribuidos.
- La proyección verifica un efecto persistente específico, no todos los efectos posibles de otros dominios.

### Riesgos

- Un RabbitMQ de un nodo con volumen no constituye alta disponibilidad ante pérdida permanente de disco.
- Se requiere almacenamiento persistente y permisos de aplicación mínimos; el superusuario se limita al verificador/migraciones de la base aislada.
- La prueba de caos solo puede detener/reiniciar el proyecto de validación, nunca el broker compartido de otros equipos.

## Alternativas consideradas

| Alternativa | Por qué se descarta |
|---|---|
| Enviar al broker dentro del request sin outbox | El commit de negocio y la publicación no son atómicos |
| Marcar inbox antes de una transacción separada del efecto | Puede perder el efecto si cae entre ambas escrituras |
| ACK antes de confirmar el efecto o el retry | Puede perder mensajes ante una caída |
| Regenerar el ID en cada reintento | El consumidor ya no reconoce la misma entrega lógica |
| Cambiar los argumentos de la DLQ existente | Rompe declaraciones RabbitMQ y consumidores desplegados |
| Afirmar exactly-once universal | El mecanismo garantiza idempotencia del efecto documentado sobre entrega al menos una vez |

## Referencias

- [ADR-001: RabbitMQ](./ADR-001-message-broker.md), [ADR-004: modelado](./ADR-004-status-parametrization-and-audit-standard.md), [ADR-020: integración](./ADR-020-reference-data-iam-e2e-integration.md).
- [Modelo del servicio](../../../09-microservices/services/02-reference-data-service/data-model.md), [diccionario](../../../06-data/data-dictionary.md), [eventos](../../../09-microservices/services/02-reference-data-service/events.md).
- [Plan de validación](../../../11-quality/reference-data-hu-ref-020-r1-validation.md), [operación](../../../10-devops/reference-data-integration.md).
- [RabbitMQ 3.13: quorum queues y dead-lettering](https://www.rabbitmq.com/docs/3.13/quorum-queues).
