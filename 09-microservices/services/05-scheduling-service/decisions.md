# Decisiones internas — scheduling-service

estado 🟢 Estable — 2026-10-18

> Para decisiones que afectan más de un servicio → crear ADR en `05-architecture/decisions/records/`
> Ver ADR-001 (motor del workflow), ADR-002 (read models para dependencias síncronas) y ADR-010 (endurecimiento de seguridad R4)

| # | Decisión | Alternativas descartadas | Motivo | Fecha |
|---|----------|--------------------------|--------|-------|
| 01 | La detección de conflictos es responsabilidad de scheduling-service, no de los servicios fuente | Cada servicio valida sus propios conflictos | El conflicto es una propiedad de la combinación instructor+ambiente+franja, no de cada recurso por separado | 2026-06-17 |
| 02 | Un horario en estado BORRADOR no bloquea recursos | Bloquear desde BORRADOR | Reduce fricción en la fase de diseño del horario | 2026-06-17 |
| 03 | Un horario PUBLICADO es inmutable — cambios requieren un nuevo BORRADOR | Edición in-place del horario publicado | Garantiza que instructores y aprendices tengan siempre la versión correcta; el historial de versiones es auditable sin reconstrucción | 2026-06-17 |
| 04 | Read models locales de disponibilidad de instructor y ambiente (ADR-002) | Consultar instructor-service y environment-service en tiempo real para cada validación | Elimina dependencias síncronas en el camino crítico de validación; el scheduling-service puede operar aunque los servicios fuente estén degradados | 2026-06-20 |
| 05 | Patrón Outbox para el evento `schedule.published` | Publicar directamente al broker en el mismo request HTTP | Evita split-brain: si el broker falla después del commit la fila de outbox garantiza entrega eventual; se elimina la posibilidad de un horario publicado en BD sin evento emitido | 2026-06-20 |
| 06 | `class_session` almacena `start_time`, `end_time` y `day_of_week` desnormalizados | Derivar esos campos haciendo JOIN a `time_slot` en cada consulta | La detección de conflictos necesita comparar rangos horarios sobre miles de sesiones; el JOIN repetido escala O(n·log n) con índices compuestos mientras que el acceso directo es O(1) por sesión; la desnormalización se justifica porque `time_slot` es inmutable una vez creado | 2026-06-20 |
| 07 | `time_slot` como plantilla reutilizable (no rangos start/end ad-hoc en cada sesión) | Permitir que cada sesión defina su propio rango horario libre | Estandariza los bloques del horario institucional; evita franjas fragmentadas que generarían falsos negativos en la detección de conflictos; facilita la reasignación masiva cuando el instituto cambia sus bloques | 2026-06-20 |
| 08 | La detección de conflictos es eager (se ejecuta en VALIDATE) no lazy (no se ejecuta en INSERT) | Detectar conflictos solo al intentar publicar o al persistir cada sesión | Permite editar borradores libremente sin bloqueos; la validación explícita al transicionar a PUBLISHED_PENDING es el único punto de falla controlado; errores se reportan todos juntos, no uno por uno durante la carga | 2026-06-20 |
| 09 | Validación asimétrica RS256 con JWKS de IAM, autorización RBAC por `SCH_*` features, política Fail-Closed y respuesta 404 ante IDOR (ADR-010) | Confiar en cabeceras perimetrales sin verificar firma; usar claves compartidas simétricas; retornar 403 en consultas directas a recursos ajenos | Previene suplantación de identidad (spoofing), ataques alg:none, fuga de metadatos de horarios de otros centros y manipulación de parámetros de auditoría (`publishedBy`); validado con suite de 17 pruebas negativas automatizadas | 2026-10-18 |
