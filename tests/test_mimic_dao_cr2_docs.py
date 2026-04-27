"""
FEATURE-059-C / CR-002: DAO-to-mimic flow contract tests.

These tests verify the skill-level contracts that route behavior-learning
requests through the Knowledge Librarian DAO while the mimic skill owns polling
until the toolbar Analysis button is clicked.
"""
from pathlib import Path


ROOT = Path(__file__).parent.parent
MIMIC_SKILL = ROOT / ".github/skills/x-ipe-knowledge-mimic-web-behavior-tracker/SKILL.md"
DAO_SKILL = ROOT / ".github/skills/x-ipe-assistant-knowledge-librarian-DAO/SKILL.md"


def test_mimic_start_active_tracking_owns_polling_until_analysis():
    text = MIMIC_SKILL.read_text(encoding="utf-8")

    assert "this operation owns the 5s polling loop" in text
    assert "toolbar Analysis is clicked" in text
    assert "Polling MUST continue until toolbar Analysis is clicked" in text
    assert "Knowledge Librarian DAO does NOT own or drive per-tick polling" in text


def test_poll_tick_returns_analysis_signal_to_start_active_tracking():
    text = MIMIC_SKILL.read_text(encoding="utf-8")

    assert "Internal sub-operation for start_active_tracking" in text
    assert "analysisRequested" in text
    assert "mark_analysis_requested" in text
    assert "result.analysis_requested" in text


def test_mimic_consolidates_and_returns_payload_to_dao():
    text = MIMIC_SKILL.read_text(encoding="utf-8")

    assert "build_stop_script" in text
    assert "PostProcessor.process" in text
    assert "build_observation_payload" in text
    assert "RETURN this operation_output to the caller" in text


def test_dao_classifies_behavior_learning_requests():
    text = DAO_SKILL.read_text(encoding="utf-8")

    assert "behavior_learning" in text
    assert "learn behavior" in text
    assert "track behavior" in text
    assert "observe user flow" in text
    assert "mimic website behavior" in text


def test_dao_delegates_behavior_learning_to_mimic_active_tracking():
    text = DAO_SKILL.read_text(encoding="utf-8")

    assert "discovered_skills.mimics" in text
    assert "x-ipe-knowledge-mimic-web-behavior-tracker.start_active_tracking" in text
    assert "WAIT for `start_active_tracking` to own polling" in text
    assert "operation_output.result.observation_payload" in text
    assert "APPEND observation_payload to gathered_knowledge[]" in text
