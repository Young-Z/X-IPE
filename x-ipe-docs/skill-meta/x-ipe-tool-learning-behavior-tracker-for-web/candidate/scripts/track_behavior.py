"""
EPIC-054 / CR-001: Behavior Tracker Skill (Script-Centric Architecture)

BehaviorTrackerSkill — Session orchestrator with 5s polling loop.
InjectionManager — Script injection and reinjection on URL change.

The skill script controls everything via Chrome DevTools MCP:
- Polls every 5s to collect events and detect changes
- Takes screenshots when new events are detected
- Detects URL changes and reinjects tracker
- Manages x-ipe-docs/learning/{name}/ folder structure
- Triggers LLM post-processing only when user clicks Analysis button
"""
import json
import uuid
import os
from pathlib import Path
from datetime import datetime, timezone


class InjectionManager:
    """Manages script injection into target pages via Chrome DevTools MCP."""

    def __init__(self, session_id, config):
        self.session_id = session_id
        self.config = config
        self._iife_source = None

    def _load_iife(self):
        if self._iife_source is None:
            iife_path = Path(__file__).parent.parent / 'references' / 'tracker-toolbar.mini.js'
            if not iife_path.exists():
                iife_path = Path(__file__).parent.parent / 'references' / 'tracker-toolbar.js'
            self._iife_source = iife_path.read_text(encoding='utf-8')

    def build_injection_script(self):
        """Build the IIFE injection script with embedded session config."""
        self._load_iife()
        config_json = json.dumps({
            'sessionId': self.session_id,
            'purpose': self.config.get('purpose', ''),
            'piiWhitelist': self.config.get('pii_whitelist', []),
            'bufferCapacity': self.config.get('buffer_capacity', 10000)
        })
        return f"(function() {{ var __xipeConfig = {config_json};\n{self._iife_source}\n}})();"

    def build_collect_script(self):
        """Build script to collect events and metadata from the page."""
        return """(() => {
            if (!window.__xipeBehaviorTracker) return JSON.stringify({events:[],eventCount:0,url:location.href,error:'not_injected'});
            const d = window.__xipeBehaviorTracker.collect();
            d.analysisRequested = window.__xipeBehaviorTracker.getAnalysisFlag();
            d.status = window.__xipeBehaviorTracker.getStatus();
            return JSON.stringify(d);
        })();"""

    def build_stop_script(self):
        """Build script to stop recording and return events."""
        return """(() => {
            if (!window.__xipeBehaviorTracker) return JSON.stringify({events:[],error:'not_injected'});
            window.__xipeBehaviorTracker.stop();
            return JSON.stringify(window.__xipeBehaviorTracker.collect());
        })();"""

    def build_start_script(self):
        """Build script to start recording."""
        return """(() => {
            if (window.__xipeBehaviorTracker) { window.__xipeBehaviorTracker.start(); return 'started'; }
            return 'not_injected';
        })();"""

    def build_clear_guard_script(self):
        """Clear the injection guard so tracker can be reinjected after URL change."""
        return "window.__xipeBehaviorTrackerInjected = false;"


