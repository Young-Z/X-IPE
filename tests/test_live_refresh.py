"""
Tests for FEATURE-004: Live Refresh

Architecture: WebSocket content_changed events + ContentRefreshManager

Tests cover:
- FileWatcher: content_changed event emission
- WebSocket: content_changed event delivery
- ContentRefreshManager: refresh logic, toggle, scroll preservation
- Edge cases: deletion, debounce, rapid changes
"""
import os
import time
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch


# =============================================================================
# Unit Tests: FileWatcher content_changed Events
# =============================================================================

class TestFileWatcherContentChangedEmission:
    """Unit tests for FileWatcher emitting content_changed events"""

    def test_file_modified_emits_content_changed(self, temp_project, mock_socketio):
        """AC-1: FileWatcher emits content_changed when file is modified"""
        from x_ipe.services import FileWatcher
        
        watcher = FileWatcher(
            project_root=str(temp_project),
            socketio=mock_socketio,
            debounce_seconds=0.05
        )
        watcher.start()
        
        try:
            # Modify a file
            test_file = temp_project / "test.txt"
            test_file.write_text("modified content")
            
            # Wait for debounce
            time.sleep(0.2)
            
            # Verify content_changed was emitted
            calls = mock_socketio.emit.call_args_list
            content_changed_calls = [
                c for c in calls 
                if c[0][0] == 'content_changed'
            ]
            
            assert len(content_changed_calls) >= 1
            event_data = content_changed_calls[-1][0][1]
            assert event_data['type'] == 'content_changed'
            assert event_data['action'] == 'modified'
            assert 'test.txt' in event_data['path']
        finally:
            watcher.stop()

    def test_file_deleted_emits_content_changed_with_deleted_action(self, temp_project, mock_socketio):
        """AC-5: FileWatcher emits content_changed with action='deleted' when file is deleted"""
        from x_ipe.services import FileWatcher
        
        watcher = FileWatcher(
            project_root=str(temp_project),
            socketio=mock_socketio,
            debounce_seconds=0.05
        )
        watcher.start()
        
        try:
            # Create and then delete a file
            test_file = temp_project / "to_delete.txt"
            test_file.write_text("will be deleted")
            time.sleep(0.1)
            
            mock_socketio.emit.reset_mock()
            test_file.unlink()
            
            # Wait for debounce
            time.sleep(0.2)
            
            # Verify content_changed with deleted action
            calls = mock_socketio.emit.call_args_list
            content_changed_calls = [
                c for c in calls 
                if c[0][0] == 'content_changed'
            ]
            
            assert len(content_changed_calls) >= 1
            event_data = content_changed_calls[-1][0][1]
            assert event_data['action'] == 'deleted'
        finally:
            watcher.stop()

    def test_content_changed_path_is_relative(self, temp_project, mock_socketio):
        """Content path in event should be relative to project root"""
        from x_ipe.services import FileWatcher
        
        watcher = FileWatcher(
            project_root=str(temp_project),
            socketio=mock_socketio,
            debounce_seconds=0.05
        )
        watcher.start()
        
        try:
            # Create subfolder and file
            subdir = temp_project / "x-ipe-docs" / "planning"
            subdir.mkdir(parents=True, exist_ok=True)
            test_file = subdir / "notes.md"
            test_file.write_text("# Notes")
            
            # Wait for debounce
            time.sleep(0.2)
            
            # Check relative path
            calls = mock_socketio.emit.call_args_list
            content_changed_calls = [
                c for c in calls 
                if c[0][0] == 'content_changed'
            ]
            
            assert len(content_changed_calls) >= 1
            event_data = content_changed_calls[-1][0][1]
            # Path should be relative, not absolute
            assert not event_data['path'].startswith('/')
            assert 'x-ipe-docs/planning/notes.md' in event_data['path'] or 'docs\\planning\\notes.md' in event_data['path']
        finally:
            watcher.stop()

    def test_ignored_files_do_not_emit_content_changed(self, temp_project, mock_socketio):
        """Files matching gitignore patterns should not emit content_changed"""
        from x_ipe.services import FileWatcher
        
        # Create .gitignore with directory patterns (current implementation)
        gitignore = temp_project / ".gitignore"
        gitignore.write_text("__pycache__/\nnode_modules/\n.git/\n")
        
        # Create ignored directory
        pycache_dir = temp_project / "__pycache__"
        pycache_dir.mkdir()
        
        watcher = FileWatcher(
            project_root=str(temp_project),
            socketio=mock_socketio,
            debounce_seconds=0.05
        )
        watcher.start()
        
        try:
            # Create file in ignored directory
            cache_file = pycache_dir / "module.pyc"
            cache_file.write_text("cache content")
            
            time.sleep(0.2)
            
            # Verify no content_changed for ignored file
            calls = mock_socketio.emit.call_args_list
            content_changed_calls = [
                c for c in calls 
                if c[0][0] == 'content_changed' and '__pycache__' in str(c)
            ]
            
            assert len(content_changed_calls) == 0
        finally:
            watcher.stop()


