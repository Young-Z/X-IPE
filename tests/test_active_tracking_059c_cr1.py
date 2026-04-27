"""
FEATURE-059-C / CR-001: Active Tracking Helper Tests

Tests for active_tracking.py — pure helpers used by the agent-driven 5s
polling loop in x-ipe-knowledge-mimic-web-behavior-tracker.

Validates AC-059C-17 (a/b/c) building blocks:
- 17a: poll script + merge_events into single accumulating track-list.json
- 17b: detect_url_change + record_navigation
- 17c: should_screenshot gate + screenshot_path + record_screenshot
"""
import json
import sys
from pathlib import Path

import pytest

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
    build_clear_guard_script,
    build_observation_payload,
    build_poll_script,
    build_reset_analysis_ui_script,
    build_stop_script,
    consume_analysis_request,
    detect_url_change,
    init_session,
    is_analysis_requested,
    mark_analysis_requested,
    merge_events,
    record_navigation,
    record_screenshot,
    screenshot_path,
    should_screenshot,
)


# --- AC-17a: polling + accumulating track-list.json ---


class TestPollScript:
    def test_returns_string(self):
        s = build_poll_script()
        assert isinstance(s, str)

    def test_handles_not_injected(self):
        s = build_poll_script()
        assert "not_injected" in s
        assert "__xipeBehaviorTracker" in s

    def test_collects_url(self):
        assert "location.href" in build_poll_script()

    def test_collects_analysis_signal_and_status(self):
        s = build_poll_script()
        assert "getAnalysisFlag" in s
        assert "analysisRequested" in s
        assert "getStatus" in s


class TestMergeEvents:
    def test_creates_file_when_absent(self, tmp_path):
        path = tmp_path / "track-list.json"
        meta = {"session_id": "s1"}
        rec = merge_events(path, [{"type": "click"}], meta)
        assert path.exists()
        assert rec["schema_version"] == SCHEMA_VERSION
        assert rec["event_count"] == 1
        assert rec["session"] == meta

    def test_accumulates_across_ticks(self, tmp_path):
        path = tmp_path / "track-list.json"
        merge_events(path, [{"type": "click", "n": 1}], {"id": "s1"})
        merge_events(path, [{"type": "scroll", "n": 2}], {"id": "s1"})
        merge_events(path, [{"type": "input", "n": 3}], {"id": "s1"})
        rec = json.loads(path.read_text())
        assert rec["event_count"] == 3
        assert [e["n"] for e in rec["events"]] == [1, 2, 3]

    def test_empty_events_still_writes(self, tmp_path):
        # Even empty events should refresh last_updated; track-list.json is the
        # single source of truth (no per-tick files).
        path = tmp_path / "track-list.json"
        merge_events(path, [{"type": "click"}], {"id": "s1"})
        rec1 = json.loads(path.read_text())
        merge_events(path, [], {"id": "s1"})
        rec2 = json.loads(path.read_text())
        assert rec2["event_count"] == 1
        assert rec2["last_updated"] >= rec1["last_updated"]

    def test_preserves_screenshots_across_merges(self, tmp_path):
        path = tmp_path / "track-list.json"
        merge_events(path, [{"type": "click"}], {"id": "s1"})
        record_screenshot(path, "screenshots/tick-1.png")
        merge_events(path, [{"type": "scroll"}], {"id": "s1"})
        rec = json.loads(path.read_text())
        assert len(rec["screenshots"]) == 1
        assert rec["screenshots"][0]["path"] == "screenshots/tick-1.png"


# --- AC-17b: URL-change detection + reinject ---


class TestClearGuardScript:
    def test_clears_guard_flag(self):
        s = build_clear_guard_script()
        assert "__xipeBehaviorTrackerInjected" in s
        assert "false" in s


class TestAnalysisControlScripts:
    def test_stop_script_stops_tracker_and_returns_events(self):
        s = build_stop_script()
        assert "__xipeBehaviorTracker.stop()" in s
        assert "collect()" in s
        assert "analysisRequested" in s

    def test_reset_analysis_ui_script_calls_toolbar_reset(self):
        s = build_reset_analysis_ui_script()
        assert "resetAnalysisUI" in s


