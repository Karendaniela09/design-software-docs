# Dominio

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Dominio

## Contenido

Este directorio contiene el modelo de dominio del proyecto **Horarios SENA**. Aquí se definen los bounded contexts, las entidades principales, las reglas de negocio y los eventos de dominio que ocurren en el sistema.

> **Diferencia con `06-data`:** esta sección describe el dominio en términos de negocio (entidades, invariantes, reglas, lenguaje ubicuo). No describe tablas, columnas ni esquemas de base de datos. Esos detalles de implementación van en [`06-data/`](../06-data/).

## Archivos

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [domain-map.md](./domain-map.md) | Mapa de dominios y bounded contexts del sistema | 🟢 |
| [entities-and-rules.md](./entities-and-rules.md) | Entidades principales y reglas de negocio por módulo | 🟢 |
| [domain-events.md](./domain-events.md) | Eventos de dominio que se generan en el sistema | 🟢 |

## Referencias

- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [CHANGELOG.md](../CHANGELOG.md)
- [01-context/overview.md](../01-context/overview.md)
- [01-context/glossary.md](../01-context/glossary.md)