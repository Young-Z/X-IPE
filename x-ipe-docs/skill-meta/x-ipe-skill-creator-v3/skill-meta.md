---
skill_name: x-ipe-skill-creator-v3
skill_type: meta_skill
version: 1.0.0
created_date: 2026-02-05
upgraded_from: x-ipe-skill-creator-v2
---

# Skill Meta: x-ipe-skill-creator-v3

## Overview

Guide for creating effective X-IPE skills with complete template coverage, sub-agent DAG workflow, and validation against skill-general-guidelines-v2. V3 adds workflow-orchestration and meta-skill templates (v2 only had 2 of 4 templates implemented), enforces >= 3 concrete examples, and strengthens keyword usage compliance.

## Key Improvements Over v2

| Area | v2 Issue | v3 Fix |
|------|----------|--------|
| Templates | 4 mentioned, only 2 exist | All 4 templates must exist and be validated |
| Examples | >= 2 examples | >= 3 concrete usage examples required |
| Keywords | Mentioned but not enforced | BLOCKING/CRITICAL/MANDATORY validation |
| Sub-agent workflow | Basic | Full DAG with model hints (haiku/sonnet) |

## Acceptance Criteria

### MUST (Required for pass)

- AC-M01: **Templates Complete** - All 4 template files exist in templates/ folder: task-type-skill.md, tool-skill.md, workflow-skill.md, meta-skill.md
- AC-M02: **Template Structure Valid** - Each template follows skill-general-guidelines-v2.md section order for its skill type
- AC-M03: **Examples Minimum** - At least 3 concrete usage examples documented in references/examples.md
- AC-M04: **Keyword Enforcement** - SKILL.md uses BLOCKING/CRITICAL/MANDATORY keywords (not emoji) for importance signals
- AC-M05: **Line Count Limit** - SKILL.md body stays under 500 lines
- AC-M06: **Frontmatter Valid** - YAML frontmatter has name (1-64 chars) and description (includes trigger phrases)
- AC-M07: **Sub-Agent DAG Defined** - Execution procedure defines parallel groups with merge points and model hints (haiku/sonnet)
- AC-M08: **Guidelines Reference** - BLOCKING reference to skill-general-guidelines-v2.md in Important Notes section
- AC-M09: **DoD Step Output Coverage** - Every step output in Execution Procedure has corresponding DoD checkpoint with `<step_output>` tag
- AC-M10: **Created Skill Step Output Coverage** - Every step output in created skill's Execution Procedure has corresponding DoD checkpoint

### SHOULD (80% pass rate needed)

- AC-S01: **Section Order Compliant** - SKILL.md follows cognitive flow: CONTEXT → DECISION → ACTION → VERIFY → REFERENCE
- AC-S02: **Progressive Disclosure** - Complex details delegated to references/ folder, not inline in SKILL.md
- AC-S03: **DoR/DoD XML Format** - Definition of Ready and Definition of Done use XML checkpoint format
- AC-S04: **Variable Syntax Consistent** - Uses {variable_name} pattern throughout procedures

### COULD (Optional)

- AC-C01: **Cross-Reference Validation** - Step 11 validates bidirectional references for task_type skills
- AC-C02: **Lesson Integration** - Skill update workflow checks lesson-learned.md for accumulated feedback
- AC-C03: **Cost Efficiency** - Sub-agent model hints prefer haiku for simple tasks, sonnet for complex

## Test Scenarios

### AC-M01: Templates Complete

```yaml
test:
  name: verify_all_templates_exist
  type: file_existence
  steps:
    - glob: ".github/skills/x-ipe-skill-creator-v3/templates/*.md"
    - assert: count == 4
    - assert: contains ["task-type-skill.md", "tool-skill.md", "workflow-skill.md", "meta-skill.md"]
  expected: All 4 template files present
```

### AC-M02: Template Structure Valid

```yaml
test:
  name: verify_template_section_order
  type: content_validation
  for_each_template:
    - read: template content
    - extract: section headers
    - validate: matches skill type section order from guidelines
  expected: Each template follows cognitive flow for its skill type
```

### AC-M03: Examples Minimum

