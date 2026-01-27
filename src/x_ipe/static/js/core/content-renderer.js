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
    /**
     * Parse and render Architecture DSL to HTML using the bundled library
     */
    _parseAndRenderArchitectureDSL(dsl) {
        if (typeof ArchitectureDSL !== 'undefined') {
            return ArchitectureDSL.renderToHTML(dsl);
        }
        // Fallback if library not loaded
        console.warn('ArchitectureDSL library not loaded');
        return { 
            html: '<div class="alert alert-warning">Architecture DSL library not loaded</div>', 
            ast: { type: 'document', title: null, layers: [], errors: [], warnings: [] },
            errors: [{ message: 'Library not loaded' }], 
            warnings: [] 
        };
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
