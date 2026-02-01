/**
 * FEATURE-024: Project Quality Evaluation UI
 * 
 * Quality Evaluation View component for viewing and acting on project quality reports.
 * Integrates with Workplace sidebar and provides action bar, version timeline, and markdown preview.
 */
class QualityEvaluationView {
    constructor(container) {
        this.container = container;
        this.config = null;
        this.status = null;
        this.currentVersion = null;
    }

    // -------------------------------------------------------------------------
    // Lifecycle
    // -------------------------------------------------------------------------

    async init() {
        this.renderLoading();
        try {
            await Promise.all([
                this.loadConfig(),
                this.loadStatus()
            ]);
            
            if (this.status.exists) {
                await this.loadContent();
                this.renderWithData();
            } else {
                this.renderEmptyState();
            }
        } catch (error) {
            console.error('[QualityEval] Init error:', error);
            this.renderError('Failed to load quality evaluation data');
        }
    }

    destroy() {
        this.container.innerHTML = '';
    }

    // -------------------------------------------------------------------------
    // API Methods
    // -------------------------------------------------------------------------

    async loadConfig() {
        try {
            const response = await fetch('/api/config/copilot-prompt');
            if (response.ok) {
                this.config = await response.json();
            } else {
                this.config = this.getDefaultConfig();
            }
        } catch (error) {
            console.warn('[QualityEval] Failed to load config:', error);
            this.config = this.getDefaultConfig();
        }
    }

    async loadStatus() {
        const response = await fetch('/api/quality-evaluation/status');
        if (response.ok) {
            this.status = await response.json();
        } else {
            this.status = { exists: false, versions: [] };
        }
    }

    async loadContent(version = null) {
        const url = version 
            ? `/api/quality-evaluation/content?version=${version}`
            : '/api/quality-evaluation/content';
        
        const response = await fetch(url);
        if (response.ok) {
            const data = await response.json();
            this.currentVersion = data.version;
            this.currentContent = data.content;
            return data;
        }
        throw new Error('Failed to load content');
    }

    getDefaultConfig() {
        return {
            version: '2.0',
            evaluation: {
                evaluate: {
                    label: 'Evaluate Project Quality',
                    icon: 'bi-clipboard-check',
                    command: 'Evaluate project quality and generate report to x-ipe-docs/quality-evaluation/project-quality-evaluation.md'
                },
                refactoring: []
            },
            placeholder: {
                'evaluation-file': 'x-ipe-docs/quality-evaluation/project-quality-evaluation.md'
            }
        };
    }

    // -------------------------------------------------------------------------
    // Rendering
    // -------------------------------------------------------------------------

    renderLoading() {
        this.container.innerHTML = `
            <div class="quality-eval-view">
                <div class="quality-loading">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderError(message) {
        this.container.innerHTML = `
            <div class="quality-eval-view">
                <div class="quality-empty-state">
                    <div class="quality-empty-icon">
                        <i class="bi bi-exclamation-triangle"></i>
                    </div>
                    <h5 class="quality-empty-title">Error</h5>
                    <p class="quality-empty-desc">${message}</p>
                    <button class="btn btn-evaluate" onclick="window.qualityEvaluationView.init()">
                        <i class="bi bi-arrow-clockwise"></i>
                        Retry
                    </button>
                </div>
            </div>
        `;
    }

    renderEmptyState() {
        const evaluateConfig = this.config?.evaluation?.evaluate || this.getDefaultConfig().evaluation.evaluate;
        
        this.container.innerHTML = `
            <div class="quality-eval-view">
                <div class="quality-empty-state">
                    <div class="quality-empty-icon">
                        <i class="bi bi-clipboard-check"></i>
                    </div>
                    <h5 class="quality-empty-title">No Evaluation Yet</h5>
                    <p class="quality-empty-desc">
                        Run your first project quality evaluation to get insights on requirements coverage,
                        feature alignment, and test completeness.
                    </p>
                    <button class="btn btn-evaluate" id="quality-empty-cta">
                        <i class="bi ${evaluateConfig.icon}"></i>
                        ${evaluateConfig.label}
                    </button>
                </div>
            </div>
        `;
        
        this.bindEmptyStateEvents();
    }

    renderWithData() {
        this.container.innerHTML = `
            <div class="quality-eval-view">
                ${this.renderActionBar()}
                ${this.renderVersionTimeline()}
                <div class="quality-markdown-preview">
                    <div class="quality-markdown-content" id="quality-markdown-content">
                        ${this.renderMarkdown(this.currentContent)}
                    </div>
                </div>
            </div>
        `;
        
        this.bindEvents();
    }

    renderActionBar() {
        const evaluateConfig = this.config?.evaluation?.evaluate || this.getDefaultConfig().evaluation.evaluate;
        const refactoringOptions = this.config?.evaluation?.refactoring || [];
        
        return `
            <div class="quality-action-bar">
                ${refactoringOptions.length > 0 ? this.renderRefactoringDropdown(refactoringOptions) : ''}
                <button class="btn btn-evaluate" id="quality-evaluate-btn">
                    <i class="bi ${evaluateConfig.icon}"></i>
                    Evaluate
                </button>
            </div>
        `;
    }

    renderRefactoringDropdown(options) {
        const items = options.map(opt => `
            <div class="dropdown-item" data-command="${this.escapeHtml(opt.command)}">
                <i class="bi ${opt.icon}"></i>
                <span>${this.escapeHtml(opt.label)}</span>
            </div>
        `).join('');
        
        return `
            <div class="dropdown-refactoring">
                <button class="btn btn-refactoring">
                    <i class="bi bi-arrow-repeat"></i>
                    Refactoring
                    <i class="bi bi-chevron-down" style="font-size: 0.75rem;"></i>
                </button>
                <div class="dropdown-menu">
                    ${items}
                </div>
            </div>
        `;
    }

    renderVersionTimeline() {
        if (!this.status.versions || this.status.versions.length === 0) {
            return '';
        }
        
        const tabs = this.status.versions.map(v => `
            <div class="quality-version-tab ${v.version === this.currentVersion ? 'active' : ''}" 
                 data-version="${v.version}">
                <span class="version-number">${v.version}</span>
                <span class="version-date">${v.date}</span>
            </div>
        `).join('');
        
        return `
            <div class="quality-version-timeline">
                ${tabs}
            </div>
        `;
    }

    renderMarkdown(content) {
        if (!content) {
            return '<p class="text-muted">No content available.</p>';
        }
        
        // Use marked.js if available, otherwise basic conversion
        if (typeof marked !== 'undefined') {
            return marked.parse(content);
        }
        
        // Basic markdown conversion fallback
        return this.basicMarkdownToHtml(content);
    }

    basicMarkdownToHtml(content) {
        let html = content
            // Headers
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            // Bold and italic
            .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Inline code
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // Lists
            .replace(/^\- (.*$)/gm, '<li>$1</li>')
            .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
            // Paragraphs
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
        
        return `<p>${html}</p>`;
    }

    // -------------------------------------------------------------------------
    // Event Handling
    // -------------------------------------------------------------------------

    bindEmptyStateEvents() {
        const ctaBtn = document.getElementById('quality-empty-cta');
        if (ctaBtn) {
            ctaBtn.addEventListener('click', () => this.handleEvaluateClick());
        }
    }

    bindEvents() {
        // Evaluate button
        const evaluateBtn = document.getElementById('quality-evaluate-btn');
        if (evaluateBtn) {
            evaluateBtn.addEventListener('click', () => this.handleEvaluateClick());
        }
        
        // Refactoring dropdown items
        const refactoringItems = this.container.querySelectorAll('.dropdown-item[data-command]');
        refactoringItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const command = e.currentTarget.dataset.command;
                this.handleRefactoringClick(command);
            });
        });
        
        // Version tabs
        const versionTabs = this.container.querySelectorAll('.quality-version-tab');
        versionTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const version = e.currentTarget.dataset.version;
                this.handleVersionClick(version);
            });
        });
    }

    handleEvaluateClick() {
        const evaluateConfig = this.config?.evaluation?.evaluate || this.getDefaultConfig().evaluation.evaluate;
        const command = this.replacePlaceholders(evaluateConfig.command);
        this.sendToConsole(command);
    }

    handleRefactoringClick(command) {
        const resolvedCommand = this.replacePlaceholders(command);
        this.sendToConsole(resolvedCommand);
    }

    async handleVersionClick(version) {
        if (version === this.currentVersion) return;
        
        try {
            await this.loadContent(version);
            
            // Update active tab
            const tabs = this.container.querySelectorAll('.quality-version-tab');
            tabs.forEach(tab => {
                tab.classList.toggle('active', tab.dataset.version === version);
            });
            
            // Update content
            const contentEl = document.getElementById('quality-markdown-content');
            if (contentEl) {
                contentEl.innerHTML = this.renderMarkdown(this.currentContent);
            }
        } catch (error) {
            console.error('[QualityEval] Failed to load version:', error);
        }
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    replacePlaceholders(command) {
        if (!command) return command;
        
        const placeholders = this.config?.placeholder || {};
        let result = command;
        
        // Replace known placeholders
        if (placeholders['evaluation-file']) {
            result = result.replace(/<evaluation-file>/g, placeholders['evaluation-file']);
        }
        
        return result;
    }

    sendToConsole(command) {
        // Try to use the global terminal/console if available
        if (window.terminal && typeof window.terminal.sendCommand === 'function') {
            window.terminal.sendCommand(command);
        } else if (window.consolePopup && typeof window.consolePopup.show === 'function') {
            window.consolePopup.show(command);
        } else {
            // Fallback: copy to clipboard and show alert
            navigator.clipboard.writeText(command).then(() => {
                console.log('[QualityEval] Command copied to clipboard:', command);
                alert(`Command copied to clipboard:\n${command}`);
            }).catch(() => {
                console.log('[QualityEval] Command:', command);
                alert(`Copy this command to console:\n${command}`);
            });
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Export for global access
window.QualityEvaluationView = QualityEvaluationView;
