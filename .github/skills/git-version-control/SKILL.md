---
name: git-version-control
description: Manage git version control operations including repository initialization, staging, committing, and GitHub integration. Provides standardized .gitignore templates and structured commit messages. Use for version control setup and management during development tasks.
---

# Git Version Control

## Purpose

Provide version control operations following a consistent pattern for managing code changes throughout the development lifecycle.

**Core Operations:**
0. **Check status** of git repository
1. **Initialize** git repository
2. **Create .gitignore** based on tech stack
3. **Stage files** for commit
4. **Commit changes** with structured messages
5. **Push to GitHub** (remote integration)
6. **Pull from GitHub** (remote integration)

---

## Important Notes

### Skill Prerequisite
- This skill can be called by other skills during their execution
- This skill does NOT follow the task-execution-guideline flow (it's a utility skill)
- Repository must exist (directory must be present)

**Important:** If Agent DO NOT have skill capability, can directly go to `skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Operations

### Operation 0: Check Repository Status

**When to use:** Check if directory is a git repository and get current status.

**Input Parameters:**
```yaml
operation: status
directory: <absolute-path-to-project-root>
```

**Execution:**
```bash
cd {directory}
git status
```

**Output:**
```yaml
success: true | false
is_git_repo: true | false
branch: <current-branch> | null
has_uncommitted_changes: true | false
staged_files: [<file-paths>] | []
modified_files: [<file-paths>] | []
untracked_files: [<file-paths>] | []
message: "Repository status" | "Not a git repository"
```

---

### Operation 1: Initialize Repository

**When to use:** Setting up a new project or converting existing directory to git repo.

**Input Parameters:**
```yaml
operation: init
directory: <absolute-path-to-project-root>
```

**Execution:**
```bash
cd {directory}
git init
```

**Output:**
```yaml
success: true | false
message: "Initialized git repository at {directory}"
repository_path: {directory}
```

---

### Operation 2: Create .gitignore

**When to use:** After repository initialization or when changing tech stack.

**Input Parameters:**
```yaml
operation: create_gitignore
directory: <absolute-path-to-project-root>
tech_stack: python | nodejs
```

**Execution:**
```
1. Load appropriate .gitignore template from templates/
2. Create .gitignore file in {directory}
3. Populate with tech stack-specific patterns
```

**Tech Stack Templates:**
- `python` → Load from `templates/gitignore-python.txt`
- `nodejs` → Load from `templates/gitignore-nodejs.txt`

**Output:**
```yaml
success: true | false
message: "Created .gitignore for {tech_stack}"
gitignore_path: {directory}/.gitignore
```

---

### Operation 3: Stage Files

**When to use:** Before committing changes.

**Input Parameters:**
```yaml
operation: add
directory: <absolute-path-to-project-root>
files: [<file-paths>] | null  # null means add all (git add .)
```

**Execution:**
```bash
cd {directory}

IF files is null:
  git add .
ELSE:
  FOR EACH file in files:
    git add {file}
```

**Output:**
```yaml
success: true | false
message: "Staged {count} files"
staged_files: [<file-paths>]
```

---

### Operation 4: Commit Changes

**When to use:** After staging files, with Task Data Model context.

**Input Parameters:**
```yaml
operation: commit
directory: <absolute-path-to-project-root>
task_data:
  task_id: TASK-XXX
  task_description: <description>
  feature_id: FEATURE-XXX | null
  # ... any other Task Data Model fields
```

**Commit Message Generation:**

**Format:**
```
{task_id} commit for {feature_context}: {summary}
```

**Rules:**
1. **task_id**: Always from `task_data.task_id`
2. **feature_context**: 
   - If `task_data.feature_id` exists: `"Feature-{feature_id}"`
   - Otherwise: omit "Feature-XXX" part (just "commit for:")
3. **summary**: 
   - Extract from `task_data.task_description`
   - Focus on "what changed" not "how"
   - Max 50 words
   - Use action verbs (Set up, Implement, Fix, Update, etc.)

**Examples:**
```
# With feature context
TASK-015 commit for Feature-FEATURE-003: Set up Flask development environment with static assets and templates structure

# Without feature context (standalone task)
TASK-001 commit for: Initialize Python project with uv and configure development environment

# Bug fix
TASK-042 commit for Feature-FEATURE-007: Fix authentication token validation in user login endpoint
```

**Execution:**
```bash
cd {directory}
git commit -m "{generated_message}"
```

**Output:**
```yaml
success: true | false
message: "Committed changes"
commit_hash: <git-commit-hash>
commit_message: "{generated_message}"
```

---

### Operation 5: Push to Remote

**When to use:** After committing, to sync with GitHub.

**Input Parameters:**
```yaml
operation: push
directory: <absolute-path-to-project-root>
remote: origin | <remote-name>  # Default: origin
branch: main | <branch-name>     # Default: current branch
```

**Execution:**
```bash
cd {directory}
git push {remote} {branch}
```

**Output:**
```yaml
success: true | false
message: "Pushed to {remote}/{branch}"
remote: {remote}
branch: {branch}
```

**Notes:**
- Requires remote to be configured (git remote add origin <url>)
- Requires authentication (SSH key or token)
- May fail if remote has changes (need to pull first)

---

### Operation 6: Pull from Remote

**When to use:** To sync local repository with GitHub changes.

**Input Parameters:**
```yaml
operation: pull
directory: <absolute-path-to-project-root>
remote: origin | <remote-name>  # Default: origin
branch: main | <branch-name>     # Default: current branch
```

**Execution:**
```bash
cd {directory}
git pull {remote} {branch}
```

**Output:**
```yaml
success: true | false
message: "Pulled from {remote}/{branch}"
remote: {remote}
branch: {branch}
changes: <summary-of-changes> | "Already up to date"
```

**Notes:**
- May result in merge conflicts (requires manual resolution)
- Use before pushing if remote may have changes

---

## Usage Examples

### Example 1: New Project Setup

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

### Example 2: Feature Development Commit

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

### Example 3: Push to GitHub

```yaml
# Push to main branch
operation: push
directory: /path/to/project
remote: origin
branch: main
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Not a git repository | Operation called before init | Run init operation first |
| Nothing to commit | No changes staged | Check if files were modified |
| Remote not found | Remote not configured | Use `git remote add origin <url>` |
| Push rejected | Remote has changes | Pull changes first, resolve conflicts |
| Merge conflict | Conflicting changes during pull | Manually resolve conflicts |

### Error Output Format

```yaml
success: false
error: <error-type>
message: <detailed-error-message>
suggestion: <how-to-fix>
```

---

## Integration with Other Skills

### Called by task-type-dev-environment

```yaml
# After creating project structure
1. Call git-version-control:
   operation: init
   directory: {project_root}

2. Call git-version-control:
   operation: create_gitignore
   directory: {project_root}
   tech_stack: {selected_stack}

3. Call git-version-control:
   operation: add
   directory: {project_root}
   files: null

4. Call git-version-control:
   operation: commit
   directory: {project_root}
   task_data: {current_task_data_model}
```

### Called by Other Task Types

Any task type can call this skill to commit their changes:

```yaml
# After completing work
1. Call git-version-control:
   operation: add
   directory: {project_root}
   files: [<modified-files>] | null

2. Call git-version-control:
   operation: commit
   directory: {project_root}
   task_data: {current_task_data_model}
```

---

## Best Practices

### Commit Frequency
- **After major milestones** - Environment setup, feature completion
- **Before blocking/deferring tasks** - Save progress
- **After successful testing** - Code works as expected

### Commit Message Quality
- Use task description as base
- Be specific about changes
- Keep under 50 words for summary
- Let auto-generation handle format

### Git Workflow
1. **Init** → **Create .gitignore** (once per project)
2. **Add** → **Commit** (iterative during development)
3. **Pull** → **Push** (when syncing with remote)

### .gitignore Management
- Create during project initialization
- Update when tech stack changes
- Manually edit for project-specific exclusions

---

## Templates Reference

See `templates/` directory for:
- `gitignore-python.txt` - Python project patterns
- `gitignore-nodejs.txt` - Node.js project patterns
- `commit-message-format.md` - Detailed commit message examples

---

## Notes

- This skill does **NOT** create GitHub repositories remotely
- Remote operations require manual GitHub setup first
- Commit messages follow structured format (not conventional commits)
- All operations are synchronous (blocking until complete)
- No automatic conflict resolution (manual intervention required)
