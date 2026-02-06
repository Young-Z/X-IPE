# Example: Feature Implementation Procedure (Pattern 2 - XML)

Demonstrates Pattern 2 (Complex Procedure) for TDD-based feature implementation.

```xml
<procedure name="Feature Implementation">
  
  <step_1>
    <name>Read Technical Design</name>
    <action>
      1. Load technical design document from {feature_folder}/technical-design.md
      2. Identify components to implement
      3. Note dependencies and integration points
    </action>
    <constraints>
      - BLOCKING: Do not start coding without reading design
      - CRITICAL: Verify design is approved (status == approved)
    </constraints>
    <success_criteria>
      - All components identified
      - Dependencies mapped
      - Implementation order determined
    </success_criteria>
    <output>Implementation plan with component list</output>
  </step_1>

  <step_2>
    <name>Write Tests First</name>
    <requires>Implementation plan from step_1</requires>
    <action>
      1. Create test file at tests/test_{feature_name}.py
      2. Write failing tests for each acceptance criterion
      3. Run tests to confirm they fail
    </action>
    <constraints>
      - BLOCKING: Tests must fail before implementation
      - MANDATORY: Cover all acceptance criteria
      - CRITICAL: Include edge cases
    </constraints>
    <success_criteria>
      - Test file created
      - All acceptance criteria have tests
      - Tests run and fail as expected
    </success_criteria>
    <output>Test file with failing tests</output>
  </step_2>

  <step_3>
    <name>Implement Code</name>
    <requires>Failing tests from step_2</requires>
    <action>
      1. Implement minimum code to pass tests
      2. Follow KISS/YAGNI principles
      3. Add inline comments only where necessary
    </action>
    <constraints>
      - BLOCKING: Do not add unrequested features
      - CRITICAL: Follow existing code patterns
      - MANDATORY: Handle error cases
    </constraints>
    <success_criteria>
      - All tests pass
      - No linting errors
      - Code follows project conventions
    </success_criteria>
    <output>Implementation code with passing tests</output>
  </step_3>

  <step_4>
    <name>Verify Integration</name>
    <requires>Implementation from step_3</requires>
    <action>
      1. Run full test suite
      2. Check for regression
      3. Verify integration with dependent components
    </action>
    <constraints>
      - BLOCKING: Full test suite must pass
      - CRITICAL: No regression in existing functionality
    </constraints>
    <success_criteria>
      - All tests pass (new + existing)
      - No console errors or warnings
      - Feature works end-to-end
    </success_criteria>
    <output>Verified implementation ready for review</output>
  </step_4>

</procedure>
```
