# README Updator Tool — Examples

## Example 1: Python Project (uv)

**Input:**
```yaml
operation: update_readme
config:
  readme_path: README.md
  feature_context: null
```

**Execution:**
1. Found pyproject.toml with entry point `main.py`
2. Verified: `uv run python main.py` starts server on http://localhost:5000
3. Verified: `uv run pytest` runs 45 tests, all passing
4. Updated README.md with "How to Run" section

**Output:**
```yaml
operation_output:
  success: true
  result:
    run_command: "uv run python main.py"
    test_command: "uv run pytest"
    readme_path: "README.md"
    sections_updated: ["Prerequisites", "Installation", "Running", "Testing"]
  errors: []
```

## Example 2: Node.js Project (npm)

**Input:**
```yaml
operation: update_readme
config:
  readme_path: README.md
  feature_context:
    feature_id: FEATURE-049-A
    feature_title: "Knowledge Base Backend"
```

**Execution:**
1. Found package.json with scripts: start, dev, test
2. Verified: `npm run dev` starts dev server
3. Verified: `npm test` runs vitest, 404 tests passing
4. Updated README.md with "How to Run" section mentioning FEATURE-049-A

**Output:**
```yaml
operation_output:
  success: true
  result:
    run_command: "npm run dev"
    test_command: "npm test"
    readme_path: "README.md"
    sections_updated: ["Prerequisites", "Installation", "Running", "Testing"]
  errors: []
```

## Example 3: Invoked by Feature Closing

**Context:** Feature closing (Phase 3, Step 3.1) invokes this tool when user has enabled the readme-updator toggle.

```yaml
# Feature closing calls:
operation: update_readme
config:
  readme_path: README.md
  feature_context:
    feature_id: FEATURE-049-F
    feature_title: "KB AI Librarian & Intake"
```

The tool discovers commands, verifies them, and updates README. Feature closing continues with its remaining steps.

## Example 4: No Config Found (Error)

**Input:**
```yaml
operation: update_readme
config:
  readme_path: README.md
```

**Output:**
```yaml
operation_output:
  success: false
  result: null
  errors:
    - code: MANUAL_NO_CONFIG
      message: "Neither pyproject.toml nor package.json found in project root"
```