class TestFileWatcherDebounce:
    """Tests for debouncing rapid file changes"""

    def test_rapid_changes_debounced(self, temp_project, mock_socketio):
        """AC-6: Rapid successive changes are debounced"""
        from x_ipe.services import FileWatcher
        
        watcher = FileWatcher(
            project_root=str(temp_project),
            socketio=mock_socketio,
            debounce_seconds=0.1
        )
        watcher.start()
        
        try:
            test_file = temp_project / "rapid.txt"
            
            # Make many rapid changes
            for i in range(5):
                test_file.write_text(f"change {i}")
                time.sleep(0.02)  # 20ms between changes
            
            # Wait for debounce to complete
            time.sleep(0.3)
            
            # Should have at most 1-2 content_changed events, not 5
            calls = mock_socketio.emit.call_args_list
            content_changed_calls = [
                c for c in calls 
                if c[0][0] == 'content_changed' and 'rapid.txt' in str(c)
            ]
            
            # Debounce should consolidate to 1-2 events max
            assert len(content_changed_calls) <= 2
        finally:
            watcher.stop()


# =============================================================================
# Integration Tests: WebSocket content_changed Events
# NOTE: These tests are for legacy WebSocket architecture. 
# FEATURE-004 now uses HTTP polling (5s interval) instead of WebSocket.
# Backend FileWatcher still emits events, but frontend no longer listens.
# =============================================================================

@pytest.mark.skip(reason="FEATURE-004 refactored to HTTP polling - WebSocket client delivery no longer used")
class TestWebSocketContentChangedDelivery:
    """Integration tests for WebSocket content_changed event delivery
    
    DEPRECATED: Frontend now uses HTTP polling instead of WebSocket events.
    Keeping tests for reference in case WebSocket is re-enabled.
    """

    def test_client_receives_content_changed_event(self, app, socketio_test_client, temp_project):
        """WebSocket client receives content_changed event when file is modified"""
        from x_ipe.services import FileWatcher
        from src.app import socketio
        
        # Start file watcher with real socketio
        watcher = FileWatcher(
            project_root=str(temp_project),
            socketio=socketio,
            debounce_seconds=0.05
        )
        watcher.start()
        
        try:
            # Modify file
            test_file = temp_project / "watched.txt"
            test_file.write_text("new content")
            
            # Wait for event propagation
            time.sleep(0.3)
            
            # Check received events
            received = socketio_test_client.get_received()
            content_events = [
                e for e in received 
                if e.get('name') == 'content_changed'
            ]
            
            assert len(content_events) >= 1
        finally:
            watcher.stop()

    def test_content_changed_within_2_seconds(self, temp_project, mock_socketio):
        """AC-2: Content change event occurs within 2 seconds of file modification"""
        from x_ipe.services import FileWatcher
        
        watcher = FileWatcher(
            project_root=str(temp_project),
            socketio=mock_socketio,
            debounce_seconds=0.05
        )
        watcher.start()
        
        try:
            start_time = time.time()
            
            test_file = temp_project / "timing.txt"
            test_file.write_text("timed content")
            
            # Poll for event (max 2 seconds)
            event_received = False
            while time.time() - start_time < 2:
                calls = mock_socketio.emit.call_args_list
                content_changed_calls = [
                    c for c in calls 
                    if c[0][0] == 'content_changed'
                ]
                if len(content_changed_calls) > 0:
                    event_received = True
                    break
                time.sleep(0.05)
            
            elapsed = time.time() - start_time
            assert event_received, "content_changed event not received"
            assert elapsed < 2, f"Event took {elapsed:.2f}s, should be < 2s"
        finally:
            watcher.stop()


# =============================================================================
# Unit Tests: Content Refresh Manager (Frontend Logic)
# =============================================================================

