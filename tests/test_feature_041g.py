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

SKILLS_DIR = Path(__file__).resolve().parent.parent / ".github" / "skills"

# Mapping: skill_name -> (action_name, expected_context_refs)
SKILL_ACTION_MAP = {
    "x-ipe-task-based-ideation": ("refine_idea", ["raw-ideas", "uiux-reference"]),
    "x-ipe-task-based-idea-mockup": ("design_mockup", ["refined-idea", "uiux-reference"]),
    "x-ipe-task-based-requirement-gathering": ("requirement_gathering", ["refined-idea", "mockup-html"]),
    "x-ipe-task-based-feature-breakdown": ("feature_breakdown", ["requirement-doc"]),
    "x-ipe-task-based-feature-refinement": ("feature_refinement", ["requirement-doc", "features-list"]),
    "x-ipe-task-based-technical-design": ("technical_design", ["specification"]),
    "x-ipe-task-based-code-implementation": ("implementation", ["tech-design", "specification"]),
    "x-ipe-task-based-feature-acceptance-test": ("acceptance_testing", ["specification", "impl-files"]),
    "x-ipe-task-based-change-request": ("change_request", ["eval-report", "specification"]),
}


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
        assert "extra_context_reference" in content, (
            f"{skill_name}/SKILL.md missing 'extra_context_reference' in workflow input block"
        )

    @pytest.mark.parametrize("skill_name,expected_refs", [
        (name, refs) for name, (_, refs) in SKILL_ACTION_MAP.items()
    ])
    def test_skill_declares_correct_ref_names(self, skill_name, expected_refs):
        """SKILL.md extra_context_reference should list the correct ref names."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        if not skill_path.exists():
            pytest.skip(f"Skill {skill_name} not found")

        content = skill_path.read_text()
        for ref_name in expected_refs:
            assert ref_name in content, (
                f"{skill_name}/SKILL.md missing context ref '{ref_name}' "
                f"in extra_context_reference block"
            )


# ==============================================================================
# Tests: Execution Procedure Context Handling
# ==============================================================================

class TestExecutionProcedureUpdates:
    """Verify execution procedures reference extra_context_reference."""

    @pytest.mark.parametrize("skill_name", list(SKILL_ACTION_MAP.keys()))
    def test_procedure_references_extra_context(self, skill_name):
        """Execution procedure should mention extra_context_reference handling."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        if not skill_path.exists():
            pytest.skip(f"Skill {skill_name} not found")

        content = skill_path.read_text()
        # Should have conditional logic for extra_context_reference
        has_conditional = (
            "extra_context_reference" in content
            and ("auto-detect" in content.lower() or "auto_detect" in content.lower())
        )
        assert has_conditional, (
            f"{skill_name}/SKILL.md procedure should reference extra_context_reference "
            f"with auto-detect handling"
        )


# ==============================================================================
# Tests: Backward Compatibility
# ==============================================================================

class TestBackwardCompatibility:
    """Verify skills don't require extra_context_reference (free-mode compat)."""

    @pytest.mark.parametrize("skill_name", list(SKILL_ACTION_MAP.keys()))
    def test_extra_context_reference_is_optional(self, skill_name):
        """extra_context_reference should default to N/A, not be required."""
        skill_path = SKILLS_DIR / skill_name / "SKILL.md"
        if not skill_path.exists():
            pytest.skip(f"Skill {skill_name} not found")

        content = skill_path.read_text()
        # The input block should show extra_context_reference with a default or N/A
        # Check that it's not marked as required without a default
        has_default = (
            'extra_context_reference' in content
            and ('N/A' in content or 'default' in content.lower() or 'optional' in content.lower())
        )
        assert has_default, (
            f"{skill_name}/SKILL.md extra_context_reference should have a default value "
            f"or be marked optional for backward compatibility"
        )


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
