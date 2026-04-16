# User Manual — CLI App Mixin

> Additional sections and extraction patterns for command-line interface applications.
> The `provide_framework` operation merges these into the base playbook when `app_type: cli`.

---

## Additional Sections

### A. Command Syntax & Flags

**Replace Section 4 — Core Features with CLI-oriented structure.**

- **Command Structure** — Base syntax pattern (e.g., `app <command> [options] <args>`)
- **Global Flags** — Flags available on all commands (--verbose, --config, --output)
- **Subcommands** — Complete list of subcommands with one-line descriptions
- **Command Reference** — Detailed per-command documentation

**Knowledge request patterns (for request_knowledge):**
- "Find CLI entry point from bin/ entries in package.json, console_scripts in setup.py"
- "Extract base command syntax from --help output, usage strings, argparse/click setup"
- "List global flags from parent parser, global options, shared flags"
- "Enumerate subcommands from command registration, subparser setup, command groups"

### B. Shell Completion

**Insert into Section 2 — Installation & Setup.**

- **Bash Completion** — How to enable tab completion for Bash
- **Zsh Completion** — How to enable tab completion for Zsh
- **Fish Completion** — How to enable tab completion for Fish
- **PowerShell Completion** — How to enable tab completion for PowerShell

**Knowledge request patterns:**
- "Check if shell completion is supported from completion scripts, --completion flag"
- "Find supported shells from bash, zsh, fish, powershell completion files"
- "Extract completion install instructions from docs, Makefile targets"

### C. Piping & Scripting

**Insert after Section 4 — Core Features.**

- **Output Formats** — JSON, CSV, table, plain text output options
- **Piping** — How to pipe output to other commands
- **Scripting Usage** — Using the CLI in shell scripts and automation
- **Exit Codes** — Table of exit codes with meanings

**Knowledge request patterns:**
- "Find supported output formats from --format flag, --json flag, output formatters"
- "Check piping support from stdin reading, stdout structured output"
- "Extract exit codes from sys.exit() calls, process.exit() values, exit code constants"
- "Find scripting examples from examples/ with .sh files, automation docs"

---

## Section Overlay Patterns

These augment the base collection template when `app_type: cli`:

### For Section 2 (Installation & Setup)
- "Check package manager availability from brew formula, apt package, npm/pip install"
- "Find standalone binary from releases page, goreleaser config"
- "Extract PATH setup instructions from installation docs"

### For Section 3 (Getting Started)
- "Capture actual `app --help` output"
- "Find the simplest useful command (hello world equivalent)"
- "Check for interactive mode or REPL from interactive/shell subcommand"

### For Section 6 (Configuration)
- "Find CLI config file location from ~/.apprc, ~/.config/app/, XDG_CONFIG_HOME"
- "Check config precedence order (config file → env var → flag)"

### For Section 7 (Troubleshooting)
- "Find debug/verbose mode from --debug, --verbose, -v flags"
- "Document common permission errors and PATH issues"
