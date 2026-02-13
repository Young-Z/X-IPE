"""
Terminal WebSocket Handlers

FEATURE-005: Interactive Console v4.0

Provides WebSocket handlers for:
- Terminal session attach/detach
- PTY input/output
- Terminal resize
"""
from flask import request

from x_ipe.services import session_manager
from x_ipe.tracing import x_ipe_tracing

# Socket SID to Session ID mapping
socket_to_session = {}


def register_terminal_handlers(socketio):
    """Register WebSocket event handlers for terminal."""
    
    @socketio.on('connect')
    @x_ipe_tracing()
    def handle_connect():
        """Handle new WebSocket connection."""
        sid = request.sid
        print(f"[Terminal] Client connected: {sid}")
    
    @socketio.on('attach')
    @x_ipe_tracing()
    def handle_attach(data):
        """
        Handle session attachment.
        Creates new session or reconnects to existing one.
        """
        try:
            sid = request.sid
            requested_session_id = data.get('session_id') if data else None
            # Ensure rows/cols are valid integers with defaults
            rows = data.get('rows') if data else None
            cols = data.get('cols') if data else None
            rows = int(rows) if rows is not None else 24
            cols = int(cols) if cols is not None else 80
            
            def emit_output(output_data):
                socketio.emit('output', output_data, room=sid)
            
            # Try to reconnect to existing session
            if requested_session_id and session_manager.has_session(requested_session_id):
                session = session_manager.get_session(requested_session_id)
                
                if session.is_expired():
                    session_manager.remove_session(requested_session_id)
                elif session.state == 'connected' and session.socket_sid and session.socket_sid != sid:
                    # Session is actively used by another tab — create new session for this tab
                    print(f"[Terminal] Session {requested_session_id[:8]} active on another tab, creating new session for {sid}")
                    session_id = session_manager.create_session(emit_output, rows, cols)
                    session = session_manager.get_session(session_id)
                    session.attach(sid, emit_output)
                    socket_to_session[sid] = session_id
                    
                    socketio.emit('session_id', session_id, room=sid)
                    socketio.emit('new_session', {'session_id': session_id}, room=sid)
                    return
                else:
                    # Reconnect to existing session (disconnected or same SID reconnecting)
                    session.attach(sid, emit_output)
                    socket_to_session[sid] = requested_session_id
                    
                    # Resize PTY to match new terminal dimensions
                    session.resize(rows, cols)
                    
                    # Send reconnected with buffer so client can clear before replay
                    buffer = session.get_buffer()
                    socketio.emit('reconnected', {
                        'session_id': requested_session_id,
                        'buffer': buffer or ''
                    }, room=sid)
                    return
            
            # Create new session
            session_id = session_manager.create_session(emit_output, rows, cols)
            session = session_manager.get_session(session_id)
            session.attach(sid, emit_output)
            socket_to_session[sid] = session_id
            
            socketio.emit('session_id', session_id, room=sid)
            socketio.emit('new_session', {'session_id': session_id}, room=sid)
        except Exception as e:
            print(f"[Terminal] Error in attach handler: {e}")
            socketio.emit('error', {'message': 'Failed to attach terminal session'}, room=sid)
    
    @socketio.on('disconnect')
    @x_ipe_tracing()
    def handle_disconnect():
        """Handle WebSocket disconnection - keep session alive."""
        try:
            sid = request.sid
            session_id = socket_to_session.pop(sid, None)
            
            if session_id:
                session = session_manager.get_session(session_id)
                if session and session.socket_sid == sid:
                    session.detach()  # Only detach if this SID is the active one
            
            print(f"[Terminal] Client disconnected: {sid}")
        except Exception as e:
            print(f"[Terminal] Error in disconnect handler: {e}")
    
    @socketio.on('input')
    @x_ipe_tracing()
    def handle_input(data):
        """Forward input to PTY."""
        try:
            sid = request.sid
            session_id = socket_to_session.get(sid)
            
            if session_id:
                session = session_manager.get_session(session_id)
                if session:
                    session.write(data)
        except Exception as e:
            print(f"[Terminal] Error in input handler: {e}")
    
    @socketio.on('resize')
    @x_ipe_tracing()
    def handle_resize(data):
        """Handle terminal resize."""
        try:
            sid = request.sid
            session_id = socket_to_session.get(sid)
            
            if session_id:
                session = session_manager.get_session(session_id)
                if session:
                    rows = data.get('rows', 24)
                    cols = data.get('cols', 80)
                    session.resize(rows, cols)
        except Exception as e:
            print(f"[Terminal] Error in resize handler: {e}")
    
    @socketio.on('list_server_sessions')
    @x_ipe_tracing()
    def handle_list_server_sessions():
        """List all server-side PTY sessions for orphan detection."""
        try:
            sid = request.sid
            sessions = session_manager.list_sessions()
            socketio.emit('server_sessions', sessions, room=sid)
        except Exception as e:
            print(f"[Terminal] Error in list_server_sessions handler: {e}")
    
    @socketio.on('destroy_sessions')
    @x_ipe_tracing()
    def handle_destroy_sessions(data):
        """Destroy specific server-side sessions by ID list."""
        try:
            sid = request.sid
            session_ids = data.get('session_ids', []) if data else []
            count = session_manager.destroy_sessions(session_ids)
            socketio.emit('sessions_destroyed', {'count': count}, room=sid)
        except Exception as e:
            print(f"[Terminal] Error in destroy_sessions handler: {e}")
