# DAO Decisions — Technical Design (EPIC-054)

## DAO-108: Technical Design Decisions

**Task:** TASK-1047 — Technical Design for all 6 EPIC-054 features
**Invocation:** Auto (DAO mode — pipeline)
**Confidence:** 0.90

### Decisions Made

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| Q1 | Overall architecture pattern | Single `tracker-toolbar.js` IIFE containing RecordingEngine, PIIMasker, TrackerToolbox, BackupManager + Python skill scripts for orchestration and post-processing | KISS: single injection point avoids multiple evaluate_script calls; DRY: shared state within IIFE |
| Q2 | File organization | Skill folder: `.github/skills/x-ipe-learning-behavior-tracker-for-web/` with scripts/ and references/ | Follows existing skill pattern (UIUX reference) |
| Q3 | GUI integration approach | Extend existing `workplace.html` + new `learn-panel.js` feature module + new Flask route | DRY: reuse existing WorkplaceManager, TerminalManager, ContentViewer |
| Q4 | Shadow DOM mode | `mode: 'closed'` for toolbox | Security: prevents target page from accessing toolbox internals |
| Q5 | z-index strategy | Toolbox: 2147483640, EPIC-030-B toolbar: 2147483647 | Spec requirement: EPIC-030-B toolbar higher priority |
| Q6 | Post-processing LLM fallback | Template-based narrative if LLM unavailable | KISS: graceful degradation without blocking output |
| Q7 | program_type assignments | A=frontend, B=backend, C=frontend, D=frontend, E=frontend, F=backend | Natural split: Python orchestration/processing vs. injected JS |
| Q8 | IIFE guard mechanism | `window.__xipeBehaviorTrackerInjected` flag | Prevents double-injection on re-inject; matches UIUX reference pattern |

### Design Architecture Summary

```
Python Layer (Backend):
  track_behavior.py   → BehaviorTrackerSkill + InjectionManager
  post_processor.py   → PostProcessor + SchemaFormatter

JavaScript Layer (Injected IIFE):
  tracker-toolbar.js  → RecordingEngine + CircularBuffer + EventSerializer
                      → PIIMasker
                      → TrackerToolbox (Shadow DOM)
                      → BackupManager (LocalStorage)

Workplace GUI (Frontend):
  learn-panel.js      → LearnPanelManager
  learn.py            → Flask session API routes
  workplace.html      → Template modifications
```
