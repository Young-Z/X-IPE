# Lesson Learned Template

<!-- Template for x-ipe-docs/skill-meta/{skill}/x-ipe-meta-lesson-learned.md -->

## Quick Capture (5-line minimum)

```markdown
---
skill_name: {skill-name}
---
## LL-001 | {date} | raw | {severity}
**Issue:** {One-line description}
**Expected:** {What should have happened}
**Fix:** {Proposed improvement}
```

---

## Full Template

```markdown
---
skill_name: {skill-name}
last_updated: {YYYY-MM-DD}
---

## LL-001 | {YYYY-MM-DD} | raw | major

**Summary:** {One-line description}

**Context:**
- Task: {TASK-ID}
- Scenario: {What was being done}

**Observed:** {What the skill actually did}

**Expected:** {What the skill should have done}

**Ground Truth:** {Correct output after manual fix}

**Proposed Improvement:**
- Type: new_ac | update_ac | update_instruction | add_example
- Target: {AC-ID or section name}
- Description: {What change to make}
- incorporated_in: {skill-version when fixed, e.g., v1.2.0}

---

## Lessons Summary

| Status | Count |
|--------|-------|
| raw | 0 |
| reviewed | 0 |
| incorporated | 0 |

### Critical Issues
- None

### Patterns
{Recurring themes}
```

---

## Reference

### Status Flow
`raw` → `reviewed` → `incorporated`

### Field Values

| Field | Values |
|-------|--------|
| status | raw, reviewed, incorporated |
| severity | critical, major, minor, enhancement |
| source | human_feedback, error, observation, test_failure |
| improvement type | new_ac, update_ac, update_instruction, add_example |
