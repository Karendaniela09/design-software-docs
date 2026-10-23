# QA Technical Report R4 — IAM Session Revocation

> **Evaluation scope:** `design-software-iam-service`, branch `feat/r4-security-improvements`  
> **Documentation:** `design-software-docs`, branch `iam-r4-session-revocation`  
> **Database:** `design-software-iam-db`, branch `develop`  
> **Execution date:** 2026-10-23  
> **Status:** **VERIFIED — only formal QA promotion remains pending**

## 1. Executive summary

IAM R4 was verified at code, automated-test, and real-integration levels against isolated PostgreSQL and RabbitMQ infrastructure. The implementation validates that a valid JWT also corresponds to a persisted, active, non-revoked session owned by the authenticated user.

The evidence covers:

1. Domain and adapter unit tests.
2. The R4 security gate with 20 expected and 20 executed tests.
3. Real persistence against PostgreSQL 16 using the `iam-db/develop` migrations.
4. The outbox relay against a real, isolated RabbitMQ 3.13-management broker.
5. A successful targeted execution of `OutboxRelayPostgresIT`.

## 2. Repositories and branches verified

| Repository | Branch | R4 purpose |
|---|---|---|
| `design-software-iam-service` | `feat/r4-security-improvements` | Java/Spring IAM implementation and service tests |
| `design-software-iam-db` | `develop` | Schema, permissions, and Liquibase migrations |
| `design-software-docs` | `iam-r4-session-revocation` | ADR-018 and QA technical report |

## 3. Integration environment

The validation ran on temporary isolated infrastructure without modifying institutional environments:

| Component | Version/configuration | Result |
|---|---|---|
| PostgreSQL | 16, isolated test database | Available and reachable from IAM |
| RabbitMQ | 3.13-management, temporary isolated port | Available and reachable from the relay |
| Liquibase | Migrations from `design-software-iam-db/develop` | 37 changesets applied successfully |
| Application user | `design_software_app` with IAM read/write roles | Least-privilege connection verified |

The temporary infrastructure was stopped after testing. The isolated validation is documented as reproducible QA evidence.

## 4. Test results

### 4.1 Unit and module tests

The following commands were executed with Maven 3.9.9 and Java 21:

```text
mvn -B -ntp -pl iam-adapters -am test
mvn -B -ntp verify
```

| Suite | Result |
|---|---:|
| `iam-core` | 96/96 passed |
| `iam-adapters` | 90/90 passed |
| `iam-api` | 3/3 passed |
| Full Maven build | OK |
| Failures or errors | 0 |

### 4.2 R4 security gate

Surefire reports were compared with the 20 tests defined by `.github/workflows/iam-r4-security.yml`.

| Check | Result |
|---|---:|
| Expected R4 tests | 20 |
| Tests found | 20 |
| Missing tests | 0 |
| Failed, errored, or skipped tests | 0 |

Coverage includes invalid JWTs, `alg: none`, tampered or expired tokens, untrusted issuers, missing sessions, revoked sessions, sessions belonging to another user, and `VIEW`/`MANAGE` RBAC controls.

### 4.3 PostgreSQL integration

`mvn verify` was executed against a real PostgreSQL instance using `IAM_DB_DSN`, `IAM_DB_USERNAME`, and `IAM_DB_PASSWORD`, after applying the migrations from the `develop` branch.

```text
Integration tests detected: 56
Executed in the general suite: 55
Failures: 0
Skipped: 1 (OutboxRelayPostgresIT, because the first execution had no broker)
```

Session, authentication, user, RBAC, and persistence tests ran successfully against isolated PostgreSQL.

### 4.4 PostgreSQL + RabbitMQ integration

With PostgreSQL and RabbitMQ running together, the previously skipped test was executed directly:

```text
OutboxRelayPostgresIT
Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

The test confirmed the outbox flow persisted in PostgreSQL and published by the relay to RabbitMQ. Combining the general suite with this targeted rerun, all 56 integration tests were verified without failures.

## 5. R4 acceptance matrix

| Criterion | Evidence | Status |
|---|---|:---:|
| Validate signed JWT, issuer, and expiration | R4 gate and security tests | PASS |
| Reject unsupported algorithms or tokens | `alg: none`, tampered-token, and invalid-signature tests | PASS |
| Validate session existence and ownership | PostgreSQL integration tests | PASS |
| Reject revoked or expired sessions | Revocation and expiration tests | PASS |
| Preserve `VIEW`/`MANAGE` RBAC authorization | R4 gate | PASS |
| Publish outbox events through a real broker | `OutboxRelayPostgresIT` | PASS |
| Apply the required IAM schema | 37 Liquibase changesets | PASS |

## 6. Defects and limitations

No failures were identified in the executed tests, and no open technical defect blocks R4 validation.

The execution was manual and isolated. It does not by itself represent formal promotion to the QA environment or replace CI execution once the institutional pipeline is available.

## 7. Verdict

**Technical PASS for IAM R4.** The service branch is functional, and its integration with PostgreSQL and RabbitMQ was verified using real isolated infrastructure. The next step is formal review and promotion to the corresponding QA environment.

## References

- [ADR-018 — IAM R4 Session Revocation](../05-architecture/decisions/records/ADR-018-iam-session-revocation-r4.md)
- [IAM Service decisions](../09-microservices/services/01-iam-service/decisions.md)
- [IAM Service data model](../09-microservices/services/01-iam-service/data-model.md)
- [Testing strategy](./testing-strategy.md)

## 8. QA approval decision

### Decision: APPROVED

After reviewing the QA evidence produced on 2026-10-23, the IAM R4 delivery is considered **technically valid and ready for the next formal promotion step**.

#### Rationale

1. **Complete automated coverage**

   - Maven `verify` completed successfully.
   - `iam-core`: 96/96 passed; `iam-adapters`: 90/90 passed; `iam-api`: 3/3 passed.
   - R4 security gate: **20/20** required tests passed without failures or omissions, covering invalid JWTs, `alg: none`, tampered/expired tokens, missing/revoked/foreign sessions, and `VIEW`/`MANAGE` RBAC controls.

2. **Real integration coverage**

   - Isolated PostgreSQL 16 and RabbitMQ 3.13-management.
   - Liquibase applied **37 changesets** from `iam-db/develop`.
   - All 56 integration tests were verified, including `OutboxRelayPostgresIT` with a real broker.
   - No failures were identified.

3. **Database and documentation**

   - The `session` schema, token records, revocation states, expiration rules, and related indexes are present in `iam-db/develop`.
   - ADR-018 and the related IAM documentation references are present in the documentation branch. ADR-018 is the post-rebase identifier for the IAM session-revocation decision.

4. **Validation scope**

   QA explicitly records that this execution **does not constitute formal promotion to the institutional QA environment**. This is accepted: the architectural approval covers the **technical quality of the delivery** — code, tests, real isolated integration, and documented contract — not deployment to a shared environment.

#### Operational conditions — not blocking technical approval

- Preserve the isolated PostgreSQL/RabbitMQ execution as QA evidence.
- Follow the normal environment workflow for formal promotion to institutional QA.
- No pending design changes or open functional debt were identified within the reviewed R4 scope.

**Status: APPROVED** for technical R4 closure in the open pull requests.
