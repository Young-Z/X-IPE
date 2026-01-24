---
name: task-type-feature-breakdown
description: Break requirements into high-level features and create feature list in requirement-details.md. Calls feature-board-management to initialize feature tracking. Use when requirements are gathered and need to be split into discrete features. Triggers on requests like "break down features", "split into features", "create feature list".
---

# Task Type: Feature Breakdown

## Purpose

Break user requests into high-level features by:
1. Analyzing requirement documentation
2. Identifying feature boundaries
3. Creating feature list in requirement-details.md
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
    mockup_link: "URL to the mockup"
  - mockup_name: "Another mockup description"
    mockup_link: "URL to the mockup"
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
  task_output_links: [docs/requirements/requirement-details.md]
  mockup_list: [inherited from input or N/A]
  
  # Dynamic attributes for requirement-stage
  requirement_id: REQ-XXX
  feature_ids: [FEATURE-001, FEATURE-002, FEATURE-003]
  feature_count: 3
  linked_mockups:
    - mockup_name: "Description of mockup function"
      mockup_path: "docs/requirements/FEATURE-XXX/mockups/mockup-name.html"
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
| 1 | Analyze | Read requirement-details.md or user request | Requirements understood |
| 2 | Identify Features | Extract features using MVP-first criteria | Features identified |
| 2.5 | Process Mockups | Copy mockups to feature folders if mockup_list provided | Mockups processed |
| 3 | Create Summary | Create/update requirement-details.md with feature list | Summary written |
| 4 | Update Board | Call feature-board-management to create features | Board updated |
| 5 | Complete | Verify DoD, output summary, request human review | Human review |

**⛔ BLOCKING RULES:**
- Step 2: First feature MUST be "Minimum Runnable Feature" (MVP)
- Step 4: MUST use feature-board-management skill (not manual file editing)
- Step 5 → Human Review: Human MUST approve feature list before refinement

---

## Execution Procedure

### Step 1: Analyze Requirements

**Action:** Review requirement information to identify features

```
IF docs/requirements/requirement-details.md exists:
  1. Read existing requirement summary
  2. Identify features from requirements
ELSE:
  1. Analyze user request
  2. Extract requirements
  3. Identify features from request
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

### Step 2.5: Process Mockups (if mockup_list provided)

**Action:** Copy mockups from source to feature folder and link them

**When mockup_list is provided in input:**

```
FOR EACH feature in identified_features:
  1. Create mockups folder: docs/requirements/{FEATURE-ID}/mockups/
  
  2. FOR EACH mockup in mockup_list (that relates to this feature):
     - Copy mockup file from mockup_link source
     - Rename to: {mockup_name}.{original_extension}
     - Save to: docs/requirements/{FEATURE-ID}/mockups/{mockup_name}.{ext}
  
  3. Record linked mockups for output
```

**File Operations:**
```yaml
# Example: Input mockup_list
mockup_list:
  - mockup_name: "main-dashboard"
    mockup_link: "docs/ideas/Draft Idea - 01232026/mockup.html"
  - mockup_name: "settings-panel"
    mockup_link: "docs/ideas/Draft Idea - 01232026/mockups/settings.html"

# Result: Files created
docs/requirements/FEATURE-001/mockups/main-dashboard.html
docs/requirements/FEATURE-001/mockups/settings-panel.html
```

**Linking Mockups:**
1. Add mockup links to `docs/requirements/requirement-details.md` in "Linked Mockups" table
2. Add mockup links to each `docs/requirements/{FEATURE-ID}/specification.md` in "Linked Mockups" table

**Mockup Link Format:**
```markdown
## Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| main-dashboard | [main-dashboard.html](FEATURE-001/mockups/main-dashboard.html) |
| settings-panel | [settings-panel.html](FEATURE-001/mockups/settings-panel.html) |
```

**Rules:**
- If mockup_list is N/A or empty, skip this step
- Use relative paths from the document location
- Preserve original file extension when copying
- Create mockups folder only if mockup_list has items

---

### Step 2: Create/Update Requirement Summary

**Action:** Create or update `docs/requirements/requirement-details.md`

**File Structure:**
```markdown
# Requirement Summary

> Requirement ID: REQ-XXX  
> Created: MM-DD-YYYY  
> Last Updated: MM-DD-YYYY

## Overview
[Brief description of the requirement/epic, 2-3 paragraphs]

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-001 | User Authentication | v1.0 | JWT-based user authentication with login, logout, token refresh | None |
| FEATURE-002 | User Profile | v1.0 | User profile management and settings | FEATURE-001 |
| FEATURE-003 | Password Reset | v1.0 | Password reset functionality via email | FEATURE-001 |

---

## Feature Details

### FEATURE-001: User Authentication

