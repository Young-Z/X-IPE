"""Tests for task CRUD scripts (FEATURE-055-B).

Covers: task_create, task_update, task_query, task_archive.
"""
from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

_SCRIPTS_DIR = str(
    Path(__file__).resolve().parent.parent
    / ".github" / "skills" / "x-ipe-tool-task-board-manager" / "scripts"
)
sys.path.insert(0, _SCRIPTS_DIR)

import _board_lib
import task_archive
import task_create
import task_query
import task_update

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_task(task_id: str = "TASK-001", **overrides) -> dict:
    task = {
        "task_id": task_id,
        "task_type": "Feature Refinement",
        "description": "Test task description",
        "role": "TestAgent",
        "status": "in_progress",
        "output_links": [],
        "next_task": "x-ipe-task-based-technical-design",
    }
    task.update(overrides)
    return task


def _setup_daily(tasks_dir: Path, date_str: str, tasks: list[dict]) -> None:
    _board_lib.atomic_write_json(
        tasks_dir / f"tasks-{date_str}.json",
        {"_version": "1.0", "tasks": tasks},
    )


def _setup_index(tasks_dir: Path, entries: dict) -> None:
    _board_lib.atomic_write_json(
        tasks_dir / "tasks-index.json",
        {"_version": "1.0", "version": "1.0", "entries": entries},
    )


def _read_index(tasks_dir: Path) -> dict:
    result = _board_lib.atomic_read_json(tasks_dir / "tasks-index.json")
    assert result["success"], f"Index read failed: {result}"
    return result["data"]


def _read_daily(tasks_dir: Path, date_str: str) -> dict:
    result = _board_lib.atomic_read_json(tasks_dir / f"tasks-{date_str}.json")
    assert result["success"], f"Daily read failed: {result}"
    return result["data"]


def _full_task(task_id: str = "TASK-001", **overrides) -> dict:
    """Build a task with system-managed fields (for seeding test data)."""
    task = _make_task(task_id, **overrides)
    task.setdefault("created_at", "2026-04-03T06:00:00+00:00")
    task.setdefault("last_updated", "2026-04-03T06:00:00+00:00")
    return task


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def task_env(tmp_path, monkeypatch):
    """Isolated task board environment with tasks/ dir pre-created."""
    tasks_dir = tmp_path / "x-ipe-docs" / "planning" / "tasks"
    tasks_dir.mkdir(parents=True)
    monkeypatch.setattr(_board_lib, "_resolve_project_root", lambda: tmp_path)
    return tasks_dir


