---
title: "Workflow 03: Fork and Clone for Contributing"
section: "5"
workflow_number: 3
extraction_id: "github-download-repo-user-manual"
---

# Workflow 03: Fork and Clone for Contributing

## Goal

Fork a repository to your GitHub account and clone it locally so you can make changes and submit pull requests.

## Prerequisites

- GitHub account (signed in)
- Git installed

## Steps

1. Navigate to the repository page you want to contribute to
   - **Expected outcome:** Repository page loads

2. Click the **"Fork"** button in the top-right area of the page
   - **Expected outcome:** GitHub creates a copy of the repository under your account; you're redirected to your fork

3. On your forked repository page, click the green **"<> Code"** button
   - **Expected outcome:** Dropdown shows clone URL pointing to your fork

4. Copy the HTTPS URL and clone it to your local machine (same as Workflow 02, steps 3-7)
   - **Expected outcome:** Your fork is cloned locally

5. Add the original repository as an "upstream" remote:
   - Type `git remote add upstream https://github.com/{original-owner}/{repo}.git` and press **Enter**
   - **Expected outcome:** No output (silent success)

6. Verify remotes: type `git remote -v` and press **Enter**
   - **Expected outcome:** Shows `origin` (your fork) and `upstream` (original repo)

## Expected Result

You have a local clone of your fork with an upstream remote configured, ready for contribution workflow (branch → commit → push → pull request).

## Cross-References

- [Feature 01: Clone with HTTPS](../04-core-features/feature01-clone-https.md)
- [Workflow 02: Clone for Development](workflow02-clone-for-development.md)
