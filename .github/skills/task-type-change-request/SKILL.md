---
name: task-type-change-request
description: Process change requests by analyzing impact on existing requirements and features. Determines if CR modifies existing feature (→ refinement) or requires new feature (→ requirement update + feature breakdown). Triggers on "change request", "CR", "modify feature", "update requirement".
---

# Task Type: Change Request

## Purpose

Process change requests (CRs) systematically by:
1. Analyzing the change request against existing requirements and features
2. Classifying the CR as either modification to existing feature or new feature
3. Routing to appropriate workflow (Feature Refinement or Requirement Update + Feature Breakdown)
4. Maintaining traceability and documentation

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Change Request |
| Category | Standalone |
| Next Task Type | Feature Refinement OR Feature Breakdown (determined by classification) |
| Require Human Review | Yes |

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |

---

## Skill/Task Completion Output

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: standalone
  status: completed | blocked
  next_task_type: task-type-feature-refinement | task-type-feature-breakdown
  require_human_review: Yes
  auto_proceed: {from input Auto Proceed}
  task_output_links: [x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md]
  
  # Dynamic attributes (CR-specific)
  cr_id: CR-XXX
  cr_classification: modification | new_feature
  affected_features: [FEATURE-XXX, ...]  # For modifications
  new_feature_ids: [FEATURE-XXX, ...]    # For new features
  requirement_updated: true | false
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Change request description provided | Yes |
| 2 | Requestor/stakeholder identified | No |
| 3 | Business justification available | Yes |
| 4 | x-ipe-docs/requirements/requirement-details.md exists | Yes |
| 5 | x-ipe-docs/planning/features.md exists | Yes |

---

## Execution Flow

Execute Change Request by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Understand CR | Parse what, who, why, when of the change request | CR context documented |
| 2 | Review Existing | Read requirement-details.md and features.md | Related features identified |
| 3 | Classify CR | Apply classification criteria (modification vs new feature) | Classification determined |
| 4 | Human Approval | Present classification and reasoning to human | Human approves |
| 5 | Execute Path | Update spec (modification) or requirements (new feature) | Documents updated |
| 6 | Document CR | Create `CR-XXX.md` in feature folder and update specification version history | CR documented |

**⛔ BLOCKING RULES:**
- Step 4: BLOCKED until human explicitly approves classification
- Step 5: Do NOT proceed without human approval of classification

---

## Classification Criteria

### Best Practices for CR Classification

Based on software engineering best practices, use these criteria to determine if a CR is a **modification** or **new feature**:

#### Modification/Enhancement (Existing Feature)

| Criteria | Examples |
|----------|----------|
| Extends existing behavior | Add sorting to existing search results |
| Changes parameters/settings | Increase timeout from 30s to 60s |
| Improves existing workflow | Add confirmation step to existing checkout |
| Adds options to existing UI | New filter in existing dropdown |
| Enhances existing API | Add optional parameter to endpoint |
| Performance improvement | Optimize existing query |
| Bug-driven enhancement | Add validation that was missing |

**Characteristics:**
- Works within current system boundaries
- Builds upon existing user stories
- No new API endpoints/screens required (just changes to existing)
- Usually smaller in scope (<1 sprint)
- Same users, extended functionality

#### New Feature

| Criteria | Examples |
|----------|----------|
| Introduces new capability | Add chat when only email exists |
| New user workflow | Add multi-factor authentication |
| New data model required | Add inventory tracking to sales app |
| New API endpoints/screens | Add reporting dashboard |
| New user type | Add vendor portal to customer app |
| Independent functionality | Add notification system |
| Changes product offering | Add subscription tier |

**Characteristics:**
- Expands system boundaries
- Requires new user stories
- Needs new UI screens, API endpoints, or data models
- Usually larger in scope (≥1 sprint)
- May require separate documentation/onboarding

---

## Decision Tree

