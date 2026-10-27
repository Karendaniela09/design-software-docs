# Imágenes de evidencia

> Estado: 🟡 En progreso | Última actualización: 2026-10-24
> Autor: Valery Sinai Trujillo Quintero | Equipo: Reference Data

## Contexto

Este índice conserva las capturas R3 de Monitoring y registra las capturas de validación local HU-REF-020/R1 sobre los repositorios originales. Se captura exclusivamente el contenido del remote: no se muestran identidad, correo, controles de sesión ni tokens del host. Los catálogos y parámetros son fixtures sintéticas. Las imágenes ilustran la interfaz; las aserciones HTTP, SQL y logs acreditan el comportamiento técnico.

## Contenido

### Monitoring R3

- [Capturas R3](./r3-observability/README.md).

### Academic Management R1

- [Academic Management R1: captura del Shell y la ficha](academic-r1-shell-ficha.png) — evidencia visual de la [validación integrada R1](../../11-quality/academic-r1-validation-report.md).

### Training Environment R6

Las capturas R6 no están versionadas en este repositorio.

### Reference Data HU-REF-020 y R1

| Imagen | Evidencia |
|---|---|
| [reference-data-hu-ref-020-parameter.png](./reference-data-hu-ref-020-parameter.png) | HU-REF-020: parámetro creado, editado y persistido |
| [reference-data-hu-ref-020-learner.png](./reference-data-hu-ref-020-learner.png) | HU-REF-020: lectura de catálogos y restricciones de aprendiz |
| [reference-data-r1-recovered-catalog.png](./reference-data-r1-recovered-catalog.png) | R1: catálogo persistente después de recuperar broker y servicio |

Pendiente de la autora: captura del estado «escritura de catálogo durante caída de broker». La imagen registrada antes para ese estado era idéntica a la anterior y se retiró; hasta que exista la captura real, ese estado se acredita con las aserciones HTTP/SQL/logs del [informe](../../11-quality/reference-data-hu-ref-020-r1-validation.md).

## Referencias

- [Informe y resultados HU-REF-020/R1](../../11-quality/reference-data-hu-ref-020-r1-validation.md).
- [Reglas de seguridad documental](../../00-governance/security-rules.md).
