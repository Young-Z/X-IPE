# Technical Design: Copy Design as Mockup Mode

> Feature ID: FEATURE-030-B-MOCKUP
> Version: v2.0
> Status: Designed
> Last Updated: 02-14-2026

## Reference

This feature's technical design is documented in the parent design document:

→ **[FEATURE-030-B Technical Design](../FEATURE-030-B/technical-design.md#24-mockup-mode-xipe-toolbar-mockupjs)**

See sections:
- **2.4** Mockup Mode (xipe-toolbar-mockup.js) — smart-snap detection, component capture, overlay with drag handles
- **2.6** Injection Performance — Stage 2 injection strategy
- **2.7** Agent Skill Updates — rubric analysis flow, deep capture command, iterative validation
- **2.9** Error Handling — element removal, max components, deep capture failures

## Key Design Decisions

1. **Smart-snap traverses max 5 ancestor levels** — first pass: semantic tags (section, nav, article...) + ARIA roles. Second pass (fallback): div with dimensions > 50×50px.
2. **Lightweight capture**: limited property set (~25 CSS props) for initial capture. Deep capture (all getComputedStyle + outerHTML) only on agent request.
3. **Agent rubric analysis** is done server-side by the agent skill, not in the toolbar. Toolbar only captures data and executes deep_capture commands.
4. **Mode registered via `window.__xipeRegisterMode('mockup', fn)`** — core provides DOM container.
5. **Max 20 components per session** — enforced in toolbar to keep payload manageable.
