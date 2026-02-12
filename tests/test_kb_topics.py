"""Tests for FEATURE-025-D: KB Topics & Summaries.

Tests cover:
- KBService.get_summary_versions()
- KBService.get_summary_content()
- KBService.get_topic_detail()
- GET /api/kb/topics/<name>/detail endpoint
- GET /api/kb/topics/<name>/summary endpoint
"""
import json
import tempfile
import shutil
import pytest
from pathlib import Path

from x_ipe.services import KBService
from x_ipe.app import create_app


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def temp_project_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def kb_with_topics(temp_project_dir):
    """KB with 2 topics, summaries, and raw files."""
    kb = Path(temp_project_dir) / "x-ipe-docs" / "knowledge-base"
    # Topic 1: machine-learning (2 summaries, 2 raw files)
    (kb / "topics" / "machine-learning" / "raw").mkdir(parents=True)
    (kb / "processed" / "machine-learning").mkdir(parents=True)
    (kb / "topics" / "machine-learning" / "raw" / "paper.pdf").write_bytes(b"%PDF-fake-content")
    (kb / "topics" / "machine-learning" / "raw" / "guide.md").write_text("# ML Guide\nContent here")
    (kb / "topics" / "machine-learning" / "metadata.json").write_text(json.dumps({
        "name": "machine-learning",
        "description": "ML topic",
        "file_count": 2,
        "last_updated": "2026-02-05T10:30:45Z",
        "tags": ["ml", "ai"]
    }))
    (kb / "processed" / "machine-learning" / "summary-v1.md").write_text(
        "# Topic: machine-learning\n\n> Generated: 2026-02-03\n> Version: v1\n\n## Overview\nFirst version."
    )
    (kb / "processed" / "machine-learning" / "summary-v2.md").write_text(
        "# Topic: machine-learning\n\n> Generated: 2026-02-05\n> Version: v2\n\n## Overview\nSecond version with more detail."
    )

    # Topic 2: api-design (1 summary, 1 raw file)
    (kb / "topics" / "api-design" / "raw").mkdir(parents=True)
    (kb / "processed" / "api-design").mkdir(parents=True)
    (kb / "topics" / "api-design" / "raw" / "rest-guide.md").write_text("# REST Guide")
    (kb / "topics" / "api-design" / "metadata.json").write_text(json.dumps({
        "name": "api-design",
        "description": "API design patterns",
        "file_count": 1,
        "last_updated": "2026-02-04T08:00:00Z",
        "tags": ["api", "rest"]
    }))
    (kb / "processed" / "api-design" / "summary-v1.md").write_text(
        "# Topic: api-design\n\n> Generated: 2026-02-04\n> Version: v1\n\n## Overview\nAPI patterns."
    )

    # Index + structure
    (kb / "landing").mkdir(parents=True, exist_ok=True)
    (kb / "index").mkdir(parents=True, exist_ok=True)
    (kb / "index" / "file-index.json").write_text(json.dumps({
        "version": "1.0",
        "last_updated": "2026-02-05T15:00:00Z",
        "files": []
    }))
    return kb


@pytest.fixture
def kb_empty_topic(temp_project_dir):
    """KB with a topic that has no summaries."""
    kb = Path(temp_project_dir) / "x-ipe-docs" / "knowledge-base"
    (kb / "topics" / "empty-topic" / "raw").mkdir(parents=True)
    (kb / "processed" / "empty-topic").mkdir(parents=True)
    (kb / "topics" / "empty-topic" / "metadata.json").write_text(json.dumps({
        "name": "empty-topic",
        "description": "No summaries yet",
        "file_count": 0,
        "last_updated": "2026-02-05T10:00:00Z",
        "tags": []
    }))
    (kb / "landing").mkdir(parents=True, exist_ok=True)
    (kb / "index").mkdir(parents=True, exist_ok=True)
    (kb / "index" / "file-index.json").write_text(json.dumps({
        "version": "1.0", "last_updated": "2026-02-05T15:00:00Z", "files": []
    }))
    return kb


@pytest.fixture
def kb_service(temp_project_dir, kb_with_topics):
    return KBService(temp_project_dir)


@pytest.fixture
def kb_service_empty(temp_project_dir, kb_empty_topic):
    return KBService(temp_project_dir)


