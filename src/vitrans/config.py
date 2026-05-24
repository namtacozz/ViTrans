import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    # Overlay geometry
    x: int = 200
    y: int = 160
    width: int = 640
    height: int = 360

    # Translation
    target_language: str = "vi"
    source_language: str = "auto"

    # UI
    overlay_color: str = "blue"

    # Hotkey
    hotkey_modifier: str = "alt"
    hotkey_key: str = "t"

    # System
    run_as_admin: bool = False
    start_with_windows: bool = False


def default_config_path() -> Path:
    return Path.home() / ".vitrans" / "config.json"


def load_config(path: Path | None = None) -> AppConfig:
    config_path = path or default_config_path()
    if not config_path.exists():
        return AppConfig()

    data = json.loads(config_path.read_text(encoding="utf-8"))
    defaults = asdict(AppConfig())
    defaults.update({key: value for key, value in data.items() if key in defaults})
    return AppConfig(**defaults)


def save_config(path: Path | None, config: AppConfig) -> None:
    config_path = path or default_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")
