---
name: x-ipe-tool-git-version-control
description: Manage git version control operations including repository initialization, staging, committing, and GitHub integration. Provides standardized .gitignore templates and structured commit messages. Use for version control setup and management during development tasks.
---

# Git Version Control

## Purpose

AI Agents follow this skill to manage git version control to:
1. Check repository status and branch information
2. Initialize repositories and create .gitignore files
3. Stage, commit, push, and pull with structured commit messages

---

## Important Notes

BLOCKING: Directory must exist before any operation is called.
CRITICAL: This is a utility skill -- it does NOT follow the x-ipe-workflow-task-execution flow. Other skills call it directly.
CRITICAL: Commit messages are auto-generated from Task Data Model -- do not manually format them.

---

## About

A standardized interface for git operations used throughout the development lifecycle. Provides consistent commit message formatting tied to the Task Data Model and tech-stack-specific .gitignore templates.

**Key Concepts:**
- **Task Data Model** - Commit messages are generated from task_id, feature_id, and task_description fields
- **Commit Message Format** - `{task_id} commit for {feature_context}: {summary}` (see [references/commit-message-format.md](references/commit-message-format.md))
- **.gitignore Templates** - Pre-built patterns for Python and Node.js projects

---

## When to Use

```yaml
triggers:
  - "initialize git repository"
  - "commit changes"
  - "create gitignore"
  - "push to remote"
  - "pull from remote"
  - "check git status"

not_for:
  - "Creating GitHub repositories remotely"
  - "Resolving merge conflicts (manual intervention required)"
  - "Branch management or PR workflows"
```

---

## Input Parameters

```yaml
input:
  operation: "status | init | create_gitignore | add | commit | push | pull"
  directory: "<absolute-path-to-project-root>"
  # Operation-specific parameters:
  tech_stack: "python | nodejs"          # create_gitignore only
  files: "[<paths>] | null"             # add only; null = git add .
  task_data:                             # commit only
    task_id: "TASK-XXX"
    task_description: "<description>"
    feature_id: "FEATURE-XXX | null"
  remote: "origin | <remote-name>"       # push/pull only; default: origin
  branch: "main | <branch-name>"         # push/pull only; default: current branch
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Directory exists</name>
    <verification>Target directory is present on the filesystem</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Git repository exists (for non-init operations)</name>
    <verification>Run git status in directory -- must not return "not a git repository"</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Task Data Model available (for commit)</name>
    <verification>task_data with task_id and task_description is provided</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Status

**When:** Check if directory is a git repository and get current status.

```xml
<operation name="status">
  <action>
    1. cd {directory}
    2. Run: git status
    3. Parse branch, staged, modified, and untracked files
  </action>
  <output>
    success: true | false
    is_git_repo: true | false
    branch: current-branch | null
    has_uncommitted_changes: true | false
    staged_files: []
    modified_files: []
    untracked_files: []
  </output>
</operation>
```

### Operation: Init

**When:** Setting up a new project or converting existing directory to git repo.

```xml
<operation name="init">
  <action>
    1. cd {directory}
    2. Run: git init
  </action>
  <output>
    success: true | false
    message: "Initialized git repository at {directory}"
    repository_path: "{directory}"
  </output>
</operation>
```

### Operation: Create .gitignore

**When:** After repository initialization or when changing tech stack.

```xml
<operation name="create_gitignore">
  <action>
    1. Determine template: python -> templates/gitignore-python.txt, nodejs -> templates/gitignore-nodejs.txt
    2. Load template content
    3. Write to {directory}/.gitignore
  </action>
  <constraints>
    - BLOCKING: tech_stack must be "python" or "nodejs"
  </constraints>
  <output>
    success: true | false
    message: "Created .gitignore for {tech_stack}"
    gitignore_path: "{directory}/.gitignore"
  </output>
</operation>
```

### Operation: Stage Files

**When:** Before committing changes.

```xml
<operation name="add">
  <action>
    1. cd {directory}
    2. If files is null: run git add .
    3. If files provided: run git add {file} for each file
  </action>
  <output>
    success: true | false
    message: "Staged {count} files"
    staged_files: [file-paths]
  </output>
</operation>
```

### Operation: Commit

**When:** After staging files, with Task Data Model context.

```xml
<operation name="commit">
  <action>
    1. Generate commit message from task_data:
       - If feature_id exists: "{task_id} commit for Feature-{feature_id}: {summary}"
       - If feature_id null: "{task_id} commit for: {summary}"
    2. Summary: extract from task_description, max 50 words, use action verbs
    3. cd {directory}
    4. Run: git commit -m "{generated_message}"
  </action>
  <constraints>
    - BLOCKING: task_data.task_id is required
    - BLOCKING: task_data.task_description is required
    - Summary must focus on "what changed" not "how"
    - Max 50 words for summary
  </constraints>
  <output>
    success: true | false
    commit_hash: git-commit-hash
    commit_message: "{generated_message}"
  </output>
</operation>
```

### Operation: Push

**When:** After committing, to sync with GitHub.

```xml
<operation name="push">
  <action>
    1. cd {directory}
    2. Run: git push {remote} {branch}
  </action>
  <constraints>
    - Remote must be configured (git remote add origin url)
    - Authentication required (SSH key or token)
    - May fail if remote has changes (pull first)
  </constraints>
  <output>
    success: true | false
    message: "Pushed to {remote}/{branch}"
    remote: "{remote}"
    branch: "{branch}"
  </output>
</operation>
```

### Operation: Pull

**When:** To sync local repository with GitHub changes.

```xml
<operation name="pull">
  <action>
    1. cd {directory}
    2. Run: git pull {remote} {branch}
  </action>
  <constraints>
    - May result in merge conflicts (requires manual resolution)
    - Use before pushing if remote may have changes
  </constraints>
  <output>
    success: true | false
    message: "Pulled from {remote}/{branch}"
    remote: "{remote}"
    branch: "{branch}"
    changes: "summary-of-changes | Already up to date"
  </output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    message: "<operation-specific message>"
    # Additional fields vary per operation (see individual operations above)
  errors:
    error: "<error-type>"
    message: "<detailed-error-message>"
    suggestion: "<how-to-fix>"
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed successfully</name>
    <verification>success field returned true</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Git state is consistent</name>
    <verification>Run git status to confirm expected state after operation</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Commit message follows format (commit operation)</name>
    <verification>Message matches pattern: TASK-XXX commit for [Feature-FEATURE-XXX]: summary</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Not a git repository | Operation called before init | Run init operation first |
| Nothing to commit | No changes staged | Check if files were modified |
| Remote not found | Remote not configured | Use `git remote add origin <url>` |
| Push rejected | Remote has changes | Pull changes first, resolve conflicts |
| Merge conflict | Conflicting changes during pull | Manually resolve conflicts |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/gitignore-python.txt` | Python project .gitignore patterns |
| `templates/gitignore-nodejs.txt` | Node.js project .gitignore patterns |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples and integration patterns.
See [references/commit-message-format.md](references/commit-message-format.md) for detailed commit message guidelines.
