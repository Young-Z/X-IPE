# FEATURE-027-E: CLI Migration & Upgrade — Technical Design

## Part 1: Agent Summary

### Architecture Decision
Add `--cli` option to the existing `upgrade` command in `main.py`. When provided, it triggers a migration flow: backup → config update → redeploy. The migration logic lives in a new `_migrate_cli()` helper function in `main.py` (not a separate service — KISS: it orchestrates existing services).

### Components Modified
1. **`main.py`** — Add `--cli` option to upgrade command, add `_migrate_cli()` helper
2. No new services needed — orchestrates CLIAdapterService + MCPDeployerService

### Key Design Decisions
- Migration is a CLI-level orchestration, not a service — keeps services focused
- Backup uses `shutil.copytree` / `shutil.copy2` for simplicity
- Timestamp format: `YYYYMMDD-HHMMSS` for sortable backups
- FEATURE-027-C (skill translation) integration: when available, calls translation service; if not yet implemented, skips with a log message

---

## Part 2: Implementation Guide

### Modified: `main.py` upgrade command

Add `--cli` option:
```python
@click.option("--cli", "cli_name", default=None, help="Switch to a different CLI adapter.")
```

Flow when `--cli` is provided:
```
1. Validate cli_name against adapter registry
2. Read current CLI from .x-ipe.yaml
3. If same → "Already using {cli}", return
4. If no .x-ipe.yaml → error "Run x-ipe init first"
5. Call _migrate_cli(project_root, old_cli, new_cli, dry_run, force)
6. Skip normal skills sync
```

### Helper: `_migrate_cli()`
```python
def _migrate_cli(project_root, old_cli, new_cli, dry_run, force):
    # 1. Backup old artifacts
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = project_root / ".x-ipe" / "backup" / f"{old_cli}-{timestamp}"
    
    old_adapter = CLIAdapterService().get_adapter(old_cli)
    # Back up skills folder, instructions file, project MCP config
    
    # 2. Update .x-ipe.yaml
    # Read, update cli key, write
    
    # 3. Deploy MCP config for new CLI
    new_adapter = CLIAdapterService().get_adapter(new_cli)
    deployer = MCPDeployerService(project_root)
    deployer.deploy(new_adapter, force=force, dry_run=dry_run)
    
    # 4. Log summary
```
