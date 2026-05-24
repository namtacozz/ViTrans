"""Configurable global hotkey manager using pynput."""

from collections.abc import Callable

from pynput import keyboard


class HotkeyManager:
    """Manages a single global hotkey that can be updated at runtime."""

    def __init__(self, modifier: str, key: str, callback: Callable[[], None]):
        self._modifier = modifier
        self._key = key
        self._callback = callback
        self._listener: keyboard.GlobalHotKeys | None = None

    def start(self) -> None:
        """Start listening for the configured hotkey."""
        combo = self._build_combo_string()
        self._listener = keyboard.GlobalHotKeys({combo: self._callback})
        self._listener.start()

    def stop(self) -> None:
        """Stop listening."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def update(self, modifier: str, key: str) -> None:
        """Restart listener with a new hotkey combination."""
        self.stop()
        self._modifier = modifier
        self._key = key
        self.start()

    @property
    def display_text(self) -> str:
        """Human-readable hotkey string, e.g. 'Alt+T'."""
        parts = self._modifier.split("+")
        return "+".join(p.strip().capitalize() for p in parts) + f"+{self._key.upper()}"

    def _build_combo_string(self) -> str:
        """Convert modifier='alt', key='t' to pynput format '<alt>+t'."""
        parts = self._modifier.split("+")
        prefix = "+".join(f"<{p.strip()}>" for p in parts)
        return f"{prefix}+{self._key}"
