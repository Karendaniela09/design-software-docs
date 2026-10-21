# QA Security Audit & OWASP ASVS Level 1 Verification — scheduling-service

> Evaluation Scope: `design-software-scheduling-service`  
> Author: Daniel Salazar Vargas (CC 1075790810) — ADSO 3145555  
> Date: 2026-10-18  
> Reference: Improvement Plan (Acta No. 02 - 2026, Criteria 11.b, 11.c, 11.d)

---

## 1. Executive Summary

This QA report certifies that `scheduling-service` fulfills the security hardening criteria mandated by the SENA Improvement Plan (Acta No. 02 - 2026). The assessment validates:
1. An automated negative integration test suite consisting of **17 test cases** executing against a real Spring Security filter chain (`SecurityFilterChain`).
2. Complete verification against the **OWASP Application Security Verification Standard (ASVS v4.0.3) Level 1** baseline.
3. Verification of all remediated vulnerabilities documented in the service security model.

---

## 2. Automated Negative Test Suite Execution (`SecurityNegativeAuthIT`)

The negative integration test suite is located in:  
`schedules-api/src/test/java/co/sena/scheduling/api/SecurityNegativeAuthIT.java`

Execution command:
```bash
mvn test -Dtest=SecurityNegativeAuthIT -Dsurefire.failIfNoSpecifiedTests=false
```

### Test Case Verification Matrix

| # | Test Method Name | Acta 02 Mandated Requirement | Attack Vector Description | Expected Status | Result |
|---|---|---|---|:---:|:---:|
| 1 | `missingAuthorizationHeaderIs401` | Anonymous request | Request missing `Authorization` header | **401 Unauthorized** | PASS |
| 2 | `garbageTokenIs401` | Corrupted token | Malformed non-JWT bearer string | **401 Unauthorized** | PASS |
| 3 | `expiredTokenIs401` | **Expired token** | Valid RS256 token with past `exp` claim | **401 Unauthorized** | PASS |
| 4 | `tokenSignedWithWrongKeyIs401` | **Invalid signature** | Token signed by untrusted attacker RSA key pair | **401 Unauthorized** | PASS |
| 5 | `algNoneTokenIs401` | **Algorithm none** | Unsigned token header `{"alg":"none"}` | **401 Unauthorized** | PASS |
| 6 | `tokenWithForeignIssuerIs401` | Untrusted issuer | Token with foreign `iss` claim | **401 Unauthorized** | PASS |
| 7 | `tamperedPayloadIs401` | Tampered payload | Modified payload claims after signature generation | **401 Unauthorized** | PASS |
| 8 | `validTokenWithoutFeaturesIs403` | Missing features | Valid JWT without scheduling authorities | **403 Forbidden** | PASS |
| 9 | `viewerAttemptingEditActionIs403` | Action escalation | Read-only viewer invoking schedule modification | **403 Forbidden** | PASS |
| 10 | `conflictViewerListingTimeSlotsIs403` | Capability isolation | User with conflict authority querying timeslots | **403 Forbidden** | PASS |
| 11 | `publishWithoutPublishFeatureIs403` | Feature isolation | Editor invoking publication without `SCH_PUBLISH` | **403 Forbidden** | PASS |
| 12 | `deleteScheduleWithoutDeleteFeatureIs403`| Feature isolation | Editor invoking deletion without `SCH_DELETE_DRAFT` | **403 Forbidden** | PASS |
| 13 | `resolveConflictWithoutResolveFeatureIs403`| Feature isolation | Editor resolving conflicts without resolve feature | **403 Forbidden** | PASS |
| 14 | `accessingForeignScheduleByIdIs404NotData`| **Foreign resource by ID (IDOR)** | Requesting schedule ID from foreign training center | **404 Not Found** | PASS |
| 15 | `unknownScopeFailsClosed403` | Fail-closed scope | Token with unrecognized `scope_type` claim | **403 Forbidden** | PASS |
| 16 | `forgedRoleEscalationDiesAtSignature401` | **Role escalation** | Attacker forging `ADMIN` role with rogue key | **401 Unauthorized** | PASS |
| 17 | `trainingCenterScopeWithoutCenterClaimIs403`| **Foreign center/ficha scope** | Center scope token missing `training_center_id` | **403 Forbidden** | PASS |

### Test Execution Output Summary
```text
[INFO] Tests run: 17, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 8.224 s -- in co.sena.scheduling.api.SecurityNegativeAuthIT
[INFO] 
[INFO] Results:
[INFO] Tests run: 17, Failures: 0, Errors: 0, Skipped: 0
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] Total time: 18.097 s
```

---

## 3. OWASP ASVS v4.0.3 Level 1 Verification Checklist

The service was audited against the applicable Level 1 requirements of the OWASP Application Security Verification Standard:

