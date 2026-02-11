"""
Tests for FEATURE-028-A: Bilingual Prompt Schema & Migration.

Tests the prompt_config_service module which provides:
- migrate_prompt_config(): v2.0 → v3.0 migration utility
- extract_language_section(): bilingual template extraction (FEATURE-028-B shared utility)

TDD: All tests should FAIL before implementation.
"""

import copy
import json
import pytest


# ============ FIXTURES ============

@pytest.fixture
def v2_ideation_only():
    """Minimal v2.0 config with only ideation prompts."""
    return {
        "version": "2.0",
        "ideation": {
            "prompts": [
                {
                    "id": "generate-architecture",
                    "label": "Generate Architecture",
                    "icon": "bi-diagram-3",
                    "command": "Base on <current-idea-file> to generate layered architecture"
                }
            ]
        },
        "placeholder": {
            "current-idea-file": "Replaced with currently open file path"
        }
    }


@pytest.fixture
def v2_full_config():
    """Full v2.0 config matching actual project copilot-prompt.json."""
    return {
        "version": "2.0",
        "ideation": {
            "prompts": [
                {
                    "id": "generate-architecture",
                    "label": "Generate Architecture",
                    "icon": "bi-diagram-3",
                    "command": "Base on <current-idea-file> to generate layered architecture"
                },
                {
                    "id": "idea-reflection",
                    "label": "Idea Reflection",
                    "icon": "bi-diagram-3",
                    "command": "Extra key points in <current-idea-file>, then create a sub-agent that uses these key points to learn from the project and give feedback to the idea file (the feedback should be critical but constructive), then you use the feedback to improve the idea."
                },
                {
                    "id": "generate-mockup",
                    "label": "Generate Mockup",
                    "icon": "bi-palette",
                    "command": "Base on <current-idea-file> to generate mockups"
                },
                {
                    "id": "free-question",
                    "label": "Free Collaboration",
                    "icon": "bi-chat-dots",
                    "command": "Let's base on <current-idea-file> to collaborate, wait for my instructions."
                }
            ]
        },
        "evaluation": {
            "evaluate": {
                "label": "Evaluate Project Quality",
                "icon": "bi-clipboard-check",
                "command": "Evaluate project quality and generate report"
            },
            "refactoring": [
                {
                    "id": "refactor-all",
                    "label": "Refactor All",
                    "icon": "bi-arrow-repeat",
                    "command": "Refactor all with reference to its code and <evaluation-file>"
                },
                {
                    "id": "refactor-requirements",
                    "label": "Align Requirements to Features",
                    "icon": "bi-file-text",
                    "command": "Update requirement docs to match current feature specification"
                }
            ]
        },
        "placeholder": {
            "current-idea-file": "Replaced with currently open file path",
            "evaluation-file": "x-ipe-docs/quality-evaluation/project-quality-evaluation.md"
        }
    }


@pytest.fixture
def v3_config():
    """Already-migrated v3.0 config."""
    return {
        "version": "3.0",
        "ideation": {
            "prompts": [
                {
                    "id": "generate-architecture",
                    "icon": "bi-diagram-3",
                    "prompt-details": [
                        {"language": "en", "label": "Generate Architecture", "command": "Base on <current-idea-file> to generate layered architecture"},
                        {"language": "zh", "label": "生成架构图", "command": "基于<current-idea-file>生成分层架构图"}
                    ]
                }
            ]
        },
        "placeholder": {
            "current-idea-file": "Replaced with currently open file path"
        }
    }


@pytest.fixture
def v1_legacy_config():
    """Legacy v1.0 config with flat prompts array."""
    return {
        "version": "1.0",
        "prompts": [
            {
                "id": "generate-architecture",
                "label": "Generate Architecture",
                "icon": "bi-diagram-3",
                "command": "Base on <current-idea-file> to generate layered architecture"
            }
        ],
        "placeholder": {
            "current-idea-file": "Replaced with currently open file path"
        }
    }


