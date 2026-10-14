"""TASK-6749 candidate registration, ownership, concurrency and consumer checks."""
from __future__ import annotations

import ast
import json
import os
import re
import selectors
import shlex
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

META = Path(__file__).resolve().parents[1]
SCRIPTS = META / "candidate" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import _board_lib as lib
import _task_store as store
import migrate
import task_archive
import task_create
import task_ensure
import task_query
import task_update


def task(tid="TASK-001", **overrides):
    data = {"task_type": "Skill Update", "description": "Review board contracts",
            "role": "Drift", "status": "in_progress", "output_links": [], "next_task": ""}
    if tid is not None:
        data["task_id"] = tid
    data.update(overrides)
    return data


@pytest.fixture
def env(tmp_path, monkeypatch):
    (tmp_path / "x-ipe-docs").mkdir()
    monkeypatch.setattr(lib, "_resolve_project_root", lambda: tmp_path)
    assert Path(task_create.__file__).parent == SCRIPTS
    return tmp_path


def directory(root):
    return root / "x-ipe-docs" / "planning" / "tasks"


def invoke(module, capsys, payload=None, args=None):
    module.main(args if args is not None else ["--task", json.dumps(payload)])
    captured = capsys.readouterr()
    assert not captured.err
    return json.loads(captured.out)["data"]


def snapshot(root):
    return {p.name: p.read_bytes() for p in directory(root).glob("*.json")}


def seed(root, tid, filename="tasks-2026-01-01.json", indexed=True, as_list=False, **overrides):
    full = task(tid, created_at="2026-01-01T00:00:00+00:00",
                last_updated="2026-01-01T00:00:00+00:00", **overrides)
    lib.atomic_write_json(directory(root) / filename,
                          [full] if as_list else {"_version": "1.0", "tasks": [full]})
    if indexed:
        idx = store.read_index(directory(root))
        idx["entries"][tid] = {"file": filename, "status": full["status"],
                               "last_updated": full["last_updated"]}
        lib.atomic_write_json(directory(root) / "tasks-index.json", idx)
    return full


def reject(module, capsys, payload=None, args=None, error=None):
    with pytest.raises(SystemExit) as exc:
        module.main(args if args is not None else ["--task", json.dumps(payload)])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert not captured.out
    if error:
        assert json.loads(captured.err)["error"] == error


def test_auto_bootstrap_and_explicit_compatibility(env, capsys):
    first = invoke(task_create, capsys, task(None))
    assert first["task_id"] == "TASK-001"
    assert invoke(task_create, capsys, task("T1"))["task_id"] == "T1"
    assert invoke(task_create, capsys, task("TASK-8000"))["task_id"] == "TASK-8000"
    assert invoke(task_create, capsys, task(None))["task_id"] == "TASK-8001"
    before = snapshot(env)
    reject(task_create, capsys, task("T1"), error="DUPLICATE_TASK_ID")
    assert snapshot(env) == before


@pytest.mark.parametrize("filename,indexed", [
    ("tasks-2026-01-01.json", True),
    ("tasks-2026-01-01.json", False),
    ("tasks-2026-01-01.archived.json", False),
])
def test_reserves_all_dates_archives_and_orphans(env, capsys, filename, indexed):
    seed(env, "TASK-009000", filename, indexed=indexed)
    assert invoke(task_create, capsys, task(None))["task_id"] == "TASK-9001"
    reject(task_create, capsys, task("TASK-009000"), error="DUPLICATE_TASK_ID")


def test_dangling_index_reserves_numeric_id(env, capsys):
    lib.atomic_write_json(directory(env) / "tasks-index.json",
                          {"version": "1.0", "entries": {"TASK-9999": {"file": "missing"}}})
    assert invoke(task_create, capsys, task(None))["task_id"] == "TASK-10000"
    reject(task_ensure, capsys, task("TASK-9999"), error="INCONSISTENT_BOARD")


def test_ensure_creates_supplied_then_reuses_without_writes(env, capsys):
    result = invoke(task_ensure, capsys, task("TASK-6749"))
    assert result["created"] is True
    before = snapshot(env)
    repeat = invoke(task_ensure, capsys, task("TASK-6749"))
    assert repeat["created"] is False and repeat["task"] == result["task"]
    assert snapshot(env) == before