@pytest.fixture
def seeded_env(task_env):
    """Task env with two tasks pre-seeded (TASK-001 in_progress, TASK-002 completed)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    t1 = _full_task("TASK-001", status="in_progress")
    t2 = _full_task("TASK-002", status="completed", last_updated="2026-04-03T07:00:00+00:00")
    _setup_daily(task_env, today, [t1, t2])
    _setup_index(task_env, {
        "TASK-001": {"file": f"tasks-{today}.json", "status": "in_progress", "last_updated": t1["last_updated"]},
        "TASK-002": {"file": f"tasks-{today}.json", "status": "completed", "last_updated": t2["last_updated"]},
    })
    return task_env


# ---------------------------------------------------------------------------
# TestTaskCreate
# ---------------------------------------------------------------------------

class TestTaskCreate:

    def test_happy_path(self, task_env, capsys):
        """AC-01a/b/e/f/g/h: Create valid task, verify daily file + index."""
        task_create.main(["--task", json.dumps(_make_task())])
        out = json.loads(capsys.readouterr().out)

        assert out["success"] is True
        assert out["data"]["task_id"] == "TASK-001"
        daily_name = out["data"]["file"]

        # Daily file contains task with system timestamps
        daily = _board_lib.atomic_read_json(task_env / daily_name)["data"]
        assert len(daily["tasks"]) == 1
        t = daily["tasks"][0]
        assert t["task_id"] == "TASK-001"
        assert t["created_at"] == t["last_updated"]
        datetime.fromisoformat(t["created_at"])  # valid ISO

        # Index has entry
        idx = _read_index(task_env)
        assert "TASK-001" in idx["entries"]
        assert idx["entries"]["TASK-001"]["file"] == daily_name

    def test_strips_caller_timestamps(self, task_env, capsys):
        """AC-01e: System overrides caller-provided timestamps."""
        task_create.main(["--task", json.dumps(_make_task(created_at="2000-01-01T00:00:00Z",
                                                           last_updated="2000-01-01T00:00:00Z"))])
        out = json.loads(capsys.readouterr().out)
        daily = _board_lib.atomic_read_json(task_env / out["data"]["file"])["data"]
        assert daily["tasks"][0]["created_at"] != "2000-01-01T00:00:00Z"

    def test_rejects_invalid_json(self, task_env, capsys):
        """AC-01b: Invalid JSON exits with code 1."""
        with pytest.raises(SystemExit) as exc:
            task_create.main(["--task", "not-json"])
        assert exc.value.code == 1
        assert "INVALID_JSON" in capsys.readouterr().err

    def test_rejects_unknown_fields(self, task_env, capsys):
        """AC-01c: Unknown fields rejected by strict schema."""
        with pytest.raises(SystemExit) as exc:
            task_create.main(["--task", json.dumps(_make_task(extra="bad"))])
        assert exc.value.code == 1
        assert "SCHEMA_VALIDATION_FAILED" in capsys.readouterr().err

    def test_rejects_duplicate_id(self, task_env, capsys):
        """AC-01d: Duplicate task_id rejected."""
        task_create.main(["--task", json.dumps(_make_task())])
        capsys.readouterr()
        with pytest.raises(SystemExit) as exc:
            task_create.main(["--task", json.dumps(_make_task())])
        assert exc.value.code == 1
        assert "DUPLICATE_TASK_ID" in capsys.readouterr().err

    def test_rejects_missing_required(self, task_env, capsys):
        """AC-01b: Missing required field rejected."""
        with pytest.raises(SystemExit) as exc:
            task_create.main(["--task", json.dumps({"task_id": "T1"})])
        assert exc.value.code == 1
        assert "SCHEMA_VALIDATION_FAILED" in capsys.readouterr().err

    def test_appends_same_day(self, task_env, capsys):
        """AC-01f: Multiple tasks append to same daily file."""
        task_create.main(["--task", json.dumps(_make_task("TASK-001"))])
        r1 = json.loads(capsys.readouterr().out)
        task_create.main(["--task", json.dumps(_make_task("TASK-002"))])
        r2 = json.loads(capsys.readouterr().out)

        assert r1["data"]["file"] == r2["data"]["file"]
        daily = _board_lib.atomic_read_json(task_env / r1["data"]["file"])["data"]
        assert len(daily["tasks"]) == 2

    def test_bootstraps_directory(self, tmp_path, monkeypatch, capsys):
        """AC-06a: Auto-creates tasks/ dir and index if missing."""
        monkeypatch.setattr(_board_lib, "_resolve_project_root", lambda: tmp_path)
        tasks_dir = tmp_path / "x-ipe-docs" / "planning" / "tasks"
        assert not tasks_dir.exists()

        task_create.main(["--task", json.dumps(_make_task())])
        assert json.loads(capsys.readouterr().out)["success"]
        assert tasks_dir.exists()
        assert (tasks_dir / "tasks-index.json").exists()

    def test_rejects_non_dict(self, task_env, capsys):
        """AC-01b: Non-object JSON rejected."""
        with pytest.raises(SystemExit) as exc:
            task_create.main(["--task", '"a string"'])
        assert exc.value.code == 1
        assert "INVALID_TASK" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# TestTaskUpdate
# ---------------------------------------------------------------------------

class TestTaskUpdate:

    def test_partial_merge(self, seeded_env, capsys):
        """AC-02a/b/c/f: Partial merge updates only provided fields."""
        task_update.main(["--task-id", "TASK-001",
                          "--updates", json.dumps({"status": "done"})])
        out = json.loads(capsys.readouterr().out)

        assert out["success"]
        assert "status" in out["data"]["updated_fields"]
        assert "last_updated" in out["data"]["updated_fields"]

        # Verify task in daily file
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        daily = _read_daily(seeded_env, today)
        task = next(t for t in daily["tasks"] if t["task_id"] == "TASK-001")
        assert task["status"] == "completed"  # "done" normalized to "completed"
        assert task["description"] == "Test task description"  # unchanged
        assert task["last_updated"] > "2026-04-03T06:00:00+00:00"

    def test_rejects_immutable_task_id(self, seeded_env, capsys):
        """AC-02d: Cannot change task_id."""
        with pytest.raises(SystemExit) as exc:
            task_update.main(["--task-id", "TASK-001",
                              "--updates", json.dumps({"task_id": "TASK-999"})])
        assert exc.value.code == 1
        assert "IMMUTABLE_FIELD" in capsys.readouterr().err

    def test_rejects_immutable_created_at(self, seeded_env, capsys):
        """AC-02d: Cannot change created_at."""
        with pytest.raises(SystemExit) as exc:
            task_update.main(["--task-id", "TASK-001",
                              "--updates", json.dumps({"created_at": "2099-01-01T00:00:00Z"})])
        assert exc.value.code == 1
        assert "IMMUTABLE_FIELD" in capsys.readouterr().err

    def test_updates_index(self, seeded_env, capsys):
        """AC-02e/06b: Index entry updated on task update."""
        task_update.main(["--task-id", "TASK-001",
                          "--updates", json.dumps({"status": "done"})])
        capsys.readouterr()

        idx = _read_index(seeded_env)
        assert idx["entries"]["TASK-001"]["status"] == "completed"  # "done" normalized
        assert idx["entries"]["TASK-001"]["last_updated"] > "2026-04-03T06:00:00+00:00"

    def test_not_found(self, task_env, capsys):
        """Exit code 2 when task doesn't exist."""
        _setup_index(task_env, {})
        with pytest.raises(SystemExit) as exc:
            task_update.main(["--task-id", "NOPE",
                              "--updates", json.dumps({"status": "done"})])
        assert exc.value.code == 2
        assert "TASK_NOT_FOUND" in capsys.readouterr().err

    def test_rejects_unknown_field(self, seeded_env, capsys):
        """Unknown update field rejected."""
        with pytest.raises(SystemExit) as exc:
            task_update.main(["--task-id", "TASK-001",
                              "--updates", json.dumps({"nonexistent": "val"})])
        assert exc.value.code == 1
        assert "UNKNOWN_FIELD" in capsys.readouterr().err

    def test_rejects_wrong_type(self, seeded_env, capsys):
        """Type mismatch rejected."""
        with pytest.raises(SystemExit) as exc:
            task_update.main(["--task-id", "TASK-001",
                              "--updates", json.dumps({"output_links": "not-a-list"})])
        assert exc.value.code == 1
        assert "TYPE_ERROR" in capsys.readouterr().err

    def test_strips_last_updated(self, seeded_env, capsys):
        """last_updated is auto-set, caller value silently stripped."""
        task_update.main(["--task-id", "TASK-001",
                          "--updates", json.dumps({"status": "done", "last_updated": "ignored"})])
        out = json.loads(capsys.readouterr().out)
        assert out["success"]

    def test_empty_after_strip(self, seeded_env, capsys):
        """Only last_updated in updates → empty after strip → error."""
        with pytest.raises(SystemExit) as exc:
            task_update.main(["--task-id", "TASK-001",
                              "--updates", json.dumps({"last_updated": "ignored"})])
        assert exc.value.code == 1
        assert "EMPTY_UPDATES" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# TestTaskQueryById
