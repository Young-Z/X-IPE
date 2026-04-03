"""
FEATURE-054-B: Chrome DevTools Injection & Page Lifecycle
FEATURE-054-F: behavior-recording.json Output (orchestration)

BehaviorTrackerSkill — Main skill entry point.
InjectionManager — Script injection and page lifecycle management.
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

    def build_injection_script(self):
        """Build the IIFE injection script with embedded session config."""
        if self._iife_source is None:
            iife_path = Path(__file__).parent.parent / 'references' / 'tracker-toolbar.js'
            self._iife_source = iife_path.read_text(encoding='utf-8')

        config_json = json.dumps({
            'sessionId': self.session_id,
            'purpose': self.config.get('purpose', ''),
            'piiWhitelist': self.config.get('pii_whitelist', []),
            'bufferCapacity': self.config.get('buffer_capacity', 10000)
        })

        return f"(function() {{ var __xipeConfig = {config_json};\n{self._iife_source}\n}})();"

    def build_collect_script(self):
        """Build script to collect recorded events from the page."""
        return """
        (function() {
            if (window.__xipeBehaviorTracker) {
                return JSON.stringify(window.__xipeBehaviorTracker.collect());
            }
            return JSON.stringify({ events: [], error: 'Tracker not found' });
        })();
        """

    def build_stop_script(self):
        """Build script to stop recording and return events."""
        return """
        (function() {
            if (window.__xipeBehaviorTracker) {
                window.__xipeBehaviorTracker.stop();
                return JSON.stringify(window.__xipeBehaviorTracker.collect());
            }
            return JSON.stringify({ events: [], error: 'Tracker not found' });
        })();
        """


class BehaviorTrackerSkill:
    """Main skill orchestrator for web behavior tracking.

    Usage by AI agent:
        1. navigate_page(url) to open the target
        2. evaluate_script(injection_manager.build_injection_script()) to inject
        3. User interacts with the page
        4. evaluate_script(injection_manager.build_stop_script()) to stop and collect
        5. post_processor.process(events, session_config) to generate output
        6. Write output to project folder
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

    def get_session_metadata(self):
        """Return session metadata for output file."""
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
        """Mark session as started."""
        self.started_at = datetime.now(timezone.utc).isoformat()

    def mark_stopped(self):
        """Mark session as stopped."""
        self.stopped_at = datetime.now(timezone.utc).isoformat()

    def write_output(self, project_root, events, analysis=None):
        """Write behavior-recording JSON to project folder."""
        self.mark_stopped()

        try:
            from .post_processor import PostProcessor
        except ImportError:
            from post_processor import PostProcessor
        processor = PostProcessor()

        session_meta = self.get_session_metadata()

        try:
            result = processor.process(events, session_meta)
            session_meta['postProcessingStatus'] = 'completed'
        except Exception:
            # Retry once
            try:
                result = processor.process(events, session_meta)
                session_meta['postProcessingStatus'] = 'completed'
            except Exception:
                result = {
                    'statistics': processor.compute_statistics(events),
                    'analysis': {
                        'flow_narrative': 'Post-processing failed. Raw events preserved.',
                        'key_paths': [],
                        'pain_points': [],
                        'ai_annotations': []
                    }
                }
                session_meta['postProcessingStatus'] = 'failed'

        # Extract unique pages from events
        pages = []
        seen_urls = set()
        for ev in events:
            page_url = ev.get('metadata', {}).get('pageUrl', '')
            if page_url and page_url not in seen_urls:
                seen_urls.add(page_url)
                pages.append({'url': page_url, 'title': ev.get('metadata', {}).get('pageTitle', '')})

        output = {
            'schema_version': '1.0',
            'session': session_meta,
            'pages': pages,
            'statistics': result['statistics'],
            'events': events,
            'analysis': result['analysis']
        }

        output_path = Path(project_root) / f'behavior-recording-{self.session_id}.json'
        output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
        return str(output_path)
