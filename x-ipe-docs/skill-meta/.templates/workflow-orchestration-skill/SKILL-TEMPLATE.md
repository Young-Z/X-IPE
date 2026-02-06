---
name: {skill-name}
description: {Brief workflow purpose. Triggers on "{trigger1}", "{trigger2}". Provides {N}-step workflow for {goal}.}
---

<!-- ToC recommended for implementations >100 lines -->

# {Skill Title}

## Prerequisites
- {Required skill, state, or artifact that must exist before workflow starts}

---

## Data Model

### {Entity} Structure
```yaml
{entity}:
  {entity}_id: {PREFIX}-XXX
  {entity}_type: <Type from Registry>
  description: <≤50 words>
  category: <derived from type> | Standalone
  status: {state1} | {state2} | {state3}
  next_{entity}_type: <Type> | null
  require_human_review: true | false
  auto_proceed: true | false
  output_links:                    # List of artifact references
    - type: file | url | artifact
      path: <relative path or URL>
      description: <optional, ≤20 words>
  change_summary: <≤100 words> | null
```

### State Transitions
| State | Terminal | Next States |
|-------|----------|-------------|
| `{state1}` | No | → `{state2}` |
| `{state2}` | No | → `{state3}` or → `{state1}` |
| `{state3}` | Yes | END |

---

## Workflow Lifecycle

| Step | Name | Action | Output | Next |
|------|------|--------|--------|------|
| 1 | {Planning} | {action} | {entity} record | → 2 |
| 2 | {Validation} | Gate check | Pass/Fail | → 3 or STOP |
| 3 | {Execution} | Load sub-skill | Updated {entity} | → 4 |
| 4 | {Routing} | Check auto_proceed | Loop or END | → 2 or END |

> ⚠️ **CRITICAL:** Steps are BLOCKING. Never skip. Gate failures STOP workflow.

---

### Step 1: {Planning}
**Trigger:** Human request matching pattern in Types Registry

**Process:**
1. Match request to `{entity}_type` via Registry
2. Create {entity} record (pre-populate from context if available)
3. Set `status = {state1}`, derive category

**Output:** Complete {entity} record

---

### Step 2: {Validation}
```
CHECK {entity}_id exists         → FAIL: "Missing {entity} ID"
CHECK {entity}_type in Registry  → FAIL: "Unknown type: {type}"
CHECK required_artifacts exist   → FAIL: "Missing: {artifact}"

IF any fails → status=blocked, STOP
ELSE → status={state2}, proceed
```

---

### Step 3: {Execution}
1. Load skill from `Registry[{entity}_type]`
2. Pass {entity} to skill, execute procedure
3. Merge output: `status`, `next_{entity}_type`, `require_human_review`, `output_links`

**Sub-Skill Output Contract:**
```yaml
status: <new status>
next_{entity}_type: <Type> | null
require_human_review: true | false
output_links:
  - type: file
    path: "path/to/artifact.md"
```

---

### Step 4: {Routing}
```
IF require_human_review = true → STOP (await approval)
ELSE IF auto_proceed AND next_{entity}_type != null:
   → {entity}_type = next_{entity}_type
   → GOTO Step 2
ELSE → status={state3}, END
```

---

## Types Registry

| Type | Pattern | Skill | Category | Next Type | Human Review |
|------|---------|-------|----------|-----------|--------------|
| {Type1} | "keyword1", "keyword2" | `{skill-1}` | {category-a} | {Type2} | No |
| {Type2} | "keyword3" | `{skill-2}` | {category-a} | - | Yes |
| {Type3} | "keyword4" | `{skill-3}` | Standalone | - | Yes |

> **Category derivation:** Types in same category form a chain (Entry → Exit). Standalone types are self-contained.

---

## Reference Files
<!-- Add when SKILL.md >100 lines or complex examples needed -->
<!-- 
- `references/examples.md` - Extended workflow examples
- `references/edge-cases.md` - Error handling scenarios
-->

---

## Definition of Done (Optional)
<!-- Uncomment and customize if workflow has specific completion criteria
- [ ] All {entity} records have terminal status
- [ ] All output_links are valid and accessible
- [ ] Human review completed where required
-->

---

## Agent Output

```
✅ {Workflow} Complete               ⛔ {Workflow} Blocked
- {Entity}: {id}                     - {Entity}: {id}
- Status: {status}                   - Step: {N}
- Outputs: {links}                   - Reason: {message}
```
