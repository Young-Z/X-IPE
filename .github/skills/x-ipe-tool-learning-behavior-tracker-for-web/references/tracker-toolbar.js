/**
 * X-IPE Behavior Tracker — Injected IIFE
 * 
 * FEATURE-054-C: RecordingEngine + CircularBuffer + EventSerializer
 * FEATURE-054-D: TrackerToolbox (Shadow DOM)
 * FEATURE-054-E: PIIMasker
 * 
 * Injected via Chrome DevTools evaluate_script.
 * Config is provided by the wrapper in track_behavior.py as __xipeConfig.
 */

// Guard against double injection
if (!window.__xipeBehaviorTrackerInjected) {
    window.__xipeBehaviorTrackerInjected = true;

    const config = (typeof __xipeConfig !== 'undefined') ? __xipeConfig : {
        sessionId: 'unknown',
        purpose: '',
        piiWhitelist: [],
        bufferCapacity: 10000
    };

    // ========== FEATURE-054-E: PIIMasker ==========
    class PIIMasker {
        constructor(cfg) {
            this._whitelist = new Set(cfg.piiWhitelist || []);
            this._maskToken = '[MASKED]';
            this._passwordToken = '[PASSWORD_FIELD]';
        }

        mask(eventRecord) {
            if (!eventRecord.target) return eventRecord;
            const t = eventRecord.target;
            if (this._isPasswordField(t)) {
                t.textContent = this._passwordToken;
                t.value = this._passwordToken;
                return eventRecord;
            }
            if (this._isWhitelisted(t.cssSelector)) {
                return eventRecord;
            }
            if (t.textContent) t.textContent = this._maskToken;
            if (t.value) t.value = this._maskToken;
            return eventRecord;
        }

        addToWhitelist(sel) { this._whitelist.add(sel); }
        removeFromWhitelist(sel) { this._whitelist.delete(sel); }
        getWhitelist() { return [...this._whitelist]; }

        _isPasswordField(target) {
            return target.tagName === 'INPUT' &&
                (target.type === 'password' || target.autocomplete === 'current-password' ||
                 target.autocomplete === 'new-password');
        }

        _isWhitelisted(cssSelector) {
            if (!cssSelector) return false;
            for (const pattern of this._whitelist) {
                if (cssSelector.includes(pattern) || cssSelector === pattern) return true;
            }
            return false;
        }
    }

    // ========== FEATURE-054-C: CircularBuffer ==========
    class CircularBuffer {
        constructor(capacity) {
            this._capacity = capacity;
            this._buffer = [];
            this._head = 0;
            this._size = 0;
        }

        push(item) {
            if (this._size < this._capacity) {
                this._buffer.push(item);
                this._size++;
            } else {
                this._buffer[this._head] = item;
                this._head = (this._head + 1) % this._capacity;
            }
        }

        toArray() {
            if (this._size < this._capacity) return this._buffer.slice();
            return [
                ...this._buffer.slice(this._head),
                ...this._buffer.slice(0, this._head)
            ];
        }

        clear() {
            this._buffer = [];
            this._head = 0;
            this._size = 0;
        }

        getSize() { return this._size; }
        isFull() { return this._size >= this._capacity; }
    }

    // ========== FEATURE-054-C: EventSerializer ==========
    class EventSerializer {
        constructor(sessionStartTime) {
            this._startTime = sessionStartTime;
        }

        serialize(domEvent, type) {
            const now = Date.now();
            const target = domEvent.target || domEvent.srcElement;
            const record = {
                type: type,
                timestamp: now,
                relativeTime: now - this._startTime,
                target: this._serializeTarget(target),
                metadata: {
                    pageUrl: window.location.href,
                    pageTitle: document.title,
                    viewportWidth: window.innerWidth,
                    viewportHeight: window.innerHeight
                },
                details: {}
            };

            switch (type) {
                case 'click':
                    record.details = { x: domEvent.clientX, y: domEvent.clientY, button: domEvent.button };
                    break;
                case 'input':
                    record.details = { inputType: domEvent.inputType || 'unknown' };
                    break;
                case 'scroll':
                    record.details = { scrollX: window.scrollX, scrollY: window.scrollY };
                    break;
                case 'navigation':
                    record.details = { fromUrl: domEvent.fromUrl || '', toUrl: window.location.href };
                    break;
                case 'resize':
                    record.details = {
                        newWidth: window.innerWidth, newHeight: window.innerHeight,
                        oldWidth: domEvent.oldWidth || 0, oldHeight: domEvent.oldHeight || 0
                    };
                    break;
                case 'focus':
                    record.details = { gained: domEvent.type === 'focusin' };
                    break;
                case 'drag':
                    record.details = {
                        startX: domEvent.clientX, startY: domEvent.clientY,
                        endX: domEvent.clientX, endY: domEvent.clientY
                    };
                    break;
            }
            return record;
        }

        _serializeTarget(el) {
            if (!el || !el.tagName) return { tagName: 'unknown', cssSelector: '' };
            const rect = el.getBoundingClientRect ? el.getBoundingClientRect() : {};
            return {
                tagName: el.tagName,
                id: el.id || '',
                classList: el.classList ? [...el.classList] : [],
                cssSelector: this._buildSelector(el),
                textContent: (el.textContent || '').slice(0, 200),
                value: el.value || '',
                type: el.type || '',
                autocomplete: el.autocomplete || '',
                role: el.getAttribute ? (el.getAttribute('role') || '') : '',
                ariaLabel: el.getAttribute ? (el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || '') : '',
                boundingBox: { x: rect.x || 0, y: rect.y || 0, width: rect.width || 0, height: rect.height || 0 }
            };
        }

        _buildSelector(el) {
            if (!el || !el.tagName) return '';
            let sel = el.tagName.toLowerCase();
            if (el.id) sel += '#' + el.id;
            if (el.classList && el.classList.length) {
                sel += '.' + [...el.classList].join('.');
            }
            return sel;
        }
    }

    // ========== FEATURE-054-C: RecordingEngine ==========
    class RecordingEngine {
        constructor(cfg, buffer, piiMasker, onEvent) {
            this._buffer = buffer;
            this._pii = piiMasker;
            this._onEvent = onEvent;
            this._serializer = new EventSerializer(Date.now());
            this._listeners = new Map();
            this._recording = false;
            this._scrollTimer = null;
            this._resizeTimer = null;
            this._lastViewport = { w: window.innerWidth, h: window.innerHeight };
        }

        start() {
            if (this._recording) return;
            this._recording = true;
            this._attach('click', 'click');
            this._attach('dblclick', 'double_click');
            this._attach('contextmenu', 'right_click');
            this._attach('input', 'input');
            this._attachDebounced('scroll', 'scroll', 200);
            this._attach('popstate', 'navigation');
            this._attach('hashchange', 'navigation');
            this._attachDebounced('resize', 'resize', 300);
            this._attach('focusin', 'focus');
            this._attach('focusout', 'focus');
            this._attach('dragstart', 'drag');
            this._attach('dragend', 'drag');
        }

        stop() {
            this._recording = false;
            for (const [eventName, handler] of this._listeners) {
                document.removeEventListener(eventName, handler, true);
                window.removeEventListener(eventName, handler, true);
            }
            this._listeners.clear();
        }

        pause() { this._recording = false; }
        resume() { this._recording = true; }
        getEventCount() { return this._buffer.getSize(); }

        _attach(eventName, type) {
            const handler = (e) => {
                if (!this._recording) return;
                try {
                    const serialized = this._serializer.serialize(e, type);
                    if (type === 'resize') {
                        serialized.details.oldWidth = this._lastViewport.w;
                        serialized.details.oldHeight = this._lastViewport.h;
                        this._lastViewport = { w: window.innerWidth, h: window.innerHeight };
                    }
                    const masked = this._pii.mask(serialized);
                    this._buffer.push(masked);
                    if (this._onEvent) this._onEvent(masked);
                } catch (err) {
                    console.warn('[X-IPE Tracker] Event handler error:', err);
                }
            };
            const target = ['scroll', 'resize', 'popstate', 'hashchange'].includes(eventName) ? window : document;
            target.addEventListener(eventName, handler, true);
            this._listeners.set(eventName, handler);
        }

        _attachDebounced(eventName, type, delayMs) {
            let timer = null;
            const handler = (e) => {
                if (!this._recording) return;
                clearTimeout(timer);
                timer = setTimeout(() => {
                    try {
                        const serialized = this._serializer.serialize(e, type);
                        if (type === 'resize') {
                            serialized.details.oldWidth = this._lastViewport.w;
                            serialized.details.oldHeight = this._lastViewport.h;
                            this._lastViewport = { w: window.innerWidth, h: window.innerHeight };
                        }
                        const masked = this._pii.mask(serialized);
                        this._buffer.push(masked);
                        if (this._onEvent) this._onEvent(masked);
                    } catch (err) {
                        console.warn('[X-IPE Tracker] Debounced handler error:', err);
                    }
                }, delayMs);
            };
            const target = ['scroll', 'resize'].includes(eventName) ? window : document;
            target.addEventListener(eventName, handler, true);
            this._listeners.set(eventName, handler);
        }
    }

    // ========== FEATURE-054-B: BackupManager ==========
    class BackupManager {
        constructor(sessionId) {
            this._key = '__xipe_behavior_backup_' + sessionId;
        }

        flush(buffer) {
            try {
                const data = {
                    events: buffer.toArray(),
                    lastFlushTime: new Date().toISOString(),
                    pageUrl: window.location.href
                };
                localStorage.setItem(this._key, JSON.stringify(data));
            } catch (e) {
                console.warn('[X-IPE Tracker] LocalStorage backup failed:', e);
            }
        }

        restore(buffer) {
            try {
                const raw = localStorage.getItem(this._key);
                if (!raw) return;
                const data = JSON.parse(raw);
                if (data.events && Array.isArray(data.events)) {
                    for (const event of data.events) {
                        buffer.push(event);
                    }
                }
                this.clear();
            } catch (e) {
                console.warn('[X-IPE Tracker] LocalStorage restore failed:', e);
            }
        }

        clear() {
            try { localStorage.removeItem(this._key); } catch (e) { /* ignore */ }
        }
    }

    // ========== FEATURE-054-D: TrackerToolbox (Shadow DOM) ==========
    class TrackerToolbox {
        constructor(cfg, engine, piiMasker) {
            this._engine = engine;
            this._pii = piiMasker;
            this._config = cfg;
            this._host = null;
            this._shadow = null;
            this._eventList = null;
            this._minimized = false;
            this._eventCount = 0;
            this._maxVisibleEvents = 50;
        }

        render() {
            this._host = document.createElement('div');
            this._host.id = '__xipe-tracker-toolbox-host';
            document.body.appendChild(this._host);
            this._shadow = this._host.attachShadow({ mode: 'closed' });
            this._shadow.innerHTML = this._getStyles() + this._getHTML();

            this._eventList = this._shadow.querySelector('.event-list');
            this._setupControls();
            this._setupDrag();
        }

        appendEvent(event) {
            this._eventCount++;
            this._updateCounter();
            if (!this._eventList || this._minimized) return;

            const row = document.createElement('div');
            row.className = 'event-row';
            row.innerHTML = this._formatEventRow(event);
            this._eventList.prepend(row);

            while (this._eventList.children.length > this._maxVisibleEvents) {
                this._eventList.removeChild(this._eventList.lastChild);
            }
        }

        minimize() {
            this._minimized = true;
            const panel = this._shadow.querySelector('.toolbox');
            const pill = this._shadow.querySelector('.toolbox-pill');
            if (panel) panel.style.display = 'none';
            if (pill) pill.style.display = 'flex';
        }

        maximize() {
            this._minimized = false;
            const panel = this._shadow.querySelector('.toolbox');
            const pill = this._shadow.querySelector('.toolbox-pill');
            if (panel) panel.style.display = 'flex';
            if (pill) pill.style.display = 'none';
        }

        destroy() {
            if (this._host && this._host.parentNode) {
                this._host.parentNode.removeChild(this._host);
            }
        }

        _updateCounter() {
            const counter = this._shadow.querySelector('.event-counter');
            if (counter) counter.textContent = this._eventCount;
            const pillCounter = this._shadow.querySelector('.pill-counter');
            if (pillCounter) pillCounter.textContent = this._eventCount + ' events';
        }

        _formatEventRow(event) {
            const icons = { click: '🖱', input: '⌨', scroll: '📜', navigation: '🔗', resize: '↔', focus: '◉', drag: '✥' };
            const icon = icons[event.type] || '•';
            const target = (event.target || {}).cssSelector || (event.target || {}).tagName || '';
            const time = event.relativeTime ? (event.relativeTime / 1000).toFixed(1) + 's' : '';
            return `<span class="ev-icon">${icon}</span><span class="ev-type">${event.type}</span><span class="ev-target">${this._esc(target)}</span><span class="ev-time">${time}</span>`;
        }

        _esc(str) {
            const d = document.createElement('span');
            d.textContent = str || '';
            return d.innerHTML;
        }

        _getStyles() {
            return `<style>
:host { position:fixed; bottom:20px; right:20px; z-index:2147483640; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; font-size:13px; }
.toolbox { width:380px; max-height:480px; background:rgba(15,23,42,0.85); backdrop-filter:blur(20px); border:1px solid rgba(255,255,255,0.1); border-radius:12px; color:#e2e8f0; box-shadow:0 25px 50px rgba(0,0,0,0.4); display:flex; flex-direction:column; overflow:hidden; }
.header { cursor:grab; padding:10px 14px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center; }
.header-title { display:flex; align-items:center; gap:6px; font-weight:600; }
.header-actions { display:flex; gap:4px; }
.header-actions button { background:none; border:none; color:#94a3b8; cursor:pointer; font-size:14px; padding:2px 4px; border-radius:4px; }
.header-actions button:hover { color:#e2e8f0; background:rgba(255,255,255,0.1); }
.status-bar { padding:6px 14px; border-bottom:1px solid rgba(255,255,255,0.05); font-size:11px; color:#94a3b8; display:flex; justify-content:space-between; }
.controls { padding:8px 14px; display:flex; gap:6px; border-bottom:1px solid rgba(255,255,255,0.05); }
.controls button { padding:4px 12px; border-radius:6px; border:1px solid rgba(255,255,255,0.15); background:rgba(255,255,255,0.05); color:#e2e8f0; cursor:pointer; font-size:12px; }
.controls button:hover { background:rgba(255,255,255,0.1); }
.controls button.active { background:rgba(239,68,68,0.3); border-color:rgba(239,68,68,0.5); }
.event-list { flex:1; overflow-y:auto; max-height:280px; }
.event-row { display:flex; align-items:center; gap:6px; padding:4px 14px; border-bottom:1px solid rgba(255,255,255,0.03); font-size:12px; }
.ev-icon { width:16px; text-align:center; }
.ev-type { width:65px; color:#10b981; }
.ev-target { flex:1; color:#94a3b8; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.ev-time { width:45px; text-align:right; color:#64748b; }
.pii-panel { padding:8px 14px; border-top:1px solid rgba(255,255,255,0.1); }
.pii-panel .label { font-size:11px; color:#94a3b8; margin-bottom:4px; }
.pii-tags { display:flex; flex-wrap:wrap; gap:4px; }
.pii-tag { background:rgba(255,255,255,0.1); padding:2px 8px; border-radius:10px; font-size:11px; display:flex; align-items:center; gap:4px; }
.pii-tag .remove { cursor:pointer; color:#ef4444; }
.pii-add { background:none; border:1px dashed rgba(255,255,255,0.2); padding:2px 8px; border-radius:10px; font-size:11px; cursor:pointer; color:#94a3b8; }
.pii-add:hover { border-color:#10b981; color:#10b981; }
.toolbox-pill { display:none; background:rgba(15,23,42,0.85); backdrop-filter:blur(20px); border:1px solid rgba(255,255,255,0.1); border-radius:20px; padding:6px 14px; color:#e2e8f0; cursor:pointer; align-items:center; gap:6px; font-size:12px; box-shadow:0 4px 12px rgba(0,0,0,0.3); }
.toolbox-pill:hover { border-color:#10b981; }
.recording-dot { width:8px; height:8px; border-radius:50%; background:#ef4444; animation:pulse 1.5s infinite; }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.4; } }
</style>`;
        }

        _getHTML() {
            return `
<div class="toolbox">
    <div class="header">
        <div class="header-title"><span class="recording-dot"></span> Behavior Tracker</div>
        <div class="header-actions">
            <button class="btn-minimize" title="Minimize">_</button>
            <button class="btn-close" title="Close">✕</button>
        </div>
    </div>
    <div class="status-bar">
        <span>Session: ${this._config.sessionId.slice(0, 8)}</span>
        <span>Events: <span class="event-counter">0</span></span>
    </div>
    <div class="controls">
        <button class="btn-record active">● Record</button>
        <button class="btn-pause">⏸ Pause</button>
        <button class="btn-stop">■ Stop</button>
    </div>
    <div class="event-list"></div>
    <div class="pii-panel">
        <div class="label">PII Whitelist</div>
        <div class="pii-tags" id="pii-tags"></div>
    </div>
</div>
<div class="toolbox-pill">
    <span class="recording-dot"></span>
    <span class="pill-counter">0 events</span>
    <span>▲</span>
</div>`;
        }

        _setupControls() {
            const s = this._shadow;
            s.querySelector('.btn-record')?.addEventListener('click', () => {
                this._engine.resume();
                s.querySelector('.btn-record').classList.add('active');
                s.querySelector('.btn-pause').classList.remove('active');
            });
            s.querySelector('.btn-pause')?.addEventListener('click', () => {
                this._engine.pause();
                s.querySelector('.btn-pause').classList.add('active');
                s.querySelector('.btn-record').classList.remove('active');
            });
            s.querySelector('.btn-stop')?.addEventListener('click', () => {
                this._engine.stop();
            });
            s.querySelector('.btn-minimize')?.addEventListener('click', () => this.minimize());
            s.querySelector('.btn-close')?.addEventListener('click', () => this.destroy());
            s.querySelector('.toolbox-pill')?.addEventListener('click', () => this.maximize());

            this._renderPIITags();
        }

        _renderPIITags() {
            const container = this._shadow.querySelector('#pii-tags');
            if (!container) return;

            const tags = this._pii.getWhitelist().map(sel =>
                `<span class="pii-tag">${this._esc(sel)}<span class="remove" data-sel="${this._esc(sel)}">✕</span></span>`
            ).join('');

            container.innerHTML = tags + '<button class="pii-add">+ Add</button>';

            container.querySelectorAll('.remove').forEach(el => {
                el.addEventListener('click', () => {
                    this._pii.removeFromWhitelist(el.dataset.sel);
                    this._renderPIITags();
                });
            });

            container.querySelector('.pii-add')?.addEventListener('click', () => {
                const sel = prompt('Enter CSS selector to reveal (e.g., .product-title):');
                if (sel && sel.trim()) {
                    this._pii.addToWhitelist(sel.trim());
                    this._renderPIITags();
                }
            });
        }

        _setupDrag() {
            const header = this._shadow.querySelector('.header');
            if (!header) return;
            let startX, startY, startBottom, startRight;

            const onMove = (e) => {
                const dx = e.clientX - startX;
                const dy = e.clientY - startY;
                const newRight = Math.max(0, startRight - dx);
                const newBottom = Math.max(0, startBottom - dy);
                this._host.style.right = newRight + 'px';
                this._host.style.bottom = newBottom + 'px';
            };

            const onUp = () => {
                document.removeEventListener('mousemove', onMove);
                document.removeEventListener('mouseup', onUp);
                header.style.cursor = 'grab';
            };

            header.addEventListener('mousedown', (e) => {
                e.preventDefault();
                startX = e.clientX;
                startY = e.clientY;
                const rect = this._host.getBoundingClientRect();
                startRight = window.innerWidth - rect.right;
                startBottom = window.innerHeight - rect.bottom;
                header.style.cursor = 'grabbing';
                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
            });
        }
    }

    // ========== Initialize all components ==========
    const buffer = new CircularBuffer(config.bufferCapacity || 10000);
    const backup = new BackupManager(config.sessionId);
    const piiMasker = new PIIMasker(config);
    const toolbox = new TrackerToolbox(config, null, piiMasker);

    const engine = new RecordingEngine(config, buffer, piiMasker, (e) => toolbox.appendEvent(e));
    toolbox._engine = engine;

    backup.restore(buffer);
    engine.start();
    toolbox.render();

    // Expose for collection by the agent
    window.__xipeBehaviorTracker = {
        collect: () => ({ events: buffer.toArray(), eventCount: buffer.getSize() }),
        stop: () => { engine.stop(); backup.flush(buffer); },
        pause: () => engine.pause(),
        resume: () => engine.resume(),
        getEventCount: () => buffer.getSize()
    };
}
