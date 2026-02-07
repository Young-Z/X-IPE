# User Manual - Examples

## Example: Python Web Application

**Request:** "Document how to run this Python web app"

**Execution:**
```
1. Execute Task Flow from x-ipe-workflow-task-execution skill

2. Step 1 - Identify Commands:
   Found: pyproject.toml with entry point src/app.py
   Run command: uv run python -m src.app
   Test command: uv run pytest

3. Step 2 - Verify Commands:
   $ uv run python -m src.app
   Running on http://localhost:5000
   Verified successfully.

4. Step 3 - Update README:
   Added "How to Run" section with:
   - Prerequisites: Python 3.12+, uv
   - Installation: uv sync
   - Run: uv run python -m src.app
   - Test: uv run pytest

5. Return Task Completion Output:
   status: completed
   next_task_based_skill: null
   require_human_review: yes
   task_output_links: [README.md]
   run_command: "uv run python -m src.app"
   test_command: "uv run pytest"

6. Resume Task Flow from x-ipe-workflow-task-execution skill
```

### Example README Output

```markdown
## How to Run

1.  **Install Dependencies:**
    ```bash
    uv sync
    ```

2.  **Run the Application:**
    ```bash
    uv run python -m src.app
    ```

3.  **Run Tests:**
    ```bash
    uv run pytest
    ```
```
