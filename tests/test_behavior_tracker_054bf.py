"""
EPIC-054 / CR-001 compatibility tests for the retired learning behavior tracker.

The old x-ipe-tool-learning-behavior-tracker-for-web skill has been replaced by
x-ipe-knowledge-mimic-web-behavior-tracker. These tests keep the original
behavioral guarantees covered against the new active_tracking helpers.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).parent.parent
        / ".github"
        / "skills"
        / "x-ipe-knowledge-mimic-web-behavior-tracker"
        / "scripts"
    ),
)

from active_tracking import (  # noqa: E402
    SCHEMA_VERSION,
    _fix_double_encoded_utf8,
    build_clear_guard_script,
    build_poll_script,
    detect_url_change,
    init_session,
    merge_events,
    record_navigation,
    record_screenshot,
    screenshot_path,
    should_screenshot,
)


class TestMimicActiveTrackingCompatibility:
    def test_init_session_seeds_metadata_and_navigation_history(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session_dir = Path(tmpdir) / "x-ipe-docs" / ".mimicked" / "test-session"
            session = init_session(
                session_dir=session_dir,
                session_id="test-session",
                target_app="https://example.com/path",
                purpose="Test",
                pii_whitelist=[],
                buffer_capacity=10000,
                active_config={"polling_interval_s": 5},
            )

            assert session["session_id"] == "test-session"
            assert session["purpose"] == "Test"
            assert session["navigation_history"] == ["https://example.com/path"]
            assert (session_dir / "session.json").exists()

    def test_merge_events_writes_schema_2_track_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            track_list = Path(tmpdir) / "track-list.json"
            record = merge_events(
                track_list,
                [{"type": "click", "timestamp": 1000}],
                {"session_id": "test-session"},
            )

            assert track_list.exists()
            data = json.loads(track_list.read_text(encoding="utf-8"))
            assert record["schema_version"] == SCHEMA_VERSION
            assert data["schema_version"] == "2.0"
            assert data["event_count"] == 1

    def test_merge_events_fixes_double_encoded_chinese(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            garbled = "为了您".encode("utf-8").decode("latin-1")
            track_list = Path(tmpdir) / "track-list.json"

            merge_events(
                track_list,
                [{"type": "click", "target": {"textContent": garbled}}],
                {"session_id": "test-session"},
            )

            data = json.loads(track_list.read_text(encoding="utf-8"))
            assert data["events"][0]["target"]["textContent"] == "为了您"

    def test_fix_double_encoded_utf8_recurses_nested_structures(self):
        garbled = "为了您".encode("utf-8").decode("latin-1")
        fixed = _fix_double_encoded_utf8({"events": [{"text": garbled}]})
        assert fixed == {"events": [{"text": "为了您"}]}

    def test_url_change_detection_and_navigation_recording(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session_dir = Path(tmpdir)
            init_session(session_dir, "sid", "https://example.com/page1", "Test", [], 10000)

            assert detect_url_change(session_dir, "https://example.com/page1") is False
            assert detect_url_change(session_dir, "https://example.com/page2") is True

            record_navigation(session_dir, "https://example.com/page2")
            record_navigation(session_dir, "https://example.com/page2")

            session = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))
            assert session["navigation_history"] == [
                "https://example.com/page1",
                "https://example.com/page2",
            ]

    def test_screenshot_gate_and_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session_dir = Path(tmpdir) / "sid"

            assert should_screenshot(1, 0) is True
            assert should_screenshot(1, 1) is False
            assert screenshot_path(session_dir, 2) == session_dir / "screenshots" / "tick-2.png"

    def test_record_screenshot_appends_to_track_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            track_list = Path(tmpdir) / "track-list.json"
            merge_events(track_list, [], {"session_id": "sid"})

            record_screenshot(track_list, "screenshots/tick-1.png")

            data = json.loads(track_list.read_text(encoding="utf-8"))
            assert data["screenshots"][0]["path"] == "screenshots/tick-1.png"

    def test_script_builders_match_old_agent_contract(self):
        poll_script = build_poll_script()
        clear_script = build_clear_guard_script()

        assert "window.__xipeBehaviorTracker.collect()" in poll_script
        assert "not_injected" in poll_script
        assert clear_script == "window.__xipeBehaviorTrackerInjected = false;"
