"""
FEATURE-022-D: Feedback Storage & Submission Tests

TDD tests for backend API and service.
"""
import pytest
import json
import base64
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestUiuxFeedbackService:
    """Tests for UiuxFeedbackService"""
    
    def test_save_feedback_creates_folder(self, tmp_path):
        """Service should create feedback folder"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        
        service = UiuxFeedbackService(str(tmp_path))
        data = {
            'name': 'Feedback-20260128-120000',
            'url': 'http://localhost:3000',
            'elements': ['button.submit'],
            'description': 'Test feedback'
        }
        
        result = service.save_feedback(data)
        
        assert result['success']
        folder = tmp_path / 'x-ipe-docs' / 'uiux-feedback' / 'Feedback-20260128-120000'
        assert folder.exists()
    
    def test_save_feedback_md_content(self, tmp_path):
        """Feedback.md should contain structured content"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        
        service = UiuxFeedbackService(str(tmp_path))
        data = {
            'name': 'Feedback-20260128-120000',
            'url': 'http://localhost:3000/dashboard',
            'elements': ['button.submit', 'div.form-group'],
            'description': 'The submit button is hard to find'
        }
        
        service.save_feedback(data)
        
        feedback_md = tmp_path / 'x-ipe-docs' / 'uiux-feedback' / 'Feedback-20260128-120000' / 'feedback.md'
        content = feedback_md.read_text()
        
        assert '**ID:** Feedback-20260128-120000' in content
        assert '**URL:** http://localhost:3000/dashboard' in content
        assert '- `button.submit`' in content
        assert '- `div.form-group`' in content
        assert 'The submit button is hard to find' in content
    
    def test_save_screenshot_decodes_base64(self, tmp_path):
        """Service should decode and save screenshot as PNG"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        
        # Create minimal valid PNG (1x1 transparent)
        png_bytes = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # RGBA
            0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,  # compressed data
            0x05, 0x00, 0x01, 0xAD, 0x0E, 0x14, 0x00, 0x00,  # 
            0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42,  # IEND chunk
            0x60, 0x82
        ])
        base64_data = f"data:image/png;base64,{base64.b64encode(png_bytes).decode()}"
        
        service = UiuxFeedbackService(str(tmp_path))
        data = {
            'name': 'Feedback-20260128-120000',
            'url': 'http://localhost:3000',
            'elements': ['button.submit'],
            'screenshot': base64_data
        }
        
        service.save_feedback(data)
        
        screenshot = tmp_path / 'x-ipe-docs' / 'uiux-feedback' / 'Feedback-20260128-120000' / 'page-screenshot.png'
        assert screenshot.exists()
        assert screenshot.read_bytes()[:4] == b'\x89PNG'
    
    def test_unique_folder_name_appends_suffix(self, tmp_path):
        """Duplicate folder names should get -1, -2 suffix"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        
        service = UiuxFeedbackService(str(tmp_path))
        
        # Create first entry
        data = {
            'name': 'Feedback-Test',
            'url': 'http://localhost:3000',
            'elements': ['button.submit']
        }
        result1 = service.save_feedback(data)
        
        # Create second with same name
        result2 = service.save_feedback(data)
        
        # Create third
        result3 = service.save_feedback(data)
        
        assert result1['name'] == 'Feedback-Test'
        assert result2['name'] == 'Feedback-Test-1'
        assert result3['name'] == 'Feedback-Test-2'
    
    def test_save_without_screenshot(self, tmp_path):
        """Should save feedback even without screenshot"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        
        service = UiuxFeedbackService(str(tmp_path))
        data = {
            'name': 'Feedback-NoScreenshot',
            'url': 'http://localhost:3000',
            'elements': ['button.submit'],
            'screenshot': None
        }
        
        result = service.save_feedback(data)
        
        assert result['success']
        folder = tmp_path / 'x-ipe-docs' / 'uiux-feedback' / 'Feedback-NoScreenshot'
        assert (folder / 'feedback.md').exists()
        assert not (folder / 'page-screenshot.png').exists()
    
    def test_save_with_empty_description(self, tmp_path):
        """Should save with empty description using placeholder"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        
        service = UiuxFeedbackService(str(tmp_path))
        data = {
            'name': 'Feedback-NoDesc',
            'url': 'http://localhost:3000',
            'elements': ['button.submit'],
            'description': ''
        }
        
        result = service.save_feedback(data)
        
        assert result['success']
        feedback_md = tmp_path / 'x-ipe-docs' / 'uiux-feedback' / 'Feedback-NoDesc' / 'feedback.md'
        content = feedback_md.read_text()
        assert '_No description provided_' in content
    
    def test_feedback_md_includes_screenshot_reference(self, tmp_path):
        """Feedback.md should include screenshot reference when present"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        
        service = UiuxFeedbackService(str(tmp_path))
        data = {
            'name': 'Feedback-WithScreenshot',
            'url': 'http://localhost:3000',
            'elements': ['button.submit'],
            'screenshot': 'data:image/png;base64,aGVsbG8='  # Will fail to save but flag is set
        }
        
        service.save_feedback(data)
        
        feedback_md = tmp_path / 'x-ipe-docs' / 'uiux-feedback' / 'Feedback-WithScreenshot' / 'feedback.md'
        content = feedback_md.read_text()
        assert '![Screenshot](./page-screenshot.png)' in content
    
    def test_returns_relative_folder_path(self, tmp_path):
        """Result should include relative folder path"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        
        service = UiuxFeedbackService(str(tmp_path))
        data = {
            'name': 'Feedback-RelPath',
            'url': 'http://localhost:3000',
            'elements': ['button.submit']
        }
        
        result = service.save_feedback(data)
        
        assert result['folder'] == 'x-ipe-docs/uiux-feedback/Feedback-RelPath'


