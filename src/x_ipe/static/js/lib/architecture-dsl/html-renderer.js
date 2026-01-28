/**
 * Architecture DSL HTML Renderer (Module View - Corporate Style)
 * 
 * Renders parsed Architecture DSL AST to pure HTML with inline styles.
 * Designed for embedding in markdown preview or other HTML contexts.
 * 
 * Features:
 * - Self-contained HTML with inline styles (no external CSS)
 * - Corporate style matching the Canvas renderer
 * - Layer auto-color detection
 * - 12-column grid layout
 * - Icon components (folder, file, db)
 * 
 * @module architecture-dsl/html-renderer
 */

// Module-level DSL store for copy button (when used as ES module)
const _dslStore = {};
let _dslIdCounter = 0;

// Export for external access
export function getDslFromStore(id) {
    return _dslStore[id];
}

export class ArchitectureHTMLRenderer {
    constructor(options = {}) {
        // Layout constants
        this.LAYER_GAP = options.layerGap || 16;
        this.MODULE_GAP = options.moduleGap || 14;
        this.COMPONENT_GAP = options.componentGap || 10;
        this.BORDER_RADIUS = options.borderRadius || 8;
        this.COMPONENT_RADIUS = options.componentRadius || 18;
        
        // Layer color auto-detection patterns
        this.LAYER_COLOR_PATTERNS = [
            { patterns: ['presentation', 'ui', 'frontend', 'view'], bg: '#fce7f3', border: '#ec4899' },
            { patterns: ['service', 'api', 'gateway'], bg: '#fef3c7', border: '#f97316' },
            { patterns: ['business', 'domain', 'logic', 'core'], bg: '#dbeafe', border: '#3b82f6' },
            { patterns: ['data', 'persistence', 'storage', 'db'], bg: '#dcfce7', border: '#22c55e' },
            { patterns: ['infrastructure', 'infra', 'platform'], bg: '#f3e8ff', border: '#a855f7' }
        ];
        
        // Colors (Corporate theme)
        this.colors = {
            background: '#f8fafc',
            backgroundGradientEnd: '#f1f5f9',
            layerBg: '#ffffff',
            layerBorder: '#374151',
            moduleBorder: '#d1d5db',
            badgeBg: '#1f2937',
            badgeText: '#ffffff',
            labelBg: '#1f2937',
            labelText: '#ffffff',
            titleText: '#374151',
            moduleTitle: '#374151',
            iconLabelText: '#6b7280',
            ...options.colors
        };
        
        // Fonts
        this.fonts = {
            heading: "'Inter', system-ui, -apple-system, sans-serif",
            body: "system-ui, -apple-system, sans-serif"
        };
        
        // Include hover effects (set false for static markdown)
        this.includeHoverEffects = options.includeHoverEffects !== false;
        
        // Include animations
        this.includeAnimations = options.includeAnimations !== false;
    }
    
    /**
     * Auto-detect layer colors based on layer name
     * @private
     */
    _detectLayerColors(layerName) {
        const nameLower = layerName.toLowerCase();
        for (const pattern of this.LAYER_COLOR_PATTERNS) {
            if (pattern.patterns.some(p => nameLower.includes(p))) {
                return { bg: pattern.bg, border: pattern.border };
            }
        }
        return { bg: this.colors.layerBg, border: this.colors.layerBorder };
    }

    /**
     * Render AST to HTML string
     * @param {Object} ast - Parsed DSL AST
     * @param {Object} options - Render options
     * @returns {string} HTML string
     */
    render(ast, options = {}) {
        const containerClass = options.className || 'arch-diagram';
        const includeWrapper = options.includeWrapper !== false;
        const originalDsl = options.originalDsl || '';
        
        // Store theme for use in layer rendering
        this.currentTheme = ast.theme || 'default';
        
        // Store canvas size for styling
        this.canvasSize = ast.canvas || null;
        
        let html = '';
        
        if (includeWrapper) {
            html += this._renderStyles(containerClass);
            
            // Apply canvas size if specified
            const canvasStyle = this.canvasSize 
                ? `width: ${this.canvasSize.width}; min-height: ${this.canvasSize.height};`
                : '';
            html += `<div class="${containerClass}"${canvasStyle ? ` style="${canvasStyle}"` : ''}>`;
            
            // Add copy button if DSL is provided - store DSL in module store to avoid escaping issues
            if (originalDsl) {
                const dslId = 'arch-dsl-' + (++_dslIdCounter);
                _dslStore[dslId] = originalDsl;
                html += `<button class="${containerClass}-copy-btn" data-dsl-id="${dslId}" onclick="ArchitectureDSL.copyDsl('${dslId}',this)" title="Copy DSL">📋</button>`;
            }
        }
        
        // Title
        if (ast.title) {
            html += `<div class="${containerClass}-title">${this._escapeHtml(ast.title)}</div>`;
        }
        
        // Layers container
        html += `<div class="${containerClass}-content">`;
        
        // Render each layer
        ast.layers.forEach((layer, index) => {
            html += this._renderLayer(layer, containerClass, index);
        });
        
        html += '</div>'; // content
        
        if (includeWrapper) {
            html += '</div>'; // container
        }
        
        return html;
    }
    
