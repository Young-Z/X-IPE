# Feature Specification: Interactive Console

> Feature ID: FEATURE-005  
> Version: v2.0  
> Status: Refined  
> Last Updated: 01-22-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v2.0 | 01-22-2026 | Major upgrade: xterm.js integration, session persistence (1hr/10KB buffer), auto-reconnection, connection status, split-pane (up to 2 terminals), debounced resize | - |
| v1.0 | 01-18-2026 | Initial specification with VanillaTerminal, basic PTY, WebSocket communication | - |

## Overview

The Interactive Console v2.0 is a major upgrade that brings enterprise-grade terminal capabilities to the Document Viewer application. This version replaces the basic VanillaTerminal implementation with a full xterm.js-based terminal emulator, adds session persistence with output buffering for reconnection, auto-reconnection with session reattach, and optional split-pane support for up to 2 terminals.

**Key Improvements from v1.0:**
- **xterm.js Integration**: Full terminal emulator with 256 colors, cursor positioning, and proper ANSI escape sequence handling
- **Session Persistence**: PTY sessions survive WebSocket disconnects for up to 1 hour, with output buffer replay on reconnection
- **Auto-Reconnection**: Automatic WebSocket reconnection with transparent session reattachment
- **Connection Status**: Visual indicator showing terminal connection state
- **Multiple Terminals**: Optional split-pane support for up to 2 side-by-side terminals
- **Improved Resize**: Debounced resize with proper PTY SIGWINCH handling

## User Stories

- As a **developer**, I want to **have a full-featured terminal with color support**, so that **I can see formatted output from tools like git, pytest, and linters**.

- As a **developer**, I want to **my terminal session to persist if I briefly lose connection**, so that **I don't lose running processes or command context**.

- As a **developer**, I want to **see the output I missed while disconnected**, so that **I can understand what happened during the brief network interruption**.

- As a **developer**, I want to **have visual feedback about connection status**, so that **I know if the terminal is connected or reconnecting**.

- As a **developer**, I want to **optionally open a second terminal**, so that **I can run a server in one and commands in another**.

- As a **developer**, I want to **the terminal to resize properly when I adjust the panel**, so that **output displays correctly without wrapping issues**.

## Acceptance Criteria

### Phase 1: Core Upgrade (P1)

- [ ] AC-1.1: Terminal uses xterm.js 5.x for rendering (not VanillaTerminal)
- [ ] AC-1.2: Terminal displays 256-color ANSI output correctly
- [ ] AC-1.3: Cursor positioning and movement works (vim, htop-lite)
- [ ] AC-1.4: Arrow keys navigate shell history (zsh/bash native)
- [ ] AC-1.5: PTY session persists for 1 hour after WebSocket disconnect
- [ ] AC-1.6: Output buffer (10KB) replays on reconnection
- [ ] AC-1.7: Session ID stored in localStorage for reconnection
- [ ] AC-1.8: Socket.IO auto-reconnects with exponential backoff
- [ ] AC-1.9: Reconnection automatically reattaches to existing session

### Phase 2: UX Polish (P2)

- [ ] AC-2.1: Connection status indicator visible in terminal header (green/red dot)
- [ ] AC-2.2: Status shows "Connected", "Disconnected", or "Reconnecting..."
- [ ] AC-2.3: Terminal resize uses debounce (150ms) to prevent excessive PTY signals
- [ ] AC-2.4: Resize sends SIGWINCH to PTY with correct dimensions
- [ ] AC-2.5: Panel height persists in localStorage
- [ ] AC-2.6: "Reconnected to session" message shown on successful reconnection

### Phase 3: Advanced (P3)

- [ ] AC-3.1: "Add Terminal" button creates second terminal pane
- [ ] AC-3.2: Maximum of 2 terminals supported
- [ ] AC-3.3: Terminals display side-by-side with equal width
- [ ] AC-3.4: Each terminal has independent PTY session
- [ ] AC-3.5: Close button removes terminal pane
- [ ] AC-3.6: Focus border indicates active terminal
- [ ] AC-3.7: Click on terminal pane sets focus
- [ ] AC-3.8: All session IDs stored in localStorage array

## Functional Requirements

### FR-1: xterm.js Terminal Display

**Description:** Full terminal emulator using xterm.js library

**Details:**
- Input: WebSocket messages from backend PTY
- Process: Render output with xterm.js including ANSI parsing
- Output: Visual terminal with full emulation

**xterm.js Configuration:**
```javascript
{
  cursorBlink: true,
  cursorStyle: 'block',
  fontSize: 14,
  fontFamily: 'Menlo, Monaco, "Courier New", monospace',
  scrollback: 1000,
  theme: {
    background: '#1e1e1e',
    foreground: '#d4d4d4',
    cursor: '#ffffff',
    cursorAccent: '#000000',
    selection: 'rgba(255, 255, 255, 0.3)',
    // Full 16-color palette
    black: '#000000',
    red: '#cd3131',
    green: '#0dbc79',
    yellow: '#e5e510',
    blue: '#2472c8',
    magenta: '#bc3fbc',
    cyan: '#11a8cd',
    white: '#e5e5e5',
    brightBlack: '#666666',
    brightRed: '#f14c4c',
    brightGreen: '#23d18b',
    brightYellow: '#f5f543',
    brightBlue: '#3b8eea',
    brightMagenta: '#d670d6',
    brightCyan: '#29b8db',
    brightWhite: '#ffffff'
  }
}
```

