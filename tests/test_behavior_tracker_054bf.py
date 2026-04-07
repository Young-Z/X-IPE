"""
EPIC-054 / CR-001: Behavior Tracker Tests
- BehaviorTrackerSkill tests (polling model, folder management)
- InjectionManager tests (new scripts)
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / '.github' / 'skills' / 'x-ipe-tool-learning-behavior-tracker-for-web' / 'scripts'))

from track_behavior import BehaviorTrackerSkill, InjectionManager, _fix_double_encoded_utf8


class TestBehaviorTrackerSkill:
    """CR-001: Skill orchestrator with polling model tests."""

    def test_session_id_generated(self):
        skill = BehaviorTrackerSkill('https://example.com')
        assert skill.session_id
        assert len(skill.session_id) > 0

    def test_session_metadata(self):
        skill = BehaviorTrackerSkill('https://example.com/path', purpose='Test')
        skill.mark_started()
        meta = skill.get_session_metadata()
        assert meta['domain'] == 'example.com'
        assert meta['purpose'] == 'Test'
        assert meta['startedAt'] is not None

    def test_setup_output_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill = BehaviorTrackerSkill('https://example.com')
            result = skill.setup_output_folder(tmpdir, 'test-learning')
            assert os.path.isdir(os.path.join(tmpdir, 'x-ipe-docs', 'learning', 'test-learning', 'track'))
            assert os.path.isdir(os.path.join(tmpdir, 'x-ipe-docs', 'learning', 'test-learning', 'imgs'))
            assert 'test-learning' in result

    def test_get_track_list_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill = BehaviorTrackerSkill('https://example.com')
            skill.setup_output_folder(tmpdir, 'my-session')
            path = skill.get_track_list_path()
            assert path.endswith('track-list.json')
            assert 'my-session' in path

    def test_get_screenshot_path_increments(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill = BehaviorTrackerSkill('https://example.com')
            skill.setup_output_folder(tmpdir, 'test')
            p1 = skill.get_screenshot_path()
            p2 = skill.get_screenshot_path()
            assert '001' in p1
            assert '002' in p2
            assert p1 != p2

    def test_process_poll_result_new_events(self):
        skill = BehaviorTrackerSkill('https://example.com')
        result = skill.process_poll_result({
            'events': [{'type': 'click'}],
            'eventCount': 1,
            'url': 'https://example.com',
            'analysisRequested': False
        })
        assert result['new_events'] is True
        assert result['event_count'] == 1

    def test_process_poll_result_no_new_events(self):
        skill = BehaviorTrackerSkill('https://example.com')
        skill._last_event_count = 5
        result = skill.process_poll_result({
            'events': [], 'eventCount': 5, 'url': 'https://example.com'
        })
        assert result['new_events'] is False

    def test_process_poll_result_url_change(self):
        skill = BehaviorTrackerSkill('https://example.com/page1')
        result = skill.process_poll_result({
            'events': [], 'eventCount': 0, 'url': 'https://example.com/page2'
        })
        assert result['url_changed'] is True
        assert result['current_url'] == 'https://example.com/page2'

    def test_process_poll_result_analysis_flag(self):
        skill = BehaviorTrackerSkill('https://example.com')
        result = skill.process_poll_result({
            'events': [], 'eventCount': 0, 'url': 'https://example.com',
            'analysisRequested': True
        })
        assert result['analysis_requested'] is True

    def test_write_track_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill = BehaviorTrackerSkill('https://example.com', purpose='Test')
            skill.setup_output_folder(tmpdir, 'test-session')
            skill.mark_started()
            events = [{'type': 'click', 'timestamp': 1000}]
            path = skill.write_track_list(events)
            assert os.path.exists(path)
            data = json.loads(Path(path).read_text())
            assert data['schema_version'] == '2.0'
            assert len(data['events']) == 1

    def test_process_poll_fixes_double_encoded_chinese(self):
        """Double-encoded UTF-8 Chinese text should be fixed during poll processing."""
        skill = BehaviorTrackerSkill('https://example.com')
        # Simulate double-encoded Chinese: "为了您" → UTF-8 bytes → Latin-1 chars
        garbled = '为了您'.encode('utf-8').decode('latin-1')
        result = skill.process_poll_result({
            'events': [{'type': 'click', 'target': {'textContent': garbled}}],
            'eventCount': 1,
            'url': 'https://example.com'
        })
        assert result['new_events'] is True
        assert skill._all_events[0]['target']['textContent'] == '为了您'

    def test_process_poll_preserves_ascii_text(self):
        """Pure ASCII text should pass through unchanged."""
        skill = BehaviorTrackerSkill('https://example.com')
        result = skill.process_poll_result({
            'events': [{'type': 'click', 'target': {'textContent': 'Buy Now'}}],
            'eventCount': 1,
            'url': 'https://example.com'
        })
        assert skill._all_events[0]['target']['textContent'] == 'Buy Now'

    def test_write_track_list_chinese_readable(self):
        """Chinese characters should be readable in written JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill = BehaviorTrackerSkill('https://example.com', purpose='测试')
            skill.setup_output_folder(tmpdir, 'chinese-test')
            skill.mark_started()
            events = [{'type': 'click', 'target': {'textContent': '创建子内容'}}]
            path = skill.write_track_list(events)
            content = Path(path).read_text(encoding='utf-8')
            assert '创建子内容' in content
            assert '测试' in content

    def test_write_output_legacy_compat(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill = BehaviorTrackerSkill('https://example.com', purpose='Test')
            skill.mark_started()
            events = [
                {'type': 'click', 'timestamp': 1000,
                 'metadata': {'pageUrl': 'https://example.com/'},
                 'target': {'cssSelector': 'button'}},
            ]
            output_path = skill.write_output(tmpdir, events)
            assert output_path is not None
            assert os.path.exists(output_path)


class TestInjectionManager:
    """CR-001: Injection script tests."""

    def test_build_injection_script_contains_config(self):
        mgr = InjectionManager('test-session', {'purpose': 'Test', 'pii_whitelist': [], 'buffer_capacity': 5000})
        script = mgr.build_injection_script()
        assert 'test-session' in script
        assert '5000' in script

    def test_build_collect_script(self):
        mgr = InjectionManager('test', {})
        script = mgr.build_collect_script()
        assert '__xipeBehaviorTracker' in script
        assert 'getAnalysisFlag' in script
        assert 'getStatus' in script

    def test_build_stop_script(self):
        mgr = InjectionManager('test', {})
        script = mgr.build_stop_script()
        assert 'stop' in script

    def test_build_start_script(self):
        mgr = InjectionManager('test', {})
        script = mgr.build_start_script()
        assert 'start' in script

    def test_build_clear_guard_script(self):
        mgr = InjectionManager('test', {})
        script = mgr.build_clear_guard_script()
        assert '__xipeBehaviorTrackerInjected' in script
        assert 'false' in script


class TestFixDoubleEncodedUtf8:
    """Tests for _fix_double_encoded_utf8 utility."""

    def test_fixes_chinese_text(self):
        garbled = '为了您'.encode('utf-8').decode('latin-1')
        assert _fix_double_encoded_utf8(garbled) == '为了您'

    def test_fixes_special_symbols(self):
        # ● (U+25CF) double-encoded
        garbled = '●'.encode('utf-8').decode('latin-1')
        assert _fix_double_encoded_utf8(garbled) == '●'

    def test_preserves_ascii(self):
        assert _fix_double_encoded_utf8('Hello World') == 'Hello World'

    def test_preserves_correct_unicode(self):
        # Already correct Unicode should remain unchanged if
        # it can't be interpreted as Latin-1 → UTF-8
        assert _fix_double_encoded_utf8('café') == 'café'

    def test_handles_nested_dict(self):
        data = {'target': {'textContent': '为了您'.encode('utf-8').decode('latin-1')}}
        fixed = _fix_double_encoded_utf8(data)
        assert fixed['target']['textContent'] == '为了您'

    def test_handles_list_of_events(self):
        garbled = '创建'.encode('utf-8').decode('latin-1')
        data = [{'target': {'textContent': garbled}}, {'target': {'textContent': 'ok'}}]
        fixed = _fix_double_encoded_utf8(data)
        assert fixed[0]['target']['textContent'] == '创建'
        assert fixed[1]['target']['textContent'] == 'ok'

    def test_handles_non_string_types(self):
        assert _fix_double_encoded_utf8(42) == 42
        assert _fix_double_encoded_utf8(None) is None
        assert _fix_double_encoded_utf8(True) is True