    /**
     * Render inline styles
     * @private
     */
    _renderStyles(containerClass) {
        const c = containerClass;
        const hoverStyles = this.includeHoverEffects ? `
            .${c}-layer-wrapper:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            }
            .${c}-layer-wrapper:hover .${c}-layer-label {
                background: #6366f1;
                min-width: 40px;
            }
            .${c}-layer-wrapper:hover .${c}-layer {
                border-color: #6366f1;
            }
            .${c}-module:hover {
                border-color: #3b82f6;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
                transform: scale(1.01);
            }
            .${c}-module:hover .${c}-module-title {
                color: #3b82f6;
            }
            .${c}-component:hover {
                background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
                transform: translateY(-2px) scale(1.02);
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            }
        ` : '';
        
        const animationStyles = this.includeAnimations ? `
            @keyframes ${c}-fadeSlideIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .${c}-layer-wrapper {
                animation: ${c}-fadeSlideIn 0.5s ease-out backwards;
            }
            .${c}-layer-wrapper:nth-child(1) { animation-delay: 0.1s; }
            .${c}-layer-wrapper:nth-child(2) { animation-delay: 0.2s; }
            .${c}-layer-wrapper:nth-child(3) { animation-delay: 0.3s; }
            .${c}-layer-wrapper:nth-child(4) { animation-delay: 0.4s; }
            .${c}-layer-wrapper:nth-child(5) { animation-delay: 0.5s; }
        ` : '';
        
        // If canvas size is specified, don't restrict with max-width
        const containerMaxWidth = this.canvasSize ? 'none' : '1200px';
        
        return `<style>
            .${c} {
                font-family: ${this.fonts.body};
                max-width: ${containerMaxWidth};
                margin: 0 auto;
                box-sizing: border-box;
                position: relative;
            }
            .${c}-copy-btn {
                position: absolute;
                top: 8px;
                right: 8px;
                width: 32px;
                height: 32px;
                border: none;
                border-radius: 6px;
                background: rgba(255,255,255,0.9);
                cursor: pointer;
                font-size: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0.6;
                transition: opacity 0.2s, background 0.2s;
                z-index: 10;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .${c}-copy-btn:hover {
                opacity: 1;
                background: #ffffff;
            }
            .${c}-title {
                font-family: ${this.fonts.heading};
                font-size: 26px;
                font-weight: 700;
                color: ${this.colors.titleText};
                text-align: center;
                margin-bottom: 24px;
            }
            .${c}-content {
                display: flex;
                flex-direction: column;
                gap: ${this.LAYER_GAP}px;
            }
            .${c}-layer-wrapper {
                display: flex;
                gap: 0;
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                border-radius: ${this.BORDER_RADIUS}px;
            }
            .${c}-layer-label {
                writing-mode: vertical-rl;
                text-orientation: mixed;
                transform: rotate(180deg);
                background: ${this.colors.labelBg};
                padding: 5px 3px;
                font-family: ${this.fonts.heading};
                font-size: 12px;
                font-weight: 600;
                color: ${this.colors.labelText};
                letter-spacing: 0.5px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 0 ${this.BORDER_RADIUS}px ${this.BORDER_RADIUS}px 0;
                min-width: 36px;
                transition: background 0.2s ease, min-width 0.2s ease;
                line-height: 1.3;
                text-align: center;
            }
            .${c}-layer {
                flex: 1;
                padding: 20px;
                border: 2px solid;
                border-left: none;
                border-radius: 0 ${this.BORDER_RADIUS}px ${this.BORDER_RADIUS}px 0;
                transition: border-color 0.2s ease;
            }
            .${c}-layer-row {
                display: grid;
                grid-template-columns: repeat(12, 1fr);
                gap: ${this.MODULE_GAP}px;
                align-items: start;
            }
            .${c}-module {
                background: ${this.colors.layerBg};
                border: 1.5px dashed ${this.colors.moduleBorder};
                border-radius: ${this.BORDER_RADIUS}px;
                padding: 14px;
                display: flex;
                flex-direction: column;
                gap: 12px;
                height: 100%;
                box-sizing: border-box;
                transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease;
            }
            .${c}-module-title {
                font-family: ${this.fonts.heading};
                font-size: 14px;
                font-weight: 700;
                color: ${this.colors.moduleTitle};
                text-align: left;
                transition: color 0.15s ease;
            }
            .${c}-module-content {
                display: grid;
                gap: ${this.COMPONENT_GAP}px;
                align-items: start;
            }
            .${c}-component {
                background: ${this.colors.badgeBg};
                color: ${this.colors.badgeText};
                border-radius: ${this.COMPONENT_RADIUS}px;
                padding: 3px 5px;
                font-family: ${this.fonts.heading};
                font-size: 12px;
                font-weight: 500;
                text-align: center;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 43px;
                cursor: default;
                transition: all 0.2s ease;
                line-height: 1.3;
            }
            .${c}-icon-component {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 6px;
                padding: 8px;
                min-height: 60px;
            }
            .${c}-icon {
                font-size: 28px;
                line-height: 1;
            }
            .${c}-icon-label {
                font-family: ${this.fonts.heading};
                font-size: 11px;
                font-weight: 500;
                color: ${this.colors.iconLabelText};
                text-align: center;
            }
            ${hoverStyles}
            ${animationStyles}
        </style>`;
    }
    
