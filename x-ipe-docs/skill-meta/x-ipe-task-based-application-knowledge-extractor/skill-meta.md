# Skill Meta: x-ipe-task-based-application-knowledge-extractor

> Version: v1.0 | Status: Candidate | Last Updated: 03-17-2026

---

## Skill Metadata

```yaml
skill_name: "x-ipe-task-based-application-knowledge-extractor"
skill_type: "task-based"
skill_category: "standalone"
version: "1.0.0"
status: "candidate"
created_date: "2026-03-17"
last_modified: "2026-03-17"
```

---

## Skill Summary

**Purpose:** Extract knowledge from applications (source code repos, documentation folders, public URLs, running web apps, single files) and package it into KB intake format. Works as a "hands-on worker" — doing the actual data gathering, reading files, browsing web, inspecting apps. Delegates to tool skills (e.g., `x-ipe-tool-knowledge-extraction-user-manual`) for extraction structure (playbooks, collection templates, acceptance criteria).

**Triggers:**
- "extract knowledge"
- "knowledge extraction"
- "extract user manual"
- "analyze application"
- "extract documentation"
- "build knowledge base from app"

**Category:** `standalone`

**Next Task-Based Skills:**
- `x-ipe-tool-kb-librarian` — Organize extracted KB files into knowledge base

---

## Acceptance Criteria Mapping

### MoSCoW Priority Classification

| AC ID | Description | MoSCoW | Test Type |
|-------|-------------|--------|-----------|
| **MUST Have** |
| AC-050A-01a | SKILL.md exists with valid input/output YAML | Must | Unit |
| AC-050A-01b | Input parameters declare target, purpose, config_overrides | Must | Unit |
| AC-050A-01c | Output result declares extraction_status, loaded_tool_skills, detected types, checkpoint_path | Must | Unit |
| AC-050A-02a | Detect "source_code_repo" for directories with Python/JS source files | Must | Unit |
| AC-050A-02b | Detect "documentation_folder" for directories with only markdown | Must | Unit |
| AC-050A-02c | Detect "public_url" for https:// URLs | Must | Unit |
| AC-050A-02d | Detect "running_web_app" for localhost URLs | Must | Unit |
| AC-050A-02e | Detect "single_file" for single file paths | Must | Unit |
| AC-050A-02f | Return error for non-existent paths | Must | Unit |
| AC-050A-04a | Discover and load tool skills via glob pattern | Must | Integration |
| AC-050A-04b | Tool skill returns playbook, collection template, acceptance criteria paths | Must | Integration |
| AC-050A-04c | Halt with error when no matching tool skill exists | Must | Unit |
| AC-050A-06a | Create .checkpoint/ folder in working directory | Must | Unit |
| **SHOULD Have** |
| AC-050A-03a | Detect "web" app type for package.json + HTML | Should | Unit |
| AC-050A-03b | Detect "cli" app type for argparse/click/commander | Should | Unit |
| AC-050A-03c | Detect "mobile" app type for React Native/Flutter/Swift | Should | Unit |
| AC-050A-03d | Classify "unknown" for documentation folders | Should | Unit |
| AC-050A-04d | Select only tool skill matching extraction category | Should | Unit |
| AC-050A-06b | Write extracted content to temp file in .checkpoint/ | Should | Unit |
| AC-050A-06c | Read tool skill feedback from file path | Should | Unit |
| AC-050A-06d | Create timestamped subfolder when .checkpoint/ exists | Should | Unit |
| **COULD Have** |
| AC-050A-05a | Suggest applicable categories for source code with REST endpoints | Could | Unit |
| AC-050A-05b | Select v1-supported category and log deferred categories | Could | Unit |
| AC-050A-05c | Halt with error when no applicable category detected | Could | Unit |

---

## Test Scenarios

### Happy Path Scenarios

#### Scenario 1: Local Flask Web App → User Manual Extraction

```yaml
# Input
target: "/Users/dev/my-flask-app"
purpose: "user-manual"
config_overrides:
  max_retries: 3

# Expected Behavior
1. Detect input_type: "source_code_repo"
2. Detect format: "mixed (python, html, markdown)"
3. Detect app_type: "web" (Flask framework detected)
4. Select category: "user-manual"
5. Load tool skill: "x-ipe-tool-knowledge-extraction-user-manual"
6. Initialize .checkpoint/session-{timestamp}/
7. Return status: "ready_for_extraction"

# Expected Output
status: "ready_for_extraction"
input_analysis:
  input_type: "source_code_repo"
  format: "mixed"
  app_type: "web"
  source_metadata:
    primary_language: "python"
    framework: "flask"
loaded_tool_skill: "x-ipe-tool-knowledge-extraction-user-manual"
checkpoint_path: ".checkpoint/session-20260317-143022/"
```

#### Scenario 2: Public URL Documentation → User Manual Extraction