class TestNavigationTracking:
    def test_first_call_returns_change(self, tmp_path):
        # No history yet → treat as change so initial seed happens.
        assert detect_url_change(tmp_path, "https://example.com") is True

    def test_init_session_seeds_history(self, tmp_path):
        s = init_session(
            tmp_path,
            session_id="mimic-20260423-abc",
            target_app="https://example.com",
            purpose="test",
            pii_whitelist=[],
            buffer_capacity=10000,
        )
        assert s["navigation_history"] == ["https://example.com"]
        assert s["analysis_requested"] is False
        assert s["analysis_handoff_consumed"] is False

    def test_no_change_when_url_matches_last(self, tmp_path):
        init_session(tmp_path, "s1", "https://example.com", "p", [], 10000)
        assert detect_url_change(tmp_path, "https://example.com") is False

    def test_change_detected_when_url_differs(self, tmp_path):
        init_session(tmp_path, "s1", "https://example.com", "p", [], 10000)
        assert detect_url_change(tmp_path, "https://example.com/page2") is True

    def test_record_navigation_appends(self, tmp_path):
        init_session(tmp_path, "s1", "https://example.com", "p", [], 10000)
        record_navigation(tmp_path, "https://example.com/page2")
        record_navigation(tmp_path, "https://example.com/page3")
        session = json.loads((tmp_path / "session.json").read_text())
        assert session["navigation_history"] == [
            "https://example.com",
            "https://example.com/page2",
            "https://example.com/page3",
        ]

    def test_record_navigation_dedupes_consecutive(self, tmp_path):
        init_session(tmp_path, "s1", "https://example.com", "p", [], 10000)
        record_navigation(tmp_path, "https://example.com/page2")
        record_navigation(tmp_path, "https://example.com/page2")  # duplicate
        session = json.loads((tmp_path / "session.json").read_text())
        assert session["navigation_history"] == [
            "https://example.com",
            "https://example.com/page2",
        ]

    def test_analysis_request_survives_navigation_update_until_consumed(self, tmp_path):
        init_session(tmp_path, "s1", "https://example.com", "p", [], 10000)
        mark_analysis_requested(tmp_path)
        record_navigation(tmp_path, "https://example.com/page2")

        assert is_analysis_requested(tmp_path) is True
        session = json.loads((tmp_path / "session.json").read_text())
        assert session["analysis_requested"] is True
        assert session["analysis_handoff_consumed"] is False
        assert session["navigation_history"][-1] == "https://example.com/page2"

        consumed = consume_analysis_request(tmp_path)
        assert consumed["analysis_requested"] is False
        assert consumed["analysis_handoff_consumed"] is True
        assert is_analysis_requested(tmp_path) is False


# --- AC-17c: screenshot gating + path layout ---


class TestScreenshotGate:
    def test_no_screenshot_when_no_new_events(self):
        assert should_screenshot(5, 5) is False

    def test_no_screenshot_when_count_decreased(self):
        # Defensive: shouldn't happen but should not screenshot.
        assert should_screenshot(3, 5) is False

    def test_screenshot_when_new_events_arrive(self):
        assert should_screenshot(7, 5) is True


class TestScreenshotLayout:
    def test_path_under_screenshots_dir(self, tmp_path):
        p = screenshot_path(tmp_path, 3)
        assert p.parent.name == "screenshots"
        assert p.name == "tick-3.png"
        assert p.parent.parent == tmp_path

    def test_record_screenshot_appends_to_track_list(self, tmp_path):
        path = tmp_path / "track-list.json"
        merge_events(path, [{"type": "click"}], {"id": "s1"})
        record_screenshot(path, "screenshots/tick-1.png")
        record_screenshot(path, "screenshots/tick-5.png")
        rec = json.loads(path.read_text())
        assert [s["path"] for s in rec["screenshots"]] == [
            "screenshots/tick-1.png",
            "screenshots/tick-5.png",
        ]
        assert all("captured_at" in s for s in rec["screenshots"])

    def test_record_screenshot_no_op_when_track_list_missing(self, tmp_path):
        # Should not raise, just no-op.
        record_screenshot(tmp_path / "missing.json", "x.png")


# --- Integration: full tick simulation ---


class TestActiveTickSimulation:
    """Simulates 3 ticks of the agent-driven loop using only helpers."""

    def test_three_ticks_flow(self, tmp_path):
        sd = tmp_path
        init_session(sd, "s1", "https://app.example.com", "demo", [], 10000)
        track = sd / "track-list.json"

        # Tick 1: 2 new events, screenshot expected
        last_count = 0
        merge_events(track, [{"t": "click"}, {"t": "input"}], {"id": "s1"})
        rec = json.loads(track.read_text())
        assert should_screenshot(rec["event_count"], last_count)
        record_screenshot(track, "screenshots/tick-1.png")
        last_count = rec["event_count"]

        # Tick 2: no new events, NO screenshot
        merge_events(track, [], {"id": "s1"})
        rec = json.loads(track.read_text())
        assert should_screenshot(rec["event_count"], last_count) is False
        last_count = rec["event_count"]

        # Tick 3: URL change → re-inject + record + new events + screenshot
        new_url = "https://app.example.com/checkout"
        assert detect_url_change(sd, new_url) is True
        record_navigation(sd, new_url)
        merge_events(track, [{"t": "scroll"}], {"id": "s1"})
        rec = json.loads(track.read_text())
        assert should_screenshot(rec["event_count"], last_count)
        record_screenshot(track, "screenshots/tick-3.png")

        # Final assertions
        rec = json.loads(track.read_text())
        session = json.loads((sd / "session.json").read_text())
        assert rec["event_count"] == 3
        assert len(rec["screenshots"]) == 2
        assert session["navigation_history"] == [
            "https://app.example.com",
            "https://app.example.com/checkout",
        ]


# --- AC-18c: final payload returned to DAO ---


class TestObservationPayload:
    def test_builds_final_payload_for_dao(self, tmp_path):
        track = tmp_path / "track-list.json"
        merge_events(
            track,
            [{"type": "click", "target": {"cssSelector": "button.buy"}}],
            {"session_id": "mimic-20260427-abc"},
        )
        summary = {"analysis": {"flow_narrative": "User clicked buy."}}

        payload = build_observation_payload(track, summary)

        assert payload["tracking_session_id"] == "mimic-20260427-abc"
        assert payload["analysis_requested"] is True
        assert payload["event_count"] == 1
        assert payload["observation_summary"] == summary
        assert payload["observations"][0]["type"] == "click"
        assert payload["raw_events"] == payload["observations"]
        assert payload["writes_to"] == str(tmp_path)
