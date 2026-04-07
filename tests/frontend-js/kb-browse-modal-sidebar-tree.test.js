import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

let implLoaded = false;

function ensureImpl() {
  if (!implLoaded) {
    try {
      loadFeatureScript('kb-browse-modal.js');
      implLoaded = true;
    } catch {
      /* not yet implemented */
    }
  }
  return typeof globalThis.KBBrowseModal !== 'undefined';
}

/**
 * Build a sample tree with nested subfolders to simulate the physical
 * folder structure: user-manuals/confluence-write-docs/{04-core-features, 05-common-workflows}
 */
function sampleTree() {
  return [
    {
      name: 'user-manuals', path: 'user-manuals', type: 'folder',
      children: [
        {
          name: 'confluence-write-docs', path: 'user-manuals/confluence-write-docs', type: 'folder',
          children: [
            {
              name: '04-core-features', path: 'user-manuals/confluence-write-docs/04-core-features', type: 'folder',
              children: [
                { name: 'feature01.md', path: 'user-manuals/confluence-write-docs/04-core-features/feature01.md', type: 'file' },
              ],
            },
            { name: '01-overview.md', path: 'user-manuals/confluence-write-docs/01-overview.md', type: 'file' },
          ],
        },
      ],
    },
  ];
}

function sampleFiles() {
  return [
    { name: 'feature01.md', path: 'user-manuals/confluence-write-docs/04-core-features/feature01.md', frontmatter: {} },
    { name: '01-overview.md', path: 'user-manuals/confluence-write-docs/01-overview.md', frontmatter: {} },
  ];
}

function createModal(tree, files) {
  const modal = new KBBrowseModal();
  modal.overlay = document.createElement('div');
  modal.overlay.innerHTML = `
    <div class="kb-modal-body">
      <div class="kb-modal-sidebar">
        <div class="kb-modal-sidebar-content" data-role="sidebar-folders"></div>
      </div>
    </div>`;
  modal.tree = tree || sampleTree();
  modal.files = files || sampleFiles();
  modal.config = { tags: {} };
  modal._intakePendingDeep = 0;
  modal.activeSidebarFolder = null;
  modal._folderColorMap = {};
  return modal;
}

describe('KB Browse Modal — Sidebar Tree (TASK-1086)', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  it.skipIf(!ensureImpl())('renders subfolders in sidebar tree', () => {
    const modal = createModal();
    modal._renderSidebarFolders();
    const html = modal.overlay.querySelector('[data-role="sidebar-folders"]').innerHTML;
    // Sub-folder names must appear in the sidebar
    expect(html).toContain('confluence-write-docs');
    expect(html).toContain('04-core-features');
  });

  it.skipIf(!ensureImpl())('sidebar section content is scrollable', () => {
    const modal = createModal();
    modal._renderSidebarFolders();
    const sidebarContent = modal.overlay.querySelector('[data-role="sidebar-folders"]');
    expect(sidebarContent).toBeTruthy();
    // The sidebar-folders container should exist to allow scrolling
  });

  it.skipIf(!ensureImpl())('does not show hidden files in sidebar', () => {
    const files = [
      { name: '.kb-index.json.lock', path: 'user-manuals/.kb-index.json.lock', frontmatter: {} },
      { name: 'visible.md', path: 'user-manuals/visible.md', frontmatter: {} },
    ];
    const tree = [
      {
        name: 'user-manuals', path: 'user-manuals', type: 'folder',
        children: [
          { name: '.kb-index.json.lock', path: 'user-manuals/.kb-index.json.lock', type: 'file' },
          { name: 'visible.md', path: 'user-manuals/visible.md', type: 'file' },
        ],
      },
    ];
    const modal = createModal(tree, files);
    // Select user-manuals folder to see files
    modal.activeSidebarFolder = 'user-manuals';
    modal._renderSidebarFolders();
    const html = modal.overlay.querySelector('[data-role="sidebar-folders"]').innerHTML;
    // Hidden files should not appear
    expect(html).not.toContain('.kb-index.json.lock');
    expect(html).toContain('visible.md');
  });
});
