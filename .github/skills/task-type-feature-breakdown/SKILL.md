---
name: task-type-feature-breakdown
description: Break requirements into high-level features and create feature list in requirement-details.md (or current active part). Calls feature-board-management to initialize feature tracking. Use when requirements are gathered and need to be split into discrete features. Triggers on requests like "break down features", "split into features", "create feature list".
---

# Task Type: Feature Breakdown

## Purpose

Break user requests into high-level features by:
1. Analyzing requirement documentation (or current active part)
2. Identifying feature boundaries
3. Creating feature list in requirement-details.md (or current active part)
4. Calling feature-board-management to create features on board

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Feature Breakdown |
| Category | requirement-stage |
| Next Task Type | Feature Refinement |
| Require Human Review | Yes |

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |
| Mockup List | N/A |

**Mockup List Structure:**
```yaml
mockup_list:
  - mockup_name: "Description of what function the mockup is for"
    mockup_list: "URL to the mockup"
  - mockup_name: "Another mockup description"
    mockup_list: "URL to the mockup"
```

---

## Skill/Task Completion Output

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: requirement-stage
  status: completed | blocked
  next_task_type: task-type-feature-refinement
  require_human_review: Yes
  task_output_links: [x-ipe-docs/requirements/requirement-details.md] # or requirement-details-part-X.md
  mockup_list: [inherited from input or N/A]
  
  # Dynamic attributes for requirement-stage
  requirement_id: REQ-XXX
  feature_ids: [FEATURE-001, FEATURE-002, FEATURE-003]
  feature_count: 3
  requirement_details_part: null | 1 | 2 | ... # current active part number (null if no parts)
  linked_mockups:
    - mockup_name: "Description of mockup function"
      mockup_path: "x-ipe-docs/requirements/FEATURE-XXX/mockups/mockup-name.html"
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Requirement documentation exists (user request or requirement doc) | Yes |

---

## Execution Flow

Execute Feature Breakdown by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Analyze | Read requirement-details.md (or current active part) or user request | Requirements understood |
| 2 | Identify Features | Extract features using MVP-first criteria | Features identified |
| 2.5 | Process Mockups | **Auto-detect** mockups from idea folder, copy to feature folders | Mockups processed |
| 3 | Create Summary | Create/update requirement-details.md (or current active part) with feature list | Summary written |
| 4 | Update Board | Call feature-board-management to create features | Board updated |
| 5 | Update Index | If parts exist, update requirement-details-index.md | Index updated |
| 6 | Complete | Verify DoD, output summary, request human review | Human review |

**⛔ BLOCKING RULES:**
- Step 1: If parts exist, work with the CURRENT ACTIVE PART (highest part number)
- Step 2: First feature MUST be "Minimum Runnable Feature" (MVP)
- **Step 2.5: MUST scan idea folder for mockups before skipping** (auto-detection required)
- Step 3: Feature List goes into the PART FILE, NOT the index
- Step 4: MUST use feature-board-management skill (not manual file editing)
- Step 6 → Human Review: Human MUST approve feature list before refinement

---

## Execution Procedure

### Step 1: Analyze Requirements

**Action:** Review requirement information to identify features

```
1. Determine which file to read:
   a. Check if x-ipe-docs/requirements/requirement-details-part-X.md files exist
   b. IF parts exist → Read the CURRENT ACTIVE PART (highest part number)
   c. ELSE IF x-ipe-docs/requirements/requirement-details.md exists → Read it
   d. ELSE → Analyze user request directly

2. Read the determined file:
   - Understand existing requirement summary
   - Identify features from requirements
```

**Look for:**
- Verbs (actions the system must perform)
- Nouns (entities the system must manage)
- Boundaries (where one function ends and another begins)
- User goals and workflows

**Feature Identification Criteria:**

1.  **Prioritize MVP:** The first feature MUST be the "Minimum Runnable Feature". It should be small but sufficient to demonstrate the core value loop (even if imperfect).
2.  **Iterative Expansion:** Subsequent features should build upon the first one, adding complexity or breadth.
3.  **Single Responsibility:** Each feature does one thing well.
4.  **Independent:** Can be developed/tested in isolation (mostly).
5.  **Deliverable Value:** Provides value when completed.
6.  **Reasonable Size:** Fits within a development sprint.

| Consideration | Description |
|---------------|-------------|
| MVP Requirement | First feature = Runnable core loop |
| Complexity | Start simple, then add complexity |
| Dependencies | Minimize cross-feature dependencies |

---

### Step 2.5: Process Mockups

**⚠️ MANDATORY CHECK - Auto-detect mockups if not provided**

**Action:** Auto-detect mockups from idea folder, then copy to feature folders and link them.

**Procedure:**
1. If mockup_list empty → scan `x-ipe-docs/ideas/{idea-folder}/mockups/`
2. If still empty → skip to Step 3
3. Create `x-ipe-docs/requirements/{FEATURE-ID}/mockups/` for each feature
4. Copy mockups, link in requirement-details.md and specification.md

