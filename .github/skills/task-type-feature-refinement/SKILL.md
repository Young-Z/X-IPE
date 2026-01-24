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

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |

---

## Skill/Task Completion Output

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: feature-stage
  status: completed | blocked
  next_task_type: task-type-technical-design
  require_human_review: Yes
  task_output_links: [docs/requirements/FEATURE-XXX/specification.md]
  feature_id: FEATURE-XXX
  feature_title: {title}
  feature_version: {version}
  feature_phase: Feature Refinement
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
| 3 | Web Research | Research domain rules, compliance, best practices | Research complete |
| 4 | Create Spec | Create/update `specification.md` with all sections | Specification written |
| 5 | Complete | Verify DoD, output summary, request human review | Human review |

**⛔ BLOCKING RULES:**
- Step 1: BLOCKED if feature not on board or status not "Planned"
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
1. IF docs/requirements/requirement-details.md exists:
   READ requirement-details.md to understand:
     - Overall requirement context
     - Related features
     - Business goals

2. IF feature has dependencies:
   FOR EACH dependency in Feature Data Model:
     CHECK if dependency specification exists
     READ to understand integration points

3. IF feature has architecture implications:
   CHECK docs/architecture/ for relevant designs
```

**🌐 Web Search (Recommended):**
Use web search capability to research:
- Domain-specific business rules and edge cases
- Industry compliance requirements (GDPR, PCI-DSS, HIPAA, etc.)
- User experience best practices for similar features
- Common pitfalls and edge cases in similar implementations
- Accessibility requirements and standards (WCAG)

**🎨 Mockup Reference (Conditional):**
```
IF Technical Scope includes [Frontend] OR [Full Stack]:
  1. Check specification.md for "Linked Mockups" section
  2. Open and review each linked mockup file
  3. Extract UI/UX requirements:
     - Layout and component structure
     - User interaction patterns
     - Visual design elements
     - Form fields and validation
  4. Document UI-specific acceptance criteria based on mockups
  5. Note any gaps between mockup and requirements

ELSE (Backend/API Only/Database):
  - Skip mockup reference
  - Focus on data models, APIs, and business logic
```

---

### Step 3: Create/Update Feature Specification

**Action:** Create or update specification at `docs/requirements/FEATURE-XXX/specification.md`

---

## ⚠️ Single File with Version History (IMPORTANT)

**Rule:** Maintain ONE specification file per feature with version history inside.

**DO NOT create versioned files like:**
- ❌ `specification-v2.md`
- ❌ `specification-v1.md`

**Instead:**
- ✅ Keep single `specification.md` file
- ✅ Add/update Version History table after the header
- ✅ Update content in place with new version

**Version History Format (add after document header):**
```markdown
## Version History

| Version | Date | Description |
|---------|------|-------------|
| v2.0 | 01-22-2026 | Major upgrade: xterm.js, session persistence, split-pane |
| v1.0 | 01-18-2026 | Initial specification |
```

**When updating existing specification:**
1. Increment version in document header (v1.0 → v2.0)
2. Add new row to Version History table
3. Update specification content in place
4. Keep the same filename: `specification.md`

---

**Specification Structure:**
```markdown
# Feature Specification: {Feature Title}

> Feature ID: FEATURE-XXX  
> Version: v1.0  
> Status: Refined  
> Last Updated: MM-DD-YYYY

## Overview

[2-3 paragraph detailed description of what this feature does, why it's needed, and who will use it]

## User Stories

As a [user type], I want to [action/goal], so that [benefit/value].

**Examples:**
- As a **customer**, I want to **save items to my cart**, so that **I can purchase them later**.
- As an **admin**, I want to **view all user orders**, so that **I can track sales and resolve issues**.

## Acceptance Criteria

- [ ] Criterion 1: [Specific, measurable condition]
- [ ] Criterion 2: [Specific, measurable condition]
- [ ] Criterion 3: [Specific, measurable condition]
- [ ] Criterion 4: [Specific, measurable condition]
- [ ] Criterion 5: [Specific, measurable condition]

## Functional Requirements

### FR-1: [Requirement Name]

**Description:** [What the system must do]

**Details:**
- Input: [What data is provided]
- Process: [What happens]
- Output: [What result is produced]

### FR-2: [Requirement Name]
[Repeat for each functional requirement]

## Non-Functional Requirements

### NFR-1: Performance

- Response time: [X seconds/milliseconds]
- Throughput: [X requests per second]
- Concurrent users: [X users]

### NFR-2: Security

- Authentication required: [Yes/No]
- Authorization level: [Role/permission required]
- Data encryption: [What data, how encrypted]

### NFR-3: Scalability

- Expected growth: [User/data growth projections]
- Scaling strategy: [Horizontal/vertical]

## UI/UX Requirements

[If applicable]

**Wireframes/Mockups:** [Link or embed]

**User Flows:**
1. User navigates to [page/screen]
2. User performs [action]
3. System displays [result]

**UI Elements:**
- Button: [Label, action]
- Form fields: [List with validation rules]
- Error messages: [List with conditions]

## Dependencies

### Internal Dependencies

- **FEATURE-XXX:** [Why this feature is needed, what it provides]
- **FEATURE-YYY:** [Why this feature is needed, what it provides]

### External Dependencies

- **Library/Service Name:** [Purpose, version if known]
- **Third-party API:** [What functionality it provides]

## Business Rules

### BR-1: [Rule Name]

**Rule:** [Clear statement of business rule]

**Example:** 
- Only authenticated users can add items to cart
- Prices must be positive numbers
- Discounts cannot exceed 90%

### BR-2: [Rule Name]
[Repeat for each business rule]

## Edge Cases & Constraints

### Edge Case 1: [Scenario]

**Scenario:** [Describe unusual or boundary condition]  
**Expected Behavior:** [How system should respond]

**Examples:**
- User session expires during checkout → Redirect to login, preserve cart
- Database connection lost → Show error, queue for retry
- Invalid input format → Return validation error with details

## Out of Scope

- [Explicitly list what this feature does NOT include]
- [Helps prevent scope creep]

**Examples:**
- Social media login (only email/password for v1.0)
- Multi-factor authentication (planned for v2.0)
- Mobile app support (web only for v1.0)

## Technical Considerations

[Hints for technical design - not detailed design, just considerations]

- Suggested technology/framework
- Known performance requirements
- Security considerations
- Integration points

## Open Questions

- [ ] Question 1: [What needs clarification]
- [ ] Question 2: [What needs decision]
- [ ] Question 3: [What needs stakeholder input]

---
```

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
| 1 | docs/requirements/FEATURE-XXX/specification.md created | Yes |
| 2 | All specification sections completed | Yes |
| 3 | Acceptance criteria are testable | Yes |
| 4 | Dependencies documented | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

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
