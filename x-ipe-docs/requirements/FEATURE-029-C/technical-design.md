# FEATURE-029-C: Session Hover Preview — Technical Design

## Part 1: Architecture Overview

### Approach

Add hover preview capability to SessionExplorer by:
1. Adding mouseenter/mouseleave handlers on each session bar
2. Creating a reusable preview container with a read-only xterm.js Terminal
3. Populating preview from source session's buffer + live socket output
4. Managing hover state with timers for 500ms delay and 100ms grace period

### Key Design Decisions

- **Single reusable preview container**: One DOM element + one xterm.js Terminal, reused across hovers (avoids repeated creation/disposal overhead)
- **Buffer copy approach**: Read source terminal's buffer line-by-line via `buffer.active.getLine(i).translateToString()` — no backend changes needed
- **Live updates via socket listener**: Add temporary `output` listener to source session's socket; remove on dismiss
- **Grace period**: 100ms timeout on mouseleave before dismissing — cancelled if cursor re-enters bar or preview

### Component Interaction

```
SessionExplorer
  ├── addSessionBar()      ← add mouseenter/mouseleave handlers
  ├── _showPreview(key)    ← create/populate preview terminal
  ├── _dismissPreview()    ← clean up preview terminal + listeners
  ├── _previewContainer    ← reusable DOM element
  ├── _previewTerminal     ← reusable xterm.js Terminal
  ├── _previewKey          ← currently previewed session key
  ├── _hoverTimer          ← 500ms delay timer
  └── _graceTimer          ← 100ms grace period timer
```

## Part 2: Implementation Steps

### Step 1: Add preview state properties to SessionExplorer constructor

After `this.manager = terminalManager;`, add:

```javascript
this._previewContainer = null;  // DOM element
this._previewTerminal = null;   // xterm.js Terminal
this._previewFitAddon = null;   // FitAddon for preview
this._previewKey = null;        // currently previewed session key
this._hoverTimer = null;        // 500ms delay
this._graceTimer = null;        // 100ms grace period
this._previewOutputHandler = null; // socket output listener ref
```

### Step 2: Add mouseenter/mouseleave handlers in addSessionBar()

After the click listener on the bar element, add:

```javascript
bar.addEventListener('mouseenter', () => {
    // Skip active session
    if (bar.dataset.active === 'true') return;
    clearTimeout(this._graceTimer);
    this._hoverTimer = setTimeout(() => this._showPreview(key, bar), 500);
});
bar.addEventListener('mouseleave', () => {
    clearTimeout(this._hoverTimer);
    this._graceTimer = setTimeout(() => this._dismissPreview(), 100);
});
```

### Step 3: Create _initPreviewContainer() method

Creates the reusable preview DOM structure once:

```javascript
_initPreviewContainer() {
    if (this._previewContainer) return;

    this._previewContainer = document.createElement('div');
    this._previewContainer.className = 'session-preview';
    this._previewContainer.style.display = 'none';

    const header = document.createElement('div');
    header.className = 'session-preview-header';
    this._previewContainer.appendChild(header);

    const body = document.createElement('div');
    body.className = 'session-preview-body';
    this._previewContainer.appendChild(body);

    // Grace period: re-entering preview cancels dismiss
    this._previewContainer.addEventListener('mouseenter', () => {
        clearTimeout(this._graceTimer);
    });
    this._previewContainer.addEventListener('mouseleave', () => {
        this._graceTimer = setTimeout(() => this._dismissPreview(), 100);
    });

    // Click to switch session
    this._previewContainer.addEventListener('click', () => {
        if (this._previewKey) {
            const key = this._previewKey;
            this._dismissPreview();
            this.manager.switchSession(key);
        }
    });

    // Append to terminal panel (position: relative parent)
    document.getElementById('terminal-panel').appendChild(this._previewContainer);

    // Create reusable xterm.js Terminal
    this._previewTerminal = new Terminal({
        disableStdin: true,
        scrollback: 500,
        fontSize: 12,
        fontFamily: terminalConfig.fontFamily,
        theme: terminalConfig.theme,
        cursorBlink: false
    });
    this._previewFitAddon = new FitAddon();
    this._previewTerminal.loadAddon(this._previewFitAddon);
    this._previewTerminal.open(body);
}
```

### Step 4: Create _showPreview(key, barElement) method

Populates and shows the preview:

```javascript
_showPreview(key, barElement) {
    const session = this.manager.sessions.get(key);
    if (!session) return;

    this._initPreviewContainer();

    // Dismiss any existing preview
    if (this._previewKey && this._previewKey !== key) {
        this._cleanupPreviewListeners();
    }
    this._previewKey = key;

    // Update header
    this._previewContainer.querySelector('.session-preview-header').textContent = session.name;

    // Clear previous content
    this._previewTerminal.clear();

    // Copy buffer from source terminal
    const srcBuffer = session.terminal.buffer.active;
    const lines = [];
    for (let i = 0; i < srcBuffer.length; i++) {
        const line = srcBuffer.getLine(i);
        if (line) lines.push(line.translateToString(true));
    }
    if (lines.length > 0) {
        this._previewTerminal.write(lines.join('\r\n'));
    }
    this._previewTerminal.scrollToBottom();

    // Add live output listener
    if (session.socket) {
        this._previewOutputHandler = (data) => {
            if (this._previewKey === key) {
                this._previewTerminal.write(data);
                this._previewTerminal.scrollToBottom();
            }
        };
        session.socket.on('output', this._previewOutputHandler);
    }

    // Position and show
    this._previewContainer.style.display = 'flex';
    try { this._previewFitAddon.fit(); } catch(e) {}
}
```

### Step 5: Create _dismissPreview() method

```javascript
_dismissPreview() {
    clearTimeout(this._hoverTimer);
    clearTimeout(this._graceTimer);
    this._cleanupPreviewListeners();
    this._previewKey = null;
    if (this._previewContainer) {
        this._previewContainer.style.display = 'none';
    }
}

_cleanupPreviewListeners() {
    if (this._previewOutputHandler && this._previewKey) {
        const session = this.manager.sessions.get(this._previewKey);
        if (session && session.socket) {
            session.socket.off('output', this._previewOutputHandler);
        }
        this._previewOutputHandler = null;
    }
}
```

### Step 6: Update removeSessionBar() to dismiss preview if needed

In the existing `removeSessionBar(key)` method, before removing the bar:

```javascript
if (this._previewKey === key) this._dismissPreview();
```

### Step 7: Add CSS styles to terminal.css

After the FEATURE-029-B section:

```css
/* FEATURE-029-C: Session Hover Preview */
.session-preview {
    position: absolute;
    right: 181px; /* explorer width (180px) + 1px */
    top: 40px;    /* below header */
    width: 50%;
    height: 60%;
    background: #1e1e1e;
    border: 1px solid #4ec9b0;
    border-radius: 4px;
    display: none;
    flex-direction: column;
    z-index: 50;
    box-shadow: -4px 4px 12px rgba(0,0,0,0.5);
    cursor: pointer;
}
.session-preview-header {
    padding: 4px 8px;
    font-size: 12px;
    color: #4ec9b0;
    border-bottom: 1px solid #333;
    flex-shrink: 0;
}
.session-preview-body {
    flex: 1;
    overflow: hidden;
}
```
