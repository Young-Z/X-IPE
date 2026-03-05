# General Implementation Tool Skill - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Go/Gin API Implementation

**Context:**
- tech_stack entry: "Go/Gin"
- No x-ipe-tool-implementation-go exists → falls back to general
- 3 @backend AAA scenarios received from orchestrator

### Execution Flow

```
1. Identify Language/Framework:
   - source_code_path: src/api/
   - Found: go.mod with "github.com/gin-gonic/gin"
   - Identified: Go with Gin web framework

2. Research Best Practices:
   - Go testing: standard "testing" package + testify for assertions
   - Gin patterns: handler functions, middleware, JSON binding
   - Linting: golangci-lint
   - Project structure: cmd/, internal/, pkg/ convention

3. Learn Existing Code:
   - Existing handlers use gin.Context pattern
   - JSON responses use c.JSON()
   - Error handling follows middleware pattern

4. Implement Code:
   - Created: src/api/handlers/project_handler.go
   - Followed existing gin.Context pattern

5. Write Tests:
   @backend Test Scenario: "Create project via API"
   → func TestCreateProject(t *testing.T) {
       // Arrange
       router := setupTestRouter()
       // Act
       w := httptest.NewRecorder()
       req, _ := http.NewRequest("POST", "/api/projects", body)
       router.ServeHTTP(w, req)
       // Assert
       assert.Equal(t, 201, w.Code)
     }

6. Run Tests: 3/3 pass ✓
7. Run Lint: golangci-lint run → pass ✓
```

### Output

```yaml
operation_output:
  success: true
  result:
    implementation_files:
      - "src/api/handlers/project_handler.go"
    test_files:
      - "src/api/handlers/project_handler_test.go"
    test_results:
      - scenario: "Create project via API"
        assert_clause: "Response status is 201"
        status: "pass"
      - scenario: "Create project via API"
        assert_clause: "Response body contains project ID"
        status: "pass"
      - scenario: "Reject invalid project name"
        assert_clause: "Response status is 400"
        status: "pass"
    lint_status: "pass"
    stack_identified: "Go/Gin"
  errors: []
```

---

## Example 2: Rust/Actix-Web Implementation

**Context:**
- tech_stack entry: "Rust/Actix"
- No matching tool skill → general fallback
- 2 @backend scenarios

### Execution Flow

```
1. Identify: Cargo.toml with actix-web dependency → Rust/Actix-Web

2. Research:
   - Testing: #[actix_web::test] macro
   - Patterns: extractors, responders, app state
   - Linting: cargo clippy

3. Learn: Follow existing module structure in src/

4. Implement: src/handlers/project.rs

5. Write Tests: 2 test functions mapped to scenarios

6. Run: cargo test → 2/2 pass
7. Lint: cargo clippy → pass
```

---

## Example 3: Stack Unidentifiable

**Context:**
- source_code_path is empty
- AAA scenarios don't hint at technology

### Execution Flow

```
1. Identify:
   - No files in source_code_path
   - No package files found
   - AAA scenarios describe generic CRUD operations

2. ERROR: STACK_UNIDENTIFIABLE
   - Cannot determine language
   - Signal orchestrator: "Unable to identify tech stack from source path or scenarios"
   - Orchestrator asks human for explicit tech_stack hint

3. Human provides: "Use Python/FastAPI"
4. Resume with explicit stack → research FastAPI patterns → implement
```
