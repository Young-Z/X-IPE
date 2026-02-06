# Example: Requirement Gathering Workflow (Pattern 3 - Phase Blocks)

Demonstrates Pattern 3 (Long Workflow) with nested Pattern 1 (YAML) and Pattern 2 (XML) inside phases.

```markdown
## Phase 1: Initial Request Analysis (Simple)

**Entry Criteria:** User has provided a feature request or requirement

Perform the following:
1. Read the user's request carefully
2. Identify the core problem being solved
3. List explicit requirements mentioned
4. Note any implicit requirements or assumptions

CRITICAL: Do not assume requirements not explicitly stated.

**Exit Criteria:** 
- Core problem is documented
- Explicit requirements listed
- Assumptions identified and flagged for clarification

---

## Phase 2: Clarification (Complex Branching - YAML)

**Entry Criteria:** Phase 1 complete + ambiguities identified

```yaml
workflow:
  name: "Clarification Process"
  steps:
    - step: 1
      name: "Assess Ambiguity Impact"
      action: "Evaluate each ambiguity for implementation impact"
      branch:
        if: "ambiguity_count == 0"
        then: "Skip to Phase 3"
        else: "Continue to step 2"
      gate: "assessment_complete == true"
      
    - step: 2
      name: "Formulate Questions"
      action: "Create clarifying questions for ambiguities"
      branch:
        if: "impact == high"
        then: "Mark as BLOCKING - must resolve before proceeding"
        else_if: "impact == medium"
        then: "Include in question batch"
        else: "Document assumption, proceed with default"
      gate: "questions_prepared == true"
      
    - step: 3
      name: "Present Questions"
      action: "Present questions to user (max 5 at a time)"
      gate: "user_responded == true"
      
    - step: 4
      name: "Document Responses"
      action: "Record user answers and update requirements"
      gate: "responses_documented == true"

  blocking_rules:
    - "BLOCKING: Do not proceed with assumptions for high-impact ambiguities"
```

**Exit Criteria:**
- All high-impact questions answered
- Responses documented
- Remaining ambiguities are low-impact

---

## Phase 3: Requirement Structuring (Linear with Constraints - XML)

**Entry Criteria:** Phase 2 complete + sufficient clarity achieved

```xml
<procedure name="Requirement Structuring">
  <step_1>
    <name>Categorize Requirements</name>
    <action>
      1. Group requirements by functional area
      2. Identify cross-cutting concerns
    </action>
    <constraints>
      - CRITICAL: Each requirement belongs to exactly one primary category
    </constraints>
    <success_criteria>
      - All requirements categorized
      - No orphan requirements
    </success_criteria>
    <output>Categorized requirement list</output>
  </step_1>

  <step_2>
    <name>Map Dependencies</name>
    <requires>Categorized list from step_1</requires>
    <action>
      1. Identify requirement dependencies
      2. Check for circular dependencies
      3. Determine implementation order
    </action>
    <constraints>
      - BLOCKING: Circular dependencies must be resolved
    </constraints>
    <success_criteria>
      - Dependency graph complete
      - No circular dependencies
    </success_criteria>
    <output>Dependency graph</output>
  </step_2>

  <step_3>
    <name>Prioritize</name>
    <requires>Dependency graph from step_2</requires>
    <action>
      1. Mark as must-have vs nice-to-have
      2. Estimate complexity (low/medium/high)
    </action>
    <constraints>
      - MANDATORY: Prioritization must be validated with user
    </constraints>
    <success_criteria>
      - All requirements prioritized
      - Complexity estimated
    </success_criteria>
    <output>Prioritized requirement list</output>
  </step_3>
</procedure>
```

**Exit Criteria:**
- Requirements categorized
- Dependencies mapped
- Priorities assigned

---

## Phase 4: Acceptance Criteria Definition (Simple)

**Entry Criteria:** Phase 3 complete + requirements prioritized

Perform the following:
1. Write 2-5 acceptance criteria per requirement
2. Make criteria testable (specific, measurable)
3. Include happy path and edge cases
4. Define what "done" means for each

MANDATORY: Each criterion must be independently verifiable.

**Exit Criteria:**
- All requirements have acceptance criteria
- Criteria are testable
- Edge cases covered

---

## Phase 5: Documentation (Simple)

**Entry Criteria:** Phase 4 complete + acceptance criteria approved

Perform the following:
1. Create requirement summary document
2. Include all sections: problem, requirements, acceptance criteria
3. Add version history entry
4. Save to x-ipe-docs/requirements/{requirement_id}/

BLOCKING: Document must be reviewed before feature breakdown.

**Exit Criteria:**
- Document created at correct path
- All sections complete
- Version history initialized
```
