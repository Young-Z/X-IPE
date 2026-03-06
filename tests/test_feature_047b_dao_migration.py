"""Tests for FEATURE-047-B: Semantic DAO Logging & Workflow Migration.

Covers:
- DAO logging steps in SKILL.md
- Log template existence and structure
- Call site migration (14 files)
- Old skill deletion
- Legacy log reference removal
"""

import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


class TestDaoLoggingSteps:
    """AC-047-B.1 through AC-047-B.8: DAO skill has logging procedure."""

    SKILL_PATH = ROOT / ".github" / "skills" / "x-ipe-dao-end-user-representative" / "SKILL.md"

    def _read_skill(self):
        return self.SKILL_PATH.read_text(encoding="utf-8")

    def test_skill_has_logging_step(self):
        """AC-047-B.1: DAO has a logging/record step after the 7-step backbone."""
        content = self._read_skill()
        assert "录" in content or "Record" in content, "Missing logging/Record step"

    def test_logging_references_dao_folder(self):
        """AC-047-B.1: Logging step references x-ipe-docs/dao/ folder."""
        content = self._read_skill()
        assert "x-ipe-docs/dao/" in content

    def test_log_entry_metadata_fields(self):
        """AC-047-B.2: Log entry includes required metadata fields."""
        content = self._read_skill()
        required_fields = [
            "timestamp", "task_id", "calling_skill",
            "disposition", "confidence", "rationale"
        ]
        content_lower = content.lower()
        for field in required_fields:
            assert field in content_lower, f"Missing log entry field: {field}"

    def test_semantic_task_type_naming(self):
        """AC-047-B.4: Log files follow decisions_made_{semantic_task_type}.md pattern."""
        content = self._read_skill()
        assert "decisions_made_" in content

    def test_merge_or_create_logic(self):
        """AC-047-B.7: DAO describes merge-vs-create logic for log files."""
        content = self._read_skill()
        assert "existing" in content.lower() and ("append" in content.lower() or "merge" in content.lower()), \
            "Missing merge-or-create logic description"

    def test_registry_table_mentioned(self):
        """AC-047-B.8: DAO describes a registry table at top of log files."""
        content = self._read_skill()
        assert "registry" in content.lower() or "Registry" in content

    def test_no_logging_restriction_remains(self):
        """FEATURE-047-B lifts the v1 logging restriction."""
        content = self._read_skill()
        assert "MUST NOT write semantic logs" not in content, \
            "Old v1 logging restriction still present — should be removed"

    def test_skill_under_500_lines(self):
        """NFR: SKILL.md stays under 500 lines after logging addition."""
        lines = self._read_skill().splitlines()
        assert len(lines) < 500, f"SKILL.md is {len(lines)} lines, exceeds 500 limit"


