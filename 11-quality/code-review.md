# Revisión de código

> Estado: 🟡 En progreso | Última actualización: 2026-08-28
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: Calidad

Criterios y flujo para revisar los cambios del sistema **Horarios SENA**. Hoy los PRs son de tres tipos: **capa de datos** (repos `*-db`: changelogs Liquibase, DDL, seeds), **capa de aplicación ya construida** de `iam-service` (Java/Spring) y `notification-service` (Go) — el stack es **políglota Java + Go**, [ADR-006](../05-architecture/decisions/records/ADR-006-polyglot-stack-strategy.md) — y documentación. El bloque de revisión de código de aplicación **ya aplica** a esos dos servicios. La revisión es obligatoria: ningún cambio entra a una rama padre sin al menos una aprobación (ver [Definition of Done](../00-governance/definition-of-done.md)).

## Flujo de revisión

Alineado con las [convenciones de Git](../00-governance/git-conventions.md) (`develop → qa → staging → main`):

1. El autor abre PR desde su rama hija (`hu-NN-dev`, `feat/*`, `fix/*`, etc.) hacia la rama padre correspondiente.
2. El PR cumple la [Definition of Ready](../00-governance/definition-of-ready.md) antes de solicitar revisión.
3. Se asigna revisor según el **modelo de merge vigente** (ver abajo): hoy un **revisor central** de Arquitectura; a futuro, **CODEOWNERS**. Mínimo **1 aprobación**; para cambios en contratos compartidos (API, modelo de datos, eventos, convenciones de Git) se recomiendan **2**.
4. El revisor aplica el checklist correspondiente y deja comentarios accionables.
5. El autor resuelve los comentarios; los hilos se cierran antes del merge.
6. Merge solo con checks verdes y aprobación. El autor actualiza el `CHANGELOG` si el cambio toca gobernanza, estructura de carpetas o un contrato compartido.

## Checklist base (todo PR)

Deriva de la Definition of Done y de la Definition of Ready:

- [ ] El commit sigue **Conventional Commits**: `<type>(NN-section): descripción en inglés` (tipos permitidos según el repo; ver git-conventions).
- [ ] El cambio es pequeño, atómico y trazable a una HU o tarea.
- [ ] Los enlaces relativos funcionan y el archivo está enlazado desde el `README.md` de su sección (para docs).
- [ ] No hay **secretos** ni datos sensibles: sin credenciales, tokens, `.env` con valores reales, `.pem`/`.key`, ni datos personales de aprendices/instructores (ver [security-rules.md](../00-governance/security-rules.md)).
- [ ] `CHANGELOG` actualizado si aplica (gobernanza, estructura, contrato compartido).
- [ ] Los checks automáticos del PR pasan.

## Checklist de cambios de datos (repos `*-db` / DDL / Liquibase)

Aplica a la capa que existe hoy. Complementa a [modeling-conventions.md](../06-data/modeling-conventions.md) y [migration-strategy.md](../06-data/migration-strategy.md):

- [ ] Cada **changeset** declara `id` + `author` únicos y su **`rollback`** espejo en `05_rollbacks/` con la misma ruta relativa.
- [ ] Se respeta el **orden de aplicación**: tablas sin FK en `03_tables`, FKs vía `ALTER TABLE` en `04_alter`, índices (incluido uno por FK) en `10_indexes`.
- [ ] Cada FK declara acción `ON UPDATE`/`ON DELETE` acorde a la convención (catálogo/padre `RESTRICT`, composición `CASCADE`, opcional `SET NULL`).
- [ ] **Nomenclatura de constraints**: `pk_`, `uq_`, `fk_`, `ck_`, `ix_`.
- [ ] El servicio escribe **solo en su schema** (nunca en `public`); tracking de Liquibase aislado por módulo.
- [ ] **Seeds idempotentes** en `02_dml/` (`ON CONFLICT DO NOTHING`/`MERGE`); datos de prueba aislados con `context`/`labels` para que no lleguen a `staging`/`main`.
- [ ] Lógica almacenada (vistas/funciones/procedimientos/triggers) marcada con **`runOnChange: true`**.
- [ ] **Estados**: los estados de negocio usan el catálogo parametrizable (`status_category`/`status`) según ADR-004; los enums técnicos cerrados permanecen como `VARCHAR + CHECK` (no `ENUM` nativo).
- [ ] Auditoría según estándar: tablas transaccionales con `created_*`/`updated_*`/`deleted_*`, `is_active`, `row_version`; append-only solo con su timestamp de inserción.
- [ ] Migración probada en local: `update` + `status` verdes y `rollback` reversible (ver [testing-strategy.md](./testing-strategy.md)).

