# FEATURE-022-D: Technical Design

**Feature ID:** FEATURE-022-D  
**Version:** v1.0  
**Status:** Designed  
**Created:** 01-28-2026  
**Updated:** 01-28-2026 17:15:00

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (JS)                          │
│  ┌─────────────────┐    ┌────────────────────────────────┐  │
│  │  UIUXFeedback   │───▶│  submitFeedback()              │  │
│  │  Manager        │    │  - POST /api/uiux-feedback     │  │
│  │  (entries)      │    │  - Update entry status         │  │
│  └─────────────────┘    │  - Type terminal command       │  │
│                         └────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │ POST JSON
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Flask)                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  uiux_feedback_routes.py                            │    │
│  │  - POST /api/uiux-feedback                          │    │
│  │  - Validate request                                 │    │
│  │  - Call FeedbackService                             │    │
│  └────────────────────────┬────────────────────────────┘    │
│                           │                                  │
│  ┌────────────────────────▼────────────────────────────┐    │
│  │  FeedbackService                                    │    │
│  │  - create_feedback_folder()                         │    │
│  │  - save_feedback_md()                               │    │
│  │  - save_screenshot()                                │    │
│  │  - handle_duplicate_names()                         │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────┘
                               │ File System
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  x-ipe-docs/uiux-feedback/                                  │
│  └── Feedback-20260128-171500/                              │
│      ├── feedback.md                                        │
│      └── page-screenshot.png (optional)                     │
└─────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Backend Route: `uiux_feedback_routes.py`

```python
from flask import Blueprint, request, jsonify
from ..services.uiux_feedback_service import UiuxFeedbackService

uiux_feedback_bp = Blueprint('uiux_feedback', __name__)

@uiux_feedback_bp.route('/api/uiux-feedback', methods=['POST'])
def submit_feedback():
    """Submit UI/UX feedback entry"""
    data = request.get_json()
    
    # Validate required fields
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    required = ['name', 'url', 'elements']
    for field in required:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
    
    # Get project root from config
    from flask import current_app
    project_root = current_app.config.get('PROJECT_ROOT', '.')
    
    # Save feedback
    service = UiuxFeedbackService(project_root)
    result = service.save_feedback(data)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 500
```

### 2. Service: `uiux_feedback_service.py`

```python
import os
import base64
from pathlib import Path
from datetime import datetime

class UiuxFeedbackService:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.feedback_dir = self.project_root / 'x-ipe-docs' / 'uiux-feedback'
    
    def save_feedback(self, data: dict) -> dict:
        """Save feedback entry to file system"""
        try:
            # Get unique folder name
            folder_name = self._get_unique_folder_name(data['name'])
            folder_path = self.feedback_dir / folder_name
            
            # Create folder
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Save feedback.md
            self._save_feedback_md(folder_path, data)
            
            # Save screenshot if present
            if data.get('screenshot'):
                self._save_screenshot(folder_path, data['screenshot'])
            
            return {
                'success': True,
                'folder': str(folder_path.relative_to(self.project_root)),
                'name': folder_name
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_unique_folder_name(self, name: str) -> str:
        """Get unique folder name, appending suffix if needed"""
        base_name = name
        folder_path = self.feedback_dir / base_name
        
        if not folder_path.exists():
            return base_name
        
        # Append suffix
        counter = 1
        while True:
            new_name = f"{base_name}-{counter}"
            if not (self.feedback_dir / new_name).exists():
                return new_name
            counter += 1
    
    def _save_feedback_md(self, folder_path: Path, data: dict) -> None:
        """Generate and save feedback.md"""
        now = datetime.now()
        
        # Build elements list
        elements_md = '\n'.join([f"- `{el}`" for el in data.get('elements', [])])
        
        # Build screenshot section
        screenshot_md = ''
        if data.get('screenshot'):
            screenshot_md = '\n## Screenshot\n\n![Screenshot](./page-screenshot.png)'
        
        # Build feedback section
        feedback_text = data.get('description', '').strip()
        if not feedback_text:
            feedback_text = '_No description provided_'
        
        content = f"""# UI/UX Feedback

**ID:** {data['name']}
**URL:** {data['url']}
**Date:** {now.strftime('%Y-%m-%d %H:%M:%S')}

## Selected Elements

{elements_md}

## Feedback

{feedback_text}
{screenshot_md}
"""
        
        (folder_path / 'feedback.md').write_text(content, encoding='utf-8')
    
    def _save_screenshot(self, folder_path: Path, base64_data: str) -> None:
        """Decode and save screenshot PNG"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # Decode and save
            image_data = base64.b64decode(base64_data)
            (folder_path / 'page-screenshot.png').write_bytes(image_data)
        except Exception as e:
            # Log warning but don't fail
            print(f"Warning: Failed to save screenshot: {e}")
```

