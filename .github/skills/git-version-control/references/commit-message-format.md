# Commit Message Format

## Overview

This document provides detailed examples and guidelines for the structured commit message format used by the git-version-control skill.

---

## Format Template

```
{task_id} commit for {feature_context}: {summary}
```

---

## Components

### 1. Task ID
- **Source**: `task_data.task_id`
- **Format**: `TASK-XXX` (always uppercase)
- **Required**: Yes (always present)
- **Purpose**: Link commit to specific task

**Examples:**
- `TASK-001`
- `TASK-042`
- `TASK-123`

---

### 2. Feature Context
- **Source**: `task_data.feature_id`
- **Format**: `Feature-{feature_id}`
- **Required**: No (only if feature_id exists)
- **Purpose**: Link commit to feature for feature-stage tasks

**Rules:**
- If `task_data.feature_id` exists → Include `Feature-{feature_id}`
- If `task_data.feature_id` is null → Omit (just "commit for:")

**Examples:**
- With feature: `Feature-FEATURE-003`
- With feature: `Feature-FEATURE-015`
- Without feature: (omitted, becomes "commit for:")

---

### 3. Summary
- **Source**: `task_data.task_description` + key changes
- **Max Length**: 50 words
- **Required**: Yes
- **Purpose**: Describe what changed

**Guidelines:**
1. **Start with action verb**: Set up, Implement, Fix, Update, Add, Remove, Refactor
2. **Be specific**: Include key technologies/components
3. **Focus on "what"**: Not "how"
4. **Concise**: Remove unnecessary words

**Good Examples:**
- `Set up Python development environment with uv and project structure`
- `Implement user authentication API with JWT token validation`
- `Fix database connection timeout in user service`
- `Update feature board with new technical design artifacts`

**Bad Examples:**
- ❌ `Did some work` (not specific)
- ❌ `Changed files` (no context)
- ❌ `Fixed the bug that was causing the system to crash when users tried to login with invalid credentials and the session expired` (too long)

---

## Complete Examples

### Standalone Tasks

**Task: Project Initialization**
```yaml
task_data:
  task_id: TASK-001
  task_description: Initialize Python project with uv
  feature_id: null
```
**Generated Message:**
```
TASK-001 commit for: Initialize Python project with uv
```

---

**Task: Development Environment Setup**
```yaml
task_data:
  task_id: TASK-002
  task_description: Set up Node.js development environment with npm and testing framework
  feature_id: null
```
**Generated Message:**
```
TASK-002 commit for: Set up Node.js development environment with npm and testing framework
```

---

**Task: Bug Fix (Standalone)**
```yaml
task_data:
  task_id: TASK-099
  task_description: Fix memory leak in background worker process
  feature_id: null
```
**Generated Message:**
```
TASK-099 commit for: Fix memory leak in background worker process
```

---

### Feature-Stage Tasks

**Task: Technical Design**
```yaml
task_data:
  task_id: TASK-015
  task_description: Create technical design for user authentication system
  feature_id: FEATURE-003
```
**Generated Message:**
```
TASK-015 commit for Feature-FEATURE-003: Create technical design for user authentication system
```

---

**Task: Code Implementation**
```yaml
task_data:
  task_id: TASK-023
  task_description: Implement JWT token generation and validation endpoints
  feature_id: FEATURE-005
```
**Generated Message:**
```
TASK-023 commit for Feature-FEATURE-005: Implement JWT token generation and validation endpoints
```

---

**Task: Test Generation**
```yaml
task_data:
  task_id: TASK-031
  task_description: Generate unit tests for payment processing module
  feature_id: FEATURE-008
```
**Generated Message:**
```
TASK-031 commit for Feature-FEATURE-008: Generate unit tests for payment processing module
```

---

**Task: Bug Fix (Within Feature)**
```yaml
task_data:
  task_id: TASK-042
  task_description: Fix authentication token validation in login endpoint
  feature_id: FEATURE-007
```
**Generated Message:**
```
TASK-042 commit for Feature-FEATURE-007: Fix authentication token validation in login endpoint
```

---

**Task: Feature Closing**
```yaml
task_data:
  task_id: TASK-056
  task_description: Complete user profile management feature with documentation
  feature_id: FEATURE-012
```
**Generated Message:**
```
TASK-056 commit for Feature-FEATURE-012: Complete user profile management feature with documentation
```

---

### Requirement-Stage Tasks

