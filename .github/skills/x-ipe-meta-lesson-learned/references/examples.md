# Lesson Learned Examples

## Example 1: Skill Error During Execution

**Trigger:** "The technical design skill failed with an error"

```
Step 1: Identify Skill
→ skill_name: x-ipe-task-based-technical-design
→ Verified: .github/skills/x-ipe-task-based-technical-design/ exists
→ Created: x-ipe-docs/skill-meta/x-ipe-task-based-technical-design/

Step 2: Gather Context
→ context:
    task_id: TASK-150
    scenario: Creating technical design for FEATURE-025
    inputs: feature_id=FEATURE-025

Step 3: Document Issue
→ observed_behavior: |
    Skill threw error at step 3:
    "KeyError: 'acceptance_criteria' not found in specification.md"
    
→ expected_behavior: |
    Skill should handle missing acceptance_criteria gracefully
    or use feature requirements as fallback.

Step 4: Capture Ground Truth
→ ground_truth: |
    When specification.md lacks acceptance_criteria section:
    1. Log warning: "No acceptance_criteria found"
    2. Fall back to requirements from feature-board
    3. Continue with design using requirements as criteria

Step 5: Propose Improvement
→ proposed_improvement:
    type: update_instruction
    target: "Execution Procedure Step 3"
    description: "Add fallback handling for missing acceptance_criteria"
    
→ proposed_ac:
    should:
      - id: AC-NEW
        description: "Handles missing specification sections gracefully"
        test_method: error_handling
        expected: "Falls back to feature requirements without error"

Step 6: Save Lesson
→ Created: x-ipe-docs/skill-meta/x-ipe-task-based-technical-design/x-ipe-meta-lesson-learned.md
→ Added lesson: LL-001
→ status: raw
```

---

## Example 2: Wrong Output Format

**Trigger:** "The requirement gathering output doesn't follow the template"

```
Step 1: Identify Skill
→ skill_name: x-ipe-task-based-requirement-gathering
→ Verified exists

Step 2: Gather Context
→ context:
    task_id: TASK-155
    scenario: Gathering requirements for new feature request
    inputs: User request about "add dark mode support"

Step 3: Document Issue
→ observed_behavior: |
    Output file requirement-details.md:
    - Missing "Constraints" section
    - "Success Criteria" section has wrong format (bullets instead of checkboxes)
    - No version header
    
→ expected_behavior: |
    Output should match template exactly:
    - All sections present
    - Checkboxes for success criteria (- [ ] format)
    - Version header at top

Step 4: Capture Ground Truth
→ ground_truth: |
    Correct requirement-details.md structure:
    
    # Requirement: {title}
    > Version: 1.0.0
    > Status: Draft
    
    ## Overview
    {description}
    
    ## Success Criteria
    - [ ] Criterion 1
    - [ ] Criterion 2
    
    ## Constraints
    - Constraint 1
    - Constraint 2

Step 5: Propose Improvement
→ proposed_improvement:
    type: new_ac
    target: acceptance_criteria.must
    description: "Require template structure validation"
    
→ proposed_ac:
    must:
      - id: AC-NEW
        description: "Output follows requirement-details.md template structure"
        test_method: structure_validation
        expected: "All sections present, correct formatting"

Step 6: Save Lesson
→ Updated: x-ipe-meta-lesson-learned.md
→ Added lesson: LL-002
→ severity: major
→ status: raw
```

---

## Example 3: Human Feedback

**Trigger:** "This technical design is missing error handling - please capture that as a lesson"

```
Step 1: Identify Skill
→ Inferred from context: x-ipe-task-based-technical-design
→ Confirmed with user

Step 2: Gather Context
→ context:
    task_id: TASK-160
    scenario: Technical design for API integration feature
    inputs: FEATURE-030

Step 3: Document Issue
→ observed_behavior: |
    Technical design document has no Error Handling section.
    
→ expected_behavior: |
    Technical design should include Error Handling section
    documenting expected exceptions and recovery strategies.

Step 4: Capture Ground Truth
→ Asked: "What should the Error Handling section contain?"
→ Human response: "List of expected exceptions, recovery strategies, fallback behaviors"

→ ground_truth: |
    Technical design must include ## Error Handling section with:
    - Table of expected exceptions
    - Recovery strategy for each
    - Fallback behaviors
    - Logging requirements
    
    Example:
    | Exception | Recovery | Fallback |
    |-----------|----------|----------|
    | ConnectionError | Retry 3x | Use cached data |
    | TimeoutError | Retry with backoff | Return partial result |

Step 5: Propose Improvement
→ proposed_improvement:
    type: new_ac
    target: acceptance_criteria.should
    description: "Require Error Handling section in technical design"
    
→ proposed_ac:
    should:
      - id: AC-NEW
        description: "Includes Error Handling section with exception table"
        test_method: section_exists
        expected: "Error Handling section with exception/recovery/fallback table"

Step 6: Save Lesson
→ Updated: x-ipe-meta-lesson-learned.md
→ Added lesson: LL-003
→ severity: major
→ source: human_feedback
→ status: raw
```

---

## Example 4: Edge Case Not Covered

**Trigger:** "The feature breakdown skill didn't handle a feature with no acceptance criteria"

```
Step 1: Identify Skill
→ skill_name: x-ipe-task-based-feature-breakdown

Step 2: Gather Context
→ context:
    task_id: TASK-165
    scenario: Breaking down requirement into features
    inputs: requirement-details.md with 3 user stories but no AC

Step 3: Document Issue
→ observed_behavior: |
    Skill assumed acceptance criteria existed.
    Created features with empty AC section.
    
→ expected_behavior: |
    Skill should derive AC from user stories when none provided.
    Or flag to user that AC are missing and need to be defined.

Step 4: Capture Ground Truth
→ ground_truth: |
    When requirement has no explicit acceptance criteria:
    1. Check for user stories
    2. If user stories exist: derive AC from "Given/When/Then" if present
    3. If no derivable AC: ask user "No acceptance criteria found. 
       Please provide AC for: {feature_name}"
    4. Do not proceed with empty AC

Step 5: Propose Improvement
→ proposed_improvement:
    type: add_example
    target: references/examples.md
    description: "Add example for handling missing acceptance criteria"

→ proposed_ac:
    must:
      - id: AC-NEW
        description: "Handles missing acceptance criteria appropriately"
        test_method: edge_case_handling
        expected: "Derives from user stories OR prompts user"

Step 6: Save Lesson
→ Created: x-ipe-meta-lesson-learned.md for x-ipe-task-based-feature-breakdown
→ Added lesson: LL-001
→ severity: major
→ status: raw
```
