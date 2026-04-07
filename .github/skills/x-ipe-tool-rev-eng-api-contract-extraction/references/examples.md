# Usage Examples — API Contract Extraction

> Examples showing how the orchestrator interacts with this tool skill.

---

## Example 1: Full API Extraction Flow

```yaml
# Step 1: Extract API contracts from codebase
Orchestrator: extract(
  repo_path="/path/to/repo",
  phase1_output=".x-ipe-checkpoint/phase1/",
  phase2_output=".x-ipe-checkpoint/phase2/",
  output_dir=".x-ipe-checkpoint/section-03/"
)
→ {
    success: true,
    extracted_content: ".x-ipe-checkpoint/section-03/",
    # Created files:
    #   index.md (API inventory with counts)
    #   01-internal-apis.md (12 module-boundary functions)
    #   02-external-http-apis.md (8 REST endpoints)
    #   03-cli-commands.md (3 CLI commands)
    #   04-websocket-rpc-apis.md ("None detected")
    #   05-plugin-extension-apis.md ("None detected")
    #   06-schema-documentation.md (request/response types)
  }

# Step 2: Validate extracted contracts
Orchestrator: validate(
  content_path=".x-ipe-checkpoint/section-03/",
  section_id="3-api-contract-extraction"
)
→ {
    passed: true,
    criteria: [
      { id: "REQ-1", status: "pass", feedback: "Inventory table: 23 total APIs" },
      { id: "REQ-2", status: "pass", feedback: "All APIs have typed parameters" },
      { id: "REQ-3", status: "pass", feedback: "All APIs have return types" },
      { id: "REQ-4", status: "pass", feedback: "APIs grouped by 4 modules" },
      { id: "REQ-5", status: "pass", feedback: "All APIs cite file:line" }
    ],
    missing_info: []
  }

# Step 3: Collect and execute API-relevant tests
Orchestrator: collect_tests(
  repo_path="/path/to/repo",
  phase2_output=".x-ipe-checkpoint/phase2/"
)
→ {
    collected_tests: [
      { path: "tests/test_api_users.py", claim: "POST /users endpoint contract" },
      { path: "tests/test_api_auth.py", claim: "POST /auth/login response schema" },
      { path: "tests/test_cli_import.py", claim: "CLI import command arguments" }
    ]
  }

Orchestrator: execute_tests(repo_path="/path/to/repo")
→ {
    tests_run: 3, tests_passed: 2, tests_failed: 1,
    claim_mapping: [
      { test: "test_api_users.py", claim: "POST /users contract", result: "confirmed" },
      { test: "test_api_auth.py", claim: "POST /auth/login schema", result: "confirmed" },
      { test: "test_cli_import.py", claim: "CLI import args", result: "failed — flag --format removed" }
    ]
  }
# Failed test triggers re-verification of CLI command documentation

# Step 4: Package into final output
Orchestrator: package(
  content_path=".x-ipe-checkpoint/section-03/",
  output_dir="output/section-03-api-contracts/"
)
→ { package_path: "output/section-03-api-contracts/" }
```

---

## Example 2: API Inventory Table

```markdown
# API Inventory — Example Output in index.md

| API Group | Type | Endpoint Count | Module | Reference |
|-----------|------|---------------|--------|-----------|
| User Management | Internal | 5 | `src/services/user/` | [01-internal-apis.md](01-internal-apis.md#user-management) |
| Auth Service | Internal | 3 | `src/services/auth/` | [01-internal-apis.md](01-internal-apis.md#auth-service) |
| Repository Layer | Internal | 4 | `src/repositories/` | [01-internal-apis.md](01-internal-apis.md#repository-layer) |
| REST API | External HTTP | 8 | `src/handlers/` | [02-external-http-apis.md](02-external-http-apis.md) |
| CLI | CLI | 3 | `src/cli/` | [03-cli-commands.md](03-cli-commands.md) |

**Total: 23 APIs** (12 internal, 8 HTTP, 3 CLI)
```

---

