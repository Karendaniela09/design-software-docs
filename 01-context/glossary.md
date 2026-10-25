# Glosario

> Estado: 🟡 Borrador | Última actualización: 2026-08-28
> Puente entre el lenguaje de dominio (español SENA) y el técnico (inglés). Ver [domain-map.md](../02-domain/domain-map.md).

## Términos de dominio SENA

| Término | Definición | Entidad técnica (en) |
|---------|------------|----------------------|
| Ficha (de caracterización) | Instancia de un programa de formación para una cohorte específica de aprendices en un centro. Tiene número único de SOFIA Plus | `EnrollmentFicha` |
| Programa de formación | Diseño curricular aprobado a nivel nacional (Técnico, Tecnólogo, etc.) | `TrainingProgram` |
| Competencia | Unidad de aprendizaje dentro de un programa; norma de competencia laboral | `Competency` |
| RAP (Resultado de Aprendizaje) | Subunidad de una competencia; unidad mínima de formación | `LearningOutcome` |
| Juicio evaluativo | Resultado de evaluar a un aprendiz en un RAP: aprobado o no aprobado; sin juicio = pendiente. No hay nota numérica | `LearnerRapAssessment` (`APPROVED` / `NOT_APPROVED`) |
| Línea / Red tecnológica | Niveles de agrupación curricular por área de conocimiento | `TechLine` / `TechNetwork` |
| Jornada | Bloque de tiempo de operación: Diurna, Nocturna, Mixta (Madrugada/Fin de semana) | `training_shift` (catálogo) |
| Modalidad | Forma de impartir: Presencial, Virtual, Híbrida | `training_modality` (catálogo) |
| Horario | Conjunto de sesiones de clase asignadas a una ficha en un período | `Schedule` |
| Sesión de clase | Una clase concreta: ficha + instructor + ambiente + franja + fecha | `ClassSession` |
| Franja horaria | Bloque de tiempo recurrente (ej: lunes 07:00–10:00) | `TimeSlot` |
| Ambiente (de formación) | Espacio físico donde ocurre la clase: aula, laboratorio, taller | `Environment` |
| Instructor | Formador vinculado al SENA (planta, contratista u hora-cátedra) | `Instructor` |
| Aprendiz | Persona en proceso de formación, vinculada a una ficha | `Learner` |
| Etapa lectiva | Fase de formación en el centro | `current_stage = LECTURE` |
| Etapa productiva | Fase de práctica del aprendiz en una empresa | `ProductiveStage` |
| Coordinador (académico) | Responsable de gestionar fichas, instructores y horarios de un centro | rol `COORDINATOR` |
| Subdirector de centro | Máxima autoridad operativa del centro | rol `CENTER_DIRECTOR` |
| Plan de mejoramiento | Acciones para corregir desviaciones de un actor o una ficha | `ImprovementPlan` / `ActorImprovementPlan` |
| Bitácora | Registro cronológico de eventos de un actor | `ActivityLog` |
| SOFIA Plus | Sistema de información nacional del SENA (fuente de fichas y programas) | (sistema externo, ACL) |

## Términos técnicos / arquitectura

| Término | Definición |
|---------|------------|
| Bounded Context | Frontera lógica de un subdominio con su propio modelo (DDD). Equivale a un microservicio aquí |
| Microservicio | Servicio independiente con su propia BD, despliegue y equipo |
| Componente desplegable | Unidad ejecutable dentro de un servicio (`-api`, `-worker`, `-workflow`) |
| Arquitectura Hexagonal | Patrón que separa el dominio de la infraestructura mediante puertos y adaptadores |
| Read model | Proyección local de datos de otro servicio, poblada por eventos (ADR-002) |
| JWT | JSON Web Token; credencial firmada que porta identidad y permisos |
| JWKS | JSON Web Key Set; endpoint público (`/.well-known/jwks.json`) con las claves de firma de iam-service. Edge y servicios verifican el JWT RS256 **localmente** con estas claves, sin llamada síncrona a iam. Soporta rotación de clave (DEC-008) |
| Refresh token | Token de larga vida (7 días) que renueva el `access_token` (vida corta, 15 min) sin re-autenticar. El access token porta identidad/permisos; el refresh solo sirve para obtener uno nuevo |
| Idempotencia | Propiedad por la que procesar el mismo evento más de una vez produce el mismo resultado. Se garantiza deduplicando por `event_id` (p. ej. en notification-service) |
| RBAC | Role-Based Access Control; autorización por rol |
| Feature | Unidad atómica de permiso en este sistema (reemplaza resource+action) |
| Scope | Alcance de datos que un rol puede ver/operar (GLOBAL, TRAINING_CENTER, OWN_*) |
| Evento de dominio | Hecho de negocio ya ocurrido, publicado al broker (`scheduling.schedule.published`) |
| ACL (Anti-Corruption Layer) | Capa que traduce un modelo externo al modelo interno |
| Outbox pattern | Técnica para garantizar entrega de eventos consistente con la transacción de BD |
| DLQ (Dead Letter Queue) | Cola de mensajes que no pudieron procesarse tras varios reintentos |
| PII | Personally Identifiable Information; datos personales protegidos por ley |
| HALT-DB-NAMING | Regla del ecosistema: entidades/atributos/contratos en inglés, singular, ASCII |

## Estados clave

| Entidad | Estados |
|---------|---------|
| Ficha | INDUCTION → EXECUTION → PRODUCTIVE_STAGE → COMPLETED (o CANCELLED) |
| Horario | DRAFT → UNDER_REVIEW → PUBLISHED (→ ARCHIVED) |
| Aprendiz | ACTIVE / DROPOUT / TRANSFERRED / GRADUATED / CANCELLED |
| Seguimiento de ficha | ON_TRACK / AT_RISK / CRITICAL |
| Alerta | INFO / LOW / MEDIUM / HIGH / CRITICAL |
