# Learning Sessions

Tracked behavior sessions for AI agent training. Historical sessions were captured by the retired `x-ipe-tool-learning-behavior-tracker-for-web` skill. New behavior observations are captured by `x-ipe-knowledge-mimic-web-behavior-tracker` and written to `x-ipe-docs/.mimicked/`.

| Session | Purpose | Domain | Events | Screenshots | Date |
|---------|---------|--------|--------|-------------|------|
| [download-repo-github](./download-repo-github/) | learn how to download repo | github.com | 29 | 4 | 2026-04-03 |
| [downloading-repo-github](./downloading-repo-github/) | learn downloading repo | github.com | 0 | 1 | 2026-04-03 |
| [github-download-repo](./github-download-repo/) | learn downloading repo | github.com | 27 | 5 | 2026-04-03 |

## Folder Structure

```
x-ipe-docs/learning/{session-name}/
├── track/
│   └── track-list.json    # Recorded events (schema v2.0)
└── imgs/
    └── screenshot-*.png   # Screenshots taken on event changes
```
