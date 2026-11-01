# HU-INT-REF-002: Institutional hierarchy integration

> Status: In review | Last updated: 2026-10-25
> Author/team: Reference Data team

Issue: [docs#295](https://github.com/code-sena/design-software-docs/issues/295).
Status: implementation candidate; acceptance criterion 6 awaits an approved deactivation policy.

## Context

Integrate macroregions, microregions, departments, municipalities, training centers and institutional units through the authenticated shell, Reference Data API and PostgreSQL. This delivery builds on HU-INT-REF-001 and reuses the transactional messaging implementation described in [ADR-021](../05-architecture/decisions/records/ADR-021-reference-data-resilient-messaging.md). The durable publication requirement remains a dependency of HU-INT-REF-004; the tests here verify the available implementation without asserting that the separate story has been accepted.

## Content

### Contract and immutable center identity

The canonical API is [reference-data.yaml](../07-api/contracts/openapi/reference-data.yaml) with [_shared.yaml](../07-api/contracts/openapi/_shared.yaml). The MFE records the exact source revision and hashes in `contracts/openapi/source.json`; run `npm run generate:types` and `npm run check:types` to reproduce its types. The shared-contracts copy must match this revision.

Existing domain rules RN-REF-01 and RN-REF-02 in [entities and rules](../02-domain/entities-and-rules.md) prohibit reassigning a center to another municipality and changing its code. Update properties remain accepted for compatibility only when equal to the stored values; a change returns HTTP 409 with `IMMUTABLE_FIELD` and leaves the record unchanged. New MFE updates omit both fields. This resolves the earlier mismatch between the update schema and the domain rules without allowing a new reassignment policy.

### Resource operations and selectors

All routes have the public prefix `/reference-data/api/v1` and upstream prefix `/api/v1`. Resources are `macroregions`, `microregions`, `departments`, `municipalities`, `training-centers` and `institutional-units`. List and get use GET, create uses POST (201), edit uses PUT (200), and deactivate uses DELETE `/{id}` (204). Deactivation preserves the row with `is_active=false`; list `is_active=true` and `is_active=false` permit review of either state. Omit the filter for both states.

| Resource | Parent filter / UUID field |
|---|---|
| Microregion | `macroregion_id` |
| Department | `microregion_id` |
| Municipality | `department_id` |
| Training center | `municipality_id` |
| Institutional unit | `training_center_id` |

Center creation uses four chained geographical selectors. Changing a parent clears every descendant and cancels obsolete requests. Parent option loaders traverse all API pages (100 per page with stable `id:asc` ordering); table pagination does not truncate form choices. Unit types are exactly `ACADEMIC`, `ADMINISTRATIVE`, and `MIXED`. Identifiers are resource UUIDs, never labels or business codes.

Invalid request fields, malformed UUIDs and unsupported unit types return 400 `BAD_REQUEST`. Missing resources or parent UUIDs return 404 `NOT_FOUND`; duplicate constrained data returns 409 `CONFLICT`; center identity changes return 409 `IMMUTABLE_FIELD`. Errors use `{error:{code,message,trace_id}}`. The MFE shows the API message while retaining the form for correction. A 409 response definition on a delete operation describes how an approved future dependency veto would be represented; it does not establish a veto rule.

### Authorization

Every resource GET requires `REF_HIERARCHY_VIEW:GLOBAL`; POST, PUT and DELETE require `REF_HIERARCHY_MANAGE:GLOBAL`. A read-only user can navigate and consult without MANAGE. Direct API requests enforce the same features independently of presentation permissions. MANAGE does not imply VIEW at the API boundary; IAM must grant each intended capability. These permissions do not authorize scoped grants to become global.

### Pending deactivation decision (acceptance criterion 6)

No approved list of blocking usages or consumer usage-check contract was found for municipalities, centers or units. The existing soft-deactivation behavior is preserved. A foreign key does not prevent an UPDATE of `is_active`. Child records alone are not treated as a newly invented veto, and Reference Data never queries another service's database.

Before approving criterion 6, the domain owner must specify which usages block each operation, which service owns the usage facts, the API/event contract for consulting those facts, the response when that service is unavailable, and how concurrent creation of a usage is handled. Then implement and test the approved 409 rule, unchanged state on veto and the UI conflict explanation. Until that decision and verification exist, the story must remain open even if the technical suite passes.

### Durable center-created event and verification

When `REFERENCE_DATA_AMQP_URL` is configured, center creation and `reference.training_center.created` are committed in the same transaction. The relay retries the persisted event ID and payload; the inbox/projection deduplicates delivery. Configure the broker in integrated environments; the standalone console publisher is not evidence of durable delivery.

Run `validation/int-ref-002/run.ps1` in docker-infra against a new isolated project. It uses the actual migrations, restricted application account, IAM signing keys, shell/MFE production builds and canonical edge routing. Fixture secrets and raw evidence are ignored by Git. It also stops RabbitMQ, creates a center successfully, verifies its committed outbox event, restarts RabbitMQ and Reference Data, and verifies recovery plus three deliberate redeliveries behind a consumer processing barrier. The expected result is one inbox entry and one projection effect.

The dedicated shell suite is `playwright.hierarchy.config.ts`, using `INT_REF_BASE_URL` and `INT_REF_FIXTURE_PASSWORD` from the runner. It checks hierarchy CRUD/status/error responses, read-only access, chained selectors, persisted browser edits and option lists beyond the first page. Evidence records technical pass/failure separately from the pending business decision; it must not mark all acceptance criteria complete automatically.

## References

- [Integration baseline](reference-data-int-ref-001.md)
- [Messaging runbook](../09-microservices/services/02-reference-data-service/runbook.md)
- [Business requirements](../04-requirements/functional.md)
