"""Tests for feature CRUD scripts (FEATURE-056-A).

Covers: feature_create.py, feature_update.py, feature_query.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts dir to path for imports
_SCRIPTS = Path(__file__).resolve().parents[1] / ".github" / "skills" / "x-ipe-tool-task-board-manager" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from feature_create import main as create_main
from feature_create import VALID_FEATURE_STATUSES
from feature_update import main as update_main
from feature_query import main as query_main


def _features_path(tmp_path: Path) -> Path:
    return tmp_path / "x-ipe-docs" / "planning" / "features" / "features.json"


def _make_feature(**overrides) -> dict:
    base = {
        "feature_id": "FEATURE-001-A",
        "epic_id": "EPIC-001",
        "title": "Test Feature",
        "version": "v1.0",
        "status": "Planned",
        "description": "A test feature",
        "dependencies": [],
        "specification_link": "",
        "created_at": "2026-01-01T00:00:00+00:00",
        "last_updated": "2026-01-01T00:00:00+00:00",
    }
    base.update(overrides)
    return base


def _seed_features(tmp_path: Path, features: list[dict]) -> None:
    """Write features.json with given features."""
    fp = _features_path(tmp_path)
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps({"_version": "1.0", "features": features}))


def _read_store(tmp_path: Path) -> dict:
    return json.loads(_features_path(tmp_path).read_text())


@pytest.fixture(autouse=True)
def _patch_root(tmp_path, monkeypatch):
    """Redirect resolve_data_path to tmp_path."""
    import _board_lib
    monkeypatch.setattr(_board_lib, "_resolve_project_root", lambda: tmp_path)


# ============================================================
# feature_create.py
# ============================================================

class TestCreateBasic:
    """Group 1: AC-056A-01a..01e"""

    def test_create_success(self, tmp_path, capsys):
        feat = {k: v for k, v in _make_feature().items() if k not in ("created_at", "last_updated")}
        create_main(["--feature", json.dumps(feat)])
        out = json.loads(capsys.readouterr().out)
        assert out["success"] is True
        assert out["data"]["feature_id"] == "FEATURE-001-A"

    def test_auto_timestamps(self, tmp_path, capsys):
        feat = {k: v for k, v in _make_feature().items() if k not in ("created_at", "last_updated")}
        feat["created_at"] = "should-be-overridden"
        create_main(["--feature", json.dumps(feat)])
        store = _read_store(tmp_path)
        saved = store["features"][0]
        assert saved["created_at"] != "should-be-overridden"
        assert "T" in saved["created_at"]

    def test_missing_required_field(self, capsys):
        feat = {"feature_id": "FEATURE-001-A"}
        with pytest.raises(SystemExit) as exc_info:
            create_main(["--feature", json.dumps(feat)])
        assert exc_info.value.code == 1

    def test_unknown_field_rejected(self, capsys):
        feat = {k: v for k, v in _make_feature().items() if k not in ("created_at", "last_updated")}
        feat["bogus_field"] = "nope"
        with pytest.raises(SystemExit) as exc_info:
            create_main(["--feature", json.dumps(feat)])
        assert exc_info.value.code == 1

    def test_invalid_status_rejected(self, capsys):
        feat = {k: v for k, v in _make_feature(status="Invalid").items()
                if k not in ("created_at", "last_updated")}
        with pytest.raises(SystemExit) as exc_info:
            create_main(["--feature", json.dumps(feat)])
        assert exc_info.value.code == 1


class TestCreateFileOps:
    """Group 2: AC-056A-02a..02d"""

    def test_creates_new_file(self, tmp_path, capsys):
        assert not _features_path(tmp_path).exists()
        feat = {k: v for k, v in _make_feature().items() if k not in ("created_at", "last_updated")}
        create_main(["--feature", json.dumps(feat)])
        assert _features_path(tmp_path).exists()
        store = _read_store(tmp_path)
        assert store["_version"] == "1.0"
        assert len(store["features"]) == 1

    def test_appends_to_existing(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        feat2 = {k: v for k, v in _make_feature(feature_id="FEATURE-001-B", title="Second").items()
                 if k not in ("created_at", "last_updated")}
        create_main(["--feature", json.dumps(feat2)])
        store = _read_store(tmp_path)
        assert len(store["features"]) == 2

    def test_duplicate_rejected(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        feat = {k: v for k, v in _make_feature().items() if k not in ("created_at", "last_updated")}
        with pytest.raises(SystemExit) as exc_info:
            create_main(["--feature", json.dumps(feat)])
        assert exc_info.value.code == 1
        err = capsys.readouterr().err
        assert "DUPLICATE_ERROR" in err

    def test_invalid_json_string(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            create_main(["--feature", "not-json"])
        assert exc_info.value.code == 1

    def test_non_object_json(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            create_main(["--feature", '["array"]'])
        assert exc_info.value.code == 1


# ============================================================
# feature_update.py
# ============================================================

class TestUpdateBasic:
    """Group 3: AC-056A-03a..03e"""

    def test_update_success(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        update_main(["--feature-id", "FEATURE-001-A", "--updates", '{"title": "Updated Title"}'])
        out = json.loads(capsys.readouterr().out)
        assert out["success"] is True
        assert "title" in out["data"]["updated_fields"]
        store = _read_store(tmp_path)
        assert store["features"][0]["title"] == "Updated Title"

    def test_auto_last_updated(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature(last_updated="2020-01-01T00:00:00Z")])
        update_main(["--feature-id", "FEATURE-001-A", "--updates", '{"title": "New"}'])
        store = _read_store(tmp_path)
        assert store["features"][0]["last_updated"] != "2020-01-01T00:00:00Z"

    def test_immutable_feature_id(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        with pytest.raises(SystemExit) as exc_info:
            update_main(["--feature-id", "FEATURE-001-A", "--updates", '{"feature_id": "NEW"}'])
        assert exc_info.value.code == 1
        assert "IMMUTABLE_FIELD" in capsys.readouterr().err

    def test_immutable_epic_id(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        with pytest.raises(SystemExit) as exc_info:
            update_main(["--feature-id", "FEATURE-001-A", "--updates", '{"epic_id": "EPIC-999"}'])
        assert exc_info.value.code == 1

    def test_immutable_created_at(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        with pytest.raises(SystemExit) as exc_info:
            update_main(["--feature-id", "FEATURE-001-A", "--updates", '{"created_at": "now"}'])
        assert exc_info.value.code == 1

    def test_unknown_field(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        with pytest.raises(SystemExit) as exc_info:
            update_main(["--feature-id", "FEATURE-001-A", "--updates", '{"bogus": "val"}'])
        assert exc_info.value.code == 1
        assert "UNKNOWN_FIELD" in capsys.readouterr().err

    def test_not_found(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        with pytest.raises(SystemExit) as exc_info:
            update_main(["--feature-id", "FEATURE-999-Z", "--updates", '{"title": "X"}'])
        assert exc_info.value.code == 2

    def test_no_features_file(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            update_main(["--feature-id", "FEATURE-001-A", "--updates", '{"title": "X"}'])
        assert exc_info.value.code == 2


class TestUpdateStatus:
    """Group 4: AC-056A-04a..04b"""

    def test_valid_status(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        update_main(["--feature-id", "FEATURE-001-A", "--updates", '{"status": "Completed"}'])
        store = _read_store(tmp_path)
        assert store["features"][0]["status"] == "Completed"

    def test_invalid_status(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        with pytest.raises(SystemExit) as exc_info:
            update_main(["--feature-id", "FEATURE-001-A", "--updates", '{"status": "BadStatus"}'])
        assert exc_info.value.code == 1
        assert "INVALID_STATUS" in capsys.readouterr().err

    def test_empty_updates(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        with pytest.raises(SystemExit) as exc_info:
            update_main(["--feature-id", "FEATURE-001-A", "--updates", '{}'])
        assert exc_info.value.code == 1


# ============================================================
# feature_query.py — List Mode
# ============================================================

class TestQueryList:
    """Group 5: AC-056A-05a..05g"""

    def test_list_all_sorted(self, tmp_path, capsys):
        feats = [
            _make_feature(feature_id="FEATURE-001-A", last_updated="2026-01-01T00:00:00Z"),
            _make_feature(feature_id="FEATURE-001-B", last_updated="2026-01-03T00:00:00Z"),
            _make_feature(feature_id="FEATURE-001-C", last_updated="2026-01-02T00:00:00Z"),
        ]
        _seed_features(tmp_path, feats)
        query_main([])
        out = json.loads(capsys.readouterr().out)
        assert out["success"] is True
        ids = [f["feature_id"] for f in out["data"]["features"]]
        assert ids == ["FEATURE-001-B", "FEATURE-001-C", "FEATURE-001-A"]

    def test_filter_by_epic_id(self, tmp_path, capsys):
        feats = [
            _make_feature(feature_id="FEATURE-001-A", epic_id="EPIC-001"),
            _make_feature(feature_id="FEATURE-002-A", epic_id="EPIC-002"),
        ]
        _seed_features(tmp_path, feats)
        query_main(["--epic-id", "EPIC-001"])
        out = json.loads(capsys.readouterr().out)
        assert len(out["data"]["features"]) == 1
        assert out["data"]["features"][0]["epic_id"] == "EPIC-001"

    def test_filter_by_status(self, tmp_path, capsys):
        feats = [
            _make_feature(feature_id="FEATURE-001-A", status="Planned"),
            _make_feature(feature_id="FEATURE-001-B", status="Completed"),
        ]
        _seed_features(tmp_path, feats)
        query_main(["--status", "Completed"])
        out = json.loads(capsys.readouterr().out)
        assert len(out["data"]["features"]) == 1

    def test_search_case_insensitive(self, tmp_path, capsys):
        feats = [
            _make_feature(feature_id="FEATURE-001-A", title="Auth Module"),
            _make_feature(feature_id="FEATURE-001-B", title="Database Layer"),
        ]
        _seed_features(tmp_path, feats)
        query_main(["--search", "auth"])
        out = json.loads(capsys.readouterr().out)
        assert len(out["data"]["features"]) == 1
        assert out["data"]["features"][0]["title"] == "Auth Module"

    def test_pagination(self, tmp_path, capsys):
        feats = [_make_feature(feature_id=f"FEATURE-001-{chr(65+i)}") for i in range(7)]
        _seed_features(tmp_path, feats)
        query_main(["--page", "2", "--page-size", "3"])
        out = json.loads(capsys.readouterr().out)
        assert out["data"]["page"] == 2
        assert out["data"]["page_size"] == 3
        assert out["data"]["total"] == 7
        assert out["data"]["total_pages"] == 3
        assert len(out["data"]["features"]) == 3

    def test_combined_filters(self, tmp_path, capsys):
        feats = [
            _make_feature(feature_id="FEATURE-001-A", epic_id="EPIC-001", status="Planned"),
            _make_feature(feature_id="FEATURE-001-B", epic_id="EPIC-001", status="Completed"),
            _make_feature(feature_id="FEATURE-002-A", epic_id="EPIC-002", status="Planned"),
        ]
        _seed_features(tmp_path, feats)
        query_main(["--epic-id", "EPIC-001", "--status", "Planned"])
        out = json.loads(capsys.readouterr().out)
        assert len(out["data"]["features"]) == 1
        assert out["data"]["features"][0]["feature_id"] == "FEATURE-001-A"

    def test_no_features_file(self, capsys):
        query_main([])
        out = json.loads(capsys.readouterr().out)
        assert out["success"] is True
        assert out["data"]["total"] == 0
        assert out["data"]["total_pages"] == 1


# ============================================================
# feature_query.py — Single Mode
# ============================================================

class TestQuerySingle:
    """Group 6: AC-056A-06a..06c"""

    def test_single_found(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        query_main(["--feature-id", "FEATURE-001-A"])
        out = json.loads(capsys.readouterr().out)
        assert out["success"] is True
        assert out["data"]["feature"]["feature_id"] == "FEATURE-001-A"

    def test_single_not_found(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        with pytest.raises(SystemExit) as exc_info:
            query_main(["--feature-id", "FEATURE-999-Z"])
        assert exc_info.value.code == 2

    def test_single_mode_ignores_filters(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature(status="Planned")])
        query_main(["--feature-id", "FEATURE-001-A", "--status", "Completed"])
        out = json.loads(capsys.readouterr().out)
        assert out["success"] is True
        assert out["data"]["feature"]["status"] == "Planned"


# ============================================================
# feature_query.py — Epic Summary
# ============================================================

class TestEpicSummary:
    """Group 7: AC-056A-07a..07d"""

    def test_summary_multiple_epics(self, tmp_path, capsys):
        feats = [
            _make_feature(feature_id="FEATURE-001-A", epic_id="EPIC-001", status="Planned"),
            _make_feature(feature_id="FEATURE-001-B", epic_id="EPIC-001", status="Completed"),
            _make_feature(feature_id="FEATURE-002-A", epic_id="EPIC-002", status="Planned"),
        ]
        _seed_features(tmp_path, feats)
        query_main(["--epic-summary"])
        out = json.loads(capsys.readouterr().out)
        summaries = out["data"]["summaries"]
        assert len(summaries) == 2
        epic1 = next(s for s in summaries if s["epic_id"] == "EPIC-001")
        assert epic1["total"] == 2
        assert epic1["Planned"] == 1
        assert epic1["Completed"] == 1

    def test_summary_with_epic_filter(self, tmp_path, capsys):
        feats = [
            _make_feature(feature_id="FEATURE-001-A", epic_id="EPIC-001"),
            _make_feature(feature_id="FEATURE-002-A", epic_id="EPIC-002"),
        ]
        _seed_features(tmp_path, feats)
        query_main(["--epic-summary", "--epic-id", "EPIC-002"])
        out = json.loads(capsys.readouterr().out)
        assert len(out["data"]["summaries"]) == 1
        assert out["data"]["summaries"][0]["epic_id"] == "EPIC-002"

    def test_summary_all_completed(self, tmp_path, capsys):
        feats = [
            _make_feature(feature_id="FEATURE-001-A", epic_id="EPIC-001", status="Completed"),
            _make_feature(feature_id="FEATURE-001-B", epic_id="EPIC-001", status="Completed"),
        ]
        _seed_features(tmp_path, feats)
        query_main(["--epic-summary"])
        out = json.loads(capsys.readouterr().out)
        epic1 = out["data"]["summaries"][0]
        assert epic1["total"] == 2
        assert epic1.get("Completed") == 2

    def test_summary_empty(self, capsys):
        query_main(["--epic-summary"])
        out = json.loads(capsys.readouterr().out)
        assert out["data"]["summaries"] == []


# ============================================================
# Shared Patterns
# ============================================================

class TestSharedPatterns:
    """Group 8: AC-056A-08a..08e"""

    def test_lock_timeout_arg(self, tmp_path, capsys):
        feat = {k: v for k, v in _make_feature().items() if k not in ("created_at", "last_updated")}
        create_main(["--feature", json.dumps(feat), "--lock-timeout", "5"])
        out = json.loads(capsys.readouterr().out)
        assert out["success"] is True

    def test_json_output_format(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        query_main([])
        out = json.loads(capsys.readouterr().out)
        assert "success" in out
        assert "data" in out

    def test_all_valid_statuses_accepted(self, tmp_path, capsys):
        for i, status in enumerate(sorted(VALID_FEATURE_STATUSES)):
            fid = f"FEATURE-001-{chr(65+i)}"
            feat = {k: v for k, v in _make_feature(feature_id=fid, status=status).items()
                    if k not in ("created_at", "last_updated")}
            create_main(["--feature", json.dumps(feat)])
        store = _read_store(tmp_path)
        assert len(store["features"]) == len(VALID_FEATURE_STATUSES)

    def test_update_type_error(self, tmp_path, capsys):
        _seed_features(tmp_path, [_make_feature()])
        with pytest.raises(SystemExit) as exc_info:
            update_main(["--feature-id", "FEATURE-001-A", "--updates", '{"title": 123}'])
        assert exc_info.value.code == 1
        assert "TYPE_ERROR" in capsys.readouterr().err

    def test_invalid_json_update(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            update_main(["--feature-id", "FEATURE-001-A", "--updates", "bad"])
        assert exc_info.value.code == 1
