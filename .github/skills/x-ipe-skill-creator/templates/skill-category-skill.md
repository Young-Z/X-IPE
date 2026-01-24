# Skill Category Template

Use this template when creating a skill that manages boards or category-level data.

---

```markdown
---
name: {category}+{operation-name}
description: {Brief description of what this skill manages}. {When to use}. Provides operations for {operation types}.
---

# {Skill Name}

## Purpose

AI Agents follow this skill to {what the skill manages}. This skill {mandatory/optional context}.

**Operations:**
1. **{Operation 1}** - {Brief description}
2. **{Operation 2}** - {Brief description}
3. **{Operation 3}** - {Brief description}
4. **{Operation 4}** - {Brief description}

---

## Important Notes

**Important:** {Any critical notes about skill usage}

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Input: {Data Model Name}

This skill receives the {Data Model Name} from {source}:

```yaml
{DataModel}:
  # Core fields
  {field_1}: {type/description}
  {field_2}: {type/description}
  {field_3}: {type/description}
  
  # Execution fields
  {field_4}: {type/description}
  {field_5}: {type/description}
  
  # Control fields
  {field_6}: {type/description}
```

---

## {Entity} States

| State | Terminal? | Description |
|-------|-----------|-------------|
| `{state_1}` | No | {Description} |
| `{state_2}` | No | {Description} |
| `{state_3}` | No | {Description} |
| `{state_4}` | Yes | {Description} |
| `{state_5}` | Yes | {Description} |

### Valid Transitions

```
{state_1} → {state_2}
{state_2} → {state_4} | {state_3} | {state_5}
{state_3} → {state_2}
```

---

## {Board/Entity} Operations

### Operation 1: {Operation Name}

**When:** {Trigger condition}
**Then:** {What happens}

```
1. {Step 1}
2. {Step 2}
3. {Step 3}
4. Return {result}
```

### Operation 2: {Operation Name}

**When:** {Trigger condition}
**Then:** {What happens}

```
Input: {Input description}

Process:
1. {Step 1}
2. {Step 2}
3. {Step 3}
```

### Operation 3: {Operation Name}

**When:** {Trigger condition}
**Then:** {What happens}

```
Input: {Input description}

Process:
1. {Step 1}
2. IF {condition}:
   → {Action}
3. {Step 3}
4. Update {what}
```

### Operation 4: {Operation Name}

**When:** {Trigger condition}
**Then:** {What happens}

```
Query Types:
1. By {field_1}: {Description}
2. By {field_2}: {Description}
3. By {field_3}: {Description}

Return: {What is returned}
```

### Operation 5: Validate {Entity} Integrity

**When:** ANY operation is performed
**Then:** Validate and fix issues

```
Process:
1. Scan {section 1}:
   FOR each {item} in {section}:
     IF {condition}:
       → {Fix action}
       → Log: "{message}"

2. Scan {section 2}:
   FOR each {item} in {section}:
     IF {condition}:
       → {Fix action}

3. Reconcile {stats/counts}:
   - {Check 1}
   - {Check 2}

4. Return validation report
```

**⚠️ MANDATORY:** This operation runs automatically as the final step of ALL other operations.

---

## {Board/Data} Sections

The {board/data store} has these sections:

### {Section 1 Name}
```yaml
{field}: {default value}
```

### {Section 2 Name}
| Column 1 | Column 2 | Column 3 | Column 4 |
|----------|----------|----------|----------|

Contains: {What goes here}
⛔ **{Constraint}**

### {Section 3 Name}
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|

Contains: {What goes here}
✅ **{Requirement}**

---

## Status Symbols

| Status | Symbol | Description |
|--------|--------|-------------|
| {status_1} | {emoji} | {Description} |
| {status_2} | {emoji} | {Description} |
| {status_3} | {emoji} | {Description} |
| {status_4} | {emoji} | {Description} |

---

## Templates

- `templates/{template-1}.md` - {Description}
- `templates/{template-2}.yaml` - {Description}

---

## Examples

### Example 1: {Example Name}

**Request:** "{Example request}"

```
Step 1: {Action}
→ {Detail}

Step 2: {Action}
→ {Detail}

Step 3: {Action}
→ {Detail}

Result: {Outcome}
```

### Example 2: {Example Name}

**Request:** "{Example request}"

```
Step 1: {Action}
→ {Detail}

Step 2: {Action}
→ {Detail}

Result: {Outcome}
```

### Example 3: {Example Name}

**Scenario:** {Scenario description}

```
Initial State:
  {Section}:
    - {Item 1}
    - {Item 2}

Step 1: {Action}
→ {Result}

Step 2: {Action}
→ {Result}

Final State:
  {Section}:
    - {Item 1}
    - {Item 2}
```
```

---

## Template Usage Notes

### Required Sections (Must Include)

1. **Frontmatter** - name (category+operation format) and description
2. **Purpose** - what skill manages with operation list
3. **Important Notes** - critical usage notes
4. **Input Data Model** - YAML schema of input
5. **States** - valid states and transitions
6. **Operations** - all CRUD operations
7. **Board/Data Sections** - structure of managed data
8. **Status Symbols** - visual indicators
9. **Templates** - reference to template files
10. **Examples** - at least 2-3 concrete examples

### Optional Sections (Add if Needed)

- **Legend** - if categories or types need explanation
- **Integration** - if other skills call this skill
- **Notes** - additional guidance

### Naming Convention

Skill category skills use compound names:
- `{category}+{operation-name}`
- Examples:
  - `feature-stage+feature-board-management`
  - `requirement-stage+requirement-board-management`
  - `ideation-stage+ideation-board-management`

For standalone board management:
- `{entity}-board-management`
- Example: `task-board-management`
