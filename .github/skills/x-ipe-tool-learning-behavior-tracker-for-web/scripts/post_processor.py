"""
FEATURE-054-F: behavior-recording.json Output & Post-Processing

PostProcessor — Transforms raw event buffer into structured analysis.
"""
from collections import Counter, defaultdict
from datetime import datetime


class PostProcessor:
    """Process raw events into structured behavior-recording analysis."""

    def process(self, events, session_meta):
        """Run full post-processing pipeline. Returns statistics + analysis dict."""
        statistics = self.compute_statistics(events)
        pain_points = self._identify_pain_points(events)
        annotations = self._annotate_events(events, pain_points)
        analysis = {
            'flow_narrative': self._generate_flow_narrative(events, session_meta),
            'key_paths': self._extract_key_paths(events),
            'key_path_summary': self._extract_key_path_summary(events, annotations),
            'pain_points': pain_points,
            'ai_annotations': annotations
        }
        return {'statistics': statistics, 'analysis': analysis}

    def compute_statistics(self, events):
        """Compute event statistics."""
        type_counts = Counter(e.get('type', 'unknown') for e in events)
        page_urls = []
        for e in events:
            url = (e.get('metadata') or {}).get('pageUrl', '')
            if url and url not in page_urls:
                page_urls.append(url)

        return {
            'totalEvents': len(events),
            'byType': dict(type_counts),
            'pageCount': len(page_urls),
            'uniquePages': page_urls
        }

    def _generate_flow_narrative(self, events, session_meta):
        """Generate human-readable flow description from events."""
        if not events:
            return 'No events recorded.'

        pages_visited = []
        for e in events:
            url = (e.get('metadata') or {}).get('pageUrl', '')
            if url and (not pages_visited or pages_visited[-1] != url):
                pages_visited.append(url)

        click_targets = []
        for e in events:
            if e.get('type') == 'click':
                target = e.get('target', {})
                label = target.get('id') or target.get('tagName', 'element')
                if label not in click_targets:
                    click_targets.append(label)

        domain = session_meta.get('domain', 'the website')
        purpose = session_meta.get('purpose', '')
        parts = [f'User visited {domain}']
        if purpose:
            parts[0] += f' ({purpose})'
        parts.append(f'navigating through {len(pages_visited)} page(s)')

        event_count = len(events)
        click_count = sum(1 for e in events if e.get('type') == 'click')
        input_count = sum(1 for e in events if e.get('type') == 'input')

        if click_count:
            parts.append(f'performing {click_count} click(s)')
        if input_count:
            parts.append(f'{input_count} input(s)')

        if click_targets[:5]:
            parts.append(f'interacting with: {", ".join(click_targets[:5])}')

        return '. '.join(parts) + f'. Total: {event_count} events.'

    def _extract_key_paths(self, events):
        """Extract most-traversed page sequences."""
        pages = []
        for e in events:
            url = (e.get('metadata') or {}).get('pageUrl', '')
            if url and (not pages or pages[-1] != url):
                pages.append(url)

        if len(pages) < 2:
            return []

        # Extract sequential pairs and count
        pair_counts = Counter()
        for i in range(len(pages) - 1):
            pair_counts[(pages[i], pages[i + 1])] += 1

        paths = []
        for (from_url, to_url), freq in pair_counts.most_common(5):
            paths.append({
                'path': [from_url, to_url],
                'frequency': freq,
                'description': f'{_shorten_url(from_url)} → {_shorten_url(to_url)}'
            })
        return paths

    def _identify_pain_points(self, events):
        """Detect pain points using heuristics."""
        pain_points = []

        # Heuristic 1: Repeated action (same target + type >= 3 times within 30s)
        window_ms = 30000
        for i, event in enumerate(events):
            if event.get('type') not in ('click', 'input'):
                continue
            target_sel = (event.get('target') or {}).get('cssSelector', '')
            if not target_sel:
                continue
            count = 1
            indices = [i]
            for j in range(i + 1, min(i + 50, len(events))):
                other = events[j]
                if other.get('type') != event.get('type'):
                    continue
                if (other.get('target') or {}).get('cssSelector') != target_sel:
                    continue
                if other.get('timestamp', 0) - event.get('timestamp', 0) > window_ms:
                    break
                count += 1
                indices.append(j)
            if count >= 3:
                pain_points.append({
                    'type': 'repeated_action',
                    'description': f'{event["type"]} on {target_sel} repeated {count} times within 30s',
                    'eventIndices': indices[:count]
                })

        # Heuristic 2: Hesitation (>5s between non-scroll events)
        for i in range(1, len(events)):
            if events[i].get('type') in ('scroll', 'resize'):
                continue
            if events[i - 1].get('type') in ('scroll', 'resize'):
                continue
            gap = events[i].get('timestamp', 0) - events[i - 1].get('timestamp', 0)
            if gap > 5000:
                label = 'long_pause' if gap > 30000 else 'hesitation'
                pain_points.append({
                    'type': label,
                    'description': f'{gap // 1000}s pause before event at index {i}',
                    'eventIndex': i,
                    'duration_ms': gap
                })

        # Heuristic 3: Back-navigation
        visited = set()
        for i, e in enumerate(events):
            if e.get('type') == 'navigation':
                to_url = (e.get('details') or {}).get('toUrl', '')
                if to_url in visited:
                    pain_points.append({
                        'type': 'back_navigation',
                        'description': f'Returned to previously visited {_shorten_url(to_url)}',
                        'eventIndex': i
                    })
                from_url = (e.get('details') or {}).get('fromUrl', '')
                if from_url:
                    visited.add(from_url)

        # Heuristic 4: Rage clicks (>=5 clicks on same target within 3s)
        for i, event in enumerate(events):
            if event.get('type') != 'click':
                continue
            target_sel = (event.get('target') or {}).get('cssSelector', '')
            if not target_sel:
                continue
            count = 1
            for j in range(i + 1, min(i + 20, len(events))):
                other = events[j]
                if other.get('type') != 'click':
                    continue
                if (other.get('target') or {}).get('cssSelector') != target_sel:
                    continue
                if other.get('timestamp', 0) - event.get('timestamp', 0) > 3000:
                    break
                count += 1
            if count >= 5:
                pain_points.append({
                    'type': 'rage_clicks',
                    'description': f'{count} rapid clicks on {target_sel} within 3s',
                    'eventIndex': i
                })

        return pain_points[:20]  # Cap at 20

    def _annotate_events(self, events, pain_points=None):
        """Add AI annotations with spec-compliant schema: comment, is_key_path, intent_category, confidence."""
        if pain_points is None:
            pain_points = self._identify_pain_points(events)

        INTENT_MAP = {
            'click': 'selection', 'double_click': 'selection', 'right_click': 'selection',
            'input': 'data_entry', 'navigation': 'navigation', 'scroll': 'exploration',
            'drag': 'selection', 'focus': 'exploration', 'resize': 'exploration'
        }

        pain_indices = {}
        for pp in pain_points:
            idx = pp.get('eventIndex') or (pp.get('eventIndices', [None])[0])
            if idx is not None:
                pain_indices[idx] = pp

        annotations = []
        for i, event in enumerate(events):
            ev_type = event.get('type', 'unknown')
            intent = INTENT_MAP.get(ev_type, 'exploration')
            is_pain = i in pain_indices
            is_key = ev_type in ('click', 'input', 'navigation', 'double_click')
            confidence = 0.5 if is_pain else (0.8 if is_key else 0.6)

            comment = ''
            if is_pain:
                comment = pain_indices[i].get('description', 'Pain point detected')
                intent = 'error_recovery' if pain_indices[i]['type'] in ('rage_clicks', 'back_navigation') else intent

            annotations.append({
                'eventIndex': i,
                'comment': comment,
                'is_key_path': is_key,
                'intent_category': intent,
                'confidence': round(confidence, 2)
            })

        return annotations

    def _extract_key_path_summary(self, events, annotations):
        """Extract ordered list of key-path events."""
        summary = []
        for ann in annotations:
            if ann.get('is_key_path'):
                idx = ann['eventIndex']
                if idx < len(events):
                    ev = events[idx]
                    target = (ev.get('target') or {}).get('cssSelector', '')
                    summary.append({
                        'step': len(summary) + 1,
                        'eventIndex': idx,
                        'type': ev.get('type', ''),
                        'target': target,
                        'intent': ann['intent_category'],
                        'description': f"{ev.get('type', '')} on {target}" if target else ev.get('type', '')
                    })
        return summary


def _shorten_url(url):
    """Shorten URL for display."""
    if not url:
        return ''
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.path or '/'
    except Exception:
        return url[:50]
