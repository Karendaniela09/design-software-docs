# ADR-016: Rendimiento reproducible de las consultas de Auditoría

**Estado:** ACCEPTED
**Fecha:** 2026-10-21
**Autores:** Freinier Cardona
**Equipos involucrados:** Auditoría, Datos, DevOps, QA

## Contexto

`audit.audit_record` conserva el histórico append-only y está particionado por
`received_at`. La API de lectura mantiene tres recorridos que pueden procesar
volúmenes altos: listado acotado por centro y tipo de evento, listado por
servicio origen y exportación acotada por centro. Los tres conservan el orden
contractual `received_at DESC, id DESC`.

Los índices de una sola columna obligaban a ordenar conjuntos grandes para esos
recorridos. El R2 del plan de mejoramiento exige una carga autenticada de 50
usuarios virtuales durante cinco minutos, p95 menor de 300 ms, errores menores
del 1 %, comparación de tres planes `EXPLAIN (ANALYZE, BUFFERS)` y una migración
Liquibase reversible con evidencia antes y después.

## Decisión

Se decide añadir exactamente tres índices compuestos y ordenados en
`design-software-audit-db`:

1. `(training_center_id, event_type, received_at DESC, id DESC)` para el
   listado filtrado por centro y tipo.
2. `(source_service, received_at DESC, id DESC)` para el listado por servicio
   origen.
3. `(training_center_id, received_at DESC, id DESC)` para la exportación por
   centro.

Los índices se entregan en el changeset Liquibase
`r2-audit-performance-query-indexes` y su rollback elimina los tres objetos.
La aplicación no cambia rutas, autorización, cursor, particionado ni el modelo
append-only.

La carga se define con k6 junto al código ejecutable. Obtiene una credencial
IAM una sola vez en `setup`, la conserva únicamente en memoria y prueba lista,
detalle y exportación mediante la API real. Los valores de ejecución se reciben
desde archivos `.env` locales no versionados; las plantillas y Compose permiten
reproducir el entorno después de clonar los repositorios.

## Consecuencias

### Positivas

- PostgreSQL puede satisfacer filtro y orden mediante scans ordenados para las
  tres consultas medidas.
- La evidencia de planes y rollback es repetible en un proyecto Compose aislado.
- La carga no crea rutas de prueba ni evita IAM, permisos o alcance de datos.

### Negativas / trade-offs

- Cada índice aumenta el costo de escritura y almacenamiento del histórico.
- Las cifras de p95 dependen de recursos Docker, datos y cuenta IAM del entorno;
  el arnés conserva resultados separados para repetir la comparación.

### Riesgos

- Agregar índices para todos los filtros opcionales sin medición degradaría las
  escrituras; cualquier índice adicional requiere una nueva comparación.
- Un token estático o credenciales versionadas invalidarían la prueba y la regla
  de secretos del proyecto.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Índices de una sola columna y sort posterior | No evita los sorts o scans grandes observados en las tres rutas. |
| Un índice para cada filtro opcional | No responde a una ruta medida y aumenta innecesariamente el costo de insert. |
| Ruta HTTP o token de prueba estático | Cambiaría el contrato y eludiría la autenticación que R2 debe medir. |
| Ejecutar el rollback manualmente fuera de Liquibase | No deja trazabilidad ni asegura reversibilidad desplegable. |

## Referencias

- [R2 technical report and acceptance criteria](../../../11-quality/qa-report-r2-audit-service.md)
- [Ficha de audit-service](../../../09-microservices/services/09-audit-service/README.md)
- `design-software-audit-db/01_ddl/10_indexes/002_add_audit_query_performance_indexes.sql`
- `design-software-audit-db/05_rollbacks/01_ddl/10_indexes/002_add_audit_query_performance_indexes.rollback.sql`
- `design-software-audit-service/performance/k6/audit-query.js`