@pytest.fixture
def client(temp_project_dir, kb_with_topics):
    app = create_app({"TESTING": True, "PROJECT_ROOT": temp_project_dir})
    return app.test_client()


@pytest.fixture
def client_empty(temp_project_dir, kb_empty_topic):
    app = create_app({"TESTING": True, "PROJECT_ROOT": temp_project_dir})
    return app.test_client()


# ── Service Tests: get_summary_versions ───────────────────────────────

class TestGetSummaryVersions:
    def test_returns_versions_newest_first(self, kb_service):
        versions = kb_service.get_summary_versions("machine-learning")
        assert len(versions) == 2
        assert versions[0]["version"] == 2
        assert versions[1]["version"] == 1

    def test_marks_latest_as_current(self, kb_service):
        versions = kb_service.get_summary_versions("machine-learning")
        assert versions[0]["current"] is True
        assert versions[1]["current"] is False

    def test_each_version_has_date(self, kb_service):
        versions = kb_service.get_summary_versions("machine-learning")
        for v in versions:
            assert "date" in v
            assert "Z" in v["date"]

    def test_empty_when_no_summaries(self, kb_service_empty):
        versions = kb_service_empty.get_summary_versions("empty-topic")
        assert versions == []

    def test_empty_when_topic_not_found(self, kb_service):
        versions = kb_service.get_summary_versions("nonexistent")
        assert versions == []

    def test_limits_to_5_versions(self, kb_service, kb_with_topics):
        processed = kb_with_topics / "processed" / "machine-learning"
        for i in range(3, 9):
            (processed / f"summary-v{i}.md").write_text(f"# v{i}")
        versions = kb_service.get_summary_versions("machine-learning")
        assert len(versions) == 5
        assert versions[0]["version"] == 8


# ── Service Tests: get_summary_content ────────────────────────────────

class TestGetSummaryContent:
    def test_returns_latest_by_default(self, kb_service):
        result = kb_service.get_summary_content("machine-learning")
        assert result is not None
        assert result["version"] == 2
        assert "Second version" in result["content"]

    def test_returns_specific_version(self, kb_service):
        result = kb_service.get_summary_content("machine-learning", "1")
        assert result is not None
        assert result["version"] == 1
        assert "First version" in result["content"]

    def test_returns_none_for_missing_version(self, kb_service):
        result = kb_service.get_summary_content("machine-learning", "99")
        assert result is None

    def test_returns_none_for_missing_topic(self, kb_service):
        result = kb_service.get_summary_content("nonexistent")
        assert result is None

    def test_returns_none_when_no_summaries(self, kb_service_empty):
        result = kb_service_empty.get_summary_content("empty-topic")
        assert result is None

    def test_content_has_required_fields(self, kb_service):
        result = kb_service.get_summary_content("machine-learning")
        assert "version" in result
        assert "date" in result
        assert "content" in result


# ── Service Tests: get_topic_detail ───────────────────────────────────

class TestGetTopicDetail:
    def test_returns_full_detail(self, kb_service):
        detail = kb_service.get_topic_detail("machine-learning")
        assert detail is not None
        assert detail["name"] == "machine-learning"
        assert "summary_count" in detail
        assert "summaries" in detail
        assert "files" in detail
        assert "related_topics" in detail

    def test_summary_count_matches(self, kb_service):
        detail = kb_service.get_topic_detail("machine-learning")
        assert detail["summary_count"] == 2

    def test_files_listed(self, kb_service):
        detail = kb_service.get_topic_detail("machine-learning")
        assert len(detail["files"]) == 2
        names = [f["name"] for f in detail["files"]]
        assert "paper.pdf" in names
        assert "guide.md" in names

    def test_file_has_required_fields(self, kb_service):
        detail = kb_service.get_topic_detail("machine-learning")
        for f in detail["files"]:
            assert "name" in f
            assert "path" in f
            assert "size" in f
            assert "type" in f

    def test_related_topics_excludes_self(self, kb_service):
        detail = kb_service.get_topic_detail("machine-learning")
        assert "machine-learning" not in detail["related_topics"]
        assert "api-design" in detail["related_topics"]

    def test_related_topics_limited_to_4(self, kb_service, kb_with_topics):
        for i in range(6):
            topic = f"extra-topic-{i}"
            (kb_with_topics / "topics" / topic / "raw").mkdir(parents=True)
            (kb_with_topics / "topics" / topic / "metadata.json").write_text(
                json.dumps({"name": topic, "description": "", "file_count": 0,
                            "last_updated": "2026-02-05T10:00:00Z", "tags": []})
            )
        detail = kb_service.get_topic_detail("machine-learning")
        assert len(detail["related_topics"]) <= 4

    def test_returns_none_for_missing_topic(self, kb_service):
        detail = kb_service.get_topic_detail("nonexistent")
        assert detail is None

    def test_empty_topic_has_empty_files_and_summaries(self, kb_service_empty):
        detail = kb_service_empty.get_topic_detail("empty-topic")
        assert detail is not None
        assert detail["summary_count"] == 0
        assert detail["summaries"] == []

    def test_summaries_are_newest_first(self, kb_service):
        detail = kb_service.get_topic_detail("machine-learning")
        versions = [s["version"] for s in detail["summaries"]]
        assert versions == sorted(versions, reverse=True)


