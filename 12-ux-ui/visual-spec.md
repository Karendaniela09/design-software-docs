# Visual spec — Web Shell and MFEs

> Estado: 🟢 Normativa (aprobada por el dueño el 2026-11-02) | Última actualización: 2026-11-02
> Autor: Jesús Ariel González Bonilla (PM + Arquitecto) | Equipo: UX-UI

This document is **normative** for how every screen of the Web Shell and the nine MFEs looks. It is written in English; labels shown to users stay in Spanish as in the product.

Scope: **appearance and tokens only**. It does not change flows, endpoints, permissions or functional components. The one non-visual change it carries (navigation derived from features) is tracked as HU-SHELL-019 ([docs#493](https://github.com/code-sena/design-software-docs/issues/493)).

Source of truth for values: [mockup-ddd/design-tokens.md](./mockup-ddd/design-tokens.md), which feeds the generated tokens of `design-software-design-system`. Every number below is an existing token or one defined there. **No MFE declares its own values.**

SENA identity is kept (green `--color-brand` and the logo). Nothing is copied from another product: only restraint is borrowed (fewer boxes, more useful space, hierarchy through typography).

---

## 1. Typography

- **Font: Inter**, served by the design-system (self-hosted woff2 latin variable, `font-display: swap`) with `system-ui` as fallback: `--font-family-base: Inter, system-ui, sans-serif`. No MFE loads fonts or declares `@font-face`. No rule in this spec depends on Inter; with the fallback the layout is unchanged.
- **Four sizes in the app**:

| Role | Token | Value | Weight | Line height | Use |
|---|---|---|---|---|---|
| Meta | `--font-size-xs` | 12 px | 400 / 500 | 16 px | Table headers, field labels, menu section labels, badges, help text, pagination |
| UI base | `--font-size-sm` (alias `--font-size-body`) | 14 px | 400 / 500 | 20 px | Default text: menu, cells, inputs, buttons, page description |
| Subtitle | `--font-size-md` | 16 px | 600 | 24 px | h2 of a section, title of a panel, dialog or drawer |
| Page title | `--font-size-xl` | 24 px | 600 | 32 px | One h1 per page, `letter-spacing: var(--letter-spacing-tight)` |

- The app body is 14 px (`ui.css` applies `--font-size-body` to `body`).
- Mobile exception (<= 768 px): inputs, selects and textareas use `--font-size-md` (16 px) to avoid iOS zoom.
- `--font-size-lg`, `--font-size-2xl` and `--font-size-3xl` are **not used in MFEs**; they stay for login and brand screens of the shell.
- **Allowed weights:** 400 regular, 500 medium (buttons, active item, labels), 600 semibold (h1/h2, section labels). **700 and 800 are not used** in the app.
- Numbers, dates, times and counters in tables use `font-variant-numeric: tabular-nums`, applied only to those columns (class `.num`), **not** to identifiers such as UUIDs or period codes (with Inter it would split "2026-1" visually).
- Sentence case everywhere ("Ficha", not "FICHA"). Sustained uppercase is forbidden in table headers and the menu.

---

## 2. Color roles

| Role | Token | Value | Use |
|---|---|---|---|
| Text | `--color-text` | #101828 | Titles, cells, menu items |
| Muted text | `--color-text-muted` | #475467 | Description, meta, table headers, section labels |
| Subtle text | `--color-text-subtle` | #667085 | Placeholder, inactive icons, text separators. 4.97:1 on white |
| Canvas | `--color-background` | #ffffff | Content area (**no longer grey**) |
| Surface | `--color-surface` | #ffffff | Topbar, sidebar, table, panels, dialogs |
| Soft surface | `--color-surface-subtle` | #f9fafb | Table header, row hover |
| Muted surface | `--color-surface-muted` | #f2f4f7 | Menu item hover, current page of the pager, neutral badge |
| Border | `--color-border` | #eaecf0 | Lines, dividers, table frame, secondary button border |
| Control border | `--color-control-border` | #667085 | Inputs, selects, checkboxes (3:1, WCAG 1.4.11) |
| Brand / accent | `--color-brand` | #007832 | Primary button, active item text, links, focus ring |
| Brand hover | `--color-brand-hover` | #00652b | Primary hover |
| Soft brand | `--color-brand-soft` | #ecf7f0 | Active item background, selected row, current page of the pager |
| Status | `--color-success` / `-warning` / `-danger` / `-info` / `-conflict` and their `*-surface` | | Semantics only (badges, alerts). Never decoration |

Business status badge = text + dot + soft background, no border:

| Status | Text | Background | Note |
|---|---|---|---|
| Borrador (`DRAFT`) | `--color-text-muted` | `--color-surface-muted` | |
| En revisión (`UNDER_REVIEW`) | `--color-warning` | `--color-warning-surface` | |
| Publicado (`PUBLISHED`) | `--color-success` | `--color-success-surface` | The brand green does **not** mean "Publicado" |
| Archivado (`ARCHIVED`) | `--color-text-muted` | `--color-surface-subtle` (7.36:1) | Hollow dot (`background: transparent; box-shadow: inset 0 0 0 1px currentColor`) so it differs from Borrador |
| Conflicto | `--color-conflict` | `--color-danger-surface` | |

Status is always colour **plus** text (plus dot or icon), never colour alone.

Pager: current page `background: var(--color-brand-soft); color: var(--color-brand)` (same as the menu); disabled `color: var(--color-text-subtle); opacity: .5`.

Contrast verified (WCAG 2.x): text 17.75:1, muted 7.69:1, subtle 4.97:1 on white and 4.76:1 on `surface-subtle`, brand 5.63:1 on white and 5.12:1 on `brand-soft`, white on brand 5.63:1, status badges 5.4 to 7.2:1.

---

## 3. Spacing and density

Scale `--space-1…8` = 4 · 8 · 12 · 16 · 24 · 32 · 40 · 48 px. No other values.

| Element | Rule |
|---|---|
| Topbar | `--topbar-height` = **56 px** |
| Sidebar | `--sidebar-width` = **224 px**; collapsed `--sidebar-collapsed-width` = **64 px** |
| Menu item | **32 px** high (`--nav-item-height`), padding `0 var(--space-2)`, 16 px icon, gap `--space-2`, no spacing between items |
| Content area padding | `var(--space-5) var(--space-6)` (24/32); <= 1024: `--space-5`; <= 768: `--space-4` |
| Page header | h1 (32 px line) + description (20 px); actions aligned top right; `margin-bottom: var(--space-4)`; about 72 px in total |
| Toolbar / filters | One row. 36 px controls, `gap: var(--space-2)`, `margin-bottom: var(--space-3)` |
| Table row | **40 px** (`--table-row-height`): padding `var(--space-2) var(--space-3)`, 1 px `--color-border` bottom line |
| Table header | 36 px, 12 px / 500 `--color-text-muted`, background `--color-surface-subtle` |
| Form field | **36 px** (`--control-height`); label 12 px / 500 above, gap `--space-1` |
| Button | 36 px default; **28 px** compact (`--control-height-sm`) in tables, pager and toolbars (desktop) |
| Radius | `--radius-sm` (6) for controls and block badges; `--radius-md` (10) for table frame, panels and dialogs; `--radius-lg` only login |
| Shadow | None on in-page surfaces. `--shadow-md` only on overlays (menu, drawer, dialog) |

### Touch targets at <= 768 px (44 px)

Every interactive target is **at least `--control-height-touch` = 44 px** high at <= 768 px: menu items, form controls, buttons, text buttons ("Ver"), icon buttons (hamburger, bell), pager buttons and the page-size select. The table row grows to 44 px.

- Apply `min-height: var(--control-height-touch)` to those elements inside the `@media (width <= 768px)` block. Beware of specificity: `.page-size .control` must be listed with its full selector or the 28 px desktop rule wins.
- To avoid inflating the look of icon buttons, pager buttons and text buttons, it is allowed to enlarge only the hit area with a pseudo-element: `position: relative` on the control and `::after { content: ''; position: absolute; inset: calc((var(--control-height-touch) - 100%) / -2) 0; }`.
- Form controls at <= 768 px use `--control-height-touch` instead of `--control-height`.

### Cards

- Cards are allowed only for: KPI or dashboard tiles, side panels or drawers, dialogs, and groups of a long form.
- **Never a card inside a card.** Never a card wrapping a whole page.
- The main table is **not** in a card. It only has its frame: 1 px `--color-border` with `--radius-md`.
- Title and count live in the page header or the toolbar, not in a "card header".

### Maximum width on wide screens

- Data pages (tables, grids, calendar): fluid up to `--content-max-width` = **1440 px**, **left-aligned** (not centered), so the h1 and the table stay next to the menu.
- Form or detail pages: `--content-max-width-form` = **720 px**, left-aligned.
- Running text (descriptions, help): `max-width: 72ch`.

---

## 4. Navigation

### 4.1 Shape

- **Compact sidebar:** 224 px, background `--color-surface`, 1 px `--color-border` on the right.
- **Flat links:** 14 px / 400 `--color-text` text with a 16 px icon in `--color-text-subtle`. **No border, no background and no shadow at rest.** Hover: background `--color-surface-muted`.
- **Active:** background `--color-brand-soft`, text and icon `--color-brand`, weight 500, and `aria-current="page"`. One indicator only (no side bar).
- **Sections:** 12 px / 600 `--color-text-muted` label in sentence case, `margin-top: var(--space-4)`, `padding-inline: var(--space-2)`. A section with no visible items shows no label. The first group (Inicio and personal items) has no label.
- The role label above the menu is removed (the role is under the name in the topbar).
- **Cerrar sesión:** a flat item at the foot of the sidebar in `--color-text-muted`, no border. Same action as before.
- **Collapsed (desktop):** 64 px, icons only with `title` and `aria-label`; section labels become a 1 px divider.
- **Skip link** "Saltar al contenido" is kept (it is functionality), visible on `:focus-visible`.
- **Topbar 56 px:** 28 px logo, "Gestión de Horarios" 14 / 600, 1 px divider and "Centro de Formación" 14 `--color-text-muted` (hidden <= 1024). On the right: bell (32 px icon button) and user (28 px avatar `--radius-sm` on `--color-brand-soft`, name 14 / 500, role 12 muted). At <= 768 name and role are hidden in the topbar, so the avatar carries `title` and `aria-label` with name and role **and** the drawer header shows name and role (12 px muted). The role is rendered as the raw enum until the backend provides a display name (visual debt).

### Mobile drawer (<= 768 px): accessibility contract

At <= 768 px the menu is closed by default and opens as an overlay panel (`min(var(--sidebar-drawer-width), 85vw)`, 280 px max, `--color-scrim` behind it) with the **same button** of the topbar. Content uses the full width. Destinations and actions do not change.

1. The button has `aria-controls` and **`aria-expanded`**, in sync with the drawer state.
2. When it opens, focus moves to the first menu item.
3. `Esc`, a click on the scrim or choosing an item closes the drawer, and **focus returns to the button**.
4. While open, the background content is `inert` and the body does not scroll.
5. The button's `aria-label` is "Abrir menú" / "Cerrar menú" according to state; on desktop the same button keeps "Colapsar menú" / "Expandir menú".
6. Open and close use `--duration-base` with `--ease-out`, and respect `prefers-reduced-motion`.

### 4.2 What each role sees: by feature, not by module

> **Supersedes the HU-001 E2 criterion** ("the menu is derived from `me.modules`"). Decision of 2026-11-02, tracked as HU-SHELL-019 ([docs#493](https://github.com/code-sena/design-software-docs/issues/493)). Docs first, then code.

**Rationale.** With the real RBAC grants, filtering by module showed a COORDINATOR the "Mi horario" items of an instructor and a learner (11 items), and showed a LEARNER "Horarios", "Parametrización" and "Datos de referencia". `MeResponse` already carries `features: string[]` and `actor_type: USER | INSTRUCTOR | LEARNER`, so the contract does not change. A feature alone is not enough: SYSTEM_ADMIN, CENTER_DIRECTOR and COORDINATOR also hold `SCH_VIEW_OWN` through GLOBAL or TRAINING_CENTER scope, so personal items also require `actor_type`.

Visibility rule: `visible = any(requires) && (actor? == me.actor_type)`. "Fichas" admits an alternative (`orOwn`).

| Section | Item (id) | Label | Requires (any of) | actor_type | Route (unchanged) |
|---|---|---|---|---|---|
| none | `home` | Inicio | *(always)*. No role holds `DASH_PERSONAL` or `DASH_CENTER_OVERVIEW`, so requiring them would hide Inicio for everyone | | `/` |
| none | `instructor-schedule` | Mi horario | `SCH_VIEW_OWN` | INSTRUCTOR | `/scheduling/mi-horario` |
| none | `my-schedule` | Mi horario | `SCH_VIEW_OWN` | LEARNER | `/scheduling/mi-horario-aprendiz` |
| none | `instructor-availability` | Mi disponibilidad | `ACT_INSTRUCTOR_VIEW` | INSTRUCTOR | `/actors/mi-disponibilidad` |
| none | `notifications` | Notificaciones | `MON_NOTIFICATION_VIEW` | | `/monitoring/notificaciones` |
| Planeación | `schedules` | Horarios | `SCH_VIEW_ALL` | | `/scheduling/horarios` |
| Planeación | `availability` | Disponibilidad | `ENV_VIEW`, `ENV_AVAILABILITY_QUERY` | | `/training-environment/disponibilidad` |
| Formación | `fichas` | Fichas | `ACADEMIC_FICHA_VIEW`; or `ACADEMIC_FICHA_VIEW_OWN` + INSTRUCTOR | | `/academic-management/fichas` |
| Formación | `tracking` | Seguimiento | `MON_TRACKING_SESSION_CREATE`, `MON_TRACKING_SESSION_VIEW` | | `/monitoring/seguimiento` |
| Formación | `indicators` | Indicadores | `MON_KPI_VIEW`, `MON_DASHBOARD_FULL`, `MON_DASHBOARD_OWN` | | `/monitoring/indicadores` |
| Documentos | `documents` | Documentos | `DOC_VIEW` | | `/document/documentos` |
| Documentos | `templates` | Plantillas | `DOC_TEMPLATE_VIEW`, `DOC_TEMPLATE_MANAGE` | | `/document/documentos/plantillas` |
| Administración | `users` | Usuarios | `IDENTITY_USER_VIEW`, `IDENTITY_USER_MANAGE` | | `/iam/usuarios` |
| Administración | `reference-data` | Datos de referencia | `REF_CATALOG_MANAGE`, `REF_HIERARCHY_MANAGE` (the `*_VIEW` features are for dropdown lookups and do not open the menu) | | `/reference-data/datos-referencia` |
| Administración | `parameters` | Parametrización | `REF_PARAMETER_VIEW`, `REF_PARAMETER_MANAGE` | | `/reference-data/parametrizacion` |
| Administración | `audit` | Auditoría | `AUDIT_LOG_VIEW` | | `/audit/auditoria` |

Result with the seeded grants of develop:

| Role | Today (by module) | Proposal (feature + actor_type) | Items |
|---|---|---|---|
| INSTRUCTOR | Horarios, Disponibilidad, Fichas, both "Mi horario", Mi disponibilidad, Seguimiento, Notificaciones, Indicadores, Datos de referencia, Parametrización | Inicio, Mi horario, Mi disponibilidad, Notificaciones; Planeación: Disponibilidad; Formación: Fichas, Seguimiento, Indicadores | 11 to 8 |
| COORDINATOR | The 11 of the instructor (including both foreign "Mi …") | Inicio, Notificaciones; Planeación: Horarios, Disponibilidad; Formación: Fichas, Seguimiento, Indicadores | 11 to 7 |
| SYSTEM_ADMIN | 15 | Inicio, Notificaciones; Planeación (2); Formación (3); Documentos (2); Administración (4) | 15 to 13 |
| LEARNER | Horarios, Fichas, Parametrización, Datos de referencia, Mi horario (instructor), … | Inicio, Mi horario, Notificaciones | 10 to 3 |

Notes:

- The menu filter is **presentation only**. The backend keeps authorizing every endpoint and each MFE keeps its internal guards (for example `SchedulesPage` shows "Sin acceso" when `SCH_VIEW_*` is missing).
- The table lives in `navigation-table.ts` (new fields `section`, `requires`, `actor`). The `module` field may stay as a fallback during the transition.
- "Mi horario" loses the "(instructor)" suffix: each user sees a single variant.
- "Inicio" always visible is the only item that *appears* for roles that had none today; the owner confirms it.
- Open owner decisions (not applied here): (a) COORDINATOR has no `DOC_VIEW`, so Documentos is not shown to it; (b) renaming "Disponibilidad" to "Ambientes" (today it is confused with "Mi disponibilidad"; labels stay "Disponibilidad" until decided); (c) `ScheduleConflictsPage` and `TimeSlotsPage` have no menu entry and this spec adds none.

---

## 5. Page anatomy (mandatory for every MFE)

```
<section data-mfe="<domain>" class="page">   no own background, no min-height:100vh, no own padding
  PageHeader   h1 (24/600) + optional description (14, muted, max 72ch, one sentence)
               actions on the right: at most 1 primary + secondary ones
  Toolbar      filters (search first) · "Limpiar" as a text button, visible only when filters are active
               right side: result count ("42 horarios") and view actions
  Content      table | grid | form | calendar
  Footer       pagination: "1–10 de 42" · page size · ‹ 1 2 3 ›
</section>
```

States, all inside the Content area (the header and toolbar never disappear):

| State | Shape |
|---|---|
| Loading | 5 skeleton rows of 40 px in the table, or a 16 px spinner + "Cargando horarios…" (14 px muted) on one line. Never a full-screen spinner once the shell has loaded |
| Empty | Left-aligned block with `--space-6` padding: 14 / 500 title ("Sin horarios") + 14 muted text + optional text button. Icon at most 20 px in `--color-text-subtle` |
| Error | Inline alert: `--color-danger-surface` background, `--color-danger` text, 14 px, `role="alert"`, "Reintentar" text button. No own coloured border |
| No access | Same as Empty with the permissions copy (current copy is kept) |
| Detail panel | Right drawer, 480 px (`--shadow-md`); full screen on mobile |

**Row actions.** A single **text button** ("Ver", 14 / 500 `--color-brand`, no border) in the last column. It stays a `<button>` with the same `aria-label`, `data-testid` and `onClick` as today; do not turn it into an `<a>`. With more than one action, group them in a "⋯" menu with a single 28 px icon button (44 px hit area on mobile). Never a row of bordered buttons.

**Row action on mobile (<= 768 px).** The action column must not scroll out of view. In the mobile block:

- `.col-action { position: sticky; inset-inline-end: 0; background: var(--color-surface); box-shadow: inset 1px 0 0 var(--color-border); }` (a divider, not an elevation, so the "no shadow on in-page surfaces" rule holds).
- Long identifiers are truncated: `.cell-id { max-width: 9ch; overflow: hidden; text-overflow: ellipsis; }` with the full value in `title`.
- The table keeps horizontal scroll inside its frame; the sticky column is the visual cue that more columns exist.

---

## 6. Do and don't (verifiable with `check-consumer-tokens` or grep)

**Do**

1. Use only `var(--…)` from the design-system for color, size, weight, spacing, radius, shadow, control height and width.
2. Use a `.module.css` per component; the remote root carries `data-mfe="<domain>"`.
3. Follow the anatomy of section 5: one h1 per page, sentence case.
4. Show status with colour + text (+ dot or icon), never colour alone.
5. Use `tabular-nums` on number, date, time and count columns.
6. Use explicit transition properties: `transition: background-color var(--duration-fast) ease`. On button `:active`, `transform: scale(0.98)`.
7. Keep focus visible: `outline: var(--focus-ring-width) solid var(--color-brand); outline-offset: 2px` on `:focus-visible`.
8. Respect `prefers-reduced-motion`.
9. Keep touch targets at 44 px at <= 768 px (section 3) and the drawer contract (section 4.1).

**Don't** (the check fails if any appears outside `design-system/src/`)

1. Color literals (`#…`, `rgb(…)`).
2. Literal sizes (`0.85rem`, `0.925rem`, `1.75rem`, `15px`, `9px`) and spacing tokens used as font size.
3. Numeric `font-weight` (`600`, `800`), or `700` / `800` through a token in the app.
4. A `font-family` other than `var(--font-family-base)`, or an own `@font-face`.
5. Literal fallbacks: `var(--color-brand, #027D32)`. The token always exists.
6. `transition: all`.
7. `min-height: 100vh`, an own page background or a centered `max-width` on the page root.
8. A card inside a card; a "card header" that repeats the h1.
9. A bordered button for every item of a list or menu.
10. `text-transform: uppercase` in table headers, menu or buttons.
11. `box-shadow` on in-page surfaces (overlays only).
12. `border-radius: 9999px` outside badges and avatars.

---

## 7. Rollout order (docs first)

1. **docs:** this file, [design-tokens.md](./mockup-ddd/design-tokens.md) and the HU-001 E2 criterion (HU-SHELL-019).
2. **design-system:** one PR with the tokens of `design-tokens.md` (regenerate, fix `ui.css`, update the token tests: `size3xl`, `topbar_height`, `sidebar_width`, `control_height_touch = 44px`; new tests for `color_text_subtle` >= 4.5:1 and `table_row_height` >= 24 px).
3. **web-shell:** `AppShell.module.css` (density, flat menu, sections, mobile drawer with the contract of 4.1), `navigation-table.ts` and `use-navigation.ts` (feature filter).
4. **MFEs:** `scheduling-mfe` (`SchedulesPage`) as pilot, then the other eight. Each must leave `check-consumer-tokens` green. Existing tests must pass without changing any `data-testid` or `aria-label`; only table header texts may change.

Non-visual consequences the owner ratified together: menu filter by features and `actor_type` (presentation only), "Inicio" visible to everyone, mobile menu as a drawer instead of stacked, "Limpiar" visible only with active filters, no "card header" with the count, and pager "Anterior / Siguiente" as icons only (keeping `aria-label="Página anterior/siguiente"`).

---

## Referencias

- [mockup-ddd/design-tokens.md](./mockup-ddd/design-tokens.md) — token values
- [navigation-map.md](./navigation-map.md) · [mockup-ddd/sitemap.md](./mockup-ddd/sitemap.md) — navigation by role
- [../04-requirements/user-stories.md](../04-requirements/user-stories.md) — HU-SHELL-019
