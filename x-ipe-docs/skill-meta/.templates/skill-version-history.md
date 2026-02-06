# Skill Version History Template

<!-- Copy YAML below to create skill-version-history.md. No markdown body needed. -->

```yaml
---
skill_name: {skill-name}
current_version: 1.0.0

versions:
  - version: 1.0.0
    date: {YYYY-MM-DD}
    author: {agent-nickname or human}
    changes:
      - type: initial  # Types: initial|ac_added|ac_updated|ac_removed|instruction_updated|breaking|fix
        description: "Initial creation"
        # Optional: source_lesson: LL-001
        # Optional: migration: "Migration steps for breaking changes"
    test_results:
      pass_rate: 100%
      tests_run: 0  # Count of test scenarios validated (manual or automated)
      # Optional: failed_tests: ["TC-001: reason"]
---
```

<!--
## Reference (not part of template)

### Semantic Versioning
- Major (X.0.0): Breaking changes requiring migration
- Minor (x.Y.0): New AC, features added
- Patch (x.y.Z): Fixes, clarifications

### Change Types
- initial: First version
- ac_added/ac_updated/ac_removed: Acceptance criteria changes
- instruction_updated: SKILL.md procedure changed
- breaking: Requires migration (add migration field)
- fix: Bug fix

### Test Results
tests_run = number of test scenarios validated for this version
(can be manual walkthroughs or automated tests)
-->