@pytest.fixture
def v2_with_custom_prompt():
    """v2.0 config with a user-added custom prompt."""
    return {
        "version": "2.0",
        "ideation": {
            "prompts": [
                {
                    "id": "generate-architecture",
                    "label": "Generate Architecture",
                    "icon": "bi-diagram-3",
                    "command": "Base on <current-idea-file> to generate layered architecture"
                },
                {
                    "id": "my-custom-prompt",
                    "label": "My Custom Action",
                    "icon": "bi-star",
                    "command": "Do something custom with <current-idea-file>"
                }
            ]
        },
        "placeholder": {
            "current-idea-file": "Replaced with currently open file path"
        }
    }


# ============ UNIT TESTS: migrate_prompt_config ============

class TestMigratePromptConfigVersion:
    """Tests for version handling in migration."""

    def test_sets_version_to_3_0(self, v2_ideation_only):
        """Migration MUST update version to 3.0."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_ideation_only)
        assert result["version"] == "3.0"

    def test_idempotent_on_v3(self, v3_config):
        """Migration on v3.0 config MUST return unchanged (AC-028-A.18)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        original = copy.deepcopy(v3_config)
        result = migrate_prompt_config(v3_config)
        assert result == original

    def test_handles_v1_legacy(self, v1_legacy_config):
        """Migration MUST handle v1.0 legacy format (EC-4)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v1_legacy_config)
        assert result["version"] == "3.0"
        assert "ideation" in result
        assert "prompts" not in result  # flat prompts moved to ideation


class TestMigratePromptConfigIdeation:
    """Tests for ideation prompts migration."""

    def test_creates_prompt_details_array(self, v2_ideation_only):
        """Each ideation prompt MUST have prompt-details array (AC-028-A.2)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_ideation_only)
        prompt = result["ideation"]["prompts"][0]
        assert "prompt-details" in prompt
        assert isinstance(prompt["prompt-details"], list)

    def test_en_entry_in_prompt_details(self, v2_ideation_only):
        """Migration MUST wrap label/command into EN prompt-details entry (AC-028-A.14)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_ideation_only)
        prompt = result["ideation"]["prompts"][0]
        en = next(d for d in prompt["prompt-details"] if d["language"] == "en")
        assert en["label"] == "Generate Architecture"
        assert "<current-idea-file>" in en["command"]

    def test_zh_entry_for_known_prompt(self, v2_ideation_only):
        """Known prompts MUST get ZH translation (AC-028-A.6, AC-028-A.9)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_ideation_only)
        prompt = result["ideation"]["prompts"][0]
        zh_entries = [d for d in prompt["prompt-details"] if d["language"] == "zh"]
        assert len(zh_entries) == 1
        assert zh_entries[0]["label"]  # non-empty
        assert zh_entries[0]["command"]  # non-empty

    def test_removes_top_level_label(self, v2_ideation_only):
        """label MUST NOT exist at prompt level after migration (AC-028-A.5, AC-028-A.16)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_ideation_only)
        prompt = result["ideation"]["prompts"][0]
        assert "label" not in prompt

    def test_removes_top_level_command(self, v2_ideation_only):
        """command MUST NOT exist at prompt level after migration (AC-028-A.16)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_ideation_only)
        prompt = result["ideation"]["prompts"][0]
        assert "command" not in prompt

    def test_preserves_id_at_prompt_level(self, v2_ideation_only):
        """id MUST remain at prompt level (AC-028-A.7)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_ideation_only)
        prompt = result["ideation"]["prompts"][0]
        assert prompt["id"] == "generate-architecture"

    def test_preserves_icon_at_prompt_level(self, v2_ideation_only):
        """icon MUST remain at prompt level (AC-028-A.7)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_ideation_only)
        prompt = result["ideation"]["prompts"][0]
        assert prompt["icon"] == "bi-diagram-3"