def test_resume_old_completed_preserves_outputs_routing_timestamps(env, capsys):
    existing = seed(env, "TASK-6749", status="completed", output_links=["evidence.md"], next_task="other")
    before = snapshot(env)
    result = invoke(task_ensure, capsys, task("TASK-6749"))
    assert result["created"] is False and result["task"] == existing
    assert result["file"] == "tasks-2026-01-01.json"
    assert snapshot(env) == before


@pytest.mark.parametrize("field,value,error", [
    ("role", "Nova", "OWNERSHIP_CONFLICT"),
    ("role", "", "OWNERSHIP_CONFLICT"),
    ("role", "drift", "OWNERSHIP_CONFLICT"),
    ("task_type", "Bug Fix", "CONTEXT_CONFLICT"),
    ("description", "Different task", "CONTEXT_CONFLICT"),
])
def test_ensure_rejects_existing_ownership_context(env, capsys, field, value, error):
    seed(env, "TASK-6749", **{field: value})
    before = snapshot(env)
    reject(task_ensure, capsys, task("TASK-6749"), error=error)
    assert snapshot(env) == before


def test_ensure_missing_id_rejected_without_board_creation(env, capsys):
    reject(task_ensure, capsys, task(None), error="SCHEMA_VALIDATION_FAILED")
    assert not directory(env).exists()


def test_ensure_blank_caller_cannot_claim_unassigned(env, capsys):
    seed(env, "TASK-001", role="")
    before = snapshot(env)
    reject(task_ensure, capsys, task(role=""), error="OWNERSHIP_REQUIRED")
    assert snapshot(env) == before


@pytest.mark.parametrize("payload,error", [
    ("null", "INVALID_TASK"), ("[]", "INVALID_TASK"), ("{", "INVALID_JSON"),
    (json.dumps(task(assignee="Drift")), "SCHEMA_VALIDATION_FAILED"),
    (json.dumps(task(status=[])), "SCHEMA_VALIDATION_FAILED"),
    (json.dumps(task(status="unknown")), "INVALID_STATUS"),
    (json.dumps(task(tid="")), "INVALID_TASK_ID"),
])
def test_ensure_rejects_invalid_input(env, capsys, payload, error):
    reject(task_ensure, capsys, args=["--task", payload], error=error)
    assert not directory(env).exists()


@pytest.mark.parametrize("status", sorted(lib.VALID_TASK_STATUSES | {"done", "complete"}))
def test_create_update_canonical_statuses(env, capsys, status):
    result = invoke(task_create, capsys, task(status=status))
    actual = invoke(task_query, capsys, args=["--task-id", result["task_id"]])["task"]
    assert actual["status"] == lib.normalize_task_status(status)
    invoke(task_update, capsys, args=["--task-id", result["task_id"], "--updates", json.dumps({"status": status})])
    actual = invoke(task_query, capsys, args=["--task-id", result["task_id"]])["task"]
    assert actual["status"] == lib.normalize_task_status(status)


@pytest.mark.parametrize("status,error", [("Unknown", "INVALID_STATUS"), ([], "TYPE_ERROR")])
def test_update_status_fails_without_mutation(env, capsys, status, error):
    invoke(task_create, capsys, task())
    before = snapshot(env)
    reject(task_update, capsys, args=["--task-id", "TASK-001", "--updates", json.dumps({"status": status})], error=error)
    assert snapshot(env) == before


@pytest.mark.parametrize("arg", ["--page", "--page-size"])
@pytest.mark.parametrize("value", ["0", "-1"])
def test_query_positive_pagination(env, capsys, arg, value):
    reject(task_query, capsys, args=[arg, value], error="INVALID_PAGINATION")
    assert not directory(env).exists()


def test_all_date_complete_pagination_exact_role_and_readonly(env, capsys):
    seed(env, "TASK-OLD")
    today = task_create._today_filename()
    recent = [task(f"TASK-{i+100}", role="Nova", description="Mentions Drift",
                   created_at="2026-10-13", last_updated="2026-10-13") for i in range(51)]
    lib.atomic_write_json(directory(env) / today, {"tasks": recent})
    before = snapshot(env)
    assert invoke(task_query, capsys, args=["--status", "in_progress"])["total"] == 51
    first = invoke(task_query, capsys, args=["--range", "all", "--status", "in_progress", "--page-size", "50"])
    assert first["total_pages"] == 2 and first["total"] == 52
    second = invoke(task_query, capsys, args=["--range", "all", "--status", "in_progress", "--page-size", "50", "--page", "2"])
    exact = [t["task_id"] for t in first["tasks"] + second["tasks"] if t["role"] == "Drift"]
    assert exact == ["TASK-OLD"]
    assert snapshot(env) == before


