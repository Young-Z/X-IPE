# User Manual — CLI App Mixin

> Additional sections and extraction prompts for command-line interface applications.
> Merge these into the base playbook and collection templates when `app_type: cli`.

---

## Additional Sections

### A. Command Syntax & Flags

**Playbook addition** (replace Section 4 — Core Features with CLI-oriented structure):

- **Command Structure** — Base syntax pattern (e.g., `app <command> [options] <args>`)
- **Global Flags** — Flags available on all commands (--verbose, --config, --output)
- **Subcommands** — Complete list of subcommands with one-line descriptions
- **Command Reference** — Detailed per-command documentation

<!-- EXTRACTION PROMPTS:
- What is the CLI entry point? (look for bin/ entries in package.json, console_scripts in setup.py/pyproject.toml)
- What is the base command syntax? (look for --help output, usage strings, argparse/click/commander setup)
- What global flags exist? (look for parent parser, global options, shared flags)
- What subcommands are available? (look for command registration, subparser setup, command groups)
-->

### B. Shell Completion

**Playbook addition** (insert into Section 2 — Installation & Setup):

- **Bash Completion** — How to enable tab completion for Bash
- **Zsh Completion** — How to enable tab completion for Zsh
- **Fish Completion** — How to enable tab completion for Fish
- **PowerShell Completion** — How to enable tab completion for PowerShell

<!-- EXTRACTION PROMPTS:
- Is shell completion supported? (look for completion scripts, --completion flag, completions/ directory)
- Which shells are supported? (look for bash, zsh, fish, powershell completion files)
- How to install completions? (look for install instructions in docs, Makefile completion target)
-->

### C. Piping & Scripting

**Playbook addition** (insert after Section 4 — Core Features):

- **Output Formats** — JSON, CSV, table, plain text output options
- **Piping** — How to pipe output to other commands
- **Scripting Usage** — Using the CLI in shell scripts and automation
- **Exit Codes** — Table of exit codes with meanings

<!-- EXTRACTION PROMPTS:
- What output formats are supported? (look for --format flag, --json flag, output formatters)
- Does the CLI support piping? (look for stdin reading, stdout structured output)
- What exit codes does the CLI use? (look for sys.exit() calls, process.exit() values, exit code constants)
- Are there scripting examples? (look for examples/ with .sh files, automation docs)
-->

---

## Section Overlay Prompts

These prompts augment the base collection template when `app_type: cli`:

### For Section 2 (Installation & Setup)
<!-- ADDITIONAL PROMPTS:
- Is the CLI available via package managers? (look for brew formula, apt package, npm global install, pip install)
- Is there a standalone binary? (look for releases page, goreleaser config, build scripts)
- How to add to PATH? (look for installation instructions mentioning PATH)
-->

### For Section 3 (Getting Started)
<!-- ADDITIONAL PROMPTS:
- What does `app --help` show? (capture actual help output)
- What is the simplest useful command? (look for "hello world" equivalent)
- Is there an interactive mode or REPL? (look for interactive/shell subcommand)
-->

### For Section 5 (Configuration)
<!-- ADDITIONAL PROMPTS:
- Where is the CLI config file? (look for ~/.apprc, ~/.config/app/, XDG_CONFIG_HOME usage)
- Does the CLI support config file + env var + flag precedence? (look for config loading order)
-->

### For Section 6 (Troubleshooting)
<!-- ADDITIONAL PROMPTS:
- How to run in debug/verbose mode? (look for --debug, --verbose, -v flags)
- Common permission errors? (look for sudo usage, file permission checks)
- PATH or binary-not-found issues?
-->
