# Matriz de trazabilidad

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Producto / QA

## Contexto

La matriz de trazabilidad conecta los requisitos funcionales (RF), las historias de usuario (HU), las decisiones de arquitectura (ADR) y las pruebas (casos de prueba). Esto garantiza que cada requisito esté cubierto por al menos una historia de usuario y una prueba, y que las decisiones arquitectónicas estén alineadas con los requisitos.

---

## Leyenda

| Columna | Significado |
|---------|-------------|
| **RF** | Requisito funcional (RF-XXX) |
| **HU** | Historia de usuario (HU-XXX) |
| **ADR** | Decisión de arquitectura (ADR-NNN) |
| **Prueba** | Tipo de prueba que cubre el requisito (Unitaria, Integración, Aceptación) |
| **Cubierto** | ✅ = Sí, ⚠️ = Parcial, ❌ = No |

---

## Tabla de trazabilidad

| RF | HU | ADR | Prueba | Cubierto |
|----|----|-----|--------|----------|
| RF-001 | HU-001 | ADR-005 (Clean Architecture) | Unitaria, Integración | ✅ |
| RF-002 | HU-002 | ADR-005 | Unitaria, Integración | ✅ |
| RF-003 | HU-003 | ADR-005 | Unitaria, Integración | ✅ |
| RF-004 | HU-003 | ADR-005 | Unitaria, Integración | ✅ |
| RF-005 | HU-004 | ADR-005 | Unitaria, Integración | ✅ |
| RF-006 | HU-004 | ADR-005 | Unitaria, Integración | ✅ |
| RF-007 | HU-005 | ADR-005 | Unitaria, Integración | ✅ |
| RF-008 | HU-006 | ADR-005 | Unitaria, Integración | ✅ |
| RF-009 | HU-006 | ADR-005 | Unitaria, Integración | ✅ |
| RF-010 | HU-007 | ADR-005 | Unitaria, Integración | ✅ |
| RF-011 | HU-008 | ADR-005 | Unitaria, Integración | ✅ |
| RF-012 | HU-009 | ADR-005 | Unitaria, Integración | ✅ |
| RF-013 | HU-010 | ADR-005 | Unitaria, Integración | ✅ |
| RF-014 | HU-011 | ADR-005 | Unitaria, Integración | ✅ |
| RF-015 | HU-010, HU-011 | ADR-005 | Unitaria, Integración | ✅ |
| RF-016 | HU-012 | ADR-005 | Unitaria, Integración | ✅ |
| RF-017 | HU-010, HU-011 | ADR-005 | Unitaria, Integración | ✅ |
| RF-018 | HU-010, HU-011, HU-037 | ADR-004 (Auditoría) | Unitaria, Integración | ✅ |
| RF-019 | HU-013 | ADR-005 | Unitaria, Integración | ✅ |
| RF-020 | HU-013 | ADR-005 | Unitaria, Integración | ✅ |
| RF-021 | HU-013 | ADR-005 | Unitaria, Integración | ✅ |
| RF-022 | HU-014 | ADR-005 | Unitaria, Integración | ✅ |
| RF-023 | HU-015 | ADR-005 | Unitaria, Integración | ✅ |
| RF-024 | HU-015 | ADR-005 | Unitaria, Integración | ✅ |
| RF-025 | HU-015 | ADR-005 | Unitaria, Integración | ✅ |
| RF-026 | HU-016 | ADR-005 | Unitaria, Integración | ✅ |
| RF-027 | HU-015 | ADR-005 | Unitaria, Integración | ✅ |
| RF-028 | HU-017 | ADR-005 | Unitaria, Integración | ✅ |
| RF-029 | HU-018 | ADR-005 | Unitaria, Integración | ✅ |
| RF-030 | HU-018 | ADR-005 | Unitaria, Integración | ✅ |
| RF-031 | HU-019 | ADR-005 | Unitaria, Integración | ✅ |
| RF-032 | HU-020 | ADR-005 | Unitaria, Integración | ✅ |
| RF-033 | (Fase 3) | ADR-005 | Unitaria, Integración | ⚠️ |
| RF-034 | HU-020 | ADR-005 | Unitaria, Integración | ✅ |
| RF-035 | HU-021 | ADR-005 | Unitaria, Integración | ✅ |
| RF-036 | HU-022 | ADR-005 | Unitaria, Integración | ✅ |
| RF-037 | HU-023 | ADR-003 (Validación de conflictos) | Unitaria, Integración | ✅ |
| RF-038 | HU-023 | ADR-003 | Unitaria, Integración | ✅ |
| RF-039 | HU-023 | ADR-003 | Unitaria, Integración | ✅ |
| RF-040 | HU-023 | ADR-003 | Unitaria, Integración | ✅ |
| RF-041 | HU-025 | ADR-005 | Unitaria, Integración | ✅ |
| RF-042 | HU-024 | ADR-005 | Unitaria, Integración | ✅ |
| RF-043 | HU-025 | ADR-005 | Unitaria, Integración | ✅ |
| RF-044 | HU-026 | ADR-005 | Unitaria, Integración | ✅ |
| RF-045 | HU-027 | ADR-005 | Unitaria, Integración | ✅ |
| RF-046 | HU-028 | ADR-005 | Unitaria, Integración | ✅ |
| RF-047 | HU-029 | ADR-005 | Unitaria, Integración | ✅ |
| RF-048 | HU-030 | ADR-005 | Unitaria, Integración | ✅ |
| RF-049 | HU-030 | ADR-005 | Unitaria, Integración | ✅ |
| RF-050 | HU-030 | ADR-005 | Unitaria, Integración | ✅ |
| RF-051 | HU-031 | ADR-005 | Unitaria, Integración | ✅ |
| RF-052 | HU-031 | ADR-005 | Unitaria, Integración | ✅ |
| RF-053 | HU-033 | ADR-005 | Unitaria, Integración | ✅ |
| RF-054 | HU-032 | ADR-005 | Unitaria, Integración | ✅ |
| RF-055 | HU-034 | ADR-002 (JWT) | Unitaria, Integración | ✅ |
| RF-056 | HU-035 | ADR-002 | Unitaria, Integración | ✅ |
| RF-057 | HU-036 | ADR-002 | Unitaria, Integración | ✅ |
| RF-058 | HU-037 | ADR-004 | Unitaria, Integración | ✅ |
| RF-059 | HU-034 | ADR-002 | Unitaria, Integración | ✅ |
| RF-060 | HU-034 | ADR-002 | Unitaria, Integración | ✅ |
| RF-061 | HU-038 | ADR-006 (Notificaciones) | Integración, Aceptación | ⚠️ |
| RF-062 | HU-039 | ADR-006 | Integración, Aceptación | ⚠️ |
| RF-063 | HU-037 | ADR-004 | Unitaria, Integración | ✅ |
| RF-064 | HU-040 | ADR-007 (Reportes) | Integración, Aceptación | ⚠️ |