# ── API Tests: GET /api/kb/topics/<name>/detail ───────────────────────

class TestTopicDetailEndpoint:
    def test_returns_200_with_detail(self, client):
        resp = client.get("/api/kb/topics/machine-learning/detail")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "machine-learning"
        assert "summaries" in data
        assert "files" in data

    def test_returns_404_for_missing_topic(self, client):
        resp = client.get("/api/kb/topics/nonexistent/detail")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_files_include_size_and_type(self, client):
        resp = client.get("/api/kb/topics/machine-learning/detail")
        data = resp.get_json()
        for f in data["files"]:
            assert "size" in f
            assert "type" in f

    def test_related_topics_present(self, client):
        resp = client.get("/api/kb/topics/machine-learning/detail")
        data = resp.get_json()
        assert "related_topics" in data
        assert isinstance(data["related_topics"], list)


# ── API Tests: GET /api/kb/topics/<name>/summary ─────────────────────

class TestTopicSummaryEndpoint:
    def test_returns_latest_summary(self, client):
        resp = client.get("/api/kb/topics/machine-learning/summary?version=latest")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["version"] == 2
        assert "content" in data

    def test_returns_specific_version(self, client):
        resp = client.get("/api/kb/topics/machine-learning/summary?version=1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["version"] == 1

    def test_defaults_to_latest(self, client):
        resp = client.get("/api/kb/topics/machine-learning/summary")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["version"] == 2

    def test_returns_404_for_missing_topic(self, client):
        resp = client.get("/api/kb/topics/nonexistent/summary")
        assert resp.status_code == 404

    def test_returns_404_for_missing_version(self, client):
        resp = client.get("/api/kb/topics/machine-learning/summary?version=99")
        assert resp.status_code == 404

    def test_returns_404_when_no_summaries(self, client_empty):
        resp = client_empty.get("/api/kb/topics/empty-topic/summary")
        assert resp.status_code == 404


# ── Edge Case Tests ───────────────────────────────────────────────────

class TestEdgeCases:
    def test_topic_name_with_special_chars(self, temp_project_dir):
        """Topics with hyphens and underscores work."""
        kb = Path(temp_project_dir) / "x-ipe-docs" / "knowledge-base"
        topic = "my-special_topic"
        (kb / "topics" / topic / "raw").mkdir(parents=True)
        (kb / "processed" / topic).mkdir(parents=True)
        (kb / "topics" / topic / "metadata.json").write_text(json.dumps({
            "name": topic, "description": "", "file_count": 0,
            "last_updated": "2026-02-05T10:00:00Z", "tags": []
        }))
        (kb / "landing").mkdir(parents=True, exist_ok=True)
        (kb / "index").mkdir(parents=True, exist_ok=True)
        (kb / "index" / "file-index.json").write_text(json.dumps({
            "version": "1.0", "last_updated": "2026-02-05T15:00:00Z", "files": []
        }))
        svc = KBService(temp_project_dir)
        detail = svc.get_topic_detail(topic)
        assert detail is not None
        assert detail["name"] == topic

    def test_summary_content_preserved_exactly(self, kb_service):
        result = kb_service.get_summary_content("machine-learning", "2")
        assert result["content"].startswith("# Topic: machine-learning")

    def test_empty_raw_dir(self, temp_project_dir, kb_empty_topic):
        svc = KBService(temp_project_dir)
        detail = svc.get_topic_detail("empty-topic")
        assert detail["files"] == []
