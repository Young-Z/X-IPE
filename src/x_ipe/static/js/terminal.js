/**
 * Terminal Manager
 * FEATURE-005: Interactive Console
 * 
 * Based on sample-root implementation.
 * Manages multiple xterm.js terminals with Socket.IO.
 */

(function() {
    'use strict';

    const SESSION_KEY = 'terminal_session_ids';
    const MAX_TERMINALS = 2;

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
     * TerminalManager - Manages multiple terminal instances
     * Based on sample-root/static/js/terminal.js
     */
    class TerminalManager {
        constructor(paneContainerId) {
            this.terminals = [];
            this.fitAddons = [];
            this.sockets = [];
            this.sessionIds = [];
            this.activeIndex = -1;
            
            this.paneContainer = document.getElementById(paneContainerId);
            this.statusIndicator = document.getElementById('terminal-status-indicator');
            this.statusText = document.getElementById('terminal-status-text');
            this.addButton = document.getElementById('add-terminal-btn');
            
            // Track if initial fit has been done (for containers that start hidden)
            this._initialFitDone = false;
            
            this._setupEventListeners();
            this._setupResizeObserver();
        }
        
        /**
         * Setup ResizeObserver to detect when terminal container becomes visible
         * This fixes the initial sizing issue when terminal panel starts collapsed
         */
        _setupResizeObserver() {
            if (!this.paneContainer || typeof ResizeObserver === 'undefined') return;
            
            this._resizeObserver = new ResizeObserver(debounce((entries) => {
                for (const entry of entries) {
                    const { width, height } = entry.contentRect;
                    // Only fit if container has actual dimensions
                    if (width > 0 && height > 0) {
                        console.log(`[Terminal] Container resized to ${width}x${height} - fitting terminals`);
                        this._doFit();
                        
                        // Mark initial fit as done once we have proper dimensions
                        if (!this._initialFitDone && this.terminals.length > 0) {
                            this._initialFitDone = true;
                        }
                    }
                }
            }, 50));
            
            this._resizeObserver.observe(this.paneContainer);
        }

        _setupEventListeners() {
            if (this.addButton) {
                this.addButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.addTerminal();
                });
            }
            
            // Window resize - resize all terminals (debounced)
            window.addEventListener('resize', debounce(() => this._resizeAll(), 150));
            
            // Handle page visibility changes - keep socket alive when tab is hidden
            // Session should stay open for 1 hour regardless of tab focus
            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'visible') {
                    console.log('[Terminal] Tab became visible - checking connections');
                    this._checkAndReconnectAll();
                } else {
                    console.log('[Terminal] Tab hidden - connections will stay alive');
                }
            });
            
            // Handle window focus/blur as backup
            window.addEventListener('focus', () => {
                console.log('[Terminal] Window focused - checking connections');
                this._checkAndReconnectAll();
            });
        }
        
        /**
         * Check all sockets and reconnect if needed
         */
        _checkAndReconnectAll() {
            this.sockets.forEach((socket, index) => {
                if (socket && !socket.connected) {
                    console.log(`[Terminal ${index + 1}] Reconnecting after visibility change`);
                    socket.connect();
                }
            });
        }

        /**
         * Initialize terminals
         */
        initialize() {
            const storedIds = this._getStoredSessionIds();
            if (storedIds.length > 0) {
                storedIds.forEach(id => this.addTerminal(id));
            } else {
                this.addTerminal();
            }
        }

        /**
         * Add a new terminal pane
         */
        addTerminal(existingSessionId = null) {
            if (this.terminals.length >= MAX_TERMINALS) {
                console.warn('[Terminal] Maximum terminals reached');
                return -1;
            }

            // Add splitter before second terminal
            if (this.terminals.length === 1) {
                this._addSplitter();
            }

            const index = this.terminals.length;
            
            // Create pane DOM
            const pane = this._createPane(index);
            this.paneContainer.appendChild(pane);
            
            // Create terminal
            const terminal = new Terminal(terminalConfig);
            const fitAddon = new FitAddon.FitAddon();
            terminal.loadAddon(fitAddon);
            
            // Load Unicode11 addon for special character support (powerline, icons, etc.)
            if (typeof Unicode11Addon !== 'undefined') {
                const unicode11Addon = new Unicode11Addon.Unicode11Addon();
                terminal.loadAddon(unicode11Addon);
                terminal.unicode.activeVersion = '11';
            }
            
            // Open terminal in content div
            const contentDiv = pane.querySelector('.terminal-content');
            terminal.open(contentDiv);
            
            // Store references
            this.terminals.push(terminal);
            this.fitAddons.push(fitAddon);
            this.sessionIds.push(existingSessionId);
            
            // Prevent scroll-to-top when typing in terminal
            // xterm.js uses a hidden textarea that can trigger browser scroll on focus
            this._setupScrollPrevention(terminal, contentDiv);
            
            // Fit terminal to container
            this.fitAll();
            
            // Create socket
            const socket = this._createSocket(index, existingSessionId);
            this.sockets.push(socket);
            
            // Handle input - scroll to bottom on typing and prevent page scroll
            terminal.onData(data => {
                if (socket.connected) {
                    // Preserve page scroll position
                    const scrollX = window.scrollX;
                    const scrollY = window.scrollY;
                    
                    socket.emit('input', data);
                    
                    // Scroll terminal to bottom (where cursor is)
                    terminal.scrollToBottom();
                    
                    // Restore page scroll if it changed
                    if (window.scrollX !== scrollX || window.scrollY !== scrollY) {
                        window.scrollTo(scrollX, scrollY);
                    }
                }
            });
            
            this.setFocus(index);
            this._updateAddButton();
            this._saveSessionIds();
            
            console.log(`[Terminal] Added terminal ${index + 1}`);
            return index;
        }

        /**
         * Create pane DOM element
         */
        _createPane(index) {
            const pane = document.createElement('div');
            pane.className = 'terminal-pane';
            pane.dataset.paneIndex = index;

            const header = document.createElement('div');
            header.className = 'pane-header';

            const title = document.createElement('span');
            title.className = 'pane-title';
            title.textContent = `Terminal ${index + 1}`;

            const closeBtn = document.createElement('button');
            closeBtn.className = 'close-pane-btn';
            closeBtn.innerHTML = '×';
            closeBtn.title = 'Close terminal';
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.closeTerminal(parseInt(pane.dataset.paneIndex));
            });

            header.appendChild(title);
            header.appendChild(closeBtn);

            const content = document.createElement('div');
            content.className = 'terminal-content';
            content.id = `terminal-${index}`;

            pane.appendChild(header);
            pane.appendChild(content);

            pane.addEventListener('click', () => {
                this.setFocus(parseInt(pane.dataset.paneIndex));
            });

            return pane;
        }

        /**
         * Add horizontal splitter between panes
         */
        _addSplitter() {
            const splitter = document.createElement('div');
            splitter.className = 'pane-splitter';
            splitter.id = 'pane-splitter';
            
            let startX, leftPaneWidth, rightPaneWidth;
            
            splitter.addEventListener('mousedown', (e) => {
                e.preventDefault();
                const panes = this.paneContainer.querySelectorAll('.terminal-pane');
                if (panes.length < 2) return;
                
                const leftPane = panes[0];
                const rightPane = panes[1];
                
                startX = e.clientX;
                leftPaneWidth = leftPane.offsetWidth;
                rightPaneWidth = rightPane.offsetWidth;
                
                // Visual feedback
                this.paneContainer.classList.add('dragging-splitter');
                document.body.style.cursor = 'ew-resize';
                document.body.style.userSelect = 'none';
                
                const onMove = (e) => {
                    const delta = e.clientX - startX;
                    const totalWidth = leftPaneWidth + rightPaneWidth;
                    const minWidth = 100;
                    
                    let newLeftWidth = leftPaneWidth + delta;
                    let newRightWidth = rightPaneWidth - delta;
                    
                    // Enforce minimum widths
                    if (newLeftWidth < minWidth) {
                        newLeftWidth = minWidth;
                        newRightWidth = totalWidth - minWidth;
                    } else if (newRightWidth < minWidth) {
                        newRightWidth = minWidth;
                        newLeftWidth = totalWidth - minWidth;
                    }
                    
                    // Set flex-basis for each pane
                    leftPane.style.flex = `0 0 ${newLeftWidth}px`;
                    rightPane.style.flex = `0 0 ${newRightWidth}px`;
                    
                    // Resize terminals to fit new pane sizes
                    this._doFit();
                };
                
                const onUp = () => {
                    document.removeEventListener('mousemove', onMove);
                    document.removeEventListener('mouseup', onUp);
                    
                    // Remove visual feedback
                    this.paneContainer.classList.remove('dragging-splitter');
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                    
                    // Final fit
                    this.fitAll();
                };
                
                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
            });
            
            // Insert splitter after first pane
            const firstPane = this.paneContainer.querySelector('.terminal-pane');
            if (firstPane) {
                firstPane.after(splitter);
            }
        }

        /**
         * Remove splitter when going back to single terminal
         */
        _removeSplitter() {
            const splitter = this.paneContainer.querySelector('.pane-splitter');
            if (splitter) {
                splitter.remove();
            }
            // Reset flex for remaining pane
            const panes = this.paneContainer.querySelectorAll('.terminal-pane');
            panes.forEach(pane => {
                pane.style.flex = '1';
            });
        }

        /**
         * Get current index for a socket (handles reindexing after close)
         */
        _getSocketIndex(socket) {
            return this.sockets.indexOf(socket);
        }

        /**
         * Create Socket.IO connection with improved stability
         * Session stays alive for 1 hour regardless of tab focus
         */
        _createSocket(index, existingSessionId) {
            const socket = io({
                transports: ['websocket'],           // WebSocket only for lower latency
                upgrade: false,                       // No upgrade needed since we start with WS
                reconnection: true,
                reconnectionAttempts: Infinity,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 30000,          // Max 30s between retries
                randomizationFactor: 0.5,
                timeout: 60000,                       // Initial connection timeout (60s)
                forceNew: false,
                // Heartbeat settings - match server (ping_timeout=300s, ping_interval=60s)
                pingTimeout: 300000,                  // Server waits 5min for pong
                pingInterval: 60000                   // Server pings every 60s
            });
            
            // Track connection health
            let lastPongTime = Date.now();
            let healthCheckInterval = null;
            
            const startHealthCheck = () => {
                if (healthCheckInterval) clearInterval(healthCheckInterval);
                healthCheckInterval = setInterval(() => {
                    const timeSincePong = Date.now() - lastPongTime;
                    // If no pong for 3 minutes, connection may be unhealthy (server timeout is 5min)
                    if (timeSincePong > 180000 && socket.connected) {
                        console.warn(`[Terminal ${index + 1}] Connection may be stale (${Math.round(timeSincePong/1000)}s since last pong)`);
                    }
                }, 60000);  // Check every minute
            };
            
            const stopHealthCheck = () => {
                if (healthCheckInterval) {
                    clearInterval(healthCheckInterval);
                    healthCheckInterval = null;
                }
            };

            socket.on('connect', () => {
                const idx = this._getSocketIndex(socket);
                console.log(`[Terminal ${idx + 1}] Connected`);
                lastPongTime = Date.now();
                startHealthCheck();
                this._updateStatus();
                
                const dims = this.fitAddons[idx]?.proposeDimensions();
                socket.emit('attach', {
                    session_id: existingSessionId,
                    rows: dims ? dims.rows : 24,
                    cols: dims ? dims.cols : 80
                });
            });

            socket.on('session_id', sessionId => {
                const idx = this._getSocketIndex(socket);
                if (idx >= 0) {
                    this.sessionIds[idx] = sessionId;
                    this._saveSessionIds();
                }
            });

            socket.on('new_session', data => {
                const idx = this._getSocketIndex(socket);
                if (idx >= 0) {
                    this.terminals[idx].write('\x1b[32m[New session started]\x1b[0m\r\n');
                    this.sessionIds[idx] = data.session_id;
                    this._saveSessionIds();
                }
            });

            socket.on('reconnected', () => {
                const idx = this._getSocketIndex(socket);
                if (idx >= 0) {
                    this.terminals[idx].write('\x1b[33m[Reconnected to session]\x1b[0m\r\n');
                }
            });

            socket.on('output', data => {
                const idx = this._getSocketIndex(socket);
                if (idx >= 0) {
                    const terminal = this.terminals[idx];
                    terminal.write(data);
                    // Scroll terminal viewport to bottom after output
                    terminal.scrollToBottom();
                }
            });
            
            // Handle pong to track connection health
            socket.io.engine.on('pong', () => {
                lastPongTime = Date.now();
            });

            socket.on('disconnect', reason => {
                const idx = this._getSocketIndex(socket);
                console.log(`[Terminal ${idx + 1}] Disconnected: ${reason}`);
                stopHealthCheck();
                this._updateStatus();
                
                if (reason !== 'io client disconnect' && idx >= 0) {
                    // Only show message for unexpected disconnects
                    if (reason === 'ping timeout') {
                        this.terminals[idx].write('\r\n\x1b[31m[Connection timeout - reconnecting...]\x1b[0m\r\n');
                    } else if (reason === 'transport close' || reason === 'transport error') {
                        this.terminals[idx].write('\r\n\x1b[31m[Connection lost - reconnecting...]\x1b[0m\r\n');
                    }
                }
            });

            socket.io.on('reconnect', attempt => {
                const idx = this._getSocketIndex(socket);
                console.log(`[Terminal ${idx + 1}] Reconnected after ${attempt} attempts`);
                lastPongTime = Date.now();
                startHealthCheck();
                this._updateStatus();
                
                if (idx >= 0) {
                    const sessionId = this.sessionIds[idx];
                    const dims = this.fitAddons[idx]?.proposeDimensions();
                    socket.emit('attach', {
                        session_id: sessionId,
                        rows: dims ? dims.rows : 24,
                        cols: dims ? dims.cols : 80
                    });
                }
            });

            socket.io.on('reconnect_attempt', attempt => {
                const idx = this._getSocketIndex(socket);
                console.log(`[Terminal ${idx + 1}] Reconnection attempt ${attempt}`);
                if (attempt === 1 && idx >= 0) {
                    this.terminals[idx].write('\x1b[33m[Reconnecting...]\x1b[0m\r\n');
                }
            });

            socket.io.on('reconnect_failed', () => {
                const idx = this._getSocketIndex(socket);
                stopHealthCheck();
                if (idx >= 0) {
                    this.terminals[idx].write('\r\n\x1b[31m[Connection lost - please refresh page]\x1b[0m\r\n');
                }
            });

            socket.on('connect_error', error => {
                console.error(`[Terminal ${index + 1}] Connection error:`, error.message || error);
                this._updateStatus();
            });

            return socket;
        }

        /**
         * Close a terminal
         */
        closeTerminal(index) {
            if (index < 0 || index >= this.terminals.length) return;

            if (this.sockets[index]) this.sockets[index].disconnect();
            if (this.terminals[index]) this.terminals[index].dispose();
            
            this.terminals.splice(index, 1);
            this.fitAddons.splice(index, 1);
            this.sockets.splice(index, 1);
            this.sessionIds.splice(index, 1);
            
            const pane = this.paneContainer.querySelector(`[data-pane-index="${index}"]`);
            if (pane) pane.remove();
            
            // Remove splitter when going back to 1 or 0 terminals
            if (this.terminals.length <= 1) {
                this._removeSplitter();
            }
            
            this._reindexPanes();
            
            if (this.terminals.length > 0) {
                this.setFocus(Math.min(index, this.terminals.length - 1));
                this.fitAll();
            } else {
                this.activeIndex = -1;
                this.addTerminal();
            }
            
            this._updateAddButton();
            this._saveSessionIds();
            this._updateStatus();
            
            console.log(`[Terminal] Closed terminal at index ${index}`);
        }

        /**
         * Set focus to a terminal without scrolling the page
         */
        setFocus(index) {
            if (index < 0 || index >= this.terminals.length) return;

            this.paneContainer.querySelectorAll('.terminal-pane').forEach(p => {
                p.classList.remove('focused');
            });
            
            const pane = this.paneContainer.querySelector(`[data-pane-index="${index}"]`);
            if (pane) pane.classList.add('focused');
            
            this.activeIndex = index;
            
            // Focus terminal without triggering browser scroll
            this._focusWithoutScroll(this.terminals[index]);
        }

        /**
         * Focus terminal without triggering browser scroll-to-focus behavior
         * xterm.js uses a hidden textarea for input, which can cause scroll jumps
         */
        _focusWithoutScroll(terminal) {
            if (!terminal) return;
            
            // Save current scroll positions (window and content-body)
            const scrollX = window.scrollX;
            const scrollY = window.scrollY;
            const contentBody = document.querySelector('.content-body');
            const contentBodyScroll = contentBody?.scrollTop || 0;
            
            // Get the terminal's viewport element to preserve its scroll
            const viewport = terminal.element?.querySelector('.xterm-viewport');
            const terminalScrollTop = viewport?.scrollTop || 0;
            
            // Focus with preventScroll option (modern browsers)
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
            
            // Restore scroll positions immediately
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
         * Prevents browser from scrolling page/containers when textarea receives focus/input
         */
        _setupScrollPrevention(terminal, container) {
            // Wait for terminal to fully render and create its textarea
            requestAnimationFrame(() => {
                const textarea = terminal.element?.querySelector('.xterm-helper-textarea');
                if (!textarea) return;
                
                // Find scrollable parent containers (e.g., .content-body)
                const contentBody = document.querySelector('.content-body');
                
                // Store scroll positions for all scrollable elements
                let savedScrollX = 0;
                let savedScrollY = 0;
                let savedContentBodyScroll = 0;
                
                const saveScrollPositions = () => {
                    savedScrollX = window.scrollX;
                    savedScrollY = window.scrollY;
                    if (contentBody) {
                        savedContentBodyScroll = contentBody.scrollTop;
                    }
                };
                
                const restoreScrollPositions = () => {
                    // Restore window scroll
                    if (window.scrollX !== savedScrollX || window.scrollY !== savedScrollY) {
                        window.scrollTo(savedScrollX, savedScrollY);
                    }
                    // Restore content-body scroll (main scrollable area)
                    if (contentBody && contentBody.scrollTop !== savedContentBodyScroll) {
                        contentBody.scrollTop = savedContentBodyScroll;
                    }
                };
                
                // Intercept focus events to prevent scroll
                textarea.addEventListener('focus', (e) => {
                    saveScrollPositions();
                    // Use multiple mechanisms to restore scroll
                    queueMicrotask(restoreScrollPositions);
                    requestAnimationFrame(restoreScrollPositions);
                }, { capture: true });
                
                // Intercept keydown - this is where the scroll often happens
                textarea.addEventListener('keydown', (e) => {
                    saveScrollPositions();
                    // Restore after key processing
                    queueMicrotask(restoreScrollPositions);
                    requestAnimationFrame(restoreScrollPositions);
                }, { capture: true });
                
                // Intercept input events
                textarea.addEventListener('input', (e) => {
                    saveScrollPositions();
                    queueMicrotask(restoreScrollPositions);
                    requestAnimationFrame(restoreScrollPositions);
                }, { capture: true });
                
                // Also handle the container click to prevent scroll on re-focus
                container.addEventListener('mousedown', (e) => {
                    saveScrollPositions();
                    requestAnimationFrame(restoreScrollPositions);
                });
                
                // Additional: observe for any scroll changes and restore
                // This catches edge cases where other mechanisms fail
                let scrollCheckTimeout = null;
                const scheduleScrollCheck = () => {
                    if (scrollCheckTimeout) clearTimeout(scrollCheckTimeout);
                    scrollCheckTimeout = setTimeout(() => {
                        if (document.activeElement === textarea) {
                            restoreScrollPositions();
                        }
                    }, 10);
                };
                
                textarea.addEventListener('keypress', scheduleScrollCheck, { capture: true });
            });
        }

        /**
         * Internal fit logic - fits all terminals and sends resize to server
         * Note: Do NOT call terminal.refresh() here - it resets scroll position
         */
        _doFit() {
            this.fitAddons.forEach((fitAddon, index) => {
                try {
                    fitAddon.fit();
                    const dims = fitAddon.proposeDimensions();
                    if (dims && this.sockets[index] && this.sockets[index].connected) {
                        this.sockets[index].emit('resize', { rows: dims.rows, cols: dims.cols });
                    }
                } catch (e) {}
            });
        }

        /**
         * Fit all terminals - immediate fit + double RAF backup
         * Call this from any trigger (expand, resize, zen mode, etc.)
         */
        fitAll() {
            // Immediate fit attempt
            this._doFit();
            // Double RAF ensures CSS layout is fully computed
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    this._doFit();
                    // Final fit after any remaining layout shifts
                    setTimeout(() => this._doFit(), 50);
                });
            });
        }

        /**
         * Resize all terminals (legacy name, calls fitAll)
         */
        _resizeAll() {
            this._doFit();
        }

        /**
         * Reindex panes after removal
         */
        _reindexPanes() {
            const panes = this.paneContainer.querySelectorAll('.terminal-pane');
            panes.forEach((pane, i) => {
                pane.dataset.paneIndex = i;
                pane.querySelector('.pane-title').textContent = `Terminal ${i + 1}`;
                pane.querySelector('.terminal-content').id = `terminal-${i}`;
            });
        }

        _updateAddButton() {
            if (this.addButton) {
                this.addButton.disabled = this.terminals.length >= MAX_TERMINALS;
            }
        }

        _updateStatus() {
            const connected = this.sockets.filter(s => s && s.connected).length;
            const total = this.terminals.length;

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
                const validIds = this.sessionIds.filter(id => id !== null);
                localStorage.setItem(SESSION_KEY, JSON.stringify(validIds));
            } catch (e) {}
        }

        /**
         * Send Copilot refine command with typing simulation
         * @param {string} filePath - Path to the idea file to refine
         */
        sendCopilotRefineCommand(filePath) {
            // Check if we need a new terminal (if current one is in copilot mode)
            let targetIndex = this.activeIndex;
            
            // If no terminals exist, create one
            if (this.terminals.length === 0) {
                targetIndex = this.addTerminal();
            } else if (targetIndex < 0) {
                targetIndex = 0;
            }
            
            // Check if current terminal appears to be in copilot CLI mode
            // We detect this by checking if a new terminal is needed
            const needsNewTerminal = this._isInCopilotMode(targetIndex);
            
            if (needsNewTerminal && this.terminals.length < MAX_TERMINALS) {
                targetIndex = this.addTerminal();
            }
            
            this.setFocus(targetIndex);
            
            // Build the command sequence
            const copilotCommand = 'copilot';
            const refineCommand = `refine the idea ${filePath}`;
            
            // Send commands with typing simulation
            this._sendWithTypingEffect(targetIndex, copilotCommand, () => {
                // After copilot command, wait for CLI to be ready before sending refine command
                this._waitForCopilotReady(targetIndex, () => {
                    this._sendWithTypingEffect(targetIndex, refineCommand);
                });
            });
        }

        /**
         * Send a custom Copilot prompt command with typing simulation
         * @param {string} promptCommand - The command to send (with placeholders already replaced)
         */
        sendCopilotPromptCommand(promptCommand) {
            // Check if we need a new terminal (if current one is in copilot mode)
            let targetIndex = this.activeIndex;
            
            // If no terminals exist, create one
            if (this.terminals.length === 0) {
                targetIndex = this.addTerminal();
            } else if (targetIndex < 0) {
                targetIndex = 0;
            }
            
            // Check if current terminal appears to be in copilot CLI mode
            const needsNewTerminal = this._isInCopilotMode(targetIndex);
            
            if (needsNewTerminal && this.terminals.length < MAX_TERMINALS) {
                targetIndex = this.addTerminal();
            }
            
            this.setFocus(targetIndex);
            
            // Build the command sequence
            const copilotCommand = 'copilot';
            
            // Send commands with typing simulation
            this._sendWithTypingEffect(targetIndex, copilotCommand, () => {
                // After copilot command, wait for CLI to be ready before sending the prompt
                this._waitForCopilotReady(targetIndex, () => {
                    this._sendWithTypingEffect(targetIndex, promptCommand);
                });
            });
        }

        /**
         * Wait for Copilot CLI to be ready (prompt appears)
         * @param {number} index - Terminal index
         * @param {Function} callback - Callback when ready
         * @param {number} maxAttempts - Maximum polling attempts
         */
        _waitForCopilotReady(index, callback, maxAttempts = 30) {
            let attempts = 0;
            const pollInterval = 200; // Check every 200ms
            
            const checkReady = () => {
                attempts++;
                
                if (this._isCopilotPromptReady(index)) {
                    // Small additional delay to ensure prompt is fully rendered
                    setTimeout(callback, 300);
                    return;
                }
                
                if (attempts >= maxAttempts) {
                    // Timeout - proceed anyway after max wait (6 seconds)
                    console.warn('Copilot CLI initialization timeout, proceeding anyway');
                    setTimeout(callback, 500);
                    return;
                }
                
                setTimeout(checkReady, pollInterval);
            };
            
            // Start checking after initial delay
            setTimeout(checkReady, 500);
        }

        /**
         * Check if Copilot CLI prompt is ready for input
         * @param {number} index - Terminal index
         * @returns {boolean} - True if prompt is ready
         */
        _isCopilotPromptReady(index) {
            if (index < 0 || index >= this.terminals.length) return false;
            
            const terminal = this.terminals[index];
            if (!terminal) return false;
            
            // Check last few lines of terminal buffer for copilot ready indicators
            const buffer = terminal.buffer.active;
            for (let i = Math.max(0, buffer.cursorY - 3); i <= buffer.cursorY; i++) {
                const line = buffer.getLine(i);
                if (line) {
                    const text = line.translateToString(true);
                    // Copilot CLI shows specific prompts when ready:
                    // - ">" prompt at line start
                    // - "⏺" indicator
                    // - Ends with ">" suggesting ready for input
                    if (text.match(/^>[\s]*$/) || text.includes('⏺') || text.match(/>\s*$/)) {
                        return true;
                    }
                }
            }
            return false;
        }

        /**
         * Check if terminal appears to be in Copilot CLI mode
         * @param {number} index - Terminal index
         * @returns {boolean} - True if appears to be in copilot mode
         */
        _isInCopilotMode(index) {
            if (index < 0 || index >= this.terminals.length) return false;
            
            // Get terminal buffer content to check for copilot indicators
            const terminal = this.terminals[index];
            if (!terminal) return false;
            
            // Check last few lines of terminal buffer for copilot prompt indicators
            const buffer = terminal.buffer.active;
            for (let i = Math.max(0, buffer.cursorY - 5); i <= buffer.cursorY; i++) {
                const line = buffer.getLine(i);
                if (line) {
                    const text = line.translateToString(true);
                    // Copilot CLI typically shows a specific prompt or status
                    if (text.includes('copilot>') || text.includes('Copilot') || text.includes('⏺')) {
                        return true;
                    }
                }
            }
            return false;
        }

        /**
         * Send text with typing simulation effect
         * @param {number} index - Terminal index
         * @param {string} text - Text to type
         * @param {Function} callback - Optional callback after completion
         */
        _sendWithTypingEffect(index, text, callback) {
            if (index < 0 || index >= this.sockets.length) return;
            
            const socket = this.sockets[index];
            if (!socket || !socket.connected) return;
            
            const chars = text.split('');
            let i = 0;
            
            const typeChar = () => {
                if (i < chars.length) {
                    socket.emit('input', chars[i]);
                    i++;
                    // Random delay between 30-80ms for realistic typing
                    const delay = 30 + Math.random() * 50;
                    setTimeout(typeChar, delay);
                } else {
                    // Send Enter key after typing complete
                    setTimeout(() => {
                        socket.emit('input', '\r');
                        if (callback) callback();
                    }, 100);
                }
            };
            
            typeChar();
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
            this.resizeHandle = document.getElementById('terminal-resize-handle');
            this.terminalManager = terminalManager;

            this.isExpanded = false;
            this.isZenMode = false;
            this.panelHeight = 300;

            this._bindEvents();
        }

        _bindEvents() {
            // Header click to toggle (except on buttons/status)
            this.header.addEventListener('click', (e) => {
                if (e.target.closest('.terminal-actions') || e.target.closest('.terminal-status')) return;
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

            this._initResize();

            // ESC to exit zen mode
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
                
                // Add visual feedback
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
                    
                    // Remove visual feedback
                    this.panel.classList.remove('resizing');
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                    
                    // Final fit after resize complete
                    this.terminalManager.fitAll();
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

            // Wait for layout to stabilize then fit
            setTimeout(() => this.terminalManager.fitAll(), 0);
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

            this.terminalManager.fitAll();
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

            this.terminalManager.fitAll();
        }
    }

    // Export to window
    window.TerminalManager = TerminalManager;
    window.TerminalPanel = TerminalPanel;

    console.log('[Terminal] Module loaded');
})();
