# Backend Architecture, API & Web Security Standards

This document establishes the architecture, data validation, database interaction, and web security standards for backend development within `Yzentic-setup`.

---

## Overview

Backend services and API routes built with **Node/Bun**, **Next.js Route Handlers**, **Express**, and **Prisma/Drizzle** must be type-safe, resilient, and secure by design. These standards enforce strict schema-first validation, predictable error contracts, defensive database operations, and non-negotiable defense-in-depth security.

---

## Core Standards

### 1. Schema-First Validation (Zod)
- **Mandatory Validation Boundaries:** Every incoming request boundary—request body, query parameters, route parameters, and header tokens—must be validated using a strict Zod schema before executing any business logic.
- **Strict TypeScript Inference:** Derive application types directly from Zod schemas using `z.infer<typeof Schema>` rather than maintaining duplicate interface definitions.
- **Fail Fast:** If validation fails, immediately return an RFC-compliant `422 Unprocessable Entity` or `400 Bad Request` with structured error details. Never pass untrusted payloads into downstream services.

### 2. Standardized API Envelopes & HTTP Status Codes
- **Uniform Error Envelopes:** Error responses must adhere to a standardized JSON envelope following RFC 7807 problem details:
  ```json
  {
    "error": {
      "code": "VALIDATION_FAILED",
      "message": "Invalid request parameters",
      "details": [
        { "field": "email", "issue": "Invalid email address format" }
      ]
    }
  }
  ```
- **Semantic HTTP Status Codes:**
  - `200 OK`: Successful read or update with body.
  - `201 Created`: Resource successfully created.
  - `204 No Content`: Successful mutation with no response body.
  - `400 Bad Request`: Malformed syntax or missing parameters.
  - `401 Unauthorized`: Missing or invalid authentication token/session.
  - `403 Forbidden`: Authenticated, but lacking permission/role for this resource.
  - `404 Not Found`: Target resource does not exist.
  - `409 Conflict`: Resource state conflict (e.g., duplicate unique constraint).
  - `422 Unprocessable Entity`: Semantic/schema validation failure.
  - `429 Too Many Requests`: Rate limit threshold exceeded.
  - `500 Internal Server Error`: Unexpected internal server exception (do NOT leak stack traces to client).

### 3. Database Operations & ORM Best Practices (Prisma / Drizzle)
- **Transactional Integrity:** Any mutation spanning multiple records or tables MUST be wrapped in an interactive database transaction (`prisma.$transaction(...)` or `db.transaction(...)`).
- **Cursor-Based Pagination:** For collections exceeding 50 items, use cursor-based pagination instead of offset pagination (`OFFSET / LIMIT`) to avoid severe performance degradation on large datasets.
- **Explicit Indexing:** Ensure every foreign key column, lookup field (e.g., `slug`, `email`), and sort column has an explicit database index.
- **Idempotency Keys:** For payment, order placement, or external webhook handling, mandate an `Idempotency-Key` header to safely handle client network retries without duplicate operations.

### 4. Defense-in-Depth Web Security
- **Cookie-Based Session Storage:** Store authentication tokens in `HttpOnly; SameSite=Lax; Secure` cookies. NEVER store session tokens, JWTs, or sensitive credentials in client `localStorage` or `sessionStorage` (which are vulnerable to XSS).
- **CSRF Mitigation:** Require anti-CSRF token verification or SameSite strict origin checks on all state-mutating requests (`POST`, `PUT`, `PATCH`, `DELETE`).
- **Secure Response Headers:** Enforce defensive HTTP headers across all responses:
  - `Content-Security-Policy (CSP)`
  - `Strict-Transport-Security (HSTS)`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
- **Zero Raw SQL / Injection Defense:** Always use parameterized ORM queries. Never concatenate raw strings into SQL queries.
- **Secret Hygiene:** Never commit credentials or API keys. Always manage secrets via [`varlock`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/varlock/SKILL.md) and review changes against [`owasp-security`](file:///mnt/LubaDub/Projects/Web/dual-yzentic-setup/dual-yzentic-setup/.agents/skills/owasp-security/SKILL.md).

---

## Dos and Don'ts

| Do | Don't |
| :--- | :--- |
| **Do** validate every input with Zod schemas before running business logic. | **Don't** accept raw untyped `req.body` or use `any` casting. |
| **Do** store session credentials in `HttpOnly; SameSite=Lax; Secure` cookies. | **Don't** store authentication tokens in `localStorage` where XSS can steal them. |
| **Do** wrap multi-record database operations in atomic transactions. | **Don't** run sequential database mutations without transaction safety. |
| **Do** return semantic HTTP status codes and uniform JSON error envelopes. | **Don't** return `200 OK` with `{ success: false, error: "..." }` payloads. |
| **Do** use cursor-based pagination for unbounded data lists. | **Don't** use large `OFFSET` queries that scan millions of database rows. |
