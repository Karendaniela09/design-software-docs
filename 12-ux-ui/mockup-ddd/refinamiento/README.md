# Refinamiento desde el mockup — proceso

Ronda de refinamiento **técnico** de requerimientos → base de datos → mockup, **antes de iniciar backend**.
El insumo crudo es el feedback que la gente dejó al usar el mockup como usuario final; aquí eso se
convierte en **decisiones técnicas versionadas**.

- **Mockup a revisar:** https://code-sena.github.io/design-software-mockup/ (índice: `#/inventory`)
- **Feedback crudo (Drive):** https://drive.google.com/drive/folders/17ek3tHMEv1tKWP7nYwjDp0POE3-iYzJi
- **Plantilla base:** [`PLANTILLA-refinamiento.md`](PLANTILLA-refinamiento.md) — **no se edita**; se copia.

## Cómo participar (cada aprendiz, individual)

1. **Copia** la plantilla a `respuestas/` con tu nombre y ficha:
   `respuestas/<nombre-apellido>-<ficha>.md`  (ej. `respuestas/juan-perez-3145555.md`).
2. **Llénala** con criterio técnico: por cada propuesta del Drive, decide
   ✅ Aceptar / 🔧 Aceptar con ajuste / ❌ Rechazar / 💬 Discutir, y **justifica**.
3. Respeta el **orden**: A) Requerimientos → B) Base de datos → C) Mockup.
4. Marca lo que **bloquea backend** (Sección E).
5. **Súbela por rama hija + PR a `develop`** (git-flow del proyecto):
   ```bash
   git checkout -b refinamiento/<tu-nombre>-dev origin/develop
   # crea tu respuestas/<nombre>-<ficha>.md y llénalo
   git add 12-ux-ui/mockup-ddd/refinamiento/respuestas/<nombre>-<ficha>.md
   git commit -m "docs(refinamiento): revisión de <nombre> (<ficha>)"
   git push -u origin refinamiento/<tu-nombre>-dev
   # abre PR: refinamiento/<tu-nombre>-dev  ->  develop
   ```
   > Solo agregas **tu** archivo en `respuestas/`; no toques los de otros ni el resto del repo.

## Qué pasa después (consolidación)

- Se recogen todas las respuestas de `respuestas/`.
- Se agrupan por ID de propuesta (`P-REQ-xx`, `P-BD-xx`, `P-MOCK-xx`) y se cuentan decisiones
  (mayoría / conflicto).
- Los ✅ con consenso pasan a implementación por capa (REQ → BD → Mockup).
- Los 💬 y los divididos van a reunión de cierre.
- La Sección E de todas se consolida en `CONSOLIDADO.md` → **backlog bloqueante de backend**
  (debe quedar en **cero** para arrancar a codificar). Ese archivo aún no se ha generado.

## Estructura

```
refinamiento/
├── README.md                  (este archivo)
├── PLANTILLA-refinamiento.md  (base, no editar)
├── respuestas/                (una por persona: <nombre>-<ficha>.md)
└── CONSOLIDADO.md             (se genera al integrar)
```
