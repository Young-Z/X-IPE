# Change Request - Patterns Reference

> Reference from SKILL.md: `See [references/patterns.md](references/patterns.md)`

---

## Pattern: Enhancement CR

**When:** CR adds capability to existing feature
**Example:** "Add export to CSV for the existing report"

```
1. Identify: FEATURE-005 (Reporting) exists
2. Check: CSV export is within reporting scope
3. Classify: MODIFICATION (adds to existing workflow)
4. Action: Update FEATURE-005 specification
5. Next: Feature Refinement → Technical Design
```

### Real-World Scenarios

| Request | Classification | Reasoning |
|---------|---------------|-----------|
| "Add dark mode to settings" | MODIFICATION | Settings feature exists, UI preference |
| "Add email validation" | MODIFICATION | Registration feature exists, same flow |
| "Add pagination to list" | MODIFICATION | List feature exists, UX improvement |

---

## Pattern: New Capability CR

**When:** CR introduces functionality not covered by any feature
**Example:** "Add real-time notifications"

```
1. Identify: No notification feature exists
2. Check: New data models, new UI, new service required
3. Classify: NEW FEATURE
4. Action: Update requirement-details.md
5. Next: Feature Breakdown → creates FEATURE-XXX
```

### Real-World Scenarios

| Request | Classification | Reasoning |
|---------|---------------|-----------|
| "Add chat support" | NEW_FEATURE | Entirely new capability |
| "Add payment processing" | NEW_FEATURE | New domain, new integrations |
| "Add mobile app" | NEW_FEATURE | New platform, new architecture |

---

## Pattern: Scope Expansion CR

**When:** CR significantly expands existing feature
**Example:** "Extend user authentication to support SSO"

```
1. Identify: FEATURE-001 (Authentication) exists
2. Check: SSO requires new integration, new flow, new data
3. Classify: MODIFICATION (but major) or NEW FEATURE
4. Decision: If SSO is a separate workflow → NEW FEATURE
           If SSO is another login method → MODIFICATION
5. Present to human for decision
```

### Decision Criteria

| Factor | Favors MODIFICATION | Favors NEW_FEATURE |
|--------|--------------------|--------------------|
| Same user workflow | ✓ | |
| Same data model | ✓ | |
| New integration required | | ✓ |
| Different target users | | ✓ |
| Reuses existing UI | ✓ | |
| New navigation/screens | | ✓ |

---

## Pattern: Multi-Feature CR

**When:** CR affects multiple existing features
**Example:** "Add audit logging across the system"

```
1. Identify: Multiple features affected
2. Check: Is this cross-cutting concern?
3. Classify: Usually NEW FEATURE (infrastructure)
4. Action: Create new feature for audit logging
5. Note: May require updates to existing features later
```

### Cross-Cutting Concerns Examples

| CR | Classification | Implementation |
|----|---------------|----------------|
| "Add audit logging everywhere" | NEW_FEATURE | Create logging infrastructure |
| "Add rate limiting to all APIs" | NEW_FEATURE | Create rate limit middleware |
| "Add analytics tracking" | NEW_FEATURE | Create analytics service |
| "Improve error messages" | ENHANCEMENT per feature | Update each affected feature |

---

## Pattern: Boundary Cases

### When Classification is Unclear

**Approach:**
```
1. List facts about the CR
2. Score against classification criteria
3. If close (within 2 points): ask human
4. Document the decision rationale
```

### Scoring Criteria

| Criteria | MODIFICATION Points | NEW_FEATURE Points |
|----------|--------------------|--------------------|
| Uses existing data model | +2 | |
| Creates new data model | | +2 |
| Same target users | +1 | |
| Different target users | | +2 |
| Extends existing workflow | +2 | |
| Creates new workflow | | +2 |
| Reuses existing UI | +1 | |
| New UI screens | | +1 |
| Estimated effort < 1 week | +1 | |
| Estimated effort > 2 weeks | | +1 |

**Threshold:** If difference ≤ 2, consult human for decision.

---

## Pattern: CR Chain

**When:** One CR leads to another
**Example:** "Add bulk import" → "Add import validation" → "Add import error handling"

```
1. Identify: Initial CR creates new capability
2. Subsequent CRs: Likely ENHANCEMENT to the first
3. Strategy: 
   - First CR: Create feature
   - Follow-up CRs: Refine same feature
4. Track: Use same feature folder for all related CRs
```

### Best Practice

```
CR-001: Add bulk import         → NEW_FEATURE (FEATURE-015)
CR-002: Add import validation   → ENHANCEMENT to FEATURE-015
CR-003: Add import error report → ENHANCEMENT to FEATURE-015
```

All CRs live in `x-ipe-docs/requirements/FEATURE-015/`:
```
FEATURE-015/
├── specification.md
├── CR-001.md  (original)
├── CR-002.md  (enhancement)
└── CR-003.md  (enhancement)
```