---

## Resumen de cobertura

| Estado | Cantidad | Porcentaje |
|--------|----------|------------|
| ✅ Cubierto | 58 | 90.6% |
| ⚠️ Parcial | 6 | 9.4% |
| ❌ No cubierto | 0 | 0% |
| **Total** | **64** | **100%** |

---

## Decisiones de arquitectura (ADR) relacionadas

| ADR | Título | RF relacionados |
|-----|--------|-----------------|
| ADR-001 | Clean Architecture para el backend | RF-001 a RF-064 |
| ADR-002 | Autenticación con JWT y Spring Security | RF-055, RF-056, RF-057, RF-059, RF-060 |
| ADR-003 | Validación de conflictos de horario en tiempo real | RF-037, RF-038, RF-039, RF-040 |
| ADR-004 | Auditoría append-only | RF-018, RF-058, RF-063 |
| ADR-005 | Microservicios y bases de datos por servicio | RF-001 a RF-064 |
| ADR-006 | Sistema de notificaciones por email | RF-061, RF-062 |
| ADR-007 | Generación de reportes asíncronos | RF-064 |

---

## Referencias

- [functional.md](./functional.md) — Requisitos funcionales
- [user-stories.md](./user-stories.md) — Historias de usuario
- [05-architecture/decisions/](../05-architecture/decisions/) — Registro de ADRs
- [11-quality/testing-strategy.md](../11-quality/testing-strategy.md) — Estrategia de pruebas