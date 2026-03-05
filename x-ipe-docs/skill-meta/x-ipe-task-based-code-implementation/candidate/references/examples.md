# Code Implementation - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Standard Backend+Frontend Feature with AAA Orchestration

**Context:**
- Feature: FEATURE-010-A (Project Management API + UI)
- tech_stack: ["Python/Flask", "HTML/CSS/JavaScript"]
- program_type: "fullstack"

### Execution Flow

```
1. Query Feature Board → FEATURE-010-A, status: Designed

2. Learn Technical Design:
   - Part 1: 3 components (ProjectService, ProjectAPI, ProjectUI)
   - Part 2: REST endpoints, HTML form, validation rules

3. Read Architecture → common Flask patterns from architecture docs

4. Generate AAA Scenarios:

   @backend
   Test Scenario: Create project via API
     Arrange:
       - User is authenticated with valid credentials
       - No project with name "Test Project" exists
     Act:
       - Send POST /api/projects with body { name: "Test Project" }
     Assert:
       - Response status is 201
       - Response body contains new project ID

   @backend
   Test Scenario: Reject duplicate project name
     Arrange:
       - Project "Existing" already exists
     Act:
       - Send POST /api/projects with body { name: "Existing" }
     Assert:
       - Response status is 409
       - Error message contains "already exists"

   @frontend
   Test Scenario: Display project creation form
     Arrange:
       - User is on the projects page
     Act:
       - User clicks "New Project" button
     Assert:
       - Form appears with fields: name, description
       - "Create" button is disabled until name has content

   @integration
   Test Scenario: End-to-end project creation
     Arrange:
       - User is on projects page
       - Backend API is mocked
     Act:
       - User fills "Test Project" and clicks Create
     Assert:
       - Project appears in the list
       - Mock backend received correct POST

   Coverage: 2 ACs → 1 @integration each, 2 endpoints → 2 @backend each,
             1 UI component → 1 @frontend each = 6 scenarios total ✓

5. Route & Invoke Tool Skills:
   - "Python/Flask" → x-ipe-tool-implementation-python (receives @backend scenarios)
   - "HTML/CSS/JavaScript" → x-ipe-tool-implementation-html5 (receives @frontend scenarios)
   
   Invoke python skill → receives: implementation_files, test_files, test_results (all pass)
   Invoke html5 skill → receives: implementation_files, test_files, test_results (all pass)

6. Validate Results:
   - @backend: 4/4 Asserts pass ✓
   - @frontend: 2/2 Asserts pass ✓
   - @integration: 2/2 scenarios pass ✓
   - Lint: all pass ✓
   - Overall: PASS

7. Apply Tracing:
   - Added @x_ipe_tracing to ProjectService.create_project (INFO)
   - Tests still pass ✓
```

### Output

```yaml
category: feature-stage
status: completed
next_task_based_skill: Feature Acceptance Test

task_output_links:
  - src/services/project_service.py
  - src/routes/project_api.py
  - src/static/js/project_ui.js
  - tests/test_project_service.py
  - tests/test_project_ui.py
```

---

## Example 2: Skills-Type Feature (Delegation to Skill Creator)

**Context:**
- Feature: FEATURE-045-A (Orchestrator Core + AAA Generator)
- tech_stack: ["Markdown/SKILL.md"]
- program_type: "skills"

### Execution Flow

```
1. Query Feature Board → FEATURE-045-A, status: Designed

2. Learn Technical Design:
   - Skill files flagged in technical design (.github/skills/ paths)
   - FLAG for x-ipe-meta-skill-creator delegation

3. Read Architecture → No architecture references

4. Generate AAA Scenarios:
   - SKIPPED: program_type == "skills" triggers special-case delegation in Step 5

5. Route & Invoke (Special Case):
   - program_type == "skills" detected → DELEGATE to x-ipe-meta-skill-creator
   - Invoke skill-creator for: x-ipe-task-based-code-implementation (update)
   - Invoke skill-creator for: x-ipe-tool-implementation-general (create)
   - Skill-creator runs its own 9-step process with testing
   - Both skills pass skill-creator DoD ✓

6. Validate Results:
   - SKIPPED: skill-creator has its own validation (Rounds 2-4)

7. Apply Tracing:
   - SKIPPED: only skill files (.md) modified
```

### Output

```yaml
category: feature-stage
status: completed
next_task_based_skill: Feature Acceptance Test

task_output_links:
  - .github/skills/x-ipe-task-based-code-implementation/SKILL.md
  - .github/skills/x-ipe-tool-implementation-general/SKILL.md
```

---

## Example 3: AAA Generation Fallback (Phase 1)

**Context:**
- Feature: FEATURE-020-B
- Specification has vague acceptance criteria
- AAA generation cannot produce valid scenarios

### Execution Flow

```
1-3. Standard steps (Query Board, Learn Design, Read Architecture)

4. Generate AAA Scenarios:
   - ATTEMPT: Parse specification.md
   - PROBLEM: ACs are too vague ("system should handle errors gracefully")
   - FALLBACK: Invoke x-ipe-tool-test-generation as safety net
   - Log: "AAA generation fell back to test-generation"
   - test-generation produces: 12 test files

5. Implement Code:
   - Use test-generation output as TDD guidance (original workflow)
   - Implement code to pass generated tests

6. Verify:
   - Run tests: 12/12 pass ✓
   - Lint: pass ✓
```

---

## Example 4: Tool Skill Retry on Failure

**Context:**
- Feature: FEATURE-015-C
- Backend tool skill fails on first attempt

### Execution Flow

```
4. Generate AAA Scenarios → 8 scenarios generated ✓

5. Route & Invoke:
   - Invoke python skill with 4 @backend scenarios
   - Result: 3/4 Asserts pass, 1 fails
     Failed: "Response includes pagination metadata"
     Error: "KeyError: 'total_count' in response serializer"
   
   - RETRY python skill with:
     - Original 4 scenarios
     - Error context: "KeyError: 'total_count' — response serializer missing pagination fields"
   - Retry result: 4/4 Asserts pass ✓

   - Invoke html5 skill → 4/4 Asserts pass ✓

6. Validate Results → All pass ✓
```
