# Technical Design: FEATURE-041-D — New Workflow Actions

> Feature ID: FEATURE-041-D
> Version: v1.0
> Status: Designed
> Last Updated: 03-04-2026

## Part 1: Agent-Facing Summary

### Component Table

| # | Component | File | Change Type | Tag | Description |
|---|-----------|------|-------------|-----|-------------|
| C1 | Workflow Template | `src/x_ipe/resources/config/workflow-template.json` | Modify | `config` | Add test_generation to implement; replace quality_evaluation with code_refactor + feature_closing in validation; add human_playground to feedback; update change_request action_context |
| C2 | Backend Service | `src/x_ipe/services/workflow_manager_service.py` | Modify | `backend` | Update hardcoded _stage_config, _next_actions_map, _deliverable_categories |
| C3 | Frontend ACTION_MAP | `src/x_ipe/static/js/features/workflow-stage.js` | Modify | `frontend` | Add 4 actions, remove quality_evaluation from ACTION_MAP |
| C4 | Copilot Prompts | `src/x_ipe/resources/config/copilot-prompt.json` | Modify | `config` | Add 4 prompt entries (code_refactor, feature_closing, human_playground, change_request); update implementation input_source |
| C5 | Test Generation Skill | `.github/skills/x-ipe-task-based-test-generation/SKILL.md` | Modify | `skill` | Add update_workflow_action + extra_context_reference |
| C6 | Code Refactor Skill | `.github/skills/x-ipe-task-based-code-refactor/SKILL.md` | Modify | `skill` | Add update_workflow_action + extra_context_reference |
| C7 | Feature Closing Skill | `.github/skills/x-ipe-task-based-feature-closing/SKILL.md` | Modify | `skill` | Add update_workflow_action + extra_context_reference |
| C8 | Human Playground Skill | `.github/skills/x-ipe-task-based-human-playground/SKILL.md` | Modify | `skill` | Add update_workflow_action + extra_context_reference |
| C9 | Change Request Skill | `.github/skills/x-ipe-task-based-change-request/SKILL.md` | Modify | `skill` | Add update_workflow_action; update extra_context_reference keys |
| C10 | Backend Tests | `tests/test_workflow_manager.py` | Modify | `test` | Update assertions for new action layout |
| C11 | Frontend Tests | `tests/frontend-js/workflow-panel-actions.test.js` | Modify | `test` | Update action count, mandatory/optional expectations |

### Usage Example

After implementation, the workflow pipeline becomes:

```
ideation → requirement → implement → validation → feedback

implement:  feature_refinement → technical_design → test_generation → implementation
validation: acceptance_testing → code_refactor → feature_closing
feedback:   human_playground (opt) → change_request (opt)
```

---

## Part 2: Implementation Guide

### C1: workflow-template.json

**File:** `src/x_ipe/resources/config/workflow-template.json`

#### Change 1a: Add test_generation to implement stage (after technical_design, before implementation)

Insert new action between `technical_design` (line 74-80) and `implementation` (line 82-90). Update technical_design's next_actions_suggested from `["implementation"]` to `["test_generation"]`.

```json
"technical_design": {
  "optional": false,
  "action_context": {
    "specification": { "required": true, "candidates": "feature-docs-folder" }
  },
  "deliverables": ["$output:tech-design", "$output-folder:feature-docs-folder"],
  "next_actions_suggested": ["test_generation"]
},
"test_generation": {
  "optional": false,
  "action_context": {
    "tech-design": { "required": true, "candidates": "feature-docs-folder" },
    "specification": { "required": true, "candidates": "feature-docs-folder" }
  },
  "deliverables": ["$output:test-plan", "$output-folder:test-folder"],
  "next_actions_suggested": ["implementation"]
},
```

#### Change 1b: Replace quality_evaluation with code_refactor + feature_closing in validation stage

Replace lines 106-113 (quality_evaluation) with two new actions. Update acceptance_testing's next_actions_suggested from `["quality_evaluation"]` to `["code_refactor"]`.