### V1: Architecture, Design and Threat Modeling
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V1.1.1 | 1.1.1 | Secure software development lifecycle is followed | **COMPLIANT** | Git Flow with CI gates and PR templates. |
| V1.1.2 | 1.1.2 | Security threat model exists for all application components | **COMPLIANT** | STRIDE model documented in `09-microservices/.../security.md`. |
| V1.4.1 | 1.4.1 | Separation of components into distinct trust zones | **COMPLIANT** | Traefik gateway isolates internal Docker bridge network (`ds-develop`). |
| V1.4.4 | 1.4.4 | Principle of least privilege enforced across subsystems | **COMPLIANT** | PostgreSQL role `design_software_app` restricted to `scheduling_writer`. |

### V2: Authentication
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V2.1.1 | 2.1.1 | Verify that user-supplied passwords are not accepted by API | **COMPLIANT** | Authentication delegated to `iam-service`; scheduling receives only JWTs. |
| V2.7.1 | 2.7.1 | Token verification using cryptographically secure algorithms | **COMPLIANT** | Mandatory RS256 signature verification via Nimbus and IAM JWKS. |
| V2.7.2 | 2.7.2 | Reject tokens with weak or disabled cryptographic schemes | **COMPLIANT** | Tokens with `alg: none` or symmetric HS256 rejected with HTTP 401. |
| V2.7.3 | 2.7.3 | Reject expired tokens | **COMPLIANT** | Built-in Spring Security `JwtTimestampValidator` validates `exp` claim. |

### V3: Session Management
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V3.1.1 | 3.1.1 | Stateless session architecture without server memory storage | **COMPLIANT** | `SessionCreationPolicy.STATELESS` configured in Spring Security. |
| V3.4.1 | 3.4.1 | Session termination upon token expiration | **COMPLIANT** | Short-lived tokens verified on every request without session stickiness. |

### V4: Access Control
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V4.1.1 | 4.1.1 | Principle of least privilege enforced on every endpoint | **COMPLIANT** | Granular `@PreAuthorize("hasAuthority('SCH_*')")` on all operations. |
| V4.1.2 | 4.1.2 | Prevent Horizontal and Vertical Privilege Escalation | **COMPLIANT** | Validated via `viewerAttemptingEditActionIs403` and related tests. |
| V4.1.3 | 4.1.3 | Access control enforcement occurs at trusted server side | **COMPLIANT** | Controller layer evaluates authorities; client UI checks are purely visual. |
| V4.1.5 | 4.1.5 | Insecure Direct Object Reference (IDOR) prevention | **COMPLIANT** | Foreign schedule lookups return HTTP 404 rather than leaking data. |
| V4.2.1 | 4.2.1 | Fail-closed access control when authorization decisions fail | **COMPLIANT** | Unknown or ambiguous scopes default to HTTP 403 rejection. |

### V5: Validation, Sanitization and Encoding
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V5.1.1 | 5.1.1 | Strict input validation against schema contracts | **COMPLIANT** | Contract-first OpenAPI generator and Jakarta `@Valid` annotations. |
| V5.1.3 | 5.1.3 | Strongly-typed parameter binding preventing injection | **COMPLIANT** | Hibernate parameterized queries eliminate SQL injection vectors. |

### V8: Cryptography
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V8.1.1 | 8.1.1 | Cryptographic algorithms use approved standards | **COMPLIANT** | RSA 2048-bit with SHA-256 (RS256) used for all token signatures. |
| V8.2.1 | 8.2.1 | Secrets and private keys are not hardcoded | **COMPLIANT** | Public keys dynamically retrieved from JWKS; no private keys in service. |

### V10: Malicious Code and Error Handling
| Requirement | ASVS Code | Description | Compliance Status | Evidence / Implementation |
|---|:---:|---|:---:|---|
| V10.2.1 | 10.2.1 | Exception handling does not expose sensitive internals | **COMPLIANT** | `GlobalExceptionHandler` converts technical errors to uniform envelopes. |
| V10.3.1 | 10.3.1 | Security events log user identity and correlation trace ID | **COMPLIANT** | Authenticated JWT `sub` and OpenTelemetry `trace_id` recorded on logs. |

---

## 4. Conclusion & Sign-Off

The `design-software-scheduling-service` has been thoroughly verified against all security requirements of the Improvement Plan (Acta No. 02 - 2026). The service exhibits resilient defense-in-depth characteristics, passes 17 automated negative integration tests in CI without regression, and satisfies all applicable OWASP ASVS Level 1 requirements.

---

## 5. Related References

- Architectural Decision: [ADR-015: Scheduling Service Security Hardening and Cryptographic JWT Validation](../05-architecture/decisions/records/ADR-015-scheduling-security-hardening.md)
- Microservice Security Model: [09-microservices/services/05-scheduling-service/security.md](../09-microservices/services/05-scheduling-service/security.md)
- Operations Runbook: [09-microservices/services/05-scheduling-service/runbook.md](../09-microservices/services/05-scheduling-service/runbook.md)