**Addons:**
- `xterm-addon-fit`: Auto-resize terminal to container
- `xterm-addon-web-links` (optional): Clickable URLs

### FR-2: Session Persistence

**Description:** PTY sessions survive WebSocket disconnections

**Details:**
- Input: WebSocket disconnect event
- Process: Keep PTY alive, buffer output, track disconnect time
- Output: Session available for reconnection for 1 hour

**Components:**

**PersistentSession Class:**
```python
class PersistentSession:
    session_id: str           # UUID for this session
    pty_session: PTYSession   # Underlying PTY process
    output_buffer: OutputBuffer  # Circular buffer for replay
    socket_sid: str | None    # Current socket (None if detached)
    state: 'connected' | 'disconnected'
    disconnect_time: datetime | None
    
    def attach(socket_sid, emit_callback)  # Attach WebSocket
    def detach()                           # Detach, keep PTY
    def is_expired(timeout=3600) -> bool   # Check 1hr timeout
    def get_buffer() -> str                # Get buffered output
```

**OutputBuffer Class:**
```python
class OutputBuffer:
    max_chars: int = 10240  # 10KB limit
    _buffer: deque          # Circular buffer
    
    def append(data: str)   # Add output
    def get_contents() -> str
    def clear()
```

### FR-3: Session Manager

**Description:** Manages all persistent terminal sessions

**Details:**
- Input: Session lifecycle events (create, attach, detach, cleanup)
- Process: Maintain session registry, run cleanup task
- Output: Session lookup, creation, expiration

**SessionManager Class:**
```python
class SessionManager:
    sessions: Dict[str, PersistentSession]
    
    def create_session(emit_callback, rows, cols) -> str
    def get_session(session_id) -> PersistentSession | None
    def has_session(session_id) -> bool
    def remove_session(session_id)
    def cleanup_expired() -> int  # Returns count removed
    def start_cleanup_task()      # Background cleanup every 5min
```

### FR-4: WebSocket Session Attachment

**Description:** WebSocket events for session management

**Socket.IO Events:**

**Client → Server:**
```
'attach': { session_id?: string, rows: number, cols: number }
  - If session_id provided and exists: reattach to session
  - Otherwise: create new session
  - Returns: 'session_id' or 'reconnected' event

'input': string (keystroke data)
  - Forward to PTY

'resize': { rows: number, cols: number }
  - Resize PTY window
```

**Server → Client:**
```
'session_id': string
  - New session created, store this ID

'new_session': { session_id: string }
  - Confirmation of new session

'reconnected': { session_id: string }
  - Successfully reattached to existing session

'output': string
  - Terminal output data
```

### FR-5: Auto-Reconnection

**Description:** Automatic reconnection with session reattachment

**Socket.IO Configuration:**
```javascript
{
  transports: ['websocket'],
  reconnection: true,
  reconnectionAttempts: Infinity,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  timeout: 60000
}
```

**Reconnection Flow:**
1. Socket.IO detects disconnect
2. Automatic reconnection with exponential backoff
3. On reconnect: emit 'attach' with stored session_id
4. Server reattaches to existing session
5. Buffered output replayed to client
6. 'reconnected' event shown to user

### FR-6: Connection Status Indicator

**Description:** Visual status in terminal header

**States:**
| State | Indicator | Text |
|-------|-----------|------|
| Connected | 🟢 Green dot | "Connected" |
| Disconnected | 🔴 Red dot | "Disconnected" |
| Reconnecting | 🟡 Yellow dot | "Reconnecting..." |
| Partial (multi) | 🟢 Green dot | "Connected (1/2)" |

**UI Location:** Right side of terminal header bar

### FR-7: Terminal Resize

**Description:** Debounced resize with PTY signal

**Details:**
- Input: Window resize or panel drag
- Process: Debounce 150ms, call fitAddon.fit(), emit resize
- Output: PTY receives SIGWINCH with new dimensions

**Implementation:**
```javascript
// Debounced resize
window.addEventListener('resize', debounce(() => {
    fitAddon.fit();
    const dims = fitAddon.proposeDimensions();
    socket.emit('resize', { rows: dims.rows, cols: dims.cols });
}, 150));
```

### FR-8: Multiple Terminals (P3)

**Description:** Optional split-pane support for up to 2 terminals

**Details:**
- Input: Click "Add Terminal" button
- Process: Create new pane, new PTY session, new socket
- Output: Side-by-side terminal panes

**TerminalManager Class (Frontend):**
```javascript
class TerminalManager {
    terminals: Terminal[]      // xterm instances
    fitAddons: FitAddon[]     // Fit addons
    sockets: Socket[]         // Socket.IO connections
    sessionIds: string[]      // Server session UUIDs
    activeIndex: number       // Focused pane
    
    addTerminal(existingSessionId?)  // Create new pane
    closeTerminal(index)             // Remove pane
    setFocus(index)                  // Set active terminal
    _resizeAll()                     // Resize all terminals
    _saveSessionIds()                // Persist to localStorage
}
```

