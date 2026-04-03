"""Tests for Feature Board API (FEATURE-056-B).

Covers: FeatureBoardService + feature_board_routes blueprint.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from x_ipe.services.feature_board_service import FeatureBoardService


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


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
        "created_at": "2026-01-01T00:00:00Z",
        "last_updated": "2026-01-01T00:00:00Z",
    }
    base.update(overrides)
    return base


def _seed(tmp_path: Path, features: list[dict]) -> None:
    d = tmp_path / "x-ipe-docs" / "planning" / "features"
    d.mkdir(parents=True, exist_ok=True)
    (d / "features.json").write_text(json.dumps({"_version": "1.0", "features": features}))


def _svc(tmp_path: Path) -> FeatureBoardService:
    return FeatureBoardService(str(tmp_path))


# ------------------------------------------------------------------
# Flask test app
# ------------------------------------------------------------------


@pytest.fixture()
def client(tmp_path):
    from x_ipe.app import create_app
    app = create_app()
    app.config["TESTING"] = True
    app.config["PROJECT_ROOT"] = str(tmp_path)
    with app.test_client() as c:
        yield c


@pytest.fixture()
def seeded_client(tmp_path, client):
    _seed(tmp_path, [
        _make_feature(feature_id="FEATURE-001-A", epic_id="EPIC-001", status="Planned",
                      title="Auth Module", last_updated="2026-01-03T00:00:00Z"),
        _make_feature(feature_id="FEATURE-001-B", epic_id="EPIC-001", status="Completed",
                      title="DB Layer", last_updated="2026-01-01T00:00:00Z"),
        _make_feature(feature_id="FEATURE-002-A", epic_id="EPIC-002", status="Planned",
                      title="Web UI", last_updated="2026-01-02T00:00:00Z"),
    ])
    return client


# ==================================================================
# Service — List
# ==================================================================


class TestServiceListBasic:
    """Group 1: AC-056B-01a..01d"""

    def test_returns_success(self, tmp_path):
        _seed(tmp_path, [_make_feature()])
        r = _svc(tmp_path).list_features()
        assert r["success"] is True
        assert "features" in r["data"]
        assert "pagination" in r["data"]

    def test_default_pagination(self, tmp_path):
        _seed(tmp_path, [_make_feature()])
        r = _svc(tmp_path).list_features()
        assert r["data"]["pagination"]["page"] == 1
        assert r["data"]["pagination"]["page_size"] == 50

    def test_sorted_desc(self, tmp_path):
        feats = [
            _make_feature(feature_id="A", last_updated="2026-01-01T00:00:00Z"),
            _make_feature(feature_id="B", last_updated="2026-01-03T00:00:00Z"),
            _make_feature(feature_id="C", last_updated="2026-01-02T00:00:00Z"),
        ]
        _seed(tmp_path, feats)
        r = _svc(tmp_path).list_features()
        ids = [f["feature_id"] for f in r["data"]["features"]]
        assert ids == ["B", "C", "A"]

    def test_all_fields(self, tmp_path):
        _seed(tmp_path, [_make_feature()])
        r = _svc(tmp_path).list_features()
        feat = r["data"]["features"][0]
        for key in ("feature_id", "epic_id", "title", "version", "status",
                     "description", "dependencies", "specification_link",
                     "created_at", "last_updated"):
            assert key in feat


class TestServiceFiltering:
    """Group 2: AC-056B-02a..02e"""

    def test_filter_epic_id(self, tmp_path):
        _seed(tmp_path, [
            _make_feature(feature_id="A", epic_id="EPIC-001"),
            _make_feature(feature_id="B", epic_id="EPIC-002"),
        ])
        r = _svc(tmp_path).list_features(epic_id="EPIC-001")
        assert len(r["data"]["features"]) == 1

    def test_filter_status(self, tmp_path):
        _seed(tmp_path, [
            _make_feature(feature_id="A", status="Planned"),
            _make_feature(feature_id="B", status="Completed"),
        ])
        r = _svc(tmp_path).list_features(status="Completed")
        assert len(r["data"]["features"]) == 1

    def test_search_case_insensitive(self, tmp_path):
        _seed(tmp_path, [
            _make_feature(feature_id="A", title="Auth Module"),
            _make_feature(feature_id="B", title="DB Layer"),
        ])
        r = _svc(tmp_path).list_features(search="AUTH")
        assert len(r["data"]["features"]) == 1

    def test_combined_filters(self, tmp_path):
        _seed(tmp_path, [
            _make_feature(feature_id="A", epic_id="EPIC-001", status="Planned"),
            _make_feature(feature_id="B", epic_id="EPIC-001", status="Completed"),
            _make_feature(feature_id="C", epic_id="EPIC-002", status="Planned"),
        ])
        r = _svc(tmp_path).list_features(epic_id="EPIC-001", status="Planned")
        assert len(r["data"]["features"]) == 1
        assert r["data"]["features"][0]["feature_id"] == "A"

    def test_no_match_empty(self, tmp_path):
        _seed(tmp_path, [_make_feature()])
        r = _svc(tmp_path).list_features(status="NonExistent")
        assert r["data"]["features"] == []
        assert r["data"]["pagination"]["total"] == 0
        assert r["data"]["pagination"]["total_pages"] == 1


class TestServicePagination:
    """Group 3: AC-056B-03a..03b"""

    def test_page_2(self, tmp_path):
        feats = [_make_feature(feature_id=f"F-{i}") for i in range(7)]
        _seed(tmp_path, feats)
        r = _svc(tmp_path).list_features(page=2, page_size=3)
        assert r["data"]["pagination"]["page"] == 2
        assert r["data"]["pagination"]["total"] == 7
        assert r["data"]["pagination"]["total_pages"] == 3
        assert len(r["data"]["features"]) == 3

    def test_page_beyond_range(self, tmp_path):
        _seed(tmp_path, [_make_feature()])
        r = _svc(tmp_path).list_features(page=999)
        assert r["data"]["features"] == []
        assert r["data"]["pagination"]["total"] == 1


# ==================================================================
# Service — Get
# ==================================================================


class TestServiceGet:
    """Group 4: AC-056B-04a..04c"""

    def test_found(self, tmp_path):
        _seed(tmp_path, [_make_feature()])
        r = _svc(tmp_path).get_feature("FEATURE-001-A")
        assert r["success"] is True
        assert r["data"]["feature"]["feature_id"] == "FEATURE-001-A"

    def test_not_found(self, tmp_path):
        _seed(tmp_path, [_make_feature()])
        r = _svc(tmp_path).get_feature("FEATURE-999-Z")
        assert r["success"] is False
        assert r["error"] == "NOT_FOUND"

    def test_all_fields(self, tmp_path):
        _seed(tmp_path, [_make_feature()])
        r = _svc(tmp_path).get_feature("FEATURE-001-A")
        feat = r["data"]["feature"]
        assert all(k in feat for k in ("feature_id", "title", "status", "epic_id"))


# ==================================================================
# Service — Epic Summary
# ==================================================================


class TestServiceEpicSummary:
    """Group 5: AC-056B-05a..05d"""

    def test_multiple_epics(self, tmp_path):
        _seed(tmp_path, [
            _make_feature(feature_id="A", epic_id="EPIC-001", status="Planned"),
            _make_feature(feature_id="B", epic_id="EPIC-001", status="Completed"),
            _make_feature(feature_id="C", epic_id="EPIC-002", status="Planned"),
        ])
        r = _svc(tmp_path).epic_summary()
        assert r["success"] is True
        sums = r["data"]["summaries"]
        assert len(sums) == 2
        e1 = next(s for s in sums if s["epic_id"] == "EPIC-001")
        assert e1["total"] == 2
        assert e1["Planned"] == 1
        assert e1["Completed"] == 1

    def test_filter_epic_id(self, tmp_path):
        _seed(tmp_path, [
            _make_feature(feature_id="A", epic_id="EPIC-001"),
            _make_feature(feature_id="B", epic_id="EPIC-002"),
        ])
        r = _svc(tmp_path).epic_summary(epic_id="EPIC-002")
        assert len(r["data"]["summaries"]) == 1
        assert r["data"]["summaries"][0]["epic_id"] == "EPIC-002"

    def test_all_completed(self, tmp_path):
        _seed(tmp_path, [
            _make_feature(feature_id="A", epic_id="EPIC-001", status="Completed"),
            _make_feature(feature_id="B", epic_id="EPIC-001", status="Completed"),
        ])
        r = _svc(tmp_path).epic_summary()
        assert r["data"]["summaries"][0]["Completed"] == 2

    def test_empty(self, tmp_path):
        r = _svc(tmp_path).epic_summary()
        assert r["data"]["summaries"] == []


# ==================================================================
# Service — Edge Cases
# ==================================================================


class TestServiceEdgeCases:
    """Group 7: AC-056B-07a..07c"""

    def test_no_dir(self, tmp_path):
        r = _svc(tmp_path).list_features()
        assert r["success"] is True
        assert r["data"]["features"] == []

    def test_malformed_json(self, tmp_path):
        d = tmp_path / "x-ipe-docs" / "planning" / "features"
        d.mkdir(parents=True, exist_ok=True)
        (d / "features.json").write_text("not json")
        r = _svc(tmp_path).list_features()
        assert r["data"]["features"] == []

    def test_get_from_valid_file(self, tmp_path):
        _seed(tmp_path, [_make_feature()])
        r = _svc(tmp_path).get_feature("FEATURE-001-A")
        assert r["success"] is True


# ==================================================================
# Routes — List
# ==================================================================


class TestListRoute:
    """Group 1+2+3 route tests"""

    def test_list_empty_200(self, client):
        r = client.get("/api/features/list")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True

    def test_list_with_data(self, seeded_client):
        r = seeded_client.get("/api/features/list")
        assert r.status_code == 200
        data = r.get_json()
        assert len(data["data"]["features"]) == 3

    def test_list_with_filters(self, seeded_client):
        r = seeded_client.get("/api/features/list?epic_id=EPIC-001&status=Planned")
        data = r.get_json()
        assert len(data["data"]["features"]) == 1

    def test_list_search(self, seeded_client):
        r = seeded_client.get("/api/features/list?search=auth")
        data = r.get_json()
        assert len(data["data"]["features"]) == 1

    def test_invalid_page_400(self, client):
        r = client.get("/api/features/list?page=abc")
        assert r.status_code == 400

    def test_page_size_zero_400(self, client):
        r = client.get("/api/features/list?page_size=0")
        assert r.status_code == 400

    def test_cache_control(self, client):
        r = client.get("/api/features/list")
        assert r.headers.get("Cache-Control") == "no-store"


# ==================================================================
# Routes — Get
# ==================================================================


class TestGetRoute:
    """Group 4 route tests"""

    def test_found(self, seeded_client):
        r = seeded_client.get("/api/features/get/FEATURE-001-A")
        assert r.status_code == 200
        assert r.get_json()["data"]["feature"]["feature_id"] == "FEATURE-001-A"

    def test_not_found_404(self, seeded_client):
        r = seeded_client.get("/api/features/get/FEATURE-999-Z")
        assert r.status_code == 404

    def test_cache_control(self, seeded_client):
        r = seeded_client.get("/api/features/get/FEATURE-001-A")
        assert r.headers.get("Cache-Control") == "no-store"


# ==================================================================
# Routes — Epic Summary
# ==================================================================


class TestEpicSummaryRoute:
    """Group 5 route tests"""

    def test_summary_200(self, seeded_client):
        r = seeded_client.get("/api/features/epic-summary")
        assert r.status_code == 200
        data = r.get_json()
        assert len(data["data"]["summaries"]) == 2

    def test_summary_with_filter(self, seeded_client):
        r = seeded_client.get("/api/features/epic-summary?epic_id=EPIC-001")
        data = r.get_json()
        assert len(data["data"]["summaries"]) == 1

    def test_summary_cache_control(self, seeded_client):
        r = seeded_client.get("/api/features/epic-summary")
        assert r.headers.get("Cache-Control") == "no-store"


# ==================================================================
# Error Handling & Blueprint
# ==================================================================


class TestErrorHandling:
    """Group 6: AC-056B-06a"""

    def test_internal_error_500(self, tmp_path):
        from unittest.mock import patch
        from x_ipe.app import create_app

        app = create_app()
        app.config["TESTING"] = True
        app.config["PROJECT_ROOT"] = str(tmp_path)

        with patch.object(FeatureBoardService, "list_features", side_effect=RuntimeError("boom")):
            with app.test_client() as c:
                r = c.get("/api/features/list")
                assert r.status_code == 500
                assert r.get_json()["error"] == "INTERNAL_ERROR"


class TestBlueprintRegistration:
    """Group 6: AC-056B-06c..06d"""

    def test_routes_registered(self, client):
        rules = [r.rule for r in client.application.url_map.iter_rules()]
        assert "/api/features/list" in rules
        assert "/api/features/epic-summary" in rules
        assert any("feature_id" in r for r in rules if "features/get" in r)

    def test_service_uses_direct_import(self):
        import inspect
        source = inspect.getsource(FeatureBoardService)
        assert "subprocess" not in source
