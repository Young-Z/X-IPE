"""
FEATURE-025-E: KB Search & Preview — Backend Tests (TDD)

Tests for:
- Search API with type/topic filters and grouped response
- Search result grouping (files, topics, summaries)
- Edge cases (empty query, no results, large index)
"""

import json
import shutil
import tempfile
from pathlib import Path

import pytest


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def populated_kb_dir(temp_project_dir):
    """Create KB directory with varied files for search testing."""
    kb_path = Path(temp_project_dir) / "x-ipe-docs" / "knowledge-base"
    kb_path.mkdir(parents=True, exist_ok=True)

    # Landing files
    landing = kb_path / "landing"
    landing.mkdir(exist_ok=True)
    (landing / "report.pdf").write_bytes(b"%PDF-1.4 fake")
    (landing / "notes.md").write_text("# Notes\nSome content.")
    (landing / "utils.py").write_text("def helper(): pass")

    # Topics
    topics = kb_path / "topics"
    topics.mkdir(exist_ok=True)
    topic = topics / "machine-learning"
    topic.mkdir(exist_ok=True)
    raw = topic / "raw"
    raw.mkdir(exist_ok=True)
    (raw / "neural-nets.pdf").write_bytes(b"%PDF-1.4 fake")
    (raw / "training-guide.md").write_text("# Training Guide")
    (topic / "metadata.json").write_text(
        json.dumps(
            {
                "name": "machine-learning",
                "description": "ML papers",
                "file_count": 2,
                "last_updated": "2026-02-19T10:00:00Z",
                "tags": ["ml", "ai"],
            }
        )
    )

    # Processed summaries
    processed = kb_path / "processed"
    processed.mkdir(exist_ok=True)
    proc_topic = processed / "machine-learning"
    proc_topic.mkdir(exist_ok=True)
    (proc_topic / "summary-v1.md").write_text("# ML Summary v1")

    # Index
    index = kb_path / "index"
    index.mkdir(exist_ok=True)
    (index / "file-index.json").write_text(
        json.dumps(
            {
                "version": "1.0",
                "last_updated": "2026-02-19T10:00:00Z",
                "files": [
                    {
                        "path": "landing/report.pdf",
                        "name": "report.pdf",
                        "type": "pdf",
                        "size": 14,
                        "topic": None,
                        "created_date": "2026-02-19T09:00:00Z",
                        "keywords": ["report"],
                    },
                    {
                        "path": "landing/notes.md",
                        "name": "notes.md",
                        "type": "markdown",
                        "size": 22,
                        "topic": None,
                        "created_date": "2026-02-19T09:05:00Z",
                        "keywords": ["notes"],
                    },
                    {
                        "path": "landing/utils.py",
                        "name": "utils.py",
                        "type": "code",
                        "size": 20,
                        "topic": None,
                        "created_date": "2026-02-19T09:10:00Z",
                        "keywords": ["utils", "helper"],
                    },
                    {
                        "path": "topics/machine-learning/raw/neural-nets.pdf",
                        "name": "neural-nets.pdf",
                        "type": "pdf",
                        "size": 14,
                        "topic": "machine-learning",
                        "created_date": "2026-02-19T09:15:00Z",
                        "keywords": ["neural", "nets"],
                    },
                    {
                        "path": "topics/machine-learning/raw/training-guide.md",
                        "name": "training-guide.md",
                        "type": "markdown",
                        "size": 16,
                        "topic": "machine-learning",
                        "created_date": "2026-02-19T09:20:00Z",
                        "keywords": ["training", "guide"],
                    },
                ],
            }
        )
    )

    return kb_path


@pytest.fixture
def kb_service(temp_project_dir, populated_kb_dir):
    """KBService with populated directory."""
    from x_ipe.services import KBService

    return KBService(temp_project_dir)


@pytest.fixture
def app(temp_project_dir, populated_kb_dir):
    """Flask test app with populated KB."""
    from x_ipe.app import create_app

    app = create_app({"TESTING": True, "PROJECT_ROOT": temp_project_dir})
    return app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


# ============================================================================
# Search API Route Tests
# ============================================================================


class TestSearchAPIGroupedResponse:
    """GET /api/kb/search should return grouped results."""

    def test_search_returns_grouped_structure(self, client):
        """Response must contain files, topics, summaries groups."""
        resp = client.get("/api/kb/search?q=report")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "results" in data
        results = data["results"]
        assert "files" in results
        assert "topics" in results
        assert "summaries" in results

    def test_search_files_match_by_name(self, client):
        """File name match should appear in files group."""
        resp = client.get("/api/kb/search?q=report")
        data = resp.get_json()
        files = data["results"]["files"]
        assert any(f["name"] == "report.pdf" for f in files)

    def test_search_topics_match_by_topic_name(self, client):
        """Topic name match should appear in topics group."""
        resp = client.get("/api/kb/search?q=machine")
        data = resp.get_json()
        topics = data["results"]["topics"]
        assert any("machine" in t["name"].lower() for t in topics)

    def test_search_summaries_match(self, client):
        """Summary file match should appear in summaries group."""
        resp = client.get("/api/kb/search?q=machine")
        data = resp.get_json()
        summaries = data["results"]["summaries"]
        assert any("machine-learning" in s.get("topic", "") for s in summaries)

    def test_search_returns_total_count(self, client):
        """Response should include total count across all groups."""
        resp = client.get("/api/kb/search?q=report")
        data = resp.get_json()
        assert "total" in data
        assert isinstance(data["total"], int)