class TestUiuxFeedbackRoutes:
    """Tests for API routes"""
    
    @pytest.fixture
    def client(self, tmp_path):
        """Create test client with temp project root"""
        from x_ipe.app import create_app
        
        app = create_app()
        app.config['TESTING'] = True
        app.config['PROJECT_ROOT'] = str(tmp_path)
        
        with app.test_client() as client:
            yield client
    
    def test_submit_feedback_success(self, client, tmp_path):
        """POST should return 201 on success"""
        response = client.post('/api/uiux-feedback',
            data=json.dumps({
                'name': 'Feedback-Success',
                'url': 'http://localhost:3000',
                'elements': ['button.submit'],
                'description': 'Test feedback'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success']
        assert 'folder' in data
    
    def test_submit_feedback_missing_name(self, client):
        """POST should return 400 if name missing"""
        response = client.post('/api/uiux-feedback',
            data=json.dumps({
                'url': 'http://localhost:3000',
                'elements': ['button.submit']
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert not data['success']
        assert 'name' in data['error'].lower()
    
    def test_submit_feedback_missing_url(self, client):
        """POST should return 400 if url missing"""
        response = client.post('/api/uiux-feedback',
            data=json.dumps({
                'name': 'Feedback-NoUrl',
                'elements': ['button.submit']
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert not data['success']
        assert 'url' in data['error'].lower()
    
    def test_submit_feedback_missing_elements(self, client):
        """POST should return 400 if elements missing"""
        response = client.post('/api/uiux-feedback',
            data=json.dumps({
                'name': 'Feedback-NoElements',
                'url': 'http://localhost:3000'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert not data['success']
        assert 'elements' in data['error'].lower()
    
    def test_submit_feedback_invalid_json(self, client):
        """POST should return 400 for invalid JSON"""
        response = client.post('/api/uiux-feedback',
            data='not valid json',
            content_type='application/json'
        )
        
        # Flask returns 400 for invalid JSON
        assert response.status_code in [400, 415]
    
    def test_submit_feedback_empty_body(self, client):
        """POST should return 400 for empty body"""
        response = client.post('/api/uiux-feedback',
            data=json.dumps(None),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_submit_feedback_returns_folder_path(self, client, tmp_path):
        """Response should include folder path"""
        response = client.post('/api/uiux-feedback',
            data=json.dumps({
                'name': 'Feedback-FolderPath',
                'url': 'http://localhost:3000',
                'elements': ['button.submit']
            }),
            content_type='application/json'
        )
        
        data = response.get_json()
        assert 'folder' in data
        assert 'Feedback-FolderPath' in data['folder']


class TestFeedbackEntryStatus:
    """Tests for entry status management (frontend logic)"""
    
    def test_entry_status_draft_by_default(self):
        """New entry should have status 'draft'"""
        entry = {
            'id': 'fb-123',
            'name': 'Feedback-Test',
            'status': 'draft'
        }
        assert entry['status'] == 'draft'
    
    def test_entry_status_transitions(self):
        """Test valid status transitions"""
        valid_transitions = {
            'draft': ['submitting'],
            'submitting': ['submitted', 'failed'],
            'failed': ['submitting'],  # retry
            'submitted': []  # terminal state
        }
        
        for from_status, to_statuses in valid_transitions.items():
            for to_status in to_statuses:
                assert to_status in ['draft', 'submitting', 'submitted', 'failed']
    
    def test_status_values(self):
        """All status values should be valid"""
        valid_statuses = {'draft', 'submitting', 'submitted', 'failed'}
        
        for status in valid_statuses:
            entry = {'status': status}
            assert entry['status'] in valid_statuses


class TestTerminalCommandGeneration:
    """Tests for terminal command generation"""
    
    def test_command_format(self):
        """Command should follow expected format"""
        folder_path = 'x-ipe-docs/uiux-feedback/Feedback-20260128-120000'
        expected = f"Get uiux feedback, please visit feedback folder {folder_path} to get details."
        
        # Simulate command generation
        command = f"Get uiux feedback, please visit feedback folder {folder_path} to get details."
        
        assert command == expected
        assert folder_path in command
        assert command.startswith("Get uiux feedback")
    
    def test_command_not_executed(self):
        """Command should be typed but not executed (no newline at end)"""
        folder_path = 'x-ipe-docs/uiux-feedback/Feedback-Test'
        command = f"Get uiux feedback, please visit feedback folder {folder_path} to get details."
        
        # Command should not end with newline
        assert not command.endswith('\n')
        assert not command.endswith('\r')


class TestListFeedback:
    """Tests for listing feedback entries (TASK-237)"""
    
    def test_list_feedback_returns_recent_entries(self, tmp_path):
        """Should return feedback entries from last 2 days"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        from datetime import datetime, timedelta
        import os
        
        service = UiuxFeedbackService(str(tmp_path))
        
        # Create feedback entry
        data = {
            'name': 'Feedback-Recent',
            'url': 'http://localhost:3000',
            'elements': ['button.submit'],
            'description': 'Recent feedback'
        }
        service.save_feedback(data)
        
        # List feedback (within 2 days)
        entries = service.list_feedback(days=2)
        
        assert len(entries) == 1
        assert entries[0]['name'] == 'Feedback-Recent'
    
    def test_list_feedback_sorted_desc_by_time(self, tmp_path):
        """Feedback should be sorted descending by creation time"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        import time
        
        service = UiuxFeedbackService(str(tmp_path))
        
        # Create first entry
        service.save_feedback({
            'name': 'Feedback-First',
            'url': 'http://localhost:3000',
            'elements': ['button']
        })
        
        time.sleep(0.1)  # Small delay to ensure different timestamps
        
        # Create second entry
        service.save_feedback({
            'name': 'Feedback-Second',
            'url': 'http://localhost:3000',
            'elements': ['button']
        })
        
        entries = service.list_feedback(days=2)
        
        assert len(entries) == 2
        # Second (newer) should be first
        assert entries[0]['name'] == 'Feedback-Second'
        assert entries[1]['name'] == 'Feedback-First'
    
    def test_list_feedback_excludes_old_entries(self, tmp_path):
        """Entries older than specified days should not be listed"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        from datetime import datetime, timedelta
        import os
        
        service = UiuxFeedbackService(str(tmp_path))
        
        # Create feedback entry
        data = {
            'name': 'Feedback-Old',
            'url': 'http://localhost:3000',
            'elements': ['button.submit']
        }
        service.save_feedback(data)
        
        # Modify folder mtime to be 3 days old
        folder_path = tmp_path / 'x-ipe-docs' / 'uiux-feedback' / 'Feedback-Old'
        old_time = (datetime.now() - timedelta(days=3)).timestamp()
        os.utime(folder_path, (old_time, old_time))
        
        entries = service.list_feedback(days=2)
        
        assert len(entries) == 0
    
    def test_list_feedback_returns_entry_details(self, tmp_path):
        """Entries should include id, name, url, description, date"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        
        service = UiuxFeedbackService(str(tmp_path))
        
        service.save_feedback({
            'name': 'Feedback-Details',
            'url': 'http://localhost:3000/page',
            'elements': ['button.submit'],
            'description': 'Test description'
        })
        
        entries = service.list_feedback(days=2)
        
        assert len(entries) == 1
        entry = entries[0]
        assert 'id' in entry
        assert entry['name'] == 'Feedback-Details'
        assert entry['url'] == 'http://localhost:3000/page'
        assert entry['description'] == 'Test description'
        assert 'date' in entry


class TestCleanupOldFeedback:
    """Tests for cleaning up old feedback (TASK-237)"""
    
    def test_cleanup_removes_old_feedback(self, tmp_path):
        """Should delete feedback older than 1 week"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        from datetime import datetime, timedelta
        import os
        
        service = UiuxFeedbackService(str(tmp_path))
        
        # Create old feedback
        service.save_feedback({
            'name': 'Feedback-Old',
            'url': 'http://localhost:3000',
            'elements': ['button']
        })
        
        # Modify folder mtime to be 8 days old
        folder_path = tmp_path / 'x-ipe-docs' / 'uiux-feedback' / 'Feedback-Old'
        old_time = (datetime.now() - timedelta(days=8)).timestamp()
        os.utime(folder_path, (old_time, old_time))
        
        # Run cleanup (default 7 days)
        deleted = service.cleanup_old_feedback(days=7)
        
        assert deleted == 1
        assert not folder_path.exists()
    
    def test_cleanup_preserves_recent_feedback(self, tmp_path):
        """Should NOT delete feedback within the retention period"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        
        service = UiuxFeedbackService(str(tmp_path))
        
        # Create recent feedback
        service.save_feedback({
            'name': 'Feedback-Recent',
            'url': 'http://localhost:3000',
            'elements': ['button']
        })
        
        folder_path = tmp_path / 'x-ipe-docs' / 'uiux-feedback' / 'Feedback-Recent'
        
        # Run cleanup
        deleted = service.cleanup_old_feedback(days=7)
        
        assert deleted == 0
        assert folder_path.exists()
    
    def test_cleanup_returns_count_of_deleted(self, tmp_path):
        """Should return count of deleted folders"""
        from x_ipe.services.uiux_feedback_service import UiuxFeedbackService
        from datetime import datetime, timedelta
        import os
        
        service = UiuxFeedbackService(str(tmp_path))
        
        # Create 3 old feedback entries
        for i in range(3):
            service.save_feedback({
                'name': f'Feedback-Old-{i}',
                'url': 'http://localhost:3000',
                'elements': ['button']
            })
            folder = tmp_path / 'x-ipe-docs' / 'uiux-feedback' / f'Feedback-Old-{i}'
            old_time = (datetime.now() - timedelta(days=10)).timestamp()
            os.utime(folder, (old_time, old_time))
        
        # Create 1 recent
        service.save_feedback({
            'name': 'Feedback-Recent',
            'url': 'http://localhost:3000',
            'elements': ['button']
        })
        
        deleted = service.cleanup_old_feedback(days=7)
        
        assert deleted == 3


class TestListFeedbackRoute:
    """Tests for GET /api/uiux-feedback endpoint (TASK-237)"""
    
    @pytest.fixture
    def client(self, tmp_path):
        """Create test client with temp project root"""
        from x_ipe.app import create_app
        
        app = create_app()
        app.config['TESTING'] = True
        app.config['PROJECT_ROOT'] = str(tmp_path)
        
        with app.test_client() as client:
            yield client
    
    def test_get_feedback_returns_200(self, client, tmp_path):
        """GET should return 200 OK"""
        response = client.get('/api/uiux-feedback')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'entries' in data
    
    def test_get_feedback_returns_entries(self, client, tmp_path):
        """GET should return saved entries"""
        # Create a feedback entry
        client.post('/api/uiux-feedback',
            data=json.dumps({
                'name': 'Feedback-Test',
                'url': 'http://localhost:3000',
                'elements': ['button'],
                'description': 'Test'
            }),
            content_type='application/json'
        )
        
        response = client.get('/api/uiux-feedback')
        
        data = response.get_json()
        assert len(data['entries']) == 1
        assert data['entries'][0]['name'] == 'Feedback-Test'