**Task: Requirement Gathering**
```yaml
task_data:
  task_id: TASK-003
  task_description: Document requirements for e-commerce checkout flow
  feature_id: null
  requirement_id: REQ-001
```
**Generated Message:**
```
TASK-003 commit for: Document requirements for e-commerce checkout flow
```

**Note:** Requirement-stage tasks don't have feature_id during gathering phase, so no "Feature-XXX" in message.

---

**Task: Feature Breakdown**
```yaml
task_data:
  task_id: TASK-007
  task_description: Break down shopping cart feature into implementation tasks
  feature_id: null
  requirement_id: REQ-002
```
**Generated Message:**
```
TASK-007 commit for: Break down shopping cart feature into implementation tasks
```

---

## Summary Length Guidelines

### Counting Words
- Count only substantive words
- Articles (a, an, the) count
- Prepositions (in, on, with, for) count
- Target: 5-15 words ideal, 50 words maximum

### Shortening Strategies

**Too Long:**
```
Implement the user authentication and authorization system with JWT token generation, validation, refresh token handling, and session management capabilities
```
(21 words)

**Better:**
```
Implement user authentication system with JWT tokens and session management
```
(11 words)

**Too Long:**
```
Set up the complete development environment including Python with uv package manager, virtual environment configuration, project structure with source and tests directories, and documentation
```
(26 words)

**Better:**
```
Set up Python development environment with uv and project structure
```
(11 words)

---

## Edge Cases

### Very Short Descriptions
If task_description is very short, use it as-is:
```yaml
task_data:
  task_id: TASK-100
  task_description: Add logging
  feature_id: FEATURE-020
```
**Generated Message:**
```
TASK-100 commit for Feature-FEATURE-020: Add logging
```

---

### Multiple Key Changes
Summarize multiple changes concisely:
```yaml
task_data:
  task_id: TASK-055
  task_description: Update database schema, add migrations, and modify API endpoints for user preferences
  feature_id: FEATURE-011
```
**Generated Message:**
```
TASK-055 commit for Feature-FEATURE-011: Update database schema and API endpoints for user preferences
```

---

## Anti-Patterns to Avoid

### ❌ Don't Include Implementation Details
```
Bad: TASK-042 commit for Feature-FEATURE-007: Fix bug by adding null check on line 156 in auth.py
Good: TASK-042 commit for Feature-FEATURE-007: Fix authentication token validation
```

### ❌ Don't Use Vague Terms
```
Bad: TASK-023 commit for: Did some updates
Good: TASK-023 commit for: Update user profile API endpoints
```

### ❌ Don't Duplicate Task ID in Summary
```
Bad: TASK-015 commit for: Complete TASK-015 work
Good: TASK-015 commit for: Create technical design for authentication
```

### ❌ Don't Exceed 50 Words
```
Bad: TASK-031 commit for Feature-FEATURE-008: Generate comprehensive unit tests for the payment processing module including credit card validation, payment gateway integration, transaction logging, error handling, retry logic, and notification system
Good: TASK-031 commit for Feature-FEATURE-008: Generate unit tests for payment processing module
```

---

## Auto-Generation Algorithm

```
1. Extract task_id from task_data
2. Check if feature_id exists:
   - If yes: feature_context = "Feature-{feature_id}"
   - If no: feature_context = "" (empty)
3. Extract task_description
4. Trim/summarize to max 50 words if needed
5. Construct message:
   - If feature_context exists: "{task_id} commit for {feature_context}: {summary}"
   - If feature_context empty: "{task_id} commit for: {summary}"
```

---

## Git Log Example

After several commits, `git log --oneline` might look like:

```
a3f8c92 TASK-056 commit for Feature-FEATURE-012: Complete user profile management feature with documentation
b2e7d81 TASK-042 commit for Feature-FEATURE-007: Fix authentication token validation in login endpoint
c9a1f34 TASK-031 commit for Feature-FEATURE-008: Generate unit tests for payment processing module
d4b2c56 TASK-023 commit for Feature-FEATURE-005: Implement JWT token generation and validation endpoints
e8d3a72 TASK-015 commit for Feature-FEATURE-003: Create technical design for user authentication system
f1c4b89 TASK-007 commit for: Break down shopping cart feature into implementation tasks
g2e5d91 TASK-002 commit for: Set up Node.js development environment with npm and testing framework
h7f3a46 TASK-001 commit for: Initialize Python project with uv
```

Clean, traceable, consistent! 🎉
