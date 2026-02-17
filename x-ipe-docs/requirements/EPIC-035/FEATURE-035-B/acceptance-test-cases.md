# Acceptance Test Cases: FEATURE-035-B

> Feature: Feature Board Epic Tracking
> Date: 02-17-2026
> Result: 10/10 PASS

| AC ID | Description | Result | Evidence |
|-------|-------------|--------|----------|
| AC-035-B.1 | features.md template includes Epic ID column | ✅ PASS | templates/features.md: `\| Epic ID \| Feature ID \| ...` |
| AC-035-B.2 | Sort order documented (Epic ID, then suffix) | ✅ PASS | SKILL.md Epic Status Derivation section: sort order note |
| AC-035-B.3 | create_or_update_features accepts epic_id | ✅ PASS | SKILL.md input params: `epic_id: "EPIC-XXX"` |
| AC-035-B.4 | Epic ID populated when creating features | ✅ PASS | SKILL.md create operation: "Set epic_id from input" |
| AC-035-B.5 | Feature Data Model includes epic_id | ✅ PASS | examples.md: `epic_id: EPIC-XXX` in Feature schema |
| AC-035-B.6 | Spec links use EPIC/FEATURE paths | ✅ PASS | examples.md: `EPIC-XXX/FEATURE-XXX-X/specification.md` |
| AC-035-B.7 | Template includes Epic ID column | ✅ PASS | templates/features.md: Epic ID as first column |
| AC-035-B.8 | Examples show epic_id throughout | ✅ PASS | examples.md: epic_id in Data Model, create, query, closing examples |
| AC-035-B.9 | Legacy features get "-" for Epic ID | ✅ PASS | SKILL.md: "or `-` for legacy features" and "(or `-` if not provided)" |
| AC-035-B.10 | Epic status derivation note exists | ✅ PASS | SKILL.md: "Epic Status Derivation" section with derivation table |
