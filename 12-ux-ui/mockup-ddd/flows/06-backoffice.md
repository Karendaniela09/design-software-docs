<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: DDD de flujo UX (Back-office / Soporte) + prompts Stitch
fase: diseño (UX/UI)
estado: draft
dependencias_entrada: 07-api/contracts/openapi/document.yaml, template.yaml, reference-data.yaml;
  09-microservices/services/07-document-service/data-model.md,
  02-reference-data-service/data-model.md, 09-audit-service/data-model.md;
  09-audit-service/components/audit-worker/contract.md; event-catalog.md;
  01-iam-service/rbac-design.md (MOD_AUDIT); 04-requirements/functional.md, user-stories.md;
  mockup-ddd/micro-frontends.md (mapeo MFE)
consumidores_siguientes: Google Stitch; validación de diseño; construcción de document-mfe,
  audit-mfe y reference-mfe
tldr: Pantallas de soporte back-office (documentos, plantillas, auditoría, parametrización)
  maduradas a cobertura completa: 4 pantallas base + 5 pantallas/modales nuevos (detalle de
  documento+versiones, generar documento, editor/preview de plantilla, detalle de registro de
  auditoría, formularios CRUD de parametrización), cada una etiquetada con su MFE dueño
  (document-mfe / audit-mfe / reference-mfe), derivadas de los contratos document/template/
  reference-data reales y del modelo de datos de audit-service, con prompts listos para Stitch.
decisiones_clave: storage_key nunca se muestra (write-only); descarga solo por URL firmada de la
  versión vigente; auditoría es de solo lectura y append-only (sin fragmentar su estado en
  pantallas adicionales); catálogos/parámetros solo editables por ADMIN_STAFF/SYSTEM_ADMIN
  (RN-REF-03); code/key inmutables tras creación en plantilla, catálogo, valor de catálogo y
  parámetro
halts_registrados: ninguno para Auditoría. El contrato canónico de audit-service declara la consulta
  de solo lectura (`GET /api/v1/audit-records`) sobre el modelo real de `audit_record` y las features
  RBAC `AUDIT_LOG_VIEW` y `AUDIT_EXPORT`. No se inventan campos: los mostrados son los reales del
  data-model de audit-service.
-->

# Flujo — Back-office / Soporte (documentos, auditoría, parametrización)

