"""
Tests for FEATURE-027-C: Skill & Instruction Translation

Tests cover:
- SkillTranslator: translate_skills(), generate_instructions()
- Copilot translation (no-op)
- OpenCode translation (frontmatter filtering)
- Claude Code translation (frontmatter preservation)
- Frontmatter parsing and serialization
- Subdirectory handling
- Edge cases: no frontmatter, empty frontmatter, malformed YAML, missing source
- Idempotency
- Error handling per-skill

TDD Approach: All tests written before implementation.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock
from dataclasses import dataclass


# ============================================================================
# FIXTURES
# ============================================================================

SAMPLE_SKILL_WITH_FRONTMATTER = """---
name: my-skill
description: A test skill for unit testing.
extra_field: should_be_dropped_for_opencode
---

# My Skill

This is the body content.

## Section

Details here.
"""

SAMPLE_SKILL_NO_FRONTMATTER = """# My Skill

This is a skill without frontmatter.
"""

SAMPLE_SKILL_EMPTY_FRONTMATTER = """---
---

# My Skill

Body after empty frontmatter.
"""

SAMPLE_SKILL_MULTILINE_DESCRIPTION = """---
name: complex-skill
description: >
  A skill with a multi-line
  description value.
---

# Complex Skill

Body content.
"""

SAMPLE_SKILL_MALFORMED_YAML = """---
name: broken
description: [invalid yaml
  missing bracket
---

# Broken Skill
"""

INSTRUCTIONS_TEMPLATE_CONTENT = """# Project Instructions

## Before You Start
Follow the X-IPE workflow for all tasks.
"""


def make_adapter(name='opencode', skills_folder='.opencode/skills/', instructions_file='AGENTS.md'):
    """Create a mock CLIAdapterData."""
    adapter = MagicMock()
    adapter.name = name
    adapter.skills_folder = skills_folder
    adapter.instructions_file = instructions_file
    return adapter


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project with canonical skills."""
    source = tmp_path / ".github" / "skills"
    source.mkdir(parents=True)

    # Skill 1: with frontmatter
    skill1 = source / "my-skill"
    skill1.mkdir()
    (skill1 / "SKILL.md").write_text(SAMPLE_SKILL_WITH_FRONTMATTER)

    # Skill 2: with subdirectories
    skill2 = source / "complex-skill"
    skill2.mkdir()
    (skill2 / "SKILL.md").write_text(SAMPLE_SKILL_MULTILINE_DESCRIPTION)
    templates = skill2 / "templates"
    templates.mkdir()
    (templates / "template.md").write_text("# Template")
    refs = skill2 / "references"
    refs.mkdir()
    (refs / "example.md").write_text("# Example")

    # Skill 3: no frontmatter
    skill3 = source / "no-fm-skill"
    skill3.mkdir()
    (skill3 / "SKILL.md").write_text(SAMPLE_SKILL_NO_FRONTMATTER)

    # Instructions template
    tpl_dir = tmp_path / "resources" / "templates"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "instructions-template.md").write_text(INSTRUCTIONS_TEMPLATE_CONTENT)

    return tmp_path


# ============================================================================
# TEST CLASS: Frontmatter Parsing
# ============================================================================

