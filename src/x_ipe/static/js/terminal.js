/**
 * Terminal Manager — Refactored
 * FEATURE-005: Interactive Console
 * FEATURE-029-A/B/C: Session Explorer, Actions, Hover Preview
 * FEATURE-021: Voice Input Integration
 * TASK-413: Multi-tab session stability & orphan detection
 * TASK-414/435: Auto-scroll pause with xterm.js buffer API
 * TASK-415: Session preview dismiss on mouseleave
 *
 * Architecture:
 *   TerminalManager  — session lifecycle, persistence, socket wiring
 *   SessionExplorer  — right-side panel UI (list, rename, preview, orphans)
 *   TerminalPanel    — chrome wrapper (collapse, zen, resize, explorer toggle)
 */
(function () {
    'use strict';

    // =========================================================================
    // Constants
    // =========================================================================

    const SESSION_KEY            = 'terminal_session_ids';
    const SESSION_NAMES_KEY      = 'terminal_session_names';
    const MAX_SESSIONS           = 10;
    const EXPLORER_WIDTH_KEY     = 'console_explorer_width';
    const EXPLORER_COLLAPSED_KEY = 'console_explorer_collapsed';
    const EXPLORER_DEFAULT_WIDTH = 220;
    const EXPLORER_MIN_WIDTH     = 160;
    const EXPLORER_MAX_WIDTH     = 360;
    const SCROLL_RESUME_MS       = 5000;
    const HEALTH_CHECK_MS        = 60000;
    const STALE_THRESHOLD_MS     = 180000;
    const TYPING_BASE_DELAY      = 30;
    const TYPING_JITTER          = 50;

    // =========================================================================
    // Utilities
    // =========================================================================

    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    /** Safe localStorage get with JSON parse */
    function storageGet(key, fallback) {
        try {
            const v = localStorage.getItem(key);
            return v !== null ? JSON.parse(v) : fallback;
        } catch { return fallback; }
    }

    /** Safe localStorage set with JSON stringify */
    function storageSet(key, value) {
        try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
    }

    /** Save/restore page scroll positions to prevent focus-induced jumps */
    function withScrollLock(fn) {
        const sx = window.scrollX, sy = window.scrollY;
        const cb = document.querySelector('.content-body');
        const cbs = cb?.scrollTop || 0;
        fn();
        if (window.scrollX !== sx || window.scrollY !== sy) window.scrollTo(sx, sy);
        if (cb && cb.scrollTop !== cbs) cb.scrollTop = cbs;
    }

    // =========================================================================
    // Shared terminal config
    // =========================================================================

    const terminalConfig = {
        cursorBlink: true,
        cursorStyle: 'block',
        fontSize: 14,
        fontFamily: 'Menlo, Monaco, "Courier New", monospace',
        scrollback: 1000,
        scrollOnUserInput: false,
        allowProposedApi: true,
        windowsPty: { backend: undefined, buildNumber: undefined },
        theme: {
            background: '#1e1e1e', foreground: '#d4d4d4',
            cursor: '#ffffff', cursorAccent: '#000000',
            selection: 'rgba(255, 255, 255, 0.3)',
            black: '#000000', red: '#cd3131', green: '#0dbc79',
            yellow: '#e5e510', blue: '#2472c8', magenta: '#bc3fbc',
            cyan: '#11a8cd', white: '#e5e5e5',
            brightBlack: '#666666', brightRed: '#f14c4c', brightGreen: '#23d18b',
            brightYellow: '#f5f543', brightBlue: '#3b8eea', brightMagenta: '#d670d6',
            brightCyan: '#29b8db', brightWhite: '#ffffff'
        }
    };

    const socketConfig = {
        transports: ['websocket'],
        upgrade: false,
        reconnection: true,
        reconnectionAttempts: Infinity,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 30000,
        randomizationFactor: 0.5,
        timeout: 60000,
        forceNew: true,
        pingTimeout: 300000,
        pingInterval: 60000
    };

    // =========================================================================
    // TerminalManager
    // =========================================================================

    class TerminalManager {
        constructor(contentContainerId) {
            this.sessions = new Map();
            this.activeSessionKey = null;
            this._sessionCounter = 0;
            this.contentContainer = document.getElementById(contentContainerId);
            this.statusIndicator = document.getElementById('terminal-status-indicator');
            this.statusText = document.getElementById('terminal-status-text');
            this.explorer = null;
            this.autoExecutePrompt = false;
            this._initialFitDone = false;
            this._scrollResumeTimers = new Map();
            this._activeTyping = null;

            this._loadAutoExecuteConfig();
            this._setupEventListeners();
            this._setupResizeObserver();
        }

        // -- Config -----------------------------------------------------------

        async _loadAutoExecuteConfig() {
            try {
                const resp = await fetch('/api/config');
                if (resp.ok) {
                    const data = await resp.json();
                    this.autoExecutePrompt = data.auto_execute_prompt || false;
                }
            } catch {}
        }

        // -- Resize / visibility observers ------------------------------------

        _setupResizeObserver() {
            if (!this.contentContainer || typeof ResizeObserver === 'undefined') return;
            this._resizeObserver = new ResizeObserver(debounce((entries) => {
                for (const entry of entries) {
                    const { width, height } = entry.contentRect;
                    if (width > 0 && height > 0) {
                        this._fitActiveSession();
                        if (!this._initialFitDone && this.sessions.size > 0) this._initialFitDone = true;
                    }
                }
            }, 50));
            this._resizeObserver.observe(this.contentContainer);
        }

        _setupEventListeners() {
            window.addEventListener('resize', debounce(() => this._fitActiveSession(), 150));
            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'visible') this._checkAndReconnectAll();
            });
            window.addEventListener('focus', () => this._checkAndReconnectAll());
        }

        _checkAndReconnectAll() {
            for (const [, s] of this.sessions) {
                if (s.socket && !s.socket.connected) s.socket.connect();
            }
            setTimeout(() => this.explorer?.checkOrphanedSessions(), 2000);
        }

        // -- Initialization ---------------------------------------------------

        initialize() {
            const ids = storageGet(SESSION_KEY, []);
            const names = storageGet(SESSION_NAMES_KEY, {});
            if (ids.length > 0) {
                ids.forEach(id => this.addSession(id, names[id] || null));
            } else {
                this.addSession();
            }
            setTimeout(() => this.explorer?.checkOrphanedSessions(), 3000);
        }

        // -- Session CRUD -----------------------------------------------------

        addSession(existingSessionId = null, name = null) {
            if (this.sessions.size >= MAX_SESSIONS) {
                this.explorer?.showToast('Maximum 10 sessions reached');
                return null;
            }
            const key = `s${this._sessionCounter++}`;
            const sessionName = name || this._nextName();

            // DOM container
            const container = document.createElement('div');
            container.className = 'terminal-session-container';
            container.dataset.sessionKey = key;
            this.contentContainer.appendChild(container);

            // xterm + addons
            const terminal = new Terminal(terminalConfig);
            const fitAddon = new FitAddon.FitAddon();
            terminal.loadAddon(fitAddon);
            if (typeof Unicode11Addon !== 'undefined') {
                const u = new Unicode11Addon.Unicode11Addon();
                terminal.loadAddon(u);
                terminal.unicode.activeVersion = '11';
            }
            terminal.open(container);

            const sessionData = {
                key, sessionId: existingSessionId, name: sessionName,
                terminal, fitAddon, socket: null, container, isActive: false
            };
            this.sessions.set(key, sessionData);

            this._setupScrollPrevention(terminal, container);
            this._setupAutoScrollPause(terminal, key);
            sessionData.socket = this._createSocket(key, existingSessionId);
            this._setupInput(sessionData);

            this.switchSession(key);
            this.explorer?.addSessionBar(key, sessionName);
            this.explorer?.updateActiveIndicator(this.activeSessionKey);
            this.explorer?.setAddButtonEnabled(this.sessions.size < MAX_SESSIONS);
            this._persistSessions();
            return key;
        }

        removeSession(key) {
            const session = this.sessions.get(key);
            if (!session) return;

            // Destroy backend PTY session before disconnecting socket
            if (session.sessionId && session.socket?.connected) {
                session.socket.emit('destroy_sessions', { session_ids: [session.sessionId] });
            }
            session.socket?.disconnect();
            session.terminal?.dispose();
            session.container?.remove();
            this.sessions.delete(key);

            // Clean up scroll timer
            const timer = this._scrollResumeTimers.get(key);
            if (timer) { clearTimeout(timer); this._scrollResumeTimers.delete(key); }

            this.explorer?.removeSessionBar(key);
            this.explorer?.setAddButtonEnabled(this.sessions.size < MAX_SESSIONS);

            if (this.sessions.size > 0) {
                if (this.activeSessionKey === key) {
                    this.switchSession(this.sessions.keys().next().value);
                }
                this.explorer?.updateActiveIndicator(this.activeSessionKey);
            } else {
                this.activeSessionKey = null;
                this.addSession();
            }
            this._persistSessions();
            this._updateStatus();
        }

        renameSession(key, newName) {
            const s = this.sessions.get(key);
            if (s) { s.name = newName; this._persistSessions(); }
        }

        switchSession(key) {
            const session = this.sessions.get(key);
            if (!session) return;
            for (const [, s] of this.sessions) {
                s.container.classList.remove('active');
                s.isActive = false;
            }
            session.container.classList.add('active');
            session.isActive = true;
            this.activeSessionKey = key;
            this.explorer?.updateActiveIndicator(key);
            this.fitActive();
            this._focusWithoutScroll(session.terminal);
        }

        // -- Fit / resize helpers ---------------------------------------------

        _getActiveSession() {
            return this.activeSessionKey ? this.sessions.get(this.activeSessionKey) : null;
        }

        _fitActiveSession() {
            const s = this._getActiveSession();
            if (!s) return;
            try {
                s.fitAddon.fit();
                const dims = s.fitAddon.proposeDimensions();
                if (dims && s.socket?.connected) {
                    s.socket.emit('resize', { rows: dims.rows, cols: dims.cols });
                }
            } catch {}
        }

        fitActive() {
            this._fitActiveSession();
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    this._fitActiveSession();
                    setTimeout(() => this._fitActiveSession(), 50);
                });
            });
        }

        // Legacy aliases
        fitAll()     { this.fitActive(); }
        _doFit()     { this._fitActiveSession(); }
        _resizeAll() { this._fitActiveSession(); }

        // -- Focus without scroll ---------------------------------------------

        _focusWithoutScroll(terminal) {
            if (!terminal) return;
            const viewport = terminal.element?.querySelector('.xterm-viewport');
            const vtop = viewport?.scrollTop || 0;
            withScrollLock(() => {
                try {
                    const ta = terminal.element?.querySelector('.xterm-helper-textarea');
                    if (ta) ta.focus({ preventScroll: true }); else terminal.focus();
                } catch { terminal.focus(); }
            });
            if (viewport && viewport.scrollTop !== vtop) viewport.scrollTop = vtop;
        }

        // -- Scroll prevention for textarea -----------------------------------

        _setupScrollPrevention(terminal, container) {
            requestAnimationFrame(() => {
                const textarea = terminal.element?.querySelector('.xterm-helper-textarea');
                if (!textarea) return;
                const restore = () => withScrollLock(() => {});
                const guard = () => { restore(); queueMicrotask(restore); requestAnimationFrame(restore); };

                textarea.addEventListener('focus', guard, { capture: true });
                textarea.addEventListener('keydown', guard, { capture: true });
                textarea.addEventListener('input', guard, { capture: true });
                container.addEventListener('mousedown', () => { requestAnimationFrame(restore); });

                let kpTimeout = null;
                textarea.addEventListener('keypress', () => {
                    if (kpTimeout) clearTimeout(kpTimeout);
                    kpTimeout = setTimeout(() => {
                        if (document.activeElement === textarea) restore();
                    }, 10);
                }, { capture: true });
            });
        }

        // -- Auto-scroll pause (TASK-414/435) ---------------------------------

        /**
         * Uses xterm.js buffer API (viewportY === baseY) to detect scroll state.
         */
        _isAtBottom(terminal) {
            return terminal.buffer.active.viewportY
                === terminal.buffer.active.baseY;
        }

        _setupAutoScrollPause(terminal, sessionKey) {
            const trySetup = (attempt) => {
                const viewport = terminal.element?.querySelector('.xterm-viewport');
                if (!viewport) {
                    if (attempt < 3) requestAnimationFrame(() => trySetup(attempt + 1));
                    return;
                }
                this._initAutoScrollListeners(viewport, terminal, sessionKey);
            };
            requestAnimationFrame(() => trySetup(0));
        }

        /**
         * Auto-scroll pause listeners using xterm.js buffer API (viewportY vs baseY).
         * No 'scroll' event listener here — avoids race conditions with programmatic scrolls.
         */
        _initAutoScrollListeners(viewport, terminal, sessionKey) {
            const startOrRestartTimer = () => {
                const existing = this._scrollResumeTimers.get(sessionKey);
                if (existing) clearTimeout(existing);
                this._scrollResumeTimers.set(sessionKey, setTimeout(() => {
                    this._scrollResumeTimers.delete(sessionKey);
                    terminal.scrollToBottom();
                }, 5000));
            };

            const cancelTimer = () => {
                const existing = this._scrollResumeTimers.get(sessionKey);
                if (existing) { clearTimeout(existing); this._scrollResumeTimers.delete(sessionKey); }
            };

            viewport.addEventListener('wheel', (e) => {
                if (e.deltaY < 0) {
                    // Scroll up — only start timer if viewport left the bottom
                    requestAnimationFrame(() => {
                        const isAtBottom = terminal.buffer.active.viewportY
                            === terminal.buffer.active.baseY;
                        if (!isAtBottom) startOrRestartTimer();
                    });
                    return;
                }

                // Non-upward wheel while scrolled up restarts the timer
                if (terminal.buffer.active.viewportY !== terminal.buffer.active.baseY) {
                    startOrRestartTimer();
                }

                // Scroll down past bottom — cancel timer
                if (e.deltaY > 0) {
                    requestAnimationFrame(() => {
                        const isAtBottom = terminal.buffer.active.viewportY
                            === terminal.buffer.active.baseY;
                        if (isAtBottom) cancelTimer();
                    });
                }
            }, { passive: true });
        }

        // -- Input handling ---------------------------------------------------

        _setupInput(sessionData) {
            sessionData.terminal.onData(data => {
                if (data === '\x03' && this._activeTyping) {
                    this._cancelTyping();
                    return;
                }
                if (sessionData.socket?.connected) {
                    withScrollLock(() => {
                        sessionData.socket.emit('input', data);
                        sessionData.terminal.scrollToBottom();
                    });
                }
            });
        }

        // -- Socket.IO --------------------------------------------------------

        _createSocket(sessionKey, existingSessionId) {
            const socket = io(socketConfig);
            let lastPongTime = Date.now();
            let healthCheckId = null;
            const getSession = () => this.sessions.get(sessionKey);

            const startHealthCheck = () => {
                if (healthCheckId) clearInterval(healthCheckId);
                healthCheckId = setInterval(() => {
                    const elapsed = Date.now() - lastPongTime;
                    const s = getSession();
                    if (elapsed > STALE_THRESHOLD_MS && socket.connected && s) {
                        console.warn(`[Terminal ${s.name}] Possibly stale (${Math.round(elapsed / 1000)}s)`);
                    }
                }, HEALTH_CHECK_MS);
            };
            const stopHealthCheck = () => { if (healthCheckId) { clearInterval(healthCheckId); healthCheckId = null; } };

            const emitAttach = (sessionId) => {
                const s = getSession();
                const dims = s?.fitAddon?.proposeDimensions();
                socket.emit('attach', {
                    session_id: sessionId,
                    rows: dims?.rows ?? 24,
                    cols: dims?.cols ?? 80
                });
            };

            // -- connect
            socket.on('connect', () => {
                const s = getSession();
                if (!s) return;
                lastPongTime = Date.now();
                startHealthCheck();
                this._updateStatus();
                emitAttach(existingSessionId);
            });

            // -- session lifecycle
            socket.on('session_id', id => {
                const s = getSession();
                if (s) { s.sessionId = id; this._persistSessions(); }
            });

            socket.on('new_session', data => {
                const s = getSession();
                if (s) {
                    s.terminal.write('\x1b[32m[New session started]\x1b[0m\r\n');
                    s.sessionId = data.session_id;
                    this._persistSessions();
                }
            });

            socket.on('reconnected', data => {
                const s = getSession();
                if (s) {
                    s.terminal.reset();
                    if (data?.buffer) s.terminal.write(data.buffer);
                    this.fitActive();
                }
            });

            // -- output with scroll-lock when user has scrolled up
            socket.on('output', data => {
                const s = getSession();
                if (!s) return;
                const isAtBottom = this._isAtBottom(s.terminal);
                if (isAtBottom) {
                    s.terminal.write(data);
                    s.terminal.scrollToBottom();
                } else {
                    const viewport = s.terminal.element?.querySelector('.xterm-viewport');
                    if (viewport) {
                        const savedScrollTop = viewport.scrollTop;
                        let locked = true;
                        const lockScroll = () => { if (locked) viewport.scrollTop = savedScrollTop; };
                        viewport.addEventListener('scroll', lockScroll);
                        s.terminal.write(data, () => {
                            requestAnimationFrame(() => {
                                requestAnimationFrame(() => {
                                    locked = false;
                                    viewport.removeEventListener('scroll', lockScroll);
                                    viewport.scrollTop = savedScrollTop;
                                });
                            });
                        });
                    } else {
                        s.terminal.write(data);
                    }
                }
            });

            // -- pong
            socket.io.engine.on('pong', () => { lastPongTime = Date.now(); });

            // -- disconnect / reconnect
            socket.on('disconnect', reason => {
                const s = getSession();
                stopHealthCheck();
                this._updateStatus();
                if (reason !== 'io client disconnect' && s) {
                    const msg = reason === 'ping timeout'
                        ? '[Connection timeout - reconnecting...]'
                        : (reason === 'transport close' || reason === 'transport error')
                            ? '[Connection lost - reconnecting...]' : null;
                    if (msg) s.terminal.write(`\r\n\x1b[31m${msg}\x1b[0m\r\n`);
                }
            });

            socket.io.on('reconnect', () => {
                const s = getSession();
                if (!s) return;
                lastPongTime = Date.now();
                startHealthCheck();
                this._updateStatus();
                emitAttach(s.sessionId);
            });

            socket.io.on('reconnect_attempt', attempt => {
                const s = getSession();
                if (s && attempt === 1) s.terminal.write('\x1b[33m[Reconnecting...]\x1b[0m\r\n');
            });

            socket.io.on('reconnect_failed', () => {
                stopHealthCheck();
                getSession()?.terminal.write('\r\n\x1b[31m[Connection lost - please refresh page]\x1b[0m\r\n');
            });

            socket.on('connect_error', error => {
                console.error(`[Terminal] Connection error:`, error.message || error);
                this._updateStatus();
            });

            return socket;
        }

        // -- Status -----------------------------------------------------------

        _updateStatus() {
            let connected = 0, total = 0;
            for (const [, s] of this.sessions) {
                total++;
                if (s.socket?.connected) connected++;
            }
            if (!this.statusIndicator) return;
            if (connected === total && total > 0) {
                this.statusIndicator.className = 'status-indicator connected';
                if (this.statusText) this.statusText.textContent = total > 1 ? `Connected (${connected}/${total})` : 'Connected';
            } else if (connected > 0) {
                this.statusIndicator.className = 'status-indicator connected';
                if (this.statusText) this.statusText.textContent = `Partial (${connected}/${total})`;
            } else {
                this.statusIndicator.className = 'status-indicator disconnected';
                if (this.statusText) this.statusText.textContent = 'Disconnected';
            }
        }

        // -- Persistence ------------------------------------------------------

        _nextName() {
            const used = new Set();
            for (const [, s] of this.sessions) {
                const m = s.name.match(/^Session (\d+)$/);
                if (m) used.add(+m[1]);
            }
            let n = 1;
            while (used.has(n)) n++;
            return `Session ${n}`;
        }

        _persistSessions() {
            const ids = [], names = {};
            for (const [, s] of this.sessions) {
                if (s.sessionId) { ids.push(s.sessionId); names[s.sessionId] = s.name; }
            }
            storageSet(SESSION_KEY, ids);
            storageSet(SESSION_NAMES_KEY, names);
        }

        // -- Legacy compatibility ---------------------------------------------

        get terminals()  { return Array.from(this.sessions.values()).map(s => s.terminal); }
        get sockets()    { return Array.from(this.sessions.values()).map(s => s.socket); }
        get activeIndex() {
            if (!this.activeSessionKey) return -1;
            let i = 0;
            for (const k of this.sessions.keys()) { if (k === this.activeSessionKey) return i; i++; }
            return -1;
        }
        addTerminal(existingSessionId = null) { return this.addSession(existingSessionId) ? this.activeIndex : -1; }
        setFocus(index) {
            const keys = Array.from(this.sessions.keys());
            if (index >= 0 && index < keys.length) this.switchSession(keys[index]);
        }

        // -- Voice input (FEATURE-021) ----------------------------------------

        getFocusedTerminal() {
            const s = this._getActiveSession();
            if (!s) return null;
            return {
                terminal: s.terminal, socket: s.socket, sessionId: s.sessionId,
                sendInput: (text) => { if (s.socket?.connected) s.socket.emit('input', text); }
            };
        }

        get socket() {
            for (const [, s] of this.sessions) if (s.socket?.connected) return s.socket;
            return this.sessions.values().next().value?.socket ?? null;
        }

        // -- Copilot integration ----------------------------------------------

        sendCopilotPromptCommandNoEnter(promptCommand) {
            if (this.sessions.size === 0) this.addSession();
            const s = this._getActiveSession();
            if (!s) return;
            this._sendWithTypingEffectNoEnter(s.key, this._buildCopilotCmd(promptCommand));
        }

        sendCopilotRefineCommand(filePath) { this._sendCopilotWithPrompt(`refine the idea ${filePath}`); }
        sendCopilotPromptCommand(prompt)   { this._sendCopilotWithPrompt(prompt); }

        _sendCopilotWithPrompt(prompt) {
            if (this.sessions.size === 0) this.addSession();
            const s = this._getActiveSession();
            if (!s) return;
            const cmd = this._buildCopilotCmd(prompt);
            this.autoExecutePrompt
                ? this._sendWithTypingEffect(s.key, cmd, null)
                : this._sendWithTypingEffectNoEnter(s.key, cmd);
        }

        _buildCopilotCmd(prompt) {
            return `copilot --allow-all-tools --allow-all-paths --allow-all-urls -i "${prompt.replace(/"/g, '\\"')}"`;
        }

        _waitForCopilotReady(sessionKey, callback, maxAttempts = 30) {
            const s = this.sessions.get(sessionKey);
            if (!s) return;
            let attempts = 0;
            const check = () => {
                if (++attempts > maxAttempts || this._isCopilotPromptReady(sessionKey)) {
                    setTimeout(callback, attempts > maxAttempts ? 500 : 300);
                    return;
                }
                setTimeout(check, 200);
            };
            setTimeout(check, 500);
        }

        _isCopilotPromptReady(sessionKey) {
            const s = this.sessions.get(sessionKey);
            if (!s) return false;
            const buf = s.terminal.buffer.active;
            for (let i = Math.max(0, buf.cursorY - 3); i <= buf.cursorY; i++) {
                const line = buf.getLine(i);
                if (line) {
                    const text = line.translateToString(true);
                    if (text.match(/^>[\s]*$/) || text.includes('⏺') || text.match(/>\s*$/)) return true;
                }
            }
            return false;
        }

        _isInCopilotMode(sessionKeyOrIndex) {
            let s;
            if (typeof sessionKeyOrIndex === 'number') {
                s = this.sessions.get(Array.from(this.sessions.keys())[sessionKeyOrIndex]);
            } else {
                s = this.sessions.get(sessionKeyOrIndex);
            }
            if (!s) return false;
            const buf = s.terminal.buffer.active;
            for (let i = Math.max(0, buf.cursorY - 5); i <= buf.cursorY; i++) {
                const line = buf.getLine(i);
                if (line) {
                    const text = line.translateToString(true);
                    if (text.includes('copilot>') || text.includes('Copilot') || text.includes('⏺')) return true;
                }
            }
            return false;
        }

        // -- Typing effect ----------------------------------------------------

        _sendWithTypingEffect(sessionKey, text, callback) {
            const s = this.sessions.get(sessionKey);
            if (!s?.socket?.connected) return;
            this._cancelTyping();
            const state = { cancelled: false };
            this._activeTyping = state;
            let i = 0;
            const type = () => {
                if (state.cancelled) return;
                if (i < text.length) {
                    s.socket.emit('input', text[i++]);
                    setTimeout(type, TYPING_BASE_DELAY + Math.random() * TYPING_JITTER);
                } else {
                    setTimeout(() => {
                        if (state.cancelled) return;
                        s.socket.emit('input', '\r');
                        this._activeTyping = null;
                        callback?.();
                    }, 100);
                }
            };
            type();
        }

        _sendWithTypingEffectNoEnter(sessionKey, text) {
            const s = this.sessions.get(sessionKey);
            if (!s?.socket?.connected) return;
            this._cancelTyping();
            const state = { cancelled: false };
            this._activeTyping = state;
            let i = 0;
            const type = () => {
                if (state.cancelled) return;
                if (i < text.length) {
                    s.socket.emit('input', text[i++]);
                    setTimeout(type, TYPING_BASE_DELAY + Math.random() * TYPING_JITTER);
                } else {
                    this._activeTyping = null;
                }
            };
            type();
        }

        _cancelTyping() {
            if (this._activeTyping) { this._activeTyping.cancelled = true; this._activeTyping = null; }
        }
    }

    // =========================================================================
    // SessionExplorer (FEATURE-029-A/B/C, TASK-413, TASK-415)
    // =========================================================================

    class SessionExplorer {
        constructor(terminalManager) {
            this.manager = terminalManager;
            this.listEl = document.getElementById('session-list');
            this.addBtn = document.getElementById('explorer-add-btn');
            this.manager.explorer = this;

            // Preview state (FEATURE-029-C)
            this._previewContainer = null;
            this._previewTerminal = null;
            this._previewFitAddon = null;
            this._previewKey = null;
            this._hoverTimer = null;
            this._graceTimer = null;
            this._previewOutputHandler = null;

            // Orphan detection (TASK-413)
            this._orphanBar = null;
            this._orphanCount = 0;
            this._orphanIds = [];
            this._createOrphanBar();
            this._bindEvents();
        }

        _bindEvents() {
            this.addBtn?.addEventListener('click', (e) => {
                e.stopPropagation();
                this.manager.addSession();
            });
        }

        // -- Orphan detection (TASK-413) --------------------------------------

        _createOrphanBar() {
            const bar = document.createElement('div');
            bar.className = 'orphan-sessions-bar';
            bar.style.display = 'none';
            bar.innerHTML = `
                <span class="orphan-info"><i class="bi bi-exclamation-triangle"></i> <span class="orphan-count">0</span> orphaned</span>
            `;
            const btn = document.createElement('button');
            btn.className = 'session-action-btn orphan-destroy-btn';
            btn.title = 'Destroy orphaned sessions';
            btn.innerHTML = '<i class="bi bi-trash"></i>';
            btn.addEventListener('click', (e) => { e.stopPropagation(); this._destroyOrphanedSessions(); });
            bar.appendChild(btn);
            this._orphanBar = bar;
            this.listEl.parentNode.appendChild(bar);
        }

        checkOrphanedSessions() {
            const socket = this._getAnySocket();
            if (!socket?.connected) return;
            socket.emit('list_server_sessions');
            socket.once('server_sessions', (serverSessions) => {
                const localIds = new Set();
                this.manager.sessions.forEach(s => { if (s.sessionId) localIds.add(s.sessionId); });
                const orphaned = serverSessions.filter(s => !localIds.has(s.session_id));
                this._orphanCount = orphaned.length;
                this._orphanIds = orphaned.map(s => s.session_id);
                this._updateOrphanBar();
            });
        }

        _updateOrphanBar() {
            if (!this._orphanBar) return;
            this._orphanBar.style.display = this._orphanCount > 0 ? 'flex' : 'none';
            if (this._orphanCount > 0) {
                this._orphanBar.querySelector('.orphan-count').textContent = this._orphanCount;
            }
        }

        _destroyOrphanedSessions() {
            if (!this._orphanIds.length) return;
            const socket = this._getAnySocket();
            if (!socket?.connected) return;
            socket.emit('destroy_sessions', { session_ids: this._orphanIds });
            socket.once('sessions_destroyed', () => {
                this._orphanCount = 0;
                this._orphanIds = [];
                this._updateOrphanBar();
            });
        }

        _getAnySocket() {
            for (const [, s] of this.manager.sessions) if (s.socket?.connected) return s.socket;
            return null;
        }

        // -- Session bars -----------------------------------------------------

        addSessionBar(key, name) {
            const bar = document.createElement('div');
            bar.className = 'session-bar';
            bar.dataset.sessionKey = key;
            bar.dataset.active = 'false';

            bar.innerHTML = `
                <span class="session-status-dot"></span>
                <span class="session-name">${this._escapeHtml(name)}</span>
                <button class="session-action-btn rename-btn" title="Rename"><i class="bi bi-pencil"></i></button>
                <button class="session-action-btn delete-btn" title="Delete"><i class="bi bi-trash"></i></button>
            `;

            bar.querySelector('.rename-btn').addEventListener('click', (e) => { e.stopPropagation(); this.startRename(key); });
            bar.querySelector('.delete-btn').addEventListener('click', (e) => { e.stopPropagation(); this.manager.removeSession(key); });
            bar.addEventListener('click', () => this.manager.switchSession(key));

            // Hover preview (FEATURE-029-C / TASK-415)
            bar.addEventListener('mouseenter', () => {
                if (bar.dataset.active === 'true') return;
                this._hoverTimer = setTimeout(() => this._showPreview(key, bar), 500);
            });
            bar.addEventListener('mouseleave', () => {
                clearTimeout(this._hoverTimer);
                this._dismissPreview();
            });

            this.listEl.appendChild(bar);
        }

        _escapeHtml(str) {
            const d = document.createElement('div');
            d.textContent = str;
            return d.innerHTML;
        }

        removeSessionBar(key) {
            if (this._previewKey === key) this._dismissPreview();
            this.listEl.querySelector(`[data-session-key="${key}"]`)?.remove();
        }

        updateActiveIndicator(activeKey) {
            this.listEl.querySelectorAll('.session-bar').forEach(bar => {
                bar.dataset.active = bar.dataset.sessionKey === activeKey ? 'true' : 'false';
            });
        }

        setAddButtonEnabled(enabled) { if (this.addBtn) this.addBtn.disabled = !enabled; }

        // -- Rename -----------------------------------------------------------

        startRename(key) {
            const bar = this.listEl.querySelector(`[data-session-key="${key}"]`);
            if (!bar) return;
            const nameSpan = bar.querySelector('.session-name');
            if (!nameSpan || nameSpan.tagName === 'INPUT') return;

            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'session-name-input';
            input.value = nameSpan.textContent;
            const original = nameSpan.textContent;
            let done = false;

            const finish = (save) => {
                if (done) return;
                done = true;
                const val = save ? input.value.trim() : '';
                if (val && val !== original) this.manager.renameSession(key, val);
                const span = document.createElement('span');
                span.className = 'session-name';
                span.textContent = (save && val) ? val : original;
                input.replaceWith(span);
            };

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') { e.preventDefault(); finish(true); }
                if (e.key === 'Escape') { e.preventDefault(); finish(false); }
            });
            input.addEventListener('blur', () => finish(true));
            nameSpan.replaceWith(input);
            input.focus();
            input.select();
        }

        // -- Toast ------------------------------------------------------------

        showToast(message) {
            const panel = document.getElementById('terminal-panel');
            if (!panel) return;
            let toast = panel.querySelector('.session-toast');
            if (!toast) {
                toast = document.createElement('div');
                toast.className = 'session-toast';
                toast.setAttribute('role', 'alert');
                panel.appendChild(toast);
            }
            toast.textContent = message;
            toast.classList.add('visible');
            setTimeout(() => toast.classList.remove('visible'), 2500);
        }

        // -- Preview (FEATURE-029-C) ------------------------------------------

        _initPreviewContainer() {
            if (this._previewContainer) return;
            this._previewContainer = document.createElement('div');
            this._previewContainer.className = 'session-preview';
            this._previewContainer.style.display = 'none';

            const header = document.createElement('div');
            header.className = 'session-preview-header';
            const body = document.createElement('div');
            body.className = 'session-preview-body';
            this._previewContainer.appendChild(header);
            this._previewContainer.appendChild(body);

            this._previewContainer.addEventListener('click', () => {
                if (this._previewKey) {
                    const k = this._previewKey;
                    this._dismissPreview();
                    this.manager.switchSession(k);
                }
            });

            document.getElementById('terminal-panel').appendChild(this._previewContainer);

            this._previewTerminal = new Terminal({
                disableStdin: true, scrollback: 500,
                fontSize: terminalConfig.fontSize, fontFamily: terminalConfig.fontFamily,
                theme: terminalConfig.theme, cursorBlink: false
            });
            this._previewFitAddon = new FitAddon.FitAddon();
            this._previewTerminal.loadAddon(this._previewFitAddon);
            this._previewTerminal.open(body);
        }

        _showPreview(key) {
            const session = this.manager.sessions.get(key);
            if (!session) return;
            this._initPreviewContainer();
            if (this._previewKey && this._previewKey !== key) this._cleanupPreviewListeners();
            this._previewKey = key;

            this._previewContainer.querySelector('.session-preview-header').textContent = session.name;
            this._previewTerminal.clear();

            const buf = session.terminal.buffer.active;
            const lines = [];
            for (let i = 0; i < buf.length; i++) {
                const line = buf.getLine(i);
                if (line) lines.push(line.translateToString(true));
            }
            if (lines.length) this._previewTerminal.write(lines.join('\r\n'));
            this._previewTerminal.scrollToBottom();

            if (session.socket) {
                this._previewOutputHandler = (data) => {
                    if (this._previewKey === key) {
                        this._previewTerminal.write(data);
                        this._previewTerminal.scrollToBottom();
                    }
                };
                session.socket.on('output', this._previewOutputHandler);
            }

            this._previewContainer.style.display = 'flex';
            const explorer = document.getElementById('session-explorer');
            if (explorer && !explorer.classList.contains('collapsed')) {
                this._previewContainer.style.right = explorer.style.width || '';
            }
            try { this._previewFitAddon.fit(); } catch {}
        }

        _dismissPreview() {
            clearTimeout(this._hoverTimer);
            clearTimeout(this._graceTimer);
            this._cleanupPreviewListeners();
            this._previewKey = null;
            if (this._previewContainer) this._previewContainer.style.display = 'none';
        }

        _cleanupPreviewListeners() {
            if (this._previewOutputHandler && this._previewKey) {
                const s = this.manager.sessions.get(this._previewKey);
                s?.socket?.off('output', this._previewOutputHandler);
                this._previewOutputHandler = null;
            }
        }
    }

    // =========================================================================
    // TerminalPanel — chrome wrapper
    // =========================================================================

    class TerminalPanel {
        constructor(terminalManager) {
            this.panel = document.getElementById('terminal-panel');
            this.header = document.getElementById('terminal-header');
            this.toggleBtn = document.getElementById('terminal-toggle');
            this.zenBtn = document.getElementById('terminal-zen-btn');
            this.explorerToggleBtn = document.getElementById('terminal-explorer-toggle');
            this.copilotCmdBtn = document.getElementById('copilot-cmd-btn');
            this.resizeHandle = document.getElementById('terminal-resize-handle');
            this.explorerResizeHandle = document.getElementById('explorer-resize-handle');
            this.terminalManager = terminalManager;
            this.isExpanded = false;
            this.isZenMode = false;
            this.explorerVisible = true;
            this.explorerWidth = EXPLORER_DEFAULT_WIDTH;
            this.panelHeight = 300;
            this._bindEvents();
        }

        _bindEvents() {
            this.header.addEventListener('click', (e) => {
                if (e.target.closest('.terminal-actions, .terminal-status, .terminal-header-center')) return;
                this.toggle();
            });
            this.toggleBtn.addEventListener('click', (e) => { e.stopPropagation(); this.toggle(); });
            this.zenBtn?.addEventListener('click', (e) => { e.stopPropagation(); this.toggleZenMode(); });
            this.explorerToggleBtn?.addEventListener('click', (e) => { e.stopPropagation(); this.toggleExplorer(); });
            this.copilotCmdBtn?.addEventListener('click', (e) => { e.stopPropagation(); this._insertCopilotCommand(); });
            document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && this.isZenMode) this.toggleZenMode(); });

            this._initResize();
            this._initExplorerResize();
            this._restoreExplorerState();
        }

        // -- Panel resize -----------------------------------------------------

        _initResize() {
            this.resizeHandle.addEventListener('mousedown', (e) => {
                e.preventDefault();
                const startY = e.clientY;
                const startH = this.panel.offsetHeight;
                this.panel.classList.add('resizing');
                document.body.style.cursor = 'ns-resize';
                document.body.style.userSelect = 'none';

                const onMove = (ev) => {
                    this.panelHeight = Math.min(Math.max(startH + (startY - ev.clientY), 100), window.innerHeight - 100);
                    this.panel.style.height = this.panelHeight + 'px';
                    this.terminalManager._resizeAll();
                };
                const onUp = () => {
                    document.removeEventListener('mousemove', onMove);
                    document.removeEventListener('mouseup', onUp);
                    this.panel.classList.remove('resizing');
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                    this.terminalManager.fitActive();
                };
                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
            });
        }

        // -- Collapse / expand ------------------------------------------------

        toggle()  { this.isExpanded ? this.collapse() : this.expand(); }

        expand() {
            if (this.isExpanded) return;
            this.isExpanded = true;
            this.panel.classList.remove('collapsed');
            this.panel.classList.add('expanded');
            this.panel.style.height = this.panelHeight + 'px';
            this.toggleBtn.querySelector('i').className = 'bi bi-chevron-down';
            setTimeout(() => this.terminalManager.fitActive(), 0);
        }

        collapse() {
            if (!this.isExpanded && !this.isZenMode) return;
            if (this.isZenMode) this._exitZenMode();
            this.isExpanded = false;
            this.panel.classList.remove('expanded');
            this.panel.classList.add('collapsed');
            this.panel.style.height = '';
            this.toggleBtn.querySelector('i').className = 'bi bi-chevron-up';
        }

        // -- Zen mode ---------------------------------------------------------

        toggleZenMode() { this.isZenMode ? this._exitZenMode() : this._enterZenMode(); }

        _enterZenMode() {
            if (!this.isExpanded) this.expand();
            this.isZenMode = true;
            this.panel.classList.add('zen-mode');
            this.zenBtn.querySelector('i').className = 'bi bi-fullscreen-exit';
            this.zenBtn.title = 'Exit Zen Mode (ESC)';
            const topMenu = document.querySelector('.top-menu');
            if (topMenu) topMenu.style.display = 'none';
            if (this.appContainer) this.appContainer.style.display = 'none';
            this.terminalManager.fitActive();
        }

        _exitZenMode() {
            this.isZenMode = false;
            this.panel.classList.remove('zen-mode');
            this.panel.style.height = this.panelHeight + 'px';
            this.zenBtn.querySelector('i').className = 'bi bi-arrows-fullscreen';
            this.zenBtn.title = 'Zen Mode';
            const topMenu = document.querySelector('.top-menu');
            if (topMenu) topMenu.style.display = '';
            if (this.appContainer) this.appContainer.style.display = '';
            this.terminalManager.fitActive();
        }

        // -- Explorer toggle / resize -----------------------------------------

        toggleExplorer() {
            const explorer = document.getElementById('session-explorer');
            if (!explorer) return;
            this.explorerVisible = !this.explorerVisible;
            explorer.classList.toggle('collapsed', !this.explorerVisible);
            if (this.explorerResizeHandle) this.explorerResizeHandle.style.display = this.explorerVisible ? '' : 'none';
            try { localStorage.setItem(EXPLORER_COLLAPSED_KEY, String(!this.explorerVisible)); } catch {}
            if (this.explorerVisible) this._updateExplorerWidth(this.explorerWidth);
            setTimeout(() => this.terminalManager.fitActive(), 300);
        }

        _initExplorerResize() {
            const handle = this.explorerResizeHandle;
            if (!handle) return;
            handle.addEventListener('mousedown', (e) => {
                e.preventDefault();
                handle.classList.add('dragging');
                document.body.style.cursor = 'col-resize';
                document.body.style.userSelect = 'none';
                const body = document.getElementById('terminal-body');
                const onMove = (ev) => {
                    const w = Math.max(EXPLORER_MIN_WIDTH, Math.min(EXPLORER_MAX_WIDTH, body.getBoundingClientRect().right - ev.clientX));
                    this.explorerWidth = w;
                    this._updateExplorerWidth(w);
                };
                const onUp = () => {
                    document.removeEventListener('mousemove', onMove);
                    document.removeEventListener('mouseup', onUp);
                    handle.classList.remove('dragging');
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                    try { localStorage.setItem(EXPLORER_WIDTH_KEY, String(this.explorerWidth)); } catch {}
                    this.terminalManager.fitActive();
                };
                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
            });
        }

        _restoreExplorerState() {
            const explorer = document.getElementById('session-explorer');
            if (!explorer) return;
            try {
                const w = parseInt(localStorage.getItem(EXPLORER_WIDTH_KEY), 10);
                if (!isNaN(w)) {
                    this.explorerWidth = Math.max(EXPLORER_MIN_WIDTH, Math.min(EXPLORER_MAX_WIDTH, w));
                    this._updateExplorerWidth(this.explorerWidth);
                }
            } catch {}
            try {
                if (localStorage.getItem(EXPLORER_COLLAPSED_KEY) === 'true') {
                    this.explorerVisible = false;
                    explorer.classList.add('collapsed');
                    if (this.explorerResizeHandle) this.explorerResizeHandle.style.display = 'none';
                }
            } catch {}
        }

        _updateExplorerWidth(width) {
            const explorer = document.getElementById('session-explorer');
            if (!explorer) return;
            const px = width + 'px';
            explorer.style.width = px;
            explorer.style.minWidth = px;
            explorer.style.maxWidth = px;
            const preview = document.querySelector('.session-preview');
            if (preview) preview.style.right = px;
        }

        // -- Copilot command --------------------------------------------------

        _insertCopilotCommand() {
            if (this.terminalManager.sessions.size === 0) this.terminalManager.addSession();
            const s = this.terminalManager._getActiveSession();
            if (!s) return;
            this.terminalManager._sendWithTypingEffect(s.key, 'copilot --allow-all-tools --allow-all-paths --allow-all-urls', null);
        }
    }

    // =========================================================================
    // Export
    // =========================================================================

    window.TerminalManager = TerminalManager;
    window.TerminalPanel = TerminalPanel;
    window.SessionExplorer = SessionExplorer;
})();
