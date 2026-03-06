# End-User Human Representative Examples

## Example 1: Direct answer

**Input**
```yaml
message_context:
  source: human
  task_id: "TASK-770"
  workflow_name: "EPIC-047"
  downstream_context: "EPIC-047 is intended to stand alone"
  messages:
    - content: "Should we keep the new feature standalone instead of folding it into EPIC-044?"
human_shadow: false
```

**Expected Output**
```yaml
operation_output:
  success: true
  result:
    disposition: answer
    content: "Keep it standalone. EPIC-047 defines a new capability rather than refining EPIC-044."
    rationale_summary: "The requirement history already established this as a separate epic."
    confidence: 0.88
    fallback_required: false
  errors: []
```

## Example 2: Clarification

**Input**
```yaml
message_context:
  source: human
  task_id: "TASK-771"
  workflow_name: "EPIC-047"
  downstream_context: "No concrete scope supplied"
  messages:
    - content: "Make it smarter."
human_shadow: false
```

**Expected Output**
```yaml
operation_output:
  success: true
  result:
    disposition: clarification
    content: "What kind of improvement do you want: better disposition selection, human-shadow fallback, or memory beyond v1 scope?"
    rationale_summary: "The request is too broad to change implementation safely."
    confidence: 0.74
    fallback_required: false
  errors: []
```

## Example 3: Pass through

**Input**
```yaml
message_context:
  source: human
  task_id: "TASK-772"
  workflow_name: "EPIC-047"
  downstream_context: "The worker agent owns the live execution status"
  messages:
    - content: "Where are we in the current implementation task?"
human_shadow: false
```

**Expected Output**
```yaml
operation_output:
  success: true
  result:
    disposition: pass_through
    content: "I should let the downstream implementation agent answer that status question directly."
    rationale_summary: "The downstream agent has the freshest execution context."
    confidence: 0.86
    fallback_required: false
  errors: []
```
