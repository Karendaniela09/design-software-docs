# Notification: resolución real de destinatarios

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

Configuración del worker:

```sh
export ACTORS_BASE_URL="http://actors-api:8080"
export IAM_BASE_URL="http://iam-api:8080"
export ACTORS_ACCESS_TOKEN_FILE="/run/actors-access-token.txt"
```

`notification-worker` consumes `scheduling.schedule.published` and `monitoring.alert.triggered`
(RabbitMQ, topic exchanges `scheduling-events`/`monitoring-events` per ADR-001) and, per event:
resolves the real contact through protected Actors APIs for Instructor/Learner references,
or IAM `/api/v1/users/{id}` for a schedule's `published_by` user UUID. There is no fixed-email
fallback. It attempts delivery (`Notifier`: SMTP to MailHog for EMAIL, no-op for IN_APP), and
persists the resulting `SentNotification` (`SENT`/`FAILED`). Idempotency (no double delivery for a
redelivered `event_id`) is enforced at the database level via a unique index on
`sent_notification.source_event_id`, not just app logic. On a successful send, it also stages
`notification.notification.sent` in `notification.outbox` in the **same transaction** as the status
change; a separate `OutboxRelay` polls unpublished rows and publishes them to `notification-events`
(consumed by `audit-service`), marking `published_at`.

Deliberate simplification: `scheduling.schedule.published` carries `instructor_ids` (plural), not a
single recipient; this HU notifies `published_by` only (a "your schedule was published"
confirmation) rather than fanning out one notification per instructor, since fan-out would conflict
with the one-row-per-`source_event_id` idempotency index. See `recipientRefFor` in
`internal/application/usecase/consume_domain_event.go`.

The worker requires `ACTORS_BASE_URL`, `IAM_BASE_URL` and `ACTORS_ACCESS_TOKEN_FILE`.
Mount the token file read-only; a credential agent/operator must renew its short-lived IAM
access token before expiry. The resolver rereads it for every lookup and rejects non-200,
inactive, mismatched or invalid-email contacts. Redirects never receive the bearer token.
Use HTTPS outside the isolated local Docker network and grant only the required contact-read
permissions. The R3 integration uses a dedicated local IAM reader and an SMTP sink;
institutional IdP access has not been provided or tested.
