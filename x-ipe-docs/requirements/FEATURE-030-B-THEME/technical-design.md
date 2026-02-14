# Technical Design: Catch Design Theme Mode

> Feature ID: FEATURE-030-B-THEME
> Version: v2.0
> Status: Designed
> Last Updated: 02-14-2026

## Reference

This feature's technical design is documented in the parent design document:

→ **[FEATURE-030-B Technical Design](../FEATURE-030-B/technical-design.md#23-theme-mode-xipe-toolbar-themejs)**

See sections:
- **2.3** Theme Mode (xipe-toolbar-theme.js) — module structure, offscreen canvas, magnifier, color sampling, role annotation
- **2.6** Injection Performance — Stage 2 injection strategy
- **2.8** Utility Functions — rgbToHex, rgbToHsl, cropScreenshot
- **2.9** Error Handling — CORS, canvas tainting

## Key Design Decisions

1. **Offscreen canvas populated by agent screenshot** — not html2canvas (too heavy). Agent provides viewport screenshot via CDP, toolbar loads into canvas.
2. **Magnifier uses requestAnimationFrame** — throttled to 60fps, 11×11 pixel grid at 10x zoom.
3. **Color sampling via canvas getImageData** — single pixel at click coordinates. Fallback to getComputedStyle on CORS error.
4. **Mode registered via `window.__xipeRegisterMode('theme', fn)`** — core provides DOM container.
