"""Tests for FEATURE-047-C: Instruction Resource DAO Interception.

Covers:
- DAO interception guidance in repo-local instructions (with-DAO variant)
- Packaged instruction sync (en/zh) — both DAO and no-DAO variants
- Bounded DAO description
- No internal backbone exposure
- No-DAO variants omit DAO interception mandate
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


class TestRepoLocalInstructions:
    """Repo-local instructions match no-DAO variant (dao_intercept defaults to false)."""

    INSTRUCTIONS_PATH = ROOT / ".github" / "copilot-instructions.md"

    def _read(self):
        return self.INSTRUCTIONS_PATH.read_text(encoding="utf-8")

    def test_mentions_dao_skill(self):
        """Instructions still reference x-ipe-dao-end-user-representative for within-skill use."""
        assert "x-ipe-dao-end-user-representative" in self._read()

    def test_no_dao_first_mandate(self):
        """Default (dao_intercept=false): no DAO-first interception mandate."""
        content = self._read()
        assert "EVERY user message MUST be processed through" not in content
        assert "DAO-First" not in content

    def test_keeps_skill_first_gate(self):
        """Still enforces skill-first workflow."""
        content = self._read()
        assert "Skill-First" in content
        assert "task-board.md" in content

    def test_no_internal_backbone_exposed(self):
        """No 道 or 7-step backbone in instructions."""
        content = self._read()
        assert "静虑" not in content
        assert "兼听" not in content
        assert "审势" not in content

    def test_uses_process_preference(self):
        """Instructions use process_preference.interaction_mode for within-skill DAO."""
        content = self._read()
        assert "process_preference.interaction_mode" in content

    def test_synced_with_no_dao_en_variant(self):
        """Repo-local matches the packaged no-DAO EN variant."""
        repo_local = self._read()
        no_dao_en = (ROOT / "src" / "x_ipe" / "resources" / "copilot-instructions-en-no-dao.md").read_text(encoding="utf-8")
        assert repo_local == no_dao_en


class TestPackagedEnglishInstructions:
    """AC-047-C.5, AC-047-C.7: Packaged English instructions synced."""

    EN_PATH = ROOT / "src" / "x_ipe" / "resources" / "copilot-instructions-en.md"

    def _read(self):
        return self.EN_PATH.read_text(encoding="utf-8")

    def test_mentions_dao_skill(self):
        """AC-047-C.5: Packaged EN instructions reference DAO."""
        assert "x-ipe-dao-end-user-representative" in self._read()

    def test_uses_process_preference(self):
        """AC-047-C.7: Uses process_preference.interaction_mode, not require_human_review."""
        content = self._read()
        assert "process_preference.interaction_mode" in content

    def test_synced_with_repo_local(self):
        """Packaged EN (DAO variant) has DAO content that repo-local (no-DAO) does not."""
        repo_local = (ROOT / ".github" / "copilot-instructions.md").read_text(encoding="utf-8")
        packaged = self._read()
        # Both reference DAO skill (within-skill use)
        assert "x-ipe-dao-end-user-representative" in repo_local
        assert "x-ipe-dao-end-user-representative" in packaged
        # But only the DAO variant has the interception mandate
        assert "DAO-First" in packaged
        assert "DAO-First" not in repo_local


class TestPackagedChineseInstructions:
    """AC-047-C.6: Packaged Chinese instructions have DAO guidance."""

    ZH_PATH = ROOT / "src" / "x_ipe" / "resources" / "copilot-instructions-zh.md"

    def _read(self):
        return self.ZH_PATH.read_text(encoding="utf-8")

    def test_mentions_dao_skill(self):
        """AC-047-C.6: Packaged ZH instructions reference DAO."""
        assert "x-ipe-dao-end-user-representative" in self._read()

    def test_has_auto_mode_guidance(self):
        """AC-047-C.6: ZH instructions have auto mode DAO guidance."""
        content = self._read()
        assert "auto" in content.lower()


class TestNoDaoEnglishInstructions:
    """No-DAO EN variant: DAO interception removed, within-skill DAO kept."""

    PATH = ROOT / "src" / "x_ipe" / "resources" / "copilot-instructions-en-no-dao.md"

    def _read(self):
        return self.PATH.read_text(encoding="utf-8")

    def test_no_dao_first_mandate(self):
        """No-DAO variant must NOT contain DAO-first interception mandate."""
        content = self._read()
        assert "EVERY user message MUST be processed through" not in content
        assert "DAO-First" not in content

    def test_no_instruction_units_loop(self):
        """No-DAO variant must NOT contain instruction_units/execution_plan loop."""
        content = self._read()
        assert "instruction_units[]" not in content
        assert "execution_plan" not in content

    def test_no_dao_in_preflight(self):
        """No-DAO variant pre-flight checklist should not have DAO step."""
        content = self._read()
        assert "Did I process this message through DAO?" not in content

    def test_keeps_interaction_mode_note(self):
        """No-DAO variant still references interaction_mode for within-skill use."""
        content = self._read()
        assert "process_preference.interaction_mode" in content

    def test_keeps_skill_first_gate(self):
        """No-DAO variant still enforces skill-first workflow."""
        content = self._read()
        assert "Skill-First" in content
        assert "task-board.md" in content

    def test_mentions_dao_for_within_skill(self):
        """No-DAO variant still mentions DAO in within-skill context."""
        content = self._read()
        assert "x-ipe-dao-end-user-representative" in content

    def test_no_internal_backbone_exposed(self):
        """No 7-step backbone in no-DAO instructions."""
        content = self._read()
        assert "静虑" not in content
        assert "兼听" not in content
        assert "审势" not in content


class TestNoDaoChineseInstructions:
    """No-DAO ZH variant: DAO interception removed, within-skill DAO kept."""

    PATH = ROOT / "src" / "x_ipe" / "resources" / "copilot-instructions-zh-no-dao.md"

    def _read(self):
        return self.PATH.read_text(encoding="utf-8")

    def test_no_dao_first_mandate(self):
        """No-DAO ZH variant must NOT contain DAO-first interception mandate."""
        content = self._read()
        assert "每条用户消息必须先经过" not in content
        assert "DAO优先" not in content

    def test_no_instruction_units_loop(self):
        """No-DAO ZH variant must NOT contain instruction_units loop."""
        content = self._read()
        assert "instruction_units[]" not in content
        assert "execution_plan" not in content

    def test_keeps_interaction_mode_note(self):
        """No-DAO ZH variant still references interaction_mode."""
        content = self._read()
        assert "process_preference.interaction_mode" in content

    def test_keeps_skill_first_gate(self):
        """No-DAO ZH variant still enforces skill-first workflow."""
        content = self._read()
        assert "技能优先" in content
        assert "task-board.md" in content


class TestNoDaoTemplateInstructions:
    """No-DAO template variant for non-copilot CLIs."""

    PATH = ROOT / "src" / "x_ipe" / "resources" / "templates" / "instructions-template-no-dao.md"

    def _read(self):
        return self.PATH.read_text(encoding="utf-8")

    def test_no_dao_first_mandate(self):
        """Template no-DAO variant must NOT contain DAO-first mandate."""
        content = self._read()
        assert "EVERY user message MUST be processed through" not in content
        assert "DAO-First" not in content

    def test_keeps_skill_first_gate(self):
        """Template no-DAO variant still enforces skill-first workflow."""
        content = self._read()
        assert "Skill-First" in content
        assert "task-board.md" in content

    def test_keeps_interaction_mode_note(self):
        """Template no-DAO variant still references interaction_mode."""
        content = self._read()
        assert "process_preference.interaction_mode" in content
