# Feature Breakdown: Patterns & Anti-Patterns

### Pattern: Clear Requirements

**When:** Well-documented requirements exist
**Then:**
```
1. Read requirement-details.md thoroughly
2. Identify natural feature boundaries
3. Apply MVP-first principle
4. Document dependencies between features
```

### Pattern: Vague Requirements

**When:** Requirements are ambiguous or incomplete
**Then:**
```
1. Ask clarifying questions to human
2. Document assumptions made
3. Start with minimal feature set
4. Flag areas needing more detail
```

### Pattern: Large Scope

**When:** Requirement covers many features
**Then:**
```
1. Group by domain/functionality into Epics
2. Identify MVP core (first feature per Epic)
3. Create feature hierarchy within each Epic
4. Limit initial breakdown to 5-7 features per Epic
```

### Pattern: Epic Grouping

**When:** Assessing whether to use single or multiple Epics
**Then:**
```
1. Count estimated features and distinct domains
2. IF 1 domain AND ≤7 features → single Epic
3. IF 2-3 domains AND 8-15 features → 2-3 Epics (one per domain)
4. IF 4+ domains OR >15 features → multiple Epics
5. Each Epic should be independently deliverable where possible
6. Name Epics by domain: "Product Management", "Order Processing"
```

### Pattern: Feature Split with Parent Dedup

**When:** A parent feature is split into sub-features (e.g., FEATURE-001 → A, B, C)
**Then:**
```
1. After splitting, compare parent FRs against union of sub-feature FRs
2. If 100% covered → remove parent from board and requirement-details
3. If partial → keep parent, flag uncovered FRs for human review
4. Use feature-board-management for all board changes
```

### Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skipping Epic assessment | Features lack cohesion, poor organization | Always assess Epic granularity first |
| All features in one Epic | Monolithic, hard to manage large scope | Split by domain when >7 features |
| Too many features per Epic | Overwhelming, hard to track | Limit to 5-7 features per Epic |
| Features too granular | Micromanagement | Combine related functions |
| MVP not first | Critical path unclear | Always start with runnable MVP |
| Circular dependencies | Impossible to implement | Ensure DAG structure |
| Manual board updates | Inconsistent state | Use feature-board-management skill |
| Vague feature titles | Unclear scope | Use specific, action-oriented names |
| Keeping duplicate parent | Redundant tracking, confusing | Remove parent if fully covered by sub-features |
