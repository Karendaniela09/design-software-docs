<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: inventario de componentes UI (design-system compartido + patrones por MFE)
fase: diseño (UX/UI)
estado: draft
dependencias_entrada: 12-ux-ui/design-system.md; mockup-ddd/flows/*.md; screen-inventory.md; micro-frontends.md
consumidores_siguientes: generación consistente del mockup; librería de componentes del frontend real
tldr: Catálogo de los componentes compartidos (design-system, usados por todos los MFE) y los patrones específicos de cada micro-frontend, derivados de las 45 pantallas.
decisiones_clave: los tokens/componentes base son COMPARTIDOS (un solo design-system); cada MFE solo aporta sus patrones de dominio; ningún MFE redefine tokens
halts_registrados: ninguno
-->

# Inventario de componentes UI

> Deriva de las 45 pantallas ([screen-inventory.md](screen-inventory.md)) y de
> [design-system.md](../design-system.md). **Regla:** los componentes base y los tokens son
> **compartidos** (un solo design-system); cada MFE **no** redefine tokens, solo compone.

## A. Componentes COMPARTIDOS (design-system — usados por todos los MFE)

### Layout / shell (dueño: `shell-host`)
| Componente | Descripción | Estados |
|---|---|---|
| `AppShell` | top bar + nav lateral por rol + área de contenido | colapsado/expandido, móvil (drawer) |
| `TopBar` | marca · buscador (opc) · campana notificaciones (badge) · menú de usuario | — |
| `SideNav` | ítems por `features` + `actor_type` (visual-spec §4.2) | activo, colapsado, hamburguesa móvil |
| `UserMenu` | nombre + rol + cerrar sesión | abierto/cerrado |
| `NotificationsBell` + `NotificationsPanel` | badge + overlay top-N + "Ver todas" | vacío, con ítems |
| `OfflineBanner` | "Sin conexión — datos guardados" | **condicional** (solo offline) |
| `PageHeader` | título + acción primaria | — |

### Datos
| Componente | Descripción | Estados |
|---|---|---|
| `DataTable` | tabla densa con columnas | loading (skeleton), empty, error |
| `Pagination` | ‹ anterior · 1 2 3 · siguiente › + selector page_size + "Mostrando X–Y de N" | offset; variante **cursor** ("Cargar más") |
| `FiltersBar` | filtros tipados + "Limpiar filtros" | aplicado, limpio |
| `StatusBadge` | estado de negocio con **icono + texto + color** (nunca solo color) | BORRADOR / EN_REVISIÓN / PUBLICADO / **CONFLICTO** |
| `KpiCard` | conteo/métrica + enlace "Ver todos" | — |
| `DetailPanel` | panel lateral o página de detalle read-only | loading, error |
| `EmptyState` / `ErrorState` | mensaje + acción (reintentar) | — |
| `Card` (móvil) | fila-tarjeta (tabla→tarjetas en móvil) | — |

### Formularios
| Componente | Descripción |
|---|---|
| `TextInput`, `Select`, `Textarea` | con validación inline (mensaje asociado al campo) |
| `SearchSelect` | combo con búsqueda (p. ej. buscar ficha) |
| `DateRangePicker` | rango de fechas |
| `PasswordField` | mostrar/ocultar + medidor de fortaleza |
| `FormActions` | botón primario + secundario; deshabilitado si inválido |
| `Modal` / `Dialog` | contenedor de modal; foco atrapado, cierre con Esc |
| `ConfirmDialog` | confirmación de acción irreversible (publicar, eliminar) |

### Feedback / navegación
| Componente | Descripción |
|---|---|
| `Toast` | confirmación efímera |
| `Banner` | mensaje persistente (error/aviso) |
| `Spinner` / `Skeleton` | carga |
| `Tabs` | pestañas (p. ej. "Este horario" / "Todo el centro") |
| `Breadcrumb` | migas (opcional) |

> **Accesibilidad (todos):** contraste ≥4.5:1, navegable por teclado, foco visible, objetivos
> táctiles ≥44px, ARIA en formularios/tablas (ver design-system §2).

## B. Patrones específicos por micro-frontend

| MFE | Patrones/componentes de dominio |
|---|---|
| **scheduling-mfe** | `WeekCalendarGrid` (horario semanal), `ConflictCard` (crítico), `ScheduleEditor` (agregar/editar sesiones), `PublishFlow` (confirmar + avisar conflictos), `ConflictResolvePanel` |
| **monitoring-mfe** | `KpiCard` (extiende el compartido) + `KpiChart` (línea + **línea de umbral**), `TrackingSessionForm` |
| **document-mfe** | `DocumentList`, `VersionList`, `TemplateEditor` + `TemplatePreview`, `GenerateDocumentForm`, `SignedDownloadLink` (nunca muestra `storage_key`) |
| **audit-mfe** | `AuditTrail` (lista cursor, solo lectura), `AuditRecordDetail` (visor de `payload` JSON) |
| **iam-mfe** | `LoginCard`, `UserForm`, `RoleAssignmentModal`, `SessionsList` (revocar sesión) |
| **academic-mfe** | CRUD estándar de fichas/programas (usa `DataTable`/`DetailPanel`/`FormActions`) |
| **environment-mfe** | `AvailabilityView` (ocupación por franja), CRUD de ambientes |
| **actors-mfe** | `AvailabilityExceptionForm`, listados de instructores/aprendices |
| **reference-mfe** | CRUD de catálogos/valores/parámetros (respeta RBAC de solo-lectura por rol) |

## C. Regla de composición
- Los MFE **consumen** los componentes compartidos (A); **no** los redefinen.
- Los patrones de dominio (B) se construyen **sobre** los compartidos.
- El **shell-host** provee A-layout y compone widgets de varios MFE en pantallas cross-dominio
  (p. ej. Dashboard). Ver [micro-frontends.md](micro-frontends.md).
