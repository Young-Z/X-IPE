"""Scaffold module for X-IPE project structure creation."""
from pathlib import Path
from typing import List, Tuple, Optional
import shutil
import os
import json


class ScaffoldManager:
    """Manages project structure creation."""
    
    DOCS_STRUCTURE = [
        "x-ipe-docs/requirements",
        "x-ipe-docs/planning",
        "x-ipe-docs/ideas",
        "x-ipe-docs/config",
        "x-ipe-docs/themes",
    ]
    
    GITIGNORE_ENTRIES: list = []  # No X-IPE specific gitignore entries needed
    
    def __init__(self, project_root: Path, dry_run: bool = False, force: bool = False):
        """Initialize ScaffoldManager.
        
        Args:
            project_root: Path to the project root directory.
            dry_run: If True, don't make any changes, just track what would be done.
            force: If True, overwrite existing files/folders.
        """
        self.project_root = Path(project_root).resolve()
        self.dry_run = dry_run
        self.force = force
        self.created: List[Path] = []
        self.skipped: List[Path] = []
    
    def create_docs_structure(self) -> None:
        """Create x-ipe-docs/ folder with subfolders."""
        for folder in self.DOCS_STRUCTURE:
            path = self.project_root / folder
            if path.exists():
                if not self.force:
                    self.skipped.append(path)
                    continue
            if not self.dry_run:
                path.mkdir(parents=True, exist_ok=True)
            self.created.append(path)
    
    def create_runtime_folder(self) -> None:
        """Create .x-ipe/ folder for runtime data."""
        path = self.project_root / ".x-ipe"
        if path.exists():
            if not self.force:
                self.skipped.append(path)
                return
        if not self.dry_run:
            path.mkdir(parents=True, exist_ok=True)
        self.created.append(path)
    
    def _get_resource_path(self, resource_name: str) -> Optional[Path]:
        """Get path to a bundled resource.
        
        Args:
            resource_name: Name of resource (e.g., 'skills', 'copilot-instructions.md')
            
        Returns:
            Path to resource or None if not found.
        """
        # Try importlib.resources first (installed package)
        try:
            from importlib import resources
            resource_ref = resources.files("x_ipe") / "resources" / resource_name
            if resource_ref.is_file() or resource_ref.is_dir():
                return Path(str(resource_ref))
        except (ImportError, TypeError, AttributeError):
            pass
        
        # Fall back to src layout for development
        dev_path = Path(__file__).parent.parent / "resources" / resource_name
        if dev_path.exists():
            return dev_path
        
        return None
    
    def copy_skills(self, skills_source: Optional[Path] = None) -> None:
        """Copy skills from source to .github/skills/.
        
        Args:
            skills_source: Path to skills source directory. If None, uses package skills.
        """
        target = self.project_root / ".github" / "skills"
        
        if skills_source is None:
            skills_source = self._get_resource_path("skills")
        
        if skills_source is None or not skills_source.exists():
            # No skills to copy
            return
        
        if target.exists():
            if not self.force:
                self.skipped.append(target)
                return
        
        if not self.dry_run:
            # Create parent directories
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and self.force:
                shutil.rmtree(target)
            shutil.copytree(skills_source, target, dirs_exist_ok=True)
        self.created.append(target)
    
    def copy_copilot_instructions(self) -> None:
        """Copy or merge copilot-instructions.md to .github/."""
        source = self._get_resource_path("copilot-instructions.md")
        if source is None or not source.exists():
            return
        
        target = self.project_root / ".github" / "copilot-instructions.md"
        
        if target.exists():
            if not self.force:
                # Merge: append X-IPE instructions if not already present
                if not self.dry_run:
                    existing_content = target.read_text()
                    xipe_content = source.read_text()
                    
                    # Check if X-IPE section already exists
                    if "# Copilot Instructions" in existing_content and "## Before You Start" in existing_content:
                        self.skipped.append(target)
                        return
                    
                    # Merge by appending
                    merged = existing_content.rstrip() + "\n\n" + xipe_content
                    target.write_text(merged)
                self.created.append(target)
                return
        
        if not self.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        self.created.append(target)
    
    def copy_mcp_config(self) -> None:
        """Copy mcp-config.json to .github/copilot/."""
        source = self._get_resource_path("copilot")
        if source is None or not source.exists():
            return
        
        source_file = source / "mcp-config.json"
        if not source_file.exists():
            return
        
        target = self.project_root / ".github" / "copilot" / "mcp-config.json"
        
        if target.exists():
            if not self.force:
                self.skipped.append(target)
                return
        
        if not self.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target)
        self.created.append(target)
    
    def get_project_mcp_servers(self) -> dict:
        """Get MCP servers from project's .github/copilot/mcp-config.json.
        
        Returns:
            Dict of server_name -> server_config, or empty dict if not found.
        """
        project_mcp = self.project_root / ".github" / "copilot" / "mcp-config.json"
        if not project_mcp.exists():
            return {}
        
        try:
            project_config = json.loads(project_mcp.read_text())
            return project_config.get("mcpServers", {})
        except (json.JSONDecodeError, IOError):
            return {}
    
    def merge_mcp_config(
        self,
        servers_to_merge: Optional[List[str]] = None,
        target_path: Optional[Path] = None
    ) -> None:
        """Merge project's MCP servers into global config.
        
        Args:
            servers_to_merge: List of server names to merge. If None, merges all.
            target_path: Path to target mcp-config.json. Defaults to ~/.copilot/mcp-config.json.
        
        This allows project-specific MCP servers to be available globally.
        Deep-merges mcpServers objects, with project servers added to global config.
        Existing global servers are preserved unless --force is used for conflicts.
        """
        project_servers = self.get_project_mcp_servers()
        if not project_servers:
            return
        
        # Filter to requested servers if specified
        if servers_to_merge is not None:
            project_servers = {k: v for k, v in project_servers.items() if k in servers_to_merge}
            if not project_servers:
                return
        
        # Target: configurable or default to ~/.copilot/mcp-config.json
        if target_path is None:
            global_copilot_dir = Path.home() / ".copilot"
            global_mcp = global_copilot_dir / "mcp-config.json"
        else:
            global_mcp = Path(target_path)
            global_copilot_dir = global_mcp.parent
        
        if self.dry_run:
            self.created.append(global_mcp)
            return
        
        # Load or create global config
        global_config = {"mcpServers": {}}
        if global_mcp.exists():
            try:
                global_config = json.loads(global_mcp.read_text())
                if "mcpServers" not in global_config:
                    global_config["mcpServers"] = {}
            except (json.JSONDecodeError, IOError):
                global_config = {"mcpServers": {}}
        
        # Merge: add project servers to global
        merged_count = 0
        skipped_count = 0
        for server_name, server_config in project_servers.items():
            if server_name in global_config["mcpServers"]:
                if self.force:
                    global_config["mcpServers"][server_name] = server_config
                    merged_count += 1
                else:
                    skipped_count += 1
            else:
                global_config["mcpServers"][server_name] = server_config
                merged_count += 1
        
        if merged_count > 0:
            global_copilot_dir.mkdir(parents=True, exist_ok=True)
            global_mcp.write_text(json.dumps(global_config, indent=2) + "\n")
            self.created.append(global_mcp)
        elif skipped_count > 0:
            self.skipped.append(global_mcp)
    
    def copy_config_files(self) -> None:
        """Copy config files (copilot-prompt.json, tools.json, .env.example) to x-ipe-docs/config/."""
        config_source = self._get_resource_path("config")
        if config_source is None or not config_source.exists():
            return
        
        target_dir = self.project_root / "x-ipe-docs" / "config"
        
        # Copy each config file individually (don't overwrite existing)
        config_files = ["copilot-prompt.json", "tools.json", ".env.example"]
        for filename in config_files:
            source_file = config_source / filename
            target_file = target_dir / filename
            
            if not source_file.exists():
                continue
                
            if target_file.exists():
                if not self.force:
                    self.skipped.append(target_file)
                    continue
            
            if not self.dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
            self.created.append(target_file)
    
    def copy_planning_templates(self) -> None:
        """Copy planning templates (features.md, task-board.md) to x-ipe-docs/planning/."""
        planning_source = self._get_resource_path("planning")
        if planning_source is None or not planning_source.exists():
            return
        
        target_dir = self.project_root / "x-ipe-docs" / "planning"
        
        # Copy each planning file individually (don't overwrite existing)
        planning_files = ["features.md", "task-board.md"]
        for filename in planning_files:
            source_file = planning_source / filename
            target_file = target_dir / filename
            
            if not source_file.exists():
                continue
                
            if target_file.exists():
                if not self.force:
                    self.skipped.append(target_file)
                    continue
            
            if not self.dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
            self.created.append(target_file)
    
    def copy_themes(self) -> None:
        """Copy default theme to x-ipe-docs/themes/."""
        themes_source = self._get_resource_path("themes")
        if themes_source is None or not themes_source.exists():
            return
        
        target_dir = self.project_root / "x-ipe-docs" / "themes"
        
        # Copy entire theme-default folder
        theme_source = themes_source / "theme-default"
        theme_target = target_dir / "theme-default"
        
        if not theme_source.exists():
            return
        
        if theme_target.exists():
            if not self.force:
                self.skipped.append(theme_target)
                return
        
        if not self.dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            if theme_target.exists() and self.force:
                shutil.rmtree(theme_target)
            shutil.copytree(theme_source, theme_target, dirs_exist_ok=True)
        self.created.append(theme_target)
    
    def create_config_file(self, config_content: Optional[str] = None) -> None:
        """Create .x-ipe.yaml with defaults.
        
        Args:
            config_content: Optional custom config content.
        """
        path = self.project_root / ".x-ipe.yaml"
        
        if path.exists():
            if not self.force:
                self.skipped.append(path)
                return
        
        default_content = """# X-IPE Configuration
version: 1

paths:
  project_root: "."
  x_ipe_app: "."
  docs: "x-ipe-docs"
  skills: ".github/skills"
  runtime: ".x-ipe"

server:
  host: "127.0.0.1"
  port: 5959
  debug: false
"""
        
        if not self.dry_run:
            path.write_text(config_content or default_content)
        self.created.append(path)
    
    def update_gitignore(self) -> None:
        """Add X-IPE patterns to .gitignore."""
        gitignore_path = self.project_root / ".gitignore"
        
        if not gitignore_path.exists():
            if not self.dry_run:
                gitignore_path.write_text("\n".join(self.GITIGNORE_ENTRIES))
            self.created.append(gitignore_path)
            return
        
        # Read existing content
        if self.dry_run:
            self.skipped.append(gitignore_path)
            return
            
        content = gitignore_path.read_text()
        
        # Check if X-IPE entries already exist
        if ".x-ipe/" in content:
            self.skipped.append(gitignore_path)
            return
        
        # Append X-IPE entries
        if self.GITIGNORE_ENTRIES:
            if not content.endswith("\n"):
                content += "\n"
            content += "\n".join(self.GITIGNORE_ENTRIES)
            gitignore_path.write_text(content)
            self.created.append(gitignore_path)
    
    def scaffold_all(self) -> Tuple[List[Path], List[Path]]:
        """Run all scaffolding operations.
        
        Returns:
            Tuple of (created_paths, skipped_paths).
        """
        self.create_docs_structure()
        self.copy_skills()
        self.copy_copilot_instructions()
        self.copy_mcp_config()
        self.copy_config_files()
        self.copy_planning_templates()
        self.copy_themes()
        self.create_config_file()
        self.merge_mcp_config()
        return self.get_summary()
    
    def get_summary(self) -> Tuple[List[Path], List[Path]]:
        """Return (created, skipped) paths."""
        return self.created, self.skipped
