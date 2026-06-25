# Patrones de comunicación entre microservicios

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: Arquitectura

## Contexto

Los microservicios del sistema **Horarios SENA** necesitan comunicarse entre sí para intercambiar datos y coordinar operaciones. Se utilizan dos patrones principales: **comunicación síncrona** (REST) para operaciones inmediatas y **comunicación asíncrona** (eventos) para procesos que no requieren respuesta inmediata o que deben desacoplarse.

## Comunicación síncrona (REST)

### Cuándo usarla

- Consultas de datos que requieren respuesta inmediata.
- Operaciones CRUD simples.
- Validaciones en tiempo real (ej. verificar disponibilidad de un instructor antes de crear un horario).

### Tecnología

- **Protocolo:** HTTP/HTTPS.
- **Formato:** JSON.
- **Framework:** Spring Boot con RestTemplate o WebClient.

### Ejemplo de flujo síncrono

```text
1. El frontend solicita la lista de horarios de un instructor.
2. El scheduling-service recibe la petición.
3. El scheduling-service consulta a actors-service por el instructor (GET /instructors/{id}).
4. actors-service devuelve los datos del instructor.
5. scheduling-service construye la respuesta y la devuelve al frontend.