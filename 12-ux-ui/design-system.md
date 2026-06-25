# Sistema de diseño

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Producto / Frontend

## Contexto

Este documento define el sistema de diseño del sistema **Horarios SENA**. Incluye colores, tipografía, espaciado, componentes y tokens de diseño que se utilizarán en toda la interfaz de usuario.

## Colores

| Nombre | Código HEX | Uso |
|--------|------------|-----|
| **Primario** | `#0D6EFD` | Botones principales, enlaces, elementos activos. |
| **Primario oscuro** | `#0056B3` | Hover y estados activos de elementos primarios. |
| **Secundario** | `#6C757D` | Elementos secundarios, texto de ayuda. |
| **Éxito** | `#198754` | Mensajes de éxito, confirmaciones. |
| **Advertencia** | `#FFC107` | Mensajes de advertencia, alertas. |
| **Error** | `#DC3545` | Mensajes de error, acciones peligrosas. |
| **Info** | `#0DCAF0` | Mensajes informativos. |
| **Fondo claro** | `#F8F9FA` | Fondo de páginas y tarjetas. |
| **Texto principal** | `#212529` | Texto en modo claro. |
| **Texto secundario** | `#6C757D` | Texto de ayuda, etiquetas. |
| **Borde** | `#CED4DA` | Bordes de inputs, tablas, tarjetas. |

## Tipografía

| Estilo | Tamaño | Peso | Uso |
|--------|--------|------|-----|
| **H1** | 2rem | 700 | Títulos de página. |
| **H2** | 1.5rem | 600 | Subtítulos de sección. |
| **H3** | 1.25rem | 600 | Títulos de tarjetas. |
| **H4** | 1rem | 600 | Títulos de tablas. |
| **Body** | 1rem | 400 | Texto principal. |
| **Small** | 0.875rem | 400 | Texto secundario, etiquetas. |
| **Caption** | 0.75rem | 400 | Texto muy pequeño, notas. |

**Fuente base:** `'Inter', sans-serif`

## Espaciado

| Token | Valor | Uso |
|-------|-------|-----|
| `space-xs` | 4px | Espaciado mínimo entre elementos. |
| `space-sm` | 8px | Espaciado entre elementos relacionados. |
| `space-md` | 16px | Espaciado estándar. |
| `space-lg` | 24px | Espaciado entre secciones. |
| `space-xl` | 32px | Espaciado entre bloques grandes. |

## Bordes y sombras

| Elemento | Valor |
|----------|-------|
| **Border radius (inputs)** | 4px |
| **Border radius (tarjetas)** | 8px |
| **Border radius (modales)** | 16px |
| **Sombra suave (tarjetas)** | `0 2px 4px rgba(0,0,0,0.1)` |
| **Sombra elevada (modales)** | `0 8px 16px rgba(0,0,0,0.2)` |

## Componentes base

| Componente | Descripción | Uso |
|------------|-------------|-----|
| **Button** | Botones primarios, secundarios, de peligro, de éxito. | Acciones principales y secundarias. |
| **Input** | Campos de texto, números, email, etc. | Formularios. |
| **Select** | Selectores desplegables. | Formularios con opciones predefinidas. |
| **Table** | Tablas con paginación, ordenamiento, filtros. | Listados de datos. |
| **Modal** | Ventanas modales para formularios o confirmaciones. | Crear/editar registros. |
| **Toast** | Notificaciones temporales (éxito, error, info). | Feedback de acciones. |
| **Card** | Tarjetas con contenido agrupado. | Dashboards, resúmenes. |
| **Sidebar** | Navegación lateral colapsable. | Menú principal. |
| **Spinner** | Indicador de carga. | Estados de carga. |

## Breakpoints (responsive)

| Dispositivo | Ancho mínimo | Comportamiento |
|-------------|--------------|----------------|
| **Móvil** | 320px | Sidebar colapsable, tablas con scroll horizontal. |
| **Tablet** | 768px | Columnas de tabla se apilan. |
| **Desktop** | 1024px | Layout de dos columnas, navegación lateral visible. |
| **Desktop XL** | 1440px | Layout amplio con más espacio. |

## Referencias

- [navigation-map.md](./navigation-map.md)
- [wireframes.md](./wireframes.md)
- [Figma - Sistema de diseño](https://www.figma.com/...)