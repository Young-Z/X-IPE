# Skill Standards Reflection

A structured analysis of the Anthropic Skill Creator framework standards that EVERY skill should follow.

---

## 1. Core Principles

### 1.1 Concise is Key

**The most critical principle.** The context window is a public good shared with:
- System prompt
- Conversation history
- Other skills' metadata
- User requests

**Key Questions to Ask:**
- "Does Claude really need this explanation?"
- "Does this paragraph justify its token cost?"

**Default Assumption:** Claude is already very smart. Only add context Claude doesn't already have.

**Best Practice:** Prefer concise examples over verbose explanations.

### 1.2 Set Appropriate Degrees of Freedom

Match specificity to task fragility and variability:

| Freedom Level | When to Use | Implementation |
|---------------|-------------|----------------|
| **High** | Multiple approaches valid, context-dependent decisions | Text-based instructions |
| **Medium** | Preferred pattern exists, some variation acceptable | Pseudocode or scripts with parameters |
| **Low** | Operations fragile, consistency critical, specific sequence required | Specific scripts, few parameters |

**Analogy:** A narrow bridge with cliffs needs specific guardrails (low freedom); an open field allows many routes (high freedom).

### 1.3 Progressive Disclosure

Three-level loading system to manage context efficiently:

1. **Level 1: Metadata** (~100 words) - Always in context
2. **Level 2: SKILL.md body** (<5k words) - When skill triggers
3. **Level 3: Bundled resources** (Unlimited) - As needed by Claude

### 1.4 Single Source of Truth

Information should live in either SKILL.md OR references files, **never both**. Avoid duplication.

---

## 2. Skill Anatomy

### 2.1 Required Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code
    ├── references/       - Documentation for context loading
    └── assets/           - Files used in output
```

### 2.2 SKILL.md Requirements

#### Frontmatter (YAML)

**Required fields:**
- `name`: The skill name
- `description`: Primary triggering mechanism - MUST include:
  - What the skill does
  - Specific triggers/contexts for when to use it
  - All "when to use" information (NOT in body)

**No other fields allowed in frontmatter.**

#### Body (Markdown)

- Instructions and guidance for using the skill
- Only loaded AFTER the skill triggers
- Use **imperative/infinitive form** in writing
- Keep under 500 lines

### 2.3 Bundled Resources

| Folder | Purpose | When to Use | Benefits |
|--------|---------|-------------|----------|
| `scripts/` | Executable code (Python/Bash) | Same code rewritten repeatedly, deterministic reliability needed | Token efficient, deterministic |
| `references/` | Documentation for Claude to reference | Schemas, APIs, domain knowledge, policies, detailed guides | Keeps SKILL.md lean, loaded on-demand |
| `assets/` | Files used in output (not loaded into context) | Templates, images, icons, fonts, boilerplate | Separates output resources from docs |

### 2.4 What NOT to Include

**Do NOT create extraneous files:**
- ❌ README.md
- ❌ INSTALLATION_GUIDE.md
- ❌ QUICK_REFERENCE.md
- ❌ CHANGELOG.md
- ❌ Setup/testing procedures
- ❌ User-facing documentation
- ❌ Process documentation about skill creation

**Only include:** Information needed for an AI agent to do the job at hand.

---

## 3. Progressive Disclosure Rules

### 3.1 The 500-Line Limit

- Keep SKILL.md body to essentials and **under 500 lines**
- Split content into separate files when approaching this limit
- Always reference split files from SKILL.md with clear descriptions of when to read them

### 3.2 Reference File Guidelines

| Guideline | Rule |
|-----------|------|
| Nesting depth | Keep references ONE level deep from SKILL.md |
| Long files (>100 lines) | Include table of contents at top |
| Large files (>10k words) | Include grep search patterns in SKILL.md |
| Linking | All reference files should link directly from SKILL.md |

### 3.3 Progressive Disclosure Patterns

#### Pattern 1: High-Level Guide with References

```markdown
# PDF Processing

## Quick start
Extract text with pdfplumber:
[code example]

## Advanced features
- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
```

**Use when:** Skill has core workflow + optional advanced features

#### Pattern 2: Domain-Specific Organization

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── references/
    ├── finance.md (revenue, billing)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

**Use when:** Skill has multiple domains or supports multiple frameworks/variants

**Key benefit:** Claude loads only relevant domain file (e.g., sales.md for sales questions)

#### Pattern 3: Conditional Details

```markdown
# DOCX Processing