@pytest.mark.parametrize("filename,content", [
    ("tasks-index.json", "not JSON"),
    ("tasks-index.json", '{"entries":[]}'),
    ("tasks-2026-01-01.json", "not JSON"),
    ("tasks-2026-01-01.archived.json", '{"tasks":[42]}'),
])
def test_corrupt_state_never_reset(env, capsys, filename, content):
    directory(env).mkdir(parents=True)
    (directory(env) / filename).write_text(content)
    before = snapshot(env)
    for module in (task_create, task_ensure):
        reject(module, capsys, task(None if module is task_create else "TASK-001"))
        assert snapshot(env) == before


def test_archived_and_multiple_records_not_resumed(env, capsys):
    seed(env, "TASK-001", "tasks-2026-01-01.archived.json", indexed=False)
    reject(task_ensure, capsys, task(), error="TASK_ARCHIVED")
    seed(env, "TASK-002", "tasks-2026-01-02.json")
    seed(env, "TASK-002", "tasks-2026-01-03.json")
    reject(task_ensure, capsys, task("TASK-002"), error="INCONSISTENT_BOARD")


def test_index_failure_reserves_orphan_and_blocks_resume(env, capsys, monkeypatch):
    original = store.atomic_write_json
    def fail_index(path, data):
        if Path(path).name == "tasks-index.json":
            raise OSError("injected index commit failure")
        original(path, data)
    monkeypatch.setattr(store, "atomic_write_json", fail_index)
    with pytest.raises(OSError, match="injected"):
        task_create.main(["--task", json.dumps(task())])
    monkeypatch.setattr(store, "atomic_write_json", original)
    before = snapshot(env)
    reject(task_ensure, capsys, task(), error="INCONSISTENT_BOARD")
    assert snapshot(env) == before
    assert invoke(task_create, capsys, task(None))["task_id"] == "TASK-002"


def test_historical_list_daily_string_index_and_api_get(env, capsys):
    from x_ipe.services.task_board_service import TaskBoardService
    full = seed(env, "TASK-001", as_list=True)
    idx = store.read_index(directory(env))
    idx["entries"]["TASK-001"] = "tasks-2026-01-01.json"
    lib.atomic_write_json(directory(env) / "tasks-index.json", idx)
    assert invoke(task_ensure, capsys, task())["task"] == full
    assert invoke(task_query, capsys, args=["--task-id", "TASK-001"])["task"] == full
    assert invoke(task_query, capsys, args=["--range", "all"])["tasks"] == [full]
    invoke(task_update, capsys, args=["--task-id", "TASK-001", "--updates", '{"status":"done"}'])
    saved = json.loads((directory(env) / "tasks-2026-01-01.json").read_text())
    assert isinstance(saved, list) and saved[0]["status"] == "completed"
    assert TaskBoardService(str(env)).get_task("TASK-001")["data"] == saved[0]
    invoke(task_archive, capsys, args=["--date", "2026-01-01"])
    assert json.loads((directory(env) / "tasks-2026-01-01.archived.json").read_text()) == saved


def test_create_preserves_historical_list_daily(env, capsys, monkeypatch):
    seed(env, "TASK-001", as_list=True)
    monkeypatch.setattr(task_create, "_today_filename", lambda: "tasks-2026-01-01.json")
    invoke(task_create, capsys, task(None))
    saved = json.loads((directory(env) / "tasks-2026-01-01.json").read_text())
    assert isinstance(saved, list) and len(saved) == 2
    assert invoke(task_query, capsys, args=["--task-id", "TASK-002"])["task"] == saved[1]


def test_ownership_query_does_not_hide_corrupt_daily(env, capsys):
    directory(env).mkdir(parents=True)
    (directory(env) / "tasks-2026-01-01.json").write_text("broken")
    before = snapshot(env)
    reject(task_query, capsys, args=["--range", "all", "--status", "in_progress"], error="BOARD_READ_ERROR")
    assert snapshot(env) == before


def test_update_bad_index_after_daily_lock_preserves_daily(env, capsys, monkeypatch):
    invoke(task_create, capsys, task())
    before = snapshot(env)
    original = task_update.with_file_lock
    @contextmanager
    def changed(path, **kwargs):
        if Path(path).name == "tasks-index.json.lock":
            lib.atomic_write_json(directory(env) / "tasks-index.json", {"entries": {}})
        with original(path, **kwargs):
            yield
    monkeypatch.setattr(task_update, "with_file_lock", changed)
    reject(task_update, capsys, args=["--task-id", "TASK-001", "--updates", '{"status":"done"}'], error="INCONSISTENT_BOARD")
    assert (directory(env) / task_create._today_filename()).read_bytes() == before[task_create._today_filename()]


