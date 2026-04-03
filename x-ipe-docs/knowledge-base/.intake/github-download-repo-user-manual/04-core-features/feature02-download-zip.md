---
title: "Feature 02: Download ZIP"
section: "4"
feature_number: 2
extraction_id: "github-download-repo-user-manual"
interaction_pattern: "NAVIGATION"
---

# Feature 02: Download ZIP

## Description

Download the repository as a compressed ZIP archive. This is the simplest method — no Git installation required. The ZIP contains a snapshot of the current branch (usually `main`) without Git history.

## Interaction Pattern: NAVIGATION

The "Download ZIP" link triggers a browser file download. No terminal/CLI action required.

## Step-by-Step Instructions

1. On the repository page, click the green **"<> Code"** button
   - **Expected outcome:** A dropdown panel appears
2. Scroll to the bottom of the dropdown panel
3. Click the **"Download ZIP"** link
   - **Expected outcome:** Browser begins downloading a file named `{repo}-{branch}.zip` (e.g., `X-IPE-main.zip`)
4. Wait for the download to complete (check your browser's download indicator)
5. Navigate to your Downloads folder
6. Extract the ZIP file:
   - **macOS:** Double-click the ZIP file
   - **Windows:** Right-click → "Extract All..."
   - **Linux:** Run `unzip {repo}-main.zip` and press **Enter**
7. The extracted folder contains the repository's source code

## Edge Cases

- **Large repositories:** ZIP download may take longer; file size depends on repository content
- **No Git history:** The ZIP does not include `.git` directory — you cannot pull updates
- **Branch selection:** ZIP downloads the currently selected branch (defaults to `main`)

## Screenshots

![Code dropdown with Download ZIP](screenshots/code-dropdown-open.png)
