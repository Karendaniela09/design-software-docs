# Technical Report R1 — Resilience and Messaging (Document)

**Owner:** Danna Valentina Barrios Penagos. **Branch:** `hu-r1-dev` from `develop`. **Date:** October 20, 2026.

**Design decision:** ADR-011 in the `design-software-docs` repository (`05-architecture/decisions/records/ADR-011-document-outbox-inbox-resilience.md`).  
**Screenshots:** delivered with the QA submission Markdown and not stored in this repository.

## 1. Delivered scope

| Challenge criterion | Implementation | Test |
|---|---|---|
| (a) Transactional outbox | `complete_generation` writes the version, status, inbox receipt, and `event_outbox` rows in one transaction. `apps.outbox_dispatcher.main` delivers pending rows. | `test_generation_request_becomes_an_available_downloadable_document`, chaos test |
| (b) Idempotent consumer with deduplication table | `document.message_inbox` uses primary key `(consumer_name, document_id, message_id)`; redelivery is answered from the receipt without rendering again. `event_id` is deterministic. | `test_new_version_and_redelivered_message`, chaos test |
| (c) Exponential backoff retries and DLQ with manual replay | Rendering: `min(backoff * 2^(n-1), 30 s)`. Outbox publishing: `min(2^(n-1), 300 s)`. DLQ: `pdf-renderer.dlq`; `apps.replay_dlq.main` republishes with confirmation and only then acknowledges the message. | `test_definitive_failure_...`, `test_manual_dlq_replay_...`, `test_long_retry_delay_...` |
| (d) Automated chaos test | Two scenarios (Section 4): one in-process and one against deployed containers, including an actual worker and dispatcher restart. | `test_broker_outage_after_commit_...` and `test_chaos_broker_outage_and_service_restart_...` |

## 2. Reproduction

Requirements: Docker, Python 3.12, and the Document stack running with the `docker-infra` profile:

```bash
docker compose --profile document --profile iam --profile tooling --profile edge up -d --build
pip install -e '.[dev]'
```

Integration test variables: `TEST_POSTGRES_DB_URL`, `TEST_AMQP_URL`, `TEST_S3_ENDPOINT` and, optionally, `TEST_S3_ACCESS_KEY` and `TEST_S3_SECRET_KEY`. Chaos scenarios additionally use:

- `TEST_CHAOS_COMPOSE_FILE`: absolute path to the `docker-compose.yml` file from `docker-infra`.
- `TEST_CHAOS_PROJECT` and `TEST_CHAOS_ENV_FILE` (optional): Compose project name and environment file.

```bash
python -m pytest -q
python -m pytest -q tests/test_pdf_renderer_worker_integration.py -k "broker_outage or service_restart"
```

Without `TEST_CHAOS_COMPOSE_FILE`, both chaos scenarios are cleanly skipped (`5 passed, 2 skipped`, with no errors). If the stack uses another Compose project name, the failure indicates that `TEST_CHAOS_PROJECT` and `TEST_CHAOS_ENV_FILE` must be configured.

**Isolation.** The deployed worker and dispatcher share the database with the processes running inside `pytest` and could publish outbox rows before the test does. Therefore, the `infra` fixture stops them at the beginning and starts them again at the end, except for the test marked `deployed_stack`, which controls them directly. No manual steps are required.

## 3. Results

Baseline: the service suite on a clean `develop` branch (without R1) produces **98 passed**.

With the R1 changes, the complete suite, the stack running, and chaos enabled, two consecutive runs produced:

```text
tests/test_pdf_renderer_worker_integration.py
  test_generation_request_becomes_an_available_downloadable_document   PASSED
  test_new_version_and_redelivered_message                             PASSED
  test_definitive_failure_marks_the_document_failed_and_sends_the_message_to_the_dlq   PASSED
  test_manual_dlq_replay_recovers_after_a_transient_renderer_failure   PASSED
  test_long_retry_delay_keeps_the_broker_connection_alive              PASSED
  test_broker_outage_after_commit_preserves_events_and_restart_is_idempotent   PASSED
  test_chaos_broker_outage_and_service_restart_lose_no_event_and_duplicate_none   PASSED

======================= 101 passed in 150.63s (0:02:30) =======================
```

Migrations: changeset `975` is applied after the previous 18 changesets, for a total of 19. On a new database, the `document_reader`, `document_writer`, and `document_admin` roles may not exist; therefore, the `GRANT` statements are conditional and the changeset uses `splitStatements: false`. Rollback was tested: it removes both tables and returns to 18 changesets; reapplying restores 19.

The real IAM gateway flow (generation, outbox, inbox, events, and download) completed 29 of 30 checks. The only failure is the CORS preflight, which `docker-infra` does not configure for any domain and is outside the scope of this challenge.

Database state after the flow:

```text
         event_type          | attempts | published | event_id
-----------------------------+----------+-----------+----------
 document.version.created    |        0 | t         | c79f8673
 document.document.generated |        0 | t         | 3b3c08bf
 ...

    consumer_name    | document |  message_id  | version
---------------------+----------+--------------+----------
 pdf-renderer-worker | a51e5094 | corr-7a5beb8 | 61c9b0e7
 ...

 published | pending
-----------+---------
         8 |       0
```

## 4. Chaos testing

**Scenario A — in-process** (`test_broker_outage_after_commit_preserves_events_and_restart_is_idempotent`): the worker confirms the version with two pending events; RabbitMQ is stopped and dispatch reports `(0 published, 2 deferred)`; after restart it reports `(2 published, 0 deferred)`. A new worker receives the same command again and creates neither another version nor additional events.

**Scenario B — deployed containers** (`test_chaos_broker_outage_and_service_restart_lose_no_event_and_duplicate_none`):

1. The dispatcher is stopped and the generation command is published; the deployed worker confirms the version and two rows remain pending in the outbox.
2. RabbitMQ is stopped during the flow.
3. The worker and dispatcher are restarted while the broker is still down; the dispatcher defers both rows (`attempts > 0`) and nothing is lost because the rows remain in PostgreSQL.
4. RabbitMQ is started; the restarted dispatcher publishes both rows.
5. Exactly two events are verified, with different types and different `event_id` values.
6. The same command is sent to the restarted worker; there is still one version, no new events, and no pending rows.

These scenarios demonstrate the two Acta criteria: **zero lost events and zero duplicate effects** after the broker is stopped and the service is restarted.

## 5. Decisions and limitations

- **At-least-once delivery.** A broker confirmation followed by a failure before the `published_at` commit may repeat an event with the same `event_id`; consumers deduplicate by `event_id`.
- **Outbox rows that always fail.** They are retried with backoff up to 300 seconds and have no dedicated DLQ; they remain visible through `attempts` and `last_error`. A hard limit and failure status would be required if a strict cap were mandated. The manual-replay DLQ covers generation messages.
- **Generation request.** `POST /documents/generate` publishes directly to the queue and returns 503 if it cannot; the outbox protects events generated after rendering.
- **Publishing lock.** The dispatcher keeps the row lock while publishing. This is simple and correct; with very high volume, batch claiming would be advisable.
