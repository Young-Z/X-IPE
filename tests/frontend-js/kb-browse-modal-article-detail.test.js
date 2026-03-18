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

const ARTICLE_DATA = {
  name: 'rest-conventions.md',
  path: 'api-guidelines/rest-conventions.md',
  modified_date: '2026-03-17',
  size_bytes: 4301,
  content: '# REST Conventions',
  frontmatter: {
    title: 'REST Conventions',
    description: 'Practical conventions for naming, versioning, and structuring REST APIs.',
    author: 'yzhang',
    created: '2026-03-09',
    auto_generated: false,
    tags: {
      lifecycle: ['design'],
      domain: ['api']
    }
  }
};

function createModal() {
  const modal = new KBBrowseModal();
  modal.overlay = document.createElement('div');
  modal.overlay.innerHTML = '<div data-scene="article"></div>';
  return modal;
}

describe('FEATURE-049-B / CR-003: KB Article Detail Description', () => {
  beforeEach(() => {
    if (!ensureImpl()) return;
    document.body.innerHTML = '';
    globalThis.fetch = vi.fn();
    globalThis.showToast = vi.fn();
    globalThis.showConfirmModal = vi.fn(() => Promise.resolve(true));
    globalThis.hljs = undefined;
    globalThis.marked = undefined;
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('renders a wrapped Description field when frontmatter.description exists', () => {
    if (!ensureImpl()) return;

    const modal = createModal();
    modal._renderArticleScene(ARTICLE_DATA);

    const labels = [...modal.overlay.querySelectorAll('.kb-meta-field-label')];
    const descriptionLabel = labels.find((label) => label.textContent === 'Description');

    expect(descriptionLabel).toBeTruthy();

    const descriptionRow = descriptionLabel.closest('.kb-meta-field');
    expect(descriptionRow.classList.contains('kb-meta-field-wrap')).toBe(true);
    expect(descriptionRow.querySelector('.kb-meta-field-value').textContent)
      .toContain('Practical conventions for naming, versioning, and structuring REST APIs.');
  });

  it('omits the Description field when the description is missing or blank', () => {
    if (!ensureImpl()) return;

    const modal = createModal();
    modal._renderArticleScene({
      ...ARTICLE_DATA,
      frontmatter: {
        ...ARTICLE_DATA.frontmatter,
        description: '   '
      }
    });

    const labels = [...modal.overlay.querySelectorAll('.kb-meta-field-label')].map((label) => label.textContent);
    expect(labels).not.toContain('Description');
  });

  it('defines wrapped metadata styles for multi-line descriptions', () => {
    const css = readFileSync('src/x_ipe/static/css/kb-browse-modal.css', 'utf8');

    expect(css).toContain('.kb-meta-field-wrap');
    expect(css).toContain('white-space: normal');
    expect(css).toContain('word-break: break-word');
  });
});
