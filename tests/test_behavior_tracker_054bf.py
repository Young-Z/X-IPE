"""
FEATURE-054-F: PostProcessor Tests
FEATURE-054-B: BehaviorTrackerSkill Tests
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / '.github' / 'skills' / 'x-ipe-learning-behavior-tracker-for-web' / 'scripts'))

from post_processor import PostProcessor
from track_behavior import BehaviorTrackerSkill, InjectionManager


class TestPostProcessor:
    """FEATURE-054-F: Post-processing tests."""

    def setup_method(self):
        self.processor = PostProcessor()

    def test_compute_statistics_empty(self):
        stats = self.processor.compute_statistics([])
        assert stats['totalEvents'] == 0
        assert stats['pageCount'] == 0

    def test_compute_statistics_with_events(self):
        events = [
            {'type': 'click', 'metadata': {'pageUrl': 'https://example.com/'}},
            {'type': 'click', 'metadata': {'pageUrl': 'https://example.com/'}},
            {'type': 'input', 'metadata': {'pageUrl': 'https://example.com/cart'}},
            {'type': 'scroll', 'metadata': {'pageUrl': 'https://example.com/cart'}},
        ]
        stats = self.processor.compute_statistics(events)
        assert stats['totalEvents'] == 4
        assert stats['byType']['click'] == 2
        assert stats['byType']['input'] == 1
        assert stats['pageCount'] == 2

    def test_process_returns_all_sections(self):
        events = [
            {'type': 'click', 'timestamp': 1000, 'metadata': {'pageUrl': 'https://example.com/'},
             'target': {'cssSelector': 'button.buy'}},
        ]
        session_meta = {'id': 'test-1', 'domain': 'example.com', 'purpose': 'Test'}
        result = self.processor.process(events, session_meta)
        assert 'statistics' in result
        assert 'analysis' in result
        assert 'flow_narrative' in result['analysis']
        assert 'key_paths' in result['analysis']
        assert 'pain_points' in result['analysis']
        assert 'key_path_summary' in result['analysis']
        assert 'ai_annotations' in result['analysis']
        # Verify annotation schema
        for ann in result['analysis']['ai_annotations']:
            assert 'comment' in ann
            assert 'is_key_path' in ann
            assert 'intent_category' in ann
            assert 'confidence' in ann

    def test_flow_narrative_includes_domain(self):
        events = [
            {'type': 'click', 'metadata': {'pageUrl': 'https://example.com/'}},
        ]
        result = self.processor.process(events, {'domain': 'example.com', 'purpose': ''})
        assert 'example.com' in result['analysis']['flow_narrative']

    def test_pain_points_long_pause(self):
        events = [
            {'type': 'click', 'timestamp': 1000},
            {'type': 'click', 'timestamp': 50000},  # 49s gap
        ]
        result = self.processor.process(events, {'domain': 'test.com', 'purpose': ''})
        pauses = [pp for pp in result['analysis']['pain_points'] if pp['type'] == 'long_pause']
        assert len(pauses) >= 1

    def test_pain_points_repeated_action(self):
        events = [
            {'type': 'click', 'timestamp': 1000, 'target': {'cssSelector': 'button.buy'}},
            {'type': 'click', 'timestamp': 2000, 'target': {'cssSelector': 'button.buy'}},
            {'type': 'click', 'timestamp': 3000, 'target': {'cssSelector': 'button.buy'}},
        ]
        result = self.processor.process(events, {'domain': 'test.com', 'purpose': ''})
        repeated = [pp for pp in result['analysis']['pain_points'] if pp['type'] == 'repeated_action']
        assert len(repeated) >= 1

    def test_empty_events(self):
        result = self.processor.process([], {'domain': 'test.com', 'purpose': ''})
        assert result['analysis']['flow_narrative'] == 'No events recorded.'
        assert result['analysis']['key_paths'] == []


class TestBehaviorTrackerSkill:
    """FEATURE-054-B: Skill orchestrator tests."""

    def test_session_id_generated(self):
        skill = BehaviorTrackerSkill('https://example.com')
        assert skill.session_id is not None
        assert len(skill.session_id) > 0

    def test_session_metadata(self):
        skill = BehaviorTrackerSkill('https://example.com/path', purpose='Test')
        skill.mark_started()
        meta = skill.get_session_metadata()
        assert meta['domain'] == 'example.com'
        assert meta['purpose'] == 'Test'
        assert meta['startedAt'] is not None

    def test_write_output_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill = BehaviorTrackerSkill('https://example.com', purpose='Test')
            skill.mark_started()
            events = [
                {'type': 'click', 'timestamp': 1000,
                 'metadata': {'pageUrl': 'https://example.com/'},
                 'target': {'cssSelector': 'button'}},
            ]
            output_path = skill.write_output(tmpdir, events)
            assert os.path.exists(output_path)
            data = json.loads(Path(output_path).read_text())
            assert data['schema_version'] == '1.0'
            assert data['session']['domain'] == 'example.com'
            assert len(data['events']) == 1
            assert 'pages' in data
            assert len(data['pages']) == 1
            assert data['pages'][0]['url'] == 'https://example.com/'


class TestInjectionManager:
    """FEATURE-054-B: Injection script tests."""

    def test_build_injection_script_contains_config(self):
        mgr = InjectionManager('test-session', {'purpose': 'Test', 'pii_whitelist': [], 'buffer_capacity': 5000})
        script = mgr.build_injection_script()
        assert 'test-session' in script
        assert '5000' in script

    def test_build_collect_script(self):
        mgr = InjectionManager('test', {})
        script = mgr.build_collect_script()
        assert '__xipeBehaviorTracker' in script

    def test_build_stop_script(self):
        mgr = InjectionManager('test', {})
        script = mgr.build_stop_script()
        assert 'stop' in script
