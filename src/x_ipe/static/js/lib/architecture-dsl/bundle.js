/**
 * Architecture DSL Library - Bundle (IIFE)
 * 
 * Self-contained bundle that exposes ArchitectureDSL global object.
 * Use this in non-module scripts or HTML files.
 * 
 * @version 1.1.0
 * 
 * Usage:
 *   <script src="/static/js/lib/architecture-dsl/bundle.js"></script>
 *   <script>
 *     const result = ArchitectureDSL.renderToHTML(dsl);
 *     container.innerHTML = result.html;
 *   </script>
 */
(function(global) {
    'use strict';

    // Global store for DSL sources (for copy button)
    const _dslStore = {};
    let _dslIdCounter = 0;

    // =========================================================================
    // Parser
    // =========================================================================
    
    class ArchitectureDSLParser {
        constructor() {
            this.errors = [];
            this.warnings = [];
        }

        parse(dsl) {
            this.errors = [];
            this.warnings = [];
            
            const lines = dsl.split('\n');
            const ast = {
                type: 'document',
                viewType: null,
                title: null,
                theme: 'theme-default',
                direction: 'top-to-bottom',
                canvas: null,  // e.g., { width: '1200px', height: '600px' }
                grid: { cols: 12, rows: 6 },
                textAlign: 'left',
                layers: [],
                errors: this.errors,
                warnings: this.warnings
            };

            let currentLayer = null;
            let currentModule = null;
            let lineNum = 0;
            let inMultiLineComment = false;

            for (const rawLine of lines) {
                lineNum++;
                let line = rawLine.trim();

                // Handle multi-line comments
                if (inMultiLineComment) {
                    if (line.includes("'/")) {
                        inMultiLineComment = false;
                    }
                    continue;
                }
                if (line.startsWith("/'")) {
                    inMultiLineComment = true;
                    continue;
                }

                // Skip single-line comments and empty lines
                if (line.startsWith("'") || line === '') continue;

                // Remove inline comments
                const commentIdx = line.indexOf("'");
                if (commentIdx > 0) {
                    line = line.substring(0, commentIdx).trim();
                }

                // Parse header
                if (line.startsWith('@startuml')) {
                    const match = line.match(/@startuml\s+(module-view|landscape-view)/);
                    if (match) {
                        ast.viewType = match[1];
                    } else {
                        this.errors.push({ line: lineNum, message: 'Invalid @startuml header. Use @startuml module-view or @startuml landscape-view' });
                    }
                    continue;
                }

                if (line === '@enduml') continue;

                // Parse title
                if (line.startsWith('title ')) {
                    const match = line.match(/title\s+"([^"]+)"/);
                    if (match) ast.title = match[1];
                    continue;
                }

                // Parse theme
                if (line.startsWith('theme ')) {
                    const match = line.match(/theme\s+"([^"]+)"/);
                    if (match) ast.theme = match[1];
                    continue;
                }

                // Parse direction
                if (line.startsWith('direction ')) {
                    const match = line.match(/direction\s+(top-to-bottom|left-to-right)/);
                    if (match) ast.direction = match[1];
                    continue;
                }

                // Parse canvas (explicit size: canvas 1200px, 600px or canvas 1200px 600px)
                if (line.startsWith('canvas ')) {
                    const match = line.match(/canvas\s+(\d+(?:px|%)?)\s*[,\s]\s*(\d+(?:px|%)?)/);
                    if (match) {
                        // Add 'px' unit if not specified
                        const width = match[1].match(/\d+$/) ? match[1] + 'px' : match[1];
                        const height = match[2].match(/\d+$/) ? match[2] + 'px' : match[2];
                        ast.canvas = { width, height };
                    }
                    continue;
                }

                // Parse document grid
                if (line.startsWith('grid ') && !currentModule) {
                    const match = line.match(/grid\s+(\d+)\s*x\s*(\d+)/);
                    if (match) {
                        ast.grid = { cols: parseInt(match[1]), rows: parseInt(match[2]) };
                    }
                    continue;
                }

                // Parse text-align at document level
                if (line.startsWith('text-align ') && !currentLayer && !currentModule) {
                    const match = line.match(/text-align\s+(left|center|right)/);
                    if (match) ast.textAlign = match[1];
                    continue;
                }

                // Parse layer
                if (line.startsWith('layer ')) {
                    const match = line.match(/layer\s+"([^"]+)"(?:\s+as\s+(\w+))?\s*\{?/);
                    if (match) {
                        currentLayer = {
                            type: 'layer',
                            name: match[1],
                            alias: match[2] || null,
                            rows: 1,
                            color: null,
                            borderColor: null,
                            textAlign: ast.textAlign,
                            modules: []
                        };
                        ast.layers.push(currentLayer);
                    }
                    continue;
                }

                // Inside layer
                if (currentLayer && !currentModule) {
                    if (line.startsWith('rows ')) {
                        const match = line.match(/rows\s+(\d+)/);
                        if (match) currentLayer.rows = parseInt(match[1]);
                        continue;
                    }
                    if (line.startsWith('color ')) {
                        const match = line.match(/color\s+"([^"]+)"/);
                        if (match) currentLayer.color = match[1];
                        continue;
                    }
                    if (line.startsWith('border-color ')) {
                        const match = line.match(/border-color\s+"([^"]+)"/);
                        if (match) currentLayer.borderColor = match[1];
                        continue;
                    }
                    if (line.startsWith('text-align ')) {
                        const match = line.match(/text-align\s+(left|center|right)/);
                        if (match) currentLayer.textAlign = match[1];
                        continue;
                    }
                    if (line.startsWith('module ')) {
                        const match = line.match(/module\s+"([^"]+)"(?:\s+as\s+(\w+))?\s*\{?/);
                        if (match) {
                            currentModule = {
                                type: 'module',
                                name: match[1],
                                alias: match[2] || null,
                                cols: 12,
                                rows: 1,
                                grid: { cols: 1, rows: 1 },
                                align: { h: 'center', v: 'center' },
                                gap: '8px',
                                color: null,
                                textAlign: currentLayer.textAlign,
                                components: []
                            };
                            currentLayer.modules.push(currentModule);
                        }
                        continue;
                    }
                    if (line === '}') {
                        currentLayer = null;
                        continue;
                    }
                }

                // Inside module
                if (currentModule) {
                    if (line.startsWith('cols ')) {
                        const match = line.match(/cols\s+(\d+)/);
                        if (match) currentModule.cols = parseInt(match[1]);
                        continue;
                    }
                    if (line.startsWith('rows ') && !line.includes(',')) {
                        const match = line.match(/rows\s+(\d+)/);
                        if (match) currentModule.rows = parseInt(match[1]);
                        continue;
                    }
                    if (line.startsWith('grid ')) {
                        const match = line.match(/grid\s+(\d+)\s*x\s*(\d+)/);
                        if (match) {
                            currentModule.grid = { cols: parseInt(match[1]), rows: parseInt(match[2]) };
                        }
                        continue;
                    }
                    if (line.startsWith('align ')) {
                        const match = line.match(/align\s+(left|center|right)\s+(top|center|bottom)/);
                        if (match) {
                            currentModule.align = { h: match[1], v: match[2] };
                        }
                        continue;
                    }
                    if (line.startsWith('gap ')) {
                        const match = line.match(/gap\s+(\d+(?:px|rem))/);
                        if (match) currentModule.gap = match[1];
                        continue;
                    }
                    if (line.startsWith('color ')) {
                        const match = line.match(/color\s+"([^"]+)"/);
                        if (match) currentModule.color = match[1];
                        continue;
                    }
                    if (line.startsWith('text-align ')) {
                        const match = line.match(/text-align\s+(left|center|right)/);
                        if (match) currentModule.textAlign = match[1];
                        continue;
                    }
                    if (line.startsWith('component ')) {
                        const component = this._parseComponent(line, lineNum);
                        if (component) {
                            currentModule.components.push(component);
                        }
                        continue;
                    }
                    if (line === '}') {
                        currentModule = null;
                        continue;
                    }
                }
            }

            this._validate(ast);
            return ast;
        }

        _parseComponent(line, lineNum) {
            const match = line.match(/component\s+"([^"]+)"(?:\s*\{\s*cols\s+(\d+)(?:\s*,\s*rows\s+(\d+))?\s*\})?(?:\s*<<(\w+)>>)?/);
            if (match) {
                return {
                    type: 'component',
                    name: match[1],
                    cols: match[2] ? parseInt(match[2]) : 1,
                    rows: match[3] ? parseInt(match[3]) : 1,
                    stereotype: match[4] || null
                };
            }
            this.errors.push({ line: lineNum, message: `Invalid component syntax: ${line}` });
            return null;
        }

        _validate(ast) {
            if (!ast.viewType) {
                this.errors.push({ line: 1, message: 'Missing @startuml header with view type' });
            }
            for (const layer of ast.layers) {
                const colsSum = layer.modules.reduce((sum, m) => sum + m.cols, 0);
                if (colsSum !== 12 && layer.modules.length > 0) {
                    this.warnings.push({ layer: layer.name, message: `Module cols sum to ${colsSum}, expected 12` });
                }
                if (!layer.rows || layer.rows < 1) {
                    this.warnings.push({ layer: layer.name, message: 'Layer missing rows declaration' });
                }
            }
        }

        validate(dsl) {
            const ast = this.parse(dsl);
            return { isValid: ast.errors.length === 0, errors: ast.errors, warnings: ast.warnings };
        }
    }

    // =========================================================================
    // HTML Renderer
    // =========================================================================
    
    class ArchitectureHTMLRenderer {
        constructor(options = {}) {
            this.LAYER_GAP = options.layerGap || 16;
            this.MODULE_GAP = options.moduleGap || 14;
            this.COMPONENT_GAP = options.componentGap || 10;
            this.BORDER_RADIUS = options.borderRadius || 8;
            this.COMPONENT_RADIUS = options.componentRadius || 18;
            
            this.LAYER_COLOR_PATTERNS = [
                { patterns: ['presentation', 'ui', 'frontend', 'view'], bg: '#fce7f3', border: '#ec4899' },
                { patterns: ['service', 'api', 'gateway'], bg: '#fef3c7', border: '#f97316' },
                { patterns: ['business', 'domain', 'logic', 'core'], bg: '#dbeafe', border: '#3b82f6' },
                { patterns: ['data', 'persistence', 'storage', 'db'], bg: '#dcfce7', border: '#22c55e' },
                { patterns: ['infrastructure', 'infra', 'platform'], bg: '#f3e8ff', border: '#a855f7' }
            ];
            
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
            
            this.fonts = {
                heading: "'Inter', system-ui, -apple-system, sans-serif",
                body: "system-ui, -apple-system, sans-serif"
            };
            
            this.includeHoverEffects = options.includeHoverEffects !== false;
            this.includeAnimations = options.includeAnimations !== false;
        }
        
        _detectLayerColors(layerName) {
            const nameLower = layerName.toLowerCase();
            for (const pattern of this.LAYER_COLOR_PATTERNS) {
                if (pattern.patterns.some(p => nameLower.includes(p))) {
                    return { bg: pattern.bg, border: pattern.border };
                }
            }
            return { bg: this.colors.layerBg, border: this.colors.layerBorder };
        }

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
                
                // Add copy button if DSL is provided - store DSL in global map to avoid escaping issues
                if (originalDsl) {
                    const dslId = 'arch-dsl-' + (++_dslIdCounter);
                    _dslStore[dslId] = originalDsl;
                    html += `<button class="${containerClass}-copy-btn" data-dsl-id="${dslId}" onclick="ArchitectureDSL.copyDsl('${dslId}',this)" title="Copy DSL">📋</button>`;
                }
            }
            
            if (ast.title) {
                html += `<div class="${containerClass}-title">${this._escapeHtml(ast.title)}</div>`;
            }
            
            html += `<div class="${containerClass}-content">`;
            
            ast.layers.forEach((layer, index) => {
                html += this._renderLayer(layer, containerClass, index);
            });
            
            html += '</div>';
            
            if (includeWrapper) {
                html += '</div>';
            }
            
            return html;
        }
        
        _renderStyles(containerClass) {
            const c = containerClass;
            const hoverStyles = this.includeHoverEffects ? `
                .${c}-layer-wrapper:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1); }
                .${c}-layer-wrapper:hover .${c}-layer-label { background: #6366f1; min-width: 40px; }
                .${c}-layer-wrapper:hover .${c}-layer { border-color: #6366f1; }
                .${c}-module:hover { border-color: #3b82f6; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); transform: scale(1.01); }
                .${c}-module:hover .${c}-module-title { color: #3b82f6; }
                .${c}-component:hover { background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%); transform: translateY(-2px) scale(1.02); box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
            ` : '';
            
            const animationStyles = this.includeAnimations ? `
                @keyframes ${c}-fadeSlideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
                .${c}-layer-wrapper { animation: ${c}-fadeSlideIn 0.5s ease-out backwards; }
                .${c}-layer-wrapper:nth-child(1) { animation-delay: 0.1s; }
                .${c}-layer-wrapper:nth-child(2) { animation-delay: 0.2s; }
                .${c}-layer-wrapper:nth-child(3) { animation-delay: 0.3s; }
                .${c}-layer-wrapper:nth-child(4) { animation-delay: 0.4s; }
                .${c}-layer-wrapper:nth-child(5) { animation-delay: 0.5s; }
            ` : '';
            
            // If canvas size is specified, don't restrict with max-width
            const containerMaxWidth = this.canvasSize ? 'none' : '1200px';
            
            return `<style>
                .${c} { font-family: ${this.fonts.body}; max-width: ${containerMaxWidth}; margin: 0 auto; box-sizing: border-box; position: relative; }
                .${c}-copy-btn { position: absolute; top: 8px; right: 8px; width: 32px; height: 32px; border: none; border-radius: 6px; background: rgba(255,255,255,0.9); cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; opacity: 0.6; transition: opacity 0.2s, background 0.2s; z-index: 10; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
                .${c}-copy-btn:hover { opacity: 1; background: #ffffff; }
                .${c}-title { font-family: ${this.fonts.heading}; font-size: 26px; font-weight: 700; color: ${this.colors.titleText}; text-align: center; margin-bottom: 24px; }
                .${c}-content { display: flex; flex-direction: column; gap: ${this.LAYER_GAP}px; }
                .${c}-layer-wrapper { display: flex; gap: 0; transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1); border-radius: ${this.BORDER_RADIUS}px; }
                .${c}-layer-label { writing-mode: vertical-rl; text-orientation: mixed; transform: rotate(180deg); background: ${this.colors.labelBg}; padding: 5px 3px; font-family: ${this.fonts.heading}; font-size: 12px; font-weight: 600; color: ${this.colors.labelText}; letter-spacing: 0.5px; display: flex; align-items: center; justify-content: center; border-radius: 0 ${this.BORDER_RADIUS}px ${this.BORDER_RADIUS}px 0; min-width: 36px; transition: background 0.2s ease, min-width 0.2s ease; line-height: 1.3; text-align: center; }
                .${c}-layer { flex: 1; padding: 20px; border: 2px solid; border-left: none; border-radius: 0 ${this.BORDER_RADIUS}px ${this.BORDER_RADIUS}px 0; transition: border-color 0.2s ease; }
                .${c}-layer-row { display: grid; grid-template-columns: repeat(12, 1fr); gap: ${this.MODULE_GAP}px; align-items: start; }
                .${c}-module { background: ${this.colors.layerBg}; border: 1.5px dashed ${this.colors.moduleBorder}; border-radius: ${this.BORDER_RADIUS}px; padding: 14px; display: flex; flex-direction: column; gap: 12px; height: 100%; box-sizing: border-box; transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease; }
                .${c}-module-title { font-family: ${this.fonts.heading}; font-size: 14px; font-weight: 700; color: ${this.colors.moduleTitle}; text-align: left; transition: color 0.15s ease; }
                .${c}-module-content { display: grid; gap: ${this.COMPONENT_GAP}px; align-items: start; }
                .${c}-component { background: ${this.colors.badgeBg}; color: ${this.colors.badgeText}; border-radius: ${this.COMPONENT_RADIUS}px; padding: 3px 5px; font-family: ${this.fonts.heading}; font-size: 12px; font-weight: 500; text-align: center; display: flex; align-items: center; justify-content: center; min-height: 43px; cursor: default; transition: all 0.2s ease; line-height: 1.3; }
                .${c}-icon-component { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; padding: 8px; min-height: 60px; }
                .${c}-icon { font-size: 28px; line-height: 1; }
                .${c}-icon-label { font-family: ${this.fonts.heading}; font-size: 11px; font-weight: 500; color: ${this.colors.iconLabelText}; text-align: center; }
                ${hoverStyles}
                ${animationStyles}
            </style>`;
        }
        
        _renderLayer(layer, containerClass, index) {
            const c = containerClass;
            
            // Only use auto-detected colors if theme is not default and layer has no explicit colors
            const useAutoColors = this.currentTheme && 
                this.currentTheme !== 'default' && 
                this.currentTheme !== 'theme-default';
            
            let layerBg, borderColor;
            
            if (layer.color) {
                layerBg = layer.color;
            } else if (useAutoColors) {
                layerBg = this._detectLayerColors(layer.name).bg;
            } else {
                layerBg = this.colors.layerBg;
            }
            
            if (layer.borderColor) {
                borderColor = layer.borderColor;
            } else if (useAutoColors) {
                borderColor = this._detectLayerColors(layer.name).border;
            } else {
                borderColor = this.colors.layerBorder;
            }
            
            let html = `<div class="${c}-layer-wrapper">`;
            html += `<div class="${c}-layer-label">${this._escapeHtml(layer.name.toUpperCase())}</div>`;
            html += `<div class="${c}-layer" style="background: ${layerBg}; border-color: ${borderColor};">`;
            html += `<div class="${c}-layer-row">`;
            
            for (const module of layer.modules) {
                html += this._renderModule(module, containerClass);
            }
            
            html += '</div></div></div>';
            return html;
        }
        
        _renderModule(module, containerClass) {
            const c = containerClass;
            const gridCols = module.grid?.cols || 1;
            const gap = parseInt(module.gap) || this.COMPONENT_GAP;
            const colSpan = module.cols || 12;
            
            let html = `<div class="${c}-module" style="grid-column: span ${colSpan};">`;
            html += `<div class="${c}-module-title">${this._escapeHtml(module.name)}</div>`;
            html += `<div class="${c}-module-content" style="grid-template-columns: repeat(${gridCols}, 1fr); gap: ${gap}px;">`;
            
            for (const comp of module.components) {
                html += this._renderComponent(comp, containerClass);
            }
            
            html += '</div></div>';
            return html;
        }
        
        _renderComponent(component, containerClass) {
            const c = containerClass;
            const colSpan = component.cols || 1;
            const rowSpan = component.rows || 1;
            const gridStyle = `grid-column: span ${colSpan}; grid-row: span ${rowSpan};`;
            
            if (component.stereotype && ['icon', 'folder', 'file', 'db', 'database', 'chart', 'cloud'].includes(component.stereotype)) {
                return this._renderIconComponent(component, containerClass, gridStyle);
            }
            
            return `<div class="${c}-component" style="${gridStyle}">${this._escapeHtml(component.name)}</div>`;
        }
        
        _renderIconComponent(component, containerClass, gridStyle) {
            const c = containerClass;
            const icons = { folder: '📁', file: '📄', db: '🗄️', database: '🗄️', icon: '⚙️', chart: '📊', cloud: '☁️' };
            const icon = icons[component.stereotype] || '📦';
            
            return `<div class="${c}-icon-component" style="${gridStyle}">
                <span class="${c}-icon">${icon}</span>
                <span class="${c}-icon-label">${this._escapeHtml(component.name)}</span>
            </div>`;
        }
        
        _escapeHtml(text) {
            const div = typeof document !== 'undefined' ? document.createElement('div') : null;
            let escaped;
            if (div) {
                div.textContent = text;
                escaped = div.innerHTML;
            } else {
                escaped = text
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#039;');
            }
            // Convert \n (case-insensitive) to <br> for line breaks
            return escaped.replace(/\s*\\n\s*/gi, '<br>');
        }
        
        renderToElement(ast, container, options = {}) {
            container.innerHTML = this.render(ast, options);
        }
    }

    // =========================================================================
    // Public API
    // =========================================================================
    
    function parse(dsl) {
        const parser = new ArchitectureDSLParser();
        return parser.parse(dsl);
    }
    
    function validate(dsl) {
        const parser = new ArchitectureDSLParser();
        return parser.validate(dsl);
    }
    
    function renderHTML(ast, options = {}) {
        const renderer = new ArchitectureHTMLRenderer(options);
        return renderer.render(ast, options);
    }
    
    function renderToHTML(dsl, options = {}) {
        const parser = new ArchitectureDSLParser();
        const ast = parser.parse(dsl);
        
        if (ast.errors.length > 0) {
            console.error('DSL Parse Errors:', ast.errors);
        }
        if (ast.warnings.length > 0) {
            console.warn('DSL Warnings:', ast.warnings);
        }
        
        // Pass the original DSL for the copy button
        const renderOptions = { ...options, originalDsl: dsl };
        
        const renderer = new ArchitectureHTMLRenderer(options);
        const html = renderer.render(ast, renderOptions);
        
        return { html, ast, renderer, errors: ast.errors, warnings: ast.warnings };
    }
    
    function renderToElement(dsl, container, options = {}) {
        const result = renderToHTML(dsl, options);
        container.innerHTML = result.html;
        return result;
    }
    
    /**
     * Copy DSL to clipboard (called by copy button)
     */
    function copyDsl(dslId, btn) {
        const dsl = _dslStore[dslId];
        if (dsl) {
            navigator.clipboard.writeText(dsl).then(() => {
                btn.textContent = '✓';
                setTimeout(() => { btn.textContent = '📋'; }, 1500);
            }).catch(err => {
                console.error('Failed to copy DSL:', err);
            });
        }
    }

    // Export to global
    global.ArchitectureDSL = {
        parse,
        validate,
        renderHTML,
        renderToHTML,
        renderToElement,
        copyDsl,
        ArchitectureDSLParser,
        ArchitectureHTMLRenderer
    };

})(typeof window !== 'undefined' ? window : this);
