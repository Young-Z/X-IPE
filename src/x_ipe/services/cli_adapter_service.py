"""
FEATURE-027-A: CLI Adapter Registry & Service

CLIAdapterData: Dataclass for adapter configuration.
CLIAdapterService: Load, query, detect, and manage CLI adapters.
"""
import shutil
import yaml
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

from x_ipe.tracing import x_ipe_tracing


ADAPTERS_CONFIG_FILE = 'cli-adapters.yaml'
AUTO_DETECT_PRIORITY = ['copilot', 'opencode', 'claude-code']
DEFAULT_CLI = 'copilot'


@dataclass
class CLIAdapterData:
    """
    Immutable adapter configuration loaded from cli-adapters.yaml.
    
    FEATURE-027-A: CLI Adapter Registry & Service
    """
    name: str
    display_name: str
    command: str
    run_args: str
    inline_prompt_flag: str
    prompt_format: str
    instructions_file: str
    skills_folder: str
    mcp_config_path: str
    mcp_config_format: str
    detection_command: str

    @x_ipe_tracing()
    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return asdict(self)


class CLIAdapterService:
    """
    Service for loading and querying CLI adapter configurations.
    
    FEATURE-027-A: CLI Adapter Registry & Service
    
    Works both inside Flask context (API routes) and outside (CLI commands).
    Follows ConfigService pattern: load → query → return dataclass.
    """

    def __init__(self, config_file_path: Optional[str] = None):
        self._registry: dict[str, CLIAdapterData] = {}
        self._config_file_path = config_file_path
        self._load_registry()

    @x_ipe_tracing()
    def _load_registry(self):
        """Load adapters from cli-adapters.yaml. Project config overrides bundled default."""
        if self._config_file_path:
            yaml_path = Path(self._config_file_path)
        else:
            # Project-level config first (x-ipe-docs/config/), then bundled fallback
            project_path = self._find_project_adapters_config()
            bundled_path = Path(__file__).parent.parent / 'resources' / 'config' / ADAPTERS_CONFIG_FILE
            yaml_path = project_path if project_path else bundled_path

        if not yaml_path.exists():
            raise FileNotFoundError(f"CLI adapters config not found: {yaml_path}")

        with open(yaml_path, 'r', encoding='utf-8') as f:
            raw = yaml.safe_load(f)

        for name, config in raw.get('adapters', {}).items():
            self._registry[name] = CLIAdapterData(name=name, **config)

    @x_ipe_tracing()
    def get_active_adapter(self) -> CLIAdapterData:
        """Resolve and return the active CLI adapter."""
        active_name = self._read_active_cli()

        if active_name:
            if active_name not in self._registry:
                available = ', '.join(self._registry.keys())
                raise ValueError(
                    f"Unknown CLI adapter '{active_name}'. "
                    f"Available: {available}"
                )
            return self._registry[active_name]

        # Auto-detect
        for name in AUTO_DETECT_PRIORITY:
            if name in self._registry and self.is_installed(name):
                return self._registry[name]

        # Default fallback
        return self._registry[DEFAULT_CLI]

    @x_ipe_tracing()
    def list_adapters(self) -> list[CLIAdapterData]:
        """Return all registered adapters."""
        return list(self._registry.values())

    @x_ipe_tracing()
    def get_adapter(self, name: str) -> CLIAdapterData:
        """Return a specific adapter by name. Raises KeyError if not found."""
        if name not in self._registry:
            raise KeyError(f"Unknown CLI adapter: {name}")
        return self._registry[name]

    @x_ipe_tracing()
    def detect_installed_clis(self) -> list[str]:
        """Detect which CLIs are installed on the system."""
        installed = []
        for name, adapter in self._registry.items():
            if shutil.which(adapter.detection_command):
                installed.append(name)
        return installed

    @x_ipe_tracing()
    def is_installed(self, name: str) -> bool:
        """Check if a specific CLI is installed."""
        adapter = self._registry.get(name)
        if not adapter:
            return False
        return shutil.which(adapter.detection_command) is not None

    @x_ipe_tracing()
    def switch_cli(self, name: str) -> None:
        """Switch the active CLI in .x-ipe.yaml."""
        if name not in self._registry:
            available = ', '.join(self._registry.keys())
            raise ValueError(
                f"Unknown CLI adapter '{name}'. Available: {available}"
            )

        config_path = self._find_config_yaml()
        if not config_path:
            raise FileNotFoundError("No .x-ipe.yaml found")

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

        config['cli'] = name

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f, default_flow_style=False)

    @x_ipe_tracing()
    def build_command(self, prompt: str) -> str:
        """Build a shell-safe command string for the active adapter."""
        adapter = self.get_active_adapter()
        escaped = self._escape_prompt(prompt)
        return adapter.prompt_format.format(
            command=adapter.command,
            run_args=adapter.run_args,
            inline_prompt_flag=adapter.inline_prompt_flag,
            escaped_prompt=escaped,
        ).strip()

    @staticmethod
    def _escape_prompt(prompt: str) -> str:
        """Escape shell metacharacters in prompt text."""
        prompt = prompt.replace('\\', '\\\\')
        prompt = prompt.replace('"', '\\"')
        prompt = prompt.replace('$', '\\$')
        prompt = prompt.replace('`', '\\`')
        prompt = prompt.replace('\n', '\\n')
        return prompt

    def _read_active_cli(self) -> Optional[str]:
        """Read the 'cli' key from .x-ipe.yaml."""
        config_path = self._find_config_yaml()
        if not config_path:
            return None
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config.get('cli') if config else None
        except (yaml.YAMLError, IOError):
            return None

    def _find_config_yaml(self) -> Optional[Path]:
        """Find .x-ipe.yaml by traversing up from cwd."""
        current = Path.cwd().resolve()
        for _ in range(20):
            candidate = current / '.x-ipe.yaml'
            if candidate.exists() and candidate.is_file():
                return candidate
            parent = current.parent
            if parent == current:
                break
            current = parent
        return None

    def _find_project_adapters_config(self) -> Optional[Path]:
        """Find cli-adapters.yaml in x-ipe-docs/config/ relative to project root."""
        config_yaml = self._find_config_yaml()
        if config_yaml:
            project_dir = config_yaml.parent
        else:
            project_dir = Path.cwd().resolve()

        candidate = project_dir / 'x-ipe-docs' / 'config' / ADAPTERS_CONFIG_FILE
        if candidate.exists() and candidate.is_file():
            return candidate
        return None
