# Estrategia de pruebas

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: QA / Arquitectura

## Contexto

Este documento define la estrategia de pruebas del sistema **Horarios SENA**. Las pruebas están organizadas por niveles (unitarias, integración, aceptación) y se ejecutan automáticamente en el pipeline de CI/CD. El objetivo es garantizar la calidad, estabilidad y confiabilidad del sistema.

## Pirámide de pruebas

```text
                     ┌─────────────┐
                     │  E2E / UI    │  ← Pocas, críticas
                     │  (Cypress)   │
                    ─┴─────────────┴─
                 ┌───────────────────┐
                 │   Integración     │  ← Algunas, por módulo
                 │   (Testcontainers)│
                ─┴───────────────────┴─
             ┌───────────────────────────┐
             │      Unitarias            │  ← Muchas, rápidas
             │   (JUnit + Mockito)       │
             └───────────────────────────┘