**Version:** v1.0  
**Brief Description:** Implement JWT-based user authentication with login, logout, and token refresh capabilities

**Acceptance Criteria:**
- [ ] User can login with email/password
- [ ] User receives JWT token on successful login
- [ ] Token can be refreshed before expiration
- [ ] User can logout and invalidate token
- [ ] Invalid credentials return appropriate error

**Dependencies:**
- None

**Technical Considerations:**
- JWT token expiration: 1 hour
- Refresh token expiration: 7 days
- Password hashing: bcrypt with salt rounds = 10
- Rate limiting: Max 5 login attempts per minute

---

### FEATURE-002: User Profile
[Similar structure for each feature]

---

### FEATURE-003: Password Reset  
[Similar structure for each feature]

---
```

**Feature Details Template (for each feature):**
```markdown
### {FEATURE-ID}: {Feature Title}

**Version:** v{X.Y}  
**Brief Description:** [1-2 sentence description]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Dependencies:**
- {FEATURE-ID}: [Why needed]
- None (if no dependencies)

**Technical Considerations:**
- [Key technical decisions or constraints]
- [Performance requirements]
- [Security considerations]
```

**Rules:**
- Keep brief description under 50 words
- List 3-7 acceptance criteria per feature
- Note dependencies using Feature IDs
- Technical considerations are hints for design

---

### Step 3: Call Feature Board Management

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

**Output:** Features created on docs/requirements/features.md with status "Planned"

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | `docs/requirements/requirement-details.md` created/updated with feature list | Yes |
| 2 | All features have detailed sections in requirement-details.md | Yes |
| 3 | Feature board updated via feature-board-management skill | Yes |
| 4 | All features have status "Planned" on feature board | Yes |
| 5 | If mockup_list provided: mockups copied to `docs/requirements/{FEATURE-ID}/mockups/` | Conditional |
| 6 | If mockup_list provided: Linked Mockups section updated in requirement-details.md and specification.md | Conditional |

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

### Common Dependency Patterns

**Sequential Dependencies:**
```
FEATURE-001: User Authentication (no deps)
FEATURE-002: User Profile (depends on FEATURE-001)
FEATURE-003: User Settings (depends on FEATURE-002)
```

**Parallel with Shared Dependency:**
```
FEATURE-001: Database Layer (no deps)
FEATURE-002: User Service (depends on FEATURE-001)
FEATURE-003: Product Service (depends on FEATURE-001)
```

**Multiple Dependencies:**
```
FEATURE-001: Authentication (no deps)
FEATURE-002: Authorization (no deps)
FEATURE-003: Admin Panel (depends on FEATURE-001, FEATURE-002)
```

### Dependency Rules

1. **No Circular Dependencies** - A cannot depend on B if B depends on A
2. **Foundation First** - Core/shared features have no dependencies
3. **Clear Reason** - Document why dependency exists
4. **Minimal Dependencies** - Only list direct dependencies

---

## Best Practices

### Feature Sizing

**Too Large (Split):**
- "Complete E-Commerce System" → Split into Cart, Payment, Shipping, etc.
- "User Management" → Split into Registration, Profile, Settings, etc.

**Good Size:**
- "Shopping Cart Management"
- "Payment Processing with Stripe"
- "Email Notification System"

**Too Small (Combine):**
- "Add to Cart Button" → Part of Shopping Cart feature
- "Validate Email Format" → Part of User Registration feature

### Feature Naming

**Good Names:**
- Specific: "JWT Authentication" not "Login"
- Action-oriented: "User Profile Management" not "User Profile"
- Technology-agnostic (usually): "Payment Processing" not "Stripe Integration"

**Bad Names:**
- Too vague: "User Stuff", "Main Feature"
- Too technical: "REST API Controller Layer"
- Too broad: "Everything Users Need"

### Version Numbering

- Start with v1.0 for new features
- Use v1.1, v1.2 for minor enhancements
- Use v2.0 for major redesigns
- Most breakdown features will be v1.0

---

## Integration with Feature Board Management

This skill **MUST** call the feature-board-management skill to create features on the board. This integration:

1. **Creates centralized tracking** - Single source of truth at docs/requirements/features.md
2. **Initializes status** - All features start with status "Planned"
3. **Enables queries** - Other skills can query feature board for Feature Data Model
4. **Supports lifecycle** - Board tracks features through all phases

**See:** `skills/feature-stage+feature-board-management/SKILL.md` for operation details

---

## Notes

- No longer create individual docs/requirements/FEATURE-XXX/feature.md files
- All features consolidated in requirement-details.md
- Feature board (features.md) is the status tracking system
- Feature specifications created later during Feature Refinement task
- Keep feature descriptions concise (50 words max) in the table
- More details go in the feature details section
