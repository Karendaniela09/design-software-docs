# Descripción general del proyecto

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura / Producto

## Contexto institucional

El Servicio Nacional de Aprendizaje (SENA) es una entidad pública colombiana creada mediante el Decreto Ley 118 de 1957, con la misión de ofrecer formación profesional integral a los trabajadores y jóvenes del país. Su estructura está distribuida en todo el territorio nacional, con 33 regionales, más de 100 centros de formación y miles de ambientes de aprendizaje.

En los centros de formación, la programación académica (horarios) es una actividad fundamental para el desarrollo de la formación profesional integral. Sin embargo, esta programación se realiza actualmente de manera manual o con herramientas desconectadas (hojas de cálculo, correos electrónicos, tableros físicos), lo que genera:

- Conflictos de asignación (un mismo instructor, ambiente o ficha en dos lugares a la misma hora).
- Sobrecarga administrativa en los coordinadores.
- Uso ineficiente de los recursos (ambientes, instructores).
- Falta de trazabilidad y control sobre la ejecución de la formación.

El proyecto **Horarios SENA** nace para resolver estos problemas mediante una plataforma centralizada, automatizada y validada algorítmicamente.

## Problema que resuelve el sistema

El sistema resuelve el problema de la **programación manual y conflictiva de horarios académicos** en los centros de formación del SENA. Permite asignar de manera automática y validada:

- Un **instructor** a una **ficha** en un **ambiente** en una **franja horaria**.
- Detecta en tiempo real conflictos (cruces) y los previene.
- Registra observaciones y novedades para seguimiento.

El sistema no reemplaza a SOFIA Plus (el sistema oficial de gestión académica del SENA), sino que se integra con él para consumir datos autorizados y aportar trazabilidad y control operativo.

## Objetivos

### Objetivo General

Construir un sistema modular, basado en microservicios, que permita gestionar la programación de horarios académicos en los centros de formación del SENA, con validación automática de conflictos y trazabilidad de la ejecución formativa.

### Objetivos Específicos

1. Gestionar la estructura institucional del SENA (macroregiones, microregiones, departamentos, municipios, centros de formación y sedes).
2. Administrar los catálogos base del sistema (modalidades de formación, jornadas, estados, líneas tecnológicas, etc.).
3. Gestionar los ambientes de aprendizaje (infraestructura, inventario, disponibilidad).
4. Gestionar los actores (instructores, aprendices, directivos) y sus perfiles.
5. Programar horarios asignando instructor, ambiente, ficha y franja horaria, con validación de conflictos.
6. Registrar observaciones e incidencias sobre los horarios.
7. Registrar la ejecución real de las sesiones de formación (trazabilidad).
8. Gestionar proyectos formativos y su relación con competencias y RAPs.
9. Generar notificaciones y reportes operativos.

## Valor a entregar (MVP)

El MVP (Producto Mínimo Viable) entregará:

- **Gestión de horarios conflict-free**: El sistema no permitirá doble asignación de instructor, ambiente o ficha en el mismo bloque horario.
- **Reducción del tiempo de planificación**: Los coordinadores podrán crear horarios en minutos, no en horas.
- **Visibilidad en tiempo real**: Consulta de disponibilidad de instructores y ambientes.
- **Trazabilidad básica**: Registro de observaciones y cambios.

## Usuarios del sistema

| Usuario | Rol | Responsabilidad |
|---------|-----|-----------------|
| Coordinador Académico | Planifica horarios, asigna recursos, gestiona incidencias | Creación y gestión de horarios |
| Instructor | Consulta su horario asignado y registra novedades | Consulta de horarios, registro de observaciones |
| Aprendiz | Consulta su horario de clases (futuro) | Consulta de horarios |
| Administrador | Configura catálogos, gestiona usuarios, audita el sistema | Configuración y mantenimiento |

## Referencias

- Ley 119 de 1994 — Estructura y misión del SENA
- Estatuto de la Formación Profesional Integral del SENA
- Manual de Diseño Curricular SENA
- [scope.md](./scope.md) — Alcance detallado del proyecto
- [glossary.md](./glossary.md) — Glosario de términos