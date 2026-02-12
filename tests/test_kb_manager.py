"""
Tests for FEATURE-025-C: KB Manager Skill

Tests cover:
- LLMService: complete(), is_available()
- KBManagerService: classify(), execute_classification(), cancel_processing(),
  generate_summary(), search(), reorganize()
- File content reading: text, binary detection, encoding fallback, truncation
- API endpoints: POST /api/kb/process, /process/confirm, /process/cancel,
  GET /api/kb/search, POST /api/kb/reorganize
- Integration: classify → confirm → files moved + summaries generated
- Edge cases: LLM unavailable, invalid JSON, concurrent requests, session timeout
- Tracing: @x_ipe_tracing on all service methods

TDD: All tests should FAIL before implementation.
"""
import os
import json
import uuid
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import BytesIO


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
def temp_kb_dir(temp_project_dir):
    """Create temporary knowledge-base directory structure."""
    kb_path = Path(temp_project_dir) / 'x-ipe-docs' / 'knowledge-base'
    kb_path.mkdir(parents=True, exist_ok=True)
    (kb_path / 'landing').mkdir(exist_ok=True)
    (kb_path / 'topics').mkdir(exist_ok=True)
    (kb_path / 'processed').mkdir(exist_ok=True)
    (kb_path / 'index').mkdir(exist_ok=True)
    (kb_path / 'index' / 'file-index.json').write_text(json.dumps({
        "version": "1.0",
        "last_updated": "2026-02-12T07:00:00Z",
        "files": []
    }))
    return kb_path


@pytest.fixture
def kb_with_landing_files(temp_kb_dir):
    """Create KB with files in landing folder."""
    landing = temp_kb_dir / 'landing'
    (landing / 'api-guide.md').write_text('# API Guide\nREST API design patterns and best practices.')
    (landing / 'ml-notes.txt').write_text('Machine learning notes\nNeural networks and deep learning.')
    (landing / 'image.png').write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
    # Update index
    index = {
        "version": "1.0",
        "last_updated": "2026-02-12T07:00:00Z",
        "files": [
            {"name": "api-guide.md", "path": "landing/api-guide.md", "type": "document", "size": 55},
            {"name": "ml-notes.txt", "path": "landing/ml-notes.txt", "type": "document", "size": 55},
            {"name": "image.png", "path": "landing/image.png", "type": "image", "size": 108}
        ]
    }
    (temp_kb_dir / 'index' / 'file-index.json').write_text(json.dumps(index))
    return temp_kb_dir


@pytest.fixture
def kb_with_topics(temp_kb_dir):
    """Create KB with existing topics."""
    topics = temp_kb_dir / 'topics'
    api_topic = topics / 'api-design' / 'raw'
    api_topic.mkdir(parents=True, exist_ok=True)
    (api_topic / 'existing.md').write_text('# Existing API doc')
    metadata = {"name": "api-design", "file_count": 1, "last_updated": "2026-02-12T07:00:00Z"}
    (topics / 'api-design' / 'metadata.json').write_text(json.dumps(metadata))
    return temp_kb_dir


@pytest.fixture
def mock_llm_response():
    """Mock LLM classification response."""
    return json.dumps([
        {"file": "api-guide.md", "topic": "api-design", "confidence": 0.92},
        {"file": "ml-notes.txt", "topic": "machine-learning", "confidence": 0.88}
    ])


@pytest.fixture
def mock_summary_response():
    """Mock LLM summary response."""
    return "## Key Concepts\n\n- REST API design patterns\n- Authentication strategies\n- Error handling best practices"


# ============================================================================
# LLMService Tests
# ============================================================================

class TestLLMServiceAvailability:
    """Tests for LLMService.is_available()."""

    def test_is_available_with_api_key(self):
        from x_ipe.services.llm_service import LLMService
        service = LLMService(api_key="test-key")
        assert service.is_available() is True

    def test_is_not_available_without_api_key(self):
        from x_ipe.services.llm_service import LLMService
        with patch.dict(os.environ, {}, clear=True):
            service = LLMService(api_key=None)
            assert service.is_available() is False

    def test_uses_env_var_when_no_key_provided(self):
        from x_ipe.services.llm_service import LLMService
        with patch.dict(os.environ, {'DASHSCOPE_API_KEY': 'env-key'}):
            service = LLMService()
            assert service.is_available() is True

    def test_default_model_is_qwen_turbo(self):
        from x_ipe.services.llm_service import LLMService
        service = LLMService(api_key="test")
        assert service.model == "qwen-turbo"

    def test_custom_model_override(self):
        from x_ipe.services.llm_service import LLMService
        service = LLMService(api_key="test", model="qwen-plus")
        assert service.model == "qwen-plus"


