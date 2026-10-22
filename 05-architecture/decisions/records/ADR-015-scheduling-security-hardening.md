# ADR-015: Scheduling Service Security Hardening and Cryptographic JWT Validation

**Status:** ACCEPTED  
**Date:** 2026-10-18  
**Authors:** Daniel Salazar Vargas  
**Teams involved:** Architecture, Scheduling, IAM Security  

---

## Context

The `scheduling-service` manages academic calendars, instructor session allocations, and learning environment scheduling within the SENA educational framework. In the distributed microservice architecture of `design-software`, the service is exposed via Traefik edge reverse proxy and authenticates client requests using JSON Web Tokens (JWT) issued by the central Identity and Access Management service (`iam-service`).

Prior to the engineering hardening mandated by Improvement Plan (Acta No. 02 - 2026, Individual Challenge R4):
1. The service lacked an automated negative test suite verifying defense against forged, tampered, expired, or unsigned tokens (`alg: none`).
2. Endpoint authorization did not enforce fine-grained, claim-based permissions (`SCH_*` features) or multi-tenant scope isolation (training centers and instructor ownership).
3. Critical endpoints exposed potential Insecure Direct Object Reference (IDOR) vectors, leaking private resource identifiers or confirming entity existence through descriptive error statuses.
4. Publication endpoints allowed non-contractual author parameter injection (`?publishedBy`), creating identity spoofing vulnerabilities in audit logs.

A comprehensive defense-in-depth architecture was required to enforce asymmetric cryptographic verification, fail-closed access control, and complete mitigation of STRIDE and OWASP ASVS Level 1 vulnerabilities.

---

## Decision

We decide to implement an **asymmetric cryptographic JWT validation layer with fine-grained feature-based authorization (RBAC) and fail-closed scope enforcement** in `scheduling-service`, validated by a suite of 19 automated negative integration tests running in CI (`SecurityNegativeAuthIT`).

Specifically:

1. **Strict Asymmetric Cryptographic Verification (RS256):**
   - In runtime and deployed environments, the service enforces RS256 signature verification using public keys fetched from IAM's JSON Web Key Set (`JWKS`, `kid=iam-rsa-1`).
   - In the automated CI integration suite (`SecurityNegativeAuthIT`), verification is executed hermetically using Spring Security's real `SecurityFilterChain` and `NimbusJwtDecoder` backed by an ephemeral 2048-bit RSA key pair, validating exact RS256 cryptography and issuer without an external IAM service dependency in CI.
   - Unsigned tokens (`alg: none`) and symmetric key forgery attempts are rejected at the security filter layer with `401 Unauthorized`.
   - The token issuer (`iss: sena-iam-service`) and strict time-to-live (`exp`) are validated before any controller execution.

2. **Fine-Grained Feature-Based Authorization (`SCH_*`):**
   - Access control is decoupled from broad roles (`ADMIN`, `INSTRUCTOR`) and mapped directly to granular feature authorities in the JWT payload:
     - Schedule querying: `SCH_VIEW_ALL` or `SCH_VIEW_OWN`.
     - Creation and editing: `SCH_CREATE`, `SCH_EDIT`.
     - Schedule publication and archiving: `SCH_PUBLISH`, `SCH_ARCHIVE`.
     - Conflict resolution: `SCH_CONFLICT_RESOLVE`.
     - Draft deletion: `SCH_DELETE_DRAFT`.
   - Every sensitive controller endpoint enforces `@PreAuthorize("hasAuthority('SCH_*')")`. Requests lacking required features are rejected with `403 Forbidden`.

3. **Auditing Integrity and Spoofing Prevention:**
   - In `ScheduleController.java`, the `POST /api/v1/schedules/{id}/publish` endpoint removes the non-contractual `?publishedBy` query parameter.
   - The publishing actor identifier is extracted exclusively from the validated JWT `sub` claim (`currentUserId()`), preventing publisher impersonation.

4. **IDOR Mitigation and Fail-Closed Scope Policy:**
   - When a user queries a schedule by identifier (`GET /api/v1/schedules/{id}`) that belongs to a foreign training center or instructor, the service returns `404 Not Found` rather than confirming resource existence with `403 Forbidden`.
   - When token claims indicate an unsupported, foreign, or malformed scope, the security resolver executes a **fail-closed** policy, denying access with `403 Forbidden`.

5. **Database Immutability Invariants:**
   - Published schedules are protected by database triggers (`trg_schedule_published_immutability`) prohibiting column alterations once transitioned to `PUBLISHED` or `ARCHIVED`.

---

## Consequences

### Positive

- **Elimination of Token Forgery:** Malformed, expired, foreign-issuer, and `alg: none` tokens are halted deterministically before reaching business logic.
- **Auditing Non-Repudiation:** Audit metadata (`created_by`, `published_by`, `updated_by`) is strictly tied to verified JWT subjects, correlated with distributed `trace_id`.
- **Information Leakage Prevention:** Foreign resource scanning (IDOR) is thwarted via `404 Not Found` masking.
- **CI Regression Shield:** 19 negative integration tests guarantee automated verification on every Pull Request to `develop`.

### Negative / Trade-offs

- **Testing Setup Overhead:** Integration tests require mock RSA key pair generation and dynamic Spring Security configuration to validate live cryptographic filters without external IAM dependencies.
- **Scope Coupling:** Scope validation requires extracting custom claims (`training_center_id`, `actor_id`) from incoming tokens, requiring synchronization with IAM token contract schemas.

### Risks

- Key rotation in IAM requires caching and cache-invalidation policies on `scheduling-service` JWKS clients to prevent valid tokens from being rejected during key rollover.

---

## Considered Alternatives

| Alternative | Reason for Rejection |
|---|---|
| **Symmetric HMAC-SHA256 (HS256) Shared Secret** | Requires distributing shared secret keys across microservices, increasing key compromise risk compared to asymmetric public key distribution (RS256 via JWKS). |
| **Role-Only Authorization (`hasRole('ADMIN')`)** | Too coarse; does not allow granular delegation (e.g. conflict viewers who can inspect sessions but cannot publish schedules). |
| **Permissive Scope Fallback (Fail-Open)** | Incurred high security vulnerability risk by defaulting to global access when unrecognized scopes were presented in legacy tokens. |
| **Return 403 on IDOR Queries** | Confirms to an attacker that the targeted schedule ID exists in the database, allowing brute-force resource enumeration. |

---

## References

- [05-architecture/security-threat-model.md](../../security-threat-model.md)
- [09-microservices/services/05-scheduling-service/security.md](../../09-microservices/services/05-scheduling-service/security.md)
- [11-quality/qa-report-r4-security-scheduling.md](../../11-quality/qa-report-r4-security-scheduling.md)
- OWASP Application Security Verification Standard (ASVS v4.0.3) Level 1
