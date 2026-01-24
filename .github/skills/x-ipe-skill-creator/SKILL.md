---
name: x-ipe-skill-creator
description: Guide for creating effective X-IPE skills. Use when creating a new skill (or updating an existing skill) for the X-IPE framework, including task type skills, tool skills, and skill category skills. Triggers on requests like "create skill", "new skill", "add task type skill", "create tool skill", "create category skill".
---

# X-IPE Skill Creator

This skill provides guidance for creating effective X-IPE skills.

## About X-IPE Skills

Skills are modular, self-contained packages that extend AI Agent capabilities by providing specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific domains or tasks—they transform an AI Agent from a general-purpose assistant into a specialized agent equipped with procedural knowledge.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Project-specific knowledge, schemas, business logic
4. Bundled resources - Templates, references, and scripts for complex and repetitive tasks

### X-IPE Skill Types

| Type | Purpose | Naming Convention | Template |
|------|---------|-------------------|----------|
| Task Type | Development lifecycle workflows | `task-type-{name}` | [task-type-skill.md](templates/task-type-skill.md) |
| Tool Skill | Utility functions and tool integrations | `{tool-name}` | TBD |
| Skill Category | Board management and category-level operations | `{category}+{operation}` | [skill-category-skill.md](templates/skill-category-skill.md) |

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else AI Agent needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: AI Agent is already very smart.** Only add context AI Agent doesn't already have. Challenge each piece of information: "Does AI Agent really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of AI Agent as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation loaded into context as needed
    └── templates/        - Document templates for output
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields that AI Agent reads to determine when the skill gets used, thus it is very important to be clear and comprehensive in describing what the skill is, and when it should be used.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Benefits**: Token efficient, deterministic, may be executed without loading into context

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context.

- **When to include**: For documentation that AI Agent should reference while working
- **Use cases**: Detailed workflow guides, domain knowledge, API documentation
- **Benefits**: Keeps SKILL.md lean, loaded only when AI Agent determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md

##### Templates (`templates/`)

Document templates used for generating output files.

- **When to include**: When the skill produces standardized documents
- **Examples**: `templates/requirement-details.md`, `templates/task-board.md`
- **Benefits**: Consistent output format, easy to maintain

#### What to Not Include in a Skill

A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation including:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md

The skill should only contain the information needed for an AI agent to do the job at hand.

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<500 lines)
3. **Bundled resources** - As needed by AI Agent (unlimited)

Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit.

**Key principle:** When a skill supports multiple variations, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details into separate reference files.

#### ⚠️ Mandatory: Examples in References

**For Task Type Skills:** Examples MUST be placed in `references/examples.md`, NOT inline in SKILL.md.

```
skill-name/
├── SKILL.md                    # Core skill (<500 lines)
│   └── ## Example section → Link to references/examples.md
└── references/
    └── examples.md             # Detailed execution examples (MANDATORY)
```

**Why:** Examples are verbose (often 100+ lines each) and are only needed when learning the skill, not during every execution.

**SKILL.md Example section format:**
```markdown
## Example

See [references/examples.md](references/examples.md) for concrete execution examples.
```

## Skill Creation Process

Skill creation involves these steps:

1. Identify skill type (Task Type, Tool, or Skill Category)
2. Understand the skill with concrete examples
3. Plan reusable skill contents (scripts, references, templates)
4. Initialize the skill directory
5. Edit the skill (implement resources and write SKILL.md)
6. **Validate cross-references** (check if references need to be added/updated)
7. Iterate based on real usage

Follow these steps in order, skipping only if there is a clear reason why they are not applicable.

### Step 1: Identify Skill Type

Determine which type of X-IPE skill to create:

```
IF skill follows development lifecycle workflow → Task Type Skill
   Examples: requirement gathering, code implementation, bug fix
   
IF skill manages a board or category-level data → Skill Category Skill
   Examples: task-board-management, feature-board-management
   
IF skill provides utility functions or tool integrations → Tool Skill
   Examples: git-version-control, pdf-processor
```

### Step 2: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

Example questions to ask:
- "What functionality should this skill support?"
- "Can you give some examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"

Conclude this step when there is a clear sense of the functionality the skill should support.

### Step 3: Planning the Reusable Skill Contents

Analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and templates would be helpful when executing these workflows repeatedly

Example: When building a `task-type-requirement-gathering` skill:
1. Gathering requirements requires asking clarifying questions each time
2. A `templates/requirement-details.md` template would be helpful
3. Patterns for vague vs detailed requests should be documented

### Step 4: Initializing the Skill

Create the skill directory structure:

```bash
mkdir -p .github/skills/{skill-name}/{templates,references,scripts}
```

Then create SKILL.md using the appropriate template:

