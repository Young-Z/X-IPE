"""X-IPE CLI main entry point."""
import click
from pathlib import Path
from typing import Optional

from ..core.config import XIPEConfig
from ..core.scaffold import ScaffoldManager
from ..core.skills import SkillsManager
from .. import __version__


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="x-ipe")
@click.option(
    "--project", "-p",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Project root directory. Defaults to current directory.",
)
@click.pass_context
def cli(ctx: click.Context, project: Optional[Path]) -> None:
    """X-IPE: AI-powered development framework.
    
    Manage X-IPE projects from the command line.
    """
    ctx.ensure_object(dict)
    
    # Resolve project root
    project_root = (project or Path.cwd()).resolve()
    ctx.obj["project_root"] = project_root
    
    # Try to load config
    try:
        config = XIPEConfig.load(project_root)
    except Exception:
        config = XIPEConfig.defaults(project_root)
    
    ctx.obj["config"] = config
    
    # Show help if no command specified
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show project status.
    
    Display current X-IPE project status including:
    - Configuration status
    - Skill counts
    - Project structure status
    """
    project_root = ctx.obj["project_root"]
    config = ctx.obj["config"]
    
    click.echo(f"X-IPE Status for: {project_root}")
    click.echo("-" * 40)
    
    # Config status
    if config.config_path:
        click.echo(f"✓ Config: {config.config_path.name}")
    else:
        click.echo("○ Config: Using defaults (no .x-ipe.yaml)")
    
    # Docs structure
    if config.docs_path.exists():
        click.echo(f"✓ Docs: {config.docs_path.relative_to(project_root)}")
    else:
        click.echo(f"○ Docs: Not initialized")
    
    # Runtime folder
    if config.runtime_path.exists():
        click.echo(f"✓ Runtime: {config.runtime_path.relative_to(project_root)}")
    else:
        click.echo(f"○ Runtime: Not initialized")
    
    # Skills
    skills_manager = SkillsManager(project_root)
    local_skills = skills_manager.get_local_skills()
    
    if config.skills_path.exists():
        click.echo(f"✓ Skills: {len(local_skills)} local skills")
        
        modified = skills_manager.detect_modifications()
        if modified:
            click.echo(f"  ⚠ {len(modified)} modified from package")
    else:
        click.echo(f"○ Skills: Not initialized")


@cli.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """Show X-IPE information.
    
    Display X-IPE package information including:
    - Version
    - Package location
    - Available skills
    """
    project_root = ctx.obj["project_root"]
    config = ctx.obj["config"]
    
    click.echo(f"X-IPE v{__version__}")
    click.echo("-" * 40)
    
    # Package info - use relative import
    from .. import __file__ as pkg_file
    click.echo(f"Package: {Path(pkg_file).parent}")
    
    # Config info
    click.echo(f"\nProject: {project_root}")
    click.echo(f"Config file: {config.config_path or 'None (using defaults)'}")
    
    # Paths
    click.echo(f"\nPaths:")
    click.echo(f"  docs: {config.docs_path}")
    click.echo(f"  skills: {config.skills_path}")
    click.echo(f"  runtime: {config.runtime_path}")
    
    # Server settings
    click.echo(f"\nServer:")
    click.echo(f"  host: {config.server_host}")
    click.echo(f"  port: {config.server_port}")
    click.echo(f"  debug: {config.server_debug}")
    
    # Skill summary
    skills_manager = SkillsManager(project_root)
    package_skills = skills_manager.get_package_skills()
    local_skills = skills_manager.get_local_skills()
    
    click.echo(f"\nSkills:")
    click.echo(f"  package: {len(package_skills)}")
    click.echo(f"  local: {len(local_skills)}")
    
    if local_skills:
        click.echo(f"\nLocal skills:")
        for skill in local_skills[:10]:  # Show max 10
            status = "✓" if not skill.modified else "⚠"
            click.echo(f"  {status} {skill.name}")
        if len(local_skills) > 10:
            click.echo(f"  ... and {len(local_skills) - 10} more")


@cli.command()
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Overwrite existing files.",
)
@click.option(
    "--dry-run", "-n",
    is_flag=True,
    help="Show what would be done without making changes.",
)
@click.option(
    "--no-skills",
    is_flag=True,
    help="Skip copying skills from package.",
)
@click.pass_context
def init(ctx: click.Context, force: bool, dry_run: bool, no_skills: bool) -> None:
    """Initialize X-IPE in the current project.
    
    Creates the standard X-IPE folder structure:
    - docs/ with subfolders for planning, requirements, features
    - .x-ipe/ for runtime data (database, cache)
    - .github/skills/ with bundled skills from package
    - .x-ipe.yaml configuration file
    """
    project_root = ctx.obj["project_root"]
    
    if dry_run:
        click.echo(f"Dry run - previewing changes for: {project_root}")
    else:
        click.echo(f"Initializing X-IPE in: {project_root}")
    
    click.echo("-" * 40)
    
    # Create scaffold manager
    scaffold = ScaffoldManager(project_root, dry_run=dry_run, force=force)
    
    # Create folder structure
    scaffold.create_docs_structure()
    scaffold.create_runtime_folder()
    
    # Copy skills if requested
    if not no_skills:
        scaffold.copy_skills()
    
    # Create config file
    scaffold.create_config_file()
    
    # Update .gitignore if in git repo
    if (project_root / ".git").exists():
        scaffold.update_gitignore()
    
    # Show summary
    created, skipped = scaffold.get_summary()
    
    if dry_run:
        click.echo("\nWould create:")
    else:
        click.echo("\nCreated:")
    
    for path in created:
        try:
            rel_path = path.relative_to(project_root)
        except ValueError:
            rel_path = path
        click.echo(f"  ✓ {rel_path}")
    
    if skipped:
        click.echo("\nSkipped (already exists):")
        for path in skipped:
            try:
                rel_path = path.relative_to(project_root)
            except ValueError:
                rel_path = path
            click.echo(f"  ○ {rel_path}")
    
    if dry_run:
        click.echo("\nRun without --dry-run to apply changes.")
    else:
        click.echo(f"\n✓ X-IPE initialized in {project_root}")


@cli.command()
@click.option(
    "--host", "-h",
    default=None,
    help="Host to bind to (default: from config or 127.0.0.1).",
)
@click.option(
    "--port", "-P",  # Using -P because -p is already used for --project
    type=int,
    default=None,
    help="Port to bind to (default: from config or 5000).",
)
@click.option(
    "--debug/--no-debug",
    default=None,
    help="Enable/disable debug mode.",
)
@click.option(
    "--open", "-o",
    is_flag=True,
    help="Open browser after starting server.",
)
@click.pass_context
def serve(ctx: click.Context, host: Optional[str], port: Optional[int], 
          debug: Optional[bool], open: bool) -> None:
    """Start the X-IPE web server.
    
    Launches the Flask web server with the document viewer and
    interactive console interface.
    
    Settings are loaded from .x-ipe.yaml and can be overridden
    with command line flags.
    """
    config = ctx.obj["config"]
    project_root = ctx.obj["project_root"]
    
    # Apply config defaults, with CLI overrides
    final_host = host or config.server_host
    final_port = port or config.server_port
    final_debug = debug if debug is not None else config.server_debug
    
    click.echo(f"Starting X-IPE server for: {project_root}")
    click.echo("-" * 40)
    click.echo(f"Host: {final_host}")
    click.echo(f"Port: {final_port}")
    click.echo(f"Debug: {final_debug}")
    
    url = f"http://{final_host}:{final_port}"
    click.echo(f"\nServer URL: {url}")
    
    if open:
        import webbrowser
        click.echo("Opening browser...")
        webbrowser.open(url)
    
    # Import and run the existing Flask app
    click.echo("\nPress Ctrl+C to stop the server.")
    
    try:
        # Set environment for the app
        import os
        os.environ["X_IPE_PROJECT_ROOT"] = str(project_root)
        os.environ["FLASK_DEBUG"] = "1" if final_debug else "0"
        
        # Import the Flask app
        from src.app import create_app, socketio
        
        app = create_app()
        
        # Run with socketio for WebSocket support
        socketio.run(
            app,
            host=final_host,
            port=final_port,
            debug=final_debug,
            use_reloader=final_debug,
        )
    except KeyboardInterrupt:
        click.echo("\n✓ Server stopped.")
    except ImportError as e:
        click.echo(f"\nError: Could not import app: {e}")
        click.echo("Make sure you're running from the X-IPE project root.")
        raise click.Abort()


@cli.command()
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Overwrite modified skills without prompting.",
)
@click.option(
    "--dry-run", "-n",
    is_flag=True,
    help="Show what would be done without making changes.",
)
@click.option(
    "--backup/--no-backup",
    default=True,
    help="Create backups of modified skills before overwriting.",
)
@click.option(
    "--skill", "-s",
    default=None,
    help="Upgrade only the specified skill.",
)
@click.pass_context
def upgrade(ctx: click.Context, force: bool, dry_run: bool, 
            backup: bool, skill: Optional[str]) -> None:
    """Upgrade skills from the X-IPE package.
    
    Syncs skills from the installed X-IPE package to the local
    project. Detects locally modified skills and prompts before
    overwriting (unless --force is used).
    """
    project_root = ctx.obj["project_root"]
    
    click.echo(f"Upgrading X-IPE skills in: {project_root}")
    click.echo("-" * 40)
    
    # Create skills manager
    skills_manager = SkillsManager(project_root)
    
    # Check for package skills
    package_skills = skills_manager.get_package_skills()
    if not package_skills:
        click.echo("No package skills available to sync.")
        click.echo("X-IPE may not be installed as a package, or skills are not bundled.")
        return
    
    click.echo(f"Package skills available: {len(package_skills)}")
    
    # Check local skills
    local_skills = skills_manager.get_local_skills()
    modified = skills_manager.detect_modifications()
    
    if local_skills:
        click.echo(f"Local skills: {len(local_skills)}")
        if modified:
            click.echo(f"Modified skills: {len(modified)}")
    
    # Filter by specific skill if requested
    if skill:
        package_skills = [s for s in package_skills if s.name == skill]
        if not package_skills:
            click.echo(f"\nError: Skill '{skill}' not found in package.")
            raise click.Abort()
        click.echo(f"\nUpgrading skill: {skill}")
    
    # Check for modifications that would be overwritten
    skills_to_warn = []
    if not force:
        for pkg_skill in package_skills:
            local_skill = skills_manager.get_skill_info(pkg_skill.name)
            if local_skill and local_skill.source == "local" and local_skill.modified:
                skills_to_warn.append(local_skill)
    
    if skills_to_warn:
        click.echo(f"\nThe following skills have local modifications:")
        for s in skills_to_warn:
            click.echo(f"  ⚠ {s.name}")
        
        if not dry_run:
            if not force:
                if not click.confirm("\nOverwrite modified skills?"):
                    click.echo("Aborted.")
                    return
    
    if dry_run:
        click.echo("\nDry run - would sync:")
        for pkg_skill in package_skills:
            click.echo(f"  → {pkg_skill.name}")
        click.echo("\nRun without --dry-run to apply changes.")
        return
    
    # Perform the sync
    synced = skills_manager.sync_from_package(
        skill_name=skill,
        backup=backup
    )
    
    if synced:
        click.echo(f"\n✓ Synced {len(synced)} skill(s):")
        for name in synced:
            click.echo(f"  ✓ {name}")
    else:
        click.echo("\nNo skills were synced.")
    
    if backup and skills_to_warn:
        click.echo(f"\nBackups created in: {project_root / '.x-ipe' / 'backups'}")


def main() -> None:
    """Main entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
