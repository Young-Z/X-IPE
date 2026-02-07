# Requirement File Splitting Reference

## Splitting Rules

- **Threshold:** 500 lines
- **When:** Before adding NEW requirements, check current file line count
- **How:** If current file > 500 lines, create new part

## Procedure

```
1. Determine current active file:
   a. Check if x-ipe-docs/requirements/requirement-details.md exists
   b. Check if x-ipe-docs/requirements/requirement-details-part-X.md files exist
   c. Find the highest part number (latest active part)

2. Count lines in current active file:
   - If no file exists -> current_lines = 0, active_file = requirement-details.md
   - If requirement-details.md exists (no parts) -> count its lines
   - If parts exist -> count lines in highest part number file

3. IF current_lines > 500:
   a. IF file is requirement-details.md (original, no parts yet):
      - Rename requirement-details.md -> requirement-details-part-1.md
      - Create new requirement-details-part-2.md with header template
      - New file becomes active
   
   b. ELSE IF file is requirement-details-part-X.md:
      - Create new requirement-details-part-(X+1).md with header template
      - New file becomes active

4. ELSE (current_lines <= 500):
   - Continue using current active file
```

## New Part Header Template

```markdown
# Requirement Details - Part {X}

> Continued from: [requirement-details-part-{X-1}.md](requirement-details-part-{X-1}.md)  
> Created: {MM-DD-YYYY}

---

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup List |
|---------------------|---------|-------------|

---

## Feature Details (Continued)

```

## File Naming Convention

| Scenario | File Names |
|----------|------------|
| Single file (< 500 lines total) | `requirement-details.md` |
| After first split | `requirement-details-part-1.md`, `requirement-details-part-2.md` |
| After second split | `requirement-details-part-1.md`, `requirement-details-part-2.md`, `requirement-details-part-3.md` |

## Index File (Required when parts exist)

When parts exist, create/update `requirement-details-index.md`:

```markdown
# Requirement Details Index

> Last Updated: MM-DD-YYYY

## Parts Overview

| Part | File | Features Covered | Lines |
|------|------|------------------|-------|
| 1 | [Part 1](requirement-details-part-1.md) | FEATURE-001 to FEATURE-005 | ~420 |
| 2 | [Part 2](requirement-details-part-2.md) | FEATURE-006 to FEATURE-010 | ~380 |
```

NOTE: Feature List is NOT in index - each part file has its own Feature List section.
