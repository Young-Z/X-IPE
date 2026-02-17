# Technical Design: FEATURE-009 - File Change Indicator

> Version: v1.0  
> Created: 01-22-2026  
> Last Updated: 01-22-2026

## Overview

Extend the existing `ProjectSidebar` class to track and display visual indicators (yellow dots) for files and folders that have changed since last viewed.

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     ProjectSidebar                           │
├─────────────────────────────────────────────────────────────┤
│  Existing:                                                   │
│  - sections[]           : Project structure data             │
│  - lastStructureHash    : Hash for change detection          │
│  - _checkForChanges()   : 5s polling method                  │
│                                                              │
│  New:                                                        │
│  - changedPaths         : Set<string> of changed paths       │
│  - _detectChangedPaths(): Extract specific changed paths     │
│  - _addChangedPath()    : Add path + bubble to parents       │
│  - _clearChangedPath()  : Remove path + cleanup parents      │
│  - _hasChangedChildren(): Check if folder has changes        │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Structures

### Changed Paths Set
```javascript
// In-memory tracking (cleared on page refresh)
this.changedPaths = new Set();

// Example state after x-ipe-docs/planning/features.md changes:
changedPaths = Set {
  "x-ipe-docs/planning/features.md",  // The file
  "x-ipe-docs/planning",               // Parent folder
  "docs"                         // Grandparent folder
}
```

### Path Operations
```javascript
// Extract parent paths
getParentPaths("x-ipe-docs/planning/features.md")
→ ["x-ipe-docs/planning", "docs"]

// Normalize paths (remove trailing slashes, handle edge cases)
normalizePath("x-ipe-docs/planning/") → "x-ipe-docs/planning"
```

---

## Implementation Details

### 1. Extend Constructor

```javascript
class ProjectSidebar {
    constructor(containerId) {
        // ... existing code ...
        
        // NEW: Track changed paths
        this.changedPaths = new Set();
        this.previousPaths = new Set();  // For comparison
    }
}
```

### 2. Modify `_checkForChanges()`

```javascript
async _checkForChanges() {
    try {
        const response = await fetch('/api/project/structure');
        if (!response.ok) return;
        
        const data = await response.json();
        const newHash = this._hashStructure(data.sections);
        
        // First load - initialize
        if (this.lastStructureHash === null) {
            this.lastStructureHash = newHash;
            this.previousPaths = this._extractAllPaths(data.sections);
            return;
        }
        
        // Check if structure changed
        if (this.lastStructureHash !== newHash) {
            console.log('[ProjectSidebar] Structure changed, detecting paths...');
            
            // NEW: Detect which paths changed
            const currentPaths = this._extractAllPaths(data.sections);
            this._detectChangedPaths(this.previousPaths, currentPaths);
            
            this.lastStructureHash = newHash;
            this.previousPaths = currentPaths;
            this.sections = data.sections;
            this.render();
            this.showToast('File structure updated', 'info');
        }
    } catch (error) {
        console.error('[ProjectSidebar] Poll error:', error);
    }
}
```

### 3. Add Path Detection Methods

```javascript
/**
 * Extract all file/folder paths from structure
 */
_extractAllPaths(sections) {
    const paths = new Set();
    
    const traverse = (items, parentPath = '') => {
        for (const item of items) {
            paths.add(item.path);
            if (item.children) {
                traverse(item.children, item.path);
            }
        }
    };
    
    for (const section of sections) {
        if (section.children) {
            traverse(section.children);
        }
    }
    
    return paths;
}

/**
 * Detect changed paths between old and new structure
 */
_detectChangedPaths(oldPaths, newPaths) {
    // Find new paths (added)
    for (const path of newPaths) {
        if (!oldPaths.has(path)) {
            this._addChangedPath(path);
        }
    }
    
    // Find removed paths (mark parent as changed)
    for (const path of oldPaths) {
        if (!newPaths.has(path)) {
            const parent = this._getParentPath(path);
            if (parent) {
                this._addChangedPath(parent);
            }
        }
    }
}

/**
 * Add path and bubble up to parents
 */
_addChangedPath(path) {
    if (!path) return;
    
    this.changedPaths.add(path);
    
    // Bubble up to parents
    const parts = path.split('/');
    for (let i = parts.length - 1; i > 0; i--) {
        const parentPath = parts.slice(0, i).join('/');
        this.changedPaths.add(parentPath);
    }
}

/**
 * Clear path and cleanup parents if no changed children
 */
_clearChangedPath(path) {
    this.changedPaths.delete(path);
    
    // Check parents - clear if no other changed children
    const parts = path.split('/');
    for (let i = parts.length - 1; i > 0; i--) {
        const parentPath = parts.slice(0, i).join('/');
        if (!this._hasChangedChildren(parentPath)) {
            this.changedPaths.delete(parentPath);
        }
    }
    
    // Re-render to update UI
    this.render();
}

/**
 * Check if folder has any changed children
 */
_hasChangedChildren(folderPath) {
    for (const path of this.changedPaths) {
        if (path.startsWith(folderPath + '/')) {
            return true;
        }
    }
    return false;
}

/**
 * Get parent path
 */
_getParentPath(path) {
    const parts = path.split('/');
    if (parts.length <= 1) return null;
    return parts.slice(0, -1).join('/');
}
```

### 4. Modify `renderFile()` and `renderFolder()`

