# Revisión de código (Code Review)

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Desarrollo

## Contexto

Este documento define el proceso de revisión de código (Code Review) para el sistema **Horarios SENA**. Todas las contribuciones al código deben pasar por una revisión antes de ser integradas a la rama `dev`.

El objetivo es garantizar la calidad, consistencia y seguridad del código, así como compartir conocimiento entre los miembros del equipo.

## Flujo de revisión

1. El desarrollador escribe el código en una rama hija.
2. El desarrollador crea un Pull Request (PR) hacia la rama `dev`.
3. El PR se asigna a uno o más revisores.
4. Los revisores analizan el código y dejan comentarios.
5. El autor realiza los cambios solicitados.
6. Cuando todos los comentarios están resueltos, el PR se aprueba.
7. El PR se fusiona (merge) a la rama `dev`.

## Roles en la revisión

| Rol | Responsabilidad |
|-----|-----------------|
| **Autor** | Crea el Pull Request, responde comentarios, realiza cambios solicitados. |
| **Revisor** | Revisa el código, hace comentarios, aprueba o solicita cambios. |
| **Aprobador** | Tiene la autoridad final para aprobar y hacer merge (Tech Lead o Arquitecto). |

## Checklist de revisión

### 1. Arquitectura y diseño

- [ ] El código sigue los principios de Clean Architecture.
- [ ] Las dependencias apuntan hacia adentro (domain → application → infrastructure).
- [ ] No hay lógica de negocio en controladores o DTOs.
- [ ] No hay lógica de persistencia en la capa de dominio.

### 2. Estilo y formato

- [ ] El código sigue las convenciones de estilo (Google Java Style Guide / Prettier).
- [ ] Los nombres de clases, métodos y variables son descriptivos.
- [ ] No hay código muerto o comentado.
- [ ] Los imports están organizados.

### 3. Funcionalidad

- [ ] La funcionalidad cumple con los requisitos descritos en la historia de usuario.
- [ ] Los casos de borde están cubiertos.
- [ ] Las validaciones están implementadas (DTOs, lógica de negocio).

### 4. Pruebas

- [ ] Se agregaron pruebas unitarias para la nueva funcionalidad.
- [ ] Las pruebas existentes pasan.
- [ ] La cobertura de código no disminuye.
- [ ] Se incluyeron pruebas de integración si es necesario.

### 5. Seguridad

- [ ] No se exponen datos sensibles en logs o respuestas.
- [ ] Las validaciones de entrada están implementadas.
- [ ] Se usan parámetros bind para evitar inyección SQL.
- [ ] No hay credenciales hardcodeadas.

### 6. Documentación

- [ ] La API está documentada con OpenAPI (Swagger).
- [ ] Los métodos públicos tienen Javadoc/TSDoc.
- [ ] El README del módulo se actualizó si es necesario.

### 7. Rendimiento

- [ ] Las consultas a BD están optimizadas (índices, evita N+1).
- [ ] No hay operaciones bloqueantes innecesarias.
- [ ] Los timeouts están configurados.

## Tipos de comentarios

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| **Crítico** | Debe corregirse antes del merge. | "Esta consulta causa un N+1, debe optimizarse." |
| **Sugerencia** | Mejora opcional. | "Considera usar Optional en lugar de null." |
| **Pregunta** | Aclaración sobre el código. | "¿Por qué se usa este patrón aquí?" |
| **Elogio** | Reconocimiento de buena práctica. | "Excelente manejo de excepciones aquí." |

## Tiempos de respuesta

| Rol | Tiempo máximo |
|-----|---------------|
| **Revisor** | 24 horas para revisión inicial. |
| **Autor** | 48 horas para responder comentarios o realizar cambios. |
| **Aprobador** | 12 horas para aprobación final. |

## Criterios de aprobación

Un Pull Request puede ser aprobado cuando:

- [ ] Todos los comentarios críticos han sido resueltos.
- [ ] Al menos un revisor ha aprobado.
- [ ] Los tests pasan en el pipeline de CI.
- [ ] La cobertura de código no disminuye.
- [ ] La rama está actualizada con `dev`.

## Criterios de rechazo

Un Pull Request será rechazado si:

- La funcionalidad no cumple con los requisitos.
- Hay issues críticos de seguridad.
- La cobertura de código disminuye significativamente (>5%).
- Hay conflictos de merge no resueltos.

## Herramientas de soporte

| Herramienta | Propósito |
|-------------|-----------|
| **GitHub Pull Requests** | Plataforma de revisión. |
| **SonarQube** | Análisis automático de calidad (futuro). |
| **Codecov / JaCoCo** | Reporte de cobertura en PRs. |
| **Checkstyle / ESLint** | Validación automática de estilo. |

## Referencias

- [testing-strategy.md](./testing-strategy.md)
- [00-governance/git-conventions.md](../00-governance/git-conventions.md)
- [05-architecture/overview.md](../05-architecture/overview.md)