---
title: "Feature 03: Clone with GitHub CLI"
section: "4"
feature_number: 3
extraction_id: "github-download-repo-user-manual"
interaction_pattern: "CLI_DISPATCH"
---

# Feature 03: Clone with GitHub CLI

## Description

Clone a repository using the GitHub CLI (`gh`), which provides a streamlined experience with built-in authentication and additional features like forking.

## Interaction Pattern: CLI_DISPATCH

| Attribute | Detail |
|-----------|--------|
| System receiving command | Local terminal with `gh` CLI installed |
| Enter required | **YES** — press Enter to execute `gh repo clone` |
| Expected output | Clone progress similar to `git clone` |
| Completion signal | Terminal prompt returns; repository folder appears |

## Prerequisites

- GitHub CLI must be installed: https://cli.github.com/
- Verify installation: type `gh --version` and press **Enter**

## Step-by-Step Instructions

1. On the repository page, click the green **"<> Code"** button
   - **Expected outcome:** A dropdown panel appears
2. Click the **"GitHub CLI"** tab in the dropdown
   - **Expected outcome:** The command field shows `gh repo clone {owner}/{repo}`
3. Click the **copy icon** (📋) next to the command
   - **Expected outcome:** Command is copied to clipboard
4. Open your terminal application
5. Navigate to your preferred directory: type `cd ~/projects` and press **Enter**
6. Paste the command: `gh repo clone {owner}/{repo}`
7. Press **Enter** to execute
   - **Expected outcome:** Repository is cloned to a new directory
8. If this is your first time using `gh`, you may be prompted to authenticate:
   - Follow the on-screen instructions to log in via browser
9. When the terminal prompt returns, the clone is complete

## Screenshots

![GitHub CLI tab](screenshots/code-dropdown-ghcli.png)
