<!-- RESUMEN-EJECUTIVO
agente: Jesús Ariel González Bonilla (PM + Arquitecto)
capacidad: design tokens ratificados (placeholder locked) para el mockup
fase: diseño (UX/UI)
estado: accepted (placeholder locked; ampliado 2026-11-02 con la spec visual unificada)
dependencias_entrada: 12-ux-ui/design-system.md; mockups aceptados v1/v2 (valores WCAG verificados)
consumidores_siguientes: generación del mockup (consistencia visual), design-system del frontend real
tldr: Valores concretos de color/tipografía/espaciado FIJADOS para el mockup, tomados de los mockups ya aceptados y verificados WCAG AA. Pendientes de ratificación oficial de marca SENA, pero locked para consistencia.
decisiones_clave: verde #007832 como marca; estados con color+icono+texto; contrastes AA verificados; tokens compartidos por todos los MFE
halts_registrados: color/tipografía oficiales SENA pendientes de lineamiento
-->

# Design tokens (ratificados — placeholder locked)

> **ESTADO: locked para el mockup.** Valores concretos tomados de los mockups **ya aceptados**
> (dashboard/horarios v2) y **verificados WCAG 2.1 AA**. Quedan **fijos** para que el mockup sea
> visualmente consistente. **Pendiente:** ratificación del lineamiento oficial de marca SENA
> (si cambia el verde/tipografía, se actualiza aquí y se regenera). Complementa
> [design-system.md](../design-system.md).

> **Implementación canónica:** `mockups/app/assets/tokens.css` es la fuente de los valores
> exactos. Además del subconjunto ratificado que lista este doc, `tokens.css` define
> `--color-brand-hover` / `--color-brand-soft`, la escala tipográfica completa
> (`--font-size-xs…3xl`, pesos, line-heights), la escala de espaciado (`--space-1…8`),
> sombras (`--shadow-sm/md`), z-index y dimensiones de layout
> (`--topbar-height`, `--sidebar-width`, `--sidebar-collapsed-width`; valores vigentes en la sección de densidad más abajo).
> Este documento lista el subconjunto ratificado; `tokens.css` manda para los valores exactos.

