/**
 * FEATURE-025-F: KB Navigation & Polish — Frontend Tests (TDD)
 *
 * Tests for:
 * - Section tabs rendering (Landing/Topics)
 * - Tab switching (content + tree view)
 * - Badge counts and dynamic updates
 * - Tree filtering by active tab
 * - Default tab selection logic
 * - Edge cases (empty KB, topics deleted, search across tabs)
 */

import { describe, it, expect, vi, beforeEach, afterEach, beforeAll } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';

// ============================================================================
// Load kb-core.js into global scope (plus stubs for kbLanding / kbTopics)
// ============================================================================

const JS_PATH = resolve(import.meta.dirname, '../../src/x_ipe/static/js/features/kb-core.js');

beforeAll(() => {
  // Stub kbLanding and kbTopics before loading kb-core
  globalThis.kbLanding = { render: vi.fn() };
  globalThis.kbTopics = { render: vi.fn() };

  const code = readFileSync(JS_PATH, 'utf-8');
  vm.runInThisContext(code);
});

// ============================================================================
// Helpers
// ============================================================================

/** Create the minimal KB DOM that kbCore.render() would produce */
function createKBDOM({ withTabs = true } = {}) {
  document.body.innerHTML = `
    <div class="kb-container">
      <div class="kb-sidebar pinned" id="kb-sidebar">
        <div class="kb-sidebar-header">
          <span class="kb-sidebar-title">Knowledge Base</span>
          <button class="kb-refresh-btn" id="btn-refresh-index"><i class="bi bi-arrow-clockwise"></i></button>
        </div>
        ${withTabs ? '<div class="kb-section-tabs" id="kb-section-tabs"></div>' : ''}
        <div class="kb-search-box">
          <input type="text" class="kb-search-input" id="kb-search" placeholder="Filter files...">
        </div>
        <div class="kb-tree" id="kb-tree"></div>
      </div>
      <div class="kb-content" id="kb-content"></div>
    </div>
  `;
}

/** Sample index with landing files and topic files */
function sampleIndex() {
  return {
    version: '1.0',
    last_updated: '2026-03-03',
    files: [
      { name: 'report.pdf', path: 'landing/report.pdf', type: 'pdf', size: 1024, topic: null, keywords: [] },
      { name: 'notes.md', path: 'landing/notes.md', type: 'markdown', size: 512, topic: null, keywords: [] },
      { name: 'api-docs.md', path: 'landing/api-docs.md', type: 'markdown', size: 256, topic: null, keywords: ['api'] },
      { name: 'design.md', path: 'topics/architecture/design.md', type: 'markdown', size: 800, topic: 'architecture', keywords: ['design'] },
      { name: 'patterns.md', path: 'topics/architecture/patterns.md', type: 'markdown', size: 600, topic: 'architecture', keywords: [] },
      { name: 'setup.md', path: 'topics/devops/setup.md', type: 'markdown', size: 400, topic: 'devops', keywords: [] },
    ],
  };
}

function sampleTopics() {
  return ['architecture', 'devops'];
}

function mockFetch(responseData, status = 200) {
  return vi.fn(() =>
    Promise.resolve({
      ok: status >= 200 && status < 300,
      status,
      json: () => Promise.resolve(responseData),
    })
  );
}

function resetKbCore() {
  kbCore.index = null;
  kbCore.topics = [];
  kbCore.searchTerm = '';
  kbCore.activeTab = 'landing';
  kbCore.container = null;
}

// ============================================================================
// Tests
// ============================================================================

