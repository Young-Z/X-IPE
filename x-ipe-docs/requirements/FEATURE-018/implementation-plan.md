# Implementation Plan: FEATURE-018 X-IPE CLI Tool

> Created: 01-25-2026  
> Strategy: Incremental phases that don't break existing features

---

## Overview

This plan breaks FEATURE-018 into 6 safe phases. Each phase:
- Is independently testable
- Doesn't break existing `main.py` + `src/` structure
- Can be merged/deployed separately

---

## Phase Summary

| Phase | Description | Risk | Existing Code Impact |
|-------|-------------|------|---------------------|
| 1 | Core modules (config, hashing) | Low | None - new files only |
| 2 | Scaffold module | Low | None - new files only |
| 3 | Skills manager module | Low | None - new files only |
| 4 | CLI entry point + status/info | Low | None - adds CLI alongside |
| 5 | CLI init command | Low | None - creates project files |
| 6 | CLI serve command | Medium | Reuses existing app.py |
| 7 | CLI upgrade command | Low | Uses skills manager |
| 8 | Package restructure (optional) | High | Moves files, updates imports |

---

## Phase 1: Core Modules

**Goal:** Create foundational modules without touching existing code.

**New Files:**
```
src/
└── x_ipe/                    # New subpackage
    ├── __init__.py           # Package version
    ├── core/
    │   ├── __init__.py
    │   ├── config.py         # XIPEConfig class
    │   ├── hashing.py        # hash_file, hash_directory
    │   └── paths.py          # Path resolution utilities
```

**Tests to Pass:** 25 tests
- TestConfigModule (10)
- TestHashingModule (5)
- TestPackageStructure (partial: 2)

**Acceptance Criteria:**
- [ ] `from src.x_ipe.core.config import XIPEConfig` works
- [ ] `from src.x_ipe.core.hashing import hash_file` works
- [ ] Existing `python main.py` still works
- [ ] Existing tests still pass

---

## Phase 2: Scaffold Module

**Goal:** Create scaffolding utilities for project initialization.

**New Files:**
```
src/x_ipe/
└── core/
    └── scaffold.py           # ScaffoldManager class
```

**New Package Data:**
```
src/x_ipe/
└── scaffolds/                # Template files
    ├── x-ipe-docs/
    │   ├── ideas/.gitkeep
    │   ├── planning/task-board.md
    │   ├── requirements/.gitkeep
    │   └── themes/.gitkeep
    ├── github/
    │   └── copilot-instructions.md
    └── config/
        └── x-ipe.yaml.template
```

**Tests to Pass:** 8 tests
- TestScaffoldModule (8)

**Acceptance Criteria:**
- [ ] ScaffoldManager can create x-ipe-docs/ structure
- [ ] ScaffoldManager can copy templates
- [ ] Dry-run mode works
- [ ] Existing tests still pass

---

## Phase 3: Skills Manager Module

**Goal:** Create skills discovery and synchronization utilities.

**New Files:**
```
src/x_ipe/
└── core/
    └── skills.py             # SkillsManager, SkillInfo classes
```

**Tests to Pass:** 10 tests
- TestSkillsModule (10)

**Acceptance Criteria:**
- [ ] SkillsManager discovers package skills (from .github/skills/)
- [ ] SkillsManager discovers local skills
- [ ] Hash comparison works
- [ ] Backup functionality works
- [ ] Existing tests still pass

---

## Phase 4: CLI Entry Point + Status/Info

**Goal:** Create CLI with basic diagnostic commands.

**New Files:**
```
src/x_ipe/
├── cli.py                    # Click CLI main group
└── commands/
    ├── __init__.py
    ├── status.py             # x-ipe status
    └── info.py               # x-ipe info
```

**pyproject.toml Update:**
```toml
[project.scripts]
x-ipe = "src.x_ipe.cli:main"
```

**Tests to Pass:** 26 tests
- TestCLIEntryPoint (8)
- TestStatusCommand (8)
- TestInfoCommand (10)

**Acceptance Criteria:**
- [ ] `uv run x-ipe --help` works
- [ ] `uv run x-ipe status` shows project status
- [ ] `uv run x-ipe info` shows diagnostics
- [ ] Existing `python main.py` still works

---

## Phase 5: CLI Init Command

**Goal:** Implement project initialization command.

**New Files:**
```
src/x_ipe/
└── commands/
    └── init.py               # x-ipe init
```

**Tests to Pass:** 15 tests
- TestInitCommand (15)

**Acceptance Criteria:**
- [ ] `x-ipe init` creates x-ipe-docs/, .x-ipe/, .github/skills/
- [ ] `--force` flag works
- [ ] `--dry-run` flag works
- [ ] Git-aware .gitignore updates
- [ ] Existing tests still pass

---

## Phase 6: CLI Serve Command

**Goal:** Implement server launch command that reuses existing Flask app.

**New Files:**
```
src/x_ipe/
└── commands/
    └── serve.py              # x-ipe serve
```

**Strategy:** Import and reuse existing `src.app.create_app()` and `src.app.socketio`.

**Tests to Pass:** 12 tests
- TestServeCommand (12)

**Acceptance Criteria:**
- [ ] `x-ipe serve` starts server
- [ ] `--port`, `--host`, `--open`, `--debug` flags work
- [ ] Loads config from .x-ipe.yaml
- [ ] `python main.py` still works as before

---

## Phase 7: CLI Upgrade Command

**Goal:** Implement skills upgrade command.

**New Files:**
```
src/x_ipe/
└── commands/
    └── upgrade.py            # x-ipe upgrade
```

**Tests to Pass:** 12 tests
- TestUpgradeCommand (12)

**Acceptance Criteria:**
- [ ] `x-ipe upgrade` syncs skills
- [ ] Detects modified skills
- [ ] Creates backups
- [ ] `--force` and `--dry-run` flags work

---

## Phase 8: Package Restructure (Optional/Future)

**Goal:** Full PyPI-ready package structure.

**Changes:**
1. Move `src/` contents to `src/x_ipe/`
2. Update all imports
3. Bundle skills as package data
4. Publish to PyPI

**Risk:** High - touches many files
**Recommendation:** Do this in a separate PR after CLI is stable

---

## Dependency Graph

```
Phase 1 (Core) ─┬─► Phase 2 (Scaffold) ─┬─► Phase 5 (Init)
                │                        │
                └─► Phase 3 (Skills) ────┴─► Phase 7 (Upgrade)
                │
                └─► Phase 4 (CLI+Status/Info) ─► Phase 6 (Serve)
```

---

## Test Progress Tracking

| Phase | Tests | Status |
|-------|-------|--------|
| 1 - Core Modules | 15/15 | ⬜ Not started |
| 2 - Scaffold | 8/8 | ⬜ Not started |
| 3 - Skills Manager | 10/10 | ⬜ Not started |
| 4 - CLI + Status/Info | 26/26 | ⬜ Not started |
| 5 - Init Command | 15/15 | ⬜ Not started |
| 6 - Serve Command | 12/12 | ⬜ Not started |
| 7 - Upgrade Command | 12/12 | ⬜ Not started |
| **Total** | **103/103** | **0% complete** |

---

## Notes

- Each phase creates a separate task on the task board
- Tests are run after each phase to ensure no regressions
- `main.py` and existing `src/app.py` remain unchanged until Phase 8
- CLI adds functionality alongside, not replacing existing entry points
