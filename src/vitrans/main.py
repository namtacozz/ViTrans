import sys
import threading
from pathlib import Path

from vitrans.encoding import configure_utf8_stdio

configure_utf8_stdio()

from pynput import keyboard
from PyQt6.QtCore import QObject, QRect, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from vitrans.capture import capture_rect
from vitrans.config import default_config_path, load_config, save_config
from vitrans.geometry import content_capture_rect, font_size_for_bbox, translate_capture_bbox_to_overlay
from vitrans.models import TranslatedBox
from vitrans.ocr import read_text, warm_up_reader
from vitrans.overlay import TOP_BAR_HEIGHT, OverlayWindow
from vitrans.selection import SelectionWindow
from vitrans.translate import TranslationError, translate_texts


class UiBridge(QObject):
    toggle_requested = pyqtSignal()


class ViTransApp:
    def __init__(self):
        self.config_path = default_config_path()
        self.config = load_config(self.config_path)
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setQuitOnLastWindowClosed(False)
        self.bridge = UiBridge()
        self.overlay = OverlayWindow(self.config, self.translate_selection, self.hide_overlay)
        self.selection_window: SelectionWindow | None = None
        self.tray = self._create_tray()
        self.bridge.toggle_requested.connect(self.toggle_overlay)
        self.hotkey_listener = keyboard.GlobalHotKeys({"<alt>+t": self.toggle_overlay_threadsafe})
        threading.Thread(target=warm_up_reader, daemon=True).start()

    def _create_tray(self) -> QSystemTrayIcon:
        icon_path = Path(__file__).resolve().parents[2] / "assets" / "logo.png"
        tray = QSystemTrayIcon(QIcon(str(icon_path)), self.qt_app)
        tray.setToolTip("ViTrans")
        menu = QMenu()

        open_ui = QAction("Open Ui")
        open_ui.triggered.connect(self.open_ui)
        menu.addAction(open_ui)

        exit_action = QAction("Exit")
        exit_action.triggered.connect(self.quit)
        menu.addAction(exit_action)

        tray.setContextMenu(menu)
        tray.show()
        return tray

    def run(self) -> int:
        self.hotkey_listener.start()
        return self.qt_app.exec()

    def toggle_overlay_threadsafe(self) -> None:
        self.bridge.toggle_requested.emit()

    def open_ui(self) -> None:
        if self.overlay.isVisible():
            self.overlay.raise_()
            self.overlay.activateWindow()
            return
        self.start_selection()

    def toggle_overlay(self) -> None:
        if self.overlay.isVisible():
            self.hide_overlay()
            return
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
        self.overlay.clear_results()
        self.overlay.setGeometry(rect)
        self.overlay.show()
        self.overlay.raise_()
        self.overlay.activateWindow()
        self.config = self.overlay.current_config()
        save_config(self.config_path, self.config)

    def selection_cancelled(self) -> None:
        self.selection_window = None

    def hide_overlay(self) -> None:
        self.config = self.overlay.current_config()
        save_config(self.config_path, self.config)
        self.overlay.hide()

    def translate_selection(self) -> None:
        self.overlay.clear_results()
        try:
            overlay_rect = self.overlay.overlay_rect()
            capture_area = content_capture_rect(overlay_rect, TOP_BAR_HEIGHT)
            image = capture_rect(capture_area)
            ocr_results = read_text(image)
            if not ocr_results:
                self.overlay.set_status("No text found")
                return

            translated_texts = translate_texts([result.text for result in ocr_results], self.overlay.target_language())
            boxes = [
                TranslatedBox(
                    original=result.text,
                    translated=translated,
                    bbox=translate_capture_bbox_to_overlay(result.bbox, 0, TOP_BAR_HEIGHT),
                    font_size=font_size_for_bbox(result.bbox),
                )
                for result, translated in zip(ocr_results, translated_texts, strict=True)
            ]
            self.overlay.set_translated_boxes(boxes)
        except TranslationError as exc:
            self.overlay.set_status(f"Translation failed: {exc}")
        except Exception as exc:
            self.overlay.set_status(f"ViTrans failed: {exc}")

    def quit(self) -> None:
        self.config = self.overlay.current_config()
        save_config(self.config_path, self.config)
        self.hotkey_listener.stop()
        self.tray.hide()
        self.qt_app.quit()


def main() -> int:
    app = ViTransApp()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
