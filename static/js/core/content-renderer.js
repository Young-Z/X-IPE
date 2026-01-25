/**
 * Content Renderer
 * FEATURE-002: Content Viewer
 * 
 * Handles loading and rendering file content (markdown, code, etc.)
 * with syntax highlighting, Mermaid diagrams, Infographic DSL, and Architecture DSL.
 */
class ContentRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentPath = null;
        this.initMermaid();
        this.initMarked();
        this.initArchitectureDSL();
    }
    
    /**
     * Initialize Mermaid.js configuration
     */
    initMermaid() {
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                startOnLoad: false,
                theme: 'default',
                securityLevel: 'loose'
            });
        }
    }
    
    /**
     * Initialize Marked.js configuration with highlight.js
     */
    initMarked() {
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (e) {
                            console.error('Highlight error:', e);
                        }
                    }
                    return code;
                },
                breaks: true,
                gfm: true
            });
        }
    }
    
    /**
     * Initialize Architecture DSL renderer
     */
    initArchitectureDSL() {
        // Architecture DSL parser and renderer will be loaded inline
        this._architectureDSLReady = true;
    }
    
    /**
     * Load and render file content
     */
    async load(path) {
        if (!path) return;
        
        this.currentPath = path;
        this.showLoading();
        
        try {
            const response = await fetch(`/api/file/content?path=${encodeURIComponent(path)}`);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `HTTP error ${response.status}`);
            }
            
            const data = await response.json();
            this.render(data);
        } catch (error) {
            console.error('Failed to load file:', error);
            this.showError(error.message);
        }
    }
    
    /**
     * Render content based on file type
     */
    render(data) {
        const { content, type, path, extension } = data;
        
        if (type === 'markdown') {
            this.renderMarkdown(content);
        } else if (type === 'html') {
            this.renderHtml(content);
        } else {
            this.renderCode(content, type);
        }
    }
    
    /**
     * Render markdown content with Mermaid diagrams, Infographic DSL, and Architecture DSL
     */
    renderMarkdown(content) {
        // Pre-process Mermaid blocks
        const mermaidBlocks = [];
        let processedContent = content.replace(
            /```mermaid\n([\s\S]*?)```/g,
            (match, diagram, offset) => {
                const id = `mermaid-${mermaidBlocks.length}`;
                mermaidBlocks.push({ id, diagram: diagram.trim() });
                return `<div class="mermaid" id="${id}"></div>`;
            }
        );
        
        // Pre-process Infographic blocks
        const infographicBlocks = [];
        processedContent = processedContent.replace(
            /```infographic\n([\s\S]*?)```/g,
            (match, syntax) => {
                const id = `infographic-${infographicBlocks.length}`;
                infographicBlocks.push({ id, syntax: syntax.trim() });
                return `<div class="infographic-container" id="${id}" style="min-height: 200px; width: 100%; margin: 1rem 0;"></div>`;
            }
        );
        
        // Pre-process Architecture DSL blocks (architecture-dsl or arch-dsl)
        const architectureBlocks = [];
        processedContent = processedContent.replace(
            /```(?:architecture-dsl|arch-dsl|architecture)\n([\s\S]*?)```/g,
            (match, dsl) => {
                const id = `architecture-${architectureBlocks.length}`;
                architectureBlocks.push({ id, dsl: dsl.trim() });
                return `<div class="architecture-diagram-container" id="${id}" style="min-height: 200px; width: 100%; margin: 1rem 0; overflow: auto;"></div>`;
            }
        );
        
        // Parse markdown
        let html;
        if (typeof marked !== 'undefined') {
            html = marked.parse(processedContent);
        } else {
            // Fallback: escape HTML and preserve whitespace
            html = '<pre>' + this.escapeHtml(content) + '</pre>';
        }
        
        // Wrap in markdown-body container
        this.container.innerHTML = `<div class="markdown-body">${html}</div>`;
        
        // Render Mermaid diagrams
        this.renderMermaidDiagrams(mermaidBlocks);
        
        // Render Infographic diagrams
        this.renderInfographicDiagrams(infographicBlocks);
        
        // Render Architecture DSL diagrams
        this.renderArchitectureDiagrams(architectureBlocks);
        
        // Apply syntax highlighting to code blocks
        this.highlightCodeBlocks();
    }
    
    /**
     * Render HTML content in an iframe for preview
     */
    renderHtml(content) {
        // Create a blob URL for the HTML content
        const blob = new Blob([content], { type: 'text/html' });
        const blobUrl = URL.createObjectURL(blob);
        
        // Store for cleanup
        if (this._htmlBlobUrl) {
            URL.revokeObjectURL(this._htmlBlobUrl);
        }
        this._htmlBlobUrl = blobUrl;
        
        this.container.innerHTML = `
            <div class="html-preview">
                <div class="html-preview-toolbar">
                    <span class="badge bg-success"><i class="bi bi-eye"></i> HTML Preview</span>
                </div>
                <iframe class="html-preview-iframe" src="${blobUrl}" sandbox="allow-scripts allow-same-origin"></iframe>
            </div>
        `;
    }
    
    /**
     * Render Mermaid diagrams
     */
    async renderMermaidDiagrams(blocks) {
        if (typeof mermaid === 'undefined' || blocks.length === 0) return;
        
        for (const block of blocks) {
            const element = document.getElementById(block.id);
            if (element) {
                try {
                    const { svg } = await mermaid.render(block.id + '-svg', block.diagram);
                    element.innerHTML = svg;
                } catch (error) {
                    console.error('Mermaid render error:', error);
                    element.innerHTML = `<div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i>
                        Diagram rendering error: ${error.message}
                    </div>`;
                }
            }
        }
    }
    
    /**
     * Render Infographic DSL diagrams using AntV Infographic
     */
    async renderInfographicDiagrams(blocks) {
        if (typeof AntVInfographic === 'undefined' || blocks.length === 0) return;
        
        for (const block of blocks) {
            const element = document.getElementById(block.id);
            if (element) {
                try {
                    const infographic = new AntVInfographic.Infographic({
                        container: `#${block.id}`,
                        width: '100%',
                        height: '100%',
                    });
                    infographic.render(block.syntax);
                    // Re-render after fonts load for better display
                    if (document.fonts?.ready) {
                        document.fonts.ready.then(() => {
                            infographic.render(block.syntax);
                        }).catch(e => console.warn('Font loading error:', e));
                    }
                } catch (error) {
                    console.error('Infographic render error:', error);
                    element.innerHTML = `<div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i>
                        Infographic rendering error: ${error.message}
                    </div>`;
                }
            }
        }
    }
    
    /**
     * Render Architecture DSL diagrams
     */
    async renderArchitectureDiagrams(blocks) {
        if (blocks.length === 0) return;
        
        for (const block of blocks) {
            const element = document.getElementById(block.id);
            if (element) {
                try {
                    const result = this._parseAndRenderArchitectureDSL(block.dsl);
                    element.innerHTML = result.html;
                    
                    if (result.errors && result.errors.length > 0) {
                        console.warn('Architecture DSL warnings:', result.errors);
                    }
                } catch (error) {
                    console.error('Architecture DSL render error:', error);
                    element.innerHTML = `<div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i>
                        Architecture diagram rendering error: ${error.message}
                    </div>`;
                }
            }
        }
    }
    
    /**
     * Parse and render Architecture DSL to HTML
     * Inline implementation to avoid external module loading issues
     */
    _parseAndRenderArchitectureDSL(dsl) {
        // Parse DSL
        const ast = this._parseArchitectureDSL(dsl);
        
        // Render to HTML
        const html = this._renderArchitectureHTML(ast);
        
        return { html, ast, errors: ast.errors, warnings: ast.warnings };
    }
    
    /**
     * Parse Architecture DSL into AST
     */
    _parseArchitectureDSL(dsl) {
        const errors = [];
        const warnings = [];
        const lines = dsl.split('\n');
        
        const ast = {
            type: 'document',
            viewType: null,
            title: null,
            theme: 'theme-default',
            direction: 'top-to-bottom',
            grid: { cols: 12, rows: 6 },
            textAlign: 'left',
            layers: [],
            errors,
            warnings
        };

        let currentLayer = null;
        let currentModule = null;
        let inMultiLineComment = false;

        for (const rawLine of lines) {
            let line = rawLine.trim();

            if (inMultiLineComment) {
                if (line.includes("'/")) inMultiLineComment = false;
                continue;
            }
            if (line.startsWith("/'")) { inMultiLineComment = true; continue; }
            if (line.startsWith("'") || line === '') continue;

            const commentIdx = line.indexOf("'");
            if (commentIdx > 0) line = line.substring(0, commentIdx).trim();

            if (line.startsWith('@startuml')) {
                const match = line.match(/@startuml\s+(module-view|landscape-view)/);
                if (match) ast.viewType = match[1];
                continue;
            }
            if (line === '@enduml') continue;
            if (line.startsWith('title ')) {
                const match = line.match(/title\s+"([^"]+)"/);
                if (match) ast.title = match[1];
                continue;
            }
            if (line.startsWith('theme ')) {
                const match = line.match(/theme\s+"([^"]+)"/);
                if (match) ast.theme = match[1];
                continue;
            }
            if (line.startsWith('direction ')) {
                const match = line.match(/direction\s+(top-to-bottom|left-to-right)/);
                if (match) ast.direction = match[1];
                continue;
            }
            if (line.startsWith('grid ') && !currentModule) {
                const match = line.match(/grid\s+(\d+)\s*x\s*(\d+)/);
                if (match) ast.grid = { cols: parseInt(match[1]), rows: parseInt(match[2]) };
                continue;
            }
            if (line.startsWith('layer ')) {
                const match = line.match(/layer\s+"([^"]+)"(?:\s+as\s+(\w+))?\s*\{?/);
                if (match) {
                    currentLayer = {
                        type: 'layer', name: match[1], alias: match[2] || null,
                        rows: 1, color: null, borderColor: null,
                        textAlign: ast.textAlign, modules: []
                    };
                    ast.layers.push(currentLayer);
                }
                continue;
            }
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
                if (line.startsWith('module ')) {
                    const match = line.match(/module\s+"([^"]+)"(?:\s+as\s+(\w+))?\s*\{?/);
                    if (match) {
                        currentModule = {
                            type: 'module', name: match[1], alias: match[2] || null,
                            cols: 12, rows: 1, grid: { cols: 1, rows: 1 },
                            align: { h: 'center', v: 'center' }, gap: '8px',
                            color: null, textAlign: currentLayer.textAlign, components: []
                        };
                        currentLayer.modules.push(currentModule);
                    }
                    continue;
                }
                if (line === '}') { currentLayer = null; continue; }
            }
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
                    if (match) currentModule.grid = { cols: parseInt(match[1]), rows: parseInt(match[2]) };
                    continue;
                }
                if (line.startsWith('gap ')) {
                    const match = line.match(/gap\s+(\d+(?:px|rem))/);
                    if (match) currentModule.gap = match[1];
                    continue;
                }
                if (line.startsWith('component ')) {
                    const match = line.match(/component\s+"([^"]+)"(?:\s*\{\s*cols\s+(\d+)(?:\s*,\s*rows\s+(\d+))?\s*\})?(?:\s*<<(\w+)>>)?/);
                    if (match) {
                        currentModule.components.push({
                            type: 'component', name: match[1],
                            cols: match[2] ? parseInt(match[2]) : 1,
                            rows: match[3] ? parseInt(match[3]) : 1,
                            stereotype: match[4] || null
                        });
                    }
                    continue;
                }
                if (line === '}') { currentModule = null; continue; }
            }
        }
        return ast;
    }
    
    /**
     * Render Architecture AST to HTML
     */
    _renderArchitectureHTML(ast) {
        const c = 'arch-diagram';
        const layerColorPatterns = [
            { patterns: ['presentation', 'ui', 'frontend', 'view'], bg: '#fce7f3', border: '#ec4899' },
            { patterns: ['service', 'api', 'gateway'], bg: '#fef3c7', border: '#f97316' },
            { patterns: ['business', 'domain', 'logic', 'core'], bg: '#dbeafe', border: '#3b82f6' },
            { patterns: ['data', 'persistence', 'storage', 'db'], bg: '#dcfce7', border: '#22c55e' },
            { patterns: ['infrastructure', 'infra', 'platform'], bg: '#f3e8ff', border: '#a855f7' }
        ];
        
        const detectColors = (name) => {
            const nameLower = name.toLowerCase();
            for (const p of layerColorPatterns) {
                if (p.patterns.some(pat => nameLower.includes(pat))) {
                    return { bg: p.bg, border: p.border };
                }
            }
            return { bg: '#ffffff', border: '#374151' };
        };
        
        const escapeHtml = (text) => {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        };
        
        // Styles
        let html = `<style>
            .${c} { font-family: 'Inter', system-ui, sans-serif; max-width: 1200px; margin: 0 auto; }
            .${c}-title { font-size: 22px; font-weight: 700; color: #374151; text-align: center; margin-bottom: 20px; }
            .${c}-content { display: flex; flex-direction: column; gap: 16px; }
            .${c}-layer-wrapper { display: flex; gap: 0; border-radius: 8px; transition: transform 0.3s, box-shadow 0.3s; }
            .${c}-layer-wrapper:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1); }
            .${c}-layer-label { writing-mode: vertical-rl; text-orientation: mixed; transform: rotate(180deg); background: #1f2937; padding: 16px 8px; font-size: 12px; font-weight: 600; color: #fff; display: flex; align-items: center; justify-content: center; border-radius: 0 8px 8px 0; min-width: 36px; transition: background 0.2s, min-width 0.2s; }
            .${c}-layer-wrapper:hover .${c}-layer-label { background: #6366f1; min-width: 40px; }
            .${c}-layer-wrapper:hover .${c}-layer { border-color: #6366f1; }
            .${c}-layer { flex: 1; padding: 20px; border: 2px solid; border-left: none; border-radius: 0 8px 8px 0; transition: border-color 0.2s; }
            .${c}-layer-row { display: grid; grid-template-columns: repeat(12, 1fr); gap: 14px; }
            .${c}-module { background: #fff; border: 1.5px dashed #d1d5db; border-radius: 8px; padding: 14px; display: flex; flex-direction: column; gap: 12px; transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s; }
            .${c}-module:hover { border-color: #3b82f6; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); transform: scale(1.01); }
            .${c}-module-title { font-size: 14px; font-weight: 700; color: #374151; }
            .${c}-module-content { display: grid; gap: 10px; }
            .${c}-component { background: #1f2937; color: #fff; border-radius: 18px; padding: 8px 16px; font-size: 12px; font-weight: 500; text-align: center; display: flex; align-items: center; justify-content: center; min-height: 36px; transition: all 0.2s; cursor: default; }
            .${c}-component:hover { background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%); transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
            .${c}-icon-component { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 8px; min-height: 60px; transition: transform 0.2s; cursor: default; }
            .${c}-icon-component:hover { transform: scale(1.1); }
            .${c}-icon { font-size: 28px; }
            .${c}-icon-label { font-size: 11px; color: #6b7280; }
        </style>`;
        
        html += `<div class="${c}">`;
        
        if (ast.title) {
            html += `<div class="${c}-title">${escapeHtml(ast.title)}</div>`;
        }
        
        html += `<div class="${c}-content">`;
        
        for (const layer of ast.layers) {
            const colors = layer.color ? { bg: layer.color, border: layer.borderColor || '#374151' } : detectColors(layer.name);
            
            html += `<div class="${c}-layer-wrapper">`;
            html += `<div class="${c}-layer-label">${escapeHtml(layer.name.toUpperCase())}</div>`;
            html += `<div class="${c}-layer" style="background: ${colors.bg}; border-color: ${colors.border};">`;
            html += `<div class="${c}-layer-row">`;
            
            for (const module of layer.modules) {
                const gridCols = module.grid?.cols || 1;
                const gap = parseInt(module.gap) || 10;
                
                html += `<div class="${c}-module" style="grid-column: span ${module.cols || 12};">`;
                html += `<div class="${c}-module-title">${escapeHtml(module.name)}</div>`;
                html += `<div class="${c}-module-content" style="grid-template-columns: repeat(${gridCols}, 1fr); gap: ${gap}px;">`;
                
                for (const comp of module.components) {
                    const gridStyle = `grid-column: span ${comp.cols || 1}; grid-row: span ${comp.rows || 1};`;
                    
                    if (comp.stereotype && ['icon', 'folder', 'file', 'db'].includes(comp.stereotype)) {
                        const icons = { folder: '📁', file: '📄', db: '🗄️', icon: '⚙️' };
                        html += `<div class="${c}-icon-component" style="${gridStyle}"><span class="${c}-icon">${icons[comp.stereotype] || '📦'}</span><span class="${c}-icon-label">${escapeHtml(comp.name)}</span></div>`;
                    } else {
                        html += `<div class="${c}-component" style="${gridStyle}">${escapeHtml(comp.name)}</div>`;
                    }
                }
                
                html += '</div></div>';
            }
            
            html += '</div></div></div>';
        }
        
        html += '</div></div>';
        
        return html;
    }
    
    /**
     * Apply syntax highlighting to code blocks
     */
    highlightCodeBlocks() {
        if (typeof hljs === 'undefined') return;
        
        this.container.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });
    }
    
    /**
     * Render code with syntax highlighting
     */
    renderCode(content, type) {
        let highlighted = this.escapeHtml(content);
        
        if (typeof hljs !== 'undefined') {
            try {
                if (type !== 'text' && hljs.getLanguage(type)) {
                    highlighted = hljs.highlight(content, { language: type }).value;
                } else {
                    highlighted = hljs.highlightAuto(content).value;
                }
            } catch (e) {
                console.error('Highlight error:', e);
            }
        }
        
        this.container.innerHTML = `
            <div class="code-viewer">
                <pre><code class="language-${type}">${highlighted}</code></pre>
            </div>
        `;
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        this.container.innerHTML = `
            <div class="content-loading">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.container.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                <strong>Error:</strong> ${this.escapeHtml(message)}
            </div>
        `;
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
