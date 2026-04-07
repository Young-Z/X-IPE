# Examples — Section 4: Dependency Analysis

## Example 1: Extract Dependencies from a Node.js Monorepo

```yaml
invocation:
  skill: x-ipe-tool-rev-eng-dependency-analysis
  operation: extract
  input:
    repo_path: "/workspace/my-app"
    phase1_output: "/workspace/output/phase1"
    phase2_output: "/workspace/output/phase2"
    output_dir: "/workspace/output/section-04"
```

### Expected Output: 01-inter-module-deps.md (excerpt)

```markdown
# Inter-Module Dependencies

## Adjacency List

| Source Module | Target Module | Import Type | File:Line |
|---------------|---------------|-------------|-----------|
| api-gateway | auth-service | direct | src/api-gateway/routes/auth.ts:3 |
| api-gateway | user-service | direct | src/api-gateway/routes/users.ts:5 |
| user-service | db-common | direct | src/user-service/repository.ts:2 |
| auth-service | db-common | direct | src/auth-service/repository.ts:2 |
| auth-service | user-service | direct | src/auth-service/verify.ts:7 |

## Summary
- Total internal modules: 5
- Total dependency edges: 5
- Average fan-out: 1.0
```

### Expected Output: 02-external-library-deps.md (excerpt)

```markdown
# External Library Dependencies

| Library | Declared | Resolved | Type | Purpose |
|---------|----------|----------|------|---------|
| express | ^4.18.0 | 4.18.2 | runtime | HTTP server framework |
| jsonwebtoken | ^9.0.0 | 9.0.2 | runtime | JWT token generation/verification |
| pg | ^8.11.0 | 8.11.3 | runtime | PostgreSQL client |
| typescript | ^5.3.0 | 5.3.3 | dev | TypeScript compiler |
| jest | ^29.7.0 | 29.7.0 | dev | Test framework |
| @types/express | ^4.17.0 | 4.17.21 | dev | TypeScript type definitions for Express |

Source: package-lock.json (resolved), package.json (declared)
```

---

## Example 2: Circular Dependency Detection

### Expected Output: 03-circular-dependencies.md (excerpt)

```markdown
# Circular Dependencies

## Cycle 1: auth-service ↔ user-service (Severity: HIGH)

**Chain:** auth-service → user-service → auth-service

| Edge | Import Statement | File:Line |
|------|------------------|-----------|
| auth-service → user-service | `import { findUser } from '../user-service/find'` | src/auth-service/verify.ts:7 |
| user-service → auth-service | `import { validateToken } from '../auth-service/jwt'` | src/user-service/middleware.ts:3 |

**Impact:** Tight 2-module cycle. Changes to either module risk cascading to the other.
**Suggested resolution:** Extract shared interface to a common module or use dependency inversion.
```

---

## Example 3: Critical Hub Module Analysis

### Expected Output: 04-critical-dependencies.md (excerpt)

```markdown
# Critical Dependencies

## Hub Modules (Fan-In > 50%)

| Module | Fan-In | Fan-Out | Critical? | Dependents |
|--------|--------|---------|-----------|------------|
| db-common | 3/5 (60%) | 1 | ⚠️ YES | auth-service, user-service, order-service |
| shared-types | 4/5 (80%) | 0 | ⚠️ YES | api-gateway, auth-service, user-service, order-service |

### db-common — Risk Assessment
- **Role:** Database connection pool and query helpers
- **Source:** src/db-common/
- **Risk:** Schema changes here affect 60% of all modules
- **Mitigation:** Well-defined interface; changes propagate through repository pattern
```

---

## Example 4: Validate Extracted Content

```yaml
invocation:
  skill: x-ipe-tool-rev-eng-dependency-analysis
  operation: validate
  input:
    content_path: "/workspace/output/section-04"
    section_id: "4-dependency-analysis"
```

### Expected Validation Output

```yaml
validation_result:
  section_id: "4-dependency-analysis"
  passed: true
  criteria:
    - id: REQ-4.1
      status: PASS
      feedback: "Inter-module dependency graph with 5 edges across 5 modules"
    - id: REQ-4.2
      status: PASS
      feedback: "6 external libraries with resolved versions from package-lock.json"
    - id: REQ-4.3
      status: PASS
      feedback: "All dependencies classified (3 runtime, 2 dev, 1 dev type-def)"
    - id: OPT-4.4
      status: PASS
      feedback: "1 circular dependency chain detected (auth ↔ user)"
    - id: OPT-4.5
      status: PASS
      feedback: "2 critical hub modules identified (db-common, shared-types)"
    - id: OPT-4.6
      status: INCOMPLETE
      feedback: "Mermaid diagrams present but Architecture DSL not generated"
  missing_info: []
```

---

## Example 5: Package Final Output

```yaml
invocation:
  skill: x-ipe-tool-rev-eng-dependency-analysis
  operation: package
  input:
    content_path: "/workspace/output/section-04"
    output_dir: "/workspace/output/final/section-04-dependency-analysis"
```

### Expected Directory Structure

```
section-04-dependency-analysis/
├── index.md                      # Overview table: 5 modules, 5 edges, 6 libraries, 1 cycle, 2 hubs
├── 01-inter-module-deps.md       # Adjacency list + dependency table
├── 02-external-library-deps.md   # Library inventory with versions
├── 03-circular-dependencies.md   # 1 cycle: auth ↔ user
├── 04-critical-dependencies.md   # 2 hub modules: db-common, shared-types
├── 05-dependency-visualization.md # Mermaid flowchart + pie chart
├── screenshots/
└── tests/
    ├── test_auth_verify.ts        # Validates auth → user dependency
    └── test_user_middleware.ts     # Validates user → auth dependency
```
