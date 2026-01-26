# Idea Summary

> Idea ID: IDEA-004
> Folder: Draft Idea - 01232026 131611
> Version: v1
> Created: 2026-01-23
> Status: Refined

## Overview

Enable X-IPE to operate within a nested folder structure where the X-IPE application lives as a subfolder inside a larger project root. This allows X-IPE to serve as a transparent tool for projects built by AI agents, showing the full project context rather than just the X-IPE app folder.

## Problem Statement

Currently X-IPE shows its own folder as the project root. When X-IPE is deployed as a subfolder within a larger project (e.g., `project-root/x-ipe/`), users cannot easily browse the parent project's files (docs, .github/skills, etc.) from within X-IPE.

## Target Users

- Developers using X-IPE to monitor AI agent-built applications
- Users who want X-IPE to show full project context (skills, docs, source code)
- Projects where X-IPE is embedded as a development tool

## Proposed Solution

Introduce a `.x-ipe.yaml` configuration file at the project root that defines:
1. The project root path (for file tree browsing)
2. The X-IPE app path (for running the application)
3. Default behaviors for file tree scope and terminal working directory

### Configuration File Structure

```yaml
# .x-ipe.yaml - placed at project root
version: 1
paths:
  project_root: "."              # Relative to this config file
  x_ipe_app: "./x-ipe"          # Path to X-IPE application
defaults:
  file_tree_scope: "project_root"  # or "x_ipe_app"
  terminal_cwd: "project_root"
```

### Expected Folder Structure

```
project-root/           ← project_root (shown in file tree by default)
├── .x-ipe.yaml         ← Configuration file
├── x-ipe/              ← x_ipe_app path
│   ├── main.py
│   ├── src/
│   └── ...
├── .github/skills/     ← Visible in file tree
├── x-ipe-docs/               ← Visible in file tree
└── ...
```

## Key Features

| Feature | Description | Priority |
|---------|-------------|----------|
| Config file support | Read `.x-ipe.yaml` from project root or parent directories | High |
| Config discovery | Look in cwd first, then traverse parent directories | High |
| Dual path awareness | Store both project_root and x_ipe_app paths | High |
| File tree scope | Default to project_root, allow switching in UI | High |
| Terminal cwd | Start terminal at project_root (configurable) | Medium |
| Launch flexibility | Support running from project root OR x-ipe folder | Medium |

## Success Criteria

- [ ] X-IPE finds `.x-ipe.yaml` when run from any directory within the project
- [ ] File tree shows project root by default when configured
- [ ] UI allows switching between project_root and x_ipe_app views
- [ ] Terminal starts at configured working directory
- [ ] Works whether launched from project root or x-ipe subfolder

## Constraints & Considerations

- **Backward compatibility**: Must work without `.x-ipe.yaml` (current behavior as fallback)
- **Path resolution**: All paths in config are relative to the config file location
- **Settings persistence**: Existing SQLite settings should coexist with file-based config
- **Security**: Config file paths should be validated (no traversal outside project)

## Brainstorming Notes

**Key decisions made:**
1. Configuration lives in `.x-ipe.yaml` at project root (file-based, not UI settings)
2. Config discovery: check cwd, then traverse parents until found
3. Default file tree scope: project root with UI switch capability
4. Terminal cwd: project root by default (not x-ipe subfolder)
5. Support launching from either project root or x-ipe folder

**Implementation considerations:**
- Add config loader service to parse `.x-ipe.yaml`
- Modify ProjectService to use configured project_root
- Add UI toggle between "Project" and "X-IPE App" views
- Update Settings page to show detected config (read-only display)

## Source Files

- new idea.md

## Next Steps

- [ ] Proceed to Requirement Gathering
