# Informe técnico — R2 Rendimiento y datos de Scheduling

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: JuanCarlosJC-20 (medición original), con verificación a escala realista del dueño del proyecto | Equipo: Scheduling

## 1. Identificación

| Campo | Valor |
|---|---|
| Dominio | Scheduling |
| Reto | R2 — Rendimiento y datos |
| HU | [HU-SCH-017: Scheduling read-path performance (R2)](https://github.com/code-sena/design-software-docs/issues/374) |
| Decisión | [ADR-027](../05-architecture/decisions/records/ADR-027-scheduling-r2-performance.md) (PROPOSED) |
| Servicio | `scheduling-service`, PR #18: compresión JSON y `spring.jpa.open-in-view=false` en `application.properties` |
| Base de datos | `scheduling-db`, PR #60: changeset `r2-scheduling-read-path-indexes-20261020` |
| Entorno de la medición original | Docker local, PostgreSQL 16, k6 0.54.0, 2026-10-23 |

## 2. Alcance

R2 pide k6 con 50 VUs durante 5 minutos (p95 < 300 ms, errores < 1 %), el ranking de las tres consultas SQL más costosas, `EXPLAIN (ANALYZE, BUFFERS)` antes y después, un changeset reversible con rollback probado y cifras comparables.

Cambios entregados:

- `scheduling-db`: dos índices parciales sobre filas activas.
  - `ix_schedule_active_created_at` sobre `schedule(created_at) WHERE is_active = true`.
  - `ix_class_session_active_schedule_date` sobre `class_session(schedule_id, session_date) WHERE is_active = true`.
  - Rollback: elimina ambos (`05_rollbacks/01_ddl/10_indexes/003_drop_r2_read_indexes.sql`).
- `scheduling-service`: `server.compression.*` (JSON desde 1 KB) y `spring.jpa.open-in-view=false`. Es configuración de producción, no lógica Java; es la misma en los cuatro ambientes.

## 3. Carga k6 (escala pequeña)

Dataset local: 501 horarios, 10 000 sesiones y 6 franjas. Tráfico directo a `scheduling-api:8080` dentro de Compose (sin Traefik, para que su límite de tasa no condicione la prueba). JWT real de IAM.

| Estado | Configuración | p95 HTTP | Errores | Solicitudes | Checks |
|---|---|---:|---:|---:|---:|
| Antes | Sin índices R2, sin compresión, `open-in-view=true` | 10.18 ms | 0 % | 44 345 | 100 % |
| Después | Con índices R2, compresión, `open-in-view=false` | 10.27 ms | 0 % | 44 318 | 100 % |

Ambas corridas cumplen los umbrales (50 VUs, 5 min). **La diferencia (+0.09 ms) no es una mejora de latencia HTTP.** Con 10 000 sesiones repartidas entre 501 horarios (unas 20 por horario) el ordenamiento es trivial y la caché estaba caliente en la segunda corrida; esta prueba no puede mostrar el beneficio de los índices. La discrepancia entre las 7 franjas esperadas por el seed y las 6 observadas no se pudo explicar con la evidencia conservada (`ON CONFLICT (id) DO NOTHING` no garantiza las cinco inserciones).

## 4. Consultas más costosas (`pg_stat_statements`, escala pequeña)

| Consulta | Antes: total / media | Después: total / media |
|---|---:|---:|
| Listado paginado de horarios activos por `created_at` | 3 976.409 ms / 0.269 ms | 1 126.997 ms / 0.076 ms |
| Listado paginado de sesiones activas por horario y `session_date` | 1 479.420 ms / 0.100 ms | 1 408.637 ms / 0.095 ms |
| Conteo de horarios activos | 1 331.164 ms / 0.090 ms | 1 436.776 ms / 0.097 ms |

Cada ventana tuvo 14 781 y 14 772 llamadas por consulta. El top 3 fue el mismo conjunto en ambas; cambió el orden.

## 5. `EXPLAIN (ANALYZE, BUFFERS)` a escala pequeña

| Consulta | Plan antes → después | Tiempo antes → después |
|---|---|---:|
| Horarios activos, paginados | Seq Scan + top-N Sort → Index Scan con `ix_schedule_active_created_at` | 0.271 → 0.079 ms |
| Sesiones activas de un horario | Bitmap Scan + Sort → Bitmap Scan con el índice nuevo + Sort | 0.260 → 0.428 ms |
| Conteo de horarios activos | Seq Scan → Seq Scan | 0.113 → 0.104 ms |

La segunda fila se midió sobre un horario con unas 20 sesiones y una sola ejecución en frío (`shared read=2`). Con 20 filas el planificador mantiene el Bitmap Heap Scan + Sort con cualquier índice y una ejecución en frío está dominada por fallos de caché. Esa medición no puede decidir sobre el índice de sesiones; se repitió a escala realista (sección 6).

## 6. Repetición a escala realista (índice de sesiones)

PostgreSQL 16.15 desechable en Docker con el esquema de `develop` de `scheduling-db` aplicado con Liquibase (24 changesets) y datos totalmente sintéticos: 4 000 horarios (3 600 activos) y 480 120 sesiones (456 120 activas). El horario bajo prueba tiene 114 sesiones activas. Mediana de 9 ejecuciones (pasada 1) y de 15 (pasada 2, otro orden) con la caché caliente; tiempo de ejecución en ms, «sin / solo horarios / ambos / solo sesiones» según los índices R2 presentes.

| Consulta | Sin índices R2 | Solo horarios | Ambos (este PR) | Solo sesiones |
|---|---|---|---|---|
| Horarios, página 1 | 18.8 / 9.2 | 0.06 / 0.03 | 0.08 / 0.11 | 11.7 / 13.4 |
| Horarios, página 100 | 15.8 / 7.1 | 2.3 / 1.2 | 2.1 / 1.0 | 8.2 / 19.7 |
| Sesiones de un horario, página 1 | 0.60 / 0.69 | 0.81 / 0.76 | 0.11 / 0.15 | 0.11 / 0.14 |
| Sesiones con rango de `session_date` | 0.76 / 0.67 | 0.42 / 0.17 | 0.13 / 0.03 | 0.13 / 0.15 |
| Conteo de horarios activos | No lo afectan los índices R2 (Seq Scan en todas las combinaciones) | | | |

La máquina de la medición estaba compartida, así que los valores absolutos tienen ruido de hasta 2x entre pasadas. Lo fiable es la forma del plan y el orden de magnitud:

- Horarios: `Seq Scan + Sort` → `Index Scan using ix_schedule_active_created_at`, sin Sort. La ganancia crece con el número de horarios activos.
- Sesiones: `Bitmap Heap Scan on ix_class_session_schedule_id + Sort` → `Index Scan using ix_class_session_active_schedule_date`, **sin Sort** (devuelve las filas ya ordenadas por `session_date` y se detiene a las 20).
- Página profunda de sesiones (`OFFSET 100`) y conteo de horarios: sin diferencia estable; no se afirma beneficio.
- Ninguna consulta empeoró su plan con los índices. El índice de sesiones ocupa 18 MB con 480 120 sesiones (el existente `ix_class_session_schedule_id`, 4.4 MB) y, al ser parcial, solo mantiene filas activas.

## 7. Rollback del changeset

Sobre una base con `develop` aplicado, `update` ejecuta exactamente un changeset (`r2-scheduling-read-path-indexes-20261020`), `rollback-count 1` elimina ambos índices y su fila en `DATABASECHANGELOG`, un segundo `update` los recrea y `validate` no reporta errores. Liquibase Community no ofrece `rollback-one-changeset`; por eso se usa `rollback-count 1` sobre el changelog de índices. La medición original del autor hizo la misma comprobación con el changeset productivo en una base aislada.

## 8. Conclusión

- Se conservan ambos índices. El de horarios está justificado desde la escala pequeña; el de sesiones solo se ve a partir de unos cien registros por horario, que es el caso normal de un período completo, y es invisible con 20.
- Si Arquitectura prefiere esperar a medirlo con volúmenes de producción, quitarlo es mecánico: borrar el segundo `CREATE INDEX` de `003_create_r2_read_indexes.sql` y el `DROP INDEX` correspondiente de `003_drop_r2_read_indexes.sql`.
- El p95 de k6 (10.18 → 10.27 ms) no cambió: los índices se justifican por los planes de las secciones 5 y 6, no por esa prueba.
- Límites: la medición original es de Docker local con datos seed y sin Traefik; la repetición es sintética y de una máquina compartida. Ninguna es una garantía de producción.

## 9. Evidencia original retirada de este repositorio

El repositorio de documentación conserva el resultado, no las salidas crudas ni las herramientas. Los archivos originales (salidas de k6 de 951 líneas, resúmenes JSON, logs, planes y los scripts `.ps1`/`.js`) siguen en el historial del PR #338 de `design-software-docs`. El script de k6 proviene del commit `fa02666730c4af01d91075ea021a5c3cac131a8a` del repositorio de la API. Para verificarlos:

| Archivo original | SHA-256 |
|---|---|
| `k6-antes-docker-r2-20261023-161200.txt` | `96b016d51c3c2ef4d60f977ba2691756a5e0ab6ad6e7dc61a91d1be652e5f3a7` |
| `k6-despues-docker-r2-20261023-161200.txt` | `d9a3f0df84fe6f4514be6b12f042f794de5c50c506365b24feaa089ccdc046dd` |
| `k6-antes-docker-r2-20261023-161200-summary.json` | `deb05a187c3ae48c3228d7a9fdb840e57fb8408d142db8cbf56819eb6c4a8787` |
| `k6-despues-docker-r2-20261023-161200-summary.json` | `7e563af49987db83422f4709dc66bb1c7dd96e76aa97068e0127424358f16a73` |
| `pg-statements-r2-antes-docker-20261023.txt` | `f7e3fde8e8541ea684b4d11f1ff1b4ede9aa873661ca1eb2089747e6a588ce6b` |
| `pg-statements-r2-despues-docker-20261023.txt` | `d476d04a889f33c23dbc2a4a97ddbc93455613c4a6957c2c84a95ec6869fccc5` |
| `explain-top-queries-antes-docker-r2-20261023-161200.txt` | `700f8b561289716026991ea296846d0a07f9baff3b776fe0601663a65c9d6d67` |
| `explain-top-queries-despues-docker-r2-20261023-161200.txt` | `f2237e58e2f94ff481c3a0c2d266506903b8b8dd936756358a5133fd9cd51cb1` |
| `explain-r2-top3-queries-20261023.sql` | `01062707e1afd67b8b968f19690c6460b94c16aeed09215878a03f1bccd366ba` |
| `liquibase-r2-production-rollback-20261023-174209.txt` | `518a716eb736a3d5a23c62f9f94f72e0f00dd5928cb9fcba294e7bd3b9552406` |
| `tools/k6/scheduling-load.js` | `10431b521baaf8763a595fa8a295811aca94679f0ce117bacfef6431c23a44f7` |
| `tools/k6/run-r2-docker.ps1` | `c9c711259147f8520e5b71b999b9fef04093fa6e7455f2bd78f6af255768a00b` |
| `tools/windows/verify-r2-liquibase-rollback.ps1` | `8ad83d5e32f52dc22d8976a79cf10704b770e2c967181b5fa32d35e967f6f65b` |

## Referencias

- [ADR-027: Rendimiento de consultas de Scheduling para R2](../05-architecture/decisions/records/ADR-027-scheduling-r2-performance.md)
- [Modelo de datos de scheduling-service](../09-microservices/services/05-scheduling-service/data-model.md)
- [Estrategia de pruebas](./testing-strategy.md)
