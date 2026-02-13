---
skill_name: x-ipe-meta-skill-creator
total_lessons: 1
last_updated: 2026-02-13
---

# Lessons Learned: x-ipe-meta-skill-creator

## LL-001

```yaml
id: LL-001
date: 2026-02-13
severity: major
status: raw
task_id: TASK-411
reporter: Sage (agent)
skill_version: current
```

### Context

During FEATURE-030-B Code Implementation, the agent used `x-ipe-meta-skill-creator` to create the `x-ipe-tool-uiux-reference` skill. The skill had bundled resources (references/) including `examples.md` and `toolbar-template.md`.

### Observed Behavior

1. Agent created candidate SKILL.md + `candidate/references/examples.md` in Step 4
2. Agent merged candidate → `.github/skills/x-ipe-tool-uiux-reference/` in Step 8
3. Agent then created `toolbar-template.md` **directly** in `.github/skills/.../references/` — bypassing the candidate folder
4. Result: `toolbar-template.md` existed in production but was **missing** from `candidate/references/`
5. Human noticed the inconsistency

### Expected Behavior

All bundled resources should be created in `candidate/references/` **before** the merge step. The merge (`cp -r candidate/* .github/skills/{skill-name}/`) should be the **only** path from candidate to production. No files should be created directly in production.

### Ground Truth

The correct workflow is:
1. Create ALL resources (SKILL.md, references/*, scripts/*, templates/*) inside `candidate/` during Step 4
2. If new resources are identified after Step 4 but before merge: add them to `candidate/` first
3. Step 8 merge copies everything from candidate → production
4. After merge: NO direct writes to `.github/skills/{skill-name}/` — if something was missed, add to candidate and re-merge

### Improvement Proposal

```yaml
type: update_instruction
target: .github/skills/x-ipe-meta-skill-creator/SKILL.md
section: Step 4 (Round 1: Create Meta + Draft) and Step 8 (Merge or Iterate)
description: |
  1. Step 4: Add constraint that ALL bundled resources (references/, scripts/, templates/)
     must be created inside candidate/ — not just SKILL.md
  2. Step 8: Add pre-merge validation that checks candidate/ contains all files
     referenced by SKILL.md before copying to production
  3. Add post-merge constraint: NO direct writes to .github/skills/{skill-name}/
     after merge — if missing files found, add to candidate and re-merge
```
