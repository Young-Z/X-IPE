# Example: DoR/DoD (Code Implementation)

Demonstrates Definition of Ready and Definition of Done patterns using XML format.

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Technical Design Approved</name>
    <verification>technical-design.md exists with status: approved</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Test Cases Generated</name>
    <verification>Test file exists with failing tests</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Dependencies Available</name>
    <verification>All referenced components are implemented</verification>
  </checkpoint>
</definition_of_ready>
```

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>All Tests Pass</name>
    <verification>Run test suite, 100% pass rate</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Code Reviewed</name>
    <verification>PR approved or self-review documented</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>No Linting Errors</name>
    <verification>Linter returns 0 errors</verification>
  </checkpoint>
</definition_of_done>
```

---

## Additional Examples

### Feature Refinement DoR/DoD

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Feature exists on board</name>
    <verification>Feature ID found in feature-board.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Requirement summary available</name>
    <verification>requirement-summary.md exists in requirement folder</verification>
  </checkpoint>
</definition_of_ready>
```

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Specification document created</name>
    <verification>feature-specification.md exists in feature folder</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Acceptance criteria defined</name>
    <verification>At least 2 acceptance criteria per feature</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Human review complete</name>
    <verification>User approved specification</verification>
  </checkpoint>
</definition_of_done>
```
