/**
 * Architecture DSL Library
 * 
 * A standalone JavaScript library for parsing Architecture DSL and rendering
 * diagrams to HTML Canvas or pure HTML. Supports Module View (layered architecture) 
 * with the v2 grid-based layout system.
 * 
 * @module architecture-dsl
 * @version 1.1.0
 * 
 * @example
 * // Canvas rendering
 * import { renderToCanvas } from './architecture-dsl/index.js';
 * const canvas = document.getElementById('diagram');
 * renderToCanvas(dsl, canvas);
 * 
 * @example
 * // HTML rendering (for markdown preview)
 * import { renderToHTML } from './architecture-dsl/index.js';
 * const html = renderToHTML(dsl);
 * container.innerHTML = html;
 */

import { ArchitectureDSLParser } from './parser.js';
import { ArchitectureCanvasRenderer } from './renderer.js';
import { ArchitectureHTMLRenderer } from './html-renderer.js';

// Re-export classes
export { ArchitectureDSLParser, ArchitectureCanvasRenderer, ArchitectureHTMLRenderer };

/**
 * Parse DSL string to AST
 * @param {string} dsl - Architecture DSL source code
 * @returns {Object} Parsed AST
 */
export function parse(dsl) {
    const parser = new ArchitectureDSLParser();
    return parser.parse(dsl);
}

/**
 * Validate DSL syntax
 * @param {string} dsl - Architecture DSL source code
 * @returns {Object} Validation result { isValid, errors, warnings }
 */
export function validate(dsl) {
    const parser = new ArchitectureDSLParser();
    return parser.validate(dsl);
}

/**
 * Render AST to canvas
 * @param {Object} ast - Parsed AST from parse()
 * @param {HTMLCanvasElement} canvas - Target canvas element
 * @param {Object} options - Render options
 */
export function render(ast, canvas, options = {}) {
    const renderer = new ArchitectureCanvasRenderer(options);
    renderer.render(ast, canvas, options);
    return renderer;
}

/**
 * Convenience method: Parse DSL and render to canvas in one step
 * @param {string} dsl - Architecture DSL source code
 * @param {HTMLCanvasElement} canvas - Target canvas element
 * @param {Object} options - Render options
 * @returns {Object} Result with { ast, renderer, errors, warnings }
 */
export function renderToCanvas(dsl, canvas, options = {}) {
    const parser = new ArchitectureDSLParser();
    const ast = parser.parse(dsl);
    
    if (ast.errors.length > 0) {
        console.error('DSL Parse Errors:', ast.errors);
    }
    if (ast.warnings.length > 0) {
        console.warn('DSL Warnings:', ast.warnings);
    }
    
    const renderer = new ArchitectureCanvasRenderer(options);
    renderer.render(ast, canvas, options);
    
    return {
        ast,
        renderer,
        errors: ast.errors,
        warnings: ast.warnings
    };
}

/**
 * Export rendered canvas as PNG blob
 * @param {HTMLCanvasElement} canvas - Canvas with rendered diagram
 * @returns {Promise<Blob>}
 */
export function exportPNG(canvas) {
    return new Promise((resolve) => {
        canvas.toBlob(resolve, 'image/png');
    });
}

/**
 * Export rendered canvas as data URL
 * @param {HTMLCanvasElement} canvas - Canvas with rendered diagram
 * @returns {string}
 */
export function exportDataURL(canvas) {
    return canvas.toDataURL('image/png');
}

/**
 * Render AST to HTML string
 * @param {Object} ast - Parsed AST from parse()
 * @param {Object} options - Render options
 * @returns {string} HTML string
 */
export function renderHTML(ast, options = {}) {
    const renderer = new ArchitectureHTMLRenderer(options);
    return renderer.render(ast, options);
}

/**
 * Convenience method: Parse DSL and render to HTML string in one step
 * @param {string} dsl - Architecture DSL source code
 * @param {Object} options - Render options
 * @returns {Object} Result with { html, ast, errors, warnings }
 */
export function renderToHTML(dsl, options = {}) {
    const parser = new ArchitectureDSLParser();
    const ast = parser.parse(dsl);
    
    if (ast.errors.length > 0) {
        console.error('DSL Parse Errors:', ast.errors);
    }
    if (ast.warnings.length > 0) {
        console.warn('DSL Warnings:', ast.warnings);
    }
    
    const renderer = new ArchitectureHTMLRenderer(options);
    const html = renderer.render(ast, options);
    
    return {
        html,
        ast,
        renderer,
        errors: ast.errors,
        warnings: ast.warnings
    };
}

/**
 * Render DSL to a DOM element
 * @param {string} dsl - Architecture DSL source code
 * @param {HTMLElement} container - Target container element
 * @param {Object} options - Render options
 * @returns {Object} Result with { ast, errors, warnings }
 */
export function renderToElement(dsl, container, options = {}) {
    const result = renderToHTML(dsl, options);
    container.innerHTML = result.html;
    return result;
}

// Default export with all functions
export default {
    parse,
    validate,
    render,
    renderToCanvas,
    renderHTML,
    renderToHTML,
    renderToElement,
    exportPNG,
    exportDataURL,
    ArchitectureDSLParser,
    ArchitectureCanvasRenderer,
    ArchitectureHTMLRenderer
};
