For now X-IPE supports Copilot CLI, I would like it to support OpenCode CLI as well.

Prompt Support
- for example, when we click Copilot button, for now it will open console window and type "Copilot xxxx", please check from online if OpenCode support this kind of inline prompt.
- so in copilot-prompt.json adding a block, for example called copilot-cli-placeholder: { cli-command: "{opencode|copilot}", cli-args: "{--allow-all-tools --allow-all-paths --allow-all-urls}" }, use place holder in prompt so make it more general for all CLIs

Skill Support
- for Copilot CLI, I have setup initial instructions in .github/copilot-instructions.md and having skills under .github/skills folder. I need have similar implementation for OpenCode.

Config to swith between CLIs
- when we call x-ipe init or upgrade, it shall prompt if using github copilot cli or opencode cli