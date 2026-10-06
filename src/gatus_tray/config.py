from dataclasses import dataclass
from pathlib import Path
import tomllib

@dataclass(frozen=True)
class Config:
    backend: str = "gatus"
    url: str = "http://localhost:8050"
    poll_interval: float = 30
    notifications_enabled: bool = True

def load_config(path: Path | None = None) -> Config:
    path = path or Path.home() / ".config/gatus-tray/config.toml"
    if not path.exists(): return Config()
    with path.open("rb") as f: data = tomllib.load(f)
    return Config(str(data.get("backend", "gatus")), str(data.get("url", "http://localhost:8050")), float(data.get("poll_interval", 30)), bool(data.get("notifications_enabled", True)))

