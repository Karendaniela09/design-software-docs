# Gobierno documental

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

## Contexto

Este directorio contiene las reglas y políticas que todos los equipos deben seguir para documentar el proyecto **Horarios SENA**. El objetivo es mantener un repositorio ordenado, trazable y seguro, evitando duplicación de información y fugas de datos sensibles.

## Contenido

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [documentation-rules.md](./documentation-rules.md) | Naming, estructura mínima, estados, índices y diagramas | 🟢 |
| [git-conventions.md](./git-conventions.md) | Ramas (main/dev/qa/staging), ambientes, releases y commits | 🟢 |
| [microservices-documentation.md](./microservices-documentation.md) | Reglas para documentar microservicios reales | 🟢 |
| [security-rules.md](./security-rules.md) | Reglas contra fugas de información sensible | 🟢 |
| [definition-of-ready.md](./definition-of-ready.md) | Criterios para saber si un documento puede pasar a revisión | 🟢 |
| [definition-of-done.md](./definition-of-done.md) | Criterios para cerrar un documento como estable | 🟢 |

## Reglas de oro

1. **No trabajar directamente sobre `main`, `dev`, `qa` ni `staging`** — siempre usar ramas hijas y Pull Requests.
2. **Todo documento debe tener estado, autor y fecha** (usar la estructura mínima).
3. **No publicar credenciales, tokens, ni datos personales reales** (usar ejemplos seguros).
4. **Todo diagrama debe tener fuente editable** (no subir solo la imagen exportada).
5. **Los microservicios solo se documentan cuando existen en código o tienen ADR aprobada.**

## Referencias

- [CONTRIBUTING.md](../CONTRIBUTING.md) — Guía de contribución general
- [CHANGELOG.md](../CHANGELOG.md) — Historial de cambios del repositorio
- [security-rules.md](./security-rules.md) — Seguridad documental