"""Settings window for ViTrans — EVKey-style dialog."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from vitrans.config import AppConfig
from vitrans.resources import resource_path

VERSION = "1.0"

# Language options: (display_name, language_code)
SOURCE_LANGUAGES = [
    ("Tự phát hiện", "auto"),
    ("English", "en"),
    ("Tiếng Việt", "vi"),
    ("日本語 (Japanese)", "ja"),
    ("한국어 (Korean)", "ko"),
    ("中文 (Chinese)", "zh-CN"),
    ("Français", "fr"),
    ("Deutsch", "de"),
]

TARGET_LANGUAGES = [
    ("Tiếng Việt", "vi"),
    ("English", "en"),
    ("日本語 (Japanese)", "ja"),
    ("한국어 (Korean)", "ko"),
    ("中文 (Chinese)", "zh-CN"),
    ("Français", "fr"),
    ("Deutsch", "de"),
]

# Overlay color options: (display_name, key, fill_rgba, border_rgba)
OVERLAY_COLORS = [
    ("🔵 Blue", "blue", (40, 120, 220, 45), (80, 180, 255, 180)),
    ("🟢 Green", "green", (40, 180, 80, 45), (80, 255, 140, 180)),
    ("🔴 Red", "red", (220, 60, 60, 45), (255, 120, 120, 180)),
    ("🟣 Purple", "purple", (140, 60, 220, 45), (180, 120, 255, 180)),
    ("🟠 Orange", "orange", (220, 140, 40, 45), (255, 180, 80, 180)),
    ("⚪ White", "white", (200, 200, 200, 45), (230, 230, 230, 180)),
]

# Hotkey modifiers
HOTKEY_MODIFIERS = [
    ("Alt", "alt"),
    ("Ctrl", "ctrl"),
    ("Shift", "shift"),
    ("Ctrl+Shift", "ctrl+shift"),
    ("Ctrl+Alt", "ctrl+alt"),
]

# Hotkey keys
HOTKEY_KEYS = [
    ("T", "t"),
    ("R", "r"),
    ("Q", "q"),
    ("D", "d"),
    ("W", "w"),
    ("E", "e"),
    ("S", "s"),
    ("F", "f"),
    ("G", "g"),
]

SETTINGS_STYLESHEET = """
    QDialog {
        background-color: #1e1e2e;
        color: #cdd6f4;
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
    }
    QGroupBox {
        border: 1px solid #45475a;
        border-radius: 8px;
        margin-top: 14px;
        padding: 18px 12px 10px 12px;
        font-weight: bold;
        font-size: 13px;
        color: #89b4fa;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 14px;
        padding: 0 6px;
    }
    QLabel {
        color: #cdd6f4;
        font-size: 13px;
    }
    QLabel#statusLabel {
        color: #6c7086;
        font-size: 11px;
        padding: 4px 0;
    }
    QComboBox {
        background-color: #313244;
        border: 1px solid #45475a;
        border-radius: 5px;
        padding: 5px 10px;
        color: #cdd6f4;
        min-width: 160px;
        min-height: 24px;
    }
    QComboBox:hover {
        border-color: #89b4fa;
    }
    QComboBox:focus {
        border-color: #89b4fa;
    }
    QComboBox::drop-down {
        border: none;
        width: 28px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #6c7086;
        margin-right: 8px;
    }
    QComboBox QAbstractItemView {
        background-color: #313244;
        border: 1px solid #45475a;
        color: #cdd6f4;
        selection-background-color: #45475a;
        selection-color: #cdd6f4;
        outline: none;
    }
    QCheckBox {
        spacing: 8px;
        color: #cdd6f4;
        font-size: 13px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid #45475a;
        background: #313244;
    }
    QCheckBox::indicator:hover {
        border-color: #89b4fa;
    }
    QCheckBox::indicator:checked {
        background: #89b4fa;
        border-color: #89b4fa;
    }
    QPushButton {
        background-color: #313244;
        border: 1px solid #45475a;
        border-radius: 6px;
        padding: 8px 20px;
        color: #cdd6f4;
        font-weight: bold;
        font-size: 12px;
        min-height: 20px;
    }
    QPushButton:hover {
        background-color: #45475a;
        border-color: #89b4fa;
    }
    QPushButton:pressed {
        background-color: #585b70;
    }
    QPushButton#saveButton {
        background-color: #89b4fa;
        color: #1e1e2e;
        border: none;
    }
    QPushButton#saveButton:hover {
        background-color: #b4d0fb;
    }
    QPushButton#saveButton:pressed {
        background-color: #74a8f7;
    }
    QPushButton#exitButton {
        background-color: #f38ba8;
        color: #1e1e2e;
        border: none;
    }
    QPushButton#exitButton:hover {
        background-color: #eba0ac;
    }
    QPushButton#exitButton:pressed {
        background-color: #e67e99;
    }
    QPushButton#resetButton {
        color: #a6adc8;
        border-color: #45475a;
    }
"""


def _color_preview_icon(r: int, g: int, b: int, size: int = 16) -> QIcon:
    """Create a small colored circle icon for combobox items."""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(r, g, b))
    painter.setPen(QColor(r, g, b, 200))
    path = QPainterPath()
    path.addRoundedRect(1, 1, size - 2, size - 2, 3, 3)
    painter.fillPath(path, QColor(r, g, b))
    painter.end()
    return QIcon(pixmap)


class SettingsWindow(QDialog):
    """EVKey-style settings dialog for ViTrans."""

    config_changed = pyqtSignal(AppConfig)
    exit_requested = pyqtSignal()

    def __init__(self, config: AppConfig, parent: QWidget | None = None):
        super().__init__(parent)
        self._config = config
        self.setWindowTitle(f"ViTrans — {VERSION}")
        self.setWindowIcon(QIcon(str(resource_path("assets/logo.ico"))))
        self.setFixedSize(420, 430)
        self.setWindowFlags(
            Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowMinimizeButtonHint
        )
        self.setStyleSheet(SETTINGS_STYLESHEET)
        self._build_ui()
        self._load_from_config(config)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 12, 16, 12)
        content_layout.setSpacing(4)

        # -- Group: Dịch thuật --
        translate_group = QGroupBox("Dịch thuật")
        tg_layout = QVBoxLayout(translate_group)
        tg_layout.setSpacing(10)

        # Source language
        src_row = QHBoxLayout()
        src_row.setSpacing(12)
        src_label = QLabel("Ngôn ngữ nguồn")
        src_label.setMinimumWidth(120)
        src_row.addWidget(src_label)
        self.source_combo = QComboBox()
        for display, code in SOURCE_LANGUAGES:
            self.source_combo.addItem(display, code)
        src_row.addWidget(self.source_combo, 1)
        tg_layout.addLayout(src_row)

        # Target language
        tgt_row = QHBoxLayout()
        tgt_row.setSpacing(12)
        tgt_label = QLabel("Ngôn ngữ đích")
        tgt_label.setMinimumWidth(120)
        tgt_row.addWidget(tgt_label)
        self.target_combo = QComboBox()
        for display, code in TARGET_LANGUAGES:
            self.target_combo.addItem(display, code)
        tgt_row.addWidget(self.target_combo, 1)
        tg_layout.addLayout(tgt_row)

        content_layout.addWidget(translate_group)

        # -- Group: Cơ bản --
        basic_group = QGroupBox("Cơ bản")
        bg_layout = QVBoxLayout(basic_group)
        bg_layout.setSpacing(10)

        # Overlay color
        color_row = QHBoxLayout()
        color_row.setSpacing(12)
        color_label = QLabel("Màu overlay")
        color_label.setMinimumWidth(120)
        color_row.addWidget(color_label)
        self.color_combo = QComboBox()
        for display, key, fill_rgba, _border in OVERLAY_COLORS:
            icon = _color_preview_icon(fill_rgba[0], fill_rgba[1], fill_rgba[2])
            self.color_combo.addItem(icon, display, key)
        color_row.addWidget(self.color_combo, 1)
        bg_layout.addLayout(color_row)

        # Hotkey
        hotkey_row = QHBoxLayout()
        hotkey_row.setSpacing(12)
        hotkey_label = QLabel("Phím tắt")
        hotkey_label.setMinimumWidth(120)
        hotkey_row.addWidget(hotkey_label)

        self.modifier_combo = QComboBox()
        self.modifier_combo.setMinimumWidth(90)
        for display, code in HOTKEY_MODIFIERS:
            self.modifier_combo.addItem(display, code)
        hotkey_row.addWidget(self.modifier_combo)

        plus_label = QLabel("+")
        plus_label.setFixedWidth(16)
        plus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hotkey_row.addWidget(plus_label)

        self.key_combo = QComboBox()
        self.key_combo.setMinimumWidth(60)
        for display, code in HOTKEY_KEYS:
            self.key_combo.addItem(display, code)
        hotkey_row.addWidget(self.key_combo)

        hotkey_row.addStretch()
        bg_layout.addLayout(hotkey_row)

        content_layout.addWidget(basic_group)

        # -- Group: Hệ thống --
        system_group = QGroupBox("Hệ thống")
        sg_layout = QVBoxLayout(system_group)
        sg_layout.setSpacing(8)

        self.admin_check = QCheckBox("Chạy với quyền Admin")
        sg_layout.addWidget(self.admin_check)

        self.startup_check = QCheckBox("Khởi động cùng Windows")
        sg_layout.addWidget(self.startup_check)

        content_layout.addWidget(system_group)

        # -- Buttons --
        content_layout.addSpacing(8)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        save_btn = QPushButton("Lưu")
        save_btn.setObjectName("saveButton")
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)

        reset_btn = QPushButton("Đặt lại")
        reset_btn.setObjectName("resetButton")
        reset_btn.clicked.connect(self._on_reset)
        btn_row.addWidget(reset_btn)

        btn_row.addStretch()

        exit_btn = QPushButton("Thoát")
        exit_btn.setObjectName("exitButton")
        exit_btn.clicked.connect(self._on_exit)
        btn_row.addWidget(exit_btn)

        content_layout.addLayout(btn_row)

        # -- Status bar --
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        self._update_status_text()
        content_layout.addWidget(self.status_label)

        layout.addWidget(content, 1)

    def _load_from_config(self, config: AppConfig) -> None:
        """Populate UI controls from an AppConfig."""
        self._set_combo_by_data(self.source_combo, config.source_language)
        self._set_combo_by_data(self.target_combo, config.target_language)
        self._set_combo_by_data(self.color_combo, config.overlay_color)
        self._set_combo_by_data(self.modifier_combo, config.hotkey_modifier)
        self._set_combo_by_data(self.key_combo, config.hotkey_key)
        self.admin_check.setChecked(config.run_as_admin)
        self.startup_check.setChecked(config.start_with_windows)
        self._update_status_text()

    def _build_config_from_ui(self) -> AppConfig:
        """Build an AppConfig from current UI state (preserving geometry from original)."""
        return AppConfig(
            x=self._config.x,
            y=self._config.y,
            width=self._config.width,
            height=self._config.height,
            target_language=str(self.target_combo.currentData()),
            source_language=str(self.source_combo.currentData()),
            overlay_color=str(self.color_combo.currentData()),
            hotkey_modifier=str(self.modifier_combo.currentData()),
            hotkey_key=str(self.key_combo.currentData()),
            run_as_admin=self.admin_check.isChecked(),
            start_with_windows=self.startup_check.isChecked(),
        )

    def update_config(self, config: AppConfig) -> None:
        """Update the internal config reference and refresh UI."""
        self._config = config
        self._load_from_config(config)

    def _on_save(self) -> None:
        new_config = self._build_config_from_ui()

        # Warn about admin changes
        if new_config.run_as_admin and not self._config.run_as_admin:
            reply = QMessageBox.warning(
                self,
                "Chạy với quyền Admin",
                "Ứng dụng sẽ cần khởi động lại với quyền Admin.\n"
                "Bạn có muốn tiếp tục?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                self.admin_check.setChecked(False)
                return

        self._config = new_config
        self.config_changed.emit(new_config)
        self._update_status_text()

    def _on_reset(self) -> None:
        defaults = AppConfig(
            x=self._config.x,
            y=self._config.y,
            width=self._config.width,
            height=self._config.height,
        )
        self._load_from_config(defaults)

    def _on_exit(self) -> None:
        self.exit_requested.emit()

    def _update_status_text(self) -> None:
        modifier = self.modifier_combo.currentText() if hasattr(self, "modifier_combo") else "Alt"
        key = self.key_combo.currentText() if hasattr(self, "key_combo") else "T"
        self.status_label.setText(
            f"ViTrans v{VERSION}  ·  {modifier}+{key} để bắt đầu dịch"
        )

    def closeEvent(self, event) -> None:
        """Hide to tray instead of closing."""
        self.hide()
        event.ignore()

    @staticmethod
    def _set_combo_by_data(combo: QComboBox, value: str) -> None:
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return
        combo.setCurrentIndex(0)
