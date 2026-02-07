# Landscape View DSL to CSS Mapping

Complete mapping of Architecture DSL landscape-view properties to CSS implementation.

---

## Zone Level

| DSL | CSS Target | CSS Property |
|-----|------------|--------------|
| `zone "Name"` | `.zone` | Element with `.zone-title = "Name"` |

## App Level

| DSL | CSS Target | CSS Property |
|-----|------------|--------------|
| `app "Name" as alias` | `.app` | `id="alias"`, `.app-name = "Name"` |
| `tech: Value` | `.app-tech` | `textContent includes "Tech: Value"` |
| `platform: Value` | `.app-platform` | `textContent includes "Platform: Value"` |
| `status: healthy` | `.app-status` | `class="app-status healthy"` |
| `status: warning` | `.app-status` | `class="app-status warning"` |
| `status: critical` | `.app-status` | `class="app-status critical"` |

## Database Level

| DSL | CSS Target | CSS Property |
|-----|------------|--------------|
| `database "Name" as alias` | `.database` | `id="alias"`, `.database-name = "Name"` |

## Flow Level

| DSL | CSS Target | HTML Structure |
|-----|------------|----------------|
| `source --> target : "Action"` | `.flow` | `<span class="flow-source">source</span> → <span class="flow-target">target</span> "Action"` |

---

## Status Colors

| Status | Background | Glow Effect |
|--------|------------|-------------|
| `healthy` | `#22c55e` | `box-shadow: 0 0 6px #22c55e` |
| `warning` | `#f97316` | `box-shadow: 0 0 6px #f97316` |
| `critical` | `#ef4444` | `box-shadow: 0 0 6px #ef4444` + pulse animation |

---

## Theme Token Integration

When a theme is loaded, map these design-system.md tokens:

| Theme Token | CSS Variable | Usage |
|-------------|--------------|-------|
| Primary color | `--color-primary` | Zone titles, app names |
| Secondary color | `--color-secondary` | Subtitles, meta text |
| Accent color | `--color-accent` | Flow arrows, highlights |
| Neutral color | `--color-neutral` | Backgrounds |
| Heading font | `--font-heading` | Zone titles, app names |
| Body font | `--font-body` | Meta text |

---

## HTML Element Generation

### Zone HTML
```html
<div class="zone">
    <h3 class="zone-title">{name}</h3>
    <div class="zone-content">
        <!-- apps and databases -->
    </div>
</div>
```

### App HTML
```html
<div class="app" id="{alias}">
    <span class="app-status {status}"></span>
    <h4 class="app-name">{name}</h4>
    <div class="app-meta">
        <div>Tech: {tech}</div>
        <div>Platform: {platform}</div>
    </div>
</div>
```

### Database HTML
```html
<div class="database" id="{alias}">
    <div class="database-icon">🗄️</div>
    <div class="database-name">{name}</div>
</div>
```

### Flow HTML
```html
<div class="flow">
    <span class="flow-source">{source}</span>
    <span class="flow-arrow">→</span>
    <span class="flow-target">{target}</span>
    <span class="flow-action">"{action}"</span>
</div>
```
