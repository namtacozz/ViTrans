from vitrans.hotkey import HotkeyManager


def test_build_combo_string_simple():
    mgr = HotkeyManager("alt", "t", lambda: None)
    assert mgr._build_combo_string() == "<alt>+t"


def test_build_combo_string_compound_modifier():
    mgr = HotkeyManager("ctrl+shift", "r", lambda: None)
    assert mgr._build_combo_string() == "<ctrl>+<shift>+r"


def test_display_text():
    mgr = HotkeyManager("alt", "t", lambda: None)
    assert mgr.display_text == "Alt+T"


def test_display_text_compound():
    mgr = HotkeyManager("ctrl+alt", "d", lambda: None)
    assert mgr.display_text == "Ctrl+Alt+D"