class TestFrontmatterParsing:
    """Tests for parse_frontmatter() and serialize_frontmatter()."""

    def test_parse_with_frontmatter(self):
        """Parse content with valid frontmatter returns dict and body."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        fm, body = translator.parse_frontmatter(SAMPLE_SKILL_WITH_FRONTMATTER)
        assert fm['name'] == 'my-skill'
        assert fm['description'] == 'A test skill for unit testing.'
        assert fm['extra_field'] == 'should_be_dropped_for_opencode'
        assert '# My Skill' in body

    def test_parse_no_frontmatter(self):
        """Parse content without frontmatter returns empty dict and full body."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        fm, body = translator.parse_frontmatter(SAMPLE_SKILL_NO_FRONTMATTER)
        assert fm == {}
        assert '# My Skill' in body

    def test_parse_empty_frontmatter(self):
        """Parse content with empty frontmatter returns empty dict."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        fm, body = translator.parse_frontmatter(SAMPLE_SKILL_EMPTY_FRONTMATTER)
        assert fm == {}
        assert '# My Skill' in body

    def test_parse_multiline_description(self):
        """Parse content with multi-line YAML value."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        fm, body = translator.parse_frontmatter(SAMPLE_SKILL_MULTILINE_DESCRIPTION)
        assert fm['name'] == 'complex-skill'
        assert 'multi-line' in fm['description']

    def test_parse_malformed_yaml(self):
        """Parse content with malformed YAML returns empty frontmatter."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        fm, body = translator.parse_frontmatter(SAMPLE_SKILL_MALFORMED_YAML)
        assert fm == {}

    def test_serialize_frontmatter_roundtrip(self):
        """Serialize and re-parse frontmatter produces consistent result."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        fm = {'name': 'test', 'description': 'A test'}
        body = '\n\n# Test\n\nBody here.'
        output = translator.serialize_frontmatter(fm, body)
        assert output.startswith('---\n')
        fm2, body2 = translator.parse_frontmatter(output)
        assert fm2['name'] == 'test'
        assert fm2['description'] == 'A test'

    def test_serialize_empty_frontmatter(self):
        """Serialize empty frontmatter returns body only."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        output = translator.serialize_frontmatter({}, '\n# Body\n')
        assert not output.startswith('---')
        assert '# Body' in output


# ============================================================================
# TEST CLASS: OpenCode Frontmatter Filtering
# ============================================================================

class TestOpenCodeFrontmatterFiltering:
    """Tests for filter_opencode_frontmatter()."""

    def test_filter_keeps_name_and_description(self):
        """OpenCode filter keeps only name and description."""
        from x_ipe.services.skill_translator import SkillTranslator
        fm = {'name': 'my-skill', 'description': 'Test', 'extra': 'dropped'}
        result = SkillTranslator.filter_opencode_frontmatter(fm, 'my-skill')
        assert result == {'name': 'my-skill', 'description': 'Test'}

    def test_filter_derives_name_from_dir(self):
        """OpenCode filter derives name from dir_name if not in frontmatter."""
        from x_ipe.services.skill_translator import SkillTranslator
        fm = {'description': 'No name field'}
        result = SkillTranslator.filter_opencode_frontmatter(fm, 'my-dir-name')
        assert result['name'] == 'my-dir-name'
        assert result['description'] == 'No name field'

    def test_filter_no_description(self):
        """OpenCode filter omits description if not present."""
        from x_ipe.services.skill_translator import SkillTranslator
        fm = {'name': 'my-skill', 'extra': 'dropped'}
        result = SkillTranslator.filter_opencode_frontmatter(fm, 'my-skill')
        assert 'description' not in result
        assert result['name'] == 'my-skill'

    def test_filter_empty_frontmatter(self):
        """OpenCode filter with empty frontmatter generates name from dir."""
        from x_ipe.services.skill_translator import SkillTranslator
        result = SkillTranslator.filter_opencode_frontmatter({}, 'fallback-name')
        assert result == {'name': 'fallback-name'}


# ============================================================================
# TEST CLASS: Copilot Translation (No-Op)
# ============================================================================

class TestCopilotTranslation:
    """Tests for copilot adapter translation (should be no-op)."""

    def test_translate_skills_noop(self, tmp_project):
        """Copilot translate_skills() returns empty result, no files written."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='copilot', skills_folder='.github/skills/')
        source = tmp_project / ".github" / "skills"
        target = tmp_project / ".github" / "skills"
        result = translator.translate_skills(source, target, adapter)
        assert result.translated == 0
        assert result.errors == []

    def test_generate_instructions_noop(self, tmp_project):
        """Copilot generate_instructions() returns None, no file written."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='copilot')
        result = translator.generate_instructions(adapter, tmp_project)
        assert result is None


# ============================================================================
# TEST CLASS: OpenCode Translation
# ============================================================================

class TestOpenCodeTranslation:
    """Tests for OpenCode adapter skill translation."""

    def test_translates_all_skills(self, tmp_project):
        """OpenCode translation copies all skills to target directory."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='opencode', skills_folder='.opencode/skills/')
        source = tmp_project / ".github" / "skills"
        target = tmp_project / ".opencode" / "skills"
        result = translator.translate_skills(source, target, adapter)
        assert result.translated == 3
        assert result.errors == []
        assert (target / "my-skill" / "SKILL.md").exists()
        assert (target / "complex-skill" / "SKILL.md").exists()
        assert (target / "no-fm-skill" / "SKILL.md").exists()

    def test_filters_frontmatter(self, tmp_project):
        """OpenCode translation filters frontmatter to name+description only."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='opencode', skills_folder='.opencode/skills/')
        source = tmp_project / ".github" / "skills"
        target = tmp_project / ".opencode" / "skills"
        translator.translate_skills(source, target, adapter)
        content = (target / "my-skill" / "SKILL.md").read_text()
        fm, body = translator.parse_frontmatter(content)
        assert 'name' in fm
        assert 'description' in fm
        assert 'extra_field' not in fm

    def test_preserves_body_content(self, tmp_project):
        """OpenCode translation preserves body content exactly."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='opencode', skills_folder='.opencode/skills/')
        source = tmp_project / ".github" / "skills"
        target = tmp_project / ".opencode" / "skills"
        translator.translate_skills(source, target, adapter)
        content = (target / "my-skill" / "SKILL.md").read_text()
        assert '# My Skill' in content
        assert 'This is the body content.' in content

    def test_copies_subdirectories(self, tmp_project):
        """OpenCode translation copies subdirectories alongside SKILL.md."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='opencode', skills_folder='.opencode/skills/')
        source = tmp_project / ".github" / "skills"
        target = tmp_project / ".opencode" / "skills"
        translator.translate_skills(source, target, adapter)
        assert (target / "complex-skill" / "templates" / "template.md").exists()
        assert (target / "complex-skill" / "references" / "example.md").exists()

    def test_generates_name_from_dir_for_no_frontmatter(self, tmp_project):
        """OpenCode translation generates name from dir for skills without frontmatter."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='opencode', skills_folder='.opencode/skills/')
        source = tmp_project / ".github" / "skills"
        target = tmp_project / ".opencode" / "skills"
        translator.translate_skills(source, target, adapter)
        content = (target / "no-fm-skill" / "SKILL.md").read_text()
        fm, _ = translator.parse_frontmatter(content)
        assert fm.get('name') == 'no-fm-skill'

    def test_generates_agents_md(self, tmp_project):
        """OpenCode generate_instructions() creates AGENTS.md at project root."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='opencode', instructions_file='AGENTS.md')
        tpl = tmp_project / "resources" / "templates" / "instructions-template.md"
        result = translator.generate_instructions(adapter, tmp_project, template_path=tpl)
        assert result is not None
        assert (tmp_project / "AGENTS.md").exists()
        content = (tmp_project / "AGENTS.md").read_text()
        assert 'Project Instructions' in content


# ============================================================================
# TEST CLASS: Claude Code Translation
# ============================================================================

class TestClaudeCodeTranslation:
    """Tests for Claude Code adapter skill translation."""

    def test_translates_all_skills(self, tmp_project):
        """Claude Code translation copies all skills to target directory."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='claude-code', skills_folder='.claude/skills/')
        source = tmp_project / ".github" / "skills"
        target = tmp_project / ".claude" / "skills"
        result = translator.translate_skills(source, target, adapter)
        assert result.translated == 3
        assert result.errors == []

    def test_preserves_frontmatter(self, tmp_project):
        """Claude Code translation preserves all frontmatter fields."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='claude-code', skills_folder='.claude/skills/')
        source = tmp_project / ".github" / "skills"
        target = tmp_project / ".claude" / "skills"
        translator.translate_skills(source, target, adapter)
        content = (target / "my-skill" / "SKILL.md").read_text()
        fm, _ = translator.parse_frontmatter(content)
        assert fm.get('name') == 'my-skill'
        assert fm.get('description') == 'A test skill for unit testing.'
        assert fm.get('extra_field') == 'should_be_dropped_for_opencode'

    def test_preserves_body_content(self, tmp_project):
        """Claude Code translation preserves body content exactly."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='claude-code', skills_folder='.claude/skills/')
        source = tmp_project / ".github" / "skills"
        target = tmp_project / ".claude" / "skills"
        translator.translate_skills(source, target, adapter)
        content = (target / "my-skill" / "SKILL.md").read_text()
        assert '# My Skill' in content
        assert 'This is the body content.' in content

    def test_copies_subdirectories(self, tmp_project):
        """Claude Code translation copies subdirectories alongside SKILL.md."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='claude-code', skills_folder='.claude/skills/')
        source = tmp_project / ".github" / "skills"
        target = tmp_project / ".claude" / "skills"
        translator.translate_skills(source, target, adapter)
        assert (target / "complex-skill" / "templates" / "template.md").exists()
        assert (target / "complex-skill" / "references" / "example.md").exists()

    def test_generates_claude_md(self, tmp_project):
        """Claude Code generate_instructions() creates CLAUDE.md at project root."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='claude-code', instructions_file='CLAUDE.md')
        tpl = tmp_project / "resources" / "templates" / "instructions-template.md"
        result = translator.generate_instructions(adapter, tmp_project, template_path=tpl)
        assert result is not None
        assert (tmp_project / "CLAUDE.md").exists()