```yaml
Classification Logic:
  Step 1: Check if CR relates to existing feature
    - Search features.md for related functionality
    - Check if any existing feature covers this domain
    
  Step 2: Evaluate based on Step 1 result
    IF no_related_feature_exists:
      THEN: classification = "new_feature"
      ACTION: Update requirements, add to feature board
      
    IF related_feature_exists:
      THEN: Proceed to Step 3
      
  Step 3: Evaluate scope change
    IF cr_changes_fundamental_scope = true:
      THEN: classification = "new_feature"
      ACTION: Update requirements, create new feature
      
    IF cr_changes_fundamental_scope = false:
      THEN: classification = "modification"
      ACTION: Update existing feature specification
```

### Scope Change Indicators

A CR changes fundamental scope if it:
- Introduces entirely new workflows
- Requires new data models
- Adds new user types or roles
- Creates new integration points
- Significantly changes the feature's purpose

---

## Execution Procedure

### Step 1: Understand the Change Request

**Action:** Parse the CR to understand what is being requested

```
1. Identify WHAT change is being requested
2. Identify WHO requested it and WHY
3. Identify WHEN it's needed (priority/urgency)
4. Document the CR context
```

**🌐 Web Search (Recommended):**
Use web search capability to research:
- Similar features in competitor products
- Industry standards for the requested change
- Best practices for the domain
- Regulatory requirements if applicable

**Output:** CR understanding summary

---

### Step 2: Review Existing Requirements and Features

**Action:** Analyze current state to understand impact

```
1. READ x-ipe-docs/requirements/requirement-details.md
   - Understand overall project scope
   - Identify related high-level requirements

2. READ x-ipe-docs/planning/features.md (Feature Board)
   - List all existing features
   - Note feature statuses and dependencies
   - Identify potentially related features

3. FOR EACH potentially related feature:
   IF x-ipe-docs/requirements/FEATURE-XXX/specification.md exists:
     READ specification to understand:
       - Current functionality
       - User stories
       - Acceptance criteria
       - Out of scope items
```

**Output:** Related features list with relevance notes

---

### Step 3: Classify the Change Request

**Action:** Apply classification criteria to determine CR type

```
1. Create comparison matrix:
   
   | Aspect | CR Requirement | Existing Feature(s) |
   |--------|---------------|---------------------|
   | Users  | [who]         | [who]               |
   | Workflow | [what flow] | [what flow]         |
   | Data Model | [data]   | [data]              |
   | UI Elements | [screens]| [screens]          |
   | API Endpoints | [APIs] | [APIs]             |

2. Evaluate scope change:
   - Does CR work within existing boundaries? → MODIFICATION
   - Does CR expand system boundaries? → NEW FEATURE
   - Is CR a significant enhancement to existing? → Judgment call

3. Document classification decision with reasoning
```

**Classification Decision:**
```yaml
classification: modification | new_feature
reasoning: |
  [Explain why this classification was chosen]
  [Reference specific criteria that apply]
affected_features: [FEATURE-XXX, ...]  # If modification
proposed_new_feature: <title>          # If new feature
```

---

### Step 4: Ask Human for Approval

**Action:** Present classification to human for confirmation

```
Present to human:
1. CR Summary
2. Classification: MODIFICATION or NEW FEATURE
3. Reasoning for classification
4. Affected features (if modification)
5. Proposed approach

Wait for human approval before proceeding
```

⚠️ **MANDATORY:** Do NOT proceed without explicit human approval of classification.

---

### Step 5: Execute Based on Classification

#### Path A: Modification to Existing Feature

```
1. CREATE x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md
   - Document the CR details
   - Store in the affected feature's folder
   - Link to the feature specification

2. UPDATE x-ipe-docs/requirements/FEATURE-XXX/specification.md
   - Add entry to Version History table with CR reference
   - Update affected sections
   - Revise user stories if needed
   - Update acceptance criteria

3. CHECK if requirement-details.md needs update:
   IF cr_affects_high_level_requirements = true:
     UPDATE x-ipe-docs/requirements/requirement-details.md:
       - Update High-Level Requirements section if scope expanded
       - Add entry to Clarifications table documenting the change
       - Update Constraints if new constraints introduced
     SET requirement_updated = true
   ELSE:
     SET requirement_updated = false

4. SET next_task_type = task-type-feature-refinement
   - Continue with feature refinement workflow
   - Technical design may need updates
```