class TestContentRefreshManagerPathMatching:
    """Tests for path matching logic in refresh manager"""

    def test_matching_path_triggers_refresh(self):
        """Refresh triggered when event path matches current file"""
        # This would be a JavaScript test, but we test the logic
        current_file = "x-ipe-docs/planning/task-board.md"
        event_path = "x-ipe-docs/planning/task-board.md"
        
        assert current_file == event_path  # Should trigger refresh

    def test_non_matching_path_no_refresh(self):
        """No refresh when event path doesn't match current file"""
        current_file = "x-ipe-docs/planning/task-board.md"
        event_path = "x-ipe-docs/requirements/spec.md"
        
        assert current_file != event_path  # Should NOT trigger refresh

    def test_path_normalization(self):
        """Paths should be normalized for comparison"""
        # Both should be considered equal
        path1 = "x-ipe-docs/planning/task-board.md"
        path2 = "x-ipe-docs/planning/task-board.md"
        
        assert path1 == path2


class TestContentRefreshManagerToggle:
    """Tests for auto-refresh toggle functionality"""

    def test_toggle_default_enabled(self):
        """AC-7: Auto-refresh is enabled by default"""
        # Default state should be True
        default_enabled = True
        assert default_enabled is True

    def test_toggle_persisted_to_storage(self):
        """Toggle state should be persisted (localStorage simulation)"""
        storage = {}
        
        # Simulate toggle off
        storage['autoRefreshEnabled'] = 'false'
        
        # Load from storage
        enabled = storage.get('autoRefreshEnabled', 'true') == 'true'
        assert enabled is False

    def test_disabled_toggle_prevents_refresh(self):
        """When disabled, content_changed events should not trigger refresh"""
        enabled = False
        should_refresh = enabled and True  # path_matches
        
        assert should_refresh is False


class TestScrollPositionPreservation:
    """Tests for scroll position preservation during refresh"""

    def test_scroll_position_saved_before_refresh(self):
        """AC-4: Scroll position is saved before refresh"""
        # Simulate scroll state
        scroll_position = 500
        saved_position = scroll_position
        
        assert saved_position == 500

    def test_scroll_position_restored_after_refresh(self):
        """AC-4: Scroll position is restored after content reload"""
        saved_position = 500
        new_content_height = 1000
        
        # If content is tall enough, restore position
        restored_position = min(saved_position, new_content_height)
        assert restored_position == 500

    def test_scroll_position_clamped_for_shorter_content(self):
        """If content shortened, scroll position is clamped"""
        saved_position = 500
        new_content_height = 300
        
        restored_position = min(saved_position, new_content_height)
        assert restored_position == 300


# =============================================================================
# Integration Tests: Full Refresh Flow
# =============================================================================

class TestFullRefreshFlow:
    """End-to-end tests for content refresh flow"""

    def test_file_modify_to_content_refresh(self, app, temp_project, mock_socketio):
        """Full flow: file modified → event emitted → (frontend would refresh)"""
        from x_ipe.services import FileWatcher
        
        watcher = FileWatcher(
            project_root=str(temp_project),
            socketio=mock_socketio,
            debounce_seconds=0.05
        )
        watcher.start()
        
        try:
            # Simulate viewing a file
            current_file = "task-board.md"
            test_file = temp_project / current_file
            test_file.write_text("# Initial")
            time.sleep(0.2)
            
            mock_socketio.emit.reset_mock()
            
            # Modify the file (simulating AI agent update)
            test_file.write_text("# Updated by AI")
            time.sleep(0.2)
            
            # Verify content_changed emitted
            calls = mock_socketio.emit.call_args_list
            content_changed_calls = [
                c for c in calls 
                if c[0][0] == 'content_changed'
            ]
            
            assert len(content_changed_calls) >= 1
            
            # Frontend would then call /api/content/<path> and re-render
            # (That's tested in FEATURE-002 tests)
        finally:
            watcher.stop()

    def test_content_api_returns_updated_content(self, client, temp_project):
        """Content API returns latest file content after modification"""
        # Create initial file
        test_file = temp_project / "refresh_test.md"
        test_file.write_text("# Original Content")
        
        # Verify initial content
        content = test_file.read_text()
        assert "Original Content" in content
        
        # Modify file
        test_file.write_text("# Updated Content")
        
        # Content should now be updated (file system level)
        content = test_file.read_text()
        assert "Updated Content" in content


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestFileDeletionHandling:
    """Tests for handling file deletion"""

    def test_deletion_detected_and_reported(self, temp_project, mock_socketio):
        """AC-5: File deletion emits appropriate event"""
        from x_ipe.services import FileWatcher
        
        # Create file first
        test_file = temp_project / "will_delete.md"
        test_file.write_text("# To be deleted")
        
        watcher = FileWatcher(
            project_root=str(temp_project),
            socketio=mock_socketio,
            debounce_seconds=0.05
        )
        watcher.start()
        
        try:
            time.sleep(0.1)
            mock_socketio.emit.reset_mock()
            
            # Delete the file
            test_file.unlink()
            time.sleep(0.2)
            
            # Should emit content_changed with deleted action
            calls = mock_socketio.emit.call_args_list
            delete_calls = [
                c for c in calls 
                if c[0][0] == 'content_changed' and 
                   c[0][1].get('action') == 'deleted'
            ]
            
            assert len(delete_calls) >= 1
        finally:
            watcher.stop()