class TestLLMServiceComplete:
    """Tests for LLMService.complete()."""

    @patch('x_ipe.services.llm_service.Generation')
    def test_complete_returns_text(self, mock_gen):
        from x_ipe.services.llm_service import LLMService
        mock_gen.call.return_value = MagicMock(
            output=MagicMock(text="Hello world"),
            status_code=200
        )
        service = LLMService(api_key="test")
        result = service.complete("Say hello")
        assert result == "Hello world"

    @patch('x_ipe.services.llm_service.Generation')
    def test_complete_with_system_prompt(self, mock_gen):
        from x_ipe.services.llm_service import LLMService
        mock_gen.call.return_value = MagicMock(
            output=MagicMock(text="classified"),
            status_code=200
        )
        service = LLMService(api_key="test")
        result = service.complete("classify this", system="You are a classifier")
        assert result is not None
        # Verify system message was passed
        call_args = mock_gen.call.call_args
        messages = call_args[1].get('messages', []) if call_args[1] else []
        assert any(m.get('role') == 'system' for m in messages)

    @patch('x_ipe.services.llm_service.Generation')
    def test_complete_raises_on_api_error(self, mock_gen):
        from x_ipe.services.llm_service import LLMService
        mock_gen.call.return_value = MagicMock(status_code=400, message="Bad request")
        service = LLMService(api_key="test")
        with pytest.raises(RuntimeError):
            service.complete("bad prompt")

    def test_complete_without_api_key_raises(self):
        from x_ipe.services.llm_service import LLMService
        with patch.dict(os.environ, {}, clear=True):
            service = LLMService(api_key=None)
            with pytest.raises(RuntimeError):
                service.complete("hello")


# ============================================================================
# KBManagerService - Classification Tests
# ============================================================================

