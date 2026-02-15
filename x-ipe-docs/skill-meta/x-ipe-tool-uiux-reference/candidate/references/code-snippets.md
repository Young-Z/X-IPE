# Code Snippets — x-ipe-tool-uiux-reference

JavaScript code blocks for use with Chrome DevTools MCP `evaluate_script` calls.

---

## re-enable-buttons

Re-enable toolbar buttons after analyze or generate processing completes. MUST be called after every flow completion.

```js
evaluate_script(() => {
  window.__xipeAnalyzeEnabled = true;
  window.__xipeGenerateMockupEnabled = true;
  window.__xipeRefReady = false;
  const ab = document.querySelector('[data-xipe-analyze]');
  const gb = document.querySelector('[data-xipe-generate]');
  if (ab) { ab.disabled = false; ab.classList.remove('xb-proc', 'xipe-btn-processing'); }
  if (gb) { gb.disabled = false; gb.classList.remove('xb-proc', 'xipe-btn-processing'); }
})
```

---

## element-discovery

Discover ALL elements within an area's bounding_box. Pass `area.bounding_box` as argument.

```js
evaluate_script((bbox) => {
  const elements = document.querySelectorAll('*');
  const discovered = [];
  for (const el of elements) {
    if (el.closest('#xipe-toolbar-container')) continue;
    const rect = el.getBoundingClientRect();
    const intersects = (
      rect.right > bbox.x && rect.left < bbox.x + bbox.width &&
      rect.bottom > bbox.y && rect.top < bbox.y + bbox.height &&
      rect.width > 0 && rect.height > 0
    );
    if (intersects) {
      const styles = getComputedStyle(el);
      discovered.push({
        tag: el.tagName, id: el.id || null, classes: [...el.classList],
        rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        type: el.tagName === 'IMG' ? 'image' : el.tagName === 'SVG' ? 'svg' :
              el.tagName === 'CANVAS' ? 'canvas' : el.tagName === 'VIDEO' ? 'video' : 'dom',
        src: el.src || null, srcset: el.srcset || null,
        backgroundImage: styles.backgroundImage !== 'none' ? styles.backgroundImage : null,
        text: el.childNodes.length === 1 && el.childNodes[0].nodeType === 3
              ? el.textContent.trim().substring(0, 200) : null,
        computedStyles: {
          display: styles.display, position: styles.position,
          color: styles.color, backgroundColor: styles.backgroundColor,
          fontFamily: styles.fontFamily, fontSize: styles.fontSize, fontWeight: styles.fontWeight,
          lineHeight: styles.lineHeight, fontStyle: styles.fontStyle,
          margin: styles.margin, padding: styles.padding,
          width: styles.width, height: styles.height,
          textAlign: styles.textAlign, letterSpacing: styles.letterSpacing,
          borderRadius: styles.borderRadius, boxShadow: styles.boxShadow,
          backgroundImage: styles.backgroundImage, opacity: styles.opacity,
          gap: styles.gap, flexDirection: styles.flexDirection,
          alignItems: styles.alignItems, justifyContent: styles.justifyContent
        }
      });
    }
  }
  return discovered;
}, area.bounding_box)
```

---

## ancestor-background

Walk up from the selected element to `<body>` to find the first non-transparent background color/gradient. Returns the ancestor's background properties for inclusion as an enriched element.

```js
evaluate_script((selector) => {
  let el = document.querySelector(selector);
  if (!el) return null;
  const result = { backgrounds: [] };
  while (el && el !== document.documentElement) {
    const styles = getComputedStyle(el);
    const bg = styles.backgroundColor;
    const bgImg = styles.backgroundImage;
    const isTransparent = !bg || bg === 'rgba(0, 0, 0, 0)' || bg === 'transparent';
    const hasGradient = bgImg && bgImg !== 'none';
    if (!isTransparent || hasGradient) {
      result.backgrounds.push({
        tag: el.tagName,
        classes: [...el.classList].slice(0, 3),
        backgroundColor: isTransparent ? null : bg,
        backgroundImage: hasGradient ? bgImg : null
      });
    }
    el = el.parentElement;
  }
  return result;
}, area.snap_selector)
```

---

## resource-download

Download a resource via page-context fetch (same-origin). Returns base64 data URL or null.

```js
evaluate_script((url) => {
  return fetch(url).then(r => r.blob()).then(b => new Promise(resolve => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.readAsDataURL(b);
  })).catch(() => null);
}, resourceUrl)
```

---

## font-detection

Detect @font-face URLs from stylesheets accessible in the page context.

```js
evaluate_script(() => {
  const fonts = [];
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule instanceof CSSFontFaceRule) {
          fonts.push({
            family: rule.style.getPropertyValue('font-family'),
            src: rule.style.getPropertyValue('src')
          });
        }
      }
    } catch (e) { /* cross-origin — skip */ }
  }
  return fonts;
})
```

---

## aria-workaround-screenshot

**From LL-001:** When a selected element has no UID in the a11y snapshot (common for generic `<div>`, `<section>`, `<span>` without ARIA roles), use this workaround:

### Step 1: Add temporary ARIA attributes

```js
evaluate_script((selector) => {
  const el = document.querySelector(selector);
  if (el) {
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', 'xipe-target-element');
    return true;
  }
  return false;
}, elementSelector)
```

### Step 2: Take fresh snapshot and find element

```
take_snapshot()
// Find node with aria-label="xipe-target-element" in the snapshot → get UID
take_screenshot(uid: found_uid, filePath: "screenshots/{element_id}.png")
```

### Step 3: Remove temporary ARIA attributes (cleanup)

```js
evaluate_script((selector) => {
  const el = document.querySelector(selector);
  if (el) {
    el.removeAttribute('role');
    el.removeAttribute('aria-label');
  }
}, elementSelector)
```

This ensures element-level screenshots work for generic DOM elements that lack semantic ARIA roles.
