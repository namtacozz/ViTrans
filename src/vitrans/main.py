import ctypes
import sys
import threading

from vitrans.encoding import configure_utf8_stdio

configure_utf8_stdio()

from PyQt6.QtCore import QObject, QRect, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon

from vitrans.capture import capture_rect
from vitrans.config import AppConfig, default_config_path, load_config, save_config
from vitrans.geometry import content_capture_rect, font_size_for_bbox, translate_capture_bbox_to_overlay
from vitrans.hotkey import HotkeyManager
from vitrans.models import TranslatedBox
from vitrans.ocr import read_text, warm_up_reader
from vitrans.overlay import OverlayWindow
from vitrans.resources import resource_path
from vitrans.selection import SelectionWindow
from vitrans.settings import SettingsWindow
from vitrans.startup import restart_as_admin, set_startup
from vitrans.translate import TranslationError, translate_texts


def set_windows_app_id() -> None:
    if sys.platform != "win32":
        return
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ViTrans.App")


class UiBridge(QObject):
    toggle_requested = pyqtSignal()
    boxes_ready = pyqtSignal(object, list)
    status_ready = pyqtSignal(object, str)


class ViTransApp:
    def __init__(self):
        self.config_path = default_config_path()
        self.config = load_config(self.config_path)
        set_windows_app_id()
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setApplicationName("ViTrans")
        self.qt_app.setApplicationDisplayName("ViTrans")
        self.qt_app.setDesktopFileName("ViTrans")
        self.qt_app.setWindowIcon(QIcon(str(resource_path("assets/logo.ico"))))
        self.qt_app.setQuitOnLastWindowClosed(False)
        self.bridge = UiBridge()
        self.overlays: list[OverlayWindow] = []
        self.selection_window: SelectionWindow | None = None
        self.settings_window: SettingsWindow | None = None
        self.tray = self._create_tray()
        self.bridge.toggle_requested.connect(self.toggle_overlay)
        self.bridge.boxes_ready.connect(lambda overlay, boxes: overlay.set_translated_boxes(boxes))
        self.bridge.status_ready.connect(lambda overlay, message: overlay.set_status(message))
        self.ocr_lock = threading.Lock()
        self.hotkey_manager = HotkeyManager(
            self.config.hotkey_modifier,
            self.config.hotkey_key,
            self.toggle_overlay_threadsafe,
        )
        QTimer.singleShot(3000, self._start_ocr_warmup)

    def _create_tray(self) -> QSystemTrayIcon:
        tray = QSystemTrayIcon(QIcon(str(resource_path("assets/logo.ico"))), self.qt_app)
        tray.setToolTip("ViTrans")
        tray.activated.connect(self._tray_activated)
        tray.show()
        return tray

    def _tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_settings()

    def show_settings(self) -> None:
        """Open or bring to front the settings window."""
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self.config)
            self.settings_window.config_changed.connect(self._on_config_changed)
            self.settings_window.exit_requested.connect(self.quit)
        self.settings_window.update_config(self.config)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def _on_config_changed(self, new_config: AppConfig) -> None:
        old_config = self.config
        self.config = new_config
        save_config(self.config_path, self.config)

        # Update hotkey if changed
        if (old_config.hotkey_modifier != new_config.hotkey_modifier
                or old_config.hotkey_key != new_config.hotkey_key):
            self.hotkey_manager.update(new_config.hotkey_modifier, new_config.hotkey_key)

        if old_config.overlay_color != new_config.overlay_color:
            for overlay in self.overlays:
                overlay.update_overlay_color(new_config.overlay_color)

        # Handle startup registry
        if old_config.start_with_windows != new_config.start_with_windows:
            set_startup(new_config.start_with_windows)

        # Handle admin elevation (requires restart)
        if new_config.run_as_admin and not old_config.run_as_admin:
            save_config(self.config_path, self.config)
            restart_as_admin()

    def _start_ocr_warmup(self) -> None:
        threading.Thread(target=warm_up_reader, daemon=True).start()

    def run(self) -> int:
        self.hotkey_manager.start()
        return self.qt_app.exec()

    def toggle_overlay_threadsafe(self) -> None:
        self.bridge.toggle_requested.emit()

    def open_ui(self) -> None:
        self.start_selection()

    def toggle_overlay(self) -> None:
        if self.selection_window is not None and self.selection_window.isVisible():
            self.selection_window.close()
            self.selection_window = None
            return
        self.start_selection()

    def start_selection(self) -> None:
        self.selection_window = SelectionWindow(self.selection_selected, self.selection_cancelled)
        self.selection_window.showFullScreen()
        self.selection_window.raise_()
        self.selection_window.activateWindow()

    def selection_selected(self, rect: QRect) -> None:
        self.selection_window = None
        overlay: OverlayWindow | None = None

        def translate_current() -> None:
            if overlay is not None:
                self.translate_overlay(overlay)

        def hide_current() -> None:
            if overlay is not None:
                self.hide_overlay(overlay)

        overlay = OverlayWindow(self.config, translate_current, hide_current)
        overlay.setGeometry(rect)
        self.overlays.append(overlay)
        overlay.show()
        overlay.raise_()
        overlay.activateWindow()
        self.config = self._config_with_overlay_state(overlay)
        save_config(self.config_path, self.config)

    def selection_cancelled(self) -> None:
        self.selection_window = None

    def hide_overlay(self, overlay: OverlayWindow) -> None:
        self.config = self._config_with_overlay_state(overlay)
        save_config(self.config_path, self.config)
        overlay.hide()
        if overlay in self.overlays:
            self.overlays.remove(overlay)
        overlay.deleteLater()

    def translate_overlay(self, overlay: OverlayWindow) -> None:
        threading.Thread(target=self._translate_overlay_job, args=(overlay,), daemon=True).start()

    def _translate_overlay_job(self, overlay: OverlayWindow) -> None:
        try:
            overlay_rect = overlay.overlay_rect()
            source_language = overlay.source_language()
            target_language = overlay.target_language()
            capture_area = content_capture_rect(overlay_rect, 0)
            image = capture_rect(capture_area)
            with self.ocr_lock:
                ocr_results = read_text(image)
            if overlay not in self.overlays:
                return
            if not ocr_results:
                self.bridge.status_ready.emit(overlay, "No text found")
                return

            translated_texts = translate_texts(
                [result.text for result in ocr_results],
                target_language=target_language,
                source_language=source_language,
            )
            if overlay not in self.overlays:
                return
            boxes = [
                TranslatedBox(
                    original=result.text,
                    translated=translated,
                    bbox=translate_capture_bbox_to_overlay(result.bbox, 0, 0),
                    font_size=font_size_for_bbox(result.bbox),
                )
                for result, translated in zip(ocr_results, translated_texts, strict=True)
            ]
            self.bridge.boxes_ready.emit(overlay, boxes)
        except TranslationError as exc:
            if overlay in self.overlays:
                self.bridge.status_ready.emit(overlay, f"Translation failed: {exc}")
        except Exception as exc:
            if overlay in self.overlays:
                self.bridge.status_ready.emit(overlay, f"ViTrans failed: {exc}")

    def _config_with_overlay_state(self, overlay: OverlayWindow) -> AppConfig:
        geometry = overlay.geometry()
        return AppConfig(
            x=geometry.x(),
            y=geometry.y(),
            width=geometry.width(),
            height=geometry.height(),
            target_language=overlay.target_language(),
            source_language=overlay.source_language(),
            overlay_color=self.config.overlay_color,
            hotkey_modifier=self.config.hotkey_modifier,
            hotkey_key=self.config.hotkey_key,
            run_as_admin=self.config.run_as_admin,
            start_with_windows=self.config.start_with_windows,
        )

    def quit(self) -> None:
        if self.overlays:
            self.config = self._config_with_overlay_state(self.overlays[-1])
            save_config(self.config_path, self.config)
        self.hotkey_manager.stop()
        self.tray.hide()
        self.qt_app.quit()


def main() -> int:
    app = ViTransApp()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