**When to update requirement-details.md:**
- CR adds new high-level capability to existing feature
- CR changes project constraints
- CR affects multiple features
- CR changes user types or stakeholders
- CR modifies business rules at project level

**Specification Version History Update Pattern:**
```markdown
## Version History
| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| 1.1 | 2026-01-22 | Added bulk import capability | [CR-001](./CR-001.md) |
| 1.0 | 2026-01-15 | Initial specification | - |
```

#### Path B: New Feature

```
1. UPDATE x-ipe-docs/requirements/requirement-details.md
   - Add new requirement to High-Level Requirements section
   - Document in Clarifications table
   - Update Project Overview if scope changed

2. SET next_task_type = task-type-feature-breakdown
   - Continue with feature breakdown workflow
   - New feature will be added to feature board
   - CR document will be created in the new feature folder after breakdown

3. NOTE: After feature breakdown creates FEATURE-XXX folder:
   - CREATE x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md
   - This links the CR to the newly created feature
```

---

### Step 6: Create CR Documentation

**Action:** Create CR record in the feature folder at `x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md`

**Important:** 
- CR files are stored **inside the affected feature folder**, NOT in a separate change-requests folder
- This maintains traceability by co-locating the CR with its affected feature
- The specification's Version History links to the CR document

**CR Document Template:**
```markdown
# Change Request: CR-XXX

> Created: YYYY-MM-DD
> Status: Approved | Pending | Rejected
> Classification: Modification | New Feature
> Related Feature: FEATURE-XXX

## Request Details

**Requestor:** [Name/Role]
**Date Received:** YYYY-MM-DD
**Priority:** High | Medium | Low

## Description

[Detailed description of the change request]

## Business Justification

[Why this change is needed, business value]

## Impact Analysis

### Classification

**Type:** Modification to FEATURE-XXX | New Feature

**Reasoning:**
[Explain why this classification was chosen]

### Affected Components

| Component | Impact Level | Details |
|-----------|--------------|---------|
| [Feature/Module] | High/Medium/Low | [What changes] |

### Dependencies

- [List any dependencies on other features or systems]

## Proposed Approach

[High-level approach to implementing this CR]

## Approval

- [x] Classification approved by human
- [x] Approach approved by human
- [x] Ready for execution

## Links

- Feature Specification: [specification.md](./specification.md)
- Requirement Details: [requirement-details.md](../requirement-details.md)

---
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | CR documented in `x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md` | Yes |
| 2 | Classification determined and documented | Yes |
| 3 | Human approved classification | Yes |
| 4 | Feature specification Version History updated with CR reference | Yes (if modification) |
| 5 | Relevant documents updated (specification OR requirements) | Yes |
| 6 | Next task type correctly set | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Patterns

See [references/patterns.md](references/patterns.md) for detailed pattern guidance including:
- Enhancement CR pattern
- New Capability CR pattern
- Scope Expansion CR pattern
- Multi-Feature CR pattern
- Boundary cases and scoring criteria
- CR chain handling

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Skip classification | Wrong workflow chosen | Always classify explicitly |
| Assume modification | May miss scope expansion | Use decision tree |
| No human approval | Risk of wrong direction | Always get approval |
| Skip documentation | Lost traceability | Create CR document |
| Modify multiple features at once | Hard to track | One CR = One classification |
| No version history update | Lost change history | Update specification version |

---

## Example

See [references/examples.md](references/examples.md) for detailed execution examples including:
- Bulk import CR classification (NEW_FEATURE)
- UI enhancement CR classification (ENHANCEMENT)
- Ambiguous request requiring clarification
- Bug report redirection (NOT_A_CR)

---

## Notes

- **CR files live inside feature folders** - maintains traceability and co-location
- Version history in specifications links directly to CR documents
- Classification is not always black and white - when in doubt, ask human
- One CR should result in one classification (split complex CRs if needed)
- For new features, CR is created after feature breakdown creates the folder
