from pathlib import Path

from vitrans.config import AppConfig, load_config, save_config


def test_load_config_returns_defaults_when_file_missing(tmp_path: Path):
    config = load_config(tmp_path / "missing.json")
    assert config == AppConfig(x=200, y=160, width=640, height=360, target_language="vi")


def test_save_and_load_config_round_trip(tmp_path: Path):
    path = tmp_path / "config.json"
    config = AppConfig(x=10, y=20, width=800, height=500, target_language="vi")
    save_config(path, config)
    assert load_config(path) == config


def test_load_config_uses_defaults_for_missing_keys(tmp_path: Path):
    path = tmp_path / "config.json"
    path.write_text('{"x": 10, "width": 900}', encoding="utf-8")
    config = load_config(path)
    assert config == AppConfig(x=10, y=160, width=900, height=360, target_language="vi")