class TestKBManagerClassify:
    """Tests for KBManagerService.classify()."""

    def test_classify_returns_session_and_suggestions(self, kb_with_landing_files, mock_llm_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.return_value = mock_llm_response
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        result = manager.classify(["landing/api-guide.md", "landing/ml-notes.txt"])
        assert "session_id" in result
        assert "suggestions" in result
        assert len(result["suggestions"]) == 2

    def test_classify_suggestion_has_required_fields(self, kb_with_landing_files, mock_llm_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.return_value = mock_llm_response
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        result = manager.classify(["landing/api-guide.md"])
        suggestion = result["suggestions"][0]
        assert "file" in suggestion
        assert "suggested_topic" in suggestion or "topic" in suggestion
        assert "confidence" in suggestion

    def test_classify_fallback_to_uncategorized_when_llm_unavailable(self, kb_with_landing_files):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = False
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        result = manager.classify(["landing/api-guide.md"])
        assert all(
            s.get("suggested_topic", s.get("topic")) == "uncategorized"
            for s in result["suggestions"]
        )

    def test_classify_empty_paths_returns_empty(self, temp_kb_dir):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(temp_kb_dir.parent.parent))
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        result = manager.classify([])
        assert result["suggestions"] == []

    def test_classify_binary_file_classified_by_name(self, kb_with_landing_files, mock_llm_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.return_value = json.dumps([
            {"file": "image.png", "topic": "images", "confidence": 0.5}
        ])
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        result = manager.classify(["landing/image.png"])
        assert len(result["suggestions"]) == 1

    def test_classify_stores_pending_session(self, kb_with_landing_files, mock_llm_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.return_value = mock_llm_response
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        result = manager.classify(["landing/api-guide.md"])
        assert result["session_id"] in manager._pending_sessions

    def test_classify_rejects_concurrent_request(self, kb_with_landing_files, mock_llm_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.return_value = mock_llm_response
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        # First classify creates a pending session
        manager.classify(["landing/api-guide.md"])
        # Second should raise or return conflict
        with pytest.raises(ValueError):
            manager.classify(["landing/ml-notes.txt"])


# ============================================================================
# KBManagerService - Execute Classification Tests
# ============================================================================

class TestKBManagerExecuteClassification:
    """Tests for KBManagerService.execute_classification()."""

    def test_execute_moves_files_to_topics(self, kb_with_landing_files, mock_llm_response, mock_summary_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.side_effect = [mock_llm_response, mock_summary_response, mock_summary_response]
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        classify_result = manager.classify(["landing/api-guide.md", "landing/ml-notes.txt"])
        classifications = [
            {"path": "landing/api-guide.md", "topic": "api-design"},
            {"path": "landing/ml-notes.txt", "topic": "machine-learning"}
        ]
        result = manager.execute_classification(classify_result["session_id"], classifications)

        assert len(result["moved"]) == 2
        # Verify file moved
        assert (kb_with_landing_files / 'topics' / 'api-design' / 'raw' / 'api-guide.md').exists()
        assert not (kb_with_landing_files / 'landing' / 'api-guide.md').exists()

    def test_execute_creates_topic_folder(self, kb_with_landing_files, mock_llm_response, mock_summary_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.side_effect = [mock_llm_response, mock_summary_response]
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        classify_result = manager.classify(["landing/api-guide.md"])
        manager.execute_classification(classify_result["session_id"], [
            {"path": "landing/api-guide.md", "topic": "new-topic"}
        ])
        assert (kb_with_landing_files / 'topics' / 'new-topic' / 'raw').is_dir()

    def test_execute_generates_summaries(self, kb_with_landing_files, mock_llm_response, mock_summary_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.side_effect = [mock_llm_response, mock_summary_response]
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        classify_result = manager.classify(["landing/api-guide.md"])
        result = manager.execute_classification(classify_result["session_id"], [
            {"path": "landing/api-guide.md", "topic": "api-design"}
        ])
        assert "summaries_generated" in result
        summary_path = kb_with_landing_files / 'processed' / 'api-design' / 'summary-v1.md'
        assert summary_path.exists()

    def test_execute_invalid_session_raises(self, temp_kb_dir):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(temp_kb_dir.parent.parent))
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        with pytest.raises(KeyError):
            manager.execute_classification("nonexistent-session", [])

    def test_execute_handles_deleted_file_gracefully(self, kb_with_landing_files, mock_llm_response, mock_summary_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.side_effect = [mock_llm_response, mock_summary_response]
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        classify_result = manager.classify(["landing/api-guide.md"])
        # Delete file before confirm
        (kb_with_landing_files / 'landing' / 'api-guide.md').unlink()

        result = manager.execute_classification(classify_result["session_id"], [
            {"path": "landing/api-guide.md", "topic": "api-design"}
        ])
        assert len(result["errors"]) >= 1

    def test_execute_duplicate_filename_appends_suffix(self, kb_with_topics, mock_llm_response, mock_summary_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        # Add a file to landing with same name as existing topic file
        landing = kb_with_topics / 'landing'
        landing.mkdir(exist_ok=True)
        (landing / 'existing.md').write_text('# New existing doc')

        kb = KBService(str(kb_with_topics.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.side_effect = [
            json.dumps([{"file": "existing.md", "topic": "api-design", "confidence": 0.9}]),
            mock_summary_response
        ]
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        classify_result = manager.classify(["landing/existing.md"])
        result = manager.execute_classification(classify_result["session_id"], [
            {"path": "landing/existing.md", "topic": "api-design"}
        ])
        # Should have moved with suffix
        assert len(result["moved"]) == 1
        moved_file = result["moved"][0]
        assert "existing-1.md" in moved_file.get("to", moved_file.get("file", ""))

    def test_execute_updates_metadata(self, kb_with_landing_files, mock_llm_response, mock_summary_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.side_effect = [mock_llm_response, mock_summary_response]
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        classify_result = manager.classify(["landing/api-guide.md"])
        manager.execute_classification(classify_result["session_id"], [
            {"path": "landing/api-guide.md", "topic": "api-design"}
        ])
        metadata_path = kb_with_landing_files / 'topics' / 'api-design' / 'metadata.json'
        assert metadata_path.exists()
        metadata = json.loads(metadata_path.read_text())
        assert metadata["file_count"] >= 1


# ============================================================================
# KBManagerService - Cancel Tests
# ============================================================================

class TestKBManagerCancel:
    """Tests for KBManagerService.cancel_processing()."""

    def test_cancel_removes_session(self, kb_with_landing_files, mock_llm_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.return_value = mock_llm_response
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        result = manager.classify(["landing/api-guide.md"])
        cancel_result = manager.cancel_processing(result["session_id"])
        assert cancel_result["status"] == "cancelled"
        assert result["session_id"] not in manager._pending_sessions

    def test_cancel_invalid_session_raises(self, temp_kb_dir):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(temp_kb_dir.parent.parent))
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        with pytest.raises(KeyError):
            manager.cancel_processing("nonexistent")


# ============================================================================
# KBManagerService - Summary Generation Tests
# ============================================================================

class TestKBManagerSummary:
    """Tests for KBManagerService.generate_summary()."""

    def test_generate_summary_creates_versioned_file(self, kb_with_topics, mock_summary_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_topics.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.return_value = mock_summary_response
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        result = manager.generate_summary("api-design")
        assert "path" in result or "summary_path" in result
        summary_path = kb_with_topics / 'processed' / 'api-design' / 'summary-v1.md'
        assert summary_path.exists()

    def test_generate_summary_increments_version(self, kb_with_topics, mock_summary_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        # Create existing v1 summary
        processed = kb_with_topics / 'processed' / 'api-design'
        processed.mkdir(parents=True, exist_ok=True)
        (processed / 'summary-v1.md').write_text('# Old summary')

        kb = KBService(str(kb_with_topics.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.return_value = mock_summary_response
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        result = manager.generate_summary("api-design")
        v2_path = kb_with_topics / 'processed' / 'api-design' / 'summary-v2.md'
        assert v2_path.exists()
        # v1 preserved
        assert (processed / 'summary-v1.md').exists()

    def test_generate_summary_skipped_when_llm_unavailable(self, kb_with_topics):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_topics.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = False
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        result = manager.generate_summary("api-design")
        assert result.get("skipped") or result.get("error")


# ============================================================================
# KBManagerService - Search Tests
# ============================================================================

class TestKBManagerSearch:
    """Tests for KBManagerService.search()."""

    def test_search_returns_matching_files(self, kb_with_landing_files):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        results = manager.search("api")
        assert len(results) >= 1
        assert any("api" in r["name"].lower() for r in results)

    def test_search_case_insensitive(self, kb_with_landing_files):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        results_lower = manager.search("api")
        results_upper = manager.search("API")
        assert len(results_lower) == len(results_upper)

    def test_search_no_results(self, kb_with_landing_files):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        results = manager.search("nonexistent-xyz-123")
        assert len(results) == 0

    def test_search_empty_query(self, kb_with_landing_files):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        results = manager.search("")
        assert isinstance(results, list)


# ============================================================================
# KBManagerService - File Content Reading Tests
# ============================================================================

class TestKBManagerFileReading:
    """Tests for KBManagerService._read_file_content()."""

    def test_read_text_file(self, kb_with_landing_files):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        content = manager._read_file_content(
            str(kb_with_landing_files / 'landing' / 'api-guide.md')
        )
        assert "API Guide" in content

    def test_read_binary_file_returns_marker(self, kb_with_landing_files):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        content = manager._read_file_content(
            str(kb_with_landing_files / 'landing' / 'image.png')
        )
        assert "[Binary file" in content or content == ""

    def test_read_large_file_truncates(self, temp_kb_dir):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        # Create a file >1MB
        large_file = temp_kb_dir / 'landing' / 'large.txt'
        large_file.write_text('x' * (1024 * 1024 + 100))

        kb = KBService(str(temp_kb_dir.parent.parent))
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        content = manager._read_file_content(str(large_file))
        assert len(content) <= 1024 * 1024 + 50  # Allow small overhead for truncation note

    def test_read_nonexistent_file(self, temp_kb_dir):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(temp_kb_dir.parent.parent))
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        content = manager._read_file_content(str(temp_kb_dir / 'nonexistent.md'))
        assert content == "" or content is None


# ============================================================================
# KBManagerService - LLM Response Parsing Tests
# ============================================================================

class TestKBManagerResponseParsing:
    """Tests for KBManagerService._parse_classification_response()."""

    def test_parse_valid_json(self):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = MagicMock(spec=KBService)
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        response = '[{"file": "test.md", "topic": "testing", "confidence": 0.9}]'
        result = manager._parse_classification_response(response)
        assert len(result) == 1
        assert result[0]["topic"] == "testing"

    def test_parse_json_with_markdown_wrapper(self):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = MagicMock(spec=KBService)
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        response = '```json\n[{"file": "test.md", "topic": "testing", "confidence": 0.9}]\n```'
        result = manager._parse_classification_response(response)
        assert len(result) == 1

    def test_parse_invalid_json_returns_empty(self):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = MagicMock(spec=KBService)
        llm = MagicMock(spec=LLMService)
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        result = manager._parse_classification_response("not json at all")
        assert result == [] or result is None


# ============================================================================
# API Endpoint Tests
# ============================================================================

class TestKBProcessEndpoint:
    """Tests for POST /api/kb/process."""

    @pytest.fixture
    def app(self, kb_with_landing_files):
        from x_ipe.app import create_app
        app = create_app()
        app.config['TESTING'] = True
        app.config['KB_PROJECT_ROOT'] = str(kb_with_landing_files.parent.parent)
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_process_endpoint_exists(self, client):
        response = client.post('/api/kb/process',
                               json={"paths": ["landing/test.md"]})
        assert response.status_code != 404

    def test_process_returns_suggestions(self, client):
        response = client.post('/api/kb/process',
                               json={"paths": ["landing/api-guide.md"]})
        assert response.status_code == 200
        data = response.get_json()
        assert "suggestions" in data
        assert "session_id" in data

    def test_process_empty_paths_returns_400(self, client):
        response = client.post('/api/kb/process', json={"paths": []})
        assert response.status_code == 400

    def test_process_no_paths_returns_400(self, client):
        response = client.post('/api/kb/process', json={})
        assert response.status_code == 400


class TestKBProcessConfirmEndpoint:
    """Tests for POST /api/kb/process/confirm."""

    @pytest.fixture
    def app(self, kb_with_landing_files):
        from x_ipe.app import create_app
        app = create_app()
        app.config['TESTING'] = True
        app.config['KB_PROJECT_ROOT'] = str(kb_with_landing_files.parent.parent)
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_confirm_endpoint_exists(self, client):
        response = client.post('/api/kb/process/confirm',
                               json={"session_id": "test", "classifications": []})
        # Endpoint returns 404 for invalid session, but with JSON body
        data = response.get_json()
        assert data is not None
        assert "error" in data

    def test_confirm_invalid_session_returns_404(self, client):
        response = client.post('/api/kb/process/confirm',
                               json={"session_id": "nonexistent", "classifications": []})
        # Endpoint must exist (not generic 404) and return 404 for invalid session
        assert response.status_code == 404
        data = response.get_json()
        assert data is not None
        assert "error" in data


class TestKBProcessCancelEndpoint:
    """Tests for POST /api/kb/process/cancel."""

    @pytest.fixture
    def app(self, kb_with_landing_files):
        from x_ipe.app import create_app
        app = create_app()
        app.config['TESTING'] = True
        app.config['KB_PROJECT_ROOT'] = str(kb_with_landing_files.parent.parent)
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_cancel_endpoint_exists(self, client):
        response = client.post('/api/kb/process/cancel',
                               json={"session_id": "test"})
        # Endpoint returns 404 for invalid session, but with JSON body
        data = response.get_json()
        assert data is not None
        assert "error" in data


class TestKBSearchEndpoint:
    """Tests for GET /api/kb/search."""

    @pytest.fixture
    def app(self, kb_with_landing_files):
        from x_ipe.app import create_app
        app = create_app()
        app.config['TESTING'] = True
        app.config['KB_PROJECT_ROOT'] = str(kb_with_landing_files.parent.parent)
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_search_endpoint_exists(self, client):
        response = client.get('/api/kb/search?q=test')
        assert response.status_code != 404

    def test_search_returns_results(self, client):
        response = client.get('/api/kb/search?q=api')
        assert response.status_code == 200
        data = response.get_json()
        assert "results" in data
        assert "total" in data

    def test_search_missing_query_returns_400(self, client):
        response = client.get('/api/kb/search')
        assert response.status_code == 400


class TestKBReorganizeEndpoint:
    """Tests for POST /api/kb/reorganize."""

    @pytest.fixture
    def app(self, kb_with_landing_files):
        from x_ipe.app import create_app
        app = create_app()
        app.config['TESTING'] = True
        app.config['KB_PROJECT_ROOT'] = str(kb_with_landing_files.parent.parent)
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_reorganize_endpoint_exists(self, client):
        response = client.post('/api/kb/reorganize', json={})
        assert response.status_code != 404


# ============================================================================
# Tracing Tests
# ============================================================================

class TestKBManagerTracing:
    """Tests for @x_ipe_tracing decorator on KBManagerService methods."""

    def test_classify_has_tracing(self):
        from x_ipe.services.kb_manager_service import KBManagerService
        assert hasattr(KBManagerService.classify, '__wrapped__') or \
               hasattr(KBManagerService.classify, '_x_ipe_traced')

    def test_execute_classification_has_tracing(self):
        from x_ipe.services.kb_manager_service import KBManagerService
        assert hasattr(KBManagerService.execute_classification, '__wrapped__') or \
               hasattr(KBManagerService.execute_classification, '_x_ipe_traced')

    def test_search_has_tracing(self):
        from x_ipe.services.kb_manager_service import KBManagerService
        assert hasattr(KBManagerService.search, '__wrapped__') or \
               hasattr(KBManagerService.search, '_x_ipe_traced')

    def test_llm_complete_has_tracing(self):
        from x_ipe.services.llm_service import LLMService
        assert hasattr(LLMService.complete, '__wrapped__') or \
               hasattr(LLMService.complete, '_x_ipe_traced')


# ============================================================================
# Integration Tests
# ============================================================================

class TestKBManagerIntegration:
    """End-to-end integration tests."""

    def test_full_classify_confirm_flow(self, kb_with_landing_files, mock_llm_response, mock_summary_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.side_effect = [mock_llm_response, mock_summary_response]
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        # Classify
        classify_result = manager.classify(["landing/api-guide.md"])
        assert classify_result["session_id"]

        # Confirm
        result = manager.execute_classification(classify_result["session_id"], [
            {"path": "landing/api-guide.md", "topic": "api-design"}
        ])
        assert len(result["moved"]) == 1
        assert (kb_with_landing_files / 'topics' / 'api-design' / 'raw' / 'api-guide.md').exists()

    def test_classify_cancel_flow(self, kb_with_landing_files, mock_llm_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        llm.complete.return_value = mock_llm_response
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        classify_result = manager.classify(["landing/api-guide.md"])
        cancel_result = manager.cancel_processing(classify_result["session_id"])
        assert cancel_result["status"] == "cancelled"
        # File should still be in landing
        assert (kb_with_landing_files / 'landing' / 'api-guide.md').exists()

    def test_summary_classification_failure_still_moves_files(self, kb_with_landing_files, mock_llm_response):
        from x_ipe.services.kb_manager_service import KBManagerService
        from x_ipe.services.kb_service import KBService
        from x_ipe.services.llm_service import LLMService

        kb = KBService(str(kb_with_landing_files.parent.parent))
        llm = MagicMock(spec=LLMService)
        llm.is_available.return_value = True
        # First call returns classification, second call (summary) fails
        llm.complete.side_effect = [mock_llm_response, Exception("LLM error")]
        manager = KBManagerService(kb_service=kb, llm_service=llm)

        classify_result = manager.classify(["landing/api-guide.md"])
        result = manager.execute_classification(classify_result["session_id"], [
            {"path": "landing/api-guide.md", "topic": "api-design"}
        ])
        # File should still be moved even if summary fails
        assert len(result["moved"]) >= 1
        assert (kb_with_landing_files / 'topics' / 'api-design' / 'raw' / 'api-guide.md').exists()
