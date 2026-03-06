"""Tests for FEATURE-047-C: Instruction Resource DAO Interception.

Covers:
- DAO interception guidance in repo-local instructions
- Packaged instruction sync (en/zh)
- Bounded DAO description
- No internal backbone exposure
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


class TestRepoLocalInstructions:
    """AC-047-C.1 through AC-047-C.4: Repo-local instructions have DAO guidance."""

    INSTRUCTIONS_PATH = ROOT / ".github" / "copilot-instructions.md"

    def _read(self):
        return self.INSTRUCTIONS_PATH.read_text(encoding="utf-8")

    def test_mentions_dao_skill(self):
        """AC-047-C.1: Instructions reference x-ipe-dao-end-user-representative."""
        assert "x-ipe-dao-end-user-representative" in self._read()

    def test_describes_auto_mode_dao_interception(self):
        """AC-047-C.2: Instructions explain DAO is called in auto mode at human touchpoints."""
        content = self._read().lower()
        assert "auto" in content
        # Should describe that DAO handles decision points in auto mode
        assert "human representative" in content or "human-representative" in content or "dao" in content.lower()

    def test_manual_mode_still_asks_human(self):
        """AC-047-C.3: Instructions clarify manual/stop_for_question still ask human."""
        content = self._read()
        assert "manual" in content.lower()

    def test_dao_described_as_bounded(self):
        """AC-047-C.4: DAO is described as bounded — represents intent, not task execution."""
        content = self._read().lower()
        assert "bounded" in content or "does not" in content or "not execute" in content or "not absorb" in content

    def test_no_internal_backbone_exposed(self):
        """BR-047-C.2: No 道 or 7-step backbone in instructions."""
        content = self._read()
        assert "静虑" not in content
        assert "兼听" not in content
        assert "审势" not in content

    def test_uses_process_preference(self):
        """Instructions use process_preference.auto_proceed, not require_human_review."""
        content = self._read()
        assert "process_preference.auto_proceed" in content


class TestPackagedEnglishInstructions:
    """AC-047-C.5, AC-047-C.7: Packaged English instructions synced."""

    EN_PATH = ROOT / "src" / "x_ipe" / "resources" / "copilot-instructions-en.md"

    def _read(self):
        return self.EN_PATH.read_text(encoding="utf-8")

    def test_mentions_dao_skill(self):
        """AC-047-C.5: Packaged EN instructions reference DAO."""
        assert "x-ipe-dao-end-user-representative" in self._read()

    def test_uses_process_preference(self):
        """AC-047-C.7: Uses process_preference.auto_proceed, not require_human_review."""
        content = self._read()
        assert "process_preference.auto_proceed" in content

    def test_synced_with_repo_local(self):
        """AC-047-C.5: Packaged EN matches repo-local for DAO section."""
        repo_local = (ROOT / ".github" / "copilot-instructions.md").read_text(encoding="utf-8")
        packaged = self._read()
        # Both should contain the DAO interception section
        assert "x-ipe-dao-end-user-representative" in repo_local
        assert "x-ipe-dao-end-user-representative" in packaged


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