**See:** [references/breakdown-guidelines.md](references/breakdown-guidelines.md) for detailed mockup processing procedures and examples.

---

### Step 3: Create/Update Requirement Summary

**Action:** Create or update requirement-details file (or current active part)

**Target File Determination:**
- IF parts exist → Update CURRENT ACTIVE PART (highest part number)
- ELSE → Update x-ipe-docs/requirements/requirement-details.md

**Feature List Table Format:**
```markdown
| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-001 | User Authentication | v1.0 | JWT-based auth | None |
| FEATURE-002 | User Profile | v1.0 | Profile management | FEATURE-001 |
```

**⚠️ IMPORTANT:** Each part file has its OWN Feature List section. Index does NOT contain a Feature List.

**See:** [references/breakdown-guidelines.md](references/breakdown-guidelines.md) for:
- Full file structure templates (single file and part files)
- Feature Details template
- Part file management rules

---

### Step 4: Call Feature Board Management

**Action:** Create features on the feature board

```
CALL feature-stage+feature-board-management skill:
  operation: create_or_update_features
  features:
    - feature_id: FEATURE-001
      title: User Authentication
      version: v1.0
      description: JWT-based user authentication with login, logout, token refresh
      dependencies: []
    - feature_id: FEATURE-002
      title: User Profile  
      version: v1.0
      description: User profile management and settings
      dependencies: [FEATURE-001]
    [... etc for all features]
```

**Output:** Features created on x-ipe-docs/planning/features.md with status "Planned"

---

### Step 5: Update Index (if parts exist)

**Action:** Update requirement-details-index.md when parts exist

**When to execute:** Only if requirement-details-part-X.md files exist

**Procedure:**
1. Open x-ipe-docs/requirements/requirement-details-index.md
2. Update "Parts Overview" table with new feature range
3. Update "Lines" column with approximate line count

**See:** [references/breakdown-guidelines.md](references/breakdown-guidelines.md) for index file structure.

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Requirement-details file (or current part) updated with Feature List | Yes |
| 2 | All features have detailed sections in requirement-details (or part) | Yes |
| 3 | Feature board updated via feature-board-management skill | Yes |
| 4 | All features have status "Planned" on feature board | Yes |
| 5 | If parts exist: requirement-details-index.md updated | Conditional |
| 6 | If mockup_list provided: mockups copied to `x-ipe-docs/requirements/{FEATURE-ID}/mockups/` | Conditional |
| 7 | If mockup_list provided: Linked Mockups section updated | Conditional |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

### Pattern: Clear Requirements

**When:** Well-documented requirements exist
**Then:**
```
1. Read requirement-details.md thoroughly
2. Identify natural feature boundaries
3. Apply MVP-first principle
4. Document dependencies between features
```

### Pattern: Vague Requirements

**When:** Requirements are ambiguous or incomplete
**Then:**
```
1. Ask clarifying questions to human
2. Document assumptions made
3. Start with minimal feature set
4. Flag areas needing more detail
```

### Pattern: Large Scope

**When:** Requirement covers many features
**Then:**
```
1. Group by domain/functionality
2. Identify MVP core (first feature)
3. Create feature hierarchy
4. Limit initial breakdown to 5-7 features
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Too many features | Overwhelming, hard to track | Limit to 5-7 features max |
| Features too granular | Micromanagement | Combine related functions |
| MVP not first | Critical path unclear | Always start with runnable MVP |
| Circular dependencies | Impossible to implement | Ensure DAG structure |
| Manual board updates | Inconsistent state | Use feature-board-management skill |
| Vague feature titles | Unclear scope | Use specific, action-oriented names |

---

## Example

See [references/examples.md](references/examples.md) for detailed execution examples including:
- E-commerce platform feature breakdown
- API integration feature breakdown
- Change request (NEW_FEATURE) breakdown
- Granularity and sizing guidelines

---

## Feature Dependency Guidelines

See [references/breakdown-guidelines.md](references/breakdown-guidelines.md) for:
- Common dependency patterns (sequential, parallel, multiple)
- Dependency rules (no cycles, foundation first, minimal deps)

---

## Best Practices

See [references/breakdown-guidelines.md](references/breakdown-guidelines.md) for:
- Feature sizing guidelines (too large, good size, too small)
- Feature naming conventions (good vs bad names)
- Version numbering rules

---

## Integration with Feature Board Management

This skill **MUST** call the feature-board-management skill to create features on the board.

See [references/breakdown-guidelines.md](references/breakdown-guidelines.md) for integration details and call format.

---

## Notes

- No longer create individual x-ipe-docs/requirements/FEATURE-XXX/feature.md files
- All features consolidated in requirement-details.md
- Feature board (features.md) is the status tracking system
- Feature specifications created later during Feature Refinement task
- Keep feature descriptions concise (50 words max) in the table
- More details go in the feature details section