- **Task Type**: See [task-type-skill.md](templates/task-type-skill.md)
- **Skill Category**: See [skill-category-skill.md](templates/skill-category-skill.md)
- **Tool Skill**: TBD

### Step 5: Edit the Skill

When editing the skill, remember that it is being created for another instance of AI Agent to use. Include information that would be beneficial and non-obvious.

#### Learn Proven Design Patterns

Consult these helpful guides based on your skill's needs:

- **Multi-step processes**: See [references/workflows.md](references/workflows.md) for sequential workflows and conditional logic
- **Specific output formats**: See [references/output-patterns.md](references/output-patterns.md) for template and example patterns
- **Skill structure details**: See [references/skill-structure.md](references/skill-structure.md) for section guidelines

#### Use the Correct Template

Each skill type has required sections that MUST be included:

**Task Type Skills** (see [task-type-skill.md](templates/task-type-skill.md)):
- Purpose, Important Notes, Task Type Default Attributes
- Task Type Required Input Attributes, Skill/Task Completion Output
- Definition of Ready (DoR), Execution Flow, Execution Procedure
- Definition of Done (DoD), Patterns, Anti-Patterns, Example

**Skill Category Skills** (see [skill-category-skill.md](templates/skill-category-skill.md)):
- Purpose, Important Notes, Input Data Model
- States, Operations, Board Sections
- Status Symbols, Templates, Examples

**⚠️ STRICT: Section titles MUST match template exactly.** Do not rename, reorder, or merge sections. This ensures consistency across all X-IPE skills and enables automated validation.

#### Update SKILL.md

**Writing Guidelines:** Always use imperative/infinitive form.

##### Frontmatter

Write the YAML frontmatter with `name` and `description`:

- `name`: The skill name following naming conventions
- `description`: This is the primary triggering mechanism for your skill
  - Include both what the Skill does and specific triggers/contexts for when to use it
  - Include all "when to use" information here - Not in the body
  - Example: "Gather requirements from user requests and create requirement summary. Use when starting a new feature or receiving a new user request. Triggers on requests like 'new feature', 'add feature', 'I want to build'."

Do not include any other fields in YAML frontmatter.

##### Body

Write instructions for using the skill and its bundled resources following the appropriate template structure.

### Step 6: Validate Cross-References

**MANDATORY for all skill operations (create/update/validate).** Verify that external references to the skill are added or updated in these locations:

#### 6.1 Check `copilot-instructions.md`

For **Task Type Skills**, verify the Task Types Registry table:

| Check | Location | Action |
|-------|----------|--------|
| Skill exists in registry | `.github/copilot-instructions.md` → Task Types Registry table | Add row if missing |
| Skill name matches | `Skill` column | Update if renamed |
| Category is correct | `Category` column | Update if changed |
| Next Task is correct | `Next Task` column | Update if workflow changed |
| Human Review flag is set | `Human Review` column | Set Yes/No appropriately |

#### 6.2 Check `task-execution-guideline`

For **Task Type Skills**, verify the Category Derivation table:

| Check | Location | Action |
|-------|----------|--------|
| Skill exists in category mapping | `.github/skills/task-execution-guideline/SKILL.md` → Category Derivation table | Add to appropriate category row if missing |
| Category assignment is correct | Category column | Move to correct category if changed |

#### 6.3 Check Related Skills

Scan for skills that may need to reference the new/updated skill:

| Scenario | Check | Action |
|----------|-------|--------|
| Skill is part of a workflow | Skills with `next_task_type` pointing to this skill | Verify references are correct |
| Skill has prerequisites | Skills listed in DoR | Ensure bidirectional consistency |
| Skill produces artifacts | Skills that consume these artifacts | Add reference if missing |

#### 6.4 Cross-Reference Validation Checklist

```
□ copilot-instructions.md Task Types Registry (for Task Type skills)
□ task-execution-guideline Category Derivation table (for Task Type skills)
□ Related skills in same category (check workflow consistency)
□ Skills that reference this skill (grep for skill name in .github/skills/)
```

**Quick validation command:**
```bash
# Find all references to a skill
grep -r "skill-name" .github/skills/ .github/copilot-instructions.md
```

### Step 7: Iterate

After testing the skill, users may request improvements.

**Iteration workflow:**

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again

## References

- [templates/task-type-skill.md](templates/task-type-skill.md) - Task Type skill template
- [templates/skill-category-skill.md](templates/skill-category-skill.md) - Skill Category template
- [references/skill-structure.md](references/skill-structure.md) - Detailed structure guidelines
- [references/workflows.md](references/workflows.md) - Workflow design patterns
- [references/output-patterns.md](references/output-patterns.md) - Output format patterns