```yaml
test:
  name: verify_examples_count
  type: content_validation
  steps:
    - read: "references/examples.md"
    - count: "## Example" headers or equivalent
    - assert: count >= 3
  expected: At least 3 distinct examples documented
```

### AC-M04: Keyword Enforcement

```yaml
test:
  name: verify_keyword_usage
  type: content_validation
  steps:
    - read: "SKILL.md"
    - grep: "BLOCKING:|CRITICAL:|MANDATORY:"
    - assert: count >= 1
    - grep: "⚠️|⛔|🔴|🟢"
    - assert: count == 0
  expected: Uses keywords, not emoji, for importance signals
```

### AC-M05: Line Count Limit

```yaml
test:
  name: verify_line_count
  type: file_metric
  steps:
    - read: "SKILL.md"
    - count: lines (excluding frontmatter)
    - assert: lines < 500
  expected: SKILL.md body under 500 lines
```

### AC-M06: Frontmatter Valid

```yaml
test:
  name: verify_frontmatter
  type: yaml_validation
  steps:
    - extract: YAML frontmatter from SKILL.md
    - assert: name field exists AND length 1-64 chars
    - assert: description field exists AND contains trigger phrase
  expected: Valid frontmatter with name and description
```

### AC-M07: Sub-Agent DAG Defined

```yaml
test:
  name: verify_subagent_dag
  type: content_validation
  steps:
    - read: "SKILL.md" execution procedure section
    - find: parallel_groups OR sub_agents definition
    - assert: contains merge_to OR "both complete"
    - find: model_hint OR "haiku|sonnet" reference
  expected: DAG workflow with parallel groups and model hints
```

### AC-M08: Guidelines Reference

```yaml
test:
  name: verify_guidelines_reference
  type: content_validation
  steps:
    - read: "SKILL.md"
    - grep: "BLOCKING.*skill-general-guidelines"
    - assert: count >= 1
  expected: BLOCKING reference to guidelines in Important Notes
```

### AC-M09: DoD Step Output Coverage

```yaml
test:
  name: verify_dod_step_output_coverage
  type: content_validation
  steps:
    - read: "SKILL.md"
    - extract: all <output> tags from Execution Procedure
    - extract: all <step_output> tags from DoD
    - compare: every step output has matching DoD checkpoint
    - assert: unmatched_outputs == 0
  expected: Every step output mapped to DoD checkpoint
```

### AC-M10: Created Skill Step Output Coverage

```yaml
test:
  name: verify_created_skill_step_output_coverage
  type: content_validation
  context: Run on skill being created, not skill-creator itself
  steps:
    - read: created skill SKILL.md
    - extract: all <output> tags from Execution Procedure
    - extract: all <step_output> tags from DoD
    - compare: every step output has matching DoD checkpoint
    - assert: unmatched_outputs == 0
  expected: Created skill has complete step output coverage in DoD
```

## Validation Matrix

| Criterion | Test Type | Automated | Human Review |
|-----------|-----------|-----------|--------------|
| AC-M01 | File existence | ✅ | - |
| AC-M02 | Structure validation | ✅ | - |
| AC-M03 | Content count | ✅ | - |
| AC-M04 | Pattern matching | ✅ | - |
| AC-M05 | Line count | ✅ | - |
| AC-M06 | YAML parsing | ✅ | - |
| AC-M07 | Pattern matching | ✅ | Quality review |
| AC-M08 | Pattern matching | ✅ | - |
| AC-M09 | Content comparison | ✅ | - |
| AC-M10 | Content comparison | ✅ | - |
| AC-S01-S04 | Content analysis | Partial | Quality review |
| AC-C01-C03 | Manual review | - | ✅ |

## Pass Criteria

```yaml
pass_criteria:
  must_pass_rate: 100%  # All 10 MUST criteria pass
  should_pass_rate: 80%  # At least 3 of 4 SHOULD criteria pass
  could_pass_rate: 0%   # Optional, no minimum
  
  overall_pass:
    condition: "must_pass_rate == 100% AND should_pass_rate >= 80%"
    then: "Merge to production"
    else: "Iterate (max 3 attempts) or escalate"
```