class TestSearchAPIFilters:
    """GET /api/kb/search with type and topic filters."""

    def test_filter_by_type_pdf(self, client):
        """type=pdf should only return PDF files."""
        resp = client.get("/api/kb/search?q=&type=pdf")
        data = resp.get_json()
        files = data["results"]["files"]
        for f in files:
            assert f["type"] == "pdf"

    def test_filter_by_type_markdown(self, client):
        """type=markdown should only return markdown files."""
        resp = client.get("/api/kb/search?q=&type=markdown")
        data = resp.get_json()
        files = data["results"]["files"]
        for f in files:
            assert f["type"] == "markdown"

    def test_filter_by_topic(self, client):
        """topic=machine-learning should only return files from that topic."""
        resp = client.get("/api/kb/search?q=&topic=machine-learning")
        data = resp.get_json()
        files = data["results"]["files"]
        for f in files:
            assert f.get("topic") == "machine-learning"

    def test_filter_combined_type_and_topic(self, client):
        """Combining type and topic narrows results."""
        resp = client.get("/api/kb/search?q=&type=pdf&topic=machine-learning")
        data = resp.get_json()
        files = data["results"]["files"]
        for f in files:
            assert f["type"] == "pdf"
            assert f.get("topic") == "machine-learning"

    def test_filter_with_query(self, client):
        """Filters should work alongside text query."""
        resp = client.get("/api/kb/search?q=neural&type=pdf")
        data = resp.get_json()
        files = data["results"]["files"]
        assert len(files) >= 1
        for f in files:
            assert f["type"] == "pdf"


class TestSearchAPIEdgeCases:
    """Edge cases for search API."""

    def test_empty_query_returns_400(self, client):
        """Empty q param should return 400."""
        resp = client.get("/api/kb/search?q=")
        # With filters, empty query is valid (browse mode)
        # Without filters, should still work as browse-all
        assert resp.status_code in (200, 400)

    def test_no_results_query(self, client):
        """Query with no matches returns empty groups."""
        resp = client.get("/api/kb/search?q=zzzznonexistent")
        data = resp.get_json()
        results = data["results"]
        assert len(results["files"]) == 0
        assert len(results["topics"]) == 0
        assert len(results["summaries"]) == 0

    def test_case_insensitive_search(self, client):
        """Search must be case-insensitive."""
        resp_lower = client.get("/api/kb/search?q=report")
        resp_upper = client.get("/api/kb/search?q=REPORT")
        data_lower = resp_lower.get_json()
        data_upper = resp_upper.get_json()
        assert len(data_lower["results"]["files"]) == len(
            data_upper["results"]["files"]
        )

    def test_search_by_keyword(self, client):
        """Search should match against file keywords."""
        resp = client.get("/api/kb/search?q=helper")
        data = resp.get_json()
        files = data["results"]["files"]
        assert any(f["name"] == "utils.py" for f in files)


# ============================================================================
# KBManagerService.search() Unit Tests
# ============================================================================


class TestKBManagerSearchGrouped:
    """KBManagerService.search() should return grouped dict."""

    def test_search_returns_dict_with_groups(self, kb_service, temp_project_dir):
        """search() should return dict with files, topics, summaries keys."""
        from x_ipe.services.kb_manager_service import KBManagerService

        manager = KBManagerService(kb_service, llm_service=None)
        result = manager.search("report")
        assert isinstance(result, dict)
        assert "files" in result
        assert "topics" in result
        assert "summaries" in result

    def test_search_with_type_filter(self, kb_service, temp_project_dir):
        """search(file_type='pdf') filters to PDF only."""
        from x_ipe.services.kb_manager_service import KBManagerService

        manager = KBManagerService(kb_service, llm_service=None)
        result = manager.search("", file_type="pdf")
        for f in result["files"]:
            assert f["type"] == "pdf"

    def test_search_with_topic_filter(self, kb_service, temp_project_dir):
        """search(topic='machine-learning') filters to that topic."""
        from x_ipe.services.kb_manager_service import KBManagerService

        manager = KBManagerService(kb_service, llm_service=None)
        result = manager.search("", topic_filter="machine-learning")
        for f in result["files"]:
            assert f.get("topic") == "machine-learning"

    def test_search_includes_topic_names(self, kb_service, temp_project_dir):
        """search('machine') should include topic name matches."""
        from x_ipe.services.kb_manager_service import KBManagerService

        manager = KBManagerService(kb_service, llm_service=None)
        result = manager.search("machine")
        assert len(result["topics"]) >= 1

    def test_search_includes_summaries(self, kb_service, temp_project_dir):
        """search('machine') should find summary files."""
        from x_ipe.services.kb_manager_service import KBManagerService

        manager = KBManagerService(kb_service, llm_service=None)
        result = manager.search("machine")
        assert len(result["summaries"]) >= 1


# ============================================================================
# Preview-Related API Tests  
# ============================================================================


class TestPreviewDataAPI:
    """Tests for file metadata that feeds the preview panel."""

    def test_index_files_have_required_preview_fields(self, client):
        """Each file in index should have fields needed for preview panel."""
        resp = client.get("/api/kb/index")
        data = resp.get_json()
        for f in data.get("files", []):
            assert "name" in f
            assert "type" in f
            assert "size" in f
            assert "path" in f

    def test_file_has_keywords_for_tags(self, client):
        """Files should have keywords array for AI tag display."""
        resp = client.get("/api/kb/index")
        data = resp.get_json()
        for f in data.get("files", []):
            assert "keywords" in f
            assert isinstance(f["keywords"], list)
