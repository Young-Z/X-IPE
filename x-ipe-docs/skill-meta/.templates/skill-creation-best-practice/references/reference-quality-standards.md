# Reference: Quality Standards

Detailed quality reference for skill creation including importance keywords, common mistakes, and exclusions.

## Importance Keywords

```yaml
importance_keywords:
  status_symbols:
    description: Keep for human readability in boards/tracking
    symbols:
      ✅: Complete
      🔄: In progress
      ⏳: Pending
      🚫: Blocked
      ⏸️: Deferred
      ❌: Cancelled
      
  importance_keywords:
    description: Use instead of symbols for importance signals in skill content
    keywords:
      BLOCKING: 
        meaning: Must not skip, halts execution
        replaces: "⛔"
      CRITICAL:
        meaning: High priority, affects correctness
        replaces: "⚠️ 🔴"
      MANDATORY:
        meaning: Required, continue with warning if missing
        replaces: "⚠️"
      REQUIRED:
        meaning: Needed for completion
        replaces: "✅ (as requirement)"
      OPTIONAL:
        meaning: Can skip without impact
        replaces: "🟢"
```

## Common Mistakes (Anti-Patterns)

```yaml
anti_patterns:
  - pattern: Missing DoR/DoD
    reason: No clear entry/exit criteria
    fix: Add entry/exit criteria tables
    
  - pattern: Vague description in frontmatter
    reason: Agent can't determine when to trigger skill
    fix: Be specific about triggers in description
    
  - pattern: No blocking rules
    reason: Critical rules may be skipped
    fix: Add BLOCKING: rules to Execution Flow
    
  - pattern: Missing skill prerequisite
    reason: Agent may start without required context
    fix: Add Important Notes section
    
  - pattern: Examples inline in SKILL.md
    reason: Bloats context when examples not needed
    fix: Move to references/examples.md
    
  - pattern: SKILL.md > 500 lines
    reason: Exceeds recommended token budget
    fix: Split into reference files
    
  - pattern: Sections out of order
    reason: Inconsistent structure confuses agent
    fix: Reorder to match template
    
  - pattern: Using ⚠️/⛔ for importance
    reason: Agents pattern-match keywords better
    fix: Use BLOCKING:, CRITICAL:, MANDATORY:
    
  - pattern: Data models as prose
    reason: Agents parse structured data better
    fix: Use YAML blocks with explicit types
    
  - pattern: Complex skill without sub-agents
    reason: Missing parallelization opportunity
    fix: Consider DAG workflow decomposition
    
  - pattern: Wrong workflow pattern
    reason: Using simple YAML for complex procedures loses clarity
    fix: Match pattern to workflow complexity (see Pattern Selection Guide)
    
  - pattern: "When to Use" in body
    reason: Body only loaded after triggering
    fix: Put trigger info in frontmatter description
```

## What NOT to Include

```yaml
excluded_files:
  description: A skill should contain ONLY essential files
  do_not_create:
    - README.md
    - INSTALLATION_GUIDE.md
    - QUICK_REFERENCE.md
    - CHANGELOG.md
    - Setup/testing procedures
    - User-facing documentation
    
  rationale: |
    Skill is for AI Agent to learn and execute, not for human onboarding.
    Auxiliary documentation adds clutter and wastes context tokens.
```

## Quick Reference: Keyword Usage

| Keyword | When to Use | Example |
|---------|-------------|---------|
| `BLOCKING:` | Must halt if violated | `BLOCKING: Do not proceed without approval` |
| `CRITICAL:` | High priority warning | `CRITICAL: Backup data before migration` |
| `MANDATORY:` | Required but can warn | `MANDATORY: Include test coverage` |
| `REQUIRED:` | Needed for completion | `REQUIRED: Feature ID must exist` |
| `OPTIONAL:` | Can skip safely | `OPTIONAL: Add inline comments` |

## Quick Reference: Symbol Usage

| Context | Use Symbols? | Reason |
|---------|--------------|--------|
| Task boards | ✅ Yes | Human readability |
| Status tracking | ✅ Yes | Visual scanning |
| Skill instructions | ❌ No | Keywords more reliable |
| Importance signals | ❌ No | Agents pattern-match better |
