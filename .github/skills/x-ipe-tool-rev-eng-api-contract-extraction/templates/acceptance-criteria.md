# API Contract Extraction — Acceptance Criteria

> Validation rules for Section 3 (API Contract Extraction) used by `validate` operation.
> `[REQ]` = Required — must pass for section validation.
> `[OPT]` = Optional — contributes to quality score but not required for validation.

---

### Section 3: API Contract Extraction

**Required Criteria:**

- [ ] `[REQ]` API inventory table present with endpoint count per group
- [ ] `[REQ]` Each API documents parameters with types
- [ ] `[REQ]` Each API documents return type / response schema
- [ ] `[REQ]` APIs grouped by module or service boundary
- [ ] `[REQ]` Each API cites implementing file:line

**Optional Criteria:**

- [ ] `[OPT]` Error responses / exceptions documented
- [ ] `[OPT]` API versioning patterns noted

---

### Per-Subsection Criteria

#### 3.1 Internal APIs — Module-to-Module Interfaces

- [ ] `[REQ]` Public function/method signatures crossing module boundaries listed
- [ ] `[REQ]` Each function documents: name, parameters with types, return type
- [ ] `[REQ]` Functions grouped by source module
- [ ] `[REQ]` Each function cites file:line
- [ ] `[OPT]` Calling modules identified (who calls this API)

#### 3.2 External HTTP APIs — REST Endpoints

- [ ] `[REQ]` HTTP endpoints listed with method, path, and handler
- [ ] `[REQ]` Request parameters documented (path params, query params, body schema)
- [ ] `[REQ]` Response schema documented (success and error responses)
- [ ] `[REQ]` Each endpoint cites handler file:line
- [ ] `[OPT]` Authentication/authorization requirements noted
- [ ] `[OPT]` Middleware chain documented per endpoint
- [ ] `[OPT]` API versioning pattern identified

#### 3.3 CLI Commands

- [ ] `[REQ]` Commands listed with name, arguments, and flags (if CLI exists)
- [ ] `[REQ]` Each command cites handler file:line
- [ ] `[OPT]` Subcommand hierarchy documented
- [ ] `[OPT]` Help text or description included

#### 3.4 WebSocket/RPC APIs

- [ ] `[REQ]` Event/method names listed with schemas (if WebSocket/RPC exists)
- [ ] `[REQ]` Request and response message schemas documented
- [ ] `[REQ]` Each handler cites file:line
- [ ] `[OPT]` Connection lifecycle documented

#### 3.5 Plugin/Extension APIs

- [ ] `[REQ]` Plugin interfaces listed (if plugin system exists)
- [ ] `[REQ]` Required methods/hooks documented
- [ ] `[REQ]` Each interface cites file:line
- [ ] `[OPT]` Plugin lifecycle documented

#### 3.6 Schema Documentation

- [ ] `[OPT]` Request/response type definitions collected
- [ ] `[OPT]` Validation rules documented (required fields, constraints)
- [ ] `[OPT]` Shared types / common schemas identified
