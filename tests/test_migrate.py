"""Tests for migrate.py — FEATURE-057-C.

Validates:
- Markdown parsing: tasks and features
- Status normalization (emoji stripping)
- Output link extraction
- Date parsing
- JSON writing with duplicate detection
- Dry-run mode
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".github" / "skills" / "x-ipe-tool-task-board-manager" / "scripts"))

import _board_lib  # noqa: E402
from migrate import (  # noqa: E402
    _normalize_status,
    _parse_date,
    _parse_output_links,
    _parse_spec_link,
    _parse_table_row,
    _strip_emoji,
    parse_features_md,
    parse_tasks_md,
    write_features_json,
    write_tasks_json,
)


@pytest.fixture(autouse=True)
def _patch_project_root(monkeypatch, tmp_path):
    """Redirect _board_lib to use tmp_path as project root."""
    monkeypatch.setattr(_board_lib, "_resolve_project_root", lambda: tmp_path)


# ── Helper Data ──────────────────────────────────────────────────────

SAMPLE_TASK_MD = """# Task Board

## Active Tasks

| Task ID | Task | Description | Role | Status | Last Updated | Output Links | Next Task |
| TASK-100 | Bug Fix | Fix login issue | Alice | 🔄 in_progress | 04-03-2026 | [commit](abc123) | TASK-101 |
| TASK-101 | Implementation | Add search | Bob 🤖 | ✅ done | 04-02-2026 | — | — |

## Completed Tasks
| Task ID | Task | Description | Role | Status | Last Updated | Output Links | Notes |
|---------|-----------|-------------|------|--------|--------------|--------------|-------|
| TASK-050 | Ideation | Brainstorm | Carol | ✅ completed | 03-15-2026 | [spec](spec.md), [design](design.md) | Good |

## Cancelled Tasks

| Task ID | Task | Description | Reason | Last Updated | Output Links |
| TASK-010 | Bug Fix | Old bug | Superseded | 01-01-2026 | — |
"""

SAMPLE_FEATURES_MD = """# Feature Board

## Features