> **ESTADO: PRELIMINAR (v0).** Igual que el resto del DDD, este flujo es un instrumento de
> descubrimiento para Stitch, no un diseño final. La trazabilidad a **endpoint + tabla** es
> completa; donde no existe `HU-##` en `04-requirements/user-stories.md` se marca `HU: pendiente`.
> **Rol:** `ADMIN_STAFF` / `SYSTEM_ADMIN` (área de soporte, dentro del bucket "Administración" de
> [navigation-map.md](../../navigation-map.md); el mapa aún no detalla rutas de back-office, así
> que las rutas de este archivo son propuestas v0). Todas las pantallas se montan dentro del
> **app shell** ya definido en [01-auth.md § Pantalla 4](./01-auth.md#pantalla-4--app-shell-marco-por-rol)
> (barra superior + nav lateral), bajo un ítem de nav "Soporte" con sub-secciones Documentos,
> Plantillas, Auditoría y Parametrización. **MFE dueño por sub-sección** (ver
> [micro-frontends.md](../micro-frontends.md)): Documentos y Plantillas → `document-mfe`;
> Auditoría → `audit-mfe`; Parametrización → `reference-mfe`. El `shell-host` solo aporta el marco
> (barra superior, nav, sesión); no contiene lógica de dominio de este flujo.

**Servicios origen:** `document-service` · `reference-data-service` · `audit-service`
**Micro-frontends:** `document-mfe` (Pantallas 1, 2, 5, 6, 7) · `audit-mfe` (Pantallas 3, 8) ·
`reference-mfe` (Pantallas 4, 9)
**Contratos:** `../../../07-api/contracts/openapi/document.yaml` ·
`../../../07-api/contracts/openapi/template.yaml` ·
`../../../07-api/contracts/openapi/reference-data.yaml`
**Modelos:** `../../../09-microservices/services/07-document-service/data-model.md` ·
`../../../09-microservices/services/02-reference-data-service/data-model.md` ·
`../../../09-microservices/services/09-audit-service/data-model.md`

---

## Pantalla 1 — Documentos

- **Ruta:** `/backoffice/documentos` · **Rol:** `ADMIN_STAFF`/`SYSTEM_ADMIN` · **MFE:** `document-mfe`
  · **HU:** pendiente
  *(RF-DOC-01, RF-DOC-02 en functional.md cubren generación/versionado; no hay HU de pantalla de
  soporte)*
- **Endpoints:**
  - `GET /api/v1/documents` (`DOC_DOCUMENT_VIEW`) — lista paginada. Filtros: `domain`, `status`,
    `owner_service`, `owner_entity_id`; paginación `page`/`page_size`/`sort`.
  - `POST /api/v1/documents/generate` (`DOC_DOCUMENT_GENERATE`) — genera un documento de forma
    asíncrona a partir de una plantilla.
  - `GET /api/v1/documents/{id}` (`DOC_DOCUMENT_VIEW`) — detalle.
  - `GET /api/v1/documents/{id}/versions` (`DOC_VERSION_VIEW`) — historial de `document_version`.
  - `GET /api/v1/documents/{id}/download-url` (`DOC_DOWNLOAD`) — URL firmada (TTL 300 s) de la
    versión vigente; requiere `status = AVAILABLE`.
  - `DELETE /api/v1/documents/{id}` (`DOC_DOCUMENT_MANAGE`) — archiva (soft delete, `status = ARCHIVED`).
- **Campos reales (`Document`):** `id`, `template_id` (nullable), `title`, `domain` (`SCHEDULE` /
  `FICHA` / `CERTIFICATE` / `ACTOR` / `REPORT`), `owner_service`, `owner_entity_id`, `mime_type`,
  `size_bytes` (nullable), `status` (`GENERATING` / `AVAILABLE` / `ARCHIVED` / `EXPIRED` /
  `GENERATION_FAILED`), `row_version`, `created_by`, `created_at`, `updated_at`.
  **Nota:** `storage_key` es `writeOnly` — **nunca** se retorna ni se muestra; la descarga se
  resuelve siempre vía `download-url`.
- **Campos reales (`DocumentVersion`):** `id`, `document_id`, `version_number`, `created_by`,
  `created_at`, `notes` (nullable). Solo la versión vigente es descargable en este contrato v1
  (no hay descarga por `version_id`); versiones previas se listan como metadata/historial.

**Propósito:** dar soporte a coordinadores/administradores para localizar, regenerar, versionar y
descargar documentos generados por el sistema (constancias, horarios publicados, reportes), sin
exponer nunca la ruta interna de almacenamiento.

**Layout:**
- **Filtros** (barra superior de la tabla): select **Dominio** (`domain`), select **Estado**
  (`status`), campo **Servicio propietario** (`owner_service`, texto), campo **Entidad propietaria**
  (`owner_entity_id`, UUID — no existe endpoint transversal de búsqueda por nombre, se filtra por
  UUID exacto). Botón **Generar documento** a la derecha.
- **Tabla** (paginada): columnas Título, Dominio, Servicio propietario, Estado (badge con
  icono+texto: `GENERATING` neutro/spinner, `AVAILABLE` éxito, `ARCHIVED` neutro, `EXPIRED`
  advertencia, `GENERATION_FAILED` crítico), Actualizado (`updated_at`). Fila con acciones: **Ver
  detalle**, **Descargar** (deshabilitado si `status ≠ AVAILABLE`), **Archivar**.
- **Paginación** (al pie de la tabla, REAL y visible): barra ‹ anterior · 1 2 3 … › siguiente,
  selector de tamaño de página (`page_size`: 10/20/50) y texto **"Mostrando X–Y de N"**, alineados
  a los parámetros `page`/`page_size`/`sort` de `GET /documents`.
- **Panel de detalle** (lateral, al seleccionar fila): metadatos del documento + sección
  **Versiones** (tabla `version_number`, `created_by`, `created_at`, `notes`) + botón **Descargar
  versión vigente**.
- **Modal "Generar documento":** select **Plantilla** (`template_code`, alimentado por
  `document-templates` activos), select **Dominio**, campo **Servicio propietario**, campo
  **Entidad propietaria** (UUID), campo **Título**, editor JSON opcional **Datos** (`data`, contexto
  para el renderizador). Botón **Generar**.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Generar documento | `POST /documents/generate` | `202` → `document_id`, `status = GENERATING`; la fila aparece con badge "Generando…" y se sondea `GET /documents/{id}` hasta `AVAILABLE`/`GENERATION_FAILED` |
| Ver detalle | `GET /documents/{id}` | abre panel lateral |
| Ver versiones | `GET /documents/{id}/versions` | lista historial en el panel |
| Descargar | `GET /documents/{id}/download-url` | abre la URL firmada en pestaña nueva; error si `status ≠ AVAILABLE` (`409`) |
| Archivar | `DELETE /documents/{id}` | `204` → `status = ARCHIVED`; fila se atenúa, ya no descargable |

**Estados:** *loading* (skeleton de filas) · *empty* ("No hay documentos que coincidan con los
filtros") · *error* (banner de red/permisos, `401`/`403`) · *generando* (badge con spinner en la
fila mientras `status = GENERATING`) · *error de generación* (`GENERATION_FAILED`, badge crítico +
icono, con acción "Reintentar" que reabre el modal prellenado).

```text
PROMPT STITCH
Pantalla "Documentos" del área de soporte back-office de la plataforma SENA — Gestión de Horarios,
en español, dentro del app shell (barra superior con marca y usuario; nav lateral con ítem activo
"Soporte > Documentos"). Área de contenido con: fila de filtros (select "Dominio" con opciones
Horario/Ficha/Constancia/Actor/Reporte, select "Estado", campo de texto "Servicio propietario",
campo de texto "Entidad propietaria (UUID)") y un botón primario "Generar documento" a la derecha.
Debajo, una tabla densa con columnas Título, Dominio, Servicio propietario, Estado (con badges de
color + icono + texto: verde "Disponible", gris "Generando" con spinner, gris "Archivado", ámbar
"Expirado", rojo "Error de generación") y Actualizado, con acciones por fila (ver, descargar,
archivar) y al pie una **barra de paginación real y visible** (‹ anterior · 1 2 3 … › siguiente),
un **selector de tamaño de página** (10/20/50) y el texto **"Mostrando X–Y de N"**. Un panel
lateral derecho de detalle muestra metadatos del documento
seleccionado y una lista de versiones con fecha y autor, y un botón "Descargar versión vigente".
Incluir un modal de "Generar documento" con select de plantilla, select de dominio, campos de
texto y un textarea de datos JSON opcional. Mostrar también el estado vacío ("No hay documentos
que coincidan con los filtros") y el estado de carga (skeleton de filas). Estilo institucional
sobrio, verde SENA (placeholder), alto contraste WCAG AA, navegable por teclado, responsive.

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Pantalla 2 — Plantillas de documento

- **Ruta:** `/backoffice/documentos/plantillas` · **Rol:** `ADMIN_STAFF`/`SYSTEM_ADMIN` ·
  **MFE:** `document-mfe` · **HU:** pendiente
- **Endpoints:**
  - `GET /api/v1/document-templates` (`DOC_VIEW`) — lista paginada (sin `template_body`).
    Filtros: `output_type`, `code`, `is_active`.
  - `POST /api/v1/document-templates` (`DOC_TEMPLATE_MANAGE`) — crea (`version = 1`, `is_active = true`).
  - `GET /api/v1/document-templates/{id}` (`DOC_VIEW`) — detalle, incluye `template_body`
    (acepta `id` o `code`).
  - `PUT /api/v1/document-templates/{id}` (`DOC_TEMPLATE_MANAGE`) — actualiza; incrementa `version`.
  - `DELETE /api/v1/document-templates/{id}` (`DOC_TEMPLATE_MANAGE`) — desactiva (`is_active = false`).
  - `POST /api/v1/document-templates/{id}/preview` (`DOC_TEMPLATE_MANAGE`) — renderiza
    `template_body` contra `sample_data` sin persistir nada.
- **Campos reales (lista, `DocumentTemplateListItem`):** `id`, `code`, `name`, `output_type`
  (`PDF`/`EXCEL`/`WORD`), `version`, `is_active`.
- **Campos reales (detalle, `DocumentTemplate`):** los anteriores + `template_body` (HTML/Handlebars).
  `code` es **inmutable** tras la creación (no viaja en `DocumentTemplateUpdate`).

**Propósito:** mantener el catálogo de plantillas que el `pdf-renderer-worker` usa para generar
documentos, y validar su renderizado antes de publicarla.

**Layout:**
- **Filtros:** select **Tipo de salida**, campo **Código**, toggle **Activa**. Botón **Nueva
  plantilla**.
- **Tabla:** columnas Código, Nombre, Tipo de salida, Versión, Activa (badge sí/no). Acciones:
  **Editar**, **Desactivar**.
- **Paginación** (al pie de la tabla, REAL y visible): barra ‹ anterior · 1 2 3 … › siguiente,
  selector de tamaño de página (`page_size`: 10/20/50) y texto **"Mostrando X–Y de N"**, alineados
  a la paginación de `GET /document-templates`.
- **Editor de plantilla** (pantalla/panel completo): campo **Código** (bloqueado si ya existe),
  campo **Nombre**, select **Tipo de salida**, editor de texto/código **Cuerpo de la plantilla**
  (HTML/Handlebars), toggle **Activa**, botón **Guardar** y botón secundario **Previsualizar**.
- **Modal de previsualización:** editor JSON **Datos de muestra** (`sample_data`) + botón
  **Renderizar** → muestra `rendered_html` en un iframe/preview y, si aplica,
  **Placeholders sin valor** (`missing_placeholders`) como aviso no bloqueante.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Nueva plantilla | `POST /document-templates` | `201` → plantilla `version = 1` |
| Guardar | `PUT /document-templates/{id}` | `200` → `version` se incrementa; documentos ya generados no se ven afectados |
| Previsualizar | `POST /document-templates/{id}/preview` | `200` → `rendered_html` + `missing_placeholders[]`; no persiste nada |
| Desactivar | `DELETE /document-templates/{id}` | `204` → `is_active = false` (soft delete) |

**Estados:** *loading* (skeleton de tabla/editor) · *empty* ("No hay plantillas registradas") ·
*error* (`400`/`422` con detalle de campo) · *previsualización con placeholders faltantes*
(aviso ámbar, no bloquea guardar) · *success* (toast "Plantilla guardada — versión N").

```text
PROMPT STITCH
Pantalla "Plantillas de documento" del área de soporte back-office SENA — Gestión de Horarios, en
español, dentro del app shell (nav lateral con ítem activo "Soporte > Plantillas"). Vista de lista:
filtros (select "Tipo de salida" con PDF/Excel/Word, campo "Código", interruptor "Activa") y botón
primario "Nueva plantilla". Tabla con columnas Código, Nombre, Tipo de salida, Versión, Activa
(badge), con al pie una **barra de paginación real y visible** (‹ anterior · 1 2 3 … › siguiente),
un **selector de tamaño de página** (10/20/50) y el texto **"Mostrando X–Y de N"**. Vista de editor
(pantalla completa o panel ancho): campo "Código" bloqueado en modo
edición, campo "Nombre", select "Tipo de salida", un editor de código grande para el cuerpo
HTML/Handlebars de la plantilla, interruptor "Activa", botón primario "Guardar" y botón secundario
"Previsualizar". Modal de previsualización con un editor JSON de datos de muestra a la izquierda y
el HTML renderizado a la derecha, con una lista de "placeholders sin valor" en un aviso ámbar con
icono de advertencia. Estilo institucional sobrio, alto contraste WCAG AA, tipografía monoespaciada
para el código, responsive.

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Pantalla 3 — Auditoría

- **Ruta:** `/backoffice/auditoria` · **Rol:** `ADMIN_STAFF`/`SYSTEM_ADMIN` · **MFE:** `audit-mfe`
  · **HU:** pendiente
- **Endpoint:** [`GET /api/v1/audit-records`](https://github.com/code-sena/design-software-audit-service/blob/develop/api/openapi/audit.yaml)
  — consulta de **solo lectura** sobre `audit_record`, protegida por
  `AUDIT_LOG_VIEW` (ver) y `AUDIT_EXPORT` (exportar). Los filtros definidos por el contrato son
  consistentes con los índices reales de `audit_record`: `actor_id`,
  `entity_type` + `entity_id`, `event_type`, `source_service`, rango de fechas sobre `received_at`
  (clave de partición) con `event_occurred_at` visible por registro.
- **Campos reales (`audit_record`, data-model de audit-service):** `id`, `event_id`, `event_type`
  (ej. `scheduling.class_session.created`), `source_service`, `actor_id` (nullable — null =
  acción del sistema), `entity_type` (nullable), `entity_id` (nullable), `payload` (JSONB,
  completo), `event_occurred_at` (nullable, timestamp en el servicio origen), `received_at`
  (timestamp de recepción en el audit-worker; **no nullable**).

**Propósito:** dar trazabilidad de solo lectura de toda acción de negocio del sistema (quién,
qué, cuándo, en qué servicio), consumida vía el envelope estándar de eventos y persistida
append-only por `audit-worker`.

**Layout:**
- **Filtros:** campo **Actor** (`actor_id`, UUID), campo **Tipo de entidad** (`entity_type`),
  campo **ID de entidad** (`entity_id`, UUID), campo **Tipo de evento** (`event_type`, ej.
  `scheduling.class_session.created`), select **Servicio origen** (`source_service`), rango de
  fechas **Desde/Hasta** (sobre `received_at`). Sin botón de creación/edición: pantalla 100 %
  solo-lectura. Botón **Exportar** (`AUDIT_EXPORT`).
- **Tabla** (paginada por **cursor**, orden descendente por `received_at`): columnas Recibido
  (`received_at`), Ocurrido en origen (`event_occurred_at`), Evento (`event_type`), Servicio origen
  (`source_service`), Actor (`actor_id`; "Sistema" si null), Entidad (`entity_type` + `entity_id`).
  Acción por fila: **Ver payload**.
- **Paginación por CURSOR** (al pie de la tabla — `audit_record` es una colección append-only
  grande, no usa `page`/`page_size`): barra **"Cargar más / Siguiente"** que avanza con
  `cursor`/`limit` (sin números de página absolutos) y texto **"Mostrando X de N aprox."**.
- **Panel/modal "Ver payload":** JSON completo de `payload` en visor de solo lectura (JSON
  formateado/colapsable), más `event_id` para soporte de trazabilidad cruzada.
- **Nota de retención/partición** (visible como texto de ayuda al pie de la tabla): "Registro
  append-only; retención mínima 7 años; particionado mensual por fecha de recepción; datos con
  más de 2 años se archivan a almacenamiento frío y pueden tardar en consultarse."

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Aplicar filtros | `GET /audit-records?…` | refresca la tabla paginada |
| Ver payload | — (dato ya cargado en la fila) | abre panel/modal con el JSON completo |
| Exportar | `GET /audit-records?…&format=export` *(supuesto)* | descarga CSV/JSON de la selección filtrada |

**Estados:** *loading* (skeleton de tabla) · *empty* ("No hay eventos que coincidan con los
filtros") · *error* (`401`/`403`; o error de servicio dado que no hay contrato aún) · *rango de
fechas inválido* (validación en línea: "Desde" no puede ser posterior a "Hasta").

```text
PROMPT STITCH
Pantalla "Auditoría" del área de soporte back-office SENA — Gestión de Horarios, en español,
dentro del app shell (nav lateral con ítem activo "Soporte > Auditoría"), de solo lectura. Fila de
filtros: campo "Actor (UUID)", campo "Tipo de entidad", campo "ID de entidad", campo "Tipo de
evento" (ej. scheduling.class_session.created), select "Servicio origen", dos selectores de fecha
"Desde" / "Hasta", y un botón secundario "Exportar" a la derecha. Tabla densa de solo lectura con
columnas Recibido, Ocurrido en origen, Evento, Servicio origen, Actor (o "Sistema" si no aplica),
Entidad, y una acción "Ver payload" por fila que abre un panel con JSON formateado y colapsable.
Al pie de la tabla, una **barra de paginación por cursor** con un botón "Cargar más / Siguiente"
(sin números de página absolutos, avanza con `cursor`/`limit`) y el texto **"Mostrando X de N
aprox."**, seguida de una nota de ayuda en texto pequeño: "Registro append-only · retención mínima
7 años · particionado mensual · datos de más de 2 años se archivan en frío". Mostrar el estado
vacío ("No hay eventos que coincidan con los filtros") y el estado de carga (skeleton de filas).
Estilo institucional sobrio, alto contraste WCAG AA, tabla con scroll horizontal en móvil,
responsive.

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Pantalla 4 — Parametrización / catálogos

- **Ruta:** `/backoffice/parametrizacion` · **Rol:** `ADMIN_STAFF`/`SYSTEM_ADMIN` (edición); resto
  de roles solo lectura (RN-REF-03) · **MFE:** `reference-mfe` · **HU:** HU-19 — *Administrar la
  jerarquía institucional y catálogos* (RF-REF-01, RF-REF-02)
- **Endpoints — Catálogos (`catalog`):**
  - `GET /api/v1/catalogs` (`REF_CATALOG_VIEW`) — lista paginada. Filtros: `code`, `is_active`.
  - `POST /api/v1/catalogs` (`REF_CATALOG_MANAGE`) — crea.
  - `GET /api/v1/catalogs/{id}` (`REF_CATALOG_VIEW`) — detalle.
  - `PUT /api/v1/catalogs/{id}` (`REF_CATALOG_MANAGE`) — actualiza.
  - `DELETE /api/v1/catalogs/{id}` (`REF_CATALOG_MANAGE`) — desactiva (soft delete, `is_active = false`).
- **Endpoints — Valores de catálogo (`catalog_detail`, anidado a su `catalog` padre):**
  - `GET /api/v1/catalogs/{catalog_id}/details` (`REF_CATALOG_VIEW`) — filtros `code`, `is_active`.
  - `POST /api/v1/catalogs/{catalog_id}/details` (`REF_CATALOG_MANAGE`) — agrega valor.
  - `PUT /api/v1/catalogs/{catalog_id}/details/{id}` (`REF_CATALOG_MANAGE`) — actualiza valor.
  - `DELETE /api/v1/catalogs/{catalog_id}/details/{id}` (`REF_CATALOG_MANAGE`) — desactiva valor.
- **Endpoints — Parámetros del sistema (`parameter`, EAV):**
  - `GET /api/v1/parameters` (`REF_PARAMETER_VIEW`) — filtros `key`, `value_type`.
  - `POST /api/v1/parameters` (`REF_PARAMETER_MANAGE`) — crea.
  - `GET /api/v1/parameters/{id}` (`REF_PARAMETER_VIEW`) — detalle.
  - `PUT /api/v1/parameters/{id}` (`REF_PARAMETER_MANAGE`) — actualiza el valor. **Sin `DELETE`**:
    `parameter` no tiene `is_active`/`deleted_at`; los valores se superseden, no se eliminan.
- **Campos reales (`Catalog`):** `id`, `code` (único, ej. `MODALITY`, `SHIFT`), `name`,
  `description` (nullable), `is_active`, `created_at`.
- **Campos reales (`CatalogDetail`):** `id`, `catalog_id`, `code` (único dentro del catálogo, ej.
  `IN_PERSON`), `label`, `display_order` (nullable), `is_active`, `created_at`.
- **Campos reales (`Parameter`):** `id`, `key` (único, ej. `MAX_HOURS_PER_WEEK`), `value` (string,
  se valida según `value_type` en la capa de aplicación), `value_type`
  (`integer`/`string`/`boolean`/`json`), `description` (nullable), `created_at`.
- **Fuera de alcance de esta pantalla:** la jerarquía institucional
  (`macroregion`→`institutional_unit`, mismo servicio `reference-data-service`) no se incluye en
  este v0; queda como pantalla separada si se prioriza más adelante.

**Propósito:** dar a soporte/administración un panel único para mantener los catálogos
parametrizables que consume toda la plataforma (estados, modalidades, jornadas, etc.) y los
parámetros globales del sistema, sin hardcodear listas en el frontend.

**Layout:** dos pestañas.
- **Pestaña "Catálogos":** panel maestro-detalle. Izquierda: tabla de catálogos (Código, Nombre,
  Activo) con filtros `code`/`is_active` y botón **Nuevo catálogo**, con **paginación REAL visible**
  al pie (‹ anterior · 1 2 3 … › siguiente, selector `page_size`: 10/20/50, "Mostrando X–Y de N"),
  alineada a `GET /catalogs`. Al seleccionar un catálogo, a la derecha: cabecera con
  `name`/`description` editable + tabla de sus valores (`catalog_detail`: Código, Etiqueta, Orden,
  Activo) con filtros `code`/`is_active`, botón **Agregar valor**, acciones por fila
  **Editar**/**Desactivar**, y su propia **paginación REAL visible** al pie (misma barra
  ‹anterior·1 2 3…›siguiente + `page_size` + "Mostrando X–Y de N"), alineada a
  `GET /catalogs/{catalog_id}/details`.
- **Pestaña "Parámetros del sistema":** tabla (Clave, Valor, Tipo, Descripción) con filtros
  `key`/`value_type`, botón **Nuevo parámetro**, acción por fila **Editar** (abre modal con
  `value` tipado según `value_type`; sin acción de eliminar, solo "Actualizar valor"), y
  **paginación REAL visible** al pie (‹ anterior · 1 2 3 … › siguiente, selector `page_size`:
  10/20/50, "Mostrando X–Y de N"), alineada a `GET /parameters`.
- **Aviso de permisos:** si el usuario no tiene `REF_CATALOG_MANAGE`/`REF_PARAMETER_MANAGE`, la
  pantalla se muestra en modo solo-lectura (sin botones de creación/edición), conforme a RN-REF-03.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Nuevo catálogo | `POST /catalogs` | `201` → catálogo activo |
| Guardar catálogo | `PUT /catalogs/{id}` | `200` → actualizado |
| Desactivar catálogo | `DELETE /catalogs/{id}` | `204` → `is_active = false` |
| Agregar valor | `POST /catalogs/{catalog_id}/details` | `201` → nuevo `catalog_detail` |
| Editar valor | `PUT /catalogs/{catalog_id}/details/{id}` | `200` → actualizado |
| Desactivar valor | `DELETE /catalogs/{catalog_id}/details/{id}` | `204` → `is_active = false` |
| Nuevo parámetro | `POST /parameters` | `201` → parámetro creado |
| Actualizar valor | `PUT /parameters/{id}` | `200` → nuevo `value` (no hay historial expuesto por contrato) |

**Estados:** *loading* (skeleton en ambas columnas/tabla) · *empty* ("No hay catálogos" / "Este
catálogo aún no tiene valores" / "No hay parámetros registrados") · *error* (`400`/`404`/`409` —
p. ej. `code` duplicado) · *solo lectura* (banner informativo, sin controles de edición) ·
*success* (toast de guardado).

```text
PROMPT STITCH
Pantalla "Parametrización / catálogos" del área de soporte back-office SENA — Gestión de Horarios,
en español, dentro del app shell (nav lateral con ítem activo "Soporte > Parametrización"). Dos
pestañas superiores: "Catálogos" y "Parámetros del sistema". Pestaña Catálogos activa: layout
maestro-detalle de dos columnas; columna izquierda angosta con una lista de catálogos (código y
nombre) con un filtro, botón "Nuevo catálogo" y, al pie, una barra de paginación real y visible
(‹ anterior · 1 2 3 … › siguiente, selector de tamaño de página, "Mostrando X–Y de N"); columna
derecha ancha con el catálogo seleccionado mostrando nombre y descripción editables arriba, y
debajo una tabla de sus valores con columnas Código, Etiqueta, Orden, Activo, botón "Agregar
valor", acciones editar/desactivar por fila, y su propia barra de paginación real al pie.
Pestaña Parámetros del sistema (mostrar como vista secundaria): tabla con columnas Clave, Valor,
Tipo (integer/string/boolean/json), Descripción, botón "Nuevo parámetro", acción "Editar" por
fila, y al pie una barra de paginación real y visible (‹ anterior · 1 2 3 … › siguiente, selector
de tamaño de página, "Mostrando X–Y de N"). Incluir un banner superior opcional de "Modo solo
lectura" para el estado sin permisos de edición. Mostrar estado vacío ("Este catálogo aún no tiene
valores") y estado de carga (skeleton). Estilo institucional sobrio, verde SENA (placeholder),
alto contraste WCAG AA, objetivos táctiles ≥44px, responsive.

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Pantalla 5 — Detalle de documento + versiones

- **Ruta:** `/backoffice/documentos/:id` (deep link; el mismo contenido se monta también como panel
  lateral desde Pantalla 1 al seleccionar una fila — **una sola vista**, dos puntos de entrada, sin
  fragmentar estado) · **Rol:** `ADMIN_STAFF`/`SYSTEM_ADMIN` · **MFE:** `document-mfe` · **HU:** pendiente
- **Endpoints:**
  - `GET /api/v1/documents/{id}` (`DOC_DOCUMENT_VIEW`) — metadatos del documento.
  - `GET /api/v1/documents/{id}/versions` (`DOC_VERSION_VIEW`) — historial de `document_version`,
    orden descendente por `version_number`.
  - `GET /api/v1/documents/{id}/download-url` (`DOC_DOWNLOAD`) — URL firmada (TTL 300 s) de la
    **versión vigente**; requiere `status = AVAILABLE`.
- **Campos reales (`Document`):** `id`, `template_id` (nullable), `title`, `domain`, `owner_service`,
  `owner_entity_id`, `mime_type`, `size_bytes` (nullable), `status`, `row_version`, `created_by`,
  `created_at`, `updated_at`. **`storage_key` es `writeOnly` — nunca se retorna ni se muestra.**
- **Campos reales (`DocumentVersion`, por fila del historial):** `id`, `document_id`,
  `version_number`, `created_by`, `created_at`, `notes` (nullable). El contrato v1 no expone
  descarga por `version_id`; solo la versión vigente (resuelta vía `download-url`) es descargable.

**Propósito:** dar a soporte una vista de solo lectura completa de un documento — metadatos +
historial íntegro de versiones — sin exponer nunca la ruta interna de almacenamiento, y con la
única acción de descarga apuntando siempre a la versión vigente.

**Layout:**
- **Cabecera:** `title`, badge de `status` (icono + texto), `domain`, `owner_service` +
  `owner_entity_id` (UUID, con botón "Copiar"), `mime_type`, `size_bytes` (formateado, ej. "1.2 MB"),
  `created_by`/`created_at`, `updated_at`. Botón primario **Descargar versión vigente**
  (deshabilitado si `status ≠ AVAILABLE`, con tooltip explicando por qué).
- **Sección "Versiones":** tabla de solo lectura con columnas N.º versión (`version_number`,
  la más alta marcada "Vigente"), Autor (`created_by`), Fecha (`created_at`), Notas (`notes`,
  "—" si null). Sin paginación (el volumen de versiones por documento es acotado); si excede una
  altura razonable, scroll interno de la sección.
- **Nota de privacidad** (texto de ayuda, siempre visible): "La ruta de almacenamiento interno
  (`storage_key`) nunca se muestra; la descarga siempre usa una URL firmada temporal."

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Abrir detalle | `GET /documents/{id}` + `GET /documents/{id}/versions` | carga cabecera + tabla de versiones |
| Descargar versión vigente | `GET /documents/{id}/download-url` | abre la URL firmada en pestaña nueva; error si `status ≠ AVAILABLE` (`409`) |

**Estados:** *loading* (skeleton de cabecera + tabla) · *error* (`401`/`403`/`404`, banner con
acción "Volver a Documentos") · *sin versiones* ("Este documento aún no tiene versiones registradas"
— posible si `status = GENERATING`) · *descarga no disponible* (banner ámbar cuando `status ≠
AVAILABLE`, sin bloquear la vista) · *error de descarga* (toast si la URL firmada falla o expiró).

```text
PROMPT STITCH
Pantalla "Detalle de documento" del área de soporte back-office SENA — Gestión de Horarios, en
español, dentro del app shell (nav lateral con ítem activo "Soporte > Documentos"), de solo lectura.
Cabecera con el título del documento, un badge de estado (verde "Disponible", gris "Generando" con
spinner, gris "Archivado", ámbar "Expirado", rojo "Error de generación"), metadatos en dos columnas
(dominio, servicio propietario, entidad propietaria con botón copiar UUID, tipo MIME, tamaño en
MB/KB, autor y fecha de creación, última actualización) y un botón primario "Descargar versión
vigente" (mostrar también su estado deshabilitado con tooltip cuando el documento no está
disponible). Debajo, una sección "Versiones" con una tabla de solo lectura: columnas N.º de versión
(la más reciente con etiqueta "Vigente"), Autor, Fecha, Notas. Nota de ayuda en texto pequeño sobre
que la ruta de almacenamiento nunca se expone y la descarga usa siempre una URL firmada temporal.
Mostrar el estado vacío ("Este documento aún no tiene versiones registradas") y el estado de carga
(skeleton). Estilo institucional sobrio, alto contraste WCAG AA, responsive.

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Pantalla 6 — Modal: Generar documento

- **Ruta:** modal sobre `/backoffice/documentos` (no tiene URL propia) · **Rol:**
  `ADMIN_STAFF`/`SYSTEM_ADMIN` · **MFE:** `document-mfe` · **HU:** pendiente
  *(RF-DOC-01 en functional.md cubre generación de documentos)*
- **Endpoint:** `POST /api/v1/documents/generate` (`DOC_DOCUMENT_GENERATE`) — genera el documento
  de forma asíncrona a partir de una plantilla; encola en `document-generation-queue` para el
  pdf-renderer-worker. Alimenta el select de plantillas: `GET /api/v1/document-templates?is_active=true`
  (`DOC_VIEW`).
- **Campos reales (`GenerateDocumentRequest`):** `template_code` (referencia a
  `document_template.code`, ej. `SCHEDULE_CERTIFICATE`), `domain` (`SCHEDULE`/`FICHA`/
  `CERTIFICATE`/`ACTOR`/`REPORT`), `owner_service`, `owner_entity_id` (UUID), `title`, `data`
  (objeto JSON opcional, contexto para el renderizador). **Respuesta (`GenerateDocumentResponse`):**
  `document_id`, `status` (siempre `GENERATING`).

**Propósito:** permitir a soporte disparar la generación de un documento (constancia, reporte,
horario publicado) a partir de una plantilla activa, sin exponer detalles de renderizado.

**Layout:** modal de formulario con: select **Plantilla** (`template_code`, opciones etiquetadas
`code — name`, solo plantillas con `is_active = true`), select **Dominio**, campo de texto
**Servicio propietario**, campo de texto **Entidad propietaria** (UUID, con validación de formato),
campo de texto **Título**, editor JSON opcional **Datos** (`data`, colapsado por defecto, con
placeholder de ejemplo). Botones **Cancelar** / **Generar** (primario).

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Generar | `POST /documents/generate` | `202` → `document_id`, `status = GENERATING`; el modal se cierra, la tabla de Pantalla 1 muestra la nueva fila con badge "Generando…" y sondea `GET /documents/{id}` hasta `AVAILABLE`/`GENERATION_FAILED` |
| Cancelar | — | cierra el modal sin efecto |

**Estados:** *loading* (spinner en el select de plantillas mientras carga `document-templates`) ·
*validación en línea* (`entity_id` con formato UUID inválido, `título` vacío) · *error* (`400`/`422`
con detalle de campo, banner dentro del modal) · *enviando* (botón "Generar" en estado de carga,
deshabilitado para evitar doble envío) · *reapertura prellenada* (cuando se reabre desde la acción
"Reintentar" de un documento en `GENERATION_FAILED`, los campos vienen precargados con los valores
del intento anterior).

```text
PROMPT STITCH
Modal "Generar documento" del área de soporte back-office SENA — Gestión de Horarios, en español,
que se superpone sobre la pantalla "Documentos" (fondo atenuado). Formulario con: select "Plantilla"
(opciones con formato "código — nombre", ej. "SCHEDULE_CERTIFICATE — Constancia de horario"), select
"Dominio" (Horario/Ficha/Constancia/Actor/Reporte), campo de texto "Servicio propietario", campo de
texto "Entidad propietaria (UUID)" con validación en línea de formato, campo de texto "Título", y un
bloque colapsable "Datos (JSON opcional)" con un textarea de código y un placeholder de ejemplo.
Pie del modal con botón secundario "Cancelar" y botón primario "Generar" (mostrar también su variante
en estado de carga/deshabilitado). Mostrar un banner de error dentro del modal para validación
400/422. Estilo institucional sobrio, alto contraste WCAG AA, objetivos táctiles ≥44px, responsive.

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Pantalla 7 — Editor / Preview de plantilla de documento

- **Ruta:** `/backoffice/documentos/plantillas/:id/editar` (edición) ·
  `/backoffice/documentos/plantillas/nueva` (creación) · **Rol:** `ADMIN_STAFF`/`SYSTEM_ADMIN` ·
  **MFE:** `document-mfe` · **HU:** pendiente
- **Endpoints:**
  - `GET /api/v1/document-templates/{id}` (`DOC_VIEW`) — carga la plantilla a editar
    (acepta `id` o `code`); incluye `template_body`.
  - `POST /api/v1/document-templates` (`DOC_TEMPLATE_MANAGE`) — crea (`version = 1`,
    `is_active = true`).
  - `PUT /api/v1/document-templates/{id}` (`DOC_TEMPLATE_MANAGE`) — actualiza; incrementa `version`.
  - `POST /api/v1/document-templates/{id}/preview` (`DOC_TEMPLATE_MANAGE`) — renderiza
    `template_body` contra `sample_data` sin persistir nada.
- **Campos reales (`DocumentTemplate`):** `id`, `code` (único; **inmutable tras la creación**, no
  viaja en `DocumentTemplateUpdate`), `name`, `template_body` (HTML/Handlebars), `output_type`
  (`PDF`/`EXCEL`/`WORD`), `version` (se incrementa en cada `PUT`), `is_active`.
- **Campos reales (`DocumentTemplatePreviewRequest`/`Response`):** `sample_data` (objeto JSON de
  entrada) → `output_type`, `rendered_html`, `missing_placeholders` (array, placeholders sin valor).

**Propósito:** dar a soporte un editor dedicado de pantalla completa para escribir y versionar el
cuerpo HTML/Handlebars de una plantilla, con previsualización de renderizado antes de publicar.

**Layout:**
- **Cabecera del editor:** campo **Código** (editable solo en creación; bloqueado y con tooltip
  "El código no se puede modificar después de creado" en edición), campo **Nombre**, select
  **Tipo de salida**, toggle **Activa**, indicador de **Versión actual** (solo lectura, en edición).
- **Cuerpo:** editor de texto/código de ancho completo para **Cuerpo de la plantilla**
  (HTML/Handlebars, resaltado de sintaxis, tipografía monoespaciada, numeración de línea).
- **Pie fijo:** botón secundario **Previsualizar** y botón primario **Guardar**.
- **Modal de previsualización** (se abre desde "Previsualizar"): editor JSON **Datos de muestra**
  (`sample_data`) a la izquierda, botón **Renderizar**, y a la derecha el `rendered_html` en un
  iframe/preview sandbox; debajo, si aplica, **Placeholders sin valor** (`missing_placeholders`)
  listados en un aviso ámbar no bloqueante.

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Guardar (creación) | `POST /document-templates` | `201` → plantilla `version = 1`; redirige al editor en modo edición |
| Guardar (edición) | `PUT /document-templates/{id}` | `200` → `version` se incrementa; documentos ya generados no se ven afectados (versionado independiente del historial de `document_version`) |
| Previsualizar | `POST /document-templates/{id}/preview` | `200` → `rendered_html` + `missing_placeholders[]` en el modal; no persiste nada |
| Renderizar (dentro del modal) | `POST /document-templates/{id}/preview` | vuelve a renderizar con el `sample_data` editado |

**Estados:** *loading* (skeleton del editor al cargar una plantilla existente) · *guardando*
(botón "Guardar" en estado de carga) · *error* (`400`/`422` con detalle de campo, ej. `code`
duplicado en creación) · *previsualización con placeholders faltantes* (aviso ámbar dentro del
modal, no bloquea el guardado) · *error de previsualización* (`400`/`422` sobre `sample_data`
inválido) · *success* (toast "Plantilla guardada — versión N") · *salir sin guardar* (confirmación
si hay cambios sin persistir).

```text
PROMPT STITCH
Pantalla "Editor de plantilla de documento" del área de soporte back-office SENA — Gestión de
Horarios, en español, dentro del app shell (nav lateral con ítem activo "Soporte > Plantillas"),
de pantalla completa. Cabecera del editor con campo "Código" (mostrar la variante bloqueada con
tooltip para modo edición), campo "Nombre", select "Tipo de salida" (PDF/Excel/Word), interruptor
"Activa" y una etiqueta de solo lectura "Versión actual: N". Debajo, un editor de código grande de
ancho completo con resaltado de sintaxis y numeración de línea para el cuerpo HTML/Handlebars de la
plantilla. Pie fijo con botón secundario "Previsualizar" y botón primario "Guardar" (mostrar también
su variante en estado de carga). Incluir el modal de previsualización: panel izquierdo con un editor
JSON de "Datos de muestra" y un botón "Renderizar"; panel derecho con el HTML renderizado dentro de
un iframe de vista previa; debajo, una lista de "placeholders sin valor" en un aviso ámbar con icono
de advertencia. Mostrar el estado de carga (skeleton) y un banner de error de validación (código
duplicado). Estilo institucional sobrio, alto contraste WCAG AA, tipografía monoespaciada para el
código, responsive.

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Pantalla 8 — Modal: Detalle de registro de auditoría

- **Ruta:** modal sobre `/backoffice/auditoria` (no tiene URL propia) · **Rol:**
  `ADMIN_STAFF`/`SYSTEM_ADMIN` · **MFE:** `audit-mfe` · **HU:** pendiente
- **Endpoint:** `GET /api/v1/audit-records/{id}` (`AUDIT_LOG_VIEW`), definido en el
  [contrato canónico de audit-service](https://github.com/code-sena/design-software-audit-service/blob/develop/api/openapi/audit.yaml).
  El detalle se abre con el registro **ya cargado en la fila** de la tabla de Pantalla 3 (sin
  round-trip adicional); un deep link directo consulta el endpoint de solo lectura con la misma
  protección RBAC.
- **Campos reales (`audit_record`, data-model de audit-service):** `id`, `event_id`, `event_type`,
  `source_service`, `actor_id` (nullable — null = acción del sistema), `entity_type` (nullable),
  `entity_id` (nullable), `payload` (JSONB completo), `event_occurred_at` (nullable),
  `received_at` (no nullable). **Solo lectura — `audit_record` es append-only; este modal nunca
  edita ni elimina.**

**Propósito:** dar a soporte el detalle completo de un evento auditado — incluido el `payload`
íntegro — para trazabilidad cruzada con el servicio origen, sin salir de la tabla de auditoría.

**Layout:** modal/panel de solo lectura con: cabecera (`event_type`, badge de `source_service`,
`received_at` y `event_occurred_at` lado a lado), fila de identificación (`event_id` con botón
"Copiar", `actor_id` o "Sistema" si null, `entity_type` + `entity_id` o "—" si null), y el cuerpo
principal: visor JSON de solo lectura del `payload` completo (formateado, colapsable por nivel,
con botón "Copiar JSON"). Sin ningún control de edición/eliminación (append-only).

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Ver detalle (desde la tabla) | — (dato ya cargado en la fila de Pantalla 3) | abre el modal instantáneamente |
| Abrir por deep link | `GET /audit-records/{id}` | carga el registro y abre el modal |
| Copiar `event_id` / copiar JSON | — | copia al portapapeles, toast de confirmación |
| Cerrar | — | vuelve a la tabla de Pantalla 3 sin mutar nada |

**Estados:** *loading* (solo si se abre por deep link: skeleton del modal) · *error* (`401`/`403`/
`404` si el `id` no existe, o error de servicio dado que no hay contrato aún) · *payload vacío*
(caso límite — visor muestra `{}` explícito, no un vacío ambiguo) · *success* (render inmediato
cuando el dato ya viene de la fila, sin loading perceptible).

```text
PROMPT STITCH
Modal "Detalle de registro de auditoría" del área de soporte back-office SENA — Gestión de
Horarios, en español, que se superpone sobre la pantalla "Auditoría" (fondo atenuado), de solo
lectura. Cabecera con el tipo de evento (ej. scheduling.class_session.created), un badge del
servicio origen, y dos marcas de tiempo lado a lado ("Recibido" y "Ocurrido en origen"). Debajo,
una fila de identificación con el ID de evento (con botón "Copiar"), el actor (o "Sistema" si no
aplica), y la entidad afectada (tipo + ID). Cuerpo principal: un visor de JSON de solo lectura,
formateado y colapsable por nivel, con el payload completo del evento, y un botón "Copiar JSON".
Pie del modal con un único botón "Cerrar" (sin acciones de edición ni eliminación, es un registro
append-only). Estilo institucional sobrio, alto contraste WCAG AA, tipografía monoespaciada para el
JSON, responsive.

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Pantalla 9 — Formularios CRUD: catálogo, valor de catálogo y parámetro

- **Ruta:** modales sobre `/backoffice/parametrizacion` (no tienen URL propia) · **Rol:**
  `ADMIN_STAFF`/`SYSTEM_ADMIN` (RN-REF-03) · **MFE:** `reference-mfe` · **HU:** HU-19 —
  *Administrar la jerarquía institucional y catálogos*
- **Endpoints:**
  - Catálogo: `POST /api/v1/catalogs` · `PUT /api/v1/catalogs/{id}` (`REF_CATALOG_MANAGE`).
  - Valor de catálogo: `POST /api/v1/catalogs/{catalog_id}/details` ·
    `PUT /api/v1/catalogs/{catalog_id}/details/{id}` (`REF_CATALOG_MANAGE`).
  - Parámetro: `POST /api/v1/parameters` · `PUT /api/v1/parameters/{id}` (`REF_PARAMETER_MANAGE`).
    **Sin `DELETE`**: `parameter` no tiene `is_active`/`deleted_at`; los valores se superseden.
- **Campos reales (`Catalog`/`CatalogCreate`/`CatalogUpdate`):** `code` (único; **inmutable en
  edición**), `name`, `description` (nullable), `is_active`.
- **Campos reales (`CatalogDetail`/`CatalogDetailCreate`/`CatalogDetailUpdate`):** `code` (único
  dentro del catálogo padre; **inmutable en edición**), `label`, `display_order` (nullable),
  `is_active`.
- **Campos reales (`Parameter`/`ParameterCreate`/`ParameterUpdate`):** `key` (único; **inmutable en
  edición** — no viaja en `ParameterUpdate`), `value` (string, validado según `value_type` en la
  capa de aplicación), `value_type` (`integer`/`string`/`boolean`/`json`), `description` (nullable).

**Propósito:** dar a soporte/administración los formularios de alta y edición de los tres
sub-recursos parametrizables de la pantalla "Parametrización" (Pantalla 4), sin exponer ningún
control a roles sin `REF_CATALOG_MANAGE`/`REF_PARAMETER_MANAGE` (RN-REF-03).

**Layout:** tres modales de formulario, cada uno lanzado desde su tabla correspondiente en
Pantalla 4:
1. **Modal "Nuevo/editar catálogo":** campo **Código** (editable solo en creación; bloqueado en
   edición con tooltip), campo **Nombre**, campo de texto largo **Descripción** (opcional), toggle
   **Activo**. Botones **Cancelar** / **Guardar**.
2. **Modal "Nuevo/editar valor de catálogo":** cabecera con el catálogo padre (`code — name`, solo
   lectura), campo **Código** (editable solo en creación; bloqueado en edición), campo **Etiqueta**
   (`label`), campo numérico opcional **Orden** (`display_order`), toggle **Activo**. Botones
   **Cancelar** / **Guardar**.
3. **Modal "Nuevo/editar parámetro":** campo **Clave** (`key`, editable solo en creación; bloqueado
   en edición con tooltip "La clave no se puede modificar después de creada"), select **Tipo de
   valor** (`value_type`), campo **Valor** (`value`, el control cambia según `value_type`: numérico
   para `integer`, texto para `string`, interruptor para `boolean`, editor JSON para `json`), campo
   de texto **Descripción** (opcional). Botones **Cancelar** / **Actualizar valor** (sin acción de
   eliminar — `parameter` no soporta `DELETE`).

**Acciones:**
| Control | Endpoint | Resultado |
|---|---|---|
| Guardar (nuevo catálogo) | `POST /catalogs` | `201` → catálogo activo; cierra el modal, refresca la lista de Pantalla 4 |
| Guardar (editar catálogo) | `PUT /catalogs/{id}` | `200` → actualizado |
| Guardar (nuevo valor) | `POST /catalogs/{catalog_id}/details` | `201` → nuevo `catalog_detail` |
| Guardar (editar valor) | `PUT /catalogs/{catalog_id}/details/{id}` | `200` → actualizado |
| Guardar (nuevo parámetro) | `POST /parameters` | `201` → parámetro creado |
| Actualizar valor (parámetro) | `PUT /parameters/{id}` | `200` → nuevo `value` (no hay historial expuesto por contrato) |
| Cancelar (cualquier modal) | — | cierra sin efecto |

**Estados:** *validación en línea* (`código`/`clave` requeridos y con formato válido; `valor`
validado contra `value_type` seleccionado, ej. rechaza texto no numérico si `value_type = integer`)
· *error* (`400`/`422` con detalle de campo; `409` por `code`/`key` duplicado) · *guardando* (botón
"Guardar"/"Actualizar valor" en estado de carga) · *success* (toast "Catálogo guardado" /
"Valor guardado" / "Parámetro actualizado", cierra el modal y refresca la tabla afectada) ·
*sin permiso* (los botones que abren estos modales no se renderizan si el usuario no tiene
`REF_CATALOG_MANAGE`/`REF_PARAMETER_MANAGE`, conforme al modo solo-lectura de Pantalla 4).

```text
PROMPT STITCH
Tres modales de formulario del área de soporte back-office SENA — Gestión de Horarios, en español,
que se superponen sobre la pantalla "Parametrización / catálogos" (fondo atenuado). (1) Modal "Nuevo
catálogo": campo "Código" (mostrar también la variante bloqueada con tooltip para modo edición),
campo "Nombre", textarea "Descripción", interruptor "Activo", botones "Cancelar"/"Guardar". (2) Modal
"Nuevo valor de catálogo": cabecera de solo lectura con el catálogo padre (ej. "MODALITY —
Modalidad"), campo "Código" (con variante bloqueada en edición), campo "Etiqueta", campo numérico
"Orden", interruptor "Activo", botones "Cancelar"/"Guardar". (3) Modal "Nuevo parámetro": campo
"Clave" (con variante bloqueada en edición y tooltip), select "Tipo de valor"
(integer/string/boolean/json), campo "Valor" cuyo control cambia según el tipo (numérico, texto,
interruptor o editor JSON — mostrar la variante JSON), campo "Descripción", botones
"Cancelar"/"Actualizar valor" (sin botón de eliminar). Mostrar validación en línea (campo obligatorio
vacío) y un banner de error dentro del modal para conflicto de código/clave duplicado (409). Estilo
institucional sobrio, alto contraste WCAG AA, objetivos táctiles ≥44px, responsive.

Reglas de calidad: no dupliques ningún dato ni acción (cada CTA una sola vez; no repitas botones que
ya están en la nav lateral o en las tarjetas; no agregues fila extra de accesos directos). Nombre y
rol del usuario solo en el menú superior. Máximo 3–4 tarjetas KPI y una sección principal; densidad
moderada, sin sobrecargar. Si es una PANTALLA DE LISTA, incluye paginación REAL visible (barra ‹
anterior · 1 2 3 · siguiente ›, selector de tamaño de página, y "Mostrando X–Y de N"); si es un WIDGET
de dashboard, usa "top N · Ver todos" sin paginador. Los números deben calzar con lo listado. Datos
de ejemplo realistas y proporcionados (muy cercano a la realidad, sin lorem ipsum).
ENTREGA SIEMPRE: un ZIP con las imágenes PNG (una desktop ~1440px y una móvil ~390px por pantalla) +
el HTML/CSS/JS iterativo y funcional (autocontenido o con assets locales) que abra en el navegador.
```

---

## Mockups generados
_(pendiente — guardar en `../mockups/06-backoffice/` y enlazar aquí: documentos.png,
documento-detalle.png, generar-documento.png, plantillas.png, editor-plantilla.png, auditoria.png,
auditoria-detalle.png, parametrizacion.png, parametrizacion-formularios.png)_
