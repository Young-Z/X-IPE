/**
 * X-IPE Behavior Tracker — Lightweight IIFE (<5KB)
 * Passive event capture with minimal UI (Start/Stop/Analysis).
 * Control is handled by the mimic skill via Chrome DevTools MCP polling.
 */
if (!window.__xipeBehaviorTrackerInjected) {
    window.__xipeBehaviorTrackerInjected = true;

    const C = (typeof __xipeConfig !== 'undefined') ? __xipeConfig : {
        sessionId: 'unknown', purpose: '', piiWhitelist: [], bufferCapacity: 10000
    };

    class PIIMasker {
        constructor(cfg) {
            this._p = '[PASSWORD_FIELD]';
        }
        mask(r) {
            if (!r.target) return r;
            const t = r.target;
            if (t.tagName === 'INPUT' && (t.type === 'password' ||
                (t.autocomplete || '').includes('password'))) {
                t.textContent = this._p; t.value = this._p; return r;
            }
            return r;
        }
    }

    class CircularBuffer {
        constructor(cap) { this._c = cap; this._b = []; this._h = 0; this._s = 0; }
        push(item) {
            if (this._s < this._c) { this._b.push(item); this._s++; }
            else { this._b[this._h] = item; this._h = (this._h + 1) % this._c; }
        }
        toArray() {
            if (this._s < this._c) return this._b.slice();
            return [...this._b.slice(this._h), ...this._b.slice(0, this._h)];
        }
        clear() { this._b = []; this._h = 0; this._s = 0; }
        size() { return this._s; }
    }

    class EventSerializer {
        constructor() { this._t0 = Date.now(); }
        serialize(e, type) {
            const el = e.target;
            const r = {
                type, timestamp: Date.now(),
                target: this._ser(el),
                metadata: { pageUrl: location.href, pageTitle: document.title },
                details: {}
            };
            if (type === 'click' || type === 'double_click' || type === 'right_click')
                r.details = { x: e.clientX, y: e.clientY };
            else if (type === 'input')
                r.details = { inputType: e.inputType || '' };
            else if (type === 'scroll')
                r.details = { scrollX, scrollY };
            else if (type === 'navigation')
                r.details = { toUrl: location.href };
            return r;
        }
        _ser(el) {
            if (!el || !el.tagName) return { tagName: '', cssSelector: '' };
            let s = el.tagName.toLowerCase();
            if (el.id) s += '#' + el.id;
            else if (el.classList && el.classList.length) s += '.' + [...el.classList].join('.');
            return {
                tagName: el.tagName, cssSelector: s,
                textContent: (el.textContent || '').slice(0, 100),
                value: el.value || '', type: el.type || '',
                autocomplete: el.autocomplete || ''
            };
        }
    }

    class RecordingEngine {
        constructor(buf, pii) {
            this._buf = buf; this._pii = pii;
            this._ser = new EventSerializer();
            this._on = false; this._ls = new Map();
        }
        start() {
            if (this._on) return;
            this._on = true;
            this._add('click', 'click'); this._add('dblclick', 'double_click');
            this._add('contextmenu', 'right_click'); this._add('input', 'input');
            this._addD('scroll', 'scroll', 200);
            this._add('popstate', 'navigation'); this._add('hashchange', 'navigation');
            this._add('focusin', 'focus'); this._add('focusout', 'focus');
            this._add('dragstart', 'drag'); this._add('dragend', 'drag');
        }
        stop() {
            this._on = false;
            for (const [n, h] of this._ls) {
                document.removeEventListener(n, h, true);
                window.removeEventListener(n, h, true);
            }
            this._ls.clear();
        }
        _add(ev, type) {
            const h = (e) => {
                if (!this._on) return;
                try { this._buf.push(this._pii.mask(this._ser.serialize(e, type))); } catch (_) {}
            };
            (['scroll', 'popstate', 'hashchange'].includes(ev) ? window : document)
                .addEventListener(ev, h, true);
            this._ls.set(ev, h);
        }
        _addD(ev, type, ms) {
            let t = null;
            const h = () => {
                if (!this._on) return;
                clearTimeout(t);
                t = setTimeout(() => {
                    try { this._buf.push(this._pii.mask(this._ser.serialize({ target: document.scrollingElement }, type))); } catch (_) {}
                }, ms);
            };
            window.addEventListener(ev, h, true);
            this._ls.set(ev, h);
        }
    }

    // LocalStorage backup
    const LS_KEY = '__xipe_bk_' + C.sessionId;
    const ANALYSIS_KEY = LS_KEY + '_analysis';
    function lsFlush(buf) {
        try { localStorage.setItem(LS_KEY, JSON.stringify(buf.toArray())); } catch (_) {}
    }
    function lsRestore(buf) {
        try {
            const d = JSON.parse(localStorage.getItem(LS_KEY) || '[]');
            if (Array.isArray(d)) d.forEach(e => buf.push(e));
            localStorage.removeItem(LS_KEY);
        } catch (_) {}
    }

    // Init
    const buf = new CircularBuffer(C.bufferCapacity || 10000);
    const pii = new PIIMasker(C);
    const eng = new RecordingEngine(buf, pii);

    lsRestore(buf);

    // Minimal UI bar
    const bar = document.createElement('div');
    bar.id = '__xipe-tracker-bar';
    bar.innerHTML = '<button id="__xb-start">● Start</button><button id="__xb-stop">■ Stop</button>'
        + '<button id="__xb-analysis">📊 Analysis</button><span id="__xb-count">0</span>';
    bar.style.cssText = 'position:fixed;bottom:0;left:0;right:0;height:32px;background:#1e293b;color:#e2e8f0;'
        + 'display:flex;align-items:center;gap:8px;padding:0 12px;z-index:2147483640;font:12px sans-serif;';
    const btnStyle = 'background:none;border:1px solid #475569;color:inherit;padding:2px 10px;'
        + 'border-radius:4px;cursor:pointer;font:inherit;';
    document.body.appendChild(bar);
    bar.querySelectorAll('button').forEach(b => b.style.cssText = btnStyle);
    bar.querySelector('#__xb-count').style.cssText = 'margin-left:auto;color:#94a3b8;';

    bar.querySelector('#__xb-start').onclick = () => {
        eng.start(); window.__xipe_status = 'recording';
        bar.querySelector('#__xb-start').style.color = '#4ade80';
        bar.querySelector('#__xb-stop').style.color = '';
    };
    bar.querySelector('#__xb-stop').onclick = () => {
        eng.stop(); lsFlush(buf); window.__xipe_status = 'stopped';
        bar.querySelector('#__xb-stop').style.color = '#f87171';
        bar.querySelector('#__xb-start').style.color = '';
    };
    bar.querySelector('#__xb-analysis').onclick = () => {
        window.__xipe_analysis_requested = true;
        try { localStorage.setItem(ANALYSIS_KEY, 'true'); } catch (_) {}
        const btn = bar.querySelector('#__xb-analysis');
        btn.textContent = '⏳ Analyzing...'; btn.disabled = true;
    };

    // Periodic: update counter + flush to localStorage (survives page redirect)
    setInterval(() => {
        const el = document.getElementById('__xipe-tracker-bar');
        if (el) { const c = el.querySelector('#__xb-count'); if (c) c.textContent = buf.size() + ' events'; }
        if (window.__xipe_status === 'recording') lsFlush(buf);
    }, 1000);

    // Expose API for polling by the mimic skill
    window.__xipeBehaviorTracker = {
        collect: () => ({ events: buf.toArray(), eventCount: buf.size(), url: location.href }),
        stop: () => { eng.stop(); lsFlush(buf); },
        start: () => {
            eng.start(); window.__xipe_status = 'recording';
            const b = document.getElementById('__xipe-tracker-bar');
            if (b) { b.querySelector('#__xb-start').style.color = '#4ade80'; b.querySelector('#__xb-stop').style.color = ''; }
        },
        clear: () => buf.clear(),
        getStatus: () => window.__xipe_status || 'idle',
        getAnalysisFlag: () => {
            let stored = false;
            try { stored = localStorage.getItem(ANALYSIS_KEY) === 'true'; } catch (_) {}
            return !!window.__xipe_analysis_requested || stored;
        },
        resetAnalysisUI: () => {
            window.__xipe_analysis_requested = false;
            try { localStorage.removeItem(ANALYSIS_KEY); } catch (_) {}
            const b = document.getElementById('__xipe-tracker-bar');
            if (b) { const a = b.querySelector('#__xb-analysis'); if (a) { a.textContent = '📊 Analysis'; a.disabled = false; } }
        }
    };

    window.__xipe_status = 'idle';
    try { window.__xipe_analysis_requested = localStorage.getItem(ANALYSIS_KEY) === 'true'; }
    catch (_) { window.__xipe_analysis_requested = false; }
}
