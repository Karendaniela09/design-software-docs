# UI Spec — Academic Management: edición, cambio de estado y reportes de ficha

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto), a partir de la implementación de joseale879 y Nicolasruiz918 | Equipo: Academic Management

## Contexto

Especifica las tres pantallas que [HU-ACAD-020](https://github.com/code-sena/design-software-docs/issues/371) agrega al remote `academic-management-mfe`: editar los datos operativos de una ficha, cambiar su estado y consultar los reportes de capacidad y de avance temporal. Hoy el MFE solo lista fichas y muestra su detalle.

Las tres pantallas consumen endpoints que ya están en el [contrato OpenAPI](../07-api/contracts/openapi/academic-management.yaml): `PUT /fichas/{id}`, `PATCH /fichas/{id}/status`, `GET /reports/enrollment-by-ficha` y `GET /reports/ficha-progress`. No hay cliente HTTP propio: todas las llamadas pasan por el `httpClient` autenticado que inyecta el shell ([ADR-023](../05-architecture/decisions/records/ADR-023-web-shell-owns-login-and-session.md)) y usan rutas relativas al dominio `/academic-management/api/v1` ([ADR-022](../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md)).

**Fuera de esta especificación:** las precondiciones del ciclo de vida que dependen de otros servicios (horas ejecutadas en Scheduling, nota definitiva en Actors) y la justificación de cancelación. Siguen abiertas en [decisions.md](../09-microservices/services/03-academic-management-service/decisions.md) y las define el trabajo de R4.

## Navegación

El remote monta tres rutas bajo su prefijo `/academic-management/` y muestra una barra con «Fichas», «Capacidad y oferta» y «Avance temporal». La ruta raíz y cualquier ruta desconocida redirigen a `fichas`.

| Ruta (relativa al remote) | Pantalla |
|---------------------------|----------|
| `fichas` | Lista de fichas y panel de detalle (con edición y cambio de estado) |
| `reportes/capacidad` | Reporte «Capacidad y estado de oferta» |
| `reportes/avance` | Reporte «Avance temporal de fichas» |

## Pantalla: Editar datos operativos de una ficha

**HU relacionada:** HU-ACAD-020, escenario 1
**Ruta:** `fichas`, dentro del panel de detalle de la ficha (botón «Editar datos operativos»)
**Descripción:** el usuario corrige jornada, modalidad, fecha prevista de cierre o cupo de una ficha que no está en un estado terminal.

#### Componentes

| Componente | Tipo | Comportamiento | Estado vacío | Estado error |
|------------|------|----------------|--------------|--------------|
| Jornada | Select | Diurna, nocturna o mixta (`DAY`, `NIGHT`, `MIXED`) | Valor actual de la ficha | — |
| Modalidad | Select | Presencial, virtual o híbrida (`IN_PERSON`, `VIRTUAL`, `HYBRID`) | Valor actual de la ficha | — |
| Fecha prevista de cierre | Input date | Opcional; no puede ser anterior a la fecha de inicio. Vacío envía `null` | Vacío con la ayuda «Déjalo vacío si la ficha no tiene fecha prevista» | Mensaje «La fecha de cierre prevista no puede ser anterior al inicio.» |
| Cupo máximo | Input number | Entero mayor o igual a 1 que solo puede reducirse; la ayuda muestra el cupo actual | Cupo actual | Mensajes «El cupo debe ser un número entero positivo.» y «El cupo de una ficha solo se puede reducir.» |
| Cancelar | Button | Cierra el formulario sin enviar | — | — |
| Guardar cambios | Button | Envía `PUT /fichas/{id}` con `row_version` | — | Deshabilitado mientras guarda |

#### Estados de la pantalla

| Estado | Descripción | Componentes afectados |
|--------|-------------|----------------------|
| Guardando | «Guardando cambios de la ficha…» (región `status`); botones deshabilitados | Formulario |
| Éxito | El panel muestra la ficha actualizada y «Los datos operativos se guardaron correctamente.» | Panel de detalle y lista |
| Validación local | Mensaje bajo los campos (`role="alert"`) y no se envía nada | Campo afectado |
| Error del servicio | Mensaje con el código y el texto que devuelve la API. Un `409` indica que otra persona modificó la ficha (versión desactualizada): recargar el detalle y repetir | Banner del formulario |

#### Accesibilidad

- [x] Cada campo tiene `label` asociado y su ayuda se enlaza con `aria-describedby`.
- [x] Los errores se anuncian con `role="alert"`; el progreso, con una región `status`.
- [x] Navegable por teclado dentro del panel, que atrapa el foco y se cierra con Escape.
- [ ] Contraste AA verificado con los tokens del design system (pendiente de la revisión de UX).

## Pantalla: Cambiar el estado de una ficha

**HU relacionada:** HU-ACAD-020, escenario 2
**Ruta:** `fichas`, dentro del panel de detalle (botón «Cambiar estado»)
**Descripción:** el usuario mueve la ficha por su máquina de estados, con un paso de confirmación.

Transiciones que ofrece la pantalla (las mismas del contrato): Inducción → Ejecución o Cancelada; Ejecución → Etapa productiva o Cancelada; Etapa productiva → Finalizada o Cancelada. Finalizada y Cancelada son terminales: el panel no ofrece acciones y el gestor responde «La ficha está en un estado terminal y no admite cambios.»

#### Componentes

| Componente | Tipo | Comportamiento | Estado vacío | Estado error |
|------------|------|----------------|--------------|--------------|
| Estado actual | Texto | Muestra el estado vigente | — | — |
| Nuevo estado | Select | Solo lista las transiciones permitidas desde el estado actual | «Selecciona una transición permitida» | — |
| Fecha real de cierre | Input date | Aparece al elegir Finalizada o Cancelada y es obligatoria; para Finalizada no puede ser futura | Fecha de hoy | — |
| Revisar cambio | Button | Pasa al paso de confirmación | Deshabilitado sin estado destino | — |
| Confirmación | Bloque | Muestra «Estado actual → destino» con «Volver» y «Confirmar transición» | — | — |
| Confirmar transición | Button | Envía `PATCH /fichas/{id}/status` | — | Deshabilitado mientras guarda |

#### Estados de la pantalla

| Estado | Descripción | Componentes afectados |
|--------|-------------|----------------------|
| Guardando | «Actualizando estado…» (región `status`) | Confirmación |
| Éxito | El panel muestra el nuevo estado y «El estado de la ficha se actualizó correctamente.» | Panel de detalle y lista |
| Error del servicio | Mensaje con el código y el texto de la API: `409` transición inválida o estado terminal, `403` sin permiso (la cancelación está reservada a dirección de centro, RN-ACAD-05), `422` regla de negocio, `503` dependencia no disponible | Banner del gestor |

#### Accesibilidad

- [x] Selección y confirmación operables con teclado; el botón de cancelar usa el estilo de peligro.
- [x] Errores con `role="alert"` y progreso con región `status`.

## Pantalla: Reportes de capacidad y de avance temporal

**HU relacionada:** HU-ACAD-020, escenario 3
**Rutas:** `reportes/capacidad` y `reportes/avance`
**Descripción:** el usuario consulta los reportes propios del dominio, con los filtros del contrato.

#### Componentes

| Componente | Tipo | Comportamiento | Estado vacío | Estado error |
|------------|------|----------------|--------------|--------------|
| Centro de formación (ID) | Input text | Filtra por `training_center_id` (UUID) | Vacío = todos | — |
| Programa (ID) | Input text | Filtra por `program_id` (UUID) | Vacío = todos | — |
| Estado | Select | Filtra por estado de la ficha | «Todos» | — |
| Desde (incluido) / Hasta (exclusivo) | Input date | Rango sobre `start_date`; «Hasta» debe ser posterior a «Desde» | Vacío | «La fecha “Hasta” es exclusiva y debe ser posterior a “Desde”.» |
| Ordenar por | Select | Opciones propias de cada reporte (inicio, número de ficha, estado, cupo o cierre) | Inicio: recientes primero | — |
| Aplicar filtros / Limpiar | Buttons | Aplican o restablecen filtros y vuelven a la página 1 | — | — |
| Tabla de resultados | Table | Capacidad: ficha, programa, centro, estado, jornada, modalidad, capacidad e inicio. Avance: ficha, estado, inicio, cierre previsto, días transcurridos, días restantes y retraso | Ver estados | Ver estados |
| Paginación | Controles | Por página (10, 20 o 50), anterior y siguiente, con «Mostrando a–b de N» | Oculta sin resultados | — |

#### Estados de la pantalla

| Estado | Descripción | Componentes afectados |
|--------|-------------|----------------------|
| Cargando | «Cargando reporte…» la primera vez y «Actualizando…» en las siguientes | Tabla |
| Vacío | «No hay fichas para los filtros seleccionados» con el botón «Limpiar filtros» | Tabla |
| Error | «No pudimos cargar el reporte», el mensaje de la API y «Reintentar» | Tabla |
| Datos | Tabla con totales de la paginación; sin fecha prevista se muestra «Sin fecha prevista» y sin días restantes, «No disponible» | Tabla |

#### Accesibilidad

- [x] Cada tabla tiene `caption` accesible y encabezados con `scope="col"`.
- [x] Filtros dentro de un formulario con etiqueta `Filtros del reporte`; errores con `role="alert"`.
- [ ] Contraste AA verificado con los tokens del design system (pendiente de la revisión de UX).

## Permisos

Las operaciones exigen los features del contrato: `ACADEMIC_FICHA_MANAGE` (editar), `ACADEMIC_FICHA_STATUS` (cambiar estado) y `ACADEMIC_FICHA_VIEW` (reportes). Hoy el shell no inyecta los permisos al remote, así que la pantalla ofrece las acciones y el servicio responde `403` cuando no corresponden; el MFE muestra ese mensaje. Ocultar los controles según los permisos de la sesión queda para cuando el shell los entregue por el contrato `remote-props` (ADR-023).

## Referencias

- [Contrato OpenAPI de Academic Management](../07-api/contracts/openapi/academic-management.yaml)
- [ADR-022](../05-architecture/decisions/records/ADR-022-edge-routing-table-by-domain.md) · [ADR-023](../05-architecture/decisions/records/ADR-023-web-shell-owns-login-and-session.md)
- [Design System](./design-system.md) · [Mapa de navegación](./navigation-map.md)
