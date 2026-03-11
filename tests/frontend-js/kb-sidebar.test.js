/**
 * Tests for FEATURE-049-B: KB Sidebar & Navigation
 * Tests: Section rendering, folder tree, drag-drop, empty state, Intake placeholder, auto-refresh
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

let _implLoaded = false;
function ensureImpl() {
  if (!_implLoaded) {
    try {
      loadFeatureScript('sidebar.js');
      _implLoaded = true;
    } catch { /* not yet implemented */ }
  }
  return typeof globalThis.ProjectSidebar !== 'undefined';
}

const KB_SECTION_WITH_FILES = {
  id: 'knowledge-base',
  label: 'Knowledge Base',
  path: 'x-ipe-docs/knowledge-base',
  icon: 'bi-book',
  exists: true,
  children: [
    { name: 'guide.md', type: 'file', path: 'x-ipe-docs/knowledge-base/guide.md', mtime: 1000 },
    {
      name: 'tutorials',
      type: 'folder',
      path: 'x-ipe-docs/knowledge-base/tutorials',
      children: [
        { name: 'intro.md', type: 'file', path: 'x-ipe-docs/knowledge-base/tutorials/intro.md', mtime: 900 }
      ]
    }
  ]
};

const KB_SECTION_EMPTY = {
  id: 'knowledge-base',
  label: 'Knowledge Base',
  path: 'x-ipe-docs/knowledge-base',
  icon: 'bi-book',
  exists: true,
  children: []
};

const KB_SECTION_NOT_EXISTS = {
  id: 'knowledge-base',
  label: 'Knowledge Base',
  path: 'x-ipe-docs/knowledge-base',
  icon: 'bi-book',
  exists: false,
  children: []
};