## Non-Functional Requirements

### NFR-1: Performance

- Keystroke latency: < 50ms (local server)
- Output rendering: 60fps (xterm.js native)
- Session cleanup: Background task every 5 minutes
- Memory per session: < 20KB buffer + PTY overhead

### NFR-2: Reliability

- Sessions persist 1 hour after disconnect
- Auto-reconnect with Infinity attempts
- Graceful PTY crash handling
- No memory leaks on session cleanup

### NFR-3: Compatibility

- Chrome, Firefox, Safari, Edge (latest)
- xterm.js 5.3.0+ 
- Socket.IO 4.x
- macOS zsh/bash

## UI/UX Requirements

### Single Terminal Layout (v2.0)
```
┌─────────────────────────────────────────────────────────────┐
│ [Sidebar]  │  [Content Area]                                │
├────────────┴─────────────────────────────────────────────────┤
│ ═══════════════ [Resize Handle] ═════════════════════════════│
│ ▶ Console        🟢 Connected                    [+] [−] [×] │
│ ─────────────────────────────────────────────────────────────│
│ user@host:~/project$ ls -la                                  │
│ total 48                                                     │
│ drwxr-xr-x  12 user  staff   384 Jan 22 10:00 .              │
│ user@host:~/project$ █                                       │
└─────────────────────────────────────────────────────────────┘
```

### Split Terminal Layout (P3)
```
┌─────────────────────────────────────────────────────────────┐
│ ═══════════════ [Resize Handle] ═════════════════════════════│
│ [+] Add Terminal               🟢 Connected (2/2)      [×]   │
│ ─────────────────────────────────────────────────────────────│
│ ┌─ Terminal 1 ───────────┐ ┌─ Terminal 2 ───────────────────┐│
│ │ user@host:~$ npm start │ │ user@host:~$ npm test          ││
│ │ Server running...      │ │ PASS src/tests/app.test.js     ││
│ │ █                      │ │ █                              ││
│ └────────────────────────┘ └────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Reconnection Message
```
[Disconnected - reconnecting...]
[Reconnected to session]
user@host:~/project$ 
```

## Dependencies

### External Dependencies

| Package | Source | Version | Purpose |
|---------|--------|---------|---------|
| xterm | CDN | 5.3.0 | Terminal emulator |
| xterm-addon-fit | CDN | 0.8.0 | Auto-resize |
| Socket.IO (client) | CDN | 4.7.x | WebSocket client |
| Flask-SocketIO | PyPI | 5.x | WebSocket server |
| eventlet | PyPI | 0.33+ | Async for Socket.IO |
| ptyprocess | PyPI | 0.7+ | PTY management |

### Internal Dependencies

- **FEATURE-001:** Project structure for working directory
- **Config System:** PROJECT_ROOT setting

## Business Rules

### BR-1: Session Expiration

**Rule:** Sessions expire 1 hour after last WebSocket detachment  
**Rationale:** Prevents resource exhaustion while allowing brief disconnects

### BR-2: Buffer Limit

**Rule:** Output buffer limited to 10KB circular buffer  
**Rationale:** Sufficient for recent context without memory bloat

### BR-3: Terminal Limit

**Rule:** Maximum 2 terminals per browser session  
**Rationale:** Practical limit for split-pane UI

### BR-4: Session Isolation

**Rule:** Each browser connection has independent sessions  
**Rationale:** Multi-user support (future), security isolation

## Edge Cases

### EC-1: Session Expired Before Reconnect

**Scenario:** User reconnects after 1+ hour  
**Behavior:** Server creates new session, client stores new ID

### EC-2: Buffer Overflow

**Scenario:** Output exceeds 10KB during disconnect  
**Behavior:** Oldest output discarded, newest preserved

### EC-3: Close Last Terminal

**Scenario:** User closes the only terminal  
**Behavior:** Automatically create new terminal (never empty)

### EC-4: Rapid Connect/Disconnect

**Scenario:** Network flapping causes rapid reconnects  
**Behavior:** Session persists, debounce prevents duplicate attach

## Migration from v1.0

1. Remove VanillaTerminal class
2. Remove AnsiParser class
3. Add xterm.js CDN links
4. Replace terminal initialization with xterm.js
5. Add session_manager.py (new file)
6. Update app.py WebSocket handlers
7. Add localStorage session persistence
8. Add connection status UI

## Out of Scope (v2.0)

- Terminal themes/customization
- SSH to remote servers  
- Command autocomplete
- Integration with file tree (open terminal in folder)
- More than 2 terminals
- Cross-browser session sync

---

## Specification Quality Checklist

- [x] All acceptance criteria are testable
- [x] User stories provide clear value
- [x] Functional requirements are complete
- [x] Non-functional requirements defined
- [x] Dependencies clearly stated
- [x] Edge cases identified
- [x] Out of scope explicitly listed
- [x] Migration path from v1.0 documented
