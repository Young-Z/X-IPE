# Feature Breakdown Guidelines Reference

This document contains detailed guidelines, examples, and rules for feature breakdown. Referenced from SKILL.md.

---

## Feature Sizing Guidelines

### Too Large (Split)

Examples of features that need splitting:
- "Complete E-Commerce System" → Split into Cart, Payment, Shipping, etc.
- "User Management" → Split into Registration, Profile, Settings, etc.
- "Full Admin Dashboard" → Split into User Admin, Content Admin, Analytics, etc.

### Good Size

Features appropriately scoped:
- "Shopping Cart Management"
- "Payment Processing with Stripe"
- "Email Notification System"
- "User Profile Management"
- "JWT Authentication"

### Too Small (Combine)

Features that should be combined:
- "Add to Cart Button" → Part of Shopping Cart feature
- "Validate Email Format" → Part of User Registration feature
- "Display Error Message" → Part of Form Validation feature

---

## Feature ID Assignment Rules

### ID Format

```
FEATURE-{NNN}
```

Where NNN is a zero-padded 3-digit number (001, 002, etc.)

### Assignment Rules

1. **Sequential Assignment** - IDs assigned in order of creation
2. **No Gaps** - Do not skip numbers
3. **No Reuse** - Deleted features keep their IDs
4. **Part-Specific Ranges** - When using parts, each part covers a range:
   - Part 1: FEATURE-001 to FEATURE-011
   - Part 2: FEATURE-012 to FEATURE-017
   - etc.

### Continuation Numbering

When adding features to an existing set:
```
1. Query feature board for highest existing FEATURE-XXX
2. Start new features at next number
3. Example: If FEATURE-011 exists, next is FEATURE-012
```

---

## Priority Matrix

### Priority Levels

| Priority | Description | Typical Features |
|----------|-------------|------------------|
| P0 (Critical) | MVP must-have | Core loop, auth, primary workflow |
| P1 (High) | Important for launch | Secondary workflows, error handling |
| P2 (Medium) | Nice to have | Convenience features, polish |
| P3 (Low) | Future consideration | Advanced features, optimizations |

### Priority Assignment Criteria

1. **User Impact** - How many users affected? How severely?
2. **Business Value** - Revenue, retention, or growth impact
3. **Technical Risk** - Complex features may need early start
4. **Dependencies** - Features blocking others get higher priority

---

## Feature Naming Conventions

### Good Names

- **Specific:** "JWT Authentication" not "Login"
- **Action-oriented:** "User Profile Management" not "User Profile"
- **Technology-agnostic (usually):** "Payment Processing" not "Stripe Integration"
- **Clear scope:** "Order History Display" not "Orders"

### Bad Names

- **Too vague:** "User Stuff", "Main Feature"
- **Too technical:** "REST API Controller Layer"
- **Too broad:** "Everything Users Need"
- **Ambiguous:** "Processing", "Handler", "Manager"

---

## Version Numbering

| Version | When to Use |
|---------|-------------|
| v1.0 | Initial feature implementation |
| v1.1, v1.2 | Minor enhancements, bug fixes |
| v2.0 | Major redesign or rewrite |

**Note:** Most breakdown features will be v1.0.

---

## Feature Dependency Patterns

### Sequential Dependencies

```
FEATURE-001: User Authentication (no deps)
    └── FEATURE-002: User Profile (depends on FEATURE-001)
            └── FEATURE-003: User Settings (depends on FEATURE-002)
```

### Parallel with Shared Dependency

```
                    ┌── FEATURE-002: User Service (depends on FEATURE-001)
FEATURE-001: Database Layer ──┤
                    └── FEATURE-003: Product Service (depends on FEATURE-001)
```

### Multiple Dependencies

```
FEATURE-001: Authentication (no deps) ──┐
                                        ├── FEATURE-003: Admin Panel
FEATURE-002: Authorization (no deps) ───┘
```

### Dependency Rules

1. **No Circular Dependencies** - A cannot depend on B if B depends on A
2. **Foundation First** - Core/shared features have no dependencies
3. **Clear Reason** - Document why dependency exists
4. **Minimal Dependencies** - Only list direct dependencies, not transitive
5. **DAG Structure** - Dependency graph must be a Directed Acyclic Graph

---

## Mockup Processing Details