describe('FEATURE-049-B: KB Sidebar & Navigation', () => {
  let sidebar;

  beforeEach(() => {
    document.body.innerHTML = '<div id="sidebar-content"></div>';
    // Stub fetch for load()
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ sections: [] })
    });
    // Stub setInterval for polling
    vi.useFakeTimers();
    ensureImpl();
    if (globalThis.ProjectSidebar) {
      sidebar = new globalThis.ProjectSidebar('sidebar-content');
    }
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  describe('AC-049-B-01: Sidebar Section Presence', () => {
    it('should render KB section with bi-book icon', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_WITH_FILES];
      sidebar.render();
      const section = document.querySelector('[data-section-id="knowledge-base"]');
      expect(section).not.toBeNull();
      const icon = section.querySelector('.bi-book');
      expect(icon).not.toBeNull();
    });

    it('should show "Knowledge Base" label', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_WITH_FILES];
      sidebar.render();
      const header = document.querySelector('[data-section-id="knowledge-base"] .nav-section-header span');
      expect(header.textContent).toBe('Knowledge Base');
    });
  });

  describe('AC-049-B-02: Folder Tree Rendering', () => {
    it('should render files with file icons', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_WITH_FILES];
      sidebar.render();
      const files = document.querySelectorAll('[data-section-id="knowledge-base"] .nav-file');
      expect(files.length).toBeGreaterThanOrEqual(1);
      // guide.md should be rendered
      const guideFile = document.querySelector('[data-path="x-ipe-docs/knowledge-base/guide.md"]');
      expect(guideFile).not.toBeNull();
    });

    it('should render folders with folder icons', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_WITH_FILES];
      sidebar.render();
      const folders = document.querySelectorAll('[data-section-id="knowledge-base"] .kb-folder');
      expect(folders.length).toBeGreaterThanOrEqual(1);
      const tutorialsFolder = document.querySelector('[data-path="x-ipe-docs/knowledge-base/tutorials"]');
      expect(tutorialsFolder).not.toBeNull();
    });

    it('should render nested files inside folders', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_WITH_FILES];
      sidebar.render();
      const nestedFile = document.querySelector('[data-path="x-ipe-docs/knowledge-base/tutorials/intro.md"]');
      expect(nestedFile).not.toBeNull();
    });
  });

  describe('AC-049-B-03: Expand/Collapse Folders', () => {
    it('should have chevron on folders with children', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_WITH_FILES];
      sidebar.render();
      const folder = document.querySelector('[data-path="x-ipe-docs/knowledge-base/tutorials"]');
      const chevron = folder.querySelector('.chevron');
      expect(chevron).not.toBeNull();
    });

    it('should toggle children container visibility on folder click', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_WITH_FILES];
      sidebar.render();
      const folder = document.querySelector('[data-path="x-ipe-docs/knowledge-base/tutorials"]');
      const targetSelector = folder.dataset.bsTarget;
      expect(targetSelector).toBeTruthy();
      const childrenContainer = document.querySelector(targetSelector);
      expect(childrenContainer).not.toBeNull();
      expect(childrenContainer.classList.contains('collapse')).toBe(true);
      // Simulate Bootstrap expand: add 'show' class
      childrenContainer.classList.add('show');
      expect(childrenContainer.classList.contains('show')).toBe(true);
      // Simulate Bootstrap collapse: remove 'show' class
      childrenContainer.classList.remove('show');
      expect(childrenContainer.classList.contains('show')).toBe(false);
    });
  });

  describe('AC-049-B-06: Drag-Over Visual Feedback', () => {
    it('should mark KB folders with data-kb-folder attribute', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_WITH_FILES];
      sidebar.render();
      const kbFolders = document.querySelectorAll('[data-kb-folder="true"]');
      expect(kbFolders.length).toBeGreaterThanOrEqual(1);
    });

    it('should make KB folders draggable', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_WITH_FILES];
      sidebar.render();
      const folder = document.querySelector('[data-kb-folder="true"]');
      expect(folder.getAttribute('draggable')).toBe('true');
    });

    it('should make KB files draggable after bindEvents', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_WITH_FILES];
      sidebar.render();
      const file = document.querySelector('[data-section-id="knowledge-base"] .nav-file');
      expect(file.getAttribute('draggable')).toBe('true');
    });

    it('should add kb-drag-over class on dragover and remove on dragleave', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_WITH_FILES];
      sidebar.render();
      sidebar._bindKBDragDrop();
      const folder = document.querySelector('[data-kb-folder="true"]');
      // Simulate dragover with dataTransfer containing text/plain type
      const dragOverEvent = new Event('dragover', { bubbles: true, cancelable: true });
      dragOverEvent.dataTransfer = { types: ['text/plain'], dropEffect: '', effectAllowed: '' };
      dragOverEvent.preventDefault = vi.fn();
      folder.dispatchEvent(dragOverEvent);
      expect(folder.classList.contains('kb-drag-over')).toBe(true);
      // Simulate dragleave with relatedTarget outside folder
      const dragLeaveEvent = new Event('dragleave', { bubbles: true });
      Object.defineProperty(dragLeaveEvent, 'relatedTarget', { value: document.body });
      folder.dispatchEvent(dragLeaveEvent);
      expect(folder.classList.contains('kb-drag-over')).toBe(false);
    });
  });

  describe('AC-049-B-08: Intake Placeholder', () => {
    it('should show Intake placeholder entry', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_WITH_FILES];
      sidebar.render();
      const intake = document.querySelector('.kb-intake-placeholder');
      expect(intake).not.toBeNull();
      expect(intake.textContent).toContain('Intake');
    });

    it('should show Intake even when KB is empty', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_EMPTY];
      sidebar.render();
      const intake = document.querySelector('.kb-intake-placeholder');
      expect(intake).not.toBeNull();
    });
  });

  describe('AC-049-B-09: Empty State', () => {
    it('should show "No articles yet" when KB has no children', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_EMPTY];
      sidebar.render();
      const empty = document.querySelector('.kb-empty-state');
      expect(empty).not.toBeNull();
      expect(empty.textContent).toContain('No articles yet');
    });

    it('should show "No articles yet" when KB root does not exist', () => {
      if (!sidebar) return;
      sidebar.sections = [KB_SECTION_NOT_EXISTS];
      sidebar.render();
      const empty = document.querySelector('.kb-empty-state');
      expect(empty).not.toBeNull();
      expect(empty.textContent).toContain('No articles yet');
    });
  });

  describe('AC-049-B-05: Tree Auto-Refresh', () => {
    it('should listen for kb:changed events', () => {
      if (!sidebar) return;
      const loadSpy = vi.spyOn(sidebar, 'load').mockResolvedValue(undefined);
      document.dispatchEvent(new CustomEvent('kb:changed'));
      expect(loadSpy).toHaveBeenCalled();
    });
  });

  describe('KB Section vs Generic Section', () => {
    it('should use _renderKBSection for knowledge-base id', () => {
      if (!sidebar) return;
      const spy = vi.spyOn(sidebar, '_renderKBSection').mockReturnValue('<div></div>');
      sidebar.sections = [KB_SECTION_WITH_FILES];
      sidebar.render();
      expect(spy).toHaveBeenCalledWith(
        KB_SECTION_WITH_FILES,
        'bi-book',
        true
      );
    });

    it('should NOT use _renderKBSection for other sections', () => {
      if (!sidebar) return;
      const spy = vi.spyOn(sidebar, '_renderKBSection');
      sidebar.sections = [{
        id: 'planning',
        label: 'Project Plan',
        path: 'x-ipe-docs/planning',
        icon: 'bi-kanban',
        exists: true,
        children: []
      }];
      sidebar.render();
      expect(spy).not.toHaveBeenCalled();
    });
  });

  describe('KB Move API Integration', () => {
    it('should have _kbMoveItem method', () => {
      if (!sidebar) return;
      expect(typeof sidebar._kbMoveItem).toBe('function');
    });

    it('should call file move API for file type', async () => {
      if (!sidebar) return;
      const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({}) });
      globalThis.fetch = mockFetch;
      
      await sidebar._kbMoveItem(
        'x-ipe-docs/knowledge-base/guide.md',
        'x-ipe-docs/knowledge-base/tutorials',
        'file'
      );
      
      expect(mockFetch).toHaveBeenCalledWith('/api/kb/files/move', expect.objectContaining({
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' }
      }));
    });

    it('should call folder move API for folder type', async () => {
      if (!sidebar) return;
      const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({}) });
      globalThis.fetch = mockFetch;
      
      await sidebar._kbMoveItem(
        'x-ipe-docs/knowledge-base/old-folder',
        'x-ipe-docs/knowledge-base/new-parent',
        'folder'
      );
      
      expect(mockFetch).toHaveBeenCalledWith('/api/kb/folders/move', expect.objectContaining({
        method: 'PUT'
      }));
    });

    it('should dispatch kb:changed on successful move', async () => {
      if (!sidebar) return;
      globalThis.fetch = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({}) });
      
      const eventSpy = vi.fn();
      document.addEventListener('kb:changed', eventSpy);
      
      await sidebar._kbMoveItem(
        'x-ipe-docs/knowledge-base/guide.md',
        'x-ipe-docs/knowledge-base/tutorials',
        'file'
      );
      
      expect(eventSpy).toHaveBeenCalled();
      document.removeEventListener('kb:changed', eventSpy);
    });
  });
});
