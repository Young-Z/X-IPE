# Example: File Validation Workflow (Pattern 1 - YAML)

Demonstrates Pattern 1 (Simple Workflow) with branching logic for file type detection.

```yaml
workflow:
  name: "Validate Configuration File"
  steps:
    - step: 1
      name: "Load File"
      action: "Read configuration file from {file_path}"
      gate: "file_loaded == true"
      
    - step: 2
      name: "Parse Content"
      action: "Parse file content as YAML/JSON"
      branch:
        if: "file_extension == .yaml"
        then: "Use YAML parser"
        else: "Use JSON parser"
      gate: "parsed_content != null"
      
    - step: 3
      name: "Validate Schema"
      action: "Validate against expected schema"
      gate: "validation_errors == 0"
      
    - step: 4
      name: "Return Result"
      action: "Return validated configuration object"
      gate: "result_returned == true"

  blocking_rules:
    - "BLOCKING: Do not proceed if file does not exist"
    - "BLOCKING: Do not skip schema validation"
  
  critical_notes:
    - "CRITICAL: Preserve original file encoding"
```
