"""
FEATURE-059-C / CR-001: Active Tracking Helpers

Pure helpers for the mimic-owned 5s polling loop in the
x-ipe-knowledge-mimic-web-behavior-tracker skill.

Architecture: NO subprocess. The start_active_tracking operation owns the
5-second polling loop via Chrome DevTools MCP, calling these helpers per tick.

Helpers:
    - build_poll_script() -> str
        JS to drain the in-page event buffer (returns events + url + count).
    - build_clear_guard_script() -> str
        JS to clear window.__xipeBehaviorTrackerInjected for re-injection.
    - merge_events(track_list_path, new_events, session_meta) -> dict
        Merge new events into accumulating track-list.json (schema 2.0).
    - detect_url_change(session_dir, current_url) -> bool
        Compare current URL against last entry in session.json::navigation_history.
    - record_navigation(session_dir, url) -> None
        Append URL to session.json::navigation_history.
    - should_screenshot(event_count, last_event_count) -> bool
        Returns True iff event_count > last_event_count (matches old skill gate).
    - screenshot_path(session_dir, tick_n) -> Path
        Returns x-ipe-docs/.mimicked/{session_id}/screenshots/tick-{n}.png.
    - record_screenshot(track_list_path, screenshot_relpath) -> None
        Append screenshot path to track-list.json::screenshots array.
    - mark_analysis_requested(session_dir) -> dict
        Persist sticky toolbar Analysis request in session.json.
    - consume_analysis_request(session_dir) -> dict
        Mark Analysis handoff consumed after DAO payload is prepared.
    - build_stop_script() -> str
        JS to stop in-page tracker and return final collected events.
    - build_reset_analysis_ui_script() -> str
        JS to reset toolbar Analysis button after payload handoff.
    - build_observation_payload(track_list_path, observation_summary) -> dict
        Build final return payload for Knowledge Librarian DAO.

Source pattern: ported from the retired learning behavior tracker tool
(BehaviorTrackerSkill poll loop + InjectionManager helpers).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


SCHEMA_VERSION = "2.0"


def _fix_double_encoded_utf8(obj):
    """Fix UTF-8 text double-encoded as Latin-1 during browser transport."""
    if isinstance(obj, str):
        try:
            return obj.encode("latin-1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            return obj
    if isinstance(obj, dict):
        return {key: _fix_double_encoded_utf8(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_fix_double_encoded_utf8(item) for item in obj]
    return obj


def build_poll_script() -> str:
    """JS to drain the in-page event buffer.

    Returns a JSON string with shape:
        {events: [...], eventCount: int, url: str,
         analysisRequested: bool, status: str, error?: 'not_injected'}
    """
    return (
        "(() => {"
        "  if (!window.__xipeBehaviorTracker) {"
        "    return JSON.stringify({events:[],eventCount:0,url:location.href,error:'not_injected'});"
        "  }"
        "  const d = window.__xipeBehaviorTracker.collect();"
        "  d.url = location.href;"
        "  d.analysisRequested = window.__xipeBehaviorTracker.getAnalysisFlag();"
        "  d.status = window.__xipeBehaviorTracker.getStatus();"
        "  return JSON.stringify(d);"
        "})();"
    )


def build_clear_guard_script() -> str:
    """JS to clear the injection guard so the tracker can be re-injected."""
    return "window.__xipeBehaviorTrackerInjected = false;"


def build_stop_script() -> str:
    """JS to stop the in-page tracker and return the final event buffer."""
    return (
        "(() => {"
        "  if (!window.__xipeBehaviorTracker) {"
        "    return JSON.stringify({events:[],eventCount:0,url:location.href,error:'not_injected'});"
        "  }"
        "  window.__xipeBehaviorTracker.stop();"
        "  const d = window.__xipeBehaviorTracker.collect();"
        "  d.url = location.href;"
        "  d.status = window.__xipeBehaviorTracker.getStatus();"
        "  d.analysisRequested = window.__xipeBehaviorTracker.getAnalysisFlag();"
        "  return JSON.stringify(d);"
        "})();"
    )


def build_reset_analysis_ui_script() -> str:
    """JS to reset the toolbar Analysis UI after the DAO handoff is prepared."""
    return (
        "(() => {"
        "  if (window.__xipeBehaviorTracker) {"
        "    window.__xipeBehaviorTracker.resetAnalysisUI();"
        "  }"
        "})();"
    )


def _read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def merge_events(
    track_list_path: Path,
    new_events: list,
    session_meta: dict,
) -> dict:
    """Merge new events into accumulating track-list.json.

    Format matches the deprecated skill's write_track_list output (schema 2.0):
    a single overwritten file containing the cumulative event list. Returns
    the written record.
    """
    existing = _read_json(track_list_path, {"events": [], "screenshots": []})
    normalized_events = _fix_double_encoded_utf8(new_events or [])
    all_events = list(existing.get("events", [])) + list(normalized_events)
    record = {
        "schema_version": SCHEMA_VERSION,
        "session": session_meta,
        "events": all_events,
        "event_count": len(all_events),
        "screenshots": existing.get("screenshots", []),
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(track_list_path, record)
    return record


def detect_url_change(session_dir: Path, current_url: str) -> bool:
    """Return True iff current_url differs from the last navigation_history entry."""
    session_json = session_dir / "session.json"
    session = _read_json(session_json, {})
    history = session.get("navigation_history", [])
    if not history:
        return True
    return history[-1] != current_url


def record_navigation(session_dir: Path, url: str) -> None:
    """Append url to session.json::navigation_history (idempotent: skips duplicate of last)."""
    session_json = session_dir / "session.json"
    session = _read_json(session_json, {})
    history = list(session.get("navigation_history", []))
    if history and history[-1] == url:
        return
    history.append(url)
    session["navigation_history"] = history
    session["last_updated"] = datetime.now(timezone.utc).isoformat()
    _write_json(session_json, session)


def should_screenshot(event_count: int, last_event_count: int) -> bool:
    """Old-skill gate: only screenshot when new events have arrived."""
    return event_count > last_event_count


def screenshot_path(session_dir: Path, tick_n: int) -> Path:
    """Return x-ipe-docs/.mimicked/{session_id}/screenshots/tick-{n}.png."""
    return session_dir / "screenshots" / f"tick-{tick_n}.png"


def record_screenshot(track_list_path: Path, screenshot_relpath: str) -> None:
    """Append screenshot relpath to track-list.json::screenshots array."""
    record = _read_json(track_list_path, None)
    if record is None:
        return
    screenshots = list(record.get("screenshots", []))
    screenshots.append(
        {
            "path": screenshot_relpath,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    record["screenshots"] = screenshots
    record["last_updated"] = datetime.now(timezone.utc).isoformat()
    _write_json(track_list_path, record)


def mark_analysis_requested(session_dir: Path) -> dict:
    """Persist a sticky Analysis request in session.json until consumed."""
    session_json = session_dir / "session.json"
    session = _read_json(session_json, {})
    now = datetime.now(timezone.utc).isoformat()
    session["analysis_requested"] = True
    session["analysis_requested_at"] = session.get("analysis_requested_at") or now
    session["analysis_handoff_consumed"] = False
    session["last_updated"] = now
    _write_json(session_json, session)
    return session


def consume_analysis_request(session_dir: Path) -> dict:
    """Mark the sticky Analysis request consumed after final payload creation."""
    session_json = session_dir / "session.json"
    session = _read_json(session_json, {})
    now = datetime.now(timezone.utc).isoformat()
    session["analysis_requested"] = False
    session["analysis_handoff_consumed"] = True
    session["analysis_handoff_consumed_at"] = now
    session["last_updated"] = now
    _write_json(session_json, session)
    return session


def is_analysis_requested(session_dir: Path) -> bool:
    """Return persisted Analysis request state for start_active_tracking."""
    return bool(_read_json(session_dir / "session.json", {}).get("analysis_requested"))


def build_observation_payload(track_list_path: Path, observation_summary: dict) -> dict:
    """Build final mimic observations payload returned to Knowledge Librarian DAO."""
    record = _read_json(track_list_path, {"events": [], "event_count": 0, "session": {}})
    events = list(record.get("events", []))
    session = record.get("session", {}) or {}
    return {
        "tracking_session_id": session.get("session_id") or session.get("id"),
        "analysis_requested": True,
        "event_count": record.get("event_count", len(events)),
        "observation_summary": observation_summary or {},
        "observations": events,
        "raw_events": events,
        "writes_to": str(track_list_path.parent),
    }


def init_session(
    session_dir: Path,
    session_id: str,
    target_app: str,
    purpose: str,
    pii_whitelist: list,
    buffer_capacity: int,
    active_config: Optional[dict] = None,
) -> dict:
    """Create session.json with metadata + navigation_history seeded with target_app.

    Used by start_active_tracking. Idempotent — if session.json exists, only
    fills missing keys (does not overwrite event-count fields).
    """
    session_dir.mkdir(parents=True, exist_ok=True)
    session_json = session_dir / "session.json"
    existing = _read_json(session_json, {})
    now = datetime.now(timezone.utc).isoformat()
    session = {
        "session_id": session_id,
        "target_app": target_app,
        "purpose": purpose,
        "pii_whitelist": pii_whitelist or [],
        "buffer_capacity": buffer_capacity,
        "active_config": active_config or {},
        "navigation_history": existing.get("navigation_history") or [target_app],
        "last_event_count": existing.get("last_event_count", 0),
        "analysis_requested": existing.get("analysis_requested", False),
        "analysis_handoff_consumed": existing.get("analysis_handoff_consumed", False),
        "started_at": existing.get("started_at") or now,
        "last_updated": now,
    }
    _write_json(session_json, session)
    return session