### 3. Frontend: Submit Methods in `uiux-feedback.js`

```javascript
/**
 * Submit feedback entry to backend
 */
async _submitEntry(id) {
    const entry = this.feedbackEntries.find(e => e.id === id);
    if (!entry) return;
    
    // Update status
    entry.status = 'submitting';
    this._renderFeedbackPanel();
    
    try {
        const response = await fetch('/api/uiux-feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: entry.name,
                url: entry.url,
                elements: entry.elements,
                screenshot: entry.screenshot,
                description: entry.description
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            entry.status = 'submitted';
            entry.folder = result.folder;
            this._showToast('Feedback saved successfully', 'success');
            this._clearSelections();
            this._typeTerminalCommand(result.folder);
        } else {
            entry.status = 'failed';
            entry.error = result.error;
            this._showToast(`Failed to save: ${result.error}`, 'error');
        }
    } catch (error) {
        entry.status = 'failed';
        entry.error = error.message;
        this._showToast(`Network error: ${error.message}`, 'error');
    }
    
    this._renderFeedbackPanel();
}

/**
 * Type command into terminal (without executing)
 */
_typeTerminalCommand(folderPath) {
    const command = `Get uiux feedback, please visit feedback folder ${folderPath} to get details.`;
    
    // Find active terminal and type command
    const terminal = window.terminalManager?.getActiveTerminal?.();
    if (terminal) {
        terminal.write(command);
    }
}

/**
 * Show toast notification
 */
_showToast(message, type = 'info') {
    // Use existing toast system or create simple one
    if (window.showToast) {
        window.showToast(message, type);
    } else {
        // Simple fallback
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
}
```

### 4. Entry Rendering with Status

```javascript
_renderEntry(entry) {
    const isExpanded = entry.id === this.expandedEntryId;
    const time = this._formatTime(entry.createdAt);
    
    // Status styling
    const statusClass = `status-${entry.status}`;
    const statusIcon = {
        'draft': 'bi-pencil',
        'submitting': 'bi-arrow-repeat spin',
        'submitted': 'bi-check-circle-fill',
        'failed': 'bi-exclamation-circle-fill'
    }[entry.status] || 'bi-pencil';
    
    const statusText = {
        'draft': 'Draft',
        'submitting': 'Submitting...',
        'submitted': 'Submitted',
        'failed': 'Failed'
    }[entry.status] || 'Draft';
    
    // Disable submit button if not draft
    const submitDisabled = entry.status !== 'draft' && entry.status !== 'failed';
    
    return `
        <div class="feedback-entry ${isExpanded ? 'expanded' : ''} ${statusClass}" data-entry-id="${entry.id}">
            <div class="feedback-entry-header">
                <div class="entry-info">
                    <i class="bi bi-chevron-${isExpanded ? 'down' : 'right'} entry-chevron"></i>
                    <span class="entry-name">${entry.name}</span>
                    <span class="entry-status"><i class="bi ${statusIcon}"></i> ${statusText}</span>
                </div>
                <div class="entry-actions">
                    <button class="entry-action-btn delete-entry" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            <div class="feedback-entry-body" style="display: ${isExpanded ? 'block' : 'none'}">
                <!-- ... existing content ... -->
                
                ${entry.status === 'failed' ? `
                    <div class="entry-error">
                        <i class="bi bi-exclamation-triangle"></i>
                        ${entry.error}
                    </div>
                ` : ''}
                
                <div class="entry-actions-footer">
                    <button class="btn-submit" ${submitDisabled ? 'disabled' : ''}>
                        <i class="bi bi-send"></i>
                        ${entry.status === 'submitting' ? 'Submitting...' : 'Submit'}
                    </button>
                </div>
            </div>
        </div>
    `;
}
```