## Checklist de código de aplicación (Java + Go — ACTIVO)

Aplica hoy a `iam-service` (Java/Spring) y `notification-service` (Go); se extenderá al resto de servicios a medida que construyan su capa de aplicación.

- [ ] Respeta las fronteras de servicio y la propiedad de datos ([service-boundary-rules.md](../09-microservices/service-boundary-rules.md)); no accede a la BD de otro servicio.
- [ ] Manejo de errores explícito; sin panics (Go) ni excepciones no controladas (Java) en rutas de request.
- [ ] Contratos de API y eventos coherentes con [07-api](../07-api/) y [event-catalog.md](../09-microservices/event-catalog.md).
- [ ] Consumo de eventos **idempotente** (tolera at-least-once): dedup por `event_id` / `source_event_id`.
- [ ] Pruebas unitarias/contrato acompañan al cambio y pasan.

### Ítems derivados de incidentes reales

- [ ] **(Java) Una interfaz OpenAPI generada = un único `@RestController`.** Dos controladores implementando la misma interfaz (`UsersApi`) rompen el arranque por *ambiguous mapping* y los `@WebMvcTest` **no lo cazan**. Todo servicio Java debe tener un `@SpringBootTest` de **contexto completo** (*context-loads*) que arranque el web env (ej. `IamApiApplicationContextTest`). Ver [testing-strategy.md](./testing-strategy.md).
- [ ] **(Go/eventos) E2E con broker/BD frescos.** Las unitarias mockean el use case y no cazan defectos del camino real (incidente notification HU-004: use case devolvía `nil`). Toda HU de consumo/entrega exige E2E que cubra happy path, DLQ e idempotencia.
- [ ] **OTLP por stack.** El exportador de trazas depende del runtime: el agente Java exporta a `:4318` (http/protobuf), el SDK Go a `:4317` (gRPC) y en Python el protocolo lo decide el paquete exportador que se importa (`monitoring` usa el HTTP, `:4318`). Revisar que el endpoint del servicio coincida con su stack.
- [ ] **Outbox: envelope y renombrado `data`→`payload`.** El evento se persiste bajo `data` y el relay lo publica como `payload`; verificar que la transacción escriba el registro y el outbox juntos, y la idempotencia por `event_id`.
- [ ] **Gate Pact verde.** El check de contrato (Pact) debe pasar para los pares productor/consumidor construidos; se trata como **bloqueante** de la revisión.
- [ ] **Sync de docs SSOT si el PR toca schema.** Un cambio de esquema (`-db`) obliga a actualizar en la misma entrega el `data-model.md` del servicio y el diccionario de datos ([06-data](../06-data/)); la HU no cierra sin ese sync.

> El detalle fino de este bloque (estilo, linters por stack, umbral de cobertura, automatización del gate Pact) sigue siendo **punto abierto** hasta que exista pipeline de CI (ver deuda HU-NOTIF-009 / docs#78 en [testing-strategy.md](./testing-strategy.md)).

## Modelo de merge y asignación de revisores

El modelo real hoy es **revisor central + merge por admin vía ruleset**: un revisor central (Arquitectura) revisa los PRs de las ramas hijas hacia la rama padre, y el **merge lo ejecuta un admin** porque el *ruleset* del repositorio protege las ramas padre. Los autores no auto-mergean sobre ramas padre. Esto es consistente con el flujo git de ramas hijas (`hu-NN-dev`, `feat/*`, `fix/*`) descrito arriba.

La intención a futuro es delegar la asignación automática al archivo `CODEOWNERS`:

- Cambios de **gobernanza** (`00-governance/`), **datos** (`06-data/`) y **arquitectura** (`05-architecture/`, ADRs) → equipos de Arquitectura/Datos.
- Cada repo de servicio (`*-db` y el de aplicación) → owner del servicio correspondiente (ver [service-catalog.md](../09-microservices/service-catalog.md)).

> **Punto abierto:** el archivo `CODEOWNERS` definitivo (handles reales por servicio/carpeta) está por completar; **mientras tanto, la asignación la coordina el revisor central de Arquitectura** y el merge lo aplica un admin por el ruleset.

## Tono de la revisión

- Comentarios accionables y específicos; distinguir bloqueante de sugerencia.
- Preferir preguntas a imperativos cuando haya duda de intención.
- Revisar la **intención del cambio** (¿resuelve la HU?), no solo la sintaxis.
