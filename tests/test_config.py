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


def test_new_config_fields_have_defaults(tmp_path: Path):
    config = load_config(tmp_path / "missing.json")
    assert config.source_language == "auto"
    assert config.overlay_color == "blue"
    assert config.hotkey_modifier == "alt"
    assert config.hotkey_key == "t"
    assert config.run_as_admin is False
    assert config.start_with_windows is False


def test_old_config_backward_compatible(tmp_path: Path):
    """Config from an older version without new fields should load fine."""
    path = tmp_path / "config.json"
    path.write_text(
        '{"x": 100, "y": 200, "width": 800, "height": 600, "target_language": "vi"}',
        encoding="utf-8",
    )
    config = load_config(path)
    assert config.x == 100
    assert config.y == 200
    assert config.source_language == "auto"
    assert config.overlay_color == "blue"
    assert config.hotkey_modifier == "alt"
    assert config.hotkey_key == "t"
    assert config.run_as_admin is False
    assert config.start_with_windows is False


def test_save_and_load_full_config_round_trip(tmp_path: Path):
    path = tmp_path / "config.json"
    config = AppConfig(
        x=50,
        y=100,
        width=1024,
        height=768,
        target_language="ja",
        source_language="en",
        overlay_color="purple",
        hotkey_modifier="ctrl+shift",
        hotkey_key="r",
        run_as_admin=True,
        start_with_windows=True,
    )
    save_config(path, config)
    loaded = load_config(path)
    assert loaded == config