## API Specification

### POST /api/uiux-feedback

**Request:**
```json
{
    "name": "Feedback-20260128-171500",
    "url": "http://localhost:3000/dashboard",
    "elements": [
        "button.submit",
        "div.form-group"
    ],
    "screenshot": "data:image/png;base64,iVBORw0KGgoAAAANSUh...",
    "description": "The submit button is hard to find"
}
```

**Response (Success - 201):**
```json
{
    "success": true,
    "folder": "x-ipe-docs/uiux-feedback/Feedback-20260128-171500",
    "name": "Feedback-20260128-171500"
}
```

**Response (Error - 400):**
```json
{
    "success": false,
    "error": "Missing required field: url"
}
```

**Response (Error - 500):**
```json
{
    "success": false,
    "error": "Permission denied: cannot write to folder"
}
```

## CSS Additions

```css
/* Entry Status Styles */
.entry-status {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 10px;
    margin-left: 8px;
}

.status-draft .entry-status {
    background: #f1f5f9;
    color: #64748b;
}

.status-submitting .entry-status {
    background: #dbeafe;
    color: #3b82f6;
}

.status-submitted .entry-status {
    background: #dcfce7;
    color: #16a34a;
}

.status-failed .entry-status {
    background: #fee2e2;
    color: #dc2626;
}

/* Spin animation for submitting */
.spin {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Entry Error */
.entry-error {
    background: #fef2f2;
    color: #dc2626;
    padding: 8px 12px;
    border-radius: 4px;
    margin-bottom: 12px;
    font-size: 12px;
}

/* Submit Button */
.btn-submit {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background: #10b981;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
}

.btn-submit:hover:not(:disabled) {
    background: #059669;
}

.btn-submit:disabled {
    background: #94a3b8;
    cursor: not-allowed;
}

/* Toast Styles */
.toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 12px 20px;
    border-radius: 8px;
    color: white;
    font-size: 14px;
    z-index: 9999;
    animation: slideIn 0.3s ease;
}

.toast-success { background: #10b981; }
.toast-error { background: #ef4444; }
.toast-info { background: #3b82f6; }

@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
```

## File Structure Changes

```
src/x_ipe/
├── routes/
│   └── uiux_feedback_routes.py  (NEW)
├── services/
│   └── uiux_feedback_service.py  (NEW)
└── static/
    ├── js/
    │   └── uiux-feedback.js  (MODIFIED - add submit methods)
    └── css/
        └── uiux-feedback.css  (MODIFIED - add status styles)
```

## Test Coverage

1. **Service Tests:**
   - `test_save_feedback_creates_folder`
   - `test_save_feedback_md_content`
   - `test_save_screenshot_decodes_base64`
   - `test_unique_folder_name_appends_suffix`
   - `test_save_without_screenshot`
   - `test_save_with_empty_description`

2. **Route Tests:**
   - `test_submit_feedback_success`
   - `test_submit_feedback_missing_required`
   - `test_submit_feedback_invalid_json`
   - `test_submit_feedback_returns_folder_path`

3. **Integration Tests:**
   - `test_full_feedback_flow`
   - `test_duplicate_entry_handling`