def test_archive_corrupt_index_does_not_rename(env, capsys):
    seed(env, "TASK-001")
    (directory(env) / "tasks-index.json").write_text("broken")
    before = snapshot(env)
    reject(task_archive, capsys, args=["--date", "2026-01-01"], error="BOARD_READ_ERROR")
    assert snapshot(env) == before


def test_archive_rechecks_collision_inside_daily_lock(env, capsys, monkeypatch):
    seed(env, "TASK-001")
    original = task_archive.with_file_lock
    archived = directory(env) / "tasks-2026-01-01.archived.json"
    @contextmanager
    def collision(path, **kwargs):
        with original(path, **kwargs):
            if Path(path).name == "tasks-2026-01-01.json.lock":
                lib.atomic_write_json(archived, {"tasks": [task("KEEP")]})
            yield
    monkeypatch.setattr(task_archive, "with_file_lock", collision)
    reject(task_archive, capsys, args=["--date", "2026-01-01"], error="ALREADY_ARCHIVED")
    assert json.loads(archived.read_text())["tasks"][0]["task_id"] == "KEEP"
    assert (directory(env) / "tasks-2026-01-01.json").exists()


def test_migration_cross_date_duplicates_and_timestamps(env, capsys):
    seed(env, "TASK-001", "tasks-2026-01-01.archived.json", indexed=False)
    full = task("TASK-001", created_at="2020-01-01", last_updated="2026-02-01")
    assert migrate.write_tasks_json([full])["skipped_duplicates"] == 1
    full["task_id"] = "TASK-002"
    assert migrate.write_tasks_json([full])["skipped_duplicates"] == 0
    full["last_updated"] = "2026-03-01"
    assert migrate.write_tasks_json([full])["skipped_duplicates"] == 1
    saved = invoke(task_query, capsys, args=["--task-id", "TASK-002"])["task"]
    assert saved["created_at"] == "2020-01-01" and saved["last_updated"] == "2026-02-01"
    assert saved["status"] == "in_progress"


