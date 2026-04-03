"""
Learn Routes Blueprint

FEATURE-054-A: Workplace Learn Module GUI
Provides session listing API for behavior tracking sessions.
"""
import json
import os
from pathlib import Path
from flask import Blueprint, jsonify, current_app

from x_ipe.tracing import x_ipe_tracing

learn_bp = Blueprint('learn', __name__)


@learn_bp.route('/api/learn/sessions', methods=['GET'])
@x_ipe_tracing()
def get_learn_sessions():
    """GET /api/learn/sessions - List behavior recording sessions from project folder."""
    project_root = current_app.config.get('PROJECT_ROOT', os.getcwd())
    sessions = []

    try:
        for f in Path(project_root).glob('behavior-recording-*.json'):
            try:
                data = json.loads(f.read_text(encoding='utf-8'))
                session_info = data.get('session', {})
                stats = data.get('statistics', {})
                sessions.append({
                    'sessionId': session_info.get('id', f.stem),
                    'domain': session_info.get('domain', 'unknown'),
                    'purpose': session_info.get('purpose', ''),
                    'status': 'completed' if session_info.get('stoppedAt') else ('paused' if session_info.get('pausedAt') else 'recording'),
                    'startedAt': session_info.get('startedAt', ''),
                    'stoppedAt': session_info.get('stoppedAt'),
                    'eventCount': stats.get('totalEvents', 0),
                    'pageCount': stats.get('pageCount', 0),
                    'postProcessingStatus': session_info.get('postProcessingStatus', 'unknown'),
                    'fileName': f.name
                })
            except (json.JSONDecodeError, KeyError):
                sessions.append({
                    'sessionId': f.stem,
                    'domain': 'unknown',
                    'purpose': '',
                    'status': 'error',
                    'startedAt': '',
                    'stoppedAt': None,
                    'eventCount': 0,
                    'pageCount': 0,
                    'postProcessingStatus': 'error',
                    'fileName': f.name
                })

        sessions.sort(key=lambda s: s.get('startedAt', ''), reverse=True)
        return jsonify({'success': True, 'sessions': sessions})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