```javascript
/**
 * Render a file item with change indicator
 */
renderFile(file, depth) {
    const icon = this.getFileIcon(file.name);
    const paddingLeft = 2 + (depth * 0.75);
    const isActive = this.selectedFile === file.path;
    const isChanged = this.changedPaths.has(file.path);
    
    return `
        <div class="nav-item nav-file ${isActive ? 'active' : ''} ${isChanged ? 'has-changes' : ''}" 
             style="padding-left: ${paddingLeft}rem"
             data-path="${file.path}">
            ${isChanged ? '<span class="change-indicator"></span>' : ''}
            <i class="bi ${icon}"></i>
            <span>${file.name}</span>
        </div>
    `;
}

/**
 * Render a folder item with change indicator
 */
renderFolder(folder, depth) {
    const folderId = folder.path.replace(/[\/\.]/g, '-');
    const hasChildren = folder.children && folder.children.length > 0;
    const paddingLeft = 2 + (depth * 0.75);
    const isChanged = this.changedPaths.has(folder.path);
    
    let html = `
        <div class="nav-item nav-folder ${isChanged ? 'has-changes' : ''}" 
             style="padding-left: ${paddingLeft}rem"
             data-bs-toggle="collapse" 
             data-bs-target="#folder-${folderId}"
             data-path="${folder.path}">
            ${isChanged ? '<span class="change-indicator"></span>' : ''}
            <i class="bi bi-folder"></i>
            <span>${folder.name}</span>
            ${hasChildren ? '<i class="bi bi-chevron-down chevron ms-auto" style="font-size: 0.7rem;"></i>' : ''}
        </div>
    `;
    
    // ... rest of folder rendering ...
    
    return html;
}
```

### 5. Modify `bindEvents()`

```javascript
bindEvents() {
    // File click events - extended
    const fileItems = this.container.querySelectorAll('.nav-file');
    fileItems.forEach(item => {
        item.addEventListener('click', (e) => {
            // Remove active from all
            fileItems.forEach(f => f.classList.remove('active'));
            // Add active to clicked
            item.classList.add('active');
            
            const path = item.dataset.path;
            this.selectedFile = path;
            
            // NEW: Clear change indicator for this file
            if (this.changedPaths.has(path)) {
                this._clearChangedPath(path);
            }
            
            this.onFileSelect(path);
        });
    });
    
    // ... rest of bindEvents ...
}
```

---

## CSS Styling

Add to `base.html` or existing stylesheet:

```css
/* Change indicator dot */
.change-indicator {
    display: inline-block;
    width: 6px;
    height: 6px;
    background-color: var(--bs-warning, #ffc107);
    border-radius: 50%;
    margin-right: 6px;
    flex-shrink: 0;
    animation: fadeIn 0.3s ease-in-out;
}

/* Ensure nav-item uses flexbox for proper alignment */
.nav-item.has-changes {
    display: flex;
    align-items: center;
}

/* Optional: subtle glow effect */
.change-indicator {
    box-shadow: 0 0 4px var(--bs-warning, #ffc107);
}

@keyframes fadeIn {
    from { opacity: 0; transform: scale(0.5); }
    to { opacity: 1; transform: scale(1); }
}
```

---

## Testing Strategy

### Unit Tests
1. `_extractAllPaths()` - Returns correct path set
2. `_addChangedPath()` - Adds path and parents
3. `_clearChangedPath()` - Removes path, cleans parents
4. `_hasChangedChildren()` - Correct boolean check
5. `_detectChangedPaths()` - Identifies added/removed

### Integration Tests (Playwright/Manual)
1. Create new file → dot appears on file and parents
2. Click changed file → dot disappears
3. All children clicked → parent dot disappears
4. Page refresh → all dots cleared

---

## Implementation Phases

### Phase 1: Core Logic (Backend-less)
- [ ] Add `changedPaths` Set to constructor
- [ ] Implement `_addChangedPath()`, `_clearChangedPath()`
- [ ] Implement `_hasChangedChildren()`, `_getParentPath()`

### Phase 2: Detection Integration
- [ ] Implement `_extractAllPaths()`
- [ ] Implement `_detectChangedPaths()`
- [ ] Modify `_checkForChanges()` to call detection

### Phase 3: UI Rendering
- [ ] Modify `renderFile()` to show indicator
- [ ] Modify `renderFolder()` to show indicator
- [ ] Add CSS styles for indicator

### Phase 4: Click Handler
- [ ] Modify `bindEvents()` to clear on click
- [ ] Ensure re-render updates visual state

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/templates/index.html` | Extend `ProjectSidebar` class with change tracking |
| `src/templates/base.html` | Add CSS styles for `.change-indicator` |
| `src/services/file_service.py` | Add `mtime` field to `FileNode` for content change detection |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Performance with many files | Use Set for O(1) lookups |
| Memory leak | Set cleared on page refresh (by design) |
| Race condition in polling | Existing debounce handles this |
| UI flicker on re-render | Only re-render when clicking (not polling) |

---

## Design Change Log

| Date | Phase | Change Summary |
|------|-------|----------------|
| 01-23-2026 | Bug Fix | Added `mtime` field to `FileNode` dataclass and `_scan_directory()` to include file modification times in structure API. Frontend updated to track `previousPathMtimes` as Map instead of Set, and `_detectChangedPaths()` now compares mtimes to detect content modifications in addition to structure changes. This fixes the bug where file change indicators only appeared for new/deleted files, not content modifications. |
| 01-23-2026 | Refactoring | Updated file paths: `src/services.py` split into `src/services/` package. FileNode now in `src/services/file_service.py`. Imports via `from src.services import X` still work due to `__init__.py` re-exports. |