### Auto-Detection Procedure

```
1. IF mockup_list is NOT provided or empty:
   a. Check if requirement came from an Idea (look for idea folder reference)
   b. IF idea folder exists:
      - Scan: x-ipe-docs/ideas/{idea-folder}/mockups/
      - IF mockups found → Auto-populate mockup_list from found files
      - Notify: "Found {N} mockups in idea folder, processing..."
   
2. IF mockup_list is STILL empty after auto-detection:
   - Log: "No mockups found - skipping mockup processing"
   - Proceed to Step 3
```

### File Operations Example

```yaml
# Input mockup_list
mockup_list:
  - mockup_name: "main-dashboard"
    mockup_list: "x-ipe-docs/ideas/Draft Idea - 01232026/mockup.html"
  - mockup_name: "settings-panel"
    mockup_list: "x-ipe-docs/ideas/Draft Idea - 01232026/mockups/settings.html"

# Result: Files created
x-ipe-docs/requirements/FEATURE-001/mockups/main-dashboard.html
x-ipe-docs/requirements/FEATURE-001/mockups/settings-panel.html
```

### Linking Mockups in Documents

**Location 1:** `x-ipe-docs/requirements/requirement-details.md`

**Location 2:** `x-ipe-docs/requirements/{FEATURE-ID}/specification.md`

**Format:**
```markdown
## Linked Mockups

| Mockup Function Name | Mockup List |
|---------------------|-------------|
| main-dashboard | [main-dashboard.html](FEATURE-001/mockups/main-dashboard.html) |
| settings-panel | [settings-panel.html](FEATURE-001/mockups/settings-panel.html) |
```

### Mockup Rules

- If mockup_list is N/A or empty, skip mockup processing
- Use relative paths from the document location
- Preserve original file extension when copying
- Create mockups folder only if mockup_list has items

---

## Part File Management

### When Parts Exist

| Action | Target |
|--------|--------|
| Read requirements | Current active part (highest number) |
| Write Feature List | Current active part |
| Update Index | requirement-details-index.md |

### Part File Structure

```markdown
# Requirement Details - Part {X}

> Continued from: [requirement-details-part-{X-1}.md](requirement-details-part-{X-1}.md)  
> Created: MM-DD-YYYY

---

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-012 | Design Themes | v1.0 | Theme folder structure | FEATURE-011 |

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup List |
|---------------------|---------|-------------|
| themes-toolbox | FEATURE-012 | [themes-toolbox.html](FEATURE-012/mockups/themes-toolbox.html) |

---

## Feature Details (Continued)

### FEATURE-012: Design Themes
[Feature details...]
```

### Index File Structure

```markdown
# Requirement Details Index

> Last Updated: MM-DD-YYYY

## Parts Overview

| Part | File | Features Covered | Lines |
|------|------|------------------|-------|
| 1 | [Part 1](requirement-details-part-1.md) | FEATURE-001 to FEATURE-011 | ~420 |
| 2 | [Part 2](requirement-details-part-2.md) | FEATURE-012 to FEATURE-017 | ~415 |
```

**⚠️ IMPORTANT:** Index file contains ONLY Parts Overview table. NO Feature List in index - each part has its own.

---

## Feature Details Template

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

### Template Rules

- Keep brief description under 50 words
- List 3-7 acceptance criteria per feature
- Note dependencies using Feature IDs
- Technical considerations are hints for design

---

## Integration with Feature Board Management

This skill **MUST** call the feature-board-management skill to create features on the board.

### Why Integration Matters

1. **Creates centralized tracking** - Single source of truth at x-ipe-docs/requirements/features.md
2. **Initializes status** - All features start with status "Planned"
3. **Enables queries** - Other skills can query feature board for Feature Data Model
4. **Supports lifecycle** - Board tracks features through all phases

### Call Format

```
CALL feature-stage+feature-board-management skill:
  operation: create_or_update_features
  features:
    - feature_id: FEATURE-001
      title: User Authentication
      version: v1.0
      description: JWT-based user authentication
      dependencies: []
    - feature_id: FEATURE-002
      title: User Profile  
      version: v1.0
      description: User profile management
      dependencies: [FEATURE-001]
```

**See:** `skills/feature-stage+feature-board-management/SKILL.md` for full operation details