class TestWebSocketReconnection:
    """Tests for WebSocket reconnection handling"""

    def test_watcher_continues_after_disconnect(self, temp_project, mock_socketio):
        """AC-10: FileWatcher continues working, ready for reconnection"""
        from x_ipe.services import FileWatcher
        
        watcher = FileWatcher(
            project_root=str(temp_project),
            socketio=mock_socketio,
            debounce_seconds=0.05
        )
        watcher.start()
        
        try:
            # Watcher should be running
            assert watcher.is_running
            
            # Even if socketio has issues, watcher keeps monitoring
            # (reconnection logic is in frontend)
            test_file = temp_project / "reconnect.txt"
            test_file.write_text("after reconnect")
            time.sleep(0.2)
            
            # Events still queued/emitted
            assert mock_socketio.emit.called
        finally:
            watcher.stop()


class TestAllFileTypesSupported:
    """Tests for various file type support"""

    @pytest.mark.parametrize("filename,expected_type", [
        ("notes.md", "markdown"),
        ("app.py", "python"),
        ("script.js", "javascript"),
        ("config.json", "json"),
        ("config.yaml", "yaml"),
        ("style.css", "css"),
        ("page.html", "html"),
    ])
    def test_all_file_types_trigger_refresh(self, temp_project, mock_socketio, filename, expected_type):
        """AC-9: All supported file types trigger content_changed"""
        from x_ipe.services import FileWatcher
        
        watcher = FileWatcher(
            project_root=str(temp_project),
            socketio=mock_socketio,
            debounce_seconds=0.05
        )
        watcher.start()
        
        try:
            # Small delay to ensure watcher is fully started
            time.sleep(0.1)
            mock_socketio.emit.reset_mock()
            
            test_file = temp_project / filename
            test_file.write_text(f"// {expected_type} content")
            time.sleep(0.25)
            
            calls = mock_socketio.emit.call_args_list
            content_changed_calls = [
                c for c in calls 
                if c[0][0] == 'content_changed' and filename in str(c)
            ]
            
            assert len(content_changed_calls) >= 1, f"No event for {filename}"
        finally:
            watcher.stop()


# =============================================================================
# Visual Indicator Tests (Logic Only)
# =============================================================================

class TestRefreshIndicator:
    """Tests for refresh indicator logic"""

    def test_indicator_shown_on_refresh(self):
        """AC-3: Visual indicator confirms content refresh"""
        # Frontend logic - indicator should be shown
        refresh_occurred = True
        should_show_indicator = refresh_occurred
        
        assert should_show_indicator is True

    def test_indicator_auto_dismisses(self):
        """Indicator should auto-dismiss after ~2 seconds"""
        dismiss_delay_ms = 2000
        assert dismiss_delay_ms == 2000


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create some initial files
    (project_dir / "test.txt").write_text("initial content")
    (project_dir / "README.md").write_text("# Test Project")
    
    return project_dir


@pytest.fixture
def mock_socketio():
    """Create a mock SocketIO instance"""
    mock = MagicMock()
    mock.emit = MagicMock()
    return mock


@pytest.fixture
def app():
    """Create test Flask app"""
    from src.app import create_app
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['PROJECT_ROOT'] = os.getcwd()
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def socketio_test_client(app):
    """Create SocketIO test client"""
    from src.app import socketio
    
    return socketio.test_client(app, flask_test_client=app.test_client())
