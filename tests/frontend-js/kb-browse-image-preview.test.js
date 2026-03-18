/**
 * TASK-957: KB article image preview — frontend tests
 *
 * Verifies that _renderArticleScene() renders <img> for image files
 * and continues to render markdown for text files.
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'fs';
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

const IMAGE_DATA = {
  name: 'SMART Replenishment.jpg',
  path: 'domain/SMART Replenishment.jpg',
  content: null,
  binary: true,
  file_type: '.jpg',
  size_bytes: 449100,
  modified_date: '2026-03-18',
  frontmatter: {
    title: 'SMART Replenishment System — Mind Map',
    description: 'Mind map of the SMART Replenishment system.',
    author: 'unknown',
    created: '2026-03-18',
    auto_generated: false,
    tags: { lifecycle: ['active'], domain: ['design'] },
  },
};

const TEXT_DATA = {
  name: 'rest-conventions.md',
  path: 'api-guidelines/rest-conventions.md',
  content: '# REST Conventions\n\nSome content here.',
  size_bytes: 4301,
  modified_date: '2026-03-17',
  frontmatter: {
    title: 'REST Conventions',
    author: 'yzhang',
    created: '2026-03-09',
    auto_generated: false,
    tags: { lifecycle: ['design'], domain: ['api'] },
  },
};

function createModal() {
  const modal = new KBBrowseModal();
  modal.overlay = document.createElement('div');
  modal.overlay.innerHTML = '<div data-scene="article"></div>';
  return modal;
}

describe('TASK-957: KB Article Image Preview', () => {
  beforeEach(() => {
    if (!ensureImpl()) return;
    document.body.innerHTML = '';
    globalThis.fetch = vi.fn();
    globalThis.showToast = vi.fn();
    globalThis.showConfirmModal = vi.fn(() => Promise.resolve(true));
    globalThis.hljs = undefined;
    globalThis.marked = { parse: (s) => `<p>${s}</p>` };
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('renders an <img> tag for binary image files (.jpg)', () => {
    if (!ensureImpl()) return;

    const modal = createModal();
    modal._renderArticleScene(IMAGE_DATA);

    const img = modal.overlay.querySelector('.kb-article-content img');
    expect(img).toBeTruthy();
    expect(img.src).toContain('/api/kb/files/');
    expect(img.src).toContain('/raw');
  });

  it('renders an <img> tag for .png files', () => {
    if (!ensureImpl()) return;

    const modal = createModal();
    modal._renderArticleScene({
      ...IMAGE_DATA,
      name: 'chart.png',
      path: 'domain/chart.png',
      file_type: '.png',
    });

    const img = modal.overlay.querySelector('.kb-article-content img');
    expect(img).toBeTruthy();
  });

  it('renders an <img> tag for .webp files', () => {
    if (!ensureImpl()) return;

    const modal = createModal();
    modal._renderArticleScene({
      ...IMAGE_DATA,
      name: 'photo.webp',
      path: 'photos/photo.webp',
      file_type: '.webp',
    });

    const img = modal.overlay.querySelector('.kb-article-content img');
    expect(img).toBeTruthy();
  });

  it('does NOT render <img> for markdown text files', () => {
    if (!ensureImpl()) return;

    const modal = createModal();
    modal._renderArticleScene(TEXT_DATA);

    const content = modal.overlay.querySelector('.kb-article-content');
    expect(content).toBeTruthy();
    expect(content.innerHTML).toContain('REST Conventions');
    // Should not have a standalone image preview element
    const previewImg = content.querySelector('img.kb-image-preview');
    expect(previewImg).toBeFalsy();
  });

  it('image has alt text from title', () => {
    if (!ensureImpl()) return;

    const modal = createModal();
    modal._renderArticleScene(IMAGE_DATA);

    const img = modal.overlay.querySelector('.kb-article-content img');
    expect(img).toBeTruthy();
    expect(img.alt).toBeTruthy();
  });
});

describe('TASK-957: Image preview CSS', () => {
  it('defines styles for kb-image-preview', () => {
    const css = readFileSync('src/x_ipe/static/css/kb-browse-modal.css', 'utf8');
    expect(css).toContain('.kb-image-preview');
  });
});