def test_production_writer_http_get_compatibility(env):
    from x_ipe.services.task_board_service import TaskBoardService
    # Read-only execution of the unchanged production writer into this TEMP root
    # verifies old and promoted writers alike; no production data is touched.
    root = META.parents[2]
    writer = root / ".github" / "skills" / "x-ipe-tool-task-board-manager" / "scripts" / "task_create.py"
    result = subprocess.run([sys.executable, "-B", str(writer), "--task", json.dumps(task())],
                            cwd=env, text=True, capture_output=True, timeout=15,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    assert result.returncode == 0, result.stderr
    assert TaskBoardService(str(env)).list_tasks("all")["data"]["pagination"]["total"] == 1
    actual = TaskBoardService(str(env)).get_task("TASK-001")
    assert actual["success"] is True and actual["data"]["task_id"] == "TASK-001"


def concurrent(root, jobs):
    """Start real processes behind an input barrier; hard timeout detects deadlock."""
    processes = []
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for module, args, date in jobs:
        code = (
            f"import sys;sys.path.insert(0,{str(SCRIPTS)!r});import {module} as m;"
            "import task_create;"
                + (f"task_create._today_filename=lambda: 'tasks-{date}.json';"
                    + ("m._today_filename=task_create._today_filename;" if module == "task_ensure" else "") if date else "")
            + "print('ready',flush=True);sys.stdin.readline();"
            + f"m.main({args!r})"
        )
        proc = subprocess.Popen([sys.executable, "-B", "-c", code], cwd=root,
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, env=environment)
        processes.append(proc)
    try:
        for proc in processes:
            with selectors.DefaultSelector() as ready:
                ready.register(proc.stdout, selectors.EVENT_READ)
                assert ready.select(timeout=20), "Worker startup barrier timed out"
                assert proc.stdout.readline().strip() == "ready"
        for proc in processes:
            proc.stdin.write("go\n")
            proc.stdin.flush()
        results = []
        for proc in processes:
            out, err = proc.communicate(timeout=20)
            results.append((proc.returncode, out, err))
        return results
    finally:
        for proc in processes:
            if proc.poll() is None:
                proc.kill()
            proc.communicate()


def check_consistency(root):
    idx = store.read_index(directory(root))
    ids = []
    for path in directory(root).glob("tasks-*.json"):
        if path.name == "tasks-index.json" or path.name.endswith(".archived.json"):
            continue
        _, records = store.read_daily(path)
        for record in records:
            ids.append(record["task_id"])
            assert idx["entries"][record["task_id"]] == {
                "file": path.name, "status": record["status"], "last_updated": record["last_updated"]}
    assert len(ids) == len(set(ids)) == len(idx["entries"])
    return ids


def test_concurrent_auto_allocations_different_dates(env):
    jobs = [("task_create", ["--task", json.dumps(task(None))], f"2026-10-{10+i%3:02d}") for i in range(12)]
    results = concurrent(env, jobs)
    assert all(code == 0 and not err for code, out, err in results), results
    ids = [json.loads(out)["data"]["task_id"] for code, out, err in results]
    assert len(set(ids)) == 12
    assert set(ids) == {f"TASK-{i:03d}" for i in range(1, 13)}
    assert set(check_consistency(env)) == set(ids)


def test_concurrent_ensure_same_id_multiple_dates(env):
    jobs = [("task_ensure", ["--task", json.dumps(task("TASK-6749"))], f"2026-10-{10+i%3:02d}") for i in range(9)]
    results = concurrent(env, jobs)
    assert all(code == 0 and not err for code, out, err in results), results
    data = [json.loads(out)["data"] for code, out, err in results]
    assert sum(item["created"] for item in data) == 1
    assert all(item["task"] == data[0]["task"] for item in data)
    assert check_consistency(env) == ["TASK-6749"]
    assert {p.name for p in directory(env).glob("tasks-2026-10-*.json.lock")} == {
        "tasks-2026-10-10.json.lock", "tasks-2026-10-11.json.lock", "tasks-2026-10-12.json.lock"}


def test_concurrent_explicit_create_collision(env):
    jobs = [("task_create", ["--task", json.dumps(task())], "2026-10-13") for _ in range(6)]
    results = concurrent(env, jobs)
    assert sum(code == 0 for code, out, err in results) == 1
    for code, out, err in results:
        if code:
            assert code == 1 and json.loads(err)["error"] == "DUPLICATE_TASK_ID"
    assert check_consistency(env) == ["TASK-001"]


def test_mixed_update_archive_create_ensure_migration(env, capsys):
    seed(env, "TASK-OLD", "tasks-2026-01-01.json")
    seed(env, "TASK-EDIT", "tasks-2026-01-02.json")
    seed(env, "TASK-KEEP", "tasks-2026-01-03.json")
    planning = env / "x-ipe-docs" / "planning"
    (planning / "task-board.md").write_text(
        "| TASK-MIG | Skill Update | Review board contracts | Drift | done | 2026-01-02 | — | — |\n")
    jobs = [
        ("task_archive", ["--date", "2026-01-01"], None),
        ("task_update", ["--task-id", "TASK-EDIT", "--updates", '{"status":"completed"}'], None),
        ("task_ensure", ["--task", json.dumps(task("TASK-KEEP"))], "2026-10-13"),
        ("migrate", ["--tasks"], None),
    ] + [("task_create", ["--task", json.dumps(task(None))], "2026-01-02") for _ in range(4)]
    results = concurrent(env, jobs)
    assert all(code == 0 and not err for code, out, err in results), results
    ids = check_consistency(env)
    assert len(ids) == 7 and "TASK-OLD" not in ids and "TASK-MIG" in ids
    actual = invoke(task_query, capsys, args=["--task-id", "TASK-MIG"])["task"]
    assert actual["status"] == "completed"


def test_writers_observe_daily_then_index_lock_order(env, capsys, monkeypatch):
    held = []
    original = lib.with_file_lock
    @contextmanager
    def checked(path, **kwargs):
        name = Path(path).name
        if name != "tasks-index.json.lock":
            assert "tasks-index.json.lock" not in held
        with original(path, **kwargs):
            held.append(name)
            try:
                yield
            finally:
                assert held.pop() == name
    for module in (task_create, task_ensure, task_update, task_archive, migrate):
        monkeypatch.setattr(module, "with_file_lock", checked)
    invoke(task_create, capsys, task())
    invoke(task_ensure, capsys, task())
    invoke(task_update, capsys, args=["--task-id", "TASK-001", "--updates", '{"status":"done"}'])
    full = task("TASK-MIG", created_at="2026-01-01", last_updated="2026-01-01")
    migrate.write_tasks_json([full])
    invoke(task_archive, capsys, args=["--date", "2026-01-01"])
    assert not held


def test_candidate_output_compatible_with_actual_http_api(env, capsys):
    from flask import Flask
    from x_ipe.routes.task_board_routes import task_board_bp
    from x_ipe.routes.feature_board_routes import feature_board_bp
    import feature_create
    import feature_update
    result = invoke(task_ensure, capsys, task())
    feature_create.main(["--feature", json.dumps({
        "feature_id": "FEATURE-001-A", "epic_id": "EPIC-001", "title": "Board",
        "version": "1.0", "status": "Planned", "dependencies": []})])
    capsys.readouterr()
    feature_update.main(["--feature-id", "FEATURE-001-A", "--updates", '{"status":"Completed"}'])
    capsys.readouterr()
    app = Flask(__name__)
    app.config.update(TESTING=True, PROJECT_ROOT=str(env))
    app.register_blueprint(task_board_bp)
    app.register_blueprint(feature_board_bp)
    with app.test_client() as client:
        listed = client.get("/api/tasks/list?range=all").json["data"]
        assert listed["tasks"] == [result["task"]] and listed["pagination"]["total"] == 1
        fetched = client.get("/api/tasks/get/TASK-001")
        assert fetched.status_code == 200 and fetched.json == {"success": True, "data": result["task"]}
        feat = client.get("/api/features/get/FEATURE-001-A").json["data"]["feature"]
        assert feat["status"] == "Completed" and "assignee" not in feat
        assert client.get("/api/features/list").json["data"]["pagination"]["total"] == 1


def test_http_get_reads_cli_envelope(env, capsys):
    from x_ipe.services.task_board_service import TaskBoardService
    result = invoke(task_ensure, capsys, task())
    # Existing production task_create already emits this same envelope/schema.
    assert TaskBoardService(str(env)).get_task("TASK-001") == {
        "success": True, "data": result["task"]}


@pytest.mark.parametrize("field,value", [("status", "pending"), ("last_updated", "old")])
def test_ensure_rejects_interrupted_update_index(env, capsys, field, value):
    seed(env, "TASK-001")
    index = store.read_index(directory(env))
    index["entries"]["TASK-001"][field] = value
    lib.atomic_write_json(directory(env) / "tasks-index.json", index)
    before = snapshot(env)
    reject(task_ensure, capsys, task(), error="INCONSISTENT_BOARD")
    assert snapshot(env) == before


@pytest.mark.parametrize("content,error", [('[]', 'INVALID_BOARD'), ('{"entries":[]}', 'INVALID_BOARD'), ('broken', 'BOARD_READ_ERROR')])
@pytest.mark.parametrize("module", [task_query, task_update])
def test_single_operations_corrupt_index_fail_structured(env, capsys, content, error, module):
    seed(env, "TASK-001")
    (directory(env) / "tasks-index.json").write_text(content)
    before = snapshot(env)
    args = ["--task-id", "TASK-001"]
    if module is task_update:
        args += ["--updates", '{"status":"done"}']
    reject(module, capsys, args=args, error=error)
    assert snapshot(env) == before


def test_documented_examples_execute_in_temporary_project(env):
    seed(env, "TASK-900", "tasks-2026-01-01.json", indexed=True)
    # Archive example requires an authorized seeded date; auto-create example
    # must get TASK-001, so use nonnumeric historical ID instead.
    path = directory(env) / "tasks-2026-01-01.json"
    data = json.loads(path.read_text());data["tasks"][0]["task_id"] = "OLD"
    lib.atomic_write_json(path, data)
    lib.atomic_write_json(directory(env) / "tasks-index.json", {"entries": {
        "OLD": {"file": path.name, "status": "in_progress", "last_updated": "2026-01-01"}}})
    planning = env / "x-ipe-docs" / "planning"
    (planning / "task-board.md").write_text("# Empty tasks\n")
    (planning / "features.md").write_text("# Empty features\n")
    examples = (META / "candidate" / "references" / "examples.md").read_text()
    commands = [line for line in examples.splitlines() if line.startswith("uv run python ")]
    assert len(commands) == 11
    for line in commands:
        parts = shlex.split(line)[3:]
        name = Path(parts[0]).name
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / name), *parts[1:]],
                                cwd=env, text=True, capture_output=True, timeout=15,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        assert result.returncode == 0 and not result.stderr, (line, result.stdout, result.stderr)
    assert store.read_index(directory(env))["entries"]["TASK-001"]["status"] == "completed"
