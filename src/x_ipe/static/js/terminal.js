/**
 * Terminal Manager
 * FEATURE-005: Interactive Console
 * FEATURE-029-A: Session Explorer Core
 * 
 * Based on sample-root implementation.
 * Manages multiple xterm.js terminals with Socket.IO.
 * Session Explorer provides a right-side panel for up to 10 sessions.
 */

(function() {
    'use strict';

    const SESSION_KEY = 'terminal_session_ids';
    const SESSION_NAMES_KEY = 'terminal_session_names';
    const MAX_SESSIONS = 10;

    /**
     * Debounce utility
     */
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    /**
     * Terminal configuration - matches sample-root exactly
     */
    const terminalConfig = {
        cursorBlink: true,
        cursorStyle: 'block',
        fontSize: 14,
        fontFamily: 'Menlo, Monaco, "Courier New", monospace',
        scrollback: 1000,
        scrollOnUserInput: false,  // Disable auto-scroll when pressing up/down arrows
        allowProposedApi: true,
        windowsPty: {
            backend: undefined,
            buildNumber: undefined
        },
        theme: {
            background: '#1e1e1e',
            foreground: '#d4d4d4',
            cursor: '#ffffff',
            cursorAccent: '#000000',
            selection: 'rgba(255, 255, 255, 0.3)',
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
    };

    /**
     * TerminalManager - Manages multiple terminal sessions
     * Refactored from array-based (2 panes) to Map-based (10 sessions)
     */
    class TerminalManager {
        constructor(contentContainerId) {
            // Map<string, SessionData> where key is a local session key (s0, s1, ...)
            this.sessions = new Map();
            this.activeSessionKey = null;
            this._sessionCounter = 0;
            
            this.contentContainer = document.getElementById(contentContainerId);
            this.statusIndicator = document.getElementById('terminal-status-indicator');
            this.statusText = document.getElementById('terminal-status-text');
            
            // Session Explorer
            this.explorer = null;
            
            // Track if initial fit has been done (for containers that start hidden)
            this._initialFitDone = false;
            
            this._setupEventListeners();
            this._setupResizeObserver();
        }

        /**
         * Setup ResizeObserver to detect when terminal container becomes visible
         */
        _setupResizeObserver() {
            if (!this.contentContainer || typeof ResizeObserver === 'undefined') return;
            
            this._resizeObserver = new ResizeObserver(debounce((entries) => {
                for (const entry of entries) {
                    const { width, height } = entry.contentRect;
                    if (width > 0 && height > 0) {
                        console.log(`[Terminal] Container resized to ${width}x${height} - fitting active`);
                        this._fitActiveSession();
                        if (!this._initialFitDone && this.sessions.size > 0) {
                            this._initialFitDone = true;
                        }
                    }
                }
            }, 50));
            
            this._resizeObserver.observe(this.contentContainer);
        }

        _setupEventListeners() {
            // Window resize - fit active session (debounced)
            window.addEventListener('resize', debounce(() => this._fitActiveSession(), 150));
            
            // Handle page visibility changes
            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'visible') {
                    console.log('[Terminal] Tab became visible - checking connections');
                    this._checkAndReconnectAll();
                } else {
                    console.log('[Terminal] Tab hidden - connections will stay alive');
                }
            });
            
            window.addEventListener('focus', () => {
                console.log('[Terminal] Window focused - checking connections');
                this._checkAndReconnectAll();
            });
        }
        
        _checkAndReconnectAll() {
            for (const [key, session] of this.sessions) {
                if (session.socket && !session.socket.connected) {
                    console.log(`[Terminal ${session.name}] Reconnecting after visibility change`);
                    session.socket.connect();
                }
            }
        }

        /**
         * Initialize terminals - restore sessions or create first one
         */
        initialize() {
            const storedIds = this._getStoredSessionIds();
            const storedNames = this._getStoredSessionNames();
            if (storedIds.length > 0) {
                storedIds.forEach((id, i) => {
                    const name = storedNames[id] || this._getNextSessionName();
                    this.addSession(id, name);
                });
            } else {
                this.addSession();
            }
        }

        /**
         * Add a new session
         * @param {string|null} existingSessionId - Backend session ID to reconnect
         * @param {string|null} name - Display name for explorer
         * @returns {string} session key
         */
        addSession(existingSessionId = null, name = null) {
            if (this.sessions.size >= MAX_SESSIONS) {
                if (this.explorer) this.explorer.showToast('Maximum 10 sessions reached');
                console.warn('[Terminal] Maximum sessions reached');
                return null;
            }

            const key = `s${this._sessionCounter++}`;
            const sessionName = name || this._getNextSessionName();
            
            // Create session container DOM
            const container = this._createSessionContainer(key);
            this.contentContainer.appendChild(container);
            
            // Create terminal
            const terminal = new Terminal(terminalConfig);
            const fitAddon = new FitAddon.FitAddon();
            terminal.loadAddon(fitAddon);
            
            if (typeof Unicode11Addon !== 'undefined') {
                const unicode11Addon = new Unicode11Addon.Unicode11Addon();
                terminal.loadAddon(unicode11Addon);
                terminal.unicode.activeVersion = '11';
            }
            
            // Open terminal in container
            terminal.open(container);
            
            // Store session data
            const sessionData = {
                key,
                sessionId: existingSessionId,
                name: sessionName,
                terminal,
                fitAddon,
                socket: null,
                container,
                isActive: false
            };
            this.sessions.set(key, sessionData);
            
            // Prevent scroll-to-top when typing
            this._setupScrollPrevention(terminal, container);
            
            // Create socket
            sessionData.socket = this._createSocket(key, existingSessionId);
            
            // Handle input
            terminal.onData(data => {
                if (sessionData.socket && sessionData.socket.connected) {
                    const scrollX = window.scrollX;
                    const scrollY = window.scrollY;
                    sessionData.socket.emit('input', data);
                    terminal.scrollToBottom();
                    if (window.scrollX !== scrollX || window.scrollY !== scrollY) {
                        window.scrollTo(scrollX, scrollY);
                    }
                }
            });
            
            // Switch to new session
            this.switchSession(key);
            
            // Update explorer
            if (this.explorer) {
                this.explorer.addSessionBar(key, sessionName);
                this.explorer.updateActiveIndicator(this.activeSessionKey);
                this.explorer.setAddButtonEnabled(this.sessions.size < MAX_SESSIONS);
            }
            
            this._saveSessionIds();
            this._saveSessionNames();
            
            console.log(`[Terminal] Added session "${sessionName}" (${key})`);
            return key;
        }

        /**
         * Create session container DOM element
         */
        _createSessionContainer(key) {
            const container = document.createElement('div');
            container.className = 'terminal-session-container';
            container.dataset.sessionKey = key;
            return container;
        }

        /**
         * Remove a session
         */
        removeSession(key) {
            const session = this.sessions.get(key);
            if (!session) return;

            if (session.socket) session.socket.disconnect();
            if (session.terminal) session.terminal.dispose();
            if (session.container) session.container.remove();
            
            this.sessions.delete(key);
            
            // Update explorer
            if (this.explorer) {
                this.explorer.removeSessionBar(key);
                this.explorer.setAddButtonEnabled(this.sessions.size < MAX_SESSIONS);
            }
            
            if (this.sessions.size > 0) {
                // Switch to another session
                if (this.activeSessionKey === key) {
                    const nextKey = this.sessions.keys().next().value;
                    this.switchSession(nextKey);
                }
                if (this.explorer) {
                    this.explorer.updateActiveIndicator(this.activeSessionKey);
                }
            } else {
                this.activeSessionKey = null;
                this.addSession();
            }
            
            this._saveSessionIds();
            this._saveSessionNames();
            this._updateStatus();
            
            console.log(`[Terminal] Removed session "${session.name}" (${key})`);
        }

        /**
         * Rename a session
         */
        renameSession(key, newName) {
            const session = this.sessions.get(key);
            if (!session) return;
            session.name = newName;
            this._saveSessionNames();
            console.log(`[Terminal] Renamed session ${key} to "${newName}"`);
        }

        /**
         * Switch active session
         */
        switchSession(key) {
            const session = this.sessions.get(key);
            if (!session) return;

            // Hide all containers, show target
            for (const [k, s] of this.sessions) {
                s.container.classList.remove('active');
                s.isActive = false;
            }
            session.container.classList.add('active');
            session.isActive = true;
            this.activeSessionKey = key;
            
            // Update explorer indicator
            if (this.explorer) {
                this.explorer.updateActiveIndicator(key);
            }
            
            // Fit active terminal after display change
            this.fitActive();
            
            // Focus without scroll
            this._focusWithoutScroll(session.terminal);
        }

        /**
         * Get active session data
         */
        _getActiveSession() {
            return this.activeSessionKey ? this.sessions.get(this.activeSessionKey) : null;
        }

        /**
         * Fit the active terminal
         */
        _fitActiveSession() {
            const session = this._getActiveSession();
            if (!session) return;
            try {
                session.fitAddon.fit();
                const dims = session.fitAddon.proposeDimensions();
                if (dims && session.socket && session.socket.connected) {
                    session.socket.emit('resize', { rows: dims.rows, cols: dims.cols });
                }
            } catch (e) {}
        }

        /**
         * Fit active terminal - immediate + double RAF backup
         */
        fitActive() {
            this._fitActiveSession();
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    this._fitActiveSession();
                    setTimeout(() => this._fitActiveSession(), 50);
                });
            });
        }

        // Legacy aliases for backward compatibility
        fitAll() { this.fitActive(); }
        _doFit() { this._fitActiveSession(); }
        _resizeAll() { this._fitActiveSession(); }

        /**
         * Focus terminal without triggering browser scroll-to-focus behavior
         */
        _focusWithoutScroll(terminal) {
            if (!terminal) return;
            
            const scrollX = window.scrollX;
            const scrollY = window.scrollY;
            const contentBody = document.querySelector('.content-body');
            const contentBodyScroll = contentBody?.scrollTop || 0;
            
            const viewport = terminal.element?.querySelector('.xterm-viewport');
            const terminalScrollTop = viewport?.scrollTop || 0;
            
            try {
                const textarea = terminal.element?.querySelector('.xterm-helper-textarea');
                if (textarea) {
                    textarea.focus({ preventScroll: true });
                } else {
                    terminal.focus();
                }
            } catch (e) {
                terminal.focus();
            }
            
            if (window.scrollX !== scrollX || window.scrollY !== scrollY) {
                window.scrollTo(scrollX, scrollY);
            }
            if (contentBody && contentBody.scrollTop !== contentBodyScroll) {
                contentBody.scrollTop = contentBodyScroll;
            }
            if (viewport && viewport.scrollTop !== terminalScrollTop) {
                viewport.scrollTop = terminalScrollTop;
            }
        }

        /**
         * Setup scroll prevention for terminal's hidden textarea
         */
        _setupScrollPrevention(terminal, container) {
            requestAnimationFrame(() => {
                const textarea = terminal.element?.querySelector('.xterm-helper-textarea');
                if (!textarea) return;
                
                const contentBody = document.querySelector('.content-body');
                let savedScrollX = 0, savedScrollY = 0, savedContentBodyScroll = 0;
                
                const saveScrollPositions = () => {
                    savedScrollX = window.scrollX;
                    savedScrollY = window.scrollY;
                    if (contentBody) savedContentBodyScroll = contentBody.scrollTop;
                };
                
                const restoreScrollPositions = () => {
                    if (window.scrollX !== savedScrollX || window.scrollY !== savedScrollY) {
                        window.scrollTo(savedScrollX, savedScrollY);
                    }
                    if (contentBody && contentBody.scrollTop !== savedContentBodyScroll) {
                        contentBody.scrollTop = savedContentBodyScroll;
                    }
                };
                
                textarea.addEventListener('focus', () => {
                    saveScrollPositions();
                    queueMicrotask(restoreScrollPositions);
                    requestAnimationFrame(restoreScrollPositions);
                }, { capture: true });
                
                textarea.addEventListener('keydown', () => {
                    saveScrollPositions();
                    queueMicrotask(restoreScrollPositions);
                    requestAnimationFrame(restoreScrollPositions);
                }, { capture: true });
                
                textarea.addEventListener('input', () => {
                    saveScrollPositions();
                    queueMicrotask(restoreScrollPositions);
                    requestAnimationFrame(restoreScrollPositions);
                }, { capture: true });
                
                container.addEventListener('mousedown', () => {
                    saveScrollPositions();
                    requestAnimationFrame(restoreScrollPositions);
                });
                
                let scrollCheckTimeout = null;
                textarea.addEventListener('keypress', () => {
                    if (scrollCheckTimeout) clearTimeout(scrollCheckTimeout);
                    scrollCheckTimeout = setTimeout(() => {
                        if (document.activeElement === textarea) restoreScrollPositions();
                    }, 10);
                }, { capture: true });
            });
        }

        /**
         * Create Socket.IO connection for a session
         */
        _createSocket(sessionKey, existingSessionId) {
            const socket = io({
                transports: ['websocket'],
                upgrade: false,
                reconnection: true,
                reconnectionAttempts: Infinity,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 30000,
                randomizationFactor: 0.5,
                timeout: 60000,
                forceNew: false,
                pingTimeout: 300000,
                pingInterval: 60000
            });
            
            let lastPongTime = Date.now();
            let healthCheckInterval = null;
            
            const getSession = () => this.sessions.get(sessionKey);
            
            const startHealthCheck = () => {
                if (healthCheckInterval) clearInterval(healthCheckInterval);
                healthCheckInterval = setInterval(() => {
                    const timeSincePong = Date.now() - lastPongTime;
                    const session = getSession();
                    if (timeSincePong > 180000 && socket.connected && session) {
                        console.warn(`[Terminal ${session.name}] Connection may be stale (${Math.round(timeSincePong/1000)}s since last pong)`);
                    }
                }, 60000);
            };
            
            const stopHealthCheck = () => {
                if (healthCheckInterval) {
                    clearInterval(healthCheckInterval);
                    healthCheckInterval = null;
                }
            };

            socket.on('connect', () => {
                const session = getSession();
                if (!session) return;
                console.log(`[Terminal ${session.name}] Connected`);
                lastPongTime = Date.now();
                startHealthCheck();
                this._updateStatus();
                
                const dims = session.fitAddon?.proposeDimensions();
                socket.emit('attach', {
                    session_id: existingSessionId,
                    rows: dims ? dims.rows : 24,
                    cols: dims ? dims.cols : 80
                });
            });

            socket.on('session_id', sessionId => {
                const session = getSession();
                if (session) {
                    session.sessionId = sessionId;
                    this._saveSessionIds();
                }
            });

            socket.on('new_session', data => {
                const session = getSession();
                if (session) {
                    session.terminal.write('\x1b[32m[New session started]\x1b[0m\r\n');
                    session.sessionId = data.session_id;
                    this._saveSessionIds();
                }
            });

            socket.on('reconnected', () => {
                const session = getSession();
                if (session) {
                    session.terminal.write('\x1b[33m[Reconnected to session]\x1b[0m\r\n');
                }
            });

            socket.on('output', data => {
                const session = getSession();
                if (session) {
                    session.terminal.write(data);
                    session.terminal.scrollToBottom();
                }
            });
            
            socket.io.engine.on('pong', () => {
                lastPongTime = Date.now();
            });

            socket.on('disconnect', reason => {
                const session = getSession();
                const name = session ? session.name : sessionKey;
                console.log(`[Terminal ${name}] Disconnected: ${reason}`);
                stopHealthCheck();
                this._updateStatus();
                
                if (reason !== 'io client disconnect' && session) {
                    if (reason === 'ping timeout') {
                        session.terminal.write('\r\n\x1b[31m[Connection timeout - reconnecting...]\x1b[0m\r\n');
                    } else if (reason === 'transport close' || reason === 'transport error') {
                        session.terminal.write('\r\n\x1b[31m[Connection lost - reconnecting...]\x1b[0m\r\n');
                    }
                }
            });

            socket.io.on('reconnect', attempt => {
                const session = getSession();
                if (!session) return;
                console.log(`[Terminal ${session.name}] Reconnected after ${attempt} attempts`);
                lastPongTime = Date.now();
                startHealthCheck();
                this._updateStatus();
                
                const dims = session.fitAddon?.proposeDimensions();
                socket.emit('attach', {
                    session_id: session.sessionId,
                    rows: dims ? dims.rows : 24,
                    cols: dims ? dims.cols : 80
                });
            });

            socket.io.on('reconnect_attempt', attempt => {
                const session = getSession();
                if (!session) return;
                console.log(`[Terminal ${session.name}] Reconnection attempt ${attempt}`);
                if (attempt === 1) {
                    session.terminal.write('\x1b[33m[Reconnecting...]\x1b[0m\r\n');
                }
            });

            socket.io.on('reconnect_failed', () => {
                const session = getSession();
                stopHealthCheck();
                if (session) {
                    session.terminal.write('\r\n\x1b[31m[Connection lost - please refresh page]\x1b[0m\r\n');
                }
            });

            socket.on('connect_error', error => {
                const session = getSession();
                const name = session ? session.name : sessionKey;
                console.error(`[Terminal ${name}] Connection error:`, error.message || error);
                this._updateStatus();
            });

            return socket;
        }

        _updateStatus() {
            let connected = 0, total = 0;
            for (const [, session] of this.sessions) {
                total++;
                if (session.socket && session.socket.connected) connected++;
            }

            if (this.statusIndicator) {
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
        }

        // --- Session name helpers ---
        _getNextSessionName() {
            const usedNumbers = new Set();
            for (const [, session] of this.sessions) {
                const match = session.name.match(/^Session (\d+)$/);
                if (match) usedNumbers.add(parseInt(match[1]));
            }
            let n = 1;
            while (usedNumbers.has(n)) n++;
            return `Session ${n}`;
        }

        // --- Persistence ---
        _getStoredSessionIds() {
            try {
                const stored = localStorage.getItem(SESSION_KEY);
                return stored ? JSON.parse(stored) : [];
            } catch (e) {
                return [];
            }
        }

        _saveSessionIds() {
            try {
                const ids = [];
                for (const [, session] of this.sessions) {
                    if (session.sessionId) ids.push(session.sessionId);
                }
                localStorage.setItem(SESSION_KEY, JSON.stringify(ids));
            } catch (e) {}
        }

        _getStoredSessionNames() {
            try {
                const stored = localStorage.getItem(SESSION_NAMES_KEY);
                return stored ? JSON.parse(stored) : {};
            } catch (e) {
                return {};
            }
        }

        _saveSessionNames() {
            try {
                const names = {};
                for (const [, session] of this.sessions) {
                    if (session.sessionId) names[session.sessionId] = session.name;
                }
                localStorage.setItem(SESSION_NAMES_KEY, JSON.stringify(names));
            } catch (e) {}
        }

        // --- Legacy compatibility: index-based accessors ---
        // These provide backward compatibility for TerminalPanel and Copilot commands
        get terminals() {
            return Array.from(this.sessions.values()).map(s => s.terminal);
        }
        get sockets() {
            return Array.from(this.sessions.values()).map(s => s.socket);
        }
        get activeIndex() {
            if (!this.activeSessionKey) return -1;
            let i = 0;
            for (const key of this.sessions.keys()) {
                if (key === this.activeSessionKey) return i;
                i++;
            }
            return -1;
        }

        // Legacy method aliases
        addTerminal(existingSessionId = null) {
            return this.addSession(existingSessionId) ? this.activeIndex : -1;
        }
        setFocus(index) {
            const keys = Array.from(this.sessions.keys());
            if (index >= 0 && index < keys.length) {
                this.switchSession(keys[index]);
            }
        }

        /**
         * Get the currently focused terminal for voice input injection (FEATURE-021)
         */
        getFocusedTerminal() {
            const session = this._getActiveSession();
            if (session) {
                return {
                    terminal: session.terminal,
                    socket: session.socket,
                    sessionId: session.sessionId,
                    sendInput: (text) => {
                        if (session.socket && session.sessionId) {
                            session.socket.emit('input', text);
                        }
                    }
                };
            }
            return null;
        }

        /**
         * Get first connected socket for voice input (FEATURE-021)
         */
        get socket() {
            for (const [, session] of this.sessions) {
                if (session.socket && session.socket.connected) return session.socket;
            }
            const first = this.sessions.values().next().value;
            return first ? first.socket : null;
        }

        /**
         * Send copilot prompt without pressing Enter (FEATURE-021)
         */
        sendCopilotPromptCommandNoEnter(promptCommand) {
            if (this.sessions.size === 0) this.addSession();
            const session = this._getActiveSession();
            if (!session) return;
            const escapedPrompt = promptCommand.replace(/"/g, '\\"');
            const copilotCommand = `copilot --allow-all-tools --allow-all-paths --allow-all-urls -i "${escapedPrompt}"`;
            // Use typing effect but don't send Enter
            if (!session.socket || !session.socket.connected) return;
            const chars = copilotCommand.split('');
            let i = 0;
            const typeChar = () => {
                if (i < chars.length) {
                    session.socket.emit('input', chars[i]);
                    i++;
                    setTimeout(typeChar, 30 + Math.random() * 50);
                }
            };
            typeChar();
        }

        // --- Copilot integration ---
        sendCopilotRefineCommand(filePath) {
            this._sendCopilotWithPrompt(`refine the idea ${filePath}`);
        }

        sendCopilotPromptCommand(promptCommand) {
            this._sendCopilotWithPrompt(promptCommand);
        }

        _sendCopilotWithPrompt(prompt) {
            if (this.sessions.size === 0) {
                this.addSession();
            }
            const session = this._getActiveSession();
            if (!session) return;
            
            const escapedPrompt = prompt.replace(/"/g, '\\"');
            const copilotCommand = `copilot --allow-all-tools --allow-all-paths --allow-all-urls -i "${escapedPrompt}"`;
            this._sendWithTypingEffect(session.key, copilotCommand, null);
        }

        _waitForCopilotReady(sessionKey, callback, maxAttempts = 30) {
            const session = this.sessions.get(sessionKey);
            if (!session) return;
            let attempts = 0;
            const pollInterval = 200;
            
            const checkReady = () => {
                attempts++;
                if (this._isCopilotPromptReady(sessionKey)) {
                    setTimeout(callback, 300);
                    return;
                }
                if (attempts >= maxAttempts) {
                    console.warn('Copilot CLI initialization timeout, proceeding anyway');
                    setTimeout(callback, 500);
                    return;
                }
                setTimeout(checkReady, pollInterval);
            };
            setTimeout(checkReady, 500);
        }

        _isCopilotPromptReady(sessionKey) {
            const session = this.sessions.get(sessionKey);
            if (!session) return false;
            
            const buffer = session.terminal.buffer.active;
            for (let i = Math.max(0, buffer.cursorY - 3); i <= buffer.cursorY; i++) {
                const line = buffer.getLine(i);
                if (line) {
                    const text = line.translateToString(true);
                    if (text.match(/^>[\s]*$/) || text.includes('⏺') || text.match(/>\s*$/)) {
                        return true;
                    }
                }
            }
            return false;
        }

        _isInCopilotMode(sessionKeyOrIndex) {
            let session;
            if (typeof sessionKeyOrIndex === 'number') {
                const keys = Array.from(this.sessions.keys());
                session = this.sessions.get(keys[sessionKeyOrIndex]);
            } else {
                session = this.sessions.get(sessionKeyOrIndex);
            }
            if (!session) return false;
            
            const buffer = session.terminal.buffer.active;
            for (let i = Math.max(0, buffer.cursorY - 5); i <= buffer.cursorY; i++) {
                const line = buffer.getLine(i);
                if (line) {
                    const text = line.translateToString(true);
                    if (text.includes('copilot>') || text.includes('Copilot') || text.includes('⏺')) {
                        return true;
                    }
                }
            }
            return false;
        }

        /**
         * Send text with typing simulation effect
         */
        _sendWithTypingEffect(sessionKey, text, callback) {
            const session = this.sessions.get(sessionKey);
            if (!session || !session.socket || !session.socket.connected) return;
            
            const chars = text.split('');
            let i = 0;
            
            const typeChar = () => {
                if (i < chars.length) {
                    session.socket.emit('input', chars[i]);
                    i++;
                    const delay = 30 + Math.random() * 50;
                    setTimeout(typeChar, delay);
                } else {
                    setTimeout(() => {
                        session.socket.emit('input', '\r');
                        if (callback) callback();
                    }, 100);
                }
            };
            typeChar();
        }
    }

    /**
     * SessionExplorer - Right-side panel for session management
     */
    class SessionExplorer {
        constructor(terminalManager) {
            this.manager = terminalManager;
            this.listEl = document.getElementById('session-list');
            this.addBtn = document.getElementById('explorer-add-btn');
            
            // Register with manager
            this.manager.explorer = this;

            // FEATURE-029-C: Preview state
            this._previewContainer = null;
            this._previewTerminal = null;
            this._previewFitAddon = null;
            this._previewKey = null;
            this._hoverTimer = null;
            this._graceTimer = null;
            this._previewOutputHandler = null;
            
            this._bindEvents();
        }

        _bindEvents() {
            if (this.addBtn) {
                this.addBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.manager.addSession();
                });
            }
        }

        addSessionBar(key, name) {
            const bar = document.createElement('div');
            bar.className = 'session-bar';
            bar.dataset.sessionKey = key;
            bar.dataset.active = 'false';
            
            const dot = document.createElement('span');
            dot.className = 'session-status-dot';
            
            const nameSpan = document.createElement('span');
            nameSpan.className = 'session-name';
            nameSpan.textContent = name;

            const renameBtn = document.createElement('button');
            renameBtn.className = 'session-action-btn rename-btn';
            renameBtn.title = 'Rename';
            renameBtn.innerHTML = '<i class="bi bi-pencil"></i>';
            renameBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.startRename(key);
            });

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'session-action-btn delete-btn';
            deleteBtn.title = 'Delete';
            deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.manager.removeSession(key);
            });
            
            bar.appendChild(dot);
            bar.appendChild(nameSpan);
            bar.appendChild(renameBtn);
            bar.appendChild(deleteBtn);
            
            bar.addEventListener('click', () => {
                this.manager.switchSession(key);
            });

            // FEATURE-029-C: Hover preview triggers
            bar.addEventListener('mouseenter', () => {
                if (bar.dataset.active === 'true') return;
                clearTimeout(this._graceTimer);
                this._hoverTimer = setTimeout(() => this._showPreview(key, bar), 500);
            });
            bar.addEventListener('mouseleave', () => {
                clearTimeout(this._hoverTimer);
                this._graceTimer = setTimeout(() => this._dismissPreview(), 100);
            });
            
            this.listEl.appendChild(bar);
        }

        removeSessionBar(key) {
            if (this._previewKey === key) this._dismissPreview();
            const bar = this.listEl.querySelector(`[data-session-key="${key}"]`);
            if (bar) bar.remove();
        }

        updateActiveIndicator(activeKey) {
            this.listEl.querySelectorAll('.session-bar').forEach(bar => {
                bar.dataset.active = (bar.dataset.sessionKey === activeKey) ? 'true' : 'false';
            });
        }

        setAddButtonEnabled(enabled) {
            if (this.addBtn) this.addBtn.disabled = !enabled;
        }

        startRename(key) {
            const bar = this.listEl.querySelector(`[data-session-key="${key}"]`);
            if (!bar) return;
            const nameSpan = bar.querySelector('.session-name');
            if (!nameSpan || nameSpan.tagName === 'INPUT') return;

            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'session-name-input';
            input.value = nameSpan.textContent;
            const originalName = nameSpan.textContent;

            let done = false;
            const confirm = () => {
                if (done) return;
                done = true;
                const newName = input.value.trim();
                if (newName && newName !== originalName) {
                    this.manager.renameSession(key, newName);
                }
                const span = document.createElement('span');
                span.className = 'session-name';
                span.textContent = newName || originalName;
                input.replaceWith(span);
            };

            const cancel = () => {
                if (done) return;
                done = true;
                const span = document.createElement('span');
                span.className = 'session-name';
                span.textContent = originalName;
                input.replaceWith(span);
            };

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') { e.preventDefault(); confirm(); }
                if (e.key === 'Escape') { e.preventDefault(); cancel(); }
            });
            input.addEventListener('blur', () => confirm());

            nameSpan.replaceWith(input);
            input.focus();
            input.select();
        }

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

        // FEATURE-029-C: Preview methods
        _initPreviewContainer() {
            if (this._previewContainer) return;

            this._previewContainer = document.createElement('div');
            this._previewContainer.className = 'session-preview';
            this._previewContainer.style.display = 'none';

            const header = document.createElement('div');
            header.className = 'session-preview-header';
            this._previewContainer.appendChild(header);

            const body = document.createElement('div');
            body.className = 'session-preview-body';
            this._previewContainer.appendChild(body);

            this._previewContainer.addEventListener('mouseenter', () => {
                clearTimeout(this._graceTimer);
            });
            this._previewContainer.addEventListener('mouseleave', () => {
                this._graceTimer = setTimeout(() => this._dismissPreview(), 100);
            });
            this._previewContainer.addEventListener('click', () => {
                if (this._previewKey) {
                    const key = this._previewKey;
                    this._dismissPreview();
                    this.manager.switchSession(key);
                }
            });

            document.getElementById('terminal-panel').appendChild(this._previewContainer);

            this._previewTerminal = new Terminal({
                disableStdin: true,
                scrollback: 500,
                fontSize: 12,
                fontFamily: terminalConfig.fontFamily,
                theme: terminalConfig.theme,
                cursorBlink: false
            });
            this._previewFitAddon = new FitAddon.FitAddon();
            this._previewTerminal.loadAddon(this._previewFitAddon);
            this._previewTerminal.open(body);
        }

        _showPreview(key, barElement) {
            const session = this.manager.sessions.get(key);
            if (!session) return;

            this._initPreviewContainer();

            if (this._previewKey && this._previewKey !== key) {
                this._cleanupPreviewListeners();
            }
            this._previewKey = key;

            this._previewContainer.querySelector('.session-preview-header').textContent = session.name;

            this._previewTerminal.clear();

            const srcBuffer = session.terminal.buffer.active;
            const lines = [];
            for (let i = 0; i < srcBuffer.length; i++) {
                const line = srcBuffer.getLine(i);
                if (line) lines.push(line.translateToString(true));
            }
            if (lines.length > 0) {
                this._previewTerminal.write(lines.join('\r\n'));
            }
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
            try { this._previewFitAddon.fit(); } catch(e) {}
        }

        _dismissPreview() {
            clearTimeout(this._hoverTimer);
            clearTimeout(this._graceTimer);
            this._cleanupPreviewListeners();
            this._previewKey = null;
            if (this._previewContainer) {
                this._previewContainer.style.display = 'none';
            }
        }

        _cleanupPreviewListeners() {
            if (this._previewOutputHandler && this._previewKey) {
                const session = this.manager.sessions.get(this._previewKey);
                if (session && session.socket) {
                    session.socket.off('output', this._previewOutputHandler);
                }
                this._previewOutputHandler = null;
            }
        }
    }

    /**
     * TerminalPanel - Collapsible panel wrapper
     */
    class TerminalPanel {
        constructor(terminalManager) {
            this.panel = document.getElementById('terminal-panel');
            this.header = document.getElementById('terminal-header');
            this.toggleBtn = document.getElementById('terminal-toggle');
            this.zenBtn = document.getElementById('terminal-zen-btn');
            this.copilotCmdBtn = document.getElementById('copilot-cmd-btn');
            this.resizeHandle = document.getElementById('terminal-resize-handle');
            this.terminalManager = terminalManager;

            this.isExpanded = false;
            this.isZenMode = false;
            this.panelHeight = 300;

            this._bindEvents();
        }

        _bindEvents() {
            this.header.addEventListener('click', (e) => {
                if (e.target.closest('.terminal-actions') || 
                    e.target.closest('.terminal-status') ||
                    e.target.closest('.terminal-header-center')) return;
                this.toggle();
            });

            this.toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggle();
            });

            if (this.zenBtn) {
                this.zenBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.toggleZenMode();
                });
            }

            if (this.copilotCmdBtn) {
                this.copilotCmdBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this._insertCopilotCommand();
                });
            }

            this._initResize();

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isZenMode) {
                    this.toggleZenMode();
                }
            });
        }

        _initResize() {
            let startY, startHeight;

            this.resizeHandle.addEventListener('mousedown', (e) => {
                e.preventDefault();
                startY = e.clientY;
                startHeight = this.panel.offsetHeight;
                
                this.panel.classList.add('resizing');
                document.body.style.cursor = 'ns-resize';
                document.body.style.userSelect = 'none';

                const onMove = (e) => {
                    const delta = startY - e.clientY;
                    this.panelHeight = Math.min(Math.max(startHeight + delta, 100), window.innerHeight - 100);
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

        toggle() {
            if (this.isExpanded) {
                this.collapse();
            } else {
                this.expand();
            }
        }

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

            if (this.isZenMode) {
                this._exitZenMode();
            }

            this.isExpanded = false;
            this.panel.classList.remove('expanded');
            this.panel.classList.add('collapsed');
            this.panel.style.height = '';
            this.toggleBtn.querySelector('i').className = 'bi bi-chevron-up';
        }

        toggleZenMode() {
            if (this.isZenMode) {
                this._exitZenMode();
            } else {
                this._enterZenMode();
            }
        }

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

        /**
         * Insert copilot command into active terminal (no Enter)
         */
        _insertCopilotCommand() {
            const copilotCommand = 'copilot --allow-all-tools --allow-all-paths --allow-all-urls';
            
            if (this.terminalManager.sessions.size === 0) {
                this.terminalManager.addSession();
            }
            
            const session = this.terminalManager._getActiveSession();
            if (!session) return;
            
            this.terminalManager._sendWithTypingEffect(session.key, copilotCommand, null);
        }
    }

    // Export to window
    window.TerminalManager = TerminalManager;
    window.TerminalPanel = TerminalPanel;
    window.SessionExplorer = SessionExplorer;

    console.log('[Terminal] Module loaded');
})();
