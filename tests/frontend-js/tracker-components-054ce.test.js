/**
 * FEATURE-054-C: CircularBuffer Tests
 * FEATURE-054-E: PIIMasker Tests
 * Tests for injected tracker-toolbar.js components (CR-001: simplified <5KB IIFE)
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';

function makeMockElement(tag) {
    const children = {};
    const el = {
        id: '', tagName: tag, style: { cssText: '' }, textContent: '',
        _innerHTML: '',
        get innerHTML() { return this._innerHTML; },
        set innerHTML(v) {
            this._innerHTML = v;
            // Parse button/span ids from simple HTML
            const re = /id="([^"]+)"/g;
            let m;
            while ((m = re.exec(v)) !== null) {
                children[`#${m[1]}`] = makeMockElement('SPAN');
            }
        },
        querySelector: (sel) => children[sel] || null,
        querySelectorAll: (sel) => {
            if (sel === 'button') {
                return Object.values(children).filter(() => true).map(c => { c.style = c.style || { cssText: '' }; return c; });
            }
            return [];
        },
        appendChild: () => {},
        onclick: null
    };
    return el;
}

function loadTrackerSandbox() {
    const source = readFileSync(
        resolve(import.meta.dirname, '../../.github/skills/x-ipe-tool-learning-behavior-tracker-for-web/references/tracker-toolbar.js'),
        'utf-8'
    );

    const sandbox = {
        window: { __xipeBehaviorTrackerInjected: false },
        document: {
            createElement: (tag) => makeMockElement(tag),
            body: { appendChild: () => {} },
            getElementById: () => null,
            title: 'Test Page',
            addEventListener: () => {},
            removeEventListener: () => {},
            scrollingElement: { tagName: 'HTML' }
        },
        location: { href: 'https://test.example.com/page' },
        scrollX: 0, scrollY: 0,
        setInterval: () => 0,
        clearInterval: () => {},
        clearTimeout: () => {},
        setTimeout: (fn) => { fn(); return 0; },
        __xipeConfig: {
            sessionId: 'test-session',
            purpose: 'Test',
            piiWhitelist: [],
            bufferCapacity: 100
        },
        console: { log: () => {}, warn: () => {}, error: () => {} },
        localStorage: { setItem: () => {}, getItem: () => null, removeItem: () => {} },
        JSON: JSON,
        Date: Date,
    };
    sandbox.globalThis = sandbox;
    vm.createContext(sandbox);
    vm.runInContext(source, sandbox);
    return sandbox;
}

function extractClass(className) {
    const source = readFileSync(
        resolve(import.meta.dirname, '../../.github/skills/x-ipe-tool-learning-behavior-tracker-for-web/references/tracker-toolbar.js'),
        'utf-8'
    );
    const start = source.indexOf(`class ${className} {`);
    if (start === -1) return null;
    let depth = 0;
    let i = source.indexOf('{', start);
    for (; i < source.length; i++) {
        if (source[i] === '{') depth++;
        if (source[i] === '}') depth--;
        if (depth === 0) break;
    }
    return source.substring(start, i + 1);
}

function makeClass(className) {
    const code = extractClass(className);
    if (!code) throw new Error(`Class ${className} not found`);
    return eval(`(${code})`);
}

let CircularBuffer, PIIMasker;
try {
    CircularBuffer = makeClass('CircularBuffer');
    PIIMasker = makeClass('PIIMasker');
} catch (e) {
    // Will fail in tests with descriptive error
}

describe('CircularBuffer (FEATURE-054-C)', () => {
    it('should push and retrieve items', () => {
        const buf = new CircularBuffer(5);
        buf.push('a'); buf.push('b'); buf.push('c');
        expect(buf.toArray()).toEqual(['a', 'b', 'c']);
        expect(buf.size()).toBe(3);
    });

    it('should prune oldest when full', () => {
        const buf = new CircularBuffer(3);
        buf.push('a'); buf.push('b'); buf.push('c'); buf.push('d');
        expect(buf.toArray()).toEqual(['b', 'c', 'd']);
        expect(buf.size()).toBe(3);
    });

    it('should handle wrapping correctly', () => {
        const buf = new CircularBuffer(3);
        for (let i = 1; i <= 5; i++) buf.push(i);
        expect(buf.toArray()).toEqual([3, 4, 5]);
    });

    it('should clear buffer', () => {
        const buf = new CircularBuffer(5);
        buf.push('a'); buf.push('b');
        buf.clear();
        expect(buf.toArray()).toEqual([]);
        expect(buf.size()).toBe(0);
    });

    it('should handle capacity of 1', () => {
        const buf = new CircularBuffer(1);
        buf.push('a');
        expect(buf.toArray()).toEqual(['a']);
        buf.push('b');
        expect(buf.toArray()).toEqual(['b']);
    });

    it('should handle large capacity', () => {
        const buf = new CircularBuffer(10000);
        for (let i = 0; i < 100; i++) buf.push(i);
        expect(buf.size()).toBe(100);
    });
});

describe('PIIMasker (FEATURE-054-E)', () => {
    it('should preserve text content by default', () => {
        const pii = new PIIMasker({ piiWhitelist: [] });
        const event = {
            type: 'click',
            target: { tagName: 'BUTTON', textContent: 'Buy Now', value: '', cssSelector: 'button.buy' }
        };
        const result = pii.mask(event);
        expect(result.target.textContent).toBe('Buy Now');
    });

    it('should preserve text for all selectors', () => {
        const pii = new PIIMasker({ piiWhitelist: [] });
        const event = {
            type: 'click',
            target: { tagName: 'H2', textContent: 'iPhone 15', value: '', cssSelector: 'h2.product-title' }
        };
        const result = pii.mask(event);
        expect(result.target.textContent).toBe('iPhone 15');
    });

    it('should ALWAYS mask password fields', () => {
        const pii = new PIIMasker({ piiWhitelist: ['input#password'] });
        const event = {
            type: 'input',
            target: {
                tagName: 'INPUT', type: 'password', textContent: '', value: 'secret123',
                cssSelector: 'input#password', autocomplete: ''
            }
        };
        const result = pii.mask(event);
        expect(result.target.value).toBe('[PASSWORD_FIELD]');
    });

    it('should mask autocomplete password fields', () => {
        const pii = new PIIMasker({ piiWhitelist: [] });
        const event = {
            type: 'input',
            target: {
                tagName: 'INPUT', type: 'text', textContent: '', value: 'secret',
                cssSelector: 'input.pw', autocomplete: 'current-password'
            }
        };
        const result = pii.mask(event);
        expect(result.target.value).toBe('[PASSWORD_FIELD]');
    });

    it('should handle events without target', () => {
        const pii = new PIIMasker({ piiWhitelist: [] });
        const event = { type: 'scroll' };
        expect(pii.mask(event).type).toBe('scroll');
    });

    it('should not mask empty textContent', () => {
        const pii = new PIIMasker({ piiWhitelist: [] });
        const event = {
            type: 'click',
            target: { tagName: 'DIV', textContent: '', value: '', cssSelector: 'div.empty' }
        };
        expect(pii.mask(event).target.textContent).toBe('');
    });

    it('should preserve original textContent (no default masking)', () => {
        const pii = new PIIMasker({ piiWhitelist: [] });
        const event = {
            type: 'click',
            target: { tagName: 'BUTTON', textContent: 'Buy Now', value: '', cssSelector: 'button.buy' }
        };
        const result = pii.mask(event);
        expect(result.target.textContent).toBe('Buy Now');
    });

    it('should preserve original input value (no default masking)', () => {
        const pii = new PIIMasker({ piiWhitelist: [] });
        const event = {
            type: 'input',
            target: { tagName: 'INPUT', type: 'text', textContent: '', value: 'search query', cssSelector: 'input.search', autocomplete: '' }
        };
        const result = pii.mask(event);
        expect(result.target.value).toBe('search query');
    });
});

describe('Tracker IIFE Integration (CR-001)', () => {
    let sandbox;
    beforeEach(() => {
        try { sandbox = loadTrackerSandbox(); } catch (e) { sandbox = null; }
    });

    it('should expose __xipeBehaviorTracker API', () => {
        expect(sandbox.window.__xipeBehaviorTracker).toBeDefined();
        expect(typeof sandbox.window.__xipeBehaviorTracker.collect).toBe('function');
        expect(typeof sandbox.window.__xipeBehaviorTracker.stop).toBe('function');
        expect(typeof sandbox.window.__xipeBehaviorTracker.start).toBe('function');
        expect(typeof sandbox.window.__xipeBehaviorTracker.clear).toBe('function');
        expect(typeof sandbox.window.__xipeBehaviorTracker.getStatus).toBe('function');
        expect(typeof sandbox.window.__xipeBehaviorTracker.getAnalysisFlag).toBe('function');
    });

    it('should have collect return events array and url', () => {
        const result = sandbox.window.__xipeBehaviorTracker.collect();
        expect(result.events).toBeDefined();
        expect(Array.isArray(result.events)).toBe(true);
        expect(result.url).toBeDefined();
        expect(result.eventCount).toBeDefined();
    });

    it('should have analysis flag default to false', () => {
        const flag = sandbox.window.__xipeBehaviorTracker.getAnalysisFlag();
        expect(flag).toBe(false);
    });

    it('should set and clear analysis flag', () => {
        sandbox.window.__xipe_analysis_requested = true;
        const flag = sandbox.window.__xipeBehaviorTracker.getAnalysisFlag();
        expect(flag).toBe(true);
        // Should auto-clear after read
        expect(sandbox.window.__xipeBehaviorTracker.getAnalysisFlag()).toBe(false);
    });

    it('should have status default to idle', () => {
        expect(sandbox.window.__xipeBehaviorTracker.getStatus()).toBe('idle');
    });

    it('should set injection guard', () => {
        expect(sandbox.window.__xipeBehaviorTrackerInjected).toBe(true);
    });
});
