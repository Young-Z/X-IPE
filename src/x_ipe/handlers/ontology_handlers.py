"""
Ontology Graph Socket Handlers

FEATURE-058-F CR-001: Socket Callback for AI Agent Search Results

Provides WebSocket handlers on the /ontology namespace for:
- Client connection management
- Broadcasting search results from ui-callback.py via internal endpoint
"""
from flask import request

from x_ipe.tracing import x_ipe_tracing


def register_ontology_handlers(socketio):
    """Register WebSocket event handlers for ontology graph search callbacks."""

    @socketio.on('connect', namespace='/ontology')
    @x_ipe_tracing()
    def handle_connect():
        sid = request.sid
        print(f"[Ontology] Client connected: {sid}")

    @socketio.on('disconnect', namespace='/ontology')
    def handle_disconnect():
        sid = request.sid
        print(f"[Ontology] Client disconnected: {sid}")
