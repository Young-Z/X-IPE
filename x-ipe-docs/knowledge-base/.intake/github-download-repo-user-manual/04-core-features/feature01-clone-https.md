---
title: "Feature 01: Clone with HTTPS"
section: "4"
feature_number: 1
extraction_id: "github-download-repo-user-manual"
interaction_pattern: "CLI_DISPATCH"
---

# Feature 01: Clone with HTTPS

## Description

Clone a repository to your local machine using the HTTPS protocol. This creates a full Git repository with complete version history, allowing you to pull updates and push changes (if authorized).

## Interaction Pattern: CLI_DISPATCH

| Attribute | Detail |
|-----------|--------|
| System receiving command | Local terminal/shell |
| Enter required | **YES** — press Enter to execute `git clone` |
| Expected output | Progress messages showing objects being downloaded |
| Completion signal | Terminal prompt returns; repository folder appears in current directory |

## Step-by-Step Instructions

1. On the repository page, click the green **"<> Code"** button
   - **Expected outcome:** A dropdown panel appears with clone options
2. Ensure the **"HTTPS"** tab is selected (highlighted/underlined)
   - **Expected outcome:** The URL field shows `https://github.com/{owner}/{repo}.git`
3. Click the **copy icon** (📋) to the right of the URL field
   - **Expected outcome:** URL is copied to your clipboard; icon may briefly change to a checkmark ✓
4. Open your terminal application (Terminal on macOS, Command Prompt/PowerShell on Windows, or any shell on Linux)
5. Navigate to your preferred directory: type `cd ~/projects` and press **Enter**
6. Type: `git clone https://github.com/{owner}/{repo}.git` (paste the copied URL)
7. Press **Enter** to execute
   - **Expected output:**
     ```
     Cloning into '{repo}'...
     remote: Enumerating objects: XXXX, done.
     remote: Counting objects: 100% (XXX/XXX), done.
     remote: Compressing objects: 100% (XXX/XXX), done.
     Receiving objects: 100% (XXXX/XXXX), X.XX MiB | X.XX MiB/s, done.
     Resolving deltas: 100% (XXX/XXX), done.
     ```
8. When the terminal prompt returns, the clone is complete
9. Enter the cloned directory: type `cd {repo}` and press **Enter**

## Edge Cases

- **Private repository:** You'll be prompted for username and password/token
- **Large repository:** Clone may take several minutes; consider using `--depth 1` for a shallow clone
- **Authentication failure:** Use a Personal Access Token instead of password

## Screenshots

![HTTPS Clone dropdown](screenshots/code-dropdown-open.png)