| Feature ID | Epic ID | Feature Title | Version | Status | Specification Link | Created | Last Updated |
|------------|---------|---------------|---------|--------|-------------------|---------|--------------|
| FEATURE-001 | EPIC-001 | Navigation | v1.0 | Completed | [specification.md](x-ipe-docs/requirements/EPIC-001/spec.md) | 01-18-2026 | 03-20-2026 |
| FEATURE-002 | EPIC-001 | Search | v0.5 | Planned | — | 02-01-2026 | 02-01-2026 |
| FEATURE-003 | EPIC-002 | Editor | v1.0 | Tested | [specification.md](x-ipe-docs/requirements/EPIC-002/spec.md) | 01-20-2026 | 04-01-2026 |
"""


# ── Unit Tests: Helpers ──────────────────────────────────────────────

class TestStripEmoji:
    def test_strips_checkmark(self):
        assert _strip_emoji("✅ done") == "done"

    def test_strips_spinner(self):
        assert _strip_emoji("🔄 in_progress") == "in_progress"

    def test_no_emoji(self):
        assert _strip_emoji("pending") == "pending"

    def test_emoji_in_name(self):
        assert _strip_emoji("Bob 🤖") == "Bob"


class TestNormalizeStatus:
    def test_done_with_emoji(self):
        assert _normalize_status("✅ done") == "completed"

    def test_completed_with_emoji(self):
        assert _normalize_status("✅ completed") == "completed"

    def test_in_progress_with_emoji(self):
        assert _normalize_status("🔄 in_progress") == "in_progress"

    def test_plain_pending(self):
        assert _normalize_status("pending") == "pending"

    def test_in_progress_with_space(self):
        assert _normalize_status("in progress") == "in_progress"

    def test_unknown_passes_through(self):
        assert _normalize_status("custom_status") == "custom_status"


class TestParseOutputLinks:
    def test_markdown_links(self):
        assert _parse_output_links("[commit](abc123)") == ["abc123"]

    def test_multiple_links(self):
        result = _parse_output_links("[spec](spec.md), [design](design.md)")
        assert result == ["spec.md", "design.md"]

    def test_dash(self):
        assert _parse_output_links("—") == []

    def test_empty(self):
        assert _parse_output_links("") == []


class TestParseSpecLink:
    def test_markdown_link(self):
        assert _parse_spec_link("[specification.md](path/to/spec.md)") == "path/to/spec.md"

    def test_dash(self):
        assert _parse_spec_link("—") == ""

    def test_plain_text(self):
        assert _parse_spec_link("spec.md") == "spec.md"


class TestParseDate:
    def test_mm_dd_yyyy(self):
        result = _parse_date("04-03-2026")
        assert "2026-04-03" in result

    def test_mm_dd_yyyy_hh_mm_ss(self):
        result = _parse_date("03-15-2026 09:30:00")
        assert "2026-03-15" in result

    def test_dash_returns_now(self):
        result = _parse_date("—")
        assert "T" in result  # ISO format

    def test_empty_returns_now(self):
        result = _parse_date("")
        assert "T" in result


class TestParseTableRow:
    def test_basic_row(self):
        result = _parse_table_row("| A | B | C |")
        assert result == ["A", "B", "C"]

    def test_strips_whitespace(self):
        result = _parse_table_row("|  hello  |  world  |")
        assert result == ["hello", "world"]


# ── Integration Tests: Markdown Parsing ──────────────────────────────

class TestParseTasksMd:
    def test_parses_all_sections(self, tmp_path):
        md_path = tmp_path / "task-board.md"
        md_path.write_text(SAMPLE_TASK_MD)
        tasks = parse_tasks_md(md_path)
        assert len(tasks) == 4

    def test_active_task_fields(self, tmp_path):
        md_path = tmp_path / "task-board.md"
        md_path.write_text(SAMPLE_TASK_MD)
        tasks = parse_tasks_md(md_path)
        t100 = next(t for t in tasks if t["task_id"] == "TASK-100")
        assert t100["task_type"] == "Bug Fix"
        assert t100["description"] == "Fix login issue"
        assert t100["status"] == "in_progress"
        assert t100["next_task"] == "TASK-101"
        assert t100["output_links"] == ["abc123"]

    def test_completed_task(self, tmp_path):
        md_path = tmp_path / "task-board.md"
        md_path.write_text(SAMPLE_TASK_MD)
        tasks = parse_tasks_md(md_path)
        t050 = next(t for t in tasks if t["task_id"] == "TASK-050")
        assert t050["status"] == "completed"
        assert len(t050["output_links"]) == 2

    def test_cancelled_task(self, tmp_path):
        md_path = tmp_path / "task-board.md"
        md_path.write_text(SAMPLE_TASK_MD)
        tasks = parse_tasks_md(md_path)
        t010 = next(t for t in tasks if t["task_id"] == "TASK-010")
        assert t010["status"] == "cancelled"
        assert t010["next_task"] == ""

    def test_done_status_normalized(self, tmp_path):
        md_path = tmp_path / "task-board.md"
        md_path.write_text(SAMPLE_TASK_MD)
        tasks = parse_tasks_md(md_path)
        t101 = next(t for t in tasks if t["task_id"] == "TASK-101")
        assert t101["status"] == "completed"


class TestParseFeaturesMd:
    def test_parses_all_features(self, tmp_path):
        md_path = tmp_path / "features.md"
        md_path.write_text(SAMPLE_FEATURES_MD)
        features = parse_features_md(md_path)
        assert len(features) == 3

    def test_feature_fields(self, tmp_path):
        md_path = tmp_path / "features.md"
        md_path.write_text(SAMPLE_FEATURES_MD)
        features = parse_features_md(md_path)
        f001 = next(f for f in features if f["feature_id"] == "FEATURE-001")
        assert f001["epic_id"] == "EPIC-001"
        assert f001["title"] == "Navigation"
        assert f001["version"] == "v1.0"
        assert f001["status"] == "Completed"
        assert f001["specification_link"] == "x-ipe-docs/requirements/EPIC-001/spec.md"

    def test_no_spec_link(self, tmp_path):
        md_path = tmp_path / "features.md"
        md_path.write_text(SAMPLE_FEATURES_MD)
        features = parse_features_md(md_path)
        f002 = next(f for f in features if f["feature_id"] == "FEATURE-002")
        assert f002["specification_link"] == ""
        assert f002["status"] == "Planned"


# ── Integration Tests: JSON Writing ──────────────────────────────────

class TestWriteTasksJson:
    def test_writes_daily_files(self, tmp_path):
        tasks = [
            {
                "task_id": "TASK-1", "task_type": "Bug Fix", "description": "d",
                "role": "r", "status": "done", "created_at": "2026-04-03T00:00:00+00:00",
                "last_updated": "2026-04-03T00:00:00+00:00", "output_links": [], "next_task": "",
            },
        ]
        stats = write_tasks_json(tasks)
        assert stats["total"] == 1
        assert stats["files_written"] >= 1
        tasks_dir = tmp_path / "x-ipe-docs" / "planning" / "tasks"
        assert (tasks_dir / "tasks-2026-04-03.json").exists()
        assert (tasks_dir / "tasks-index.json").exists()

    def test_skips_duplicates(self, tmp_path):
        task = {
            "task_id": "TASK-1", "task_type": "Bug Fix", "description": "d",
            "role": "r", "status": "done", "created_at": "2026-04-03T00:00:00+00:00",
            "last_updated": "2026-04-03T00:00:00+00:00", "output_links": [], "next_task": "",
        }
        write_tasks_json([task])
        stats2 = write_tasks_json([task])
        assert stats2["skipped_duplicates"] == 1

    def test_dry_run_no_files(self, tmp_path):
        tasks = [
            {
                "task_id": "TASK-1", "task_type": "Bug Fix", "description": "d",
                "role": "r", "status": "done", "created_at": "2026-04-03T00:00:00+00:00",
                "last_updated": "2026-04-03T00:00:00+00:00", "output_links": [], "next_task": "",
            },
        ]
        stats = write_tasks_json(tasks, dry_run=True)
        assert stats["total"] == 1
        tasks_dir = tmp_path / "x-ipe-docs" / "planning" / "tasks"
        assert not (tasks_dir / "tasks-2026-04-03.json").exists()

    def test_index_contains_entries(self, tmp_path):
        task = {
            "task_id": "TASK-42", "task_type": "Bug Fix", "description": "d",
            "role": "r", "status": "done", "created_at": "2026-04-03T00:00:00+00:00",
            "last_updated": "2026-04-03T00:00:00+00:00", "output_links": [], "next_task": "",
        }
        write_tasks_json([task])
        index_path = tmp_path / "x-ipe-docs" / "planning" / "tasks" / "tasks-index.json"
        index = json.loads(index_path.read_text())
        assert "TASK-42" in index["entries"]


class TestWriteFeaturesJson:
    def test_writes_features_file(self, tmp_path):
        features = [
            {
                "feature_id": "FEATURE-1", "epic_id": "EPIC-1", "title": "Nav",
                "version": "v1.0", "status": "Completed", "description": "",
                "dependencies": [], "specification_link": "",
                "created_at": "2026-01-01T00:00:00+00:00",
                "last_updated": "2026-03-01T00:00:00+00:00",
            },
        ]
        stats = write_features_json(features)
        assert stats["total"] == 1
        fp = tmp_path / "x-ipe-docs" / "planning" / "features" / "features.json"
        assert fp.exists()
        data = json.loads(fp.read_text())
        assert len(data["features"]) == 1

    def test_skips_duplicates(self, tmp_path):
        feature = {
            "feature_id": "FEATURE-1", "epic_id": "EPIC-1", "title": "Nav",
            "version": "v1.0", "status": "Completed", "description": "",
            "dependencies": [], "specification_link": "",
            "created_at": "2026-01-01T00:00:00+00:00",
            "last_updated": "2026-03-01T00:00:00+00:00",
        }
        write_features_json([feature])
        stats2 = write_features_json([feature])
        assert stats2["skipped_duplicates"] == 1

    def test_dry_run_no_files(self, tmp_path):
        features = [
            {
                "feature_id": "FEATURE-1", "epic_id": "EPIC-1", "title": "Nav",
                "version": "v1.0", "status": "Completed", "description": "",
                "dependencies": [], "specification_link": "",
                "created_at": "2026-01-01T00:00:00+00:00",
                "last_updated": "2026-03-01T00:00:00+00:00",
            },
        ]
        stats = write_features_json(features, dry_run=True)
        assert stats["total"] == 1
        fp = tmp_path / "x-ipe-docs" / "planning" / "features" / "features.json"
        assert not fp.exists()
