# Code Refactor - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Large File Refactoring

**Request:** "Refactor the services.py file - it's getting too large"

### Phase 1: Assessment

```
Step 1.1: Identify Scope
  target: src/services.py (850 lines)
  type: Web Backend (Flask)
  feature_id: null (general refactoring)

Step 1.2: Quality Analysis
  - Readability: 5/10 (hard to navigate)
  - Maintainability: 4/10 (changes risky)
  - Testability: 6/10 (some mocking needed)
  - Cohesion: 3/10 (multiple concerns)
  - Coupling: 5/10 (moderate)
  - DRY: 6/10 (some duplication)
  quality_score_before: 4.8

Step 1.3: Feature Alignment
  → No feature_id, skipping

Step 1.4: Test Coverage
  coverage_before: 72% on services.py
  critical_gaps:
    - FileWatcherService.watch() untested
    - error handling paths untested

Step 1.5: Refactoring Plan
  principles:
    - Service Layer
    - Single Responsibility
    - Config Centralization
  phases:
    - phase: 1 - Add missing tests
    - phase: 2 - Extract FileService
    - phase: 3 - Extract TerminalService
    - phase: 4 - Extract SettingsService
```

### Phase 2: Preparation

```
Step 2.1: Feature Details
  → No feature, skipping

Step 2.2: Add Tests
  - Added 8 tests for FileWatcherService
  - Added 5 tests for error handling
  tests_added: 13
  coverage_after_prep: 86%
  ✅ Ready to refactor
```

### Phase 3: Execution

```
Step 3.1: Refactor
  Phase 1: Extract FileService
    - Created src/services/file_service.py
    - Moved FileService, FileWatcherService, ContentService
    - Updated imports in app.py
    - All 348 tests pass
    - Committed

  Phase 2: Extract TerminalService
    - Created src/services/terminal_service.py
    - Moved TerminalSession, SessionManager, etc.
    - All 348 tests pass
    - Committed

  Phase 3: Extract SettingsService
    - Created src/services/settings_service.py
    - Moved SettingsService, ProjectFoldersService
    - All 348 tests pass
    - Committed

Step 3.2: Split Complete
  files_split: 3
  original: 850 lines
  new files: 
    - file_service.py: 280 lines
    - terminal_service.py: 320 lines
    - settings_service.py: 250 lines
```

### Phase 4: Finalization

```
Step 4.1: Quality Verification
  - Readability: 8/10
  - Maintainability: 8/10
  - Testability: 8/10
  - Cohesion: 9/10
  - Coupling: 7/10
  - DRY: 7/10
  quality_score_after: 7.8
  
  All 348 tests pass
  Coverage maintained at 86%

Step 4.2: Design Update
  → No technical design exists, skipping
```

### Output

```yaml
category: Standalone
next_task_type: null
require_human_review: Yes
task_output_links:
  - src/services/file_service.py
  - src/services/terminal_service.py
  - src/services/settings_service.py
  - tests/test_file_service.py (13 tests added)

refactor_scope: "Split services.py (850 lines) into 3 domain-specific service modules"
quality_score_before: 4.8
quality_score_after: 7.8
tests_added: 13
files_split: 3
principles_applied:
  - Service Layer
  - Single Responsibility
  - Config Centralization
```

---

## Example 2: Low Coverage - Blocked Scenario

**Request:** "Refactor the utils.py module"

**Execution:**
```
1. Identify Scope:
   target: src/utils.py (300 lines)
   
2. Check Test Coverage:
   coverage: 45% ← BELOW 80% THRESHOLD
   
3. BLOCKED - Cannot proceed safely
   - Reason: Test coverage too low (45% < 80%)
   - Required: Add tests to reach ≥80% before refactoring
   
4. Return to human:
   "Cannot safely refactor utils.py. 
    Current coverage: 45%
    Required: ≥80%
    
    Action needed: Add tests for:
    - parse_config() (0% covered)
    - validate_input() (30% covered)
    - format_output() (60% covered)"
```

---

## Example 3: Feature-Related Refactoring

**Request:** "Refactor auth module to improve testability"

**Execution:**
```
1. Identify Scope:
   target: src/auth/
   feature_id: FEATURE-001 (User Authentication)

2. Read Feature Docs:
   - specification: docs/requirements/FEATURE-001/specification.md
   - technical design: docs/requirements/FEATURE-001/technical-design.md
   
3. Check Test Coverage:
   coverage: 85% ✓

4. Generate Plan:
   - Extract interfaces for dependency injection
   - Split AuthService into AuthService + TokenService
   
5. Human Approval: "approve"

6. Execute Refactor:
   - Created src/auth/interfaces.py
   - Split service classes
   - Updated tests to use interfaces
   - All tests pass

7. Update Technical Design:
   - Updated component table
   - Added Design Change Log entry:
     | 01-20-2026 | Code Refactor | Split AuthService for testability |
   
8. Output:
   quality_score_before: 6.5
   quality_score_after: 8.2
   technical_design_updated: true
```