## Example 3: External HTTP API Documentation

```markdown
# Example entry in 02-external-http-apis.md

### POST /api/v1/users

**Handler:** `src/handlers/users.py:42` → `create_user()`

**Request:**
| Parameter | Location | Type | Required | Description |
|-----------|----------|------|----------|-------------|
| email | body | string | yes | User email address |
| name | body | string | yes | Display name |
| role | body | enum("admin","user") | no | Default: "user" |

**Response (201 Created):**
```json
{
  "id": "string (UUID)",
  "email": "string",
  "name": "string",
  "role": "string",
  "created_at": "string (ISO 8601)"
}
```

**Error Responses:**
| Status | Body | Condition |
|--------|------|-----------|
| 400 | `{"error": "validation_error", "details": [...]}` | Invalid input |
| 409 | `{"error": "conflict", "message": "Email exists"}` | Duplicate email |

**Middleware:** `auth_required`, `validate_body(UserCreateSchema)`
**Versioning:** URL prefix `/api/v1/`
```

---

## Example 4: Internal API Documentation

```markdown
# Example entry in 01-internal-apis.md

### Module: Auth Service (`src/services/auth/`)

#### `authenticate(email: str, password: str) -> AuthResult`
- **File:** `src/services/auth/service.py:28`
- **Parameters:**
  - `email: str` — User email address
  - `password: str` — Plain-text password (hashed internally)
- **Returns:** `AuthResult` — `{ token: str, user: User, expires_at: datetime }`
- **Raises:** `AuthenticationError` if credentials invalid
- **Called by:** `src/handlers/auth.py:15`, `src/handlers/oauth.py:42`

#### `verify_token(token: str) -> User`
- **File:** `src/services/auth/service.py:55`
- **Parameters:**
  - `token: str` — JWT token string
- **Returns:** `User` — Decoded user object
- **Raises:** `TokenExpiredError`, `InvalidTokenError`
- **Called by:** `src/middleware/auth.py:8` (auth middleware)
```

---

## Example 5: Test-Derived Contract Evidence

```yaml
# Phase 2 test knowledge reveals API contracts through assertions
# From Section 8 test analysis:

Test: test_api_users.py:test_create_user
HTTP Call: POST /api/v1/users {"email": "test@example.com", "name": "Test"}
Assertion: response.status_code == 201
Assertion: response.json()["id"] is not None
Assertion: response.json()["email"] == "test@example.com"
→ Contract Evidence:
  - Endpoint exists: POST /api/v1/users
  - Request body: {email, name} required
  - Response: 201 with {id, email} fields

Test: test_api_users.py:test_create_duplicate_user
HTTP Call: POST /api/v1/users {"email": "existing@example.com", ...}
Assertion: response.status_code == 409
→ Contract Evidence:
  - Error response: 409 for duplicate email
```

---

## Example 6: No External APIs Scenario

```yaml
# Library codebase with only internal APIs
Orchestrator: extract(...)
→ {
    # index.md: "15 internal APIs across 3 modules. No external HTTP,
    #            CLI, WebSocket, or plugin APIs detected."
    # 01-internal-apis.md — 15 functions documented
    # 02-external-http-apis.md — "No HTTP endpoints detected"
    # 03-cli-commands.md — "No CLI commands detected"
    # 04-websocket-rpc-apis.md — "None detected"
    # 05-plugin-extension-apis.md — "None detected"
    # 06-schema-documentation.md — type definitions from internal APIs
  }

Orchestrator: validate(...)
→ {
    passed: true,  # REQ criteria met via internal APIs
    criteria: [
      { id: "REQ-1", status: "pass", feedback: "Inventory: 15 internal APIs" },
      { id: "REQ-2", status: "pass", feedback: "All typed parameters" },
      { id: "REQ-3", status: "pass", feedback: "All return types documented" },
      { id: "REQ-4", status: "pass", feedback: "Grouped by 3 modules" },
      { id: "REQ-5", status: "pass", feedback: "All cite file:line" }
    ]
  }
```