class BehaviorTrackerSkill:
    """Main skill orchestrator for web behavior tracking.

    New architecture (CR-001): Script-centric with 5s polling.
    The skill script controls Chrome DevTools MCP. The IIFE is a passive event buffer.

    Usage by AI agent:
        1. skill.setup_output_folder(project_root, folder_name)
        2. navigate_page(url)
        3. evaluate_script(injection_manager.build_injection_script())
        4. POLLING LOOP (every 5s):
           a. evaluate_script(injection_manager.build_collect_script())
           b. if new events → take_screenshot → save to imgs/
           c. if url changed → clear guard → reinject → restore from localStorage
           d. if analysis_requested → run post_processor → write corrected events
           e. write track-list.json
        5. On stop: evaluate_script(injection_manager.build_stop_script())
    """

    def __init__(self, url, purpose='', pii_whitelist=None, buffer_capacity=10000):
        self.url = url
        self.purpose = purpose
        self.session_id = str(uuid.uuid4())
        self.config = {
            'purpose': purpose,
            'pii_whitelist': pii_whitelist or [],
            'buffer_capacity': buffer_capacity
        }
        self.started_at = None
        self.stopped_at = None
        self.injection_manager = InjectionManager(self.session_id, self.config)
        self._output_folder = None
        self._last_event_count = 0
        self._last_url = url
        self._screenshot_counter = 0
        self._all_events = []

    def setup_output_folder(self, project_root, folder_name):
        """Create x-ipe-docs/learning/{folder_name}/track/ and imgs/ folders."""
        base = Path(project_root) / 'x-ipe-docs' / 'learning' / folder_name
        track_dir = base / 'track'
        imgs_dir = base / 'imgs'
        track_dir.mkdir(parents=True, exist_ok=True)
        imgs_dir.mkdir(parents=True, exist_ok=True)
        self._output_folder = base
        return str(base)

    def get_track_list_path(self):
        """Return path to track-list.json."""
        if not self._output_folder:
            return None
        return str(self._output_folder / 'track' / 'track-list.json')

    def get_screenshot_path(self):
        """Return next screenshot path."""
        if not self._output_folder:
            return None
        self._screenshot_counter += 1
        ts = datetime.now(timezone.utc).strftime('%H%M%S')
        name = f'screenshot-{self._screenshot_counter:03d}-{ts}.png'
        return str(self._output_folder / 'imgs' / name)

    def process_poll_result(self, poll_data):
        """Process a poll result. Returns dict with actions to take.

        Args:
            poll_data: dict from evaluate_script(build_collect_script())

        Returns:
            dict with keys:
                new_events: bool — new events detected
                url_changed: bool — URL changed, needs reinjection
                analysis_requested: bool — user clicked Analysis button
                event_count: int — current total events
                current_url: str — current page URL
        """
        events = poll_data.get('events', [])
        event_count = poll_data.get('eventCount', len(events))
        current_url = poll_data.get('url', '')
        analysis_requested = poll_data.get('analysisRequested', False)

        new_events = event_count > self._last_event_count
        url_changed = current_url and current_url != self._last_url

        if new_events:
            self._all_events = events
            self._last_event_count = event_count

        if url_changed:
            self._last_url = current_url

        return {
            'new_events': new_events,
            'url_changed': url_changed,
            'analysis_requested': analysis_requested,
            'event_count': event_count,
            'current_url': current_url
        }

    def write_track_list(self, events=None):
        """Write events to track-list.json."""
        if not self._output_folder:
            return None

        if events is None:
            events = self._all_events

        output = {
            'schema_version': '2.0',
            'session': self.get_session_metadata(),
            'events': events,
            'event_count': len(events),
            'last_updated': datetime.now(timezone.utc).isoformat()
        }

        path = self._output_folder / 'track' / 'track-list.json'
        path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
        return str(path)

    def run_analysis(self, events=None):
        """Run post-processing analysis (triggered by Analysis button)."""
        if events is None:
            events = self._all_events

        try:
            from .post_processor import PostProcessor
        except ImportError:
            from post_processor import PostProcessor

        processor = PostProcessor()
        session_meta = self.get_session_metadata()

        try:
            result = processor.process(events, session_meta)
            status = 'completed'
        except Exception:
            try:
                result = processor.process(events, session_meta)
                status = 'completed'
            except Exception:
                result = {
                    'statistics': processor.compute_statistics(events),
                    'analysis': {
                        'flow_narrative': 'Post-processing failed.',
                        'key_paths': [], 'pain_points': [],
                        'ai_annotations': []
                    }
                }
                status = 'failed'

        # Write analysis output alongside track-list
        if self._output_folder:
            analysis_output = {
                'schema_version': '2.0',
                'session': session_meta,
                'statistics': result['statistics'],
                'events': events,
                'analysis': result['analysis'],
                'post_processing_status': status
            }
            path = self._output_folder / 'track' / 'analysis.json'
            path.write_text(json.dumps(analysis_output, indent=2, ensure_ascii=False), encoding='utf-8')

        return result

    def get_session_metadata(self):
        """Return session metadata."""
        from urllib.parse import urlparse
        parsed = urlparse(self.url)
        return {
            'id': self.session_id,
            'domain': parsed.hostname or 'unknown',
            'purpose': self.purpose,
            'startedAt': self.started_at,
            'stoppedAt': self.stopped_at,
            'piiWhitelist': self.config['pii_whitelist'],
            'bufferCapacity': self.config['buffer_capacity']
        }

    def mark_started(self):
        self.started_at = datetime.now(timezone.utc).isoformat()

    def mark_stopped(self):
        self.stopped_at = datetime.now(timezone.utc).isoformat()

    # Legacy compat
    def write_output(self, project_root, events, analysis=None):
        """Legacy write method — redirects to new folder structure."""
        if not self._output_folder:
            self.setup_output_folder(project_root, f'session-{self.session_id[:8]}')
        self.mark_stopped()
        self._all_events = events
        self.write_track_list(events)
        result = self.run_analysis(events)
        return self.get_track_list_path()

