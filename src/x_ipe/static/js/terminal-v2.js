/**
 * Terminal Manager v2.0
 * FEATURE-005: Interactive Console
 * 
 * Clean rewrite with proper scroll isolation.
 * Architecture: TerminalInstance → PaneManager → PanelController
 */

(function() {
    'use strict';

    // =========================================================================
    // Configuration
    // =========================================================================

    const CONFIG = {
        maxTerminals: 2,
        sessionKey: 'terminal_session_ids',
        
        terminal: {
            cursorBlink: true,
            cursorStyle: 'block',
            fontSize: 14,
            fontFamily: 'Menlo, Monaco, "Courier New", monospace',
            scrollback: 1000,
            allowProposedApi: true,
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
        },
        
        socket: {
            transports: ['websocket'],
            upgrade: false,
            reconnection: true,
            reconnectionAttempts: Infinity,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 30000,
            timeout: 60000,
            pingTimeout: 300000,
            pingInterval: 60000
        }
    };

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

    // =========================================================================
    // TerminalInstance - Single terminal with its socket
    // =========================================================================

    class TerminalInstance {
        constructor(index, sessionId = null) {
            this.index = index;
            this.sessionId = sessionId;
            this.terminal = null;
            this.fitAddon = null;
            this.socket = null;
            this.container = null;
            this.onStatusChange = null;
        }

        /**
         * Initialize terminal in the given container
         */
        mount(container) {
            this.container = container;
            
            // Create xterm instance
            this.terminal = new Terminal(CONFIG.terminal);
            this.fitAddon = new FitAddon.FitAddon();
            this.terminal.loadAddon(this.fitAddon);
            
            // Load Unicode11 for special characters
            if (typeof Unicode11Addon !== 'undefined') {
                const unicode11 = new Unicode11Addon.Unicode11Addon();
                this.terminal.loadAddon(unicode11);
                this.terminal.unicode.activeVersion = '11';
            }
            
            // Open terminal
            this.terminal.open(container);
            
            // Handle input - simple, no scroll manipulation
            this.terminal.onData(data => {
                if (this.socket?.connected) {
                    this.socket.emit('input', data);
                }
            });
            
            // Connect socket
            this._connectSocket();
            
            return this;
        }

        /**
         * Create and configure socket connection
         */
        _connectSocket() {
            this.socket = io(CONFIG.socket);
            
            this.socket.on('connect', () => {
                console.log(`[Terminal ${this.index + 1}] Connected`);
                this._notifyStatus();
                
                const dims = this.fitAddon?.proposeDimensions();
                this.socket.emit('attach', {
                    session_id: this.sessionId,
                    rows: dims?.rows || 24,
                    cols: dims?.cols || 80
                });
            });

            this.socket.on('session_id', id => {
                this.sessionId = id;
            });

            this.socket.on('new_session', data => {
                this.terminal.write('\x1b[32m[New session started]\x1b[0m\r\n');
                this.sessionId = data.session_id;
            });

            this.socket.on('reconnected', () => {
                this.terminal.write('\x1b[33m[Reconnected to session]\x1b[0m\r\n');
            });

            this.socket.on('output', data => {
                this.terminal.write(data);
            });

            this.socket.on('disconnect', reason => {
                console.log(`[Terminal ${this.index + 1}] Disconnected: ${reason}`);
                this._notifyStatus();
                
                if (reason !== 'io client disconnect') {
                    if (reason === 'ping timeout') {
                        this.terminal.write('\r\n\x1b[31m[Connection timeout - reconnecting...]\x1b[0m\r\n');
                    } else if (reason === 'transport close' || reason === 'transport error') {
                        this.terminal.write('\r\n\x1b[31m[Connection lost - reconnecting...]\x1b[0m\r\n');
                    }
                }
            });

            this.socket.io.on('reconnect', attempt => {
                console.log(`[Terminal ${this.index + 1}] Reconnected after ${attempt} attempts`);
                this._notifyStatus();
                
                const dims = this.fitAddon?.proposeDimensions();
                this.socket.emit('attach', {
                    session_id: this.sessionId,
                    rows: dims?.rows || 24,
                    cols: dims?.cols || 80
                });
            });

            this.socket.io.on('reconnect_attempt', attempt => {
                if (attempt === 1) {
                    this.terminal.write('\x1b[33m[Reconnecting...]\x1b[0m\r\n');
                }
            });

            this.socket.io.on('reconnect_failed', () => {
                this.terminal.write('\r\n\x1b[31m[Connection lost - please refresh page]\x1b[0m\r\n');
            });
        }

        /**
         * Focus this terminal
         */
        focus() {
            if (!this.terminal) return;
            
            // Use preventScroll - trust the browser
            const textarea = this.terminal.element?.querySelector('.xterm-helper-textarea');
            if (textarea) {
                textarea.focus({ preventScroll: true });
            } else {
                this.terminal.focus();
            }
        }

        /**
         * Fit terminal to container
         */
        fit() {
            if (!this.fitAddon) return;
            
            try {
                this.fitAddon.fit();
                const dims = this.fitAddon.proposeDimensions();
                if (dims && this.socket?.connected) {
                    this.socket.emit('resize', { rows: dims.rows, cols: dims.cols });
                }
            } catch (e) {
                // Ignore fit errors (e.g., when container not visible)
            }
        }

        /**
         * Check if connected
         */
        get isConnected() {
            return this.socket?.connected || false;
        }

        /**
         * Notify status change callback
         */
        _notifyStatus() {
            if (this.onStatusChange) {
                this.onStatusChange(this.index, this.isConnected);
            }
        }

        /**
         * Clean up resources
         */
        dispose() {
            if (this.socket) {
                this.socket.disconnect();
                this.socket = null;
            }
            if (this.terminal) {
                this.terminal.dispose();
                this.terminal = null;
            }
            this.fitAddon = null;
            this.container = null;
        }
    }

    // =========================================================================
    // PaneManager - Manages multiple terminal panes
    // =========================================================================

    class PaneManager {
        constructor(containerId) {
            this.container = document.getElementById(containerId);
            this.terminals = [];
            this.activeIndex = -1;
            this.onStatusChange = null;

            this._setupResizeObserver();
        }

        _setupResizeObserver() {
            if (!this.container || typeof ResizeObserver === 'undefined') return;

            this._resizeObserver = new ResizeObserver(debounce((entries) => {
                for (const entry of entries) {
                    const { width, height } = entry.contentRect;
                    if (width > 0 && height > 0) {
                        this.fitAll();
                    }
                }
            }, 50));

            this._resizeObserver.observe(this.container);
        }

        /**
         * Initialize with stored sessions or create new
         */
        initialize() {
            const stored = this._loadSessionIds();
            if (stored.length > 0) {
                stored.forEach(id => this.addTerminal(id));
            } else {
                this.addTerminal();
            }
        }

        /**
         * Add a new terminal pane
         */
        addTerminal(sessionId = null) {
            if (this.terminals.length >= CONFIG.maxTerminals) {
                console.warn('[PaneManager] Max terminals reached');
                return -1;
            }

            const index = this.terminals.length;

            // Add splitter before second terminal
            if (index === 1) {
                this._addSplitter();
            }

            // Create pane DOM
            const pane = this._createPane(index);
            this.container.appendChild(pane);

            // Create terminal instance
            const contentDiv = pane.querySelector('.terminal-content');
            const instance = new TerminalInstance(index, sessionId);
            instance.onStatusChange = (idx, connected) => {
                if (this.onStatusChange) this.onStatusChange();
            };
            instance.mount(contentDiv);

            this.terminals.push(instance);
            this.setFocus(index);
            this._saveSessionIds();

            // Fit after layout settles
            requestAnimationFrame(() => this.fitAll());

            console.log(`[PaneManager] Added terminal ${index + 1}`);
            return index;
        }

        /**
         * Close a terminal
         */
        closeTerminal(index) {
            if (index < 0 || index >= this.terminals.length) return;

            // Dispose terminal
            this.terminals[index].dispose();
            this.terminals.splice(index, 1);

            // Remove pane DOM
            const pane = this.container.querySelector(`[data-pane-index="${index}"]`);
            if (pane) pane.remove();

            // Remove splitter if going to single pane
            if (this.terminals.length <= 1) {
                this._removeSplitter();
            }

            // Reindex remaining panes
            this._reindexPanes();

            // Focus another or create new
            if (this.terminals.length > 0) {
                this.setFocus(Math.min(index, this.terminals.length - 1));
                this.fitAll();
            } else {
                this.activeIndex = -1;
                this.addTerminal();
            }

            this._saveSessionIds();
            if (this.onStatusChange) this.onStatusChange();

            console.log(`[PaneManager] Closed terminal ${index + 1}`);
        }

        /**
         * Set focus to a terminal
         */
        setFocus(index) {
            if (index < 0 || index >= this.terminals.length) return;

            // Update visual focus
            this.container.querySelectorAll('.terminal-pane').forEach(p => {
                p.classList.remove('focused');
            });
            const pane = this.container.querySelector(`[data-pane-index="${index}"]`);
            if (pane) pane.classList.add('focused');

            this.activeIndex = index;
            this.terminals[index].focus();
        }

        /**
         * Fit all terminals
         */
        fitAll() {
            this.terminals.forEach(t => t.fit());
        }

        /**
         * Get connection status summary
         */
        getStatus() {
            const connected = this.terminals.filter(t => t.isConnected).length;
            const total = this.terminals.length;
            return { connected, total };
        }

        /**
         * Get session IDs for all terminals
         */
        getSessionIds() {
            return this.terminals.map(t => t.sessionId).filter(id => id !== null);
        }

        /**
         * Create pane DOM element
         */
        _createPane(index) {
            const pane = document.createElement('div');
            pane.className = 'terminal-pane';
            pane.dataset.paneIndex = index;

            pane.innerHTML = `
                <div class="pane-header">
                    <span class="pane-title">Terminal ${index + 1}</span>
                    <button class="close-pane-btn" title="Close terminal">×</button>
                </div>
                <div class="terminal-content" id="terminal-${index}"></div>
            `;

            // Event listeners
            pane.querySelector('.close-pane-btn').addEventListener('click', e => {
                e.stopPropagation();
                this.closeTerminal(parseInt(pane.dataset.paneIndex));
            });

            pane.addEventListener('click', () => {
                this.setFocus(parseInt(pane.dataset.paneIndex));
            });

            return pane;
        }

        /**
         * Add splitter between panes
         */
        _addSplitter() {
            const splitter = document.createElement('div');
            splitter.className = 'pane-splitter';
            splitter.id = 'pane-splitter';

            let startX, leftWidth, rightWidth;

            splitter.addEventListener('mousedown', e => {
                e.preventDefault();
                const panes = this.container.querySelectorAll('.terminal-pane');
                if (panes.length < 2) return;

                startX = e.clientX;
                leftWidth = panes[0].offsetWidth;
                rightWidth = panes[1].offsetWidth;

                this.container.classList.add('dragging-splitter');
                document.body.style.cursor = 'ew-resize';
                document.body.style.userSelect = 'none';

                const onMove = e => {
                    const delta = e.clientX - startX;
                    const total = leftWidth + rightWidth;
                    const minWidth = 100;

                    let newLeft = Math.max(minWidth, Math.min(total - minWidth, leftWidth + delta));
                    let newRight = total - newLeft;

                    panes[0].style.flex = `0 0 ${newLeft}px`;
                    panes[1].style.flex = `0 0 ${newRight}px`;
                    this.fitAll();
                };

                const onUp = () => {
                    document.removeEventListener('mousemove', onMove);
                    document.removeEventListener('mouseup', onUp);
                    this.container.classList.remove('dragging-splitter');
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                    this.fitAll();
                };

                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
            });

            const firstPane = this.container.querySelector('.terminal-pane');
            if (firstPane) firstPane.after(splitter);
        }

        /**
         * Remove splitter
         */
        _removeSplitter() {
            const splitter = this.container.querySelector('.pane-splitter');
            if (splitter) splitter.remove();

            this.container.querySelectorAll('.terminal-pane').forEach(p => {
                p.style.flex = '1';
            });
        }

        /**
         * Reindex panes after removal
         */
        _reindexPanes() {
            const panes = this.container.querySelectorAll('.terminal-pane');
            panes.forEach((pane, i) => {
                pane.dataset.paneIndex = i;
                pane.querySelector('.pane-title').textContent = `Terminal ${i + 1}`;
                pane.querySelector('.terminal-content').id = `terminal-${i}`;
                this.terminals[i].index = i;
            });
        }

        /**
         * Load session IDs from storage
         */
        _loadSessionIds() {
            try {
                const stored = localStorage.getItem(CONFIG.sessionKey);
                return stored ? JSON.parse(stored) : [];
            } catch (e) {
                return [];
            }
        }

        /**
         * Save session IDs to storage
         */
        _saveSessionIds() {
            try {
                localStorage.setItem(CONFIG.sessionKey, JSON.stringify(this.getSessionIds()));
            } catch (e) {
                // Ignore storage errors
            }
        }

        /**
         * Send Copilot refine command
         */
        sendCopilotRefineCommand(filePath) {
            this._sendCopilotCommand(`refine the idea ${filePath}`);
        }

        /**
         * Send Copilot prompt command (executes with Enter)
         */
        sendCopilotPromptCommand(promptCommand) {
            this._sendCopilotCommand(promptCommand, true);
        }

        /**
         * Send Copilot prompt command without pressing Enter (for review before execution)
         */
        sendCopilotPromptCommandNoEnter(promptCommand) {
            this._sendCopilotCommand(promptCommand, false);
        }

        /**
         * Internal: Send copilot command with typing effect
         * @param {string} command - Command to type
         * @param {boolean} pressEnter - Whether to press Enter after command (default: true)
         */
        _sendCopilotCommand(command, pressEnter = true) {
            let targetIndex = this.activeIndex >= 0 ? this.activeIndex : 0;

            if (this.terminals.length === 0) {
                targetIndex = this.addTerminal();
            }

            this.setFocus(targetIndex);

            const instance = this.terminals[targetIndex];
            if (!instance?.socket?.connected) return;

            // Type 'copilot' then wait and type command
            this._typeWithEffect(instance.socket, 'copilot', () => {
                this._waitForCopilotReady(instance, () => {
                    this._typeWithEffect(instance.socket, command, null, pressEnter);
                });
            });
        }

        /**
         * Type text with realistic delay
         * @param {Object} socket - Socket connection
         * @param {string} text - Text to type
         * @param {Function} callback - Optional callback after typing
         * @param {boolean} pressEnter - Whether to press Enter after typing (default: true)
         */
        _typeWithEffect(socket, text, callback, pressEnter = true) {
            const chars = text.split('');
            let i = 0;

            const typeNext = () => {
                if (i < chars.length) {
                    socket.emit('input', chars[i++]);
                    setTimeout(typeNext, 30 + Math.random() * 50);
                } else {
                    setTimeout(() => {
                        if (pressEnter) {
                            socket.emit('input', '\r');
                        }
                        if (callback) callback();
                    }, 100);
                }
            };

            typeNext();
        }

        /**
         * Wait for Copilot CLI to be ready
         */
        _waitForCopilotReady(instance, callback, maxAttempts = 30) {
            let attempts = 0;

            const check = () => {
                if (++attempts >= maxAttempts || this._isCopilotReady(instance)) {
                    setTimeout(callback, 300);
                } else {
                    setTimeout(check, 200);
                }
            };

            setTimeout(check, 500);
        }

        /**
         * Check if Copilot prompt is ready
         */
        _isCopilotReady(instance) {
            const buffer = instance.terminal?.buffer?.active;
            if (!buffer) return false;

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
    }

    // =========================================================================
    // PanelController - Collapse/expand/zen mode UI
    // =========================================================================

    class PanelController {
        constructor(paneManager) {
            this.paneManager = paneManager;
            
            this.panel = document.getElementById('terminal-panel');
            this.header = document.getElementById('terminal-header');
            this.toggleBtn = document.getElementById('terminal-toggle');
            this.zenBtn = document.getElementById('terminal-zen-btn');
            this.addBtn = document.getElementById('add-terminal-btn');
            this.resizeHandle = document.getElementById('terminal-resize-handle');
            this.statusIndicator = document.getElementById('terminal-status-indicator');
            this.statusText = document.getElementById('terminal-status-text');

            this.isExpanded = false;
            this.isZenMode = false;
            this.panelHeight = 300;

            this._bindEvents();
            
            // Listen for status changes
            this.paneManager.onStatusChange = () => this._updateStatus();
        }

        _bindEvents() {
            // Header click to toggle
            this.header.addEventListener('click', e => {
                // Don't toggle if clicking on actions, status, or voice controls
                if (e.target.closest('.terminal-actions') || 
                    e.target.closest('.terminal-status') ||
                    e.target.closest('.terminal-header-center')) return;
                this.toggle();
            });

            this.toggleBtn.addEventListener('click', e => {
                e.stopPropagation();
                this.toggle();
            });

            if (this.zenBtn) {
                this.zenBtn.addEventListener('click', e => {
                    e.stopPropagation();
                    this.toggleZenMode();
                });
            }

            if (this.addBtn) {
                this.addBtn.addEventListener('click', e => {
                    e.stopPropagation();
                    this.paneManager.addTerminal();
                    this._updateAddButton();
                });
            }

            // Resize handle
            this._initResize();

            // ESC to exit zen mode
            document.addEventListener('keydown', e => {
                if (e.key === 'Escape' && this.isZenMode) {
                    this.toggleZenMode();
                }
            });

            // Window resize
            window.addEventListener('resize', this._debounce(() => {
                this.paneManager.fitAll();
            }, 150));

            // Tab visibility
            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'visible') {
                    this._reconnectAll();
                }
            });
        }

        _initResize() {
            if (!this.resizeHandle) return;

            let startY, startHeight;

            this.resizeHandle.addEventListener('mousedown', e => {
                e.preventDefault();
                startY = e.clientY;
                startHeight = this.panel.offsetHeight;

                this.panel.classList.add('resizing');
                document.body.style.cursor = 'ns-resize';
                document.body.style.userSelect = 'none';

                const onMove = e => {
                    const delta = startY - e.clientY;
                    this.panelHeight = Math.min(Math.max(startHeight + delta, 100), window.innerHeight - 100);
                    this.panel.style.height = this.panelHeight + 'px';
                    this.paneManager.fitAll();
                };

                const onUp = () => {
                    document.removeEventListener('mousemove', onMove);
                    document.removeEventListener('mouseup', onUp);
                    this.panel.classList.remove('resizing');
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                    this.paneManager.fitAll();
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

            this.paneManager.fitAll();
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

            this.paneManager.fitAll();
        }

        _exitZenMode() {
            this.isZenMode = false;
            this.panel.classList.remove('zen-mode');
            this.panel.style.height = this.panelHeight + 'px';
            this.zenBtn.querySelector('i').className = 'bi bi-arrows-fullscreen';
            this.zenBtn.title = 'Zen Mode';

            const topMenu = document.querySelector('.top-menu');
            if (topMenu) topMenu.style.display = '';

            this.paneManager.fitAll();
        }

        _updateStatus() {
            const { connected, total } = this.paneManager.getStatus();

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
            
            this._updateAddButton();
        }

        _updateAddButton() {
            if (this.addBtn) {
                this.addBtn.disabled = this.paneManager.terminals.length >= CONFIG.maxTerminals;
            }
        }

        _reconnectAll() {
            this.paneManager.terminals.forEach(t => {
                if (t.socket && !t.socket.connected) {
                    t.socket.connect();
                }
            });
        }

        _debounce(fn, wait) {
            let timeout;
            return (...args) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => fn.apply(this, args), wait);
            };
        }
    }

    // =========================================================================
    // Compatibility Layer - Export same interface as terminal.js
    // =========================================================================

    /**
     * TerminalManager - Compatibility wrapper for existing code
     */
    class TerminalManager {
        constructor(paneContainerId) {
            this.paneManager = new PaneManager(paneContainerId);
            
            // Expose for backward compatibility
            this.terminals = [];
            this.fitAddons = [];
            this.sockets = [];
            this.sessionIds = [];
            this.activeIndex = -1;
        }

        initialize() {
            this.paneManager.initialize();
            this._syncState();
        }

        addTerminal(existingSessionId = null) {
            const result = this.paneManager.addTerminal(existingSessionId);
            this._syncState();
            return result;
        }

        closeTerminal(index) {
            this.paneManager.closeTerminal(index);
            this._syncState();
        }

        setFocus(index) {
            this.paneManager.setFocus(index);
            this._syncState();
        }

        fitAll() {
            this.paneManager.fitAll();
        }

        _resizeAll() {
            this.paneManager.fitAll();
        }

        sendCopilotRefineCommand(filePath) {
            this.paneManager.sendCopilotRefineCommand(filePath);
        }

        sendCopilotPromptCommand(promptCommand) {
            this.paneManager.sendCopilotPromptCommand(promptCommand);
        }

        sendCopilotPromptCommandNoEnter(promptCommand) {
            this.paneManager.sendCopilotPromptCommandNoEnter(promptCommand);
        }

        /**
         * Get the currently focused terminal for voice input injection
         * FEATURE-021: Console Voice Input
         */
        getFocusedTerminal() {
            // Use paneManager.activeIndex directly (not this.activeIndex which may be stale)
            const activeIdx = this.paneManager.activeIndex;
            if (activeIdx >= 0 && this.paneManager.terminals[activeIdx]) {
                const terminalData = this.paneManager.terminals[activeIdx];
                return {
                    terminal: terminalData.terminal,
                    socket: terminalData.socket,
                    sessionId: terminalData.sessionId,
                    sendInput: (text) => {
                        if (terminalData.socket && terminalData.sessionId) {
                            terminalData.socket.emit('input', text);
                        }
                    }
                };
            }
            return null;
        }

        /**
         * Get the socket connection for voice manager
         * FEATURE-021: Console Voice Input
         */
        get socket() {
            // Return the first active socket for voice input
            for (const t of this.paneManager.terminals) {
                if (t.socket && t.socket.connected) {
                    return t.socket;
                }
            }
            // If no connected socket, return first socket
            if (this.paneManager.terminals.length > 0) {
                return this.paneManager.terminals[0].socket;
            }
            return null;
        }

        _syncState() {
            // Sync internal state for any code that accesses these directly
            this.terminals = this.paneManager.terminals.map(t => t.terminal);
            this.fitAddons = this.paneManager.terminals.map(t => t.fitAddon);
            this.sockets = this.paneManager.terminals.map(t => t.socket);
            this.sessionIds = this.paneManager.terminals.map(t => t.sessionId);
            this.activeIndex = this.paneManager.activeIndex;
        }
    }

    /**
     * TerminalPanel - Compatibility wrapper
     */
    class TerminalPanel {
        constructor(terminalManager) {
            this.controller = new PanelController(terminalManager.paneManager);
            this.terminalManager = terminalManager;
            
            // Expose state for backward compatibility
            this.isExpanded = false;
            this.isZenMode = false;
        }

        toggle() {
            this.controller.toggle();
            this._syncState();
        }

        expand() {
            this.controller.expand();
            this._syncState();
        }

        collapse() {
            this.controller.collapse();
            this._syncState();
        }

        toggleZenMode() {
            this.controller.toggleZenMode();
            this._syncState();
        }

        _syncState() {
            this.isExpanded = this.controller.isExpanded;
            this.isZenMode = this.controller.isZenMode;
        }
    }

    // Export to window
    window.TerminalManager = TerminalManager;
    window.TerminalPanel = TerminalPanel;

    console.log('[Terminal v2] Module loaded');
})();
