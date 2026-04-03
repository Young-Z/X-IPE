---
title: "Workflow 02: Clone a Repository for Development"
section: "5"
workflow_number: 2
extraction_id: "github-download-repo-user-manual"
---

# Workflow 02: Clone a Repository for Development

## Goal

Clone a repository with full Git history so you can contribute changes or keep it updated.

## Prerequisites

- Git installed (`git --version` returns a version number)
- Terminal/command-line access

## Steps

1. Navigate to the repository page on GitHub (e.g., `https://github.com/Young-Z/X-IPE`)
   - **Expected outcome:** Repository page loads with file listing and README

2. Click the green **"<> Code"** button
   - **Expected outcome:** Dropdown opens with clone URL field

3. Ensure **"HTTPS"** tab is selected, then click the **copy icon** (📋) next to the URL
   - **Expected outcome:** URL like `https://github.com/Young-Z/X-IPE.git` is copied to clipboard

4. Open your **terminal** application
   - **Expected outcome:** Terminal window with command prompt appears

5. Type `cd ~/projects` and press **Enter** to navigate to your workspace
   - **Expected outcome:** Current directory changes to `~/projects`

6. Type `git clone ` followed by pasting the URL, then press **Enter**
   - **Full command:** `git clone https://github.com/Young-Z/X-IPE.git`
   - **Expected outcome:** Git downloads the repository; progress messages appear ending with "done."

7. Type `cd X-IPE` and press **Enter** to enter the project directory
   - **Expected outcome:** You are now inside the cloned repository

8. Type `git log --oneline -5` and press **Enter** to verify the clone
   - **Expected outcome:** Shows the 5 most recent commits, confirming full history was downloaded

## Expected Result

You have a complete Git repository on your local machine. You can run `git pull` anytime to fetch the latest changes.

## Cross-References

- [Feature 01: Clone with HTTPS](../04-core-features/feature01-clone-https.md)