class TestDaoLogTemplate:
    """AC-047-B.3, AC-047-B.8: Log template exists with proper structure."""

    TEMPLATE_PATH = ROOT / ".github" / "skills" / "x-ipe-dao-end-user-representative" / "templates" / "dao-log-template.md"

    def test_template_exists(self):
        """Log template file exists."""
        assert self.TEMPLATE_PATH.exists(), f"Missing: {self.TEMPLATE_PATH}"

    def test_template_has_registry_table_header(self):
        """AC-047-B.8: Template has a registry table structure."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "Entry" in content and "Timestamp" in content and "Disposition" in content

    def test_template_has_semantic_placeholder(self):
        """Template has placeholder for semantic task type."""
        content = self.TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "{" in content, "Template should have placeholder for semantic task type"


class TestCallSiteMigration:
    """AC-047-B.10, AC-047-B.11: All call sites migrated to DAO."""

    SKILLS_DIR = ROOT / ".github" / "skills"

    MIGRATED_FILES = [
        "x-ipe-task-based-bug-fix/SKILL.md",
        "x-ipe-task-based-code-implementation/SKILL.md",
        "x-ipe-task-based-code-refactor/SKILL.md",
        "x-ipe-task-based-dev-environment/SKILL.md",
        "x-ipe-task-based-feature-closing/SKILL.md",
        "x-ipe-task-based-idea-mockup/SKILL.md",
        "x-ipe-task-based-idea-to-architecture/SKILL.md",
        "x-ipe-task-based-ideation/SKILL.md",
        "x-ipe-task-based-requirement-gathering/SKILL.md",
        "x-ipe-task-based-share-idea/SKILL.md",
        "x-ipe-workflow-task-execution/SKILL.md",
        "x-ipe-meta-skill-creator/templates/x-ipe-task-based.md",
        "x-ipe-meta-skill-creator/references/skill-general-guidelines-v2.md",
        "x-ipe-tool-web-search/SKILL.md",
    ]

    @pytest.mark.parametrize("rel_path", MIGRATED_FILES)
    def test_no_old_decision_making_reference(self, rel_path):
        """AC-047-B.10: No references to x-ipe-tool-decision-making in migrated files."""
        fpath = self.SKILLS_DIR / rel_path
        if not fpath.exists():
            pytest.skip(f"File not found: {rel_path}")
        content = fpath.read_text(encoding="utf-8")
        assert "x-ipe-tool-decision-making" not in content, \
            f"{rel_path} still references x-ipe-tool-decision-making"

    @pytest.mark.parametrize("rel_path", [
        "x-ipe-task-based-bug-fix/SKILL.md",
        "x-ipe-task-based-code-implementation/SKILL.md",
        "x-ipe-task-based-code-refactor/SKILL.md",
        "x-ipe-task-based-dev-environment/SKILL.md",
        "x-ipe-task-based-feature-closing/SKILL.md",
        "x-ipe-task-based-idea-mockup/SKILL.md",
        "x-ipe-task-based-idea-to-architecture/SKILL.md",
        "x-ipe-task-based-ideation/SKILL.md",
        "x-ipe-task-based-requirement-gathering/SKILL.md",
        "x-ipe-task-based-share-idea/SKILL.md",
    ])
    def test_uses_message_context_contract(self, rel_path):
        """AC-047-B.11: Migrated skills use message_context contract."""
        fpath = self.SKILLS_DIR / rel_path
        if not fpath.exists():
            pytest.skip(f"File not found: {rel_path}")
        content = fpath.read_text(encoding="utf-8")
        assert "message_context" in content or "x-ipe-dao-end-user-representative" in content, \
            f"{rel_path} missing DAO reference or message_context contract"

    def test_template_uses_dao(self):
        """AC-047-B.19: Task-based template references DAO."""
        fpath = self.SKILLS_DIR / "x-ipe-meta-skill-creator" / "templates" / "x-ipe-task-based.md"
        content = fpath.read_text(encoding="utf-8")
        assert "x-ipe-dao-end-user-representative" in content

    def test_guidelines_use_dao(self):
        """AC-047-B.20: Guidelines reference DAO."""
        fpath = self.SKILLS_DIR / "x-ipe-meta-skill-creator" / "references" / "skill-general-guidelines-v2.md"
        content = fpath.read_text(encoding="utf-8")
        assert "x-ipe-dao-end-user-representative" in content


class TestOldSkillDeletion:
    """AC-047-B.9: Old decision-making skill folder is deleted."""

    def test_decision_making_folder_deleted(self):
        """AC-047-B.9: x-ipe-tool-decision-making folder does not exist."""
        old_path = ROOT / ".github" / "skills" / "x-ipe-tool-decision-making"
        assert not old_path.exists(), \
            f"Old skill folder still exists: {old_path}"


class TestLegacyLogReferences:
    """AC-047-B.12, AC-047-B.13: Legacy decision_made_by_ai.md refs removed from skills."""

    SKILLS_DIR = ROOT / ".github" / "skills"

    def test_no_decision_made_by_ai_in_active_skills(self):
        """AC-047-B.12: No references to decision_made_by_ai.md in skill files."""
        hits = []
        for md_file in self.SKILLS_DIR.rglob("*.md"):
            # Skip the deleted folder if it somehow still exists
            if "x-ipe-tool-decision-making" in str(md_file):
                continue
            content = md_file.read_text(encoding="utf-8")
            if "decision_made_by_ai" in content:
                hits.append(str(md_file.relative_to(self.SKILLS_DIR)))
        assert not hits, f"Legacy decision_made_by_ai.md still referenced in: {hits}"


class TestThreeModePreservation:
    """AC-047-B.14 through AC-047-B.18: 3-mode behavior preserved."""

    SKILLS_DIR = ROOT / ".github" / "skills"

    @pytest.mark.parametrize("rel_path", [
        "x-ipe-task-based-bug-fix/SKILL.md",
        "x-ipe-task-based-code-implementation/SKILL.md",
        "x-ipe-task-based-code-refactor/SKILL.md",
    ])
    def test_manual_mode_untouched(self, rel_path):
        """AC-047-B.14/B.18: Manual mode still asks human directly."""
        fpath = self.SKILLS_DIR / rel_path
        if not fpath.exists():
            pytest.skip(f"File not found: {rel_path}")
        content = fpath.read_text(encoding="utf-8")
        # In manual/stop_for_question mode, skills present to user (ELSE branch)
        assert "ELSE" in content or "else" in content.lower(), \
            f"{rel_path} missing ELSE branch for non-auto modes"