class TestMigratePromptConfigEvaluation:
    """Tests for evaluation section migration."""

    def test_evaluate_singleton_gets_prompt_details(self, v2_full_config):
        """evaluate singleton MUST have prompt-details (AC-028-A.4)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_full_config)
        evaluate = result["evaluation"]["evaluate"]
        assert "prompt-details" in evaluate
        assert isinstance(evaluate["prompt-details"], list)

    def test_evaluate_singleton_gets_id(self, v2_full_config):
        """evaluate singleton MUST get id if missing (EC-6)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_full_config)
        evaluate = result["evaluation"]["evaluate"]
        assert evaluate.get("id") == "evaluate"

    def test_evaluate_singleton_zh_translation(self, v2_full_config):
        """evaluate MUST have ZH translation (AC-028-A.11)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_full_config)
        evaluate = result["evaluation"]["evaluate"]
        zh = [d for d in evaluate["prompt-details"] if d["language"] == "zh"]
        assert len(zh) == 1

    def test_refactoring_prompts_get_prompt_details(self, v2_full_config):
        """refactoring prompts MUST have prompt-details (AC-028-A.3)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_full_config)
        for prompt in result["evaluation"]["refactoring"]:
            assert "prompt-details" in prompt

    def test_refactoring_prompts_zh_translation(self, v2_full_config):
        """refactoring prompts MUST have ZH translations (AC-028-A.10)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_full_config)
        for prompt in result["evaluation"]["refactoring"]:
            zh = [d for d in prompt["prompt-details"] if d["language"] == "zh"]
            assert len(zh) == 1, f"Missing ZH for {prompt.get('id')}"


class TestMigratePromptConfigPlaceholders:
    """Tests for placeholder preservation."""

    def test_placeholder_section_unchanged(self, v2_full_config):
        """placeholder section MUST remain unchanged (AC-028-A.8, AC-028-A.20)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        original_placeholder = copy.deepcopy(v2_full_config["placeholder"])
        result = migrate_prompt_config(v2_full_config)
        assert result["placeholder"] == original_placeholder

    def test_zh_commands_preserve_placeholder_tokens(self, v2_full_config):
        """ZH commands MUST preserve <placeholder> tokens (AC-028-A.12)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_full_config)
        # Check ideation prompts
        for prompt in result["ideation"]["prompts"]:
            en = next(d for d in prompt["prompt-details"] if d["language"] == "en")
            zh = next((d for d in prompt["prompt-details"] if d["language"] == "zh"), None)
            if zh and "<current-idea-file>" in en["command"]:
                assert "<current-idea-file>" in zh["command"], \
                    f"ZH command for {prompt['id']} missing <current-idea-file> placeholder"


class TestMigratePromptConfigEdgeCases:
    """Tests for edge cases and error handling."""

    def test_custom_prompt_wrapped_en_only(self, v2_with_custom_prompt):
        """Custom prompts MUST be wrapped as EN-only (AC-028-A.19, EC-1)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_with_custom_prompt)
        custom = next(p for p in result["ideation"]["prompts"] if p["id"] == "my-custom-prompt")
        assert len(custom["prompt-details"]) == 1
        assert custom["prompt-details"][0]["language"] == "en"

    def test_empty_prompts_array(self):
        """Empty prompts array MUST produce empty array with version bump (EC-7)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        data = {"version": "2.0", "ideation": {"prompts": []}, "placeholder": {}}
        result = migrate_prompt_config(data)
        assert result["version"] == "3.0"
        assert result["ideation"]["prompts"] == []

    def test_preserves_user_deletions(self):
        """Migration MUST preserve user deletions (EC-2)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        data = {
            "version": "2.0",
            "ideation": {
                "prompts": [
                    {"id": "generate-mockup", "label": "Generate Mockup", "icon": "bi-palette",
                     "command": "Base on <current-idea-file> to generate mockups"}
                ]
            },
            "placeholder": {}
        }
        result = migrate_prompt_config(data)
        assert len(result["ideation"]["prompts"]) == 1
        assert result["ideation"]["prompts"][0]["id"] == "generate-mockup"

    def test_does_not_mutate_input(self, v2_full_config):
        """Migration MUST NOT mutate the input dict."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        original = copy.deepcopy(v2_full_config)
        migrate_prompt_config(v2_full_config)
        assert v2_full_config == original

    def test_malformed_input_raises_error(self):
        """Malformed JSON (non-dict) MUST raise ValueError (EC-5)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        with pytest.raises((ValueError, TypeError)):
            migrate_prompt_config("not a dict")

    def test_full_migration_all_prompts(self, v2_full_config):
        """Full v2.0 config MUST migrate all prompts with both EN and ZH (AC-028-A.6)."""
        from x_ipe.services.prompt_config_service import migrate_prompt_config
        result = migrate_prompt_config(v2_full_config)
        # Check all ideation prompts
        for prompt in result["ideation"]["prompts"]:
            assert "prompt-details" in prompt
            langs = {d["language"] for d in prompt["prompt-details"]}
            assert "en" in langs, f"Missing EN for {prompt['id']}"
            assert "zh" in langs, f"Missing ZH for {prompt['id']}"

        # Check evaluate singleton
        evaluate = result["evaluation"]["evaluate"]
        assert "prompt-details" in evaluate
        langs = {d["language"] for d in evaluate["prompt-details"]}
        assert "en" in langs and "zh" in langs

        # Check refactoring prompts
        for prompt in result["evaluation"]["refactoring"]:
            assert "prompt-details" in prompt
            langs = {d["language"] for d in prompt["prompt-details"]}
            assert "en" in langs and "zh" in langs


