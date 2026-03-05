# HTML5 Implementation Tool Skill - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Responsive Landing Page with Semantic HTML

**Context:**
- tech_stack entry: "HTML5/CSS3"
- source_code_path: `src/pages/`
- 2 @frontend AAA scenarios received from orchestrator

### AAA Input

```yaml
aaa_scenarios:
  - scenario_text: |
      @frontend
      Test Scenario: Render hero section with navigation
        Arrange:
          - Landing page HTML is loaded in the DOM
        Act:
          - Page renders in a 1280px viewport
        Assert:
          - Navigation contains links with role="navigation"
          - Hero heading is an h1 element
          - Hero section uses semantic <section> tag
  - scenario_text: |
      @frontend
      Test Scenario: Responsive layout collapses on mobile
        Arrange:
          - Landing page HTML is loaded in the DOM
        Act:
          - Viewport is resized to 375px width
        Assert:
          - Navigation hamburger button is visible
          - Navigation links are hidden by default
          - Hero heading font size is smaller than desktop
```

### Execution Flow

```
1. LEARN existing code:
   - Found: no package.json framework dependencies
   - Detected: Vanilla HTML5/CSS3
   - CSS methodology: CSS custom properties in use

2. IMPLEMENT (built-in practices, no research):
   - Created: src/pages/index.html (semantic HTML5 with ARIA)
   - Created: src/pages/styles/landing.css (mobile-first responsive)
   - Created: src/pages/scripts/nav.js (keyboard-accessible hamburger)

3. WRITE vitest tests:
   - Created: tests/landing.test.js
```

### Implementation Output (snippet)

```html
<!-- src/pages/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Landing Page</title>
  <link rel="stylesheet" href="styles/landing.css">
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to content</a>

  <header class="header">
    <nav role="navigation" aria-label="Main navigation">
      <ul class="nav__list">
        <li><a href="#features">Features</a></li>
        <li><a href="#pricing">Pricing</a></li>
        <li><a href="#contact">Contact</a></li>
      </ul>
      <button class="nav__toggle" aria-expanded="false" aria-controls="nav-menu"
              aria-label="Toggle navigation menu">
        ☰
      </button>
    </nav>
  </header>

  <main id="main-content">
    <section class="hero" aria-labelledby="hero-heading">
      <h1 id="hero-heading">Build Something Great</h1>
      <p>A modern landing page with accessibility built in.</p>
    </section>
  </main>

  <footer role="contentinfo">
    <p>&copy; 2026 Example Inc.</p>
  </footer>
  <script src="scripts/nav.js" defer></script>
</body>
</html>
```

```css
/* src/pages/styles/landing.css */
:root {
  --color-primary: #1a73e8;
  --color-text: #202124;
  --spacing-md: 1rem;
  --breakpoint-md: 768px;
}

.skip-link {
  position: absolute;
  left: -9999px;
}
.skip-link:focus {
  left: 0;
  top: 0;
  z-index: 100;
  padding: var(--spacing-md);
  background: var(--color-primary);
  color: #fff;
}

.nav__toggle { display: block; }
.nav__list { display: none; }

@media (min-width: 768px) {
  .nav__toggle { display: none; }
  .nav__list { display: flex; gap: var(--spacing-md); }
}

.hero {
  padding: 2rem var(--spacing-md);
  text-align: center;
}
```

### Test Output (snippet)

```javascript
// tests/landing.test.js
import { describe, test, expect, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';
import { readFileSync } from 'fs';

const html = readFileSync('src/pages/index.html', 'utf-8');

describe('Landing page hero section', () => {
  let document;

  beforeEach(() => {
    const dom = new JSDOM(html);
    document = dom.window.document;
  });

  test('navigation contains links with role navigation', () => {
    // Arrange — DOM loaded in beforeEach
    // Act — page renders
    const nav = document.querySelector('[role="navigation"]');
    // Assert
    expect(nav).not.toBeNull();
    expect(nav.querySelectorAll('a').length).toBeGreaterThan(0);
  });

  test('hero heading is an h1 element', () => {
    const heading = document.querySelector('.hero h1');
    expect(heading).not.toBeNull();
    expect(heading.tagName).toBe('H1');
  });

  test('hero section uses semantic section tag', () => {
    const section = document.querySelector('section.hero');
    expect(section).not.toBeNull();
  });
});
```

### Output

```yaml
operation_output:
  success: true
  result:
    implementation_files:
      - "src/pages/index.html"
      - "src/pages/styles/landing.css"
      - "src/pages/scripts/nav.js"
    test_files:
      - "tests/landing.test.js"
    test_results:
      - scenario: "Render hero section with navigation"
        assert_clause: "Navigation contains links with role navigation"
        status: "pass"
      - scenario: "Render hero section with navigation"
        assert_clause: "Hero heading is an h1 element"
        status: "pass"
      - scenario: "Render hero section with navigation"
        assert_clause: "Hero section uses semantic section tag"
        status: "pass"
      - scenario: "Responsive layout collapses on mobile"
        assert_clause: "Navigation hamburger button is visible"
        status: "pass"
      - scenario: "Responsive layout collapses on mobile"
        assert_clause: "Navigation links are hidden by default"
        status: "pass"
      - scenario: "Responsive layout collapses on mobile"
        assert_clause: "Hero heading font size is smaller than desktop"
        status: "pass"
    lint_status: "pass"
    stack_identified: "HTML5/Vanilla"
  errors: []
```

---

## Example 2: Interactive Modal with Accessibility

