# Visitas empresariales y eventos de Monitoring

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

`POST /api/v1/productive-stages/{id}/visits` conserva los campos obligatorios
`updated_at`/`updated_by` y escribe `actors_tracking.company_visit_outbox` en la
misma transacción que la visita. El evento `actors.company_visit.completed`
incluye la ficha de la matrícula vigente, aprendiz, instructor supervisor y
avance calculado con las horas persistidas de la etapa. Sin horas requeridas
válidas, el avance queda nulo; no se inventa una etapa completada.

Aplicar primero los changesets de la rama R3 de `design-software-actors-db`.
Para activar el relay, configurar `ACTORS_OUTBOX_ENABLED=true`, conexión RabbitMQ,
`SPRING_RABBITMQ_PUBLISHER_CONFIRM_TYPE=correlated` y
`SPRING_RABBITMQ_PUBLISHER_RETURNS=true`. El exchange durable es `actors-events`.
Un mensaje sin ruta, rechazado o sin confirmación permanece pendiente. El mismo
`event_id` se conserva en cada reintento; los consumidores deben deduplicarlo.

La integración aislada se configura en
`design-software-docker-infra/docker-compose.monitoring-integration.yml`.
La comprobación funcional está en
`design-software-monitoring-service/scripts/test_r3_domains.py`: crea entidades
mediante APIs protegidas y verifica las filas de outbox, la asignación del
instructor, la alerta, SMTP de pruebas y Audit. Las identidades y la matrícula
inicial son fixtures locales declarados en el script. El IdP institucional
no se utiliza y ninguna prueba envía correo fuera del buzón SMTP local.