```json
"acceptance_testing": {
  "optional": false,
  "action_context": {
    "specification": { "required": true, "candidates": "feature-docs-folder" },
    "impl-files": { "required": true, "candidates": "impl-folder" }
  },
  "deliverables": ["$output:test-report", "$output-folder:test-folder"],
  "next_actions_suggested": ["code_refactor"]
},
"code_refactor": {
  "optional": false,
  "action_context": {
    "test-report": { "required": false, "candidates": "test-folder" },
    "specification": { "required": true, "candidates": "feature-docs-folder" }
  },
  "deliverables": ["$output:refactor-report"],
  "next_actions_suggested": ["feature_closing"]
},
"feature_closing": {
  "optional": false,
  "action_context": {
    "specification": { "required": true, "candidates": "feature-docs-folder" },
    "refactor-report": { "required": false }
  },
  "deliverables": ["$output:closing-report"],
  "next_actions_suggested": ["human_playground", "change_request"]
}
```

#### Change 1c: Add human_playground to feedback stage, update change_request action_context

Insert human_playground before change_request. Update change_request action_context to reference `closing-report` instead of `eval-report`.

```json
"feedback": {
  "type": "per_feature",
  "next_stage": null,
  "actions": {
    "human_playground": {
      "optional": true,
      "action_context": {
        "specification": { "required": true, "candidates": "feature-docs-folder" },
        "impl-files": { "required": false, "candidates": "impl-folder" }
      },
      "deliverables": ["$output:playground-url"],
      "next_actions_suggested": ["change_request"]
    },
    "change_request": {
      "optional": true,
      "action_context": {
        "closing-report": { "required": false },
        "specification": { "required": true, "candidates": "feature-docs-folder" }
      },
      "deliverables": ["$output:cr-doc", "$output-folder:cr-folder"],
      "next_actions_suggested": []
    }
  }
}
```

---

### C2: workflow_manager_service.py

**File:** `src/x_ipe/services/workflow_manager_service.py`

All changes are in the `_default_config()` function (lines 117-175).

#### Change 2a: _stage_config (lines 132-149)

```python
"implement": {
    "type": "per_feature",
    "mandatory_actions": ["feature_refinement", "technical_design", "test_generation", "implementation"],
    "optional_actions": [],
    "next_stage": "validation",
},
"validation": {
    "type": "per_feature",
    "mandatory_actions": ["acceptance_testing", "code_refactor", "feature_closing"],
    "optional_actions": [],
    "next_stage": "feedback",
},
"feedback": {
    "type": "per_feature",
    "mandatory_actions": [],
    "optional_actions": ["human_playground", "change_request"],
    "next_stage": None,
},
```

#### Change 2b: _deliverable_categories (lines 152-159)

```python
deliverable_categories = {
    "compose_idea": "ideas", "refine_idea": "ideas",
    "reference_uiux": "mockups", "design_mockup": "mockups",
    "requirement_gathering": "requirements", "feature_breakdown": "requirements",
    "feature_refinement": "requirements", "technical_design": "requirements",
    "test_generation": "quality",
    "implementation": "implementations",
    "acceptance_testing": "quality", "code_refactor": "quality",
    "feature_closing": "quality", "human_playground": "quality",
    "change_request": "requirements",
}
```

#### Change 2c: _next_actions_map (lines 161-174)

```python
next_actions_map = {
    "compose_idea": ["refine_idea", "reference_uiux"],
    "refine_idea": ["design_mockup", "requirement_gathering"],
    "reference_uiux": ["design_mockup", "refine_idea"],
    "design_mockup": ["requirement_gathering"],
    "requirement_gathering": ["feature_breakdown"],
    "feature_breakdown": [],
    "feature_refinement": ["technical_design"],
    "technical_design": ["test_generation"],
    "test_generation": ["implementation"],
    "implementation": ["acceptance_testing"],
    "acceptance_testing": ["code_refactor"],
    "code_refactor": ["feature_closing"],
    "feature_closing": ["human_playground", "change_request"],
    "human_playground": ["change_request"],
    "change_request": [],
}
```

