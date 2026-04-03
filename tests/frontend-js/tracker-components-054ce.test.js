/**
 * FEATURE-054-C: CircularBuffer Tests
 * FEATURE-054-E: PIIMasker Tests
 * Tests for injected tracker-toolbar.js components
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';

function loadTrackerClasses() {
    const source = readFileSync(
        resolve(import.meta.dirname, '../../.github/skills/x-ipe-learning-behavior-tracker-for-web/references/tracker-toolbar.js'),
        'utf-8'
    );

    // Execute the IIFE inside a sandbox with a mock window
    const sandbox = {
        window: { __xipeBehaviorTrackerInjected: false },
        document: { createElement: () => ({ attachShadow: () => ({ innerHTML: '' }), style: {} }), body: { appendChild: () => {} } },
        setInterval: () => 0,
        clearInterval: () => {},
        __xipeConfig: {
            sessionId: 'test',
            purpose: 'Test',
            piiWhitelist: [],
            bufferCapacity: 100
        },
        console: { log: () => {}, warn: () => {}, error: () => {} },
        localStorage: { setItem: () => {}, getItem: () => null, removeItem: () => {} },
        requestAnimationFrame: (fn) => fn(),
        JSON: JSON,
    };
    sandbox.globalThis = sandbox;
    vm.createContext(sandbox);
    vm.runInContext(source, sandbox);

    // After running, tracker object is on sandbox.window
    return sandbox;
}

let sandbox;
try {
    sandbox = loadTrackerClasses();
} catch (e) {
    // TDD phase — tests will skip if classes not available
}

// Extract classes by extracting just class code
function extractClass(className) {
    const source = readFileSync(
        resolve(import.meta.dirname, '../../.github/skills/x-ipe-learning-behavior-tracker-for-web/references/tracker-toolbar.js'),
        'utf-8'
    );
    // Find class definition (indented 4 spaces in the IIFE)
    const start = source.indexOf(`class ${className} {`);
    if (start === -1) return null;
    // Find matching closing brace at the same indent level
    let depth = 0;
    let i = source.indexOf('{', start);
    const startBrace = i;
    for (; i < source.length; i++) {
        if (source[i] === '{') depth++;
        if (source[i] === '}') depth--;
        if (depth === 0) break;
    }
    const classCode = source.substring(start, i + 1);
    return classCode;
}

// Create classes by eval-ing their source in isolation
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
        buf.push('a');
        buf.push('b');
        buf.push('c');
        expect(buf.toArray()).toEqual(['a', 'b', 'c']);
        expect(buf.getSize()).toBe(3);
    });

    it('should prune oldest when full', () => {
        const buf = new CircularBuffer(3);
        buf.push('a');
        buf.push('b');
        buf.push('c');
        buf.push('d'); // Should prune 'a'
        expect(buf.toArray()).toEqual(['b', 'c', 'd']);
        expect(buf.getSize()).toBe(3);
    });

    it('should handle wrapping correctly', () => {
        const buf = new CircularBuffer(3);
        buf.push(1);
        buf.push(2);
        buf.push(3);
        buf.push(4);
        buf.push(5);
        expect(buf.toArray()).toEqual([3, 4, 5]);
    });

    it('should report full correctly', () => {
        const buf = new CircularBuffer(2);
        expect(buf.isFull()).toBe(false);
        buf.push('a');
        expect(buf.isFull()).toBe(false);
        buf.push('b');
        expect(buf.isFull()).toBe(true);
    });

    it('should clear buffer', () => {
        const buf = new CircularBuffer(5);
        buf.push('a');
        buf.push('b');
        buf.clear();
        expect(buf.toArray()).toEqual([]);
        expect(buf.getSize()).toBe(0);
    });

    it('should handle capacity of 1', () => {
        const buf = new CircularBuffer(1);
        buf.push('a');
        expect(buf.toArray()).toEqual(['a']);
        buf.push('b');
        expect(buf.toArray()).toEqual(['b']);
    });

    it('should handle large capacity without overflow', () => {
        const buf = new CircularBuffer(10000);
        for (let i = 0; i < 100; i++) buf.push(i);
        expect(buf.getSize()).toBe(100);
        expect(buf.toArray().length).toBe(100);
    });
});

describe('PIIMasker (FEATURE-054-E)', () => {
    it('should mask text by default', () => {
        const pii = new PIIMasker({ piiWhitelist: [] });
        const event = {
            type: 'click',
            target: { tagName: 'BUTTON', textContent: 'Buy Now', value: '', cssSelector: 'button.buy' }
        };
        const result = pii.mask(event);
        expect(result.target.textContent).toBe('[MASKED]');
    });

    it('should reveal whitelisted selectors', () => {
        const pii = new PIIMasker({ piiWhitelist: ['.product-title'] });
        const event = {
            type: 'click',
            target: { tagName: 'H2', textContent: 'iPhone 15', value: '', cssSelector: 'h2.product-title' }
        };
        const result = pii.mask(event);
        expect(result.target.textContent).toBe('iPhone 15');
    });

    it('should ALWAYS mask password fields even if whitelisted', () => {
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

    it('should mask autocomplete=current-password fields', () => {
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
        const result = pii.mask(event);
        expect(result.type).toBe('scroll');
    });

    it('should add and remove whitelist entries', () => {
        const pii = new PIIMasker({ piiWhitelist: [] });
        pii.addToWhitelist('.name');
        expect(pii.getWhitelist()).toContain('.name');
        pii.removeFromWhitelist('.name');
        expect(pii.getWhitelist()).not.toContain('.name');
    });

    it('should not mask empty textContent', () => {
        const pii = new PIIMasker({ piiWhitelist: [] });
        const event = {
            type: 'click',
            target: { tagName: 'DIV', textContent: '', value: '', cssSelector: 'div.empty' }
        };
        const result = pii.mask(event);
        expect(result.target.textContent).toBe('');
    });
});