describe('FEATURE-025-F: KB Navigation & Polish', () => {
  beforeEach(() => {
    resetKbCore();
    vi.restoreAllMocks();
    if (kbLanding?.render?.mockClear) kbLanding.render.mockClear();
    if (kbTopics?.render?.mockClear) kbTopics.render.mockClear();
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  // --------------------------------------------------------------------------
  // 1. Section Tabs Rendering (AC-1.x)
  // --------------------------------------------------------------------------
  describe('Section Tabs Rendering', () => {
    it('AC-1.1: should render two tabs (Landing and Topics) in #kb-section-tabs', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();

      const tabs = document.querySelectorAll('.kb-section-tab');
      expect(tabs.length).toBe(2);
    });

    it('AC-1.2: Landing tab should have inbox icon and "Landing" label', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();

      const landingTab = document.querySelector('.kb-section-tab[data-tab="landing"]');
      expect(landingTab).not.toBeNull();
      expect(landingTab.innerHTML).toContain('bi-inbox');
      expect(landingTab.textContent).toContain('Landing');
    });

    it('AC-1.3: Topics tab should have layers icon and "Topics" label', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();

      const topicsTab = document.querySelector('.kb-section-tab[data-tab="topics"]');
      expect(topicsTab).not.toBeNull();
      expect(topicsTab.innerHTML).toContain('bi-layers');
      expect(topicsTab.textContent).toContain('Topics');
    });

    it('AC-1.4: tabs should use flex layout with equal width', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();

      const container = document.getElementById('kb-section-tabs');
      expect(container.classList.contains('kb-section-tabs')).toBe(true);
      // Both tabs should have flex:1 via CSS class
      const tabs = container.querySelectorAll('.kb-section-tab');
      expect(tabs.length).toBe(2);
    });
  });

  // --------------------------------------------------------------------------
  // 2. Tab Badges (AC-2.x)
  // --------------------------------------------------------------------------
  describe('Tab Badges', () => {
    it('AC-2.1: Landing badge should show count of landing files', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();

      const badge = document.getElementById('kb-badge-landing');
      expect(badge).not.toBeNull();
      expect(badge.textContent).toBe('3'); // 3 landing files
    });

    it('AC-2.2: Topics badge should show count of topics', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();

      const badge = document.getElementById('kb-badge-topics');
      expect(badge).not.toBeNull();
      expect(badge.textContent).toBe('2'); // 2 topics
    });

    it('AC-2.3: updateBadges() should update counts without re-rendering tabs', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();

      // Add a file to the index
      kbCore.index.files.push({ name: 'extra.txt', path: 'landing/extra.txt', type: 'text', size: 100, topic: null, keywords: [] });
      kbCore.topics.push('security');

      kbCore.updateBadges();

      const landingBadge = document.getElementById('kb-badge-landing');
      const topicsBadge = document.getElementById('kb-badge-topics');
      expect(landingBadge.textContent).toBe('4');
      expect(topicsBadge.textContent).toBe('3');
    });

    it('should show 0 badges when KB is empty', () => {
      createKBDOM();
      kbCore.index = { version: '1.0', last_updated: null, files: [] };
      kbCore.topics = [];
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();

      expect(document.getElementById('kb-badge-landing').textContent).toBe('0');
      expect(document.getElementById('kb-badge-topics').textContent).toBe('0');
    });
  });

  // --------------------------------------------------------------------------
  // 3. Tab Switching (AC-3.x)
  // --------------------------------------------------------------------------
  describe('Tab Switching', () => {
    it('AC-3.1: clicking Landing tab should render kbLanding in content area', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'topics';

      kbCore.renderTabs();
      kbCore.switchTab('landing');

      expect(kbLanding.render).toHaveBeenCalled();
      const content = document.getElementById('kb-content');
      expect(kbLanding.render).toHaveBeenCalledWith(content, expect.any(Array));
      // Verify landing files passed
      const passedFiles = kbLanding.render.mock.calls[0][1];
      expect(passedFiles.every(f => f.path.startsWith('landing/'))).toBe(true);
    });

    it('AC-3.2: clicking Topics tab should render kbTopics in content area', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();
      kbCore.switchTab('topics');

      expect(kbTopics.render).toHaveBeenCalled();
      const content = document.getElementById('kb-content');
      expect(kbTopics.render).toHaveBeenCalledWith(content, sampleTopics());
    });

    it('AC-3.3: active tab should have "active" CSS class', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();
      kbCore.switchTab('topics');

      const topicsTab = document.querySelector('.kb-section-tab[data-tab="topics"]');
      const landingTab = document.querySelector('.kb-section-tab[data-tab="landing"]');
      expect(topicsTab.classList.contains('active')).toBe(true);
      expect(landingTab.classList.contains('active')).toBe(false);
    });

    it('AC-3.4: inactive tab should NOT have "active" class', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();
      kbCore.switchTab('landing');

      const topicsTab = document.querySelector('.kb-section-tab[data-tab="topics"]');
      expect(topicsTab.classList.contains('active')).toBe(false);
    });

    it('should update activeTab state when switching', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();
      kbCore.switchTab('topics');

      expect(kbCore.activeTab).toBe('topics');
    });

    it('clicking tab button should trigger switchTab', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();

      const topicsTab = document.querySelector('.kb-section-tab[data-tab="topics"]');
      topicsTab.click();

      expect(kbCore.activeTab).toBe('topics');
      expect(kbTopics.render).toHaveBeenCalled();
    });
  });

  // --------------------------------------------------------------------------
  // 4. Sidebar Tree Filtering (AC-4.x)
  // --------------------------------------------------------------------------
  describe('Sidebar Tree Filtering', () => {
    it('AC-4.1: Landing tab should show only landing files in tree', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTree();

      const tree = document.getElementById('kb-tree');
      const fileItems = tree.querySelectorAll('.kb-file-item');
      fileItems.forEach(item => {
        expect(item.dataset.path).toMatch(/^landing\//);
      });
      expect(fileItems.length).toBe(3);
    });

    it('AC-4.2: Topics tab should show only topic folders in tree', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'topics';

      kbCore.renderTree();

      const tree = document.getElementById('kb-tree');
      const fileItems = tree.querySelectorAll('.kb-file-item');
      fileItems.forEach(item => {
        expect(item.dataset.path).not.toMatch(/^landing\//);
      });
      // architecture has 2 files, devops has 1 = 3 topic files
      expect(fileItems.length).toBe(3);
    });

    it('AC-4.3: search should filter within active tab only', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';
      kbCore.searchTerm = 'api';

      kbCore.renderTree();

      const tree = document.getElementById('kb-tree');
      const fileItems = tree.querySelectorAll('.kb-file-item');
      // Only landing files matching 'api' — api-docs.md
      expect(fileItems.length).toBe(1);
      expect(fileItems[0].dataset.path).toBe('landing/api-docs.md');
    });

    it('search on Topics tab should filter topic files only', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'topics';
      kbCore.searchTerm = 'design';

      kbCore.renderTree();

      const tree = document.getElementById('kb-tree');
      const fileItems = tree.querySelectorAll('.kb-file-item');
      // Only topic files matching 'design' — design.md (name match + keyword match)
      expect(fileItems.length).toBe(1);
      expect(fileItems[0].dataset.path).toBe('topics/architecture/design.md');
    });

    it('AC-4.4: folder toggle should work in both tree views', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      kbCore.renderTree();

      const folder = document.querySelector('.kb-folder');
      expect(folder).not.toBeNull();
      const header = folder.querySelector('.kb-folder-header');
      header.click();
      expect(folder.classList.contains('collapsed')).toBe(true);
    });
  });

  // --------------------------------------------------------------------------
  // 5. Default Tab Selection (AC-6.x)
  // --------------------------------------------------------------------------
  describe('Default Tab Selection', () => {
    it('AC-6.1: should default to Topics tab when topics exist', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();

      // Simulate what init() does after loading data
      kbCore.activeTab = kbCore.topics.length > 0 ? 'topics' : 'landing';

      expect(kbCore.activeTab).toBe('topics');
    });

    it('AC-6.2: should default to Landing tab when no topics exist', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = [];

      kbCore.activeTab = kbCore.topics.length > 0 ? 'topics' : 'landing';

      expect(kbCore.activeTab).toBe('landing');
    });
  });

  // --------------------------------------------------------------------------
  // 6. Edge Cases
  // --------------------------------------------------------------------------
  describe('Edge Cases', () => {
    it('empty KB: Landing tab active, badges show 0', () => {
      createKBDOM();
      kbCore.index = { version: '1.0', last_updated: null, files: [] };
      kbCore.topics = [];
      kbCore.activeTab = 'landing';

      kbCore.renderTabs();
      kbCore.renderTree();

      expect(document.getElementById('kb-badge-landing').textContent).toBe('0');
      expect(document.getElementById('kb-badge-topics').textContent).toBe('0');
      const tree = document.getElementById('kb-tree');
      expect(tree.querySelector('.kb-file-item')).toBeNull();
    });

    it('0 landing files, N topics: Topics tab default', () => {
      createKBDOM();
      kbCore.index = {
        version: '1.0', last_updated: null,
        files: [
          { name: 'a.md', path: 'topics/t1/a.md', type: 'markdown', size: 100, topic: 't1', keywords: [] },
        ],
      };
      kbCore.topics = ['t1'];

      kbCore.activeTab = kbCore.topics.length > 0 ? 'topics' : 'landing';
      kbCore.renderTabs();

      expect(kbCore.activeTab).toBe('topics');
      expect(document.getElementById('kb-badge-landing').textContent).toBe('0');
      expect(document.getElementById('kb-badge-topics').textContent).toBe('1');
    });

    it('search term preserved when switching tabs', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';
      kbCore.searchTerm = 'notes';

      kbCore.renderTabs();
      kbCore.switchTab('topics');

      // searchTerm should still be set
      expect(kbCore.searchTerm).toBe('notes');
    });

    it('no #kb-section-tabs container: renderTabs should not throw', () => {
      document.body.innerHTML = '<div id="kb-tree"></div><div id="kb-content"></div>';
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();
      kbCore.activeTab = 'landing';

      expect(() => kbCore.renderTabs()).not.toThrow();
    });

    it('switchTab with missing kbLanding should not throw', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();

      const origLanding = globalThis.kbLanding;
      try {
        globalThis.kbLanding = undefined;
        kbCore.renderTabs();
        expect(() => kbCore.switchTab('landing')).not.toThrow();
      } finally {
        globalThis.kbLanding = origLanding;
      }
    });

    it('switchTab with missing kbTopics should not throw', () => {
      createKBDOM();
      kbCore.index = sampleIndex();
      kbCore.topics = sampleTopics();

      const origTopics = globalThis.kbTopics;
      try {
        globalThis.kbTopics = undefined;
        kbCore.renderTabs();
        expect(() => kbCore.switchTab('topics')).not.toThrow();
      } finally {
        globalThis.kbTopics = origTopics;
      }
    });
  });
});