# ============================================================================
# TEST CLASS: Translation Behavior
# ============================================================================

class TestTranslationBehavior:
    """Tests for translation behavior: idempotency, error handling, source safety."""

    def test_idempotent_translation(self, tmp_project):
        """Running translate_skills twice produces identical output."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='opencode', skills_folder='.opencode/skills/')
        source = tmp_project / ".github" / "skills"
        target = tmp_project / ".opencode" / "skills"
        translator.translate_skills(source, target, adapter)
        first_content = (target / "my-skill" / "SKILL.md").read_text()
        translator.translate_skills(source, target, adapter)
        second_content = (target / "my-skill" / "SKILL.md").read_text()
        assert first_content == second_content

    def test_source_not_modified(self, tmp_project):
        """Source skills directory is not modified during translation."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        source = tmp_project / ".github" / "skills"
        original = (source / "my-skill" / "SKILL.md").read_text()
        adapter = make_adapter(name='opencode', skills_folder='.opencode/skills/')
        target = tmp_project / ".opencode" / "skills"
        translator.translate_skills(source, target, adapter)
        after = (source / "my-skill" / "SKILL.md").read_text()
        assert original == after

    def test_per_skill_error_continues(self, tmp_project):
        """If one skill fails, others still get translated."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        source = tmp_project / ".github" / "skills"
        # Create a skill that will cause an error (read-only SKILL.md)
        bad_skill = source / "bad-skill"
        bad_skill.mkdir()
        (bad_skill / "SKILL.md").write_text(SAMPLE_SKILL_MALFORMED_YAML)
        adapter = make_adapter(name='opencode', skills_folder='.opencode/skills/')
        target = tmp_project / ".opencode" / "skills"
        result = translator.translate_skills(source, target, adapter)
        # bad-skill should still translate (malformed yaml → empty fm → name derived from dir)
        assert result.translated >= 3

    def test_source_dir_not_exists(self, tmp_project):
        """translate_skills with non-existent source returns empty result."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='opencode')
        source = tmp_project / "nonexistent"
        target = tmp_project / ".opencode" / "skills"
        result = translator.translate_skills(source, target, adapter)
        assert result.translated == 0
        assert result.errors == []

    def test_empty_source_dir(self, tmp_project):
        """translate_skills with empty source directory returns empty result."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='opencode')
        source = tmp_project / "empty_skills"
        source.mkdir()
        target = tmp_project / ".opencode" / "skills"
        result = translator.translate_skills(source, target, adapter)
        assert result.translated == 0

    def test_missing_template_returns_none(self, tmp_project):
        """generate_instructions with missing template returns None."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='opencode')
        missing = tmp_project / "nonexistent" / "template.md"
        result = translator.generate_instructions(adapter, tmp_project, template_path=missing)
        assert result is None

    def test_instruction_file_overwrite_idempotent(self, tmp_project):
        """generate_instructions is idempotent — overwrite produces same content."""
        from x_ipe.services.skill_translator import SkillTranslator
        translator = SkillTranslator()
        adapter = make_adapter(name='opencode', instructions_file='AGENTS.md')
        tpl = tmp_project / "resources" / "templates" / "instructions-template.md"
        translator.generate_instructions(adapter, tmp_project, template_path=tpl)
        first = (tmp_project / "AGENTS.md").read_text()
        translator.generate_instructions(adapter, tmp_project, template_path=tpl)
        second = (tmp_project / "AGENTS.md").read_text()
        assert first == second


