/**
 * FEATURE-030-A: UIUX Reference Tab & Console Integration
 *
 * Manages the UIUX Reference tab in the Workplace idea creation panel.
 * Provides URL input, optional auth prerequisite, extra instructions,
 * and a "Go to Reference" button that auto-types a prompt into the console.
 */
class UiuxReferenceTab {
    constructor(container, config) {
        this.container = container;
        this.config = config || {};
        this.state = 'idle';
        this.authExpanded = false;
        this.resetTimer = null;
    }

    render() {
        this.container.innerHTML = `
            <div class="uiux-ref-pane">
                <!-- URL Input -->
                <div class="uiux-ref-input-group">
                    <label class="uiux-ref-label" for="uiux-ref-url">TARGET PAGE URL</label>
                    <div class="uiux-ref-input-wrapper">
                        <i class="bi bi-globe2 uiux-ref-input-icon"></i>
                        <input type="url" id="uiux-ref-url" class="uiux-ref-input"
                               placeholder="https://example.com/page-to-reference" required>
                    </div>
                </div>

                <!-- Auth Prerequisite (collapsible) -->
                <div class="uiux-ref-auth-section">
                    <button class="uiux-ref-auth-toggle" id="uiux-ref-auth-toggle"
                            type="button" aria-expanded="false">
                        <i class="bi bi-shield-lock"></i>
                        <span>Authentication Prerequisite</span>
                        <span class="uiux-ref-optional">(optional)</span>
                        <i class="bi bi-chevron-right uiux-ref-chevron"></i>
                    </button>
                    <div class="uiux-ref-auth-content" id="uiux-ref-auth-content">
                        <div class="uiux-ref-input-wrapper">
                            <i class="bi bi-key uiux-ref-input-icon"></i>
                            <input type="url" id="uiux-ref-auth-url" class="uiux-ref-input"
                                   placeholder="https://example.com/login">
                        </div>
                        <div class="uiux-ref-auth-hint">
                            <i class="bi bi-info-circle"></i>
                            <span>The agent will open this URL first so you can log in, then redirect to your target page.</span>
                        </div>
                    </div>
                </div>

                <!-- Extra Instructions -->
                <div class="uiux-ref-input-group">
                    <label class="uiux-ref-label" for="uiux-ref-instructions">
                        EXTRA INSTRUCTIONS <span class="uiux-ref-optional">(optional)</span>
                    </label>
                    <textarea id="uiux-ref-instructions" class="uiux-ref-textarea"
                              placeholder="e.g., Focus on the navigation bar and color palette..."
                              maxlength="1000"></textarea>
                    <div class="uiux-ref-char-count"><span id="uiux-ref-char-count-val">0</span>/1000</div>
                </div>

                <!-- Go to Reference Button -->
                <button id="uiux-ref-go-btn" class="uiux-ref-btn" data-state="idle" type="button">
                    <i class="bi bi-box-arrow-up-right uiux-ref-btn-icon"></i>
                    <span class="uiux-ref-btn-text">Go to Reference</span>
                </button>

                <!-- Flow Preview -->
                <div class="uiux-ref-flow-preview">
                    <div class="uiux-ref-flow-step">
                        <i class="bi bi-link-45deg"></i><span>Enter URL</span>
                    </div>
                    <i class="bi bi-arrow-right uiux-ref-flow-arrow"></i>
                    <div class="uiux-ref-flow-step">
                        <i class="bi bi-terminal"></i><span>Console Opens</span>
                    </div>
                    <i class="bi bi-arrow-right uiux-ref-flow-arrow"></i>
                    <div class="uiux-ref-flow-step">
                        <i class="bi bi-cursor"></i><span>Agent Navigates</span>
                    </div>
                    <i class="bi bi-arrow-right uiux-ref-flow-arrow"></i>
                    <div class="uiux-ref-flow-step">
                        <i class="bi bi-hand-index"></i><span>Pick Elements</span>
                    </div>
                </div>
            </div>
        `;
        this._bindEvents();
    }