> **Actualización 2026-11-02 (spec visual unificada).** Este documento se alinea con la spec aprobada
> por el dueño: [../visual-spec.md](../visual-spec.md) (normativa). Cambios: **Inter** como fuente base
> con respaldo de sistema, escala de uso de **4 tamaños**, roles de color, reglas de densidad y los
> tokens nuevos de la sección [Tokens de densidad, foco y movimiento](#tokens-de-densidad-foco-y-movimiento).
> Las dimensiones de layout cambian a `--topbar-height: 56px`, `--sidebar-width: 224px` y
> `--sidebar-collapsed-width: 64px`. Orden docs-first: este archivo es la fuente canónica del generador
> de tokens de `design-software-design-system`; el código se alinea después.

## Color

| Token | Valor | Uso | Contraste (sobre blanco) |
|---|---|---|---|
| `color-brand` | `#007832` | Verde institucional (marca, acción primaria, éxito) | 5.63:1 ✅ |
| `color-background` | `#FFFFFF` | Lienzo del área de contenido (deja de ser gris) | — |
| `color-surface` | `#FFFFFF` | Topbar, sidebar, tabla, paneles, diálogos | — |
| `color-surface-subtle` | `#F9FAFB` | Encabezado de tabla y hover de fila (nuevo) | — |
| `color-surface-muted` | `#F2F4F7` | Hover de ítem de menú, página activa del paginador, badge neutro (antes: fondos sutiles / filas alternas) | — |
| `color-text` | `#101828` | Texto principal | 17.75:1 ✅ |
| `color-text-muted` | `#475467` | Texto secundario, encabezados de tabla, rótulos de sección | 7.69:1 ✅ |
| `color-text-subtle` | `#667085` | Placeholder, íconos inactivos, estado Archivado (nuevo) | 4.97:1 ✅ (4.76 sobre `surface-subtle`) |
| `color-control-border` | `#667085` | Borde de inputs, selects y checkboxes (WCAG 1.4.11, ≥ 3:1) | 4.97:1 ✅ |
| `color-brand-hover` / `color-brand-soft` | `#00652B` / `#ECF7F0` | Hover del primario / fondo del ítem activo y fila seleccionada | ✅ |
| `color-border` | `#EAECF0` | Líneas, divisores, marco de tabla, borde de botón secundario | decorativo |
| `color-danger` / `color-conflict` | `#B42318` | Crítico / **conflicto** | 6.57:1 ✅ |
| `color-danger-surface` | `#FEF3F2` | Fondo de banda/badge crítico | — |
| `color-warning` | `#93370D` | Advertencia / EN_REVISIÓN | 7.21:1 (sobre `#FFFAEB`) ✅ |
| `color-warning-surface` | `#FFFAEB` | Fondo de aviso | — |
| `color-success` | `#067647` | Éxito / PUBLICADO | ✅ |
| `color-success-surface` | `#ECFDF3` | Fondo de éxito | — |
| `color-info` | `#175CD3` | Informativo / enlaces | ✅ |
| `color-info-surface` | `#EFF8FF` | Fondo informativo | — |

### Estados de negocio (siempre color + icono + texto, nunca solo color)
| Estado | Color | Superficie | Icono sugerido |
|---|---|---|---|
| BORRADOR | `color-text-muted` | `color-surface-muted` | círculo/lápiz |
| ARCHIVADO | `color-text-muted` | `color-surface-subtle` (7.36:1) | punto hueco (`inset 0 0 0 1px currentColor`) para distinguirlo de Borrador |
| EN_REVISIÓN | `color-warning` | `color-warning-surface` | reloj/alerta |
| PUBLICADO | `color-success` (**no** `color-brand`) | `color-success-surface` | check |
| **CONFLICTO** | `color-conflict` | `color-danger-surface` | triángulo de alerta |

> El verde de marca **no** representa "Publicado": se usa `color-success`. Los colores de estado son solo
> semántica (badges, alertas), nunca decoración.

> Los estados de negocio provienen del catálogo parametrizable `status`; la UI **no** hardcodea la
> lista (design-system §3 / modeling-conventions §1). Estos tokens son solo la representación visual.

## Tipografía

| Token | Valor |
|---|---|
| `font-family-base` | `Inter, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif` |
| `font-size-xs … 3xl` | `12 · 14 · 16 · 18 · 24 · 32 · 36 px` (`xs sm md lg xl 2xl 3xl`) |
| `font-size-body` | `14px` (alias de `font-size-sm`; tamaño base de la app, nuevo) |
| `font-weight` | `regular 400 · medium 500 · semibold 600 · bold 700` (en la app solo 400, 500 y 600) |
| `line-height` | `tight 1.25 · normal 1.5 · relaxed 1.7` |
| `letter-spacing-tight` | `-0.01em` (solo en h1; nuevo) |

> **Cambio de decisión (Inter).** Antes la base era solo `system-ui` por rendimiento en conectividad
> baja. Se adopta **Inter** servida por el design-system: archivo woff2 *latin* variable de ~48 KB,
> autoalojado (sin CDN), `font-display: swap`, y `system-ui` como respaldo, de modo que sin la fuente
> la UI se ve igual de legible y no bloquea el render. Ningún MFE carga fuentes ni declara
> `@font-face`. Ninguna regla de la spec depende de Inter: si no se ratifica, el valor vuelve a
> `system-ui` sin otro cambio.
>
> **Escala.** Antes: `12 · 14 · 16 · 18 · 20 · 24 · 30 px` (7 pasos). Ahora se registra la escala que
> genera el design-system, monótona: `lg = 18`, `xl = 24`, `2xl = 32`, `3xl = 36`. (La versión previa de
> `3xl` valía igual que `2xl`; se corrige a 36 px.) **Uso en la app: 4 tamaños** (`xs` 12, `sm` 14,
> `md` 16, `xl` 24); `lg`, `2xl` y `3xl` quedan fuera del uso en MFE y se reservan al login y a las
> pantallas de marca del shell. Roles, pesos y line-height por tamaño: [visual-spec.md](../visual-spec.md) §1.

## Espaciado, forma, elevación

| Grupo | Valores |
|---|---|
| `space-1…8` | escala base 4px: `4 · 8 · 12 · 16 · 24 · 32 · 40 · 48 px` |
| `radius` | `sm 6px · md 10px · lg 16px` |
| `shadow` | `sm 0 1px 2px rgba(16,24,40,.06)` · `md 0 4px 8px rgba(16,24,40,.08)` |
| `z-index` | `base 0 · dropdown 1000 · overlay 1010 · modal 1020 · toast 1030` |

## Tokens de densidad, foco y movimiento

Nuevos (aditivos; ningún MFE se rompe hasta adoptarlos). Reglas de uso: [visual-spec.md](../visual-spec.md) §3.

| Token | Valor | Uso |
|---|---|---|
| `--topbar-height` | `56px` (antes 72) | Topbar |
| `--sidebar-width` | `224px` (antes 264) | Menú lateral |
| `--sidebar-collapsed-width` | `64px` (antes 76) | Menú colapsado (solo íconos) |
| `--sidebar-drawer-width` | `280px` | Menú como panel superpuesto en ≤ 768 px: `min(280px, 85vw)` |
| `--control-height` | `36px` | Inputs, selects y botones por defecto |
| `--control-height-sm` | `28px` | Botón compacto en tabla, paginador y toolbar (en escritorio) |
| `--control-height-touch` | `44px` | Alto mínimo de todo objetivo táctil en ≤ 768 px (WCAG 2.5.5 / criterio de 44 px del proyecto) |
| `--nav-item-height` | `32px` | Ítem del menú lateral en escritorio (`--control-height-touch` en ≤ 768) |
| `--table-header-height` | `36px` | Fila de encabezado de tabla |
| `--table-row-height` | `40px` | Fila de datos (44 px en ≤ 768 px) |
| `--content-max-width` | `1440px` | Ancho máximo de páginas de datos, alineadas a la izquierda |
| `--content-max-width-form` | `720px` | Ancho máximo de formulario y detalle |
| `--focus-ring-width` | `2px` | `outline` de `:focus-visible` |
| `--duration-fast` | `120ms` | Hover y cambios de color |
| `--duration-base` | `200ms` | Drawer, menú, diálogo |
| `--ease-out` | `cubic-bezier(0.23, 1, 0.32, 1)` | Entradas de overlay; nunca `ease-in` |
| `--color-scrim` | `rgba(16, 24, 40, .32)` | Fondo detrás del menú móvil y los diálogos |

## Responsive (breakpoints)

| Nombre | Ancho | Uso |
|---|---|---|
| `mobile` | ≤ 768px | 1 columna, nav en drawer (hamburguesa), acción de fila fija a la derecha de la tabla; objetivos táctiles ≥ 44 px; PNG de referencia ~390px |
| `tablet` | 768–1024px | 2 columnas; menú como en escritorio; ≤ 1024: padding de contenido `--space-5` |
| `desktop` | > 1024px | layout completo; PNG de referencia ~1440px |

## Regla
Estos tokens son **compartidos** por todos los micro-frontends (un solo set). Ningún MFE los
redefine (ver [component-inventory.md](component-inventory.md) §C).