# ---------------------------------------------------------------------------

class TestTaskQueryById:

    def test_found(self, seeded_env, capsys):
        """AC-04a/b: Single task returned via index lookup."""
        task_query.main(["--task-id", "TASK-001"])
        out = json.loads(capsys.readouterr().out)
        assert out["success"]
        assert out["data"]["task"]["task_id"] == "TASK-001"
        assert out["data"]["task"]["status"] == "in_progress"

    def test_not_found(self, seeded_env, capsys):
        """AC-04c: Exit code 2 when task not found."""
        with pytest.raises(SystemExit) as exc:
            task_query.main(["--task-id", "NOPE"])
        assert exc.value.code == 2
        assert "TASK_NOT_FOUND" in capsys.readouterr().err

    def test_no_tasks_dir(self, tmp_path, monkeypatch, capsys):
        """Exit code 2 when tasks directory doesn't exist."""
        monkeypatch.setattr(_board_lib, "_resolve_project_root", lambda: tmp_path)
        with pytest.raises(SystemExit) as exc:
            task_query.main(["--task-id", "TASK-001"])
        assert exc.value.code == 2


# ---------------------------------------------------------------------------
# TestTaskQueryList
# ---------------------------------------------------------------------------

class TestTaskQueryList:

    def test_default_range(self, seeded_env, capsys):
        """AC-03a: Default range is 1w, returns today's tasks."""
        task_query.main([])
        out = json.loads(capsys.readouterr().out)
        assert out["success"]
        assert out["data"]["total"] == 2

    def test_status_filter(self, seeded_env, capsys):
        """AC-03b: Filter by status."""
        task_query.main(["--status", "completed"])
        out = json.loads(capsys.readouterr().out)
        assert out["data"]["total"] == 1
        assert out["data"]["tasks"][0]["status"] == "completed"

    def test_search_filter(self, seeded_env, capsys):
        """AC-03c: Text search across task fields."""
        task_query.main(["--search", "TASK-001"])
        out = json.loads(capsys.readouterr().out)
        assert out["data"]["total"] == 1
        assert out["data"]["tasks"][0]["task_id"] == "TASK-001"

    def test_search_case_insensitive(self, seeded_env, capsys):
        """AC-03c: Search is case-insensitive."""
        task_query.main(["--search", "test task"])
        out = json.loads(capsys.readouterr().out)
        assert out["data"]["total"] == 2  # both have "Test task description"

    def test_pagination(self, seeded_env, capsys):
        """AC-03d/e/h: Pagination metadata returned."""
        task_query.main(["--page", "1", "--page-size", "1"])
        out = json.loads(capsys.readouterr().out)
        data = out["data"]
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["page_size"] == 1
        assert data["total_pages"] == 2
        assert len(data["tasks"]) == 1

    def test_sort_order(self, seeded_env, capsys):
        """AC-03f: Sort by last_updated descending."""
        task_query.main([])
        out = json.loads(capsys.readouterr().out)
        tasks = out["data"]["tasks"]
        assert tasks[0]["task_id"] == "TASK-002"  # 07:00 > 06:00
        assert tasks[1]["task_id"] == "TASK-001"

    def test_skips_archived(self, task_env, capsys):
        """AC-03g: Archived files excluded from list query."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        _setup_daily(task_env, today, [_full_task("TASK-001")])
        # Create an archived file with another task
        _board_lib.atomic_write_json(
            task_env / f"tasks-{today}.archived.json",
            {"_version": "1.0", "tasks": [_full_task("TASK-ARCHIVED")]},
        )
        _setup_index(task_env, {
            "TASK-001": {"file": f"tasks-{today}.json", "status": "in_progress",
                         "last_updated": "2026-04-03T06:00:00+00:00"},
        })

        task_query.main(["--range", "all"])
        out = json.loads(capsys.readouterr().out)
        ids = [t["task_id"] for t in out["data"]["tasks"]]
        assert "TASK-001" in ids
        assert "TASK-ARCHIVED" not in ids

    def test_empty_dir(self, task_env, capsys):
        """Empty tasks dir returns empty list."""
        task_query.main(["--range", "all"])
        out = json.loads(capsys.readouterr().out)
        assert out["success"]
        assert out["data"]["total"] == 0

    def test_range_filters_old(self, task_env, capsys):
        """AC-03a: 1w range excludes files older than 7 days."""
        today = datetime.now(timezone.utc).date()
        recent = today.isoformat()
        old = (today - timedelta(days=14)).isoformat()

        _setup_daily(task_env, recent, [_full_task("TASK-RECENT")])
        _setup_daily(task_env, old, [_full_task("TASK-OLD")])
        _setup_index(task_env, {})

        task_query.main(["--range", "1w"])
        out = json.loads(capsys.readouterr().out)
        ids = [t["task_id"] for t in out["data"]["tasks"]]
        assert "TASK-RECENT" in ids
        assert "TASK-OLD" not in ids

    def test_range_all(self, task_env, capsys):
        """AC-03a: 'all' range includes everything."""
        today = datetime.now(timezone.utc).date()
        old = (today - timedelta(days=100)).isoformat()
        _setup_daily(task_env, old, [_full_task("TASK-OLD")])

        task_query.main(["--range", "all"])
        out = json.loads(capsys.readouterr().out)
        assert out["data"]["total"] == 1

    def test_no_tasks_dir_returns_empty(self, tmp_path, monkeypatch, capsys):
        """No tasks dir returns empty paginated result (not error)."""
        monkeypatch.setattr(_board_lib, "_resolve_project_root", lambda: tmp_path)
        task_query.main([])
        out = json.loads(capsys.readouterr().out)
        assert out["success"]
        assert out["data"]["total"] == 0


# ---------------------------------------------------------------------------
# TestTaskArchive
# ---------------------------------------------------------------------------

class TestTaskArchive:

    def test_happy_path(self, task_env, capsys):
        """AC-05a/b/c/d: Archive renames file, removes from index, reports count."""
        date = "2026-04-01"
        _setup_daily(task_env, date, [_full_task("TASK-A"), _full_task("TASK-B")])
        _setup_index(task_env, {
            "TASK-A": {"file": f"tasks-{date}.json", "status": "done", "last_updated": "2026-04-01T00:00:00+00:00"},
            "TASK-B": {"file": f"tasks-{date}.json", "status": "done", "last_updated": "2026-04-01T00:00:00+00:00"},
        })

        task_archive.main(["--date", date])
        out = json.loads(capsys.readouterr().out)

        assert out["success"]
        assert out["data"]["archived_file"] == f"tasks-{date}.archived.json"
        assert out["data"]["tasks_removed"] == 2

        # Original file gone, archived exists
        assert not (task_env / f"tasks-{date}.json").exists()
        assert (task_env / f"tasks-{date}.archived.json").exists()

        # Index entries removed
        idx = _read_index(task_env)
        assert "TASK-A" not in idx["entries"]
        assert "TASK-B" not in idx["entries"]

    def test_missing_file(self, task_env, capsys):
        """Exit code 2 for non-existent daily file."""
        _setup_index(task_env, {})
        with pytest.raises(SystemExit) as exc:
            task_archive.main(["--date", "2026-01-01"])
        assert exc.value.code == 2
        assert "FILE_NOT_FOUND" in capsys.readouterr().err

    def test_already_archived(self, task_env, capsys):
        """Exit code 1 if file already archived."""
        date = "2026-04-01"
        _setup_daily(task_env, date, [_full_task()])
        _board_lib.atomic_write_json(
            task_env / f"tasks-{date}.archived.json", {"_version": "1.0", "tasks": []},
        )
        _setup_index(task_env, {})

        with pytest.raises(SystemExit) as exc:
            task_archive.main(["--date", date])
        assert exc.value.code == 1
        assert "ALREADY_ARCHIVED" in capsys.readouterr().err

    def test_invalid_date_format(self, task_env, capsys):
        """Invalid date format exits with code 1."""
        with pytest.raises(SystemExit) as exc:
            task_archive.main(["--date", "not-a-date"])
        assert exc.value.code == 1
        assert "INVALID_DATE" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# TestIndexManagement
# ---------------------------------------------------------------------------

class TestIndexManagement:

    def test_auto_create_on_first_task(self, tmp_path, monkeypatch, capsys):
        """AC-06a: First create auto-creates tasks dir + index."""
        monkeypatch.setattr(_board_lib, "_resolve_project_root", lambda: tmp_path)
        task_create.main(["--task", json.dumps(_make_task())])
        capsys.readouterr()

        tasks_dir = tmp_path / "x-ipe-docs" / "planning" / "tasks"
        idx = _read_index(tasks_dir)
        assert "version" in idx
        assert "entries" in idx

    def test_entry_structure(self, task_env, capsys):
        """AC-06c: Index entry has file, status, last_updated."""
        task_create.main(["--task", json.dumps(_make_task())])
        capsys.readouterr()

        idx = _read_index(task_env)
        entry = idx["entries"]["TASK-001"]
        assert set(entry.keys()) == {"file", "status", "last_updated"}
        assert entry["file"].startswith("tasks-")
        assert entry["status"] == "in_progress"

    def test_archive_removes_entries(self, task_env, capsys):
        """AC-06d: Archive removes entries from index."""
        date = "2026-03-30"
        _setup_daily(task_env, date, [_full_task()])
        _setup_index(task_env, {
            "TASK-001": {"file": f"tasks-{date}.json", "status": "done", "last_updated": "2026-03-30T00:00:00+00:00"},
        })

        task_archive.main(["--date", date])
        capsys.readouterr()

        idx = _read_index(task_env)
        assert "TASK-001" not in idx["entries"]


# ---------------------------------------------------------------------------
# TestCLI
# ---------------------------------------------------------------------------

class TestCLI:

    def test_json_stdout_success(self, task_env, capsys):
        """AC-07b: Successful output is valid JSON on stdout."""
        task_create.main(["--task", json.dumps(_make_task())])
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["success"] is True
        assert captured.err == ""

    def test_json_stderr_error(self, task_env, capsys):
        """AC-07c: Error output is valid JSON on stderr."""
        with pytest.raises(SystemExit):
            task_create.main(["--task", "bad"])
        captured = capsys.readouterr()
        err = json.loads(captured.err)
        assert err["success"] is False
        assert "error" in err
        assert "message" in err

    def test_exit_code_0(self, task_env, capsys):
        """AC-07d: Exit code 0 on success (no SystemExit raised)."""
        task_create.main(["--task", json.dumps(_make_task())])
        capsys.readouterr()
        # If we get here, no SystemExit was raised → exit code 0

    def test_exit_code_1_validation(self, task_env, capsys):
        """AC-07d: Exit code 1 on validation error."""
        with pytest.raises(SystemExit) as exc:
            task_create.main(["--task", "null"])
        assert exc.value.code == 1

    def test_exit_code_2_not_found(self, task_env, capsys):
        """AC-07d: Exit code 2 on not found."""
        _setup_index(task_env, {})
        with pytest.raises(SystemExit) as exc:
            task_update.main(["--task-id", "NOPE", "--updates", '{"status": "done"}'])
        assert exc.value.code == 2

    def test_lock_timeout_arg(self, task_env, capsys):
        """AC-07e: --lock-timeout accepted by create/update/archive."""
        task_create.main(["--task", json.dumps(_make_task()), "--lock-timeout", "5"])
        out = json.loads(capsys.readouterr().out)
        assert out["success"]

    def test_main_callable_with_argv(self, task_env, capsys):
        """AC-07a: main(argv) signature works for all scripts."""
        task_create.main(["--task", json.dumps(_make_task("T1"))])
        capsys.readouterr()

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        task_query.main(["--task-id", "T1"])
        out = json.loads(capsys.readouterr().out)
        assert out["data"]["task"]["task_id"] == "T1"


# ---------------------------------------------------------------------------
# TestAtomicity
# ---------------------------------------------------------------------------

class TestAtomicity:

    def test_create_uses_both_locks(self, task_env, capsys):
        """AC-08a/b: Create acquires daily lock then index lock (ordered)."""
        lock_calls = []
        original_lock = _board_lib.with_file_lock

        @contextmanager
        def tracking_lock(lock_path, **kwargs):
            lock_calls.append(Path(lock_path).name)
            with original_lock(lock_path, **kwargs):
                yield

        with patch.object(task_create, "with_file_lock", tracking_lock):
            task_create.main(["--task", json.dumps(_make_task())])
        capsys.readouterr()

        assert len(lock_calls) == 2
        assert lock_calls[0].startswith("tasks-") and lock_calls[0].endswith(".json.lock")
        assert lock_calls[1] == "tasks-index.json.lock"

    def test_update_uses_both_locks(self, seeded_env, capsys):
        """AC-08a/b: Update acquires daily lock then index lock."""
        lock_calls = []
        original_lock = _board_lib.with_file_lock

        @contextmanager
        def tracking_lock(lock_path, **kwargs):
            lock_calls.append(Path(lock_path).name)
            with original_lock(lock_path, **kwargs):
                yield

        with patch.object(task_update, "with_file_lock", tracking_lock):
            task_update.main(["--task-id", "TASK-001",
                              "--updates", json.dumps({"status": "done"})])
        capsys.readouterr()

        assert len(lock_calls) == 2
        assert lock_calls[1] == "tasks-index.json.lock"

    def test_query_no_locks(self, seeded_env, capsys):
        """AC-08c: Query operations don't acquire locks (module doesn't import with_file_lock)."""
        assert not hasattr(task_query, "with_file_lock"), \
            "task_query should not import with_file_lock — queries are read-only"
        task_query.main(["--task-id", "TASK-001"])
        capsys.readouterr()

    def test_archive_uses_both_locks(self, task_env, capsys):
        """AC-08a/b: Archive acquires daily lock then index lock."""
        date = "2026-04-01"
        _setup_daily(task_env, date, [_full_task()])
        _setup_index(task_env, {
            "TASK-001": {"file": f"tasks-{date}.json", "status": "done", "last_updated": "2026-04-01T00:00:00+00:00"},
        })

        lock_calls = []
        original_lock = _board_lib.with_file_lock

        @contextmanager
        def tracking_lock(lock_path, **kwargs):
            lock_calls.append(Path(lock_path).name)
            with original_lock(lock_path, **kwargs):
                yield

        with patch.object(task_archive, "with_file_lock", tracking_lock):
            task_archive.main(["--date", date])
        capsys.readouterr()

        assert len(lock_calls) == 2
        assert lock_calls[0] == f"tasks-{date}.json.lock"
        assert lock_calls[1] == "tasks-index.json.lock"


# ---------------------------------------------------------------------------
# TestStatusNormalization — "done" and "completed" merge to "completed"
# ---------------------------------------------------------------------------

class TestStatusNormalization:
    """Verify that similar task statuses are normalized to canonical forms."""

    def test_create_normalizes_done_to_completed(self, task_env, capsys):
        """Creating a task with status 'done' stores it as 'completed'."""
        task_create.main(["--task", json.dumps(_make_task(status="done"))])
        out = json.loads(capsys.readouterr().out)
        daily = _board_lib.atomic_read_json(task_env / out["data"]["file"])["data"]
        assert daily["tasks"][0]["status"] == "completed"

    def test_create_normalizes_complete_to_completed(self, task_env, capsys):
        """Creating a task with status 'complete' stores it as 'completed'."""
        task_create.main(["--task", json.dumps(_make_task(status="complete"))])
        out = json.loads(capsys.readouterr().out)
        daily = _board_lib.atomic_read_json(task_env / out["data"]["file"])["data"]
        assert daily["tasks"][0]["status"] == "completed"

    def test_update_normalizes_done_to_completed(self, seeded_env, capsys):
        """Updating a task status to 'done' stores it as 'completed'."""
        task_update.main(["--task-id", "TASK-001",
                          "--updates", json.dumps({"status": "done"})])
        capsys.readouterr()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        daily = _read_daily(seeded_env, today)
        task = next(t for t in daily["tasks"] if t["task_id"] == "TASK-001")
        assert task["status"] == "completed"

    def test_update_index_normalizes_done(self, seeded_env, capsys):
        """Index entry reflects normalized status after update."""
        task_update.main(["--task-id", "TASK-001",
                          "--updates", json.dumps({"status": "done"})])
        capsys.readouterr()
        idx = _read_index(seeded_env)
        assert idx["entries"]["TASK-001"]["status"] == "completed"

    def test_query_done_finds_completed(self, task_env, capsys):
        """Querying --status done finds tasks with normalized 'completed' status."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        t1 = _full_task("TASK-001", status="completed")
        _setup_daily(task_env, today, [t1])
        _setup_index(task_env, {
            "TASK-001": {"file": f"tasks-{today}.json", "status": "completed",
                         "last_updated": t1["last_updated"]},
        })
        task_query.main(["--status", "done"])
        out = json.loads(capsys.readouterr().out)
        assert out["data"]["total"] == 1
        assert out["data"]["tasks"][0]["status"] == "completed"

    def test_completed_stays_completed(self, task_env, capsys):
        """Status 'completed' is already canonical and stays unchanged."""
        task_create.main(["--task", json.dumps(_make_task(status="completed"))])
        out = json.loads(capsys.readouterr().out)
        daily = _board_lib.atomic_read_json(task_env / out["data"]["file"])["data"]
        assert daily["tasks"][0]["status"] == "completed"

    def test_in_progress_unchanged(self, task_env, capsys):
        """Non-alias statuses like 'in_progress' are not changed."""
        task_create.main(["--task", json.dumps(_make_task(status="in_progress"))])
        out = json.loads(capsys.readouterr().out)
        daily = _board_lib.atomic_read_json(task_env / out["data"]["file"])["data"]
        assert daily["tasks"][0]["status"] == "in_progress"

    def test_normalize_function_in_board_lib(self):
        """_board_lib exposes normalize_task_status function."""
        assert _board_lib.normalize_task_status("done") == "completed"
        assert _board_lib.normalize_task_status("complete") == "completed"
        assert _board_lib.normalize_task_status("completed") == "completed"
        assert _board_lib.normalize_task_status("in_progress") == "in_progress"
        assert _board_lib.normalize_task_status("pending") == "pending"
