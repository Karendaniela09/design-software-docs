# QA Security Audit & OWASP ASVS Level 1 Verification — actors-service

> Evaluation Scope: `design-software-actors-service` (Commit: `7cc9ec1`, PR #27)  
> Documentation Scope: `design-software-docs` (Branch: `docs/act-r4-security-hardening`, PR #342)  
> Author: Laura Vanessa Pérez Perdomo (CC 1075228306) — ADSO 3145555  
> Date: 2026-10-21 (Updated: 2026-10-23)  
> Status: **CLOSED / 100% COMPLIANT**  
> Reference: Improvement Plan (Acta No. 02 - 2026, Criteria 11.b, 11.c, 11.d) — QA R4 Security Audit  

---

## 1. Executive Summary

This QA report certifies that `actors-service` satisfies all security hardening and quality assurance criteria mandated by the SENA Improvement Plan (Acta No. 02 - 2026, Individual Challenge R4).

The assessment validates:
1. An automated negative integration test suite comprising **16 test cases** executing against Spring Security's real filter chain (`SecurityFilterChain`), Nimbus JWT cryptographic decoder, bean validation, and error handlers.
2. An additional automated suite of cryptographic unit tests (`NimbusJwtCryptographicTest.java`), IDOR use case tests (`LearnerAuthTest.java`), and real PostgreSQL database SQL injection tests (`LearnerPersistenceSqlInjectionIT.java`).
3. Explicit negative test coverage for **multi-tenant training center scopes**, **ficha scopes**, **IDOR identity boundaries**, **internal mTLS client certificates**, and **rate limiting**.
4. 100% compliance against the applicable baseline of the **OWASP Application Security Verification Standard (ASVS v4.0.3) Level 1**.
5. Complete resolution and closure of security findings with zero test regressions.

---

## 2. Automated Negative Test Suite Execution (`SecurityNegativeTests`)

The negative integration test suite is located in:  
`actors-adapters/src/test/java/co/sena/actors/adapter/in/rest/SecurityNegativeTests.java`

Execution command:
```bash
mvn test -Dtest=SecurityNegativeTests -Dsurefire.failIfNoSpecifiedTests=false
```

### Test Case Verification Matrix

| # | Test Method Name | Acta 02 Mandated Requirement | Attack Vector Description | Expected Status | Result |
|---|---|---|---|:---:|:---:|
| 1 | `test01_expiredToken_returns401TokenExpired` | **Expired token** | Valid RS256 token with past `exp` claim | **401 Unauthorized** (`TOKEN_EXPIRED`) | PASS |
| 2 | `test02_invalidSignature_returns401TokenInvalid` | **Invalid signature** | Token signed with untrusted private key | **401 Unauthorized** (`TOKEN_INVALID`) | PASS |
| 3 | `test03_algorithmNone_returns401TokenInvalid` | **Algorithm none** | Unsigned token with header `{"alg":"none"}` | **401 Unauthorized** (`TOKEN_INVALID`) | PASS |
| 4 | `test04_missingAuthorizationHeader_returns401MissingToken` | Anonymous request | Request missing `Authorization` header | **401 Unauthorized** (`MISSING_TOKEN`) | PASS |
| 5 | `test05_malformedHeader_returns401TokenInvalid` | Corrupted token | Malformed non-JWT bearer string | **401 Unauthorized** (`TOKEN_INVALID`) | PASS |
| 6 | `test06_differentTrainingCenterScope_returns403` | **Cross-center scope** | User with center scope querying foreign center | **403 Forbidden** (`INSUFFICIENT_PERMISSIONS`) | PASS |
| 7 | `test06b_sameTrainingCenterScope_isAllowed` | Authorized scope | User with center scope querying their own center | **200 OK** | PASS |
| 8 | `test07_differentFichaScope_returns403` | **Cross-ficha scope** | User with ficha scope querying foreign ficha | **403 Forbidden** (`INSUFFICIENT_PERMISSIONS`) | PASS |
| 9 | `test08_roleEscalation_apprenticeAttemptingInstructorCreation_returns403` | **Role escalation** | Apprentice invoking instructor registration | **403 Forbidden** (`INSUFFICIENT_PERMISSIONS`) | PASS |
| 10 | `test09_idorRead_accessDeniedWithoutLearnerViewAuthority_returns403` | **IDOR Read** | Learner reading foreign learner record | **403 Forbidden** (`INSUFFICIENT_PERMISSIONS`) | PASS |
| 11 | `test10_idorUpdate_modificationDeniedWithoutManageAuthority_returns403` | **IDOR Update** | Learner modifying foreign learner record | **403 Forbidden** (`INSUFFICIENT_PERMISSIONS`) | PASS |
| 12 | `test11_sqlInjectionInQueryParams_sanitizedWithout500` | **SQL Injection** | Filtering query containing `' OR '1'='1` | **200 OK** (Sanitized, No 500) | PASS |
| 13 | `test12_xssPayloadInBody_rejectedWith400ValidationError` | **XSS Injection** | Request payload containing `<script>` tags | **400 Bad Request** (`VALIDATION_ERROR`) | PASS |
| 14 | `test13_excessiveRequests_triggersRateLimiting429` | **DoS / Rate Limit** | Request burst exceeding rate quota | **429 Too Many Requests** (`TOO_MANY_REQUESTS`) | PASS |
| 15 | `test14_untrustedMtlsClientCallingInternalLearners_returnsUnauthorized` | **mTLS Perimeter** | Internal sync call without valid client certificate | **401 Unauthorized** (`MTLS_CERTIFICATE_REQUIRED`) | PASS |
| 16 | `test15_internalServerError_doesNotLeakStacktraceOrDatabaseSchema` | **Info Leakage** | Database error masking stack traces and SQL | **500 Internal Error** (`INTERNAL_ERROR`) | PASS |

### Companion Security Test Suites

In addition to `SecurityNegativeTests`, the following dedicated suites run during build verification:
1. **`NimbusJwtCryptographicTest.java`**: Evaluates live RSA 2048-bit key-pair cryptographic verification, token alteration rejection, and `alg: none` defenses.
2. **`LearnerAuthTest.java`**: 6 unit test scenarios validating exact identity equivalence (`learner.id == actor_id`) and fail-closed denial for foreign IDs.
3. **`LearnerPersistenceSqlInjectionIT.java`**: Integration test executing against real PostgreSQL via Testcontainers, validating that parameterized repository queries prevent SQL injection payloads from executing.

---

## 3. Findings Resolution & Closure Log

### QA-ACT-R4-001 — Multi-Tenant Scope Isolation Across Training Centers
- **Severity:** High
- **Status:** **CLOSED (RESOLVED)**
- **Finding:** Endpoint `GET /api/v1/instructors` allowed querying instructors from any training center if `training_center_id` parameter was manipulated.
- **Remediation:** Enforced `@PreAuthorize("@instructorAuth.canView(#trainingCenterId)")` in `InstructorController.java`. Users scoped to a specific center receive HTTP 403 when requesting foreign center records (`test06`), while retaining legitimate access to their assigned center (`test06b`).

### QA-ACT-R4-002 — Insecure Direct Object Reference (IDOR) on Learner Records
- **Severity:** High
- **Status:** **CLOSED (RESOLVED)**
- **Finding:** Endpoints `GET /api/v1/learners/{id}` and `PUT /api/v1/learners/{id}` did not verify actor ownership for callers with `OWN_PROFILE` authority.
- **Remediation:** Enforced `@PreAuthorize("@learnerAuth.canViewLearner(#id)")` and `@PreAuthorize("@learnerAuth.canManageLearner(#id)")`. The evaluator validates that the resource ID matches the authenticated learner's identity (`test09`, `test10`).

### QA-ACT-R4-003 — Internal Perimeter Protection on Synchronization Routes
- **Severity:** High
- **Status:** **CLOSED (RESOLVED)**
- **Finding:** Route `/internal/learners/by-user/{userId}/active-ficha` was accessible without cryptographic service identity verification.
- **Remediation:** Implemented `InternalMtlsAuthenticationFilter.java` enforcing valid X.509 client certificates with `CN=iam-service`. Calls without certificates or with untrusted subjects are halted with HTTP 401 (`test14`).

---

## 4. OWASP ASVS v4.0.3 Level 1 Verification Checklist

The service was audited against the applicable Level 1 requirements of the OWASP Application Security Verification Standard:

### V1: Architecture, Design and Threat Modeling
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V1.1.1 | 1.1.1 | Secure software development lifecycle is followed | **COMPLIANT** | Git Flow with CI gates and Conventional Commits. |
| V1.1.2 | 1.1.2 | Security threat model exists for all application components | **COMPLIANT** | STRIDE threat model documented in `09-microservices/.../security.md`. |
| V1.4.1 | 1.4.1 | Separation of components into distinct trust zones | **COMPLIANT** | Traefik edge reverse proxy, isolated internal Docker network, and dedicated database schemas. |
| V1.4.4 | 1.4.4 | Principle of least privilege enforced across subsystems | **COMPLIANT** | Granular Spring Security method authorization (`@PreAuthorize`) and dedicated DB roles. |

### V2: Authentication
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V2.1.1 | 2.1.1 | Verify that user-supplied passwords are not accepted by API | **COMPLIANT** | Authentication delegated to `iam-service`; actors receives only Bearer JWTs or mTLS certs. |
| V2.7.1 | 2.7.1 | Token verification using cryptographically secure algorithms | **COMPLIANT** | Mandatory RS256 signature verification via Nimbus and public keys from JWKS. |
| V2.7.2 | 2.7.2 | Reject tokens with weak or disabled cryptographic schemes | **COMPLIANT** | Tokens with `alg: none` rejected with HTTP 401 (`TOKEN_INVALID`). |
| V2.7.3 | 2.7.3 | Reject expired tokens | **COMPLIANT** | Built-in timestamp validation rejects expired tokens with HTTP 401 (`TOKEN_EXPIRED`). |

### V3: Session Management
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V3.1.1 | 3.1.1 | Stateless session architecture without server memory storage | **COMPLIANT** | `SessionCreationPolicy.STATELESS` configured in Spring Security. |
| V3.4.1 | 3.4.1 | Session termination upon token expiration | **COMPLIANT** | Completely stateless; expired tokens are immediately rejected. |

### V4: Access Control
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V4.1.1 | 4.1.1 | Principle of least privilege enforced on every endpoint | **COMPLIANT** | Granular `@PreAuthorize("hasAuthority('ACT_*')")` on all operations. |
| V4.1.2 | 4.1.2 | Prevent Horizontal and Vertical Privilege Escalation | **COMPLIANT** | Validated via apprentice role rejection (`test08`) and multi-tenant training center/ficha scope tests (`test06`, `test07`). |
| V4.1.3 | 4.1.3 | Access control enforcement occurs at trusted server side | **COMPLIANT** | Controllers evaluate GrantedAuthorities on backend; UI checks are purely visual. |
| V4.1.5 | 4.1.5 | Insecure Direct Object Reference (IDOR) prevention | **COMPLIANT** | Learner profile read/update restricted to resource owners via `LearnerAuth` (`test09`, `test10`). |
| V4.2.1 | 4.2.1 | Fail-closed access control when authorization decisions fail | **COMPLIANT** | Unknown, missing, or cross-tenant scopes default to HTTP 403 rejection. |

### V5: Validation, Sanitization and Encoding
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V5.1.1 | 5.1.1 | Strict input validation against schema contracts | **COMPLIANT** | Jakarta `@Valid` annotations and regex constraints (`@Pattern(regexp = "^[^<>]*$")`) reject XSS payloads (`test12`). |
| V5.1.3 | 5.1.3 | Strongly-typed parameter binding preventing injection | **COMPLIANT** | Hibernate parameterized queries eliminate SQL injection vectors (`test11`, `LearnerPersistenceSqlInjectionIT`). |

### V8: Cryptography
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V8.1.1 | 8.1.1 | Cryptographic algorithms use approved standards | **COMPLIANT** | RSA 2048-bit with SHA-256 (RS256) used for token signatures; X.509 certificates for mTLS. |
| V8.2.1 | 8.2.1 | Secrets and private keys are not hardcoded | **COMPLIANT** | Public keys dynamically retrieved from JWKS; zero hardcoded DB/JWT secrets in codebase. |

### V10: Malicious Code and Error Handling
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V10.2.1 | 10.2.1 | Exception handling does not expose sensitive internals | **COMPLIANT** | `GlobalExceptionHandler` converts technical errors to uniform envelopes (`INTERNAL_ERROR`), masking stack traces and SQL schema (`test15`). |
| V10.3.1 | 10.3.1 | Security events log user identity and correlation trace ID | **COMPLIANT** | Authenticated JWT `sub` and OpenTelemetry `trace_id` recorded on logs. |

---

## 5. Conclusion & Sign-Off

The `design-software-actors-service` has been thoroughly verified against all security requirements of the Improvement Plan (Acta No. 02 - 2026). The microservice exhibits resilient defense-in-depth characteristics, passes **16 automated negative integration tests** alongside cryptographic, IDOR, and SQL injection suites, satisfies all applicable OWASP ASVS Level 1 requirements, and completely closes findings **QA-ACT-R4-001**, **QA-ACT-R4-002**, and **QA-ACT-R4-003**.

---

## 6. Related References

- Architectural Decision: [ADR-019: Actors Service Security Hardening, Decentralized OAuth2 RS256, Mutual TLS (mTLS), and Granular Scope-Based Access Control](../05-architecture/decisions/records/ADR-019-actors-security-hardening.md)
- Microservice Security Model: [09-microservices/services/06-actors-service/security.md](../09-microservices/services/06-actors-service/security.md)
- Operations Runbook: [09-microservices/services/06-actors-service/runbook.md](../09-microservices/services/06-actors-service/runbook.md)
- Internal Decisions: [09-microservices/services/06-actors-service/decisions.md](../09-microservices/services/06-actors-service/decisions.md)
