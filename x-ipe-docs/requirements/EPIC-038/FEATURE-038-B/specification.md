# Feature Specification: Session Idle Detection

> Feature ID: FEATURE-038-B
> Version: v1.0
> Status: Refined
> Last Updated: 02-20-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-20-2026 | Initial specification — is_idle() and find_idle_session() for console sessions |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Refine Idea Modal | HTML | [refine-idea-modal-v1.html](../mockups/refine-idea-modal-v1.html) | Scene 2 references session dispatch flow | current |

> **Note:** This feature has no dedicated UI mockup. The session detection logic is backend/service-layer only, consumed by FEATURE-038-A's modal.

## Overview

This feature adds **session idle detection** to the existing console session management infrastructure. Currently, `PersistentSession` has `is_expired()` (1hr disconnect timeout) but no way to detect whether a **connected** session is actively running a command vs. sitting at a shell prompt.

The feature adds:
1. **`PersistentSession.is_idle()`** — Analyzes the output buffer's last line to determine if the session shows a shell prompt, indicating no active command is running.
2. **`SessionManager.find_idle_session()`** — Iterates connected sessions and returns the first idle one, or `None` if all are busy.
3. **Session rename on claim** — When a session is found idle and claimed for a workflow action, it is renamed to `wf-{workflow_name}-{action_name}`.

This is a **CR on FEATURE-029-A** (Session Explorer Core), extending session state detection beyond connected/disconnected/expired.

**Target Users:**
- FEATURE-038-A (Action Execution Modal) — primary consumer of `find_idle_session()`
- FEATURE-038-D (Refinement Skill Integration) — uses session management for agent execution

## User Stories

- **US-038-B.1:** As the Action Execution Modal, I want to find an idle console session, so that I can dispatch an agent command without requiring the user to manually select a terminal tab.
- **US-038-B.2:** As the session management system, I want to detect whether a session is at a shell prompt, so that I can distinguish between active (busy) and available (idle) sessions.
- **US-038-B.3:** As a workflow user, I want my console session to be automatically renamed when used for a workflow action, so that I can identify which session is running which action.

## Acceptance Criteria

### Idle Detection