---

### C3: workflow-stage.js

**File:** `src/x_ipe/static/js/features/workflow-stage.js`

#### Change 3: ACTION_MAP (lines 83-103)

```javascript
implement: {
    label: 'Implement',
    actions: {
        feature_refinement: { label: 'Feature Refinement', icon: '📐', mandatory: true, interaction: 'cli', skill: 'x-ipe-task-based-feature-refinement' },
        technical_design:   { label: 'Technical Design',   icon: '⚙',  mandatory: true, interaction: 'cli', skill: 'x-ipe-task-based-technical-design' },
        test_generation:    { label: 'Test Generation',    icon: '🧪', mandatory: true, interaction: 'cli', skill: 'x-ipe-task-based-test-generation' },
        implementation:     { label: 'Implementation',     icon: '💻', mandatory: true, interaction: 'cli', skill: 'x-ipe-task-based-code-implementation' },
    }
},
validation: {
    label: 'Validation',
    actions: {
        acceptance_testing: { label: 'Acceptance Testing', icon: '✅', mandatory: true,  interaction: 'cli', skill: 'x-ipe-task-based-feature-acceptance-test' },
        code_refactor:      { label: 'Code Refactor',      icon: '🔧', mandatory: true,  interaction: 'cli', skill: 'x-ipe-task-based-code-refactor' },
        feature_closing:    { label: 'Feature Closing',    icon: '🏁', mandatory: true,  interaction: 'cli', skill: 'x-ipe-task-based-feature-closing' },
    }
},
feedback: {
    label: 'Feedback',
    actions: {
        human_playground: { label: 'Human Playground', icon: '🎮', mandatory: false, interaction: 'cli', skill: 'x-ipe-task-based-human-playground' },
        change_request:   { label: 'Change Request',   icon: '🔄', mandatory: false, interaction: 'cli', skill: 'x-ipe-task-based-change-request' },
    }
}
```

---

### C4: copilot-prompt.json

**File:** `src/x_ipe/resources/config/copilot-prompt.json`

#### Change 4a: Update implementation input_source (line 134)

```json
"input_source": ["test_generation"],
```

#### Change 4b: Add 4 new prompt entries after acceptance_testing (line 165)

Insert before the closing `]` of the workflow-prompts array:

```json
,
{
  "id": "code-refactor",
  "action": "code_refactor",
  "icon": "bi-wrench-adjustable",
  "input_source": ["acceptance_testing"],
  "prompt-details": [
    {
      "language": "en",
      "label": "Code Refactor",
      "command": "refactor code for $feature-id$ based on $output:test-report$ and $output:specification$ with code refactor skill"
    },
    {
      "language": "zh",
      "label": "代码重构",
      "command": "使用代码重构技能, 基于 $output:test-report$ 和 $output:specification$ 为 $feature-id$ 重构代码"
    }
  ]
},
{
  "id": "feature-closing",
  "action": "feature_closing",
  "icon": "bi-flag-fill",
  "input_source": ["code_refactor"],
  "prompt-details": [
    {
      "language": "en",
      "label": "Feature Closing",
      "command": "close feature $feature-id$ with $output:specification$ and $output:refactor-report$ using feature closing skill"
    },
    {
      "language": "zh",
      "label": "功能关闭",
      "command": "使用功能关闭技能, 基于 $output:specification$ 和 $output:refactor-report$ 关闭 $feature-id$"
    }
  ]
},
{
  "id": "human-playground",
  "action": "human_playground",
  "icon": "bi-controller",
  "input_source": ["implementation"],
  "prompt-details": [
    {
      "language": "en",
      "label": "Human Playground",
      "command": "create interactive playground for $feature-id$ from $output:specification$ and $output:impl-files$ with human playground skill"
    },
    {
      "language": "zh",
      "label": "人工验证",
      "command": "使用人工验证技能, 从 $output:specification$ 和 $output:impl-files$ 为 $feature-id$ 创建交互式验证环境"
    }
  ]
},
{
  "id": "change-request",
  "action": "change_request",
  "icon": "bi-arrow-repeat",
  "input_source": ["feature_closing"],
  "prompt-details": [
    {
      "language": "en",
      "label": "Change Request",
      "command": "create change request for $feature-id$ based on $output:closing-report$ and $output:specification$ with change request skill"
    },
    {
      "language": "zh",
      "label": "变更请求",
      "command": "使用变更请求技能, 基于 $output:closing-report$ 和 $output:specification$ 为 $feature-id$ 创建变更请求"
    }
  ]
}
```

---

### C5–C9: Skill SKILL.md Updates

All 5 skills need the same pattern added. The pattern comes from FEATURE-041-C (already established in the 8 core skills).

#### Pattern: update_workflow_action block

Add to the final/completion step of each skill, inside the `<action>` block:

```markdown
1. IF execution_mode == "workflow-mode":
   a. Call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server with:
      - workflow_name: {from context}
      - action: "{action_key}"
      - status: "done"
      - feature_id: {feature_id}
      - deliverables: {keyed dict of deliverable paths}
   b. Log: "Workflow action status updated to done"
```

#### Pattern: extra_context_reference in input parameters

Add under `workflow:` in the input YAML:

```yaml
workflow:
  name: "N/A"
  extra_context_reference:
    {key1}: "path | N/A | auto-detect"
    {key2}: "path | N/A | auto-detect"
```

#### Per-skill details:

| Skill | action_key | extra_context_reference keys | deliverables dict |
|-------|-----------|---------------------------|-------------------|
| C5: test-generation | `test_generation` | `tech-design`, `specification` | `{"test-plan": "{path}", "test-folder": "{path}"}` |
| C6: code-refactor | `code_refactor` | `test-report`, `specification` | `{"refactor-report": "{path}"}` |
| C7: feature-closing | `feature_closing` | `specification`, `refactor-report` | `{"closing-report": "{path}"}` |
| C8: human-playground | `human_playground` | `specification`, `impl-files` | `{"playground-url": "{path}"}` |
| C9: change-request | `change_request` | `closing-report`, `specification` (update from `eval-report`) | `{"cr-doc": "{path}", "cr-folder": "{path}"}` |

---

### C10: Backend Tests

**File:** `tests/test_workflow_manager.py`

Tests that reference action lists, _next_actions_map, or _deliverable_categories need updating:
- Any test checking implement mandatory_actions → add `"test_generation"`
- Any test checking validation mandatory/optional → replace `quality_evaluation` with `code_refactor`, `feature_closing`
- Any test checking feedback optional_actions → add `"human_playground"`
- Any test checking next_actions transitions → update chain
- Any test checking deliverable_categories → add new entries, remove `quality_evaluation`

### C11: Frontend Tests

**File:** `tests/frontend-js/workflow-panel-actions.test.js`

- Action count assertions: total actions increase from 12 to 16
- Stage-specific action counts: implement 3→4, validation 2→3, feedback 1→2
- Any test referencing `quality_evaluation` → update to `code_refactor`

---

### Implementation Order

1. **C1** (workflow-template.json) — config is authoritative source
2. **C2** (workflow_manager_service.py) — backend hardcoded fallback must match
3. **C3** (workflow-stage.js) — frontend must match template
4. **C4** (copilot-prompt.json) — prompts must reference correct deliverables
5. **C10 + C11** (tests) — update tests before running
6. **C5–C9** (skills) — skill updates are independent of app code
7. Run full test suite to verify

### Risks

- **Risk 1:** Existing workflow instances with `quality_evaluation` data. Mitigation: The backend already handles unknown actions gracefully — `_evaluate_stage_gating` is a no-op (line 789), and action status lookups use `.get()` with defaults.
- **Risk 2:** workflow-stage.js size approaching 20KB limit after adding 4 actions (~120 chars each). Mitigation: ~480 bytes added, well within limit.