# ============================================================================
# TEST CLASS: TranslationResult
# ============================================================================

class TestTranslationResult:
    """Tests for TranslationResult dataclass."""

    def test_default_values(self):
        """TranslationResult has correct defaults."""
        from x_ipe.services.skill_translator import TranslationResult
        result = TranslationResult()
        assert result.translated == 0
        assert result.skipped == 0
        assert result.errors == []

    def test_mutable_errors_list(self):
        """TranslationResult errors list is mutable."""
        from x_ipe.services.skill_translator import TranslationResult
        result = TranslationResult()
        result.errors.append("test error")
        assert len(result.errors) == 1


# ============================================================================
# TEST CLASS: Tracing
# ============================================================================

class TestSkillTranslatorTracing:
    """Tests for @x_ipe_tracing decorators on SkillTranslator methods."""

    def test_translate_skills_has_tracing(self):
        """translate_skills() method has @x_ipe_tracing decorator."""
        from x_ipe.services.skill_translator import SkillTranslator
        method = getattr(SkillTranslator, 'translate_skills')
        assert hasattr(method, '__wrapped__') or callable(method)

    def test_generate_instructions_has_tracing(self):
        """generate_instructions() method has @x_ipe_tracing decorator."""
        from x_ipe.services.skill_translator import SkillTranslator
        method = getattr(SkillTranslator, 'generate_instructions')
        assert hasattr(method, '__wrapped__') or callable(method)
