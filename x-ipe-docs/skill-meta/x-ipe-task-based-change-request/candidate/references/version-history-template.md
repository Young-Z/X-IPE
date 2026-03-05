# Version History Template

> Reference from SKILL.md: Specification version history update pattern for CR modifications.

---

## Specification Version History Update

When a CR modifies an existing feature, add an entry to the feature specification's Version History table linking to the CR document.

```markdown
## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| 1.1 | 2026-01-22 | Added bulk import capability | [CR-001](./CR-001.md) |
| 1.0 | 2026-01-15 | Initial specification | - |
```

**Rules:**
- Increment minor version for CR modifications
- Always link to the CR document in the same feature folder
- Description should summarize what changed, not the full CR
