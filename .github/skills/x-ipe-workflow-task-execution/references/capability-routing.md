# Implementation-family capability routing

Use this contract for design consultation, implementation, bug fix, refactoring
and playground creation. Testing has its own explicit opt-in policy; do not
silently apply discovery defaults to acceptance or browser tools.

1. Read the actual caller's tools.json stage/action, ignoring underscore metadata
   for activation and preserving `_extra_instruction` as bounded context.
2. Missing/empty/metadata-only implementation sections retain legacy discovery:
   discovered implementation skills are eligible, not mandatory to load.
   Any nonmetadata entry activates opt-in: only literal true enables it; false
   and undeclared tools are disabled. Nonboolean entries block that routing
   decision. Never force-enable general or substitute Python when disabled.
3. Resolve mechanically once with:

   ```sh
   python3 .github/skills/x-ipe-workflow-task-execution/scripts/delivery_preflight.py \
     --project-root /approved/project capabilities \
     --stage implement --action code_implementation
   ```

   Substitute the actual stage/action, e.g. implement/technical_design,
   feedback/bug_fix, validation/code_refactor or feedback/human_playground.
   The helper reads but does not execute tools. Review undiscovered configured
   names as gaps, not permission to invent a replacement.
4. Match enabled descriptions to actual runtime, stack and responsibility, not
   filename suffixes. Load only relevant expertise in the same context. General
   is an eligible no-specific-match fallback only when enabled and suitable.
   No suitable enabled capability blocks affected execution; design may report
   a capability gap without executing code.
5. Cache resolution in the current context using returned config/catalog
   revisions; changed configuration or tool declarations require refresh.
   Confirm relevant revisions before execution/claiming reuse. No persisted cache
   or second planner task is required.
6. Order dependent work and shared writes; backend precedes dependent frontend.
   Independent read/test calls may be batched in parallel when data, environment
   and cleanup are isolated. Loading multiple skills does not require subagents.
   Mutation by independent workers still needs explicitly owned paths and stable
   boundaries under the single-loop policy; this is not blanket parallelism.

Return the existing tool operation result unchanged. Eligibility is not execution
authority, semantic correctness or proof that a configured MCP server is available.
