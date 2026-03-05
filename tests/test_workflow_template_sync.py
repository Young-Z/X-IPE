"""
Test: Verify x-ipe-docs/config/ files are in sync with
src/x_ipe/resources/config/ (the source of truth).

TASK-731: Feedback-20260305-093837 — some actions missing action_context
and instructions because the docs config was outdated.
"""

import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCS_CONFIG = PROJECT_ROOT / "x-ipe-docs" / "config"
BUNDLED_CONFIG = PROJECT_ROOT / "src" / "x_ipe" / "resources" / "config"

DOCS_TEMPLATE = DOCS_CONFIG / "workflow-template.json"
BUNDLED_TEMPLATE = BUNDLED_CONFIG / "workflow-template.json"

DOCS_PROMPT = DOCS_CONFIG / "copilot-prompt.json"
BUNDLED_PROMPT = BUNDLED_CONFIG / "copilot-prompt.json"


@pytest.fixture
def docs_template():
    return json.loads(DOCS_TEMPLATE.read_text(encoding="utf-8"))


@pytest.fixture
def bundled_template():
    return json.loads(BUNDLED_TEMPLATE.read_text(encoding="utf-8"))


@pytest.fixture
def docs_prompt():
    return json.loads(DOCS_PROMPT.read_text(encoding="utf-8"))


@pytest.fixture
def bundled_prompt():
    return json.loads(BUNDLED_PROMPT.read_text(encoding="utf-8"))


class TestWorkflowTemplateSync:
    """Ensure docs config and bundled resource templates are identical."""

    def test_templates_are_identical(self, docs_template, bundled_template):
        """Both workflow-template.json files must have identical content."""
        assert docs_template == bundled_template, (
            "x-ipe-docs/config/workflow-template.json is out of sync with "
            "src/x_ipe/resources/config/workflow-template.json"
        )

    def test_all_actions_have_action_context(self, docs_template):
        """Every action in the template must define action_context,
        except compose_idea and reference_uiux (first actions with no inputs)."""
        NO_CONTEXT_ACTIONS = {"compose_idea", "reference_uiux"}
        missing = []
        for stage_name, stage in docs_template.get("stages", {}).items():
            for action_name, action_def in stage.get("actions", {}).items():
                if action_name in NO_CONTEXT_ACTIONS:
                    continue
                if "action_context" not in action_def:
                    missing.append(f"{stage_name}.{action_name}")
        assert not missing, (
            f"Actions missing action_context: {missing}"
        )


class TestCopilotPromptSync:
    """Ensure docs copilot-prompt.json and bundled resource are identical."""

    def test_prompts_are_identical(self, docs_prompt, bundled_prompt):
        """Both copilot-prompt.json files must have identical content."""
        assert docs_prompt == bundled_prompt, (
            "x-ipe-docs/config/copilot-prompt.json is out of sync with "
            "src/x_ipe/resources/config/copilot-prompt.json"
        )

    def test_all_workflow_actions_have_instructions(self, docs_prompt, docs_template):
        """Every action in the workflow template must have a matching
        instruction entry in copilot-prompt.json workflow-prompts."""
        NO_CONTEXT_ACTIONS = {"compose_idea", "reference_uiux"}
        prompt_actions = {
            p["action"] for p in docs_prompt.get("workflow-prompts", [])
        }
        template_actions = set()
        for stage in docs_template.get("stages", {}).values():
            for action_name in stage.get("actions", {}):
                if action_name not in NO_CONTEXT_ACTIONS:
                    template_actions.add(action_name)

        missing = template_actions - prompt_actions
        assert not missing, (
            f"Actions in workflow-template.json without instructions "
            f"in copilot-prompt.json: {missing}"
        )
