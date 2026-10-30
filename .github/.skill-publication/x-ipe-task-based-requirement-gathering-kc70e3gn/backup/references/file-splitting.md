# Requirement file splitting

This is a requirement-document threshold, not a SKILL.md body-line limit.
Check logical lines in the current active file BEFORE appending NEW requirements.
Only an already **>500-line** active file requires the split below: 473 and 500
continue in place; 501 requires a split. Do not use projected length as the trigger.
An agreed inline CR edit need not regenerate or split every existing part.

## Resolve active file and preserve contents

1. Reconcile requirement-details-index with ALL requirement-details-part-X files.
   No files means requirement-details.md will be the first active file, part 1.
   With only requirement-details.md use it. With numbered parts use the highest
   integer X, not lexicographic order. Ambiguous coexistence of original and parts
   or missing index targets blocks until an authorized disposition is known.
2. If active file has <=500 lines, append in that file; no new part or rename.
3. If original file has >500 lines and no parts exist, check part-1/part-2 paths
   are unused, rename original to requirement-details-part-1.md without changing
   its content, then create part-2 with the header below.
4. If numbered part X has >500 lines, preserve it and create part-(X+1), after
   checking collision. Do not overwrite a concurrently created part.
5. Create/update index when parts exist. Include every part, accurate Epic/feature
   coverage and line counts; retain each part's own Feature List. EPIC IDs appear
   only in Epic coverage/grouping, never in Feature ID rows.
6. Repair inbound links affected by the first rename within approved write scope,
   including required workflow deliverable references through the actual agreed
   writer. If a protected/unowned consumer cannot be repaired, block and report
   the link/owner, not a knowingly broken completion claim. Verify both preserved
   old contents and current links. Do not modify another workflow implicitly.

## New part header

```markdown
# Requirement Details - Part {X}

> Continued from: [Part {previous}](x-ipe-docs/requirements/requirement-details-part-{previous}.md)
> Created: {YYYY-MM-DD}

## Epic Coverage

| Epic ID | Title |
| --- | --- |

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
| --- | --- | --- | --- | --- |

## Linked Mockups

| Mockup Function Name | Feature | Mockup List |
| --- | --- | --- |

## Requirement Details (Continued)
```

Append gathered Epic sections using the canonical requirement template. Feature
rows remain empty until actual Feature Breakdown assignments; legacy feature
rows already present remain valid and unchanged.

## Index shape

```markdown
# Requirement Details Index

> Last Updated: {YYYY-MM-DD}

## Parts Overview

| Part | File | Epics / Features Covered | Lines |
| --- | --- | --- | --- |
| 1 | [Part 1](x-ipe-docs/requirements/requirement-details-part-1.md) | {actual coverage} | {count} |
| 2 | [Part 2](x-ipe-docs/requirements/requirement-details-part-2.md) | {actual coverage} | {count} |
```

All generated links use project-root-relative paths, not ./, ../ or absolute
filesystem paths. Record active `requirement_details_part` and actual output link;
do not confuse index with the populated `requirement-doc` deliverable.