## Creating documents
Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents
For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

**Use when:** Basic content is in SKILL.md, advanced content is conditional

---

## 4. Quality Checklist

### Frontmatter Checklist
- [ ] Has `name` field
- [ ] Has `description` field
- [ ] Description includes what skill does
- [ ] Description includes when to use/trigger conditions
- [ ] No extra fields in frontmatter
- [ ] "When to use" info is in description, NOT in body

### Body Checklist
- [ ] Under 500 lines
- [ ] Uses imperative/infinitive form
- [ ] Only contains info Claude doesn't already know
- [ ] No duplicate info (between SKILL.md and references)
- [ ] Each paragraph justifies its token cost
- [ ] Prefers examples over verbose explanations

### Structure Checklist
- [ ] SKILL.md exists and is required
- [ ] No extraneous documentation files (README, CHANGELOG, etc.)
- [ ] References are one level deep (no nested references)
- [ ] Reference files >100 lines have table of contents
- [ ] All bundled resources are referenced in SKILL.md
- [ ] Clear descriptions of when to read each reference file

### Degrees of Freedom Checklist
- [ ] High freedom tasks use text-based instructions
- [ ] Medium freedom tasks use pseudocode/parameterized scripts
- [ ] Low freedom tasks use specific scripts with few parameters
- [ ] Freedom level matches task fragility

### Scripts Checklist
- [ ] Scripts are tested and work correctly
- [ ] Scripts provide deterministic reliability
- [ ] Scripts avoid token cost of rewriting code

### Progressive Disclosure Checklist
- [ ] Skill supports multiple variations → Core workflow in SKILL.md, variants in references
- [ ] Large reference files include grep patterns
- [ ] Claude can navigate to specific content without loading everything

---

## 5. Anti-Patterns to Avoid

### 5.1 Context Window Abuse

| Anti-Pattern | Why It's Wrong | Fix |
|--------------|----------------|-----|
| Verbose explanations | Wastes context tokens | Use concise examples instead |
| Duplicating info in SKILL.md and references | Double token cost | Single source of truth |
| "When to Use" section in body | Body loads AFTER trigger decision | Put in frontmatter description |
| Loading all references upfront | Unnecessary context bloat | Progressive disclosure |

### 5.2 Structure Violations

| Anti-Pattern | Why It's Wrong | Fix |
|--------------|----------------|-----|
| README.md in skill folder | Extraneous documentation | Delete it |
| CHANGELOG.md | Process documentation, not for agent | Delete it |
| Nested references (ref → ref → ref) | Hard to navigate, complex loading | Keep one level deep |
| SKILL.md > 500 lines | Context bloat | Split into references |

### 5.3 Degrees of Freedom Mismatches

| Anti-Pattern | Why It's Wrong | Fix |
|--------------|----------------|-----|
| Script for high-freedom task | Over-constrains valid approaches | Use text instructions |
| Text instructions for fragile operation | Inconsistent, error-prone results | Use specific script |
| No parameters in scripts | Can't adapt to variations | Add appropriate parameters |

### 5.4 Description Failures

| Anti-Pattern | Why It's Wrong | Fix |
|--------------|----------------|-----|
| Vague description | Skill won't trigger correctly | Be specific about triggers |
| Missing "when to use" in description | Claude can't decide when to use | Include all trigger conditions |
| Description only says what, not when | Incomplete triggering info | Add specific contexts |

### 5.5 Reference File Mistakes

| Anti-Pattern | Why It's Wrong | Fix |
|--------------|----------------|-----|
| No ToC in long reference files | Claude can't preview scope | Add table of contents |
| References not linked from SKILL.md | Claude doesn't know they exist | Add clear links with usage guidance |
| Large files without grep patterns | Hard to search efficiently | Include search patterns |

---

## Summary

The Anthropic Skill Creator framework emphasizes:

1. **Minimal context usage** - Every token must justify its cost
2. **Smart progressive disclosure** - Load only what's needed, when needed
3. **Appropriate constraint levels** - Match freedom to task fragility
4. **Clean structure** - No extraneous files, single source of truth
5. **Effective triggering** - Description is the key to skill activation

Skills are "onboarding guides" that transform Claude from general-purpose to specialized. They should contain only what's needed for an AI agent to do the job - nothing more, nothing less.
