"""
Tests for FEATURE-041-G: Skill Extra Context Reference

Covers:
- SKILL.md files contain extra_context_reference in workflow input block
- Context ref names match action_context from workflow-template.json
- Skills have free-mode backward compatibility (no extra_context_reference required)

TDD: All tests written before implementation — all should FAIL initially.

Note: This feature is SKILL.md documentation edits only. Tests validate
the presence and correctness of the extra_context_reference parameter
in skill files, not runtime behavior.
"""
import json
import os
import re
from pathlib import Path

import pytest
import copy
from tests.test_architecture_draw_skill import (
    frontmatter, linked_resource, section, yaml_contract,
)

SKILLS_DIR = Path(__file__).resolve().parent.parent / ".github" / "skills"
ROOT = SKILLS_DIR.parents[1]

# Scope stays the original nine skills; action/context authority is current app data.
SCOPED_SKILLS = [
    'ideation', 'idea-mockup', 'requirement-gathering', 'feature-breakdown',
    'feature-refinement', 'technical-design', 'code-implementation',
    'feature-acceptance-test', 'change-request',
]
TEMPLATE = json.loads((ROOT / 'x-ipe-docs/config/workflow-template.json').read_text())
ACTION_SOURCE = (ROOT / 'src/x_ipe/static/js/features/workflow-stage.js').read_text()
ACTION_BLOCK = ACTION_SOURCE.split('    ACTION_MAP: {', 1)[1].split('    /** Main entry:', 1)[0]
ACTION_SKILLS = dict(re.findall(
    r"^\s*(\w+):\s*\{[^\n]*skill:\s*'([^']+)'", ACTION_BLOCK, re.M,
))


def action_context(action):
    matches = [stage['actions'][action].get('action_context', {})
               for stage in TEMPLATE['stages'].values() if action in stage['actions']]
    assert len(matches) == 1, f'Missing/ambiguous action: {action}'
    return matches[0]


SKILL_ACTION_MAP = {}
for short_name in SCOPED_SKILLS:
    name = 'x-ipe-task-based-' + short_name
    actions = [action for action, skill in ACTION_SKILLS.items() if skill == name]
    assert len(actions) == 1, f'Missing/ambiguous ACTION_MAP association: {name}'
    SKILL_ACTION_MAP[name] = (actions[0], list(action_context(actions[0])))


def validate_context(input_data, expected_action, contexts):
    assert input_data.get('execution_mode') is not None
    workflow = input_data['workflow']
    assert workflow['action'] == expected_action, 'Incorrect workflow action'
    refs = workflow['extra_context_reference']
    assert isinstance(refs, dict), 'Context refs must be a mapping'
    required = {name for name, definition in contexts.items() if definition['required']}
    assert required <= refs.keys(), 'Missing required input context'
    assert set(refs) == set(contexts), 'Context keys differ from current workflow template'
    for name, value in refs.items():
        assert isinstance(value, str) and 'auto-detect' in value and 'N/A' in value, name
    return refs


# ==============================================================================
# Tests: extra_context_reference Presence
# ==============================================================================

class TestExtraContextReferencePresence:
    """Verify each workflow-aware skill declares extra_context_reference."""

    @pytest.mark.parametrize("skill_name,action_refs", [
        (name, refs) for name, (_, refs) in SKILL_ACTION_MAP.items()
    ])
    def test_skill_has_extra_context_reference(self, skill_name, action_refs):
        """SKILL.md should contain extra_context_reference in workflow input block."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Skill file not found: {skill_path}"

        content = skill_path.read_text()
        frontmatter(content, skill_name)
        data = yaml_contract(content, 'Input Parameters', 'input')
        assert isinstance(data['workflow']['extra_context_reference'], dict)

    @pytest.mark.parametrize("skill_name,expected_refs", [
        (name, refs) for name, (_, refs) in SKILL_ACTION_MAP.items()
    ])
    def test_skill_declares_correct_ref_names(self, skill_name, expected_refs):
        """SKILL.md extra_context_reference should list the correct ref names."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        data = yaml_contract(content, 'Input Parameters', 'input')
        action = SKILL_ACTION_MAP[skill_name][0]
        validate_context(data, action, action_context(action))


# ==============================================================================
# Tests: Execution Procedure Context Handling
# ==============================================================================

