---
name: task-type-feature-refinement
description: Refine feature specification for a single feature. Queries feature board for context, creates/updates specification document. Use when a feature needs detailed requirements. Triggers on requests like "refine feature", "detail specification", "clarify requirements".
---

# Task Type: Feature Refinement

## Purpose

Refine feature requirements for a single feature by:
1. Querying feature board for full Feature Data Model
2. Creating/updating detailed feature specification
3. Documenting user stories, acceptance criteria, and requirements
4. NO board status update (handled by category skill)

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Feature Refinement |
| Category | feature-stage |
| Next Task Type | Technical Design |
| Require Human Review | Yes |
| Feature Phase | Feature Refinement |

---

## Task Type Required Input Attributes

| Attribute | Default Value | Description |
|-----------|---------------|-------------|
| Auto Proceed | False | Whether to auto-proceed to next task |
| Mockup List | N/A | Path to mockup file(s) from previous Idea Mockup task or context |

### Mockup List Attribute

**Purpose:** Provides UI/UX mockup reference for extracting frontend requirements into the specification.

**Source:** This value can be obtained from:
1. Previous task output (Idea Mockup task's `task_output_links`)
2. Human input (explicit mockup path provided)
3. Idea summary document's "Mockups & Prototypes" section
4. Default: N/A (no mockup available)

**Loading Logic:**
```
1. IF previous task was "Idea Mockup":
   → Extract mockup path from previous task's task_output_links
   → Set Mockup List = extracted path

2. ELSE IF human provides explicit Mockup List:
   → Use human-provided value

3. ELSE IF idea-summary-vN.md exists in related idea folder:
   → Check for "Mockups & Prototypes" section
   → Extract mockup paths
   → Set Mockup List = extracted paths

4. ELSE:
   → Set Mockup List = N/A
```

**Usage:** When Mockup List is provided, the agent MUST analyze the mockup during Step 2 (Gather Context) and extract UI/UX requirements into the specification.

---

## Skill/Task Completion Output

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: feature-stage
  status: completed | blocked
  next_task_type: task-type-technical-design
  require_human_review: Yes
  auto_proceed: {from input Auto Proceed}
  mockup_list: {updated with copied paths if mockups were copied}
  task_output_links: [x-ipe-docs/requirements/FEATURE-XXX/specification.md]
  feature_id: FEATURE-XXX
  feature_title: {title}
  feature_version: {version}
  feature_phase: Feature Refinement
  
  # Mockup-related attributes (if applicable)
  linked_mockups:
    - mockup_name: "Description of mockup function"
      mockup_path: "x-ipe-docs/requirements/FEATURE-XXX/mockups/mockup-name.html"
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Feature exists on feature board | Yes |
| 2 | Feature status is "Planned" | Yes |

---

## Execution Flow

Execute Feature Refinement by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Query Board | Get Feature Data Model from feature board | Feature data received |
| 2 | Gather Context | Read requirement-details.md, check dependencies | Context understood |
| 2.5 | Process Mockups | **Auto-detect** mockups from idea folder if not in feature folder | Mockups processed |
| 3 | Web Research | Research domain rules, compliance, best practices | Research complete |
| 4 | Create Spec | Create/update `specification.md` with all sections | Specification written |
| 5 | Complete | Verify DoD, output summary, request human review | Human review |

**⛔ BLOCKING RULES:**
- Step 1: BLOCKED if feature not on board or status not "Planned"
- **Step 2.5: MUST scan for mockups if feature folder has no mockups/** (auto-detection required)
- Step 5 → Human Review: Human MUST approve specification before Technical Design

---

## Execution Procedure

### Step 1: Query Feature Board

**Action:** Get full Feature Data Model for context

```
CALL feature-stage+feature-board-management skill:
  operation: query_feature
  feature_id: {feature_id from task_data}

RECEIVE Feature Data Model:
  feature_id: FEATURE-XXX
  title: {Feature Title}
  version: v1.0
  status: Planned
  description: {description}
  dependencies: [...]
  created: MM-DD-YYYY
  last_updated: MM-DD-YYYY HH:MM:SS
```

**Use Feature Data Model to:**
- Understand feature context
- Check dependencies
- Get initial description
- Determine if specification exists

---

### Step 2: Gather Additional Context

**Action:** Read related documents for comprehensive understanding

```
1. IF x-ipe-docs/requirements/requirement-details.md exists:
   READ requirement-details.md to understand:
     - Overall requirement context
     - Related features
     - Business goals

2. IF feature has dependencies:
   FOR EACH dependency in Feature Data Model:
     CHECK if dependency specification exists
     READ to understand integration points

3. IF feature has architecture implications:
   CHECK x-ipe-docs/architecture/ for relevant designs
```

**🌐 Web Search (Recommended):**
Use web search for: domain rules, compliance (GDPR, PCI-DSS, HIPAA), UX best practices, common pitfalls, accessibility (WCAG).

**🎨 Mockup Analysis (When Mockup List Provided):**
- Analyze mockup file(s) and extract UI/UX requirements
- Document in "UI/UX Requirements" section with acceptance criteria
- Identify gaps: missing interactions, loading/empty/error states
- Ask human about ambiguities if needed

> See [references/specification-writing-guide.md](references/specification-writing-guide.md) for mockup-to-specification mapping.

---

### Step 2.5: Process Mockups

**⚠️ MANDATORY CHECK - Auto-detect and copy mockups if not in feature folder:**

```
BEFORE proceeding to Step 3:

1. CHECK if feature folder has mockups:
   - Path: x-ipe-docs/requirements/{FEATURE-ID}/mockups/
   - IF mockups folder exists AND contains files → Skip to Step 3
   
2. IF mockups NOT in feature folder:
   a. Check if feature came from an Idea (look for idea folder reference in requirement-details.md)
   b. IF idea folder exists:
      - Scan: x-ipe-docs/ideas/{idea-folder}/mockups/
      - IF mockups found:
        → Create mockups folder: x-ipe-docs/requirements/{FEATURE-ID}/mockups/
        → Copy ALL mockup files from idea folder to feature folder
        → Update Mockup List attribute with copied file paths
        → Notify: "Found {N} mockups in idea folder, copied to feature folder"
   
3. IF Mockup List is provided (input attribute) AND NOT yet copied:
   a. Create mockups folder if not exists: x-ipe-docs/requirements/{FEATURE-ID}/mockups/
   b. FOR EACH mockup in Mockup List:
      - Copy mockup file from source path
      - Save to: x-ipe-docs/requirements/{FEATURE-ID}/mockups/{filename}
   c. Update Mockup List with new paths
   
4. IF no mockups found after auto-detection:
   - Log: "No mockups found - proceeding without mockups"
   - Proceed to Step 3
```

**File Operations:**
```yaml
# Example: Auto-detected from idea folder
Source: x-ipe-docs/ideas/004. Change Request to Workplace/mockups/
        - dashboard-v1.html
        - settings-panel.html

Target: x-ipe-docs/requirements/FEATURE-008/mockups/
        - dashboard-v1.html
        - settings-panel.html

# Example: From Mockup List input
Source (Mockup List): x-ipe-docs/ideas/Draft Idea - 01232026/mockups/home-page-v1.html
Target: x-ipe-docs/requirements/FEATURE-012/mockups/home-page-v1.html
```

**Rules:**
- Only copy if mockups NOT already in feature folder (avoid duplicates)
- Preserve original filenames when copying
- Create mockups folder only if mockups found
- Update Mockup List attribute after copying for use in Step 2 analysis

---

### Step 3: Create/Update Feature Specification

**Action:** Create or update specification at `x-ipe-docs/requirements/FEATURE-XXX/specification.md`

---

## ⚠️ Single File with Version History (IMPORTANT)

**Rule:** Maintain ONE specification file per feature with version history inside.

- ✅ Keep single `specification.md` file with Version History table
- ❌ Do NOT create versioned files like `specification-v2.md`

> See [references/specification-writing-guide.md](references/specification-writing-guide.md) for version history format.

---

**Specification Structure:**
```markdown
# Feature Specification: {Feature Title}

> Feature ID: FEATURE-XXX  
> Version: v1.0  
> Status: Refined  
> Last Updated: MM-DD-YYYY

## Version History
[Version table - see guide]

## Linked Mockups
[Mockup table if applicable - see guide]

## Overview
[2-3 paragraph description: what, why, who]

## User Stories
[As a [user], I want to [action], so that [benefit]]

## Acceptance Criteria
[Testable, measurable conditions]

## Functional Requirements
[FR-N: Requirement with Input/Process/Output]

## Non-Functional Requirements
[Performance, Security, Scalability]

## UI/UX Requirements
[Wireframes, User Flows, UI Elements]

## Dependencies
[Internal and External]

## Business Rules
[BR-N: Clear rule statements]

## Edge Cases & Constraints
[Scenarios with expected behavior]

## Out of Scope
[What is NOT included]

## Technical Considerations
[Hints for technical design - WHAT not HOW]

## Open Questions
[What needs clarification]
```

> **Full templates and examples:** See [references/specification-writing-guide.md](references/specification-writing-guide.md)

**Specification Quality Checklist:**
- [ ] All acceptance criteria are testable
- [ ] User stories provide clear value
- [ ] Functional requirements are complete
- [ ] Non-functional requirements defined
- [ ] Dependencies clearly stated
- [ ] Edge cases identified
- [ ] Out of scope explicitly listed

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | x-ipe-docs/requirements/FEATURE-XXX/specification.md created | Yes |
| 2 | All specification sections completed | Yes |
| 3 | Acceptance criteria are testable | Yes |
| 4 | Dependencies documented | Yes |
| 5 | Mockups copied to feature folder (if found in idea folder) | If Applicable |
| 6 | Mockup List analyzed (if provided or copied) | If Applicable |
| 7 | UI/UX requirements extracted from mockup | If Mockup Provided |
| 8 | Linked Mockups section populated | If Mockup Provided |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

### Pattern: Mockup-Driven Refinement

**When:** Mockup List is provided from Idea Mockup task
**Then:**
```
1. Open and thoroughly analyze mockup file(s)
2. Extract all visible UI elements and interactions
3. Create UI/UX Requirements section with:
   - Component inventory from mockup
   - User interaction flows
   - Form validation rules
   - Error/empty/loading states
4. Add "Linked Mockups" section at top of specification
5. Cross-reference acceptance criteria to mockup elements
6. Note any functionality implied by mockup not in requirements
```

### Pattern: Well-Defined Feature

**When:** Feature has clear scope from breakdown
**Then:**
```
1. Query feature board for context
2. Read requirement-details.md
3. Create specification with standard sections
4. Request human review
```

### Pattern: Feature with Dependencies

**When:** Feature depends on other features
**Then:**
```
1. Read dependent feature specifications first
2. Identify integration points
3. Document assumptions about dependencies
4. Note blocking vs non-blocking dependencies
```

### Pattern: Complex Domain

**When:** Feature involves unfamiliar domain rules
**Then:**
```
1. Research domain best practices (web search)
2. Document compliance requirements
3. Include domain glossary in specification
4. Ask human for domain-specific clarifications
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip board query | Missing context | Always query feature board first |
| Vague acceptance criteria | Untestable | Make criteria specific and measurable |
| Technical implementation details | Wrong focus | Focus on WHAT, not HOW |
| Ignore dependencies | Integration failures | Document all dependencies |
| Multiple specification files | Version confusion | Single file with version history |
| Skip web research | Reinvent wheel | Research domain best practices |
| Ignore mockup when provided | Missing UI requirements | Always analyze Mockup List |
| Skip mockup-to-spec mapping | Incomplete specification | Extract all UI elements from mockup |

---

## Example

See [references/examples.md](references/examples.md) for detailed execution examples including:
- User authentication specification
- Enhancement refinement from change request
- Missing feature entry (blocked)
- Complex feature requiring split
- Specification with thorough edge case coverage

---

## Notes

- Work on ONE feature at a time (feature_id from task_data)
- Query feature board first to get context
- Do NOT update feature board status (category skill handles this)
- Output feature_phase = "refinement" for correct board update
- Specification is input for Technical Design task
- Keep specifications detailed but focused on WHAT, not HOW
