"""
Tests for FEATURE-047-A: DAO Skill Foundation & End-User Core.

These tests validate:
- x-ipe-meta-skill-creator supports the new x-ipe-dao skill type
- DAO-specific templates exist for skill creation
- x-ipe-dao-end-user-representative exists as the first concrete human representative skill
- Skill structure, message_context contract, and bounded output are documented
"""

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / ".github" / "skills"
META_CREATOR_DIR = SKILLS_DIR / "x-ipe-meta-skill-creator"
DAO_SKILL_DIR = SKILLS_DIR / "x-ipe-dao-end-user-representative"


@pytest.fixture
def meta_creator_content():
    return (META_CREATOR_DIR / "SKILL.md").read_text()


@pytest.fixture
def dao_skill_content():
    return (DAO_SKILL_DIR / "SKILL.md").read_text()


class TestMetaSkillCreatorDaoSupport:
    def test_creator_declares_dao_skill_type(self, meta_creator_content):
        assert "x-ipe-dao" in meta_creator_content

    def test_creator_routes_dao_to_dedicated_templates(self, meta_creator_content):
        assert "templates/x-ipe-dao.md" in meta_creator_content
        assert "templates/skill-meta-x-ipe-dao.md" in meta_creator_content

    def test_dao_skill_template_exists(self):
        assert (META_CREATOR_DIR / "templates" / "x-ipe-dao.md").exists()

    def test_dao_skill_meta_template_exists(self):
        assert (META_CREATOR_DIR / "templates" / "skill-meta-x-ipe-dao.md").exists()


class TestDaoEndUserSkillStructure:
    def test_dao_skill_folder_exists(self):
        assert DAO_SKILL_DIR.exists()
        assert DAO_SKILL_DIR.is_dir()

    def test_dao_skill_md_exists(self):
        assert (DAO_SKILL_DIR / "SKILL.md").exists()

    def test_dao_references_examples_exist(self):
        assert (DAO_SKILL_DIR / "references" / "examples.md").exists()

    def test_dao_references_guidelines_exist(self):
        assert (DAO_SKILL_DIR / "references" / "dao-disposition-guidelines.md").exists()


class TestDaoEndUserSkillContent:
    def test_frontmatter_declares_name(self, dao_skill_content):
        assert "name: x-ipe-dao-end-user-representative" in dao_skill_content

    def test_documents_message_context_contract(self, dao_skill_content):
        assert "message_context:" in dao_skill_content
        assert 'source: "human | ai"' in dao_skill_content
        assert '<procedure name="end-user-representative">' in dao_skill_content

    def test_documents_supported_dispositions(self, dao_skill_content):
        for disposition in [
            "answer",
            "clarification",
            "reframe",
            "critique",
            "instruction",
            "approval",
            "pass_through",
        ]:
            assert disposition in dao_skill_content

    def test_documents_bounded_output(self, dao_skill_content):
        assert "bounded" in dao_skill_content.lower()
        assert "must not expose full inner reasoning" in dao_skill_content.lower()

    def test_documents_human_shadow_fallback(self, dao_skill_content):
        assert "human_shadow" in dao_skill_content
        assert "fallback_required" in dao_skill_content

    def test_documents_gewu_zhizhi_backbone(self, dao_skill_content):
        """The skill documents the 格物致知 backbone phases."""
        for phase in ["格物", "致知", "礼", "录", "示"]:
            assert phase in dao_skill_content

    def test_line_count_under_600(self):
        line_count = len((DAO_SKILL_DIR / "SKILL.md").read_text().splitlines())
        assert line_count < 600

    def test_documents_error_codes(self, dao_skill_content):
        for code in ["DAO_INPUT_INVALID", "DAO_DISPOSITION_UNCLEAR", "DAO_HUMAN_SHADOW_REQUIRED"]:
            assert code in dao_skill_content

    def test_external_description_avoids_dao_as_primary_term(self, dao_skill_content):
        """AC-047-A.21: frontmatter description uses universally understood language."""
        lines = dao_skill_content.splitlines()
        for line in lines:
            if line.startswith("description:"):
                assert "human representative" in line.lower() or "human" in line.lower()
                break

    def test_dao_positioned_as_internal_backbone(self, dao_skill_content):
        """AC-047-A.22: 道 (DAO) is the internal CORE backbone, not primary external term."""
        assert "CORE Backbone" in dao_skill_content or "CORE backbone" in dao_skill_content


class TestDaoTemplateContent:
    @pytest.fixture
    def dao_template_content(self):
        return (META_CREATOR_DIR / "templates" / "x-ipe-dao.md").read_text()

    def test_template_has_gewu_zhizhi_backbone(self, dao_template_content):
        """The template documents the 格物致知 backbone phases."""
        for phase in ["格物", "致知", "礼", "录", "示"]:
            assert phase in dao_template_content

    def test_template_has_bounded_output_language(self, dao_template_content):
        assert "bounded" in dao_template_content.lower()

    def test_template_has_operation_output_contract(self, dao_template_content):
        assert "operation_output:" in dao_template_content
        assert "disposition:" in dao_template_content
        assert "fallback_required:" in dao_template_content