```yaml
# Input
target: "https://docs.example.com/getting-started"
purpose: "user-manual"

# Expected Behavior
1. Detect input_type: "public_url"
2. Detect format: "html"
3. Detect app_type: "unknown" (no code markers)
4. Select category: "user-manual"
5. Load tool skill: "x-ipe-tool-knowledge-extraction-user-manual"
6. Initialize .checkpoint/session-{timestamp}/
7. Return status: "ready_for_extraction"

# Expected Output
status: "ready_for_extraction"
input_analysis:
  input_type: "public_url"
  format: "html"
  app_type: "unknown"
loaded_tool_skill: "x-ipe-tool-knowledge-extraction-user-manual"
checkpoint_path: ".checkpoint/session-20260317-143022/"
```

### Edge Case Scenarios

#### Scenario 3: Empty Directory

```yaml
# Input
target: "/Users/dev/empty-folder"
purpose: "user-manual"

# Expected Behavior
1. Analyze target directory
2. Detect 0 files
3. Halt with error: "Input directory is empty"

# Expected Output
status: "blocked"
error: "Input directory is empty"
```

#### Scenario 4: Inaccessible URL

```yaml
# Input
target: "https://nonexistent.example.com/docs"
purpose: "user-manual"

# Expected Behavior
1. Attempt URL reachability check
2. Receive HTTP 404 or timeout
3. Halt with error: "URL not reachable (HTTP 404)"

# Expected Output
status: "blocked"
error: "URL not reachable (HTTP 404)"
```

### Blocking Scenarios

#### Scenario 5: No Tool Skill Found

```yaml
# Input
target: "/Users/dev/my-app"
purpose: "user-manual"

# Expected Behavior (assuming tool skill not installed)
1. Detect input_type: "source_code_repo"
2. Select category: "user-manual"
3. Attempt to load tool skill via glob
4. Glob returns no matches
5. Halt with error: "No tool skill found for category 'user-manual'. Install x-ipe-tool-knowledge-extraction-user-manual."

# Expected Output
status: "blocked"
error: "No tool skill found for category 'user-manual'. Install x-ipe-tool-knowledge-extraction-user-manual."
```

---

## Test Coverage Requirements

| Test Type | Coverage Target | Priority |
|-----------|----------------|----------|
| Unit | ≥ 80% | Must |
| Integration | ≥ 60% | Should |
| End-to-End | ≥ 40% | Could |

---

## Dependencies

### Internal Dependencies
- **X-IPE Skill Framework:** `.github/skills/` conventions, SKILL.md format, input/output YAML contracts
- **X-IPE Config:** `x-ipe-docs/config/tools.json` for web search gating

### External Dependencies
- **`x-ipe-tool-knowledge-extraction-user-manual`:** Required for v1 extraction (built in separate EPIC)
- **EPIC-049 (KB infrastructure):** Required for downstream output via `.intake/` pipeline (FEATURE-050-E)

---

## Feature Breakdown Context

This skill is being built incrementally across 5 features:

| Feature ID | Phase | Scope | Status |
|------------|-------|-------|--------|
| FEATURE-050-A | Foundation | SKILL.md skeleton, input detection, tool skill loading, category selection, handoff init | ✅ Current |
| FEATURE-050-B | Source Extraction | File reading, web browsing, app inspection, content gathering | 🔜 Future |
| FEATURE-050-C | Extract-Validate Loop | Send to tool skill for validation, assess coverage, decide depth/breadth | 🔜 Future |
| FEATURE-050-D | Checkpoint & Resume | Retry logic, pause/resume, checkpoint management, error handling | 🔜 Future |
| FEATURE-050-E | KB Intake Output | Quality scoring, `.intake/` pipeline, completion | 🔜 Future |

**v1 Scope:** User-manual extraction category only, one purpose at a time.

---

## Documentation References

- **Specification:** `x-ipe-docs/requirements/EPIC-050/FEATURE-050-A/specification.md`
- **Technical Design:** `x-ipe-docs/requirements/EPIC-050/FEATURE-050-A/technical-design.md`
- **SKILL.md:** `x-ipe-docs/skill-meta/x-ipe-task-based-application-knowledge-extractor/candidate/SKILL.md`
- **Input Detection Heuristics:** `x-ipe-docs/skill-meta/x-ipe-task-based-application-knowledge-extractor/candidate/references/input-detection-heuristics.md`
- **Handoff Protocol:** `x-ipe-docs/skill-meta/x-ipe-task-based-application-knowledge-extractor/candidate/references/handoff-protocol.md`
- **Category Taxonomy:** `x-ipe-docs/skill-meta/x-ipe-task-based-application-knowledge-extractor/candidate/references/category-taxonomy.md`
- **Examples:** `x-ipe-docs/skill-meta/x-ipe-task-based-application-knowledge-extractor/candidate/references/examples.md`

---

## Design Principles Applied

- **SOLID:** Single Responsibility (input detection, category selection, tool loading are separate concerns)
- **YAGNI:** v1 only supports user-manual category; multi-category is deferred
- **KISS:** Hardcoded category filter in v1; AI-driven selection deferred to future

---

## Notes

- Foundation phase (FEATURE-050-A) establishes the skeleton but does NOT perform actual extraction
- The skill creates `.checkpoint/` folder but extraction logic is in FEATURE-050-B
- Tool skill interface contract is defined but tool skills are built in a separate EPIC
- All future features depend on this foundation phase completing successfully