# ============ UNIT TESTS: extract_language_section ============

class TestExtractLanguageSection:
    """Tests for extract_language_section (FEATURE-028-B shared utility)."""

    def test_extracts_en_section(self):
        """MUST extract EN content between markers (AC-028-B.12)."""
        from x_ipe.services.prompt_config_service import extract_language_section
        template = "---LANG:en---\nEN content here\n---LANG:zh---\nZH content here"
        result = extract_language_section(template, "en")
        assert result == "EN content here"

    def test_extracts_zh_section(self):
        """MUST extract ZH content between markers (AC-028-B.12)."""
        from x_ipe.services.prompt_config_service import extract_language_section
        template = "---LANG:en---\nEN content here\n---LANG:zh---\nZH content here"
        result = extract_language_section(template, "zh")
        assert result == "ZH content here"

    def test_marker_line_not_included(self):
        """Extracted content MUST NOT include the marker line (AC-028-B.13)."""
        from x_ipe.services.prompt_config_service import extract_language_section
        template = "---LANG:en---\nLine 1\nLine 2\n---LANG:zh---\nZH"
        result = extract_language_section(template, "en")
        assert "---LANG:" not in result

    def test_multiline_content(self):
        """MUST handle multiline content between markers."""
        from x_ipe.services.prompt_config_service import extract_language_section
        template = "---LANG:en---\nLine 1\nLine 2\nLine 3\n---LANG:zh---\nZH"
        result = extract_language_section(template, "en")
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result

    def test_no_markers_returns_full_template(self):
        """If no markers found, return full template (backward compat, EC-2)."""
        from x_ipe.services.prompt_config_service import extract_language_section
        template = "# Instructions\nSome content here"
        result = extract_language_section(template, "en")
        assert result == template.strip()

    def test_zh_at_end_of_file(self):
        """ZH section at EOF (no trailing marker) MUST be fully extracted."""
        from x_ipe.services.prompt_config_service import extract_language_section
        template = "---LANG:en---\nEN content\n---LANG:zh---\nZH line 1\nZH line 2"
        result = extract_language_section(template, "zh")
        assert "ZH line 1" in result
        assert "ZH line 2" in result

    def test_missing_language_returns_full_template(self):
        """If requested language marker doesn't exist, return full template (EC-6)."""
        from x_ipe.services.prompt_config_service import extract_language_section
        template = "---LANG:en---\nEN content only"
        result = extract_language_section(template, "fr")
        assert "EN content" in result
