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
import json
import subprocess
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
        
        test_file = temp_project / "to_delete.txt"
        test_file.write_text("will be deleted")
        watcher = FileWatcher(
            project_root=str(temp_project),
            socketio=mock_socketio,
            debounce_seconds=0.05
        )
        watcher.start()
        
        try:
            mock_socketio.emit.reset_mock()
            test_file.unlink()
            event_data = wait_for_emission(mock_socketio, 'content_changed', 'to_delete.txt', 'deleted')
            assert event_data == {
                'type': 'content_changed', 'path': 'to_delete.txt', 'action': 'deleted'
            }
            structure = wait_for_emission(mock_socketio, 'structure_changed', 'to_delete.txt', 'deleted')
            assert structure['path'] == event_data['path']
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
            assert 1 <= len(content_changed_calls) <= 2
        finally:
            watcher.stop()

    def test_transient_temp_file_does_not_emit_deleted_event(self, temp_project, mock_socketio):
        """Transient files added and deleted in one batch should be ignored."""
        from x_ipe.services.file_service import FileWatcherHandler
        from watchfiles import Change

        handler = FileWatcherHandler(
            callback=lambda event: mock_socketio.emit('content_changed', event),
            debounce_seconds=0.01,
            project_root=str(temp_project),
        )

        transient_file = temp_project / "draft.txt.tmp"
        handler.handle_changes({
            (Change.added, str(transient_file)),
            (Change.deleted, str(transient_file)),
        })
        time.sleep(0.05)

        delete_calls = [
            c for c in mock_socketio.emit.call_args_list
            if c[0][0] == 'content_changed' and c[0][1].get('action') == 'deleted'
        ]
        assert len(delete_calls) == 0


# =============================================================================
# Integration Tests: WebSocket content_changed Events
# The frontend now polls, but FileWatcher still publishes this backend contract.
# Actual Socket.IO delivery must be tested, not skipped because of the UI transport.
# =============================================================================

class TestWebSocketContentChangedDelivery:
    """Integration tests for WebSocket content_changed event delivery
    
    This verifies backend delivery, not a claim that the frontend subscribes.
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
            
            deadline = time.monotonic() + 2
            content_events = []
            while time.monotonic() < deadline and not content_events:
                received = socketio_test_client.get_received()
                content_events.extend(
                    e for e in received
                    if e.get('name') == 'content_changed'
                    and e['args'][0].get('path') == 'watched.txt'
                )
                if not content_events:
                    time.sleep(0.01)
            assert content_events, "Actual Socket.IO client never received the file event"
            assert content_events[-1]['args'][0] == {
                'type': 'content_changed', 'path': 'watched.txt', 'action': 'created'
            }
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
    """Execute the production polling manager in jsdom, not Python emulation."""

    def test_matching_path_triggers_refresh(self, refresh_runtime):
        """Refresh triggered when event path matches current file"""
        assert refresh_runtime['rendered_content'] == ['# Changed']

    def test_non_matching_path_no_refresh(self, refresh_runtime):
        """No refresh when event path doesn't match current file"""
        assert refresh_runtime['path_switch_fetches'] == 0
        assert refresh_runtime['path_switch_cache'] is None

    def test_path_normalization(self, refresh_runtime):
        """Paths should be normalized for comparison"""
        assert refresh_runtime['planning_unix'] is True
        assert refresh_runtime['planning_windows'] is True
        assert refresh_runtime['non_planning'] is False


class TestContentRefreshManagerToggle:
    """Tests for auto-refresh toggle functionality"""

    def test_toggle_default_enabled(self, refresh_runtime):
        """AC-7: Auto-refresh is enabled by default"""
        assert refresh_runtime['default_enabled'] is True

    def test_toggle_persisted_to_storage(self, refresh_runtime):
        """Toggle state should be persisted (localStorage simulation)"""
        assert refresh_runtime['stored_toggle'] == 'false'
        assert refresh_runtime['reloaded_enabled'] is False

    def test_disabled_toggle_prevents_refresh(self, refresh_runtime):
        """When disabled, content_changed events should not trigger refresh"""
        assert refresh_runtime['disabled_fetches'] == 0