class TestExecutionProcedureUpdates:
    """Verify execution procedures reference extra_context_reference."""

    @pytest.mark.parametrize("skill_name", list(SKILL_ACTION_MAP.keys()))
    def test_procedure_references_extra_context(self, skill_name):
        """Execution procedure should mention extra_context_reference handling."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        initialization = section(content, 'Input Parameters').split('### Input Initialization', 1)[1]
        procedure = section(content, 'Execution Procedure')
        assert re.search(r'<procedure\b[^>]*>.*<action>.+?</action>.*</procedure>', procedure, re.S)
        if skill_name in {'x-ipe-task-based-ideation', 'x-ipe-task-based-idea-mockup'}:
            # Legacy handlers are real but do not enforce required template refs.
            # Preserve this gap as a finding, not a claimed lifecycle adoption.
            handler = procedure if skill_name.endswith('-ideation') else initialization
            assert 'extra_context_reference' in handler and 'auto-detect' in handler
            assert 'N/A' in handler and re.search(r'skip', handler, re.I)
            assert 'references/lifecycle.md' not in content
            for name in SKILL_ACTION_MAP[skill_name][1]:
                assert name in handler
            if skill_name.endswith('-idea-mockup'):
                guide = linked_resource(skill_path, '.github/skills/x-ipe-task-based-idea-mockup/references/mockup-guidelines.md')
                assert 'Current Idea Folder' in guide and 'Extra Instructions' in guide
        else:
            assert 'workflow.extra_context_reference' in initialization
            assert re.search(r'broken|invalid|explicit', initialization, re.I)
            common = linked_resource(skill_path, '.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md')
            resolution = section(common, 'Source artifact resolution')
            assert 'Explicit broken' in resolution and 'never mask' in resolution
            assert 'template action_context.required' in resolution


# ==============================================================================
# Tests: Backward Compatibility
# ==============================================================================

class TestBackwardCompatibility:
    """Verify skills don't require extra_context_reference (free-mode compat)."""

    @pytest.mark.parametrize("skill_name", list(SKILL_ACTION_MAP.keys()))
    def test_extra_context_reference_is_optional(self, skill_name):
        """extra_context_reference should default to N/A, not be required."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_path.read_text()
        data = yaml_contract(content, 'Input Parameters', 'input')
        assert 'free-mode' in data['execution_mode']
        assert 'N/A' in data['workflow']['name']
        for value in data['workflow']['extra_context_reference'].values():
            assert 'N/A' in value and 'auto-detect' in value


@pytest.mark.parametrize('skill_name', list(SKILL_ACTION_MAP))
def test_missing_required_context_cannot_be_hidden_in_prose(skill_name):
    content = (SKILLS_DIR / skill_name / 'SKILL.md').read_text()
    data = yaml_contract(content, 'Input Parameters', 'input')
    action = SKILL_ACTION_MAP[skill_name][0]
    contexts = action_context(action)
    required = next(name for name, definition in contexts.items() if definition['required'])
    corrupt = copy.deepcopy(data)
    del corrupt['workflow']['extra_context_reference'][required]
    corrupt['description'] = f'{required} still mentioned outside workflow input'
    with pytest.raises(AssertionError, match='Missing required input context'):
        validate_context(corrupt, action, contexts)


def test_change_request_current_optional_report_is_not_legacy_eval_report():
    action, refs = SKILL_ACTION_MAP['x-ipe-task-based-change-request']
    assert action_context(action)['closing-report']['required'] is False
    assert 'closing-report' in refs and 'eval-report' not in refs


def test_wrong_action_and_legacy_report_corruption_are_detected():
    data = yaml_contract((SKILLS_DIR / 'x-ipe-task-based-change-request/SKILL.md').read_text(), 'Input Parameters', 'input')
    corrupt = copy.deepcopy(data)
    corrupt['workflow']['action'] = 'implementation'
    with pytest.raises(AssertionError, match='Incorrect workflow action'):
        validate_context(corrupt, 'change_request', action_context('change_request'))
    corrupt = copy.deepcopy(data)
    corrupt['workflow']['extra_context_reference']['eval-report'] = corrupt['workflow']['extra_context_reference'].pop('closing-report')
    with pytest.raises(AssertionError, match='Context keys differ'):
        validate_context(corrupt, 'change_request', action_context('change_request'))


# ==============================================================================
# Tests: Deprecation Note
# ==============================================================================

class TestInputSourceDeprecation:
    """Verify input_source deprecation is documented."""

    def test_copilot_prompt_deprecation_documented(self):
        """copilot-prompt.json or its docs should mention input_source deprecation."""
        config_dir = Path(__file__).resolve().parent.parent / "x-ipe-docs" / "config"
        copilot_prompt = config_dir / "copilot-prompt.json"

        if not copilot_prompt.exists():
            pytest.skip("copilot-prompt.json not found")

        content = copilot_prompt.read_text()
        # Either the JSON has a deprecation comment or there's a separate doc
        # For JSON files, comments aren't standard, so check for deprecated flag or doc
        has_deprecation = (
            "deprecated" in content.lower()
            or "DEPRECATED" in content
        )

        if not has_deprecation:
            # Check if there's a README or doc file
            readme = config_dir / "README.md"
            if readme.exists():
                has_deprecation = "input_source" in readme.read_text() and "deprecated" in readme.read_text().lower()

        # This test will fail until deprecation note is added
        assert has_deprecation, (
            "input_source deprecation note not found in copilot-prompt.json or config docs"
        )
