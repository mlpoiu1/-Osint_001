from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DatabaseConfig:
    path: str = "osint_toolkit.db"


@dataclass
class UIConfig:
    theme: str = "dark"
    show_status_bar: bool = True
    auto_refresh: bool = False
    refresh_interval: int = 300


@dataclass
class PluginConfig:
    auto_load: bool = True
    plugin_dirs: list[str] = field(default_factory=lambda: ["plugins"])
    check_updates: bool = False


@dataclass
class AppConfig:
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    plugins: PluginConfig = field(default_factory=PluginConfig)
    log_level: str = "INFO"
    data_dir: str = "data"

    @classmethod
    def load(cls, path: str | None = None) -> AppConfig:
        if path and Path(path).exists():
            import json
            data = json.loads(Path(path).read_text())
            config = cls()
            if "database" in data:
                config.database = DatabaseConfig(**data["database"])
            if "ui" in data:
                config.ui = UIConfig(**data["ui"])
            if "plugins" in data:
                config.plugins = PluginConfig(**data["plugins"])
            if "log_level" in data:
                config.log_level = data["log_level"]
            if "data_dir" in data:
                config.data_dir = data["data_dir"]
            return config
        return cls()

    def save(self, path: str) -> None:
        import json
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps({
            "database": self.database.__dict__,
            "ui": self.ui.__dict__,
            "plugins": self.plugins.__dict__,
            "log_level": self.log_level,
            "data_dir": self.data_dir,
        }, indent=2))