    _bindEvents() {
        // Auth toggle
        const authToggle = this.container.querySelector('#uiux-ref-auth-toggle');
        if (authToggle) {
            authToggle.addEventListener('click', () => this.toggleAuth());
        }

        // Go to Reference button
        const goBtn = this.container.querySelector('#uiux-ref-go-btn');
        if (goBtn) {
            goBtn.addEventListener('click', () => this.handleGoToReference());
        }

        // Character counter for instructions
        const textarea = this.container.querySelector('#uiux-ref-instructions');
        const counter = this.container.querySelector('#uiux-ref-char-count-val');
        if (textarea && counter) {
            textarea.addEventListener('input', () => {
                counter.textContent = textarea.value.length;
            });
        }

        // URL input focus styling
        const urlInput = this.container.querySelector('#uiux-ref-url');
        if (urlInput) {
            urlInput.addEventListener('input', () => {
                urlInput.classList.remove('uiux-ref-input-error');
            });
        }
    }

    validateForm() {
        const urlInput = this.container.querySelector('#uiux-ref-url');
        const url = urlInput ? urlInput.value.trim() : '';
        if (!url || !/^https?:\/\/.+/.test(url)) {
            if (urlInput) urlInput.classList.add('uiux-ref-input-error');
            return false;
        }
        return true;
    }

    buildPrompt(url, authUrl, instructions) {
        const prompts = this.config.copilotPrompts || [];
        const language = this.config.language || 'en';

        // Find uiux-reference prompt
        const uiuxPrompt = prompts.find(p => p.id === 'uiux-reference');
        let commandTemplate = 'copilot execute uiux-reference --url <target-url>';

        if (uiuxPrompt && uiuxPrompt['prompt-details']) {
            const detail = uiuxPrompt['prompt-details'].find(d => d.language === language)
                        || uiuxPrompt['prompt-details'].find(d => d.language === 'en');
            if (detail && detail.command) {
                commandTemplate = detail.command;
            }
        }

        let command = commandTemplate.replace(/<target-url>/g, url);
        if (authUrl) {
            command += ` --auth-url ${authUrl}`;
        }
        if (instructions) {
            const escaped = instructions.replace(/"/g, '\\"');
            command += ` --extra "${escaped}"`;
        }
        return command;
    }

    handleGoToReference() {
        if (this.state !== 'idle') return;
        if (!this.validateForm()) return;

        const { url, authUrl, instructions } = this.getFormData();
        const prompt = this.buildPrompt(url, authUrl, instructions);

        this.setState('loading');

        if (window.terminalPanel) {
            window.terminalPanel.expand();
        }
        if (window.terminalManager) {
            window.terminalManager.sendCopilotPromptCommand(prompt);
        }

        setTimeout(() => this.setState('success'), 1500);
    }

    setState(newState) {
        if (this.resetTimer) {
            clearTimeout(this.resetTimer);
            this.resetTimer = null;
        }
        this.state = newState;

        const btn = this.container.querySelector('#uiux-ref-go-btn');
        if (!btn) return;

        btn.dataset.state = newState;
        const icon = btn.querySelector('.uiux-ref-btn-icon');
        const text = btn.querySelector('.uiux-ref-btn-text');

        if (newState === 'idle') {
            if (icon) { icon.className = 'bi bi-box-arrow-up-right uiux-ref-btn-icon'; }
            if (text) { text.textContent = 'Go to Reference'; }
        } else if (newState === 'loading') {
            if (icon) { icon.className = 'uiux-ref-spinner uiux-ref-btn-icon'; }
            if (text) { text.textContent = 'Opening console...'; }
        } else if (newState === 'success') {
            if (icon) { icon.className = 'bi bi-check-lg uiux-ref-btn-icon'; }
            if (text) { text.textContent = 'Console ready — press Enter'; }
            this.resetTimer = setTimeout(() => this.setState('idle'), 2500);
        }
    }

    toggleAuth() {
        this.authExpanded = !this.authExpanded;
        const toggle = this.container.querySelector('#uiux-ref-auth-toggle');
        const content = this.container.querySelector('#uiux-ref-auth-content');
        if (toggle) {
            toggle.setAttribute('aria-expanded', this.authExpanded ? 'true' : 'false');
        }
        if (content) {
            if (this.authExpanded) {
                content.classList.add('uiux-ref-auth-expanded');
            } else {
                content.classList.remove('uiux-ref-auth-expanded');
            }
        }
    }

    getFormData() {
        return {
            url: (this.container.querySelector('#uiux-ref-url')?.value || '').trim(),
            authUrl: (this.container.querySelector('#uiux-ref-auth-url')?.value || '').trim(),
            instructions: (this.container.querySelector('#uiux-ref-instructions')?.value || '').trim()
        };
    }

    destroy() {
        if (this.resetTimer) {
            clearTimeout(this.resetTimer);
            this.resetTimer = null;
        }
    }
}
