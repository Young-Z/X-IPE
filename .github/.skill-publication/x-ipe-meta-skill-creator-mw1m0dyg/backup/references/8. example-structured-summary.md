# Example: Structured Summary

Demonstrates markdown table format for summarizing multiple items with consistent attributes.

## Feature Summary

```markdown
| Feature ID | Name | Priority | Status |
|------------|------|----------|--------|
| F-001 | User Authentication | Must-have | Pending |
| F-002 | Dashboard | Must-have | In Progress |
| F-003 | Export Reports | Nice-to-have | Pending |
```

## Dependency Summary

```markdown
| Component | Depends On | Type | Risk |
|-----------|------------|------|------|
| AuthService | Database | Hard | Low |
| Dashboard | AuthService, API | Hard | Medium |
| Reports | Dashboard | Soft | Low |
```

## Requirement Summary

```markdown
| Req ID | Description | Priority | Complexity | Status |
|--------|-------------|----------|------------|--------|
| R-001 | User login with email/password | Must-have | Medium | Approved |
| R-002 | Password reset via email | Must-have | Low | Approved |
| R-003 | OAuth integration | Nice-to-have | High | Pending |
```

## Test Coverage Summary

```markdown
| Module | Lines | Covered | Coverage | Status |
|--------|-------|---------|----------|--------|
| auth | 245 | 220 | 89.8% | ✅ Pass |
| api | 180 | 144 | 80.0% | ✅ Pass |
| utils | 95 | 70 | 73.7% | ⚠️ Below threshold |
```
