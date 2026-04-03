---
title: "Getting Started — Quick Start: Download a Repository"
section: 3
extraction_id: "github-download-repo-user-manual"
source: "https://github.com"
extracted_at: "2026-04-03T12:17:00Z"
---

# 3. Getting Started — Quick Start: Download a Repository

## Prerequisites

- A web browser (Chrome, Firefox, Safari, or Edge)
- For HTTPS Clone: Git installed on your machine (`git --version` to verify)
- For GitHub CLI: GitHub CLI installed (`gh --version` to verify)
- For ZIP download: No additional tools needed

## Quick Start: Download a Repository in Under 2 Minutes

### Step 1: Navigate to GitHub

1. Open your web browser
2. Go to **https://github.com**
3. You should see the GitHub homepage with a search bar at the top

### Step 2: Search for a Repository

1. Click the **search bar** at the top of the page (or press `/` as a keyboard shortcut)
2. Type the name of the repository you want to download (e.g., `x-ipe`)
3. Press **Enter** to execute the search
4. You should see a search results page listing matching repositories

![Search results page](screenshots/search-results.png)

### Step 3: Navigate to the Repository

1. In the search results, click on the **repository name** link (shown in blue, format: `owner/repo-name`)
2. You should see the repository's main page with file listing, README, and action buttons

![Repository main page](screenshots/repo-page-main.png)

### Step 4: Open the Code Dropdown

1. Locate the green **"<> Code"** button near the top-right of the file listing
2. Click the **"<> Code"** button
3. You should see a dropdown panel with clone URLs and download options

![Code dropdown panel](screenshots/code-dropdown-open.png)

### Step 5: Download Using Your Preferred Method

#### Option A: Clone with HTTPS (Recommended for Developers)

1. In the Code dropdown, ensure the **"HTTPS"** tab is selected (it's the default)
2. Click the **copy icon** (📋) next to the URL (e.g., `https://github.com/Young-Z/X-IPE.git`)
3. Open your **terminal** application
4. Navigate to the directory where you want the code: `cd ~/projects`
5. Type `git clone ` and paste the URL: `git clone https://github.com/Young-Z/X-IPE.git`
6. Press **Enter** to execute the command
7. You should see output like:
   ```
   Cloning into 'X-IPE'...
   remote: Enumerating objects: 5231, done.
   remote: Counting objects: 100% (1832/1832), done.
   ...
   ```
8. When the command completes (prompt returns), the repository is downloaded into a new folder

#### Option B: Download ZIP (Simplest — No Git Required)

1. In the Code dropdown, scroll down to the bottom
2. Click **"Download ZIP"**
3. Your browser will begin downloading a `.zip` file (e.g., `X-IPE-main.zip`)
4. You should see the download progress in your browser's download bar
5. Once complete, extract the ZIP file to access the source code

#### Option C: Clone with GitHub CLI

1. In the Code dropdown, click the **"GitHub CLI"** tab
2. Click the **copy icon** (📋) next to the command (e.g., `gh repo clone Young-Z/X-IPE`)
3. Open your **terminal** application
4. Paste and type the command: `gh repo clone Young-Z/X-IPE`
5. Press **Enter** to execute
6. If prompted for authentication, follow the on-screen instructions
7. You should see the repository being cloned to your local directory
