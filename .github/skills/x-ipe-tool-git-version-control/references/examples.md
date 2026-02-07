# Git Version Control - Usage Examples

## Example 1: New Project Setup

```yaml
# Step 1: Initialize repository
operation: init
directory: /path/to/project

# Step 2: Create .gitignore
operation: create_gitignore
directory: /path/to/project
tech_stack: python

# Step 3: Stage all files
operation: add
directory: /path/to/project
files: null  # Add all

# Step 4: Initial commit
operation: commit
directory: /path/to/project
task_data:
  task_id: TASK-001
  task_description: Set up Python development environment with uv
  feature_id: null

# Generated message:
# "TASK-001 commit for: Set up Python development environment with uv"
```

---

## Example 2: Feature Development Commit

```yaml
# Stage specific files
operation: add
directory: /path/to/project
files:
  - src/auth.py
  - tests/test_auth.py

# Commit with feature context
operation: commit
directory: /path/to/project
task_data:
  task_id: TASK-023
  task_description: Implement user authentication with JWT tokens
  feature_id: FEATURE-005

# Generated message:
# "TASK-023 commit for Feature-FEATURE-005: Implement user authentication with JWT tokens"
```

---

## Example 3: Push to GitHub

```yaml
# Push to main branch
operation: push
directory: /path/to/project
remote: origin
branch: main
```

---

## Integration with Other Skills

### Called by x-ipe-task-based-dev-environment

```yaml
# After creating project structure
1. Call x-ipe-tool-git-version-control:
   operation: init
   directory: {project_root}

2. Call x-ipe-tool-git-version-control:
   operation: create_gitignore
   directory: {project_root}
   tech_stack: {selected_stack}

3. Call x-ipe-tool-git-version-control:
   operation: add
   directory: {project_root}
   files: null

4. Call x-ipe-tool-git-version-control:
   operation: commit
   directory: {project_root}
   task_data: {current_task_data_model}
```

### Called by Other Task-Based Skills

Any task-based skill can call this skill to commit their changes:

```yaml
# After completing work
1. Call x-ipe-tool-git-version-control:
   operation: add
   directory: {project_root}
   files: [<modified-files>] | null

2. Call x-ipe-tool-git-version-control:
   operation: commit
   directory: {project_root}
   task_data: {current_task_data_model}
```

---

## Best Practices

### Commit Frequency
- After major milestones (environment setup, feature completion)
- Before blocking/deferring tasks (save progress)
- After successful testing (code works as expected)

### Commit Message Quality
- Use task description as base
- Be specific about changes
- Keep under 50 words for summary
- Let auto-generation handle format

### Git Workflow
1. Init -> Create .gitignore (once per project)
2. Add -> Commit (iterative during development)
3. Pull -> Push (when syncing with remote)

### .gitignore Management
- Create during project initialization
- Update when tech stack changes
- Manually edit for project-specific exclusions