    /**
     * Render a layer
     * @private
     */
    _renderLayer(layer, containerClass, index) {
        const c = containerClass;
        
        // Only use auto-detected colors if theme is not default and layer has no explicit colors
        const useAutoColors = this.currentTheme && 
            this.currentTheme !== 'default' && 
            this.currentTheme !== 'theme-default';
        
        let layerBg, borderColor;
        
        if (layer.color) {
            // Explicit color set on layer
            layerBg = layer.color;
        } else if (useAutoColors) {
            // Auto-detect based on layer name (only for non-default themes)
            layerBg = this._detectLayerColors(layer.name).bg;
        } else {
            // Default: white background
            layerBg = this.colors.layerBg;
        }
        
        if (layer.borderColor) {
            // Explicit border color set on layer
            borderColor = layer.borderColor;
        } else if (useAutoColors) {
            // Auto-detect based on layer name (only for non-default themes)
            borderColor = this._detectLayerColors(layer.name).border;
        } else {
            // Default: gray border
            borderColor = this.colors.layerBorder;
        }
        
        let html = `<div class="${c}-layer-wrapper">`;
        
        // Side label
        html += `<div class="${c}-layer-label">${this._escapeHtml(layer.name.toUpperCase())}</div>`;
        
        // Layer content
        html += `<div class="${c}-layer" style="background: ${layerBg}; border-color: ${borderColor};">`;
        html += `<div class="${c}-layer-row">`;
        
        // Modules
        for (const module of layer.modules) {
            html += this._renderModule(module, containerClass);
        }
        
        html += '</div>'; // layer-row
        html += '</div>'; // layer
        html += '</div>'; // layer-wrapper
        
        return html;
    }
    
    /**
     * Render a module
     * @private
     */
    _renderModule(module, containerClass) {
        const c = containerClass;
        const gridCols = module.grid?.cols || 1;
        const gridRows = module.grid?.rows || 1;
        const gap = parseInt(module.gap) || this.COMPONENT_GAP;
        
        // Module spans columns in 12-col grid
        const colSpan = module.cols || 12;
        
        let html = `<div class="${c}-module" style="grid-column: span ${colSpan};">`;
        
        // Module title
        html += `<div class="${c}-module-title">${this._escapeHtml(module.name)}</div>`;
        
        // Module content with internal grid
        html += `<div class="${c}-module-content" style="grid-template-columns: repeat(${gridCols}, 1fr); gap: ${gap}px;">`;
        
        // Components
        for (const comp of module.components) {
            html += this._renderComponent(comp, containerClass);
        }
        
        html += '</div>'; // module-content
        html += '</div>'; // module
        
        return html;
    }
    
    /**
     * Render a component
     * @private
     */
    _renderComponent(component, containerClass) {
        const c = containerClass;
        const colSpan = component.cols || 1;
        const rowSpan = component.rows || 1;
        
        const gridStyle = `grid-column: span ${colSpan}; grid-row: span ${rowSpan};`;
        
        // Icon components
        if (component.stereotype && ['icon', 'folder', 'file', 'db'].includes(component.stereotype)) {
            return this._renderIconComponent(component, containerClass, gridStyle);
        }
        
        // Regular pill badge
        return `<div class="${c}-component" style="${gridStyle}">${this._escapeHtml(component.name)}</div>`;
    }
    
    /**
     * Render an icon component
     * @private
     */
    _renderIconComponent(component, containerClass, gridStyle) {
        const c = containerClass;
        const icons = {
            folder: '📁',
            file: '📄',
            db: '🗄️',
            database: '🗄️',
            icon: '⚙️',
            chart: '📊',
            cloud: '☁️'
        };
        
        const icon = icons[component.stereotype] || '📦';
        
        return `<div class="${c}-icon-component" style="${gridStyle}">
            <span class="${c}-icon">${icon}</span>
            <span class="${c}-icon-label">${this._escapeHtml(component.name)}</span>
        </div>`;
    }
    
    /**
     * Escape HTML special characters and convert \n to line breaks
     * @private
     */
    _escapeHtml(text) {
        const div = typeof document !== 'undefined' ? document.createElement('div') : null;
        let escaped;
        if (div) {
            div.textContent = text;
            escaped = div.innerHTML;
        } else {
            // Fallback for non-browser environments
            escaped = text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }
        // Convert \n (case-insensitive) to <br> for line breaks in component names
        return escaped.replace(/\s*\\n\s*/gi, '<br>');
    }
    
    /**
     * Render to a DOM element
     * @param {Object} ast - Parsed DSL AST
     * @param {HTMLElement} container - Target container element
     * @param {Object} options - Render options
     */
    renderToElement(ast, container, options = {}) {
        container.innerHTML = this.render(ast, options);
    }
}

export default ArchitectureHTMLRenderer;
