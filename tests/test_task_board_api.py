"""Tests for FEATURE-055-C — Task Board API (routes + service).

Coverage targets: task_board_service.py and task_board_routes.py
AC mapping: 29 ACs across 7 groups
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from x_ipe.services.task_board_service import TaskBoardService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_task(task_id: str, **overrides) -> dict:
    """Create a minimal task dict."""
    base = {
        "task_id": task_id,
        "task_type": "Feature Refinement",
        "description": f"Description for {task_id}",
        "role": "Drift",
        "status": "done",
        "created_at": "2026-04-03T10:00:00Z",
        "last_updated": "2026-04-03T12:00:00Z",
        "output_links": [],
        "next_task": "x-ipe-task-based-technical-design",
    }
    base.update(overrides)
    return base


def _today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _write_daily(tasks_dir: Path, date_str: str, tasks: list[dict]) -> None:
    fp = tasks_dir / f"tasks-{date_str}.json"
    fp.write_text(json.dumps(tasks, indent=2))


def _write_index(tasks_dir: Path, entries: dict) -> None:
    fp = tasks_dir / "tasks-index.json"
    fp.write_text(json.dumps({"_version": "1.0", "entries": entries}, indent=2))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tasks_dir(tmp_path):
    """Create tasks directory and return its path."""
    d = tmp_path / "x-ipe-docs" / "planning" / "tasks"
    d.mkdir(parents=True)
    return d


@pytest.fixture()
def service(tmp_path, tasks_dir):
    """Return a TaskBoardService pointed at tmp_path."""
    return TaskBoardService(str(tmp_path))


@pytest.fixture()
def seeded(tasks_dir, service):
    """Seed 3 tasks across 2 daily files + index."""
    today = _today_str()
    t1 = _make_task("TASK-100", status="done", last_updated="2026-04-03T12:00:00Z")
    t2 = _make_task("TASK-101", status="in_progress", last_updated="2026-04-03T14:00:00Z",
                     task_type="Code Implementation", description="Implement API", role="Spark")
    t3 = _make_task("TASK-102", status="done", last_updated="2026-04-03T10:00:00Z")
    _write_daily(tasks_dir, today, [t1, t2])
    _write_daily(tasks_dir, "2026-04-02", [t3])
    _write_index(tasks_dir, {
        "TASK-100": {"file": f"tasks-{today}.json", "status": "done", "last_updated": t1["last_updated"]},
        "TASK-101": {"file": f"tasks-{today}.json", "status": "in_progress", "last_updated": t2["last_updated"]},
        "TASK-102": {"file": "tasks-2026-04-02.json", "status": "done", "last_updated": t3["last_updated"]},
    })
    return service


# ---------------------------------------------------------------------------
# Flask test client
# ---------------------------------------------------------------------------


@pytest.fixture()
def app(tmp_path, tasks_dir):
    """Create a minimal Flask app with task board blueprint registered."""
    from flask import Flask
    from x_ipe.routes.task_board_routes import task_board_bp

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["PROJECT_ROOT"] = str(tmp_path)
    app.register_blueprint(task_board_bp)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def seeded_client(app, tasks_dir):
    """Client with seeded task data."""
    today = _today_str()
    t1 = _make_task("TASK-100", status="done", last_updated="2026-04-03T12:00:00Z")
    t2 = _make_task("TASK-101", status="in_progress", last_updated="2026-04-03T14:00:00Z",
                     task_type="Code Implementation", description="Implement API", role="Spark")
    t3 = _make_task("TASK-102", status="done", last_updated="2026-04-03T10:00:00Z")
    _write_daily(tasks_dir, today, [t1, t2])
    _write_daily(tasks_dir, "2026-04-02", [t3])
    _write_index(tasks_dir, {
        "TASK-100": {"file": f"tasks-{today}.json", "status": "done", "last_updated": t1["last_updated"]},
        "TASK-101": {"file": f"tasks-{today}.json", "status": "in_progress", "last_updated": t2["last_updated"]},
        "TASK-102": {"file": "tasks-2026-04-02.json", "status": "done", "last_updated": t3["last_updated"]},
    })
    return app.test_client()


# ===================================================================
# SERVICE TESTS
# ===================================================================


class TestServiceListBasic:
    """AC-055C-01: List endpoint basic behavior."""

    def test_default_returns_success(self, seeded):  # AC-01a
        result = seeded.list_tasks()
        assert result["success"] is True
        assert "tasks" in result["data"]
        assert "pagination" in result["data"]

    def test_default_pagination(self, seeded):  # AC-01b
        p = seeded.list_tasks()["data"]["pagination"]
        assert p["page"] == 1
        assert p["page_size"] == 50

    def test_sorted_by_last_updated_desc(self, seeded):  # AC-01c
        tasks = seeded.list_tasks()["data"]["tasks"]
        timestamps = [t["last_updated"] for t in tasks]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_tasks_have_all_fields(self, seeded):  # AC-01d
        tasks = seeded.list_tasks()["data"]["tasks"]
        required = {"task_id", "task_type", "description", "role", "status",
                     "created_at", "last_updated", "output_links", "next_task"}
        for t in tasks:
            assert required.issubset(t.keys()), f"Missing fields in {t['task_id']}"


class TestServiceListFiltering:
    """AC-055C-02: List filtering."""

    def test_range_1w(self, seeded):  # AC-02a
        result = seeded.list_tasks(range_str="1w")
        assert result["success"] is True

    def test_range_1m(self, seeded):  # AC-02b
        result = seeded.list_tasks(range_str="1m")
        assert result["success"] is True

    def test_range_all(self, seeded):  # AC-02c
        result = seeded.list_tasks(range_str="all")
        assert len(result["data"]["tasks"]) >= 3

    def test_status_filter(self, seeded):  # AC-02d
        tasks = seeded.list_tasks(status="in_progress")["data"]["tasks"]
        assert all(t["status"] == "in_progress" for t in tasks)
        assert len(tasks) == 1

    def test_search_filter(self, seeded):  # AC-02e
        tasks = seeded.list_tasks(search="spark")["data"]["tasks"]
        assert len(tasks) == 1
        assert tasks[0]["task_id"] == "TASK-101"

    def test_combined_filters(self, seeded):  # AC-02f
        tasks = seeded.list_tasks(status="in_progress", search="implement")["data"]["tasks"]
        assert len(tasks) == 1
        assert tasks[0]["task_id"] == "TASK-101"

    def test_old_file_excluded_by_1w(self, tasks_dir, service):
        """Files older than 7 days excluded by range=1w."""
        old_date = (datetime.now(timezone.utc) - timedelta(days=10)).strftime("%Y-%m-%d")
        _write_daily(tasks_dir, old_date, [_make_task("TASK-OLD")])
        result = service.list_tasks(range_str="1w")
        ids = [t["task_id"] for t in result["data"]["tasks"]]
        assert "TASK-OLD" not in ids

    def test_search_case_insensitive(self, seeded):
        tasks = seeded.list_tasks(search="IMPLEMENT")["data"]["tasks"]
        assert len(tasks) == 1


class TestServiceListPagination:
    """AC-055C-03: Pagination."""

    def test_pagination_metadata(self, tasks_dir, service):  # AC-03a
        today = _today_str()
        tasks = [_make_task(f"TASK-{i}") for i in range(60)]
        _write_daily(tasks_dir, today, tasks)
        result = service.list_tasks(page=1, page_size=50)
        p = result["data"]["pagination"]
        assert p["total"] == 60
        assert p["page"] == 1
        assert p["page_size"] == 50
        assert p["total_pages"] == 2
        assert len(result["data"]["tasks"]) == 50

    def test_page_2(self, tasks_dir, service):  # AC-03b
        today = _today_str()
        tasks = [_make_task(f"TASK-{i}") for i in range(60)]
        _write_daily(tasks_dir, today, tasks)
        result = service.list_tasks(page=2, page_size=50)
        assert len(result["data"]["tasks"]) == 10
        assert result["data"]["pagination"]["page"] == 2

    def test_single_page(self, seeded):  # AC-03c
        p = seeded.list_tasks()["data"]["pagination"]
        assert p["total_pages"] == 1

    def test_page_beyond_range(self, seeded):  # AC-03d
        result = seeded.list_tasks(page=999)
        assert result["data"]["tasks"] == []
        assert result["data"]["pagination"]["total"] >= 1


class TestServiceGetTask:
    """AC-055C-04: Get by ID."""

    def test_found_via_index(self, seeded):  # AC-04a
        result = seeded.get_task("TASK-100")
        assert result["success"] is True
        assert result["data"]["task_id"] == "TASK-100"

    def test_not_found(self, seeded):  # AC-04b
        result = seeded.get_task("TASK-999")
        assert result["success"] is False
        assert result["error"] == "NOT_FOUND"

    def test_all_fields_returned(self, seeded):  # AC-04c
        data = seeded.get_task("TASK-100")["data"]
        required = {"task_id", "task_type", "description", "role", "status",
                     "created_at", "last_updated", "output_links", "next_task"}
        assert required.issubset(data.keys())

    def test_fallback_scan_without_index(self, tasks_dir, service):
        """Get by ID works even without index (fallback scan)."""
        today = _today_str()
        _write_daily(tasks_dir, today, [_make_task("TASK-NOINDEX")])
        result = service.get_task("TASK-NOINDEX")
        assert result["success"] is True


class TestServiceEdgeCases:
    """AC-055C-07: Service layer edge cases."""

    def test_no_tasks_dir(self, tmp_path):  # AC-07e
        svc = TaskBoardService(str(tmp_path / "nonexistent"))
        result = svc.list_tasks()
        assert result["success"] is True
        assert result["data"]["tasks"] == []
        assert result["data"]["pagination"]["total"] == 0
        assert result["data"]["pagination"]["total_pages"] == 1

    def test_skips_archived(self, tasks_dir, service):  # AC-07d
        today = _today_str()
        _write_daily(tasks_dir, today, [_make_task("TASK-LIVE")])
        archived = tasks_dir / f"tasks-{today}.archived.json"
        archived.write_text(json.dumps([_make_task("TASK-ARCHIVED")]))
        tasks = service.list_tasks()["data"]["tasks"]
        ids = [t["task_id"] for t in tasks]
        assert "TASK-LIVE" in ids
        assert "TASK-ARCHIVED" not in ids

    def test_malformed_file_skipped(self, tasks_dir, service):
        today = _today_str()
        (tasks_dir / f"tasks-{today}.json").write_text("NOT JSON{{{")
        result = service.list_tasks()
        assert result["success"] is True
        assert result["data"]["tasks"] == []


# ===================================================================
# ROUTE TESTS
# ===================================================================


class TestListRoute:
    """AC-055C-01/02/03/05/06: Route-level tests."""

    def test_list_empty_200(self, client):  # AC-01a
        resp = client.get("/api/tasks/list")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert "tasks" in body["data"]

    def test_list_with_data(self, seeded_client):
        resp = seeded_client.get("/api/tasks/list")
        assert resp.status_code == 200
        assert len(resp.get_json()["data"]["tasks"]) >= 1

    def test_list_with_filters(self, seeded_client):  # AC-02d, 02e
        resp = seeded_client.get("/api/tasks/list?status=in_progress&search=spark")
        body = resp.get_json()
        assert body["success"] is True
        assert len(body["data"]["tasks"]) == 1

    def test_invalid_range_400(self, client):  # AC-05a
        resp = client.get("/api/tasks/list?range=invalid")
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["success"] is False
        assert body["error"] == "VALIDATION_ERROR"

    def test_invalid_page_400(self, client):  # AC-05b
        resp = client.get("/api/tasks/list?page=abc")
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "VALIDATION_ERROR"

    def test_page_size_zero_400(self, client):  # AC-05c
        resp = client.get("/api/tasks/list?page_size=0")
        assert resp.status_code == 400

    def test_cache_control_header(self, client):  # AC-06c
        resp = client.get("/api/tasks/list")
        assert resp.headers.get("Cache-Control") == "no-store"


class TestGetRoute:
    """AC-055C-04: Get route tests."""

    def test_get_found(self, seeded_client):  # AC-04a
        resp = seeded_client.get("/api/tasks/get/TASK-100")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert body["data"]["task_id"] == "TASK-100"

    def test_get_not_found_404(self, seeded_client):  # AC-04b
        resp = seeded_client.get("/api/tasks/get/TASK-999")
        assert resp.status_code == 404
        body = resp.get_json()
        assert body["success"] is False
        assert body["error"] == "NOT_FOUND"

    def test_get_cache_control(self, seeded_client):  # AC-06c
        resp = seeded_client.get("/api/tasks/get/TASK-100")
        assert resp.headers.get("Cache-Control") == "no-store"


class TestErrorHandling:
    """AC-055C-05d: Unhandled exception returns 500."""

    def test_internal_error_500(self, app):
        from unittest.mock import patch
        with app.test_client() as c:
            with patch.object(TaskBoardService, "list_tasks", side_effect=RuntimeError("boom")):
                resp = c.get("/api/tasks/list")
                assert resp.status_code == 500
                body = resp.get_json()
                assert body["success"] is False
                assert body["error"] == "INTERNAL_ERROR"


class TestBlueprintRegistration:
    """AC-055C-06: Blueprint integration."""

    def test_routes_registered(self, app):  # AC-06a
        rules = [r.rule for r in app.url_map.iter_rules()]
        assert "/api/tasks/list" in rules
        assert "/api/tasks/get/<task_id>" in rules

    def test_service_uses_direct_import(self):  # AC-06b
        import inspect
        src = inspect.getsource(TaskBoardService)
        assert "subprocess" not in src