class TestScrollPositionPreservation:
    """Tests for scroll position preservation during refresh"""

    def test_scroll_position_saved_before_refresh(self, refresh_runtime):
        """AC-4: Scroll position is saved before refresh"""
        assert refresh_runtime['saved_scroll'] == 500

    def test_scroll_position_restored_after_refresh(self, refresh_runtime):
        """AC-4: Scroll position is restored after content reload"""
        assert refresh_runtime['restored_scroll'] == 500

    def test_scroll_position_clamped_for_shorter_content(self, refresh_runtime):
        """If content shortened, scroll position is clamped"""
        assert refresh_runtime['clamped_scroll'] == 300


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
        
        response = client.get('/api/file/content', query_string={'path': 'refresh_test.md'})
        assert response.status_code == 200
        assert response.get_json()['content'] == '# Original Content'
        
        # Modify file
        test_file.write_text("# Updated Content")
        
        response = client.get('/api/file/content', query_string={'path': 'refresh_test.md'})
        assert response.status_code == 200
        assert response.get_json()['content'] == '# Updated Content'

    def test_deleted_file_api_reports_not_found(self, client, temp_project):
        """The polling endpoint must report deletion rather than return cached content."""
        file = temp_project / 'deleted.md'
        file.write_text('# Temporary')
        assert client.get('/api/file/content', query_string={'path': 'deleted.md'}).status_code == 200
        file.unlink()
        response = client.get('/api/file/content', query_string={'path': 'deleted.md'})
        assert response.status_code == 404
        assert response.get_json()['error'] == 'File not found'


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

    def test_indicator_shown_on_refresh(self, refresh_runtime):
        """AC-3: Visual indicator confirms content refresh"""
        assert refresh_runtime['indicator_text'].strip() == 'Content updated'

    def test_indicator_auto_dismisses(self, refresh_runtime):
        """Indicator should auto-dismiss after ~2 seconds"""
        assert refresh_runtime['indicator_delay_ms'] == 2500
        assert refresh_runtime['indicator_remaining'] == 0


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
def app(temp_project):
    """Create test Flask app"""
    from src.app import create_app
    
    return create_app({'TESTING': True, 'PROJECT_ROOT': str(temp_project)})


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def socketio_test_client(app):
    """Create SocketIO test client"""
    from src.app import socketio
    
    client = socketio.test_client(app, flask_test_client=app.test_client())
    yield client
    if client.is_connected():
        client.disconnect()


def wait_for_emission(socketio, name, path, action, timeout=2):
    """Await the exact producer event; unrelated emissions cannot satisfy this check."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for call in socketio.emit.call_args_list:
            if call.args[0] == name and call.args[1].get('path') == path and call.args[1].get('action') == action:
                return call.args[1]
        time.sleep(0.01)
    pytest.fail(f'No {name}({path}, {action}); received {socketio.emit.call_args_list}')


class TestFileWatcherProducerContracts:
    """Actual handler → FileWatcher → both Socket.IO event payloads.

    No OS scheduler or timer sleeps: flush the real debounce queue explicitly.
    Source: FEATURE-004 FR-1/FR-5/AC-6; transient files are not viewed deliverables.
    """

    @pytest.mark.parametrize('change_kinds', [('deleted',), ('added', 'deleted'), ('modified', 'deleted')])
    def test_known_file_delete_emits_both_events(self, temp_project, mock_socketio, change_kinds):
        from x_ipe.services.file_service import FileWatcher, FileWatcherHandler
        from watchfiles import Change

        file = temp_project / 'notes.md'
        file.write_text('# Existing')
        watcher = FileWatcher(str(temp_project), mock_socketio)
        handler = FileWatcherHandler(watcher._emit_event, project_root=str(temp_project))
        file.unlink()
        with patch.object(handler, '_schedule_callback'):
            handler.handle_changes({(getattr(Change, kind), str(file)) for kind in change_kinds})
        handler._emit_events()
        assert [call.args for call in mock_socketio.emit.call_args_list] == [
            ('structure_changed', {'type': 'structure_changed', 'path': 'notes.md', 'action': 'deleted'}),
            ('content_changed', {'type': 'content_changed', 'path': 'notes.md', 'action': 'deleted'}),
        ]
        handler._emit_events()
        assert mock_socketio.emit.call_count == 2

    def test_transient_and_ignored_changes_emit_neither_event(self, temp_project, mock_socketio):
        from x_ipe.services.file_service import FileWatcher, FileWatcherHandler
        from watchfiles import Change

        (temp_project / '.gitignore').write_text('__pycache__/\n')
        ignored = temp_project / '__pycache__' / 'cached.pyc'
        ignored.parent.mkdir()
        ignored.write_bytes(b'cache')
        watcher = FileWatcher(str(temp_project), mock_socketio)
        handler = FileWatcherHandler(watcher._emit_event, ignore_patterns=watcher.ignore_patterns,
                                     project_root=str(temp_project))
        ignored.unlink()
        transient = str(temp_project / 'draft.tmp')
        with patch.object(handler, '_schedule_callback'):
            handler.handle_changes({(Change.deleted, str(ignored)),
                                    (Change.added, transient), (Change.deleted, transient)})
        handler._emit_events()
        mock_socketio.emit.assert_not_called()

        # Positive control: prove the same handler/emitter is not inert.
        with patch.object(handler, '_schedule_callback'):
            handler.handle_changes({(Change.modified, str(temp_project / 'test.txt'))})
        handler._emit_events()
        assert mock_socketio.emit.call_args.args == (
            'content_changed', {'type': 'content_changed', 'path': 'test.txt', 'action': 'modified'}
        )


@pytest.fixture(scope='module')
def refresh_runtime():
    """Run the real browser module once in Node/jsdom for Python-facing checks.

    These are production-JS execution facts, not rendered-browser acceptance.
    Missing Node/jsdom fails rather than silently skipping frontend coverage.
    """
    root = Path(__file__).resolve().parents[1]
    script = r"""