**Context:**
- tech_stack entry: "HTML5/JavaScript"
- source_code_path: `src/components/`
- 2 @frontend AAA scenarios

### AAA Input

```yaml
aaa_scenarios:
  - scenario_text: |
      @frontend
      Test Scenario: Open modal and trap focus
        Arrange:
          - Page contains a trigger button and a hidden modal
        Act:
          - User clicks the "Open Settings" button
        Assert:
          - Modal is visible with role="dialog"
          - Modal has aria-modal="true"
          - Focus moves to the first focusable element inside modal
  - scenario_text: |
      @frontend
      Test Scenario: Close modal with Escape key
        Arrange:
          - Modal is currently open
        Act:
          - User presses the Escape key
        Assert:
          - Modal is hidden
          - Focus returns to the trigger button
```

### Execution Flow

```
1. LEARN: No framework dependencies, vanilla JS patterns
2. IMPLEMENT: Created modal component with focus trap and ARIA
3. WRITE: vitest tests with keyboard event simulation
4. RUN tests: 5/5 assertions pass
5. RUN lint: ESLint + Prettier → pass
```

### Implementation Output (snippet)

```javascript
// src/components/modal.js
export function createModal(triggerEl, modalEl) {
  const focusableSelector = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

  const open = () => {
    modalEl.hidden = false;
    modalEl.setAttribute('aria-modal', 'true');
    const firstFocusable = modalEl.querySelector(focusableSelector);
    if (firstFocusable) firstFocusable.focus();
  };

  const close = () => {
    modalEl.hidden = true;
    triggerEl.focus();
  };

  triggerEl.addEventListener('click', open);

  modalEl.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') close();
  });

  const closeBtn = modalEl.querySelector('[data-modal-close]');
  if (closeBtn) closeBtn.addEventListener('click', close);

  return { open, close };
}
```

### Test Output (snippet)

```javascript
// tests/modal.test.js
import { describe, test, expect, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';
import { createModal } from '../src/components/modal.js';

describe('Modal accessibility', () => {
  let document, trigger, modal;

  beforeEach(() => {
    const dom = new JSDOM(`
      <button id="trigger">Open Settings</button>
      <div id="modal" role="dialog" hidden>
        <button data-modal-close>Close</button>
        <input type="text" />
      </div>
    `);
    document = dom.window.document;
    trigger = document.getElementById('trigger');
    modal = document.getElementById('modal');
    createModal(trigger, modal);
  });

  test('open modal sets aria-modal and moves focus', () => {
    // Act
    trigger.click();
    // Assert
    expect(modal.hidden).toBe(false);
    expect(modal.getAttribute('aria-modal')).toBe('true');
    expect(document.activeElement).toBe(modal.querySelector('button'));
  });

  test('escape key closes modal and returns focus', () => {
    // Arrange
    trigger.click();
    // Act
    const event = new dom.window.KeyboardEvent('keydown', { key: 'Escape' });
    modal.dispatchEvent(event);
    // Assert
    expect(modal.hidden).toBe(true);
    expect(document.activeElement).toBe(trigger);
  });
});
```

---

## Example 3: CSS Animation with Vanilla JS Controls

**Context:**
- tech_stack entry: "HTML5/CSS3/JavaScript"
- source_code_path: `src/animations/`
- 1 @frontend AAA scenario

### AAA Input

```yaml
aaa_scenarios:
  - scenario_text: |
      @frontend
      Test Scenario: Toggle animation with prefers-reduced-motion
        Arrange:
          - Page contains an animated card element
          - User has prefers-reduced-motion: reduce set
        Act:
          - Page loads and checks motion preference
        Assert:
          - Animation CSS class is not applied
          - Card is visible without animation
          - A "Play animation" button is available for opt-in
```

### Implementation Output (snippet)

```html
<!-- src/animations/card.html -->
<div class="card" data-animate>
  <h2>Animated Card</h2>
  <p>Content fades in smoothly.</p>
</div>
<button class="card__play-btn" aria-label="Play animation" hidden>
  Play animation
</button>
```

```css
/* src/animations/card.css */
.card {
  opacity: 1;
  transition: none;
}

@media (prefers-reduced-motion: no-preference) {
  .card[data-animate] {
    animation: fadeSlideIn 0.4s ease-out;
  }
}

@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(1rem); }
  to   { opacity: 1; transform: translateY(0); }
}
```

```javascript
// src/animations/card.js
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const card = document.querySelector('[data-animate]');
const playBtn = document.querySelector('.card__play-btn');

if (prefersReducedMotion.matches) {
  card.removeAttribute('data-animate');
  playBtn.hidden = false;
  playBtn.addEventListener('click', () => {
    card.setAttribute('data-animate', '');
    card.style.animation = 'none';
    requestAnimationFrame(() => { card.style.animation = ''; });
  });
}
```

### Output

```yaml
operation_output:
  success: true
  result:
    implementation_files:
      - "src/animations/card.html"
      - "src/animations/card.css"
      - "src/animations/card.js"
    test_files:
      - "tests/card-animation.test.js"
    test_results:
      - scenario: "Toggle animation with prefers-reduced-motion"
        assert_clause: "Animation CSS class is not applied"
        status: "pass"
      - scenario: "Toggle animation with prefers-reduced-motion"
        assert_clause: "Card is visible without animation"
        status: "pass"
      - scenario: "Toggle animation with prefers-reduced-motion"
        assert_clause: "Play animation button is available"
        status: "pass"
    lint_status: "pass"
    stack_identified: "HTML5/Vanilla"
  errors: []
```