- [ ] AC-038-B.1: `PersistentSession.is_idle()` returns `True` when the last non-empty line of the output buffer matches a shell prompt pattern
- [ ] AC-038-B.2: `is_idle()` returns `False` when the session is executing a command (output buffer's last line is not a prompt)
- [ ] AC-038-B.3: `is_idle()` returns `False` when the session is in an interactive CLI tool (vim, less, man, top, etc.)
- [ ] AC-038-B.4: Shell prompt patterns recognized by default: lines ending with `$ `, `% `, `> `, `# ` (with trailing space)
- [ ] AC-038-B.5: `is_idle()` additionally checks that no output has been received for at least `idle_timeout` seconds (default: 2s) — a rapidly scrolling buffer is not idle even if last line matches a prompt
- [ ] AC-038-B.6: `is_idle()` returns `False` for disconnected sessions (state != 'connected')
- [ ] AC-038-B.7: `is_idle()` responds within 100ms (reads from in-memory buffer only, no I/O)

### Find Idle Session

- [ ] AC-038-B.8: `SessionManager.find_idle_session()` iterates all connected sessions and returns the first one where `is_idle()` returns `True`
- [ ] AC-038-B.9: If no session is idle but session limit (10) is not reached, `find_idle_session()` returns `None` (caller decides whether to create a new one)
- [ ] AC-038-B.10: If no session is idle and session limit (10) is reached, `find_idle_session()` returns `None`
- [ ] AC-038-B.11: Method is thread-safe (uses existing `SessionManager._lock`)

### Session Rename on Claim

- [ ] AC-038-B.12: `SessionManager.claim_session_for_action(session_id, workflow_name, action_name)` renames the session to `wf-{workflow_name}-{action_name}`
- [ ] AC-038-B.13: Rename updates both backend session name and emits a WebSocket event so the frontend tab label updates
- [ ] AC-038-B.14: If the session is already claimed (name starts with `wf-`), it is still eligible for `find_idle_session()` if `is_idle()` returns `True` (previous action completed)

### Frontend Integration

- [ ] AC-038-B.15: `window.terminalManager` exposes `findIdleSession()` that calls the backend's `find_idle_session()` via WebSocket
- [ ] AC-038-B.16: `findIdleSession()` returns a Promise resolving to `{sessionId, key}` or `null`
- [ ] AC-038-B.17: If `findIdleSession()` returns `null`, the caller (FEATURE-038-A) shows an error toast or creates a new session

## Functional Requirements

**FR-038-B.1: is_idle() Method**
- Input: None (operates on instance state)
- Process:
  1. Check `self.state == 'connected'` — if not, return `False`
  2. Get last non-empty line from `self.output_buffer.get_contents()`
  3. Strip ANSI escape sequences from the line
  4. Check if the stripped line matches any shell prompt pattern (`$ `, `% `, `> `, `# ` at end)
  5. Check `time.time() - self._last_output_time >= idle_timeout` (default 2s)
  6. Return `True` only if both prompt match and timeout satisfied
- Output: `bool`

**FR-038-B.2: Last Output Timestamp Tracking**
- Input: Terminal output data received in `_read_loop()`
- Process: Each time output is received, update `self._last_output_time = time.time()`
- Output: `float` timestamp available for `is_idle()` check

**FR-038-B.3: ANSI Escape Sequence Stripping**
- Input: Raw terminal output line (may contain color codes, cursor movements)
- Process: Apply regex to strip ANSI escape sequences: `\x1b\[[0-9;]*[a-zA-Z]` and `\x1b\][^\x07]*\x07`
- Output: Clean text suitable for prompt pattern matching

**FR-038-B.4: find_idle_session() Method**
- Input: None
- Process:
  1. Acquire `self._lock`
  2. Iterate `self._sessions.values()`
  3. For each session: check `session.is_idle()`
  4. Return first idle session or `None`
- Output: `Optional[PersistentSession]`

**FR-038-B.5: claim_session_for_action() Method**
- Input: `session_id` (str), `workflow_name` (str), `action_name` (str)
- Process:
  1. Get session by ID
  2. Set `session.name = f"wf-{workflow_name}-{action_name}"`
  3. Emit WebSocket event `session_renamed` to notify frontend
- Output: `bool` (success/failure)

**FR-038-B.6: Frontend findIdleSession()**
- Input: None
- Process: Emit WebSocket event `find_idle_session`, await response
- Output: Promise resolving to `{sessionId, key}` or `null`

**FR-038-B.7: Frontend Session Rename Handler**
- Input: WebSocket `session_renamed` event with `{session_id, new_name}`
- Process: Update tab label in `sessions` Map, update localStorage, re-render tab bar
- Output: UI tab reflects new name

## Non-Functional Requirements

- **NFR-038-B.1:** `is_idle()` must complete within 100ms — reads in-memory buffer only (no disk I/O, no network calls)
- **NFR-038-B.2:** `find_idle_session()` must complete within 200ms for up to 10 sessions
- **NFR-038-B.3:** Output timestamp tracking must have negligible overhead (<1ms per output chunk)
- **NFR-038-B.4:** Thread safety — all shared state access uses existing `_lock` mechanism

## UI/UX Requirements

This feature has no direct UI. Indirect UI effects:
- Session tab labels update when renamed (e.g., "Session 3" → "wf-hello-refine_idea")
- Tab rename uses existing `renameSession()` infrastructure

## Dependencies

### Internal

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-029-A | CR target | Session Explorer Core — `PersistentSession`, `SessionManager`, `OutputBuffer` classes being extended |
| `OutputBuffer` | Read from | Provides `get_contents()` for last-line analysis |
| `terminal_handlers.py` | Integration | New WebSocket events: `find_idle_session`, `session_renamed` |
| `terminal.js` | Integration | Frontend `findIdleSession()` and rename handler |

### External

None.

## Business Rules

- **BR-038-B.1:** A session is considered "idle" only when BOTH conditions are met: (a) last output line matches a prompt pattern, AND (b) no output received for at least `idle_timeout` seconds.
- **BR-038-B.2:** `find_idle_session()` returns the FIRST idle session found — no priority/ranking logic.
- **BR-038-B.3:** A previously-claimed session (name starts with `wf-`) is still eligible for re-claim if idle.
- **BR-038-B.4:** Session limit is enforced at 10 concurrent sessions (existing constraint from FEATURE-029-A).
- **BR-038-B.5:** `find_idle_session()` never creates sessions — it only finds. Session creation is the caller's responsibility.

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Output buffer is empty (new session, no output yet) | `is_idle()` returns `False` — no prompt to match |
| Session shows prompt but output is still streaming (fast) | `is_idle()` returns `False` — `_last_output_time` within idle_timeout |
| Session running `cat` (no output, waiting for stdin) | `is_idle()` returns `False` — last line won't match prompt |
| Session shows colored prompt (ANSI codes) | ANSI stripping extracts clean text, prompt pattern matched correctly |
| Session in vim's command mode (`:` prompt) | `is_idle()` returns `False` — `:` not in default prompt patterns |
| Custom shell prompt (e.g., `→ `) | Not detected by default — user can configure in future. MVP uses `$`, `%`, `>`, `#` |
| Multiple sessions idle simultaneously | `find_idle_session()` returns the first one encountered (dict iteration order) |
| Session disconnects between find and claim | `claim_session_for_action()` checks session state, returns `False` if disconnected |
| Concurrent callers both find same idle session | First to claim wins; second caller's claim sees session already renamed but still succeeds (idempotent rename) |

## Out of Scope

- **Configurable prompt patterns via UI** — MVP uses hardcoded defaults
- **Session priority/ranking** — first-found is used
- **Automatic session creation** — caller (FEATURE-038-A) handles creation fallback
- **Session pooling / pre-warming** — not needed at current scale (≤10 sessions)
- **Detecting specific running processes** — only prompt-based detection, not `ps` inspection

## Technical Considerations

- Add `_last_output_time: float` property to `PersistentSession.__init__()` and update in `_read_loop()` callback
- Add `is_idle(idle_timeout: float = 2.0)` method to `PersistentSession`
- Add `find_idle_session()` and `claim_session_for_action()` to `SessionManager`
- ANSI stripping utility: standalone function, potentially reusable
- New WebSocket events in `terminal_handlers.py`: `find_idle_session` (request/response), `session_renamed` (broadcast)
- Frontend: add `findIdleSession()` to `TerminalManager`, add `session_renamed` event handler

## Open Questions

None — all requirements clarified during requirement gathering.