import { JSDOM } from 'jsdom';
import { readFileSync } from 'node:fs';
const dom = new JSDOM('<div id="content-body"></div><div id="toast-container"></div><input id="auto-refresh-toggle" type="checkbox">',
    { url: 'http://localhost', runScripts: 'outside-only' });
const w = dom.window;
const timers = [];
w.setInterval = () => 0;
w.setTimeout = (callback, delay) => { timers.push({ callback, delay }); return timers.length; };
w.requestAnimationFrame = callback => callback();
let fetches = 0;
let content = '# Original';
w.fetch = async () => { fetches++; return { ok: true, json: async () => ({ content }) }; };
w.eval(readFileSync('src/x_ipe/static/js/features/live-refresh.js', 'utf8') +
    '\nglobalThis.RefreshManager = ContentRefreshManager; globalThis.Poller = PlanningFilePoller;');
const body = w.document.getElementById('content-body');
Object.defineProperties(body, { scrollHeight: { configurable: true, value: 1000 }, clientHeight: { value: 200 } });
const rendered = [];
const renderer = { currentPath: 'notes.md', container: body, render: data => { rendered.push(data.content); body.scrollTop = 0; } };
const manager = new w.RefreshManager({ contentRenderer: renderer });
const result = { default_enabled: manager.isEnabled() };
manager.setEnabled(false);
result.stored_toggle = w.localStorage.getItem('autoRefreshEnabled');
result.reloaded_enabled = new w.RefreshManager({ contentRenderer: renderer }).isEnabled();
await manager._checkForChanges();
result.disabled_fetches = fetches;
manager.setEnabled(true);
await manager._checkForChanges(); // path switch: reset tracking only
result.path_switch_fetches = fetches;
result.path_switch_cache = manager.lastContent;
await manager._checkForChanges(); // cache original
await manager._checkForChanges(); // unchanged: no render
content = '# Changed';
body.scrollTop = 500;
await manager._checkForChanges();
result.rendered_content = [...rendered];
result.saved_scroll = manager.scrollPosition;
result.restored_scroll = body.scrollTop;
result.indicator_text = w.document.querySelector('.refresh-toast').textContent;
result.indicator_delay_ms = timers.at(-1).delay;
Object.defineProperty(body, 'scrollHeight', { configurable: true, value: 500 });
body.scrollTop = 500;
manager._refreshContent({ content: '# Shorter' });
result.clamped_scroll = body.scrollTop;
for (const timer of timers) timer.callback();
result.indicator_remaining = w.document.querySelectorAll('.refresh-toast').length;
const poller = new w.Poller({ pollInterval: 5000 });
result.planning_unix = poller.isPlanningFile('x-ipe-docs/planning/task-board.md');
result.planning_windows = poller.isPlanningFile('x-ipe-docs\\planning\\features.md');
result.non_planning = poller.isPlanningFile('x-ipe-docs/requirements/spec.md');
dom.window.close();
console.log(JSON.stringify(result));
"""
    result = subprocess.run(['node', '--input-type=module'], input=script, cwd=root,
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)
