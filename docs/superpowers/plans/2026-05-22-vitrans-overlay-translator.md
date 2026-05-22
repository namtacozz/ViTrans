# ViTrans Overlay Translator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows Python MVP that toggles a transparent overlay with `Alt+T`, captures selected screen text, OCRs it locally, translates it to Vietnamese online, and paints translations in place.

**Architecture:** Use small Python modules with clear boundaries: config persistence, data models, capture geometry, OCR wrapper, translation wrapper, PyQt overlay, and app entrypoint. Tests cover deterministic logic first; GUI/OCR/translation behavior gets manual validation because it depends on Windows desktop, model downloads, and network calls.

**Tech Stack:** Python 3.11+, PyQt6, mss, EasyOCR, googletrans, pynput, Pillow, pytest.

---

## File Structure

- `requirements.txt`: runtime and test dependencies.
- `src/vitrans/__init__.py`: package marker.
- `src/vitrans/models.py`: dataclasses for rectangles, OCR results, and translated boxes.
- `src/vitrans/config.py`: JSON config load/save with defaults.
- `src/vitrans/geometry.py`: coordinate transforms between capture image and overlay content area.
- `src/vitrans/capture.py`: MSS screenshot for selected overlay content area.
- `src/vitrans/ocr.py`: EasyOCR singleton wrapper.
- `src/vitrans/translate.py`: googletrans wrapper targeting Vietnamese.
- `src/vitrans/overlay.py`: PyQt6 overlay window, controls, resize/move behavior, translation painting.
- `src/vitrans/main.py`: Qt app, tray menu, global hotkey wiring.
- `tests/test_config.py`: config persistence tests.
- `tests/test_geometry.py`: bbox transform tests.
- `README.md`: run instructions and manual test checklist.

## Task 1: Project Skeleton and Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `src/vitrans/__init__.py`
- Create: `src/vitrans/models.py`
- Create: `tests/test_geometry.py`

- [ ] **Step 1: Create dependency file**

Create `requirements.txt`:

```txt
PyQt6==6.7.1
mss==9.0.1
easyocr==1.7.2
googletrans==4.0.0rc1
pynput==1.7.7
Pillow==10.4.0
pytest==8.3.2
```

- [ ] **Step 2: Create package marker**

Create `src/vitrans/__init__.py`:

```python
__all__ = []
```

- [ ] **Step 3: Create data models**

Create `src/vitrans/models.py`:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class OcrResult:
    text: str
    confidence: float
    bbox: Rect


@dataclass(frozen=True)
class TranslatedBox:
    original: str
    translated: str
    bbox: Rect
```

- [ ] **Step 4: Write failing geometry import test**

Create `tests/test_geometry.py`:

```python
from vitrans.models import Rect
from vitrans.geometry import translate_capture_bbox_to_overlay


def test_translate_capture_bbox_to_overlay_offsets_by_content_origin():
    bbox = Rect(x=10, y=20, width=100, height=30)
    result = translate_capture_bbox_to_overlay(bbox, content_origin_x=5, content_origin_y=40)
    assert result == Rect(x=15, y=60, width=100, height=30)
```

- [ ] **Step 5: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_geometry.py::test_translate_capture_bbox_to_overlay_offsets_by_content_origin -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vitrans.geometry'`.

- [ ] **Step 6: Commit**

If repository is initialized, run:

```bash
git add requirements.txt src/vitrans/__init__.py src/vitrans/models.py tests/test_geometry.py
git commit -m "chore: add project skeleton"
```

If repository is not initialized, skip commit and note: `Skipped commit: not a git repository`.

## Task 2: Geometry Transform

**Files:**
- Create: `src/vitrans/geometry.py`
- Modify: `tests/test_geometry.py`

- [ ] **Step 1: Extend failing geometry tests**

Replace `tests/test_geometry.py` with:

```python
from vitrans.models import Rect
from vitrans.geometry import content_capture_rect, translate_capture_bbox_to_overlay


def test_translate_capture_bbox_to_overlay_offsets_by_content_origin():
    bbox = Rect(x=10, y=20, width=100, height=30)
    result = translate_capture_bbox_to_overlay(bbox, content_origin_x=5, content_origin_y=40)
    assert result == Rect(x=15, y=60, width=100, height=30)


def test_content_capture_rect_excludes_top_bar():
    overlay = Rect(x=100, y=200, width=500, height=300)
    result = content_capture_rect(overlay, top_bar_height=36)
    assert result == Rect(x=100, y=236, width=500, height=264)


def test_content_capture_rect_never_returns_negative_height():
    overlay = Rect(x=100, y=200, width=500, height=20)
    result = content_capture_rect(overlay, top_bar_height=36)
    assert result == Rect(x=100, y=236, width=500, height=1)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
python -m pytest tests/test_geometry.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vitrans.geometry'` or missing functions.

- [ ] **Step 3: Implement geometry module**

Create `src/vitrans/geometry.py`:

```python
from vitrans.models import Rect


def translate_capture_bbox_to_overlay(bbox: Rect, content_origin_x: int, content_origin_y: int) -> Rect:
    return Rect(
        x=bbox.x + content_origin_x,
        y=bbox.y + content_origin_y,
        width=bbox.width,
        height=bbox.height,
    )


def content_capture_rect(overlay_rect: Rect, top_bar_height: int) -> Rect:
    return Rect(
        x=overlay_rect.x,
        y=overlay_rect.y + top_bar_height,
        width=overlay_rect.width,
        height=max(1, overlay_rect.height - top_bar_height),
    )
```

- [ ] **Step 4: Run tests to verify pass**

Run:

```bash
python -m pytest tests/test_geometry.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

If repository is initialized, run:

```bash
git add src/vitrans/geometry.py tests/test_geometry.py
git commit -m "feat: add overlay geometry helpers"
```

If repository is not initialized, skip commit and note: `Skipped commit: not a git repository`.

## Task 3: Config Persistence

**Files:**
- Create: `src/vitrans/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing config tests**

Create `tests/test_config.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
python -m pytest tests/test_config.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vitrans.config'`.

- [ ] **Step 3: Implement config module**

Create `src/vitrans/config.py`:

```python
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    x: int = 200
    y: int = 160
    width: int = 640
    height: int = 360
    target_language: str = "vi"


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
```

- [ ] **Step 4: Run tests to verify pass**

Run:

```bash
python -m pytest tests/test_config.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Run all deterministic tests**

Run:

```bash
python -m pytest tests -v
```

Expected: 6 passed.

- [ ] **Step 6: Commit**

If repository is initialized, run:

```bash
git add src/vitrans/config.py tests/test_config.py
git commit -m "feat: add config persistence"
```

If repository is not initialized, skip commit and note: `Skipped commit: not a git repository`.

## Task 4: Screen Capture

**Files:**
- Create: `src/vitrans/capture.py`

- [ ] **Step 1: Implement capture module**

Create `src/vitrans/capture.py`:

```python
from PIL import Image
from mss import mss

from vitrans.models import Rect


def capture_rect(rect: Rect) -> Image.Image:
    monitor = {
        "left": rect.x,
        "top": rect.y,
        "width": rect.width,
        "height": rect.height,
    }
    with mss() as screen_capture:
        screenshot = screen_capture.grab(monitor)
    return Image.frombytes("RGB", screenshot.size, screenshot.rgb)
```

- [ ] **Step 2: Run import check**

Run:

```bash
python -c "from vitrans.capture import capture_rect; print(capture_rect.__name__)"
```

Expected: prints `capture_rect`.

- [ ] **Step 3: Commit**

If repository is initialized, run:

```bash
git add src/vitrans/capture.py
git commit -m "feat: add screen capture helper"
```

If repository is not initialized, skip commit and note: `Skipped commit: not a git repository`.

## Task 5: OCR Wrapper

**Files:**
- Create: `src/vitrans/ocr.py`

- [ ] **Step 1: Implement OCR module**

Create `src/vitrans/ocr.py`:

```python
from functools import lru_cache

import easyocr
import numpy as np
from PIL import Image

from vitrans.models import OcrResult, Rect


@lru_cache(maxsize=1)
def get_reader() -> easyocr.Reader:
    return easyocr.Reader(["en"], gpu=False)


def _bbox_to_rect(points: list[list[float]]) -> Rect:
    xs = [int(point[0]) for point in points]
    ys = [int(point[1]) for point in points]
    min_x = min(xs)
    min_y = min(ys)
    return Rect(x=min_x, y=min_y, width=max(xs) - min_x, height=max(ys) - min_y)


def read_text(image: Image.Image, min_confidence: float = 0.35) -> list[OcrResult]:
    reader = get_reader()
    raw_results = reader.readtext(np.array(image))
    results: list[OcrResult] = []
    for points, text, confidence in raw_results:
        clean_text = text.strip()
        if not clean_text or confidence < min_confidence:
            continue
        results.append(OcrResult(text=clean_text, confidence=float(confidence), bbox=_bbox_to_rect(points)))
    return results
```

- [ ] **Step 2: Run import check without initializing model**

Run:

```bash
python -c "from vitrans.ocr import read_text; print(read_text.__name__)"
```

Expected: prints `read_text`.

- [ ] **Step 3: Commit**

If repository is initialized, run:

```bash
git add src/vitrans/ocr.py
git commit -m "feat: add easyocr wrapper"
```

If repository is not initialized, skip commit and note: `Skipped commit: not a git repository`.

## Task 6: Translation Wrapper

**Files:**
- Create: `src/vitrans/translate.py`

- [ ] **Step 1: Implement translation module**

Create `src/vitrans/translate.py`:

```python
import time

from googletrans import Translator


class TranslationError(RuntimeError):
    pass


def translate_texts(texts: list[str], target_language: str = "vi", attempts: int = 2) -> list[str]:
    if not texts:
        return []

    translator = Translator()
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            translations = translator.translate(texts, dest=target_language)
            if not isinstance(translations, list):
                translations = [translations]
            return [item.text for item in translations]
        except Exception as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(0.5)

    raise TranslationError(str(last_error))
```

- [ ] **Step 2: Run import check**

Run:

```bash
python -c "from vitrans.translate import translate_texts; print(translate_texts([]))"
```

Expected: prints `[]`.

- [ ] **Step 3: Commit**

If repository is initialized, run:

```bash
git add src/vitrans/translate.py
git commit -m "feat: add google translate wrapper"
```

If repository is not initialized, skip commit and note: `Skipped commit: not a git repository`.

## Task 7: Overlay UI

**Files:**
- Create: `src/vitrans/overlay.py`

- [ ] **Step 1: Implement overlay window**

Create `src/vitrans/overlay.py`:

```python
from collections.abc import Callable

from PyQt6.QtCore import QPoint, QRect, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QSizeGrip, QVBoxLayout, QWidget

from vitrans.config import AppConfig
from vitrans.models import Rect, TranslatedBox

TOP_BAR_HEIGHT = 36


class OverlayWindow(QWidget):
    def __init__(self, config: AppConfig, on_translate: Callable[[], None], on_hide: Callable[[], None]):
        super().__init__()
        self._on_translate = on_translate
        self._on_hide = on_hide
        self._drag_position: QPoint | None = None
        self._translated_boxes: list[TranslatedBox] = []
        self._status = ""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(QSize(240, 140))
        self.setGeometry(config.x, config.y, config.width, config.height)
        self._build_ui(config.target_language)

    def _build_ui(self, target_language: str) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        top_bar = QWidget(self)
        top_bar.setFixedHeight(TOP_BAR_HEIGHT)
        top_bar.setObjectName("topBar")
        top_bar.setStyleSheet("#topBar { background: rgba(20, 20, 20, 210); color: white; }")

        row = QHBoxLayout(top_bar)
        row.setContentsMargins(8, 4, 8, 4)
        row.setSpacing(8)

        self.language_box = QComboBox(top_bar)
        self.language_box.addItem("Vietnamese", "vi")
        self.language_box.setCurrentIndex(0 if target_language == "vi" else 0)
        row.addWidget(self.language_box)

        translate_button = QPushButton("ViTrans", top_bar)
        translate_button.clicked.connect(self._on_translate)
        row.addWidget(translate_button)

        close_button = QPushButton("X", top_bar)
        close_button.setFixedWidth(32)
        close_button.clicked.connect(self._on_hide)
        row.addWidget(close_button)

        root.addWidget(top_bar)

        self.content = QWidget(self)
        self.content.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        root.addWidget(self.content, 1)

        grip = QSizeGrip(self)
        grip.setFixedSize(18, 18)
        row.addWidget(grip)

    def current_config(self) -> AppConfig:
        geometry = self.geometry()
        return AppConfig(
            x=geometry.x(),
            y=geometry.y(),
            width=geometry.width(),
            height=geometry.height(),
            target_language=self.target_language(),
        )

    def target_language(self) -> str:
        return str(self.language_box.currentData())

    def overlay_rect(self) -> Rect:
        geometry = self.geometry()
        return Rect(x=geometry.x(), y=geometry.y(), width=geometry.width(), height=geometry.height())

    def set_translated_boxes(self, boxes: list[TranslatedBox]) -> None:
        self._status = ""
        self._translated_boxes = boxes
        self.update()

    def set_status(self, message: str) -> None:
        self._status = message
        self._translated_boxes = []
        self.update()

    def clear_results(self) -> None:
        self._status = ""
        self._translated_boxes = []
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= TOP_BAR_HEIGHT:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_position is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_position = None
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(40, 120, 220, 45))
        painter.setPen(QColor(80, 180, 255, 180))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        if self._status:
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(QRect(12, TOP_BAR_HEIGHT + 12, self.width() - 24, 60), Qt.AlignmentFlag.AlignLeft, self._status)

        painter.setFont(QFont("Segoe UI", 10))
        for item in self._translated_boxes:
            rect = QRect(item.bbox.x, item.bbox.y, item.bbox.width, max(item.bbox.height, 24))
            painter.fillRect(rect.adjusted(-2, -2, 2, 2), QColor(0, 0, 0, 190))
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap, item.translated)
```

- [ ] **Step 2: Run import check**

Run:

```bash
python -c "from vitrans.overlay import OverlayWindow, TOP_BAR_HEIGHT; print(TOP_BAR_HEIGHT)"
```

Expected: prints `36`.

- [ ] **Step 3: Commit**

If repository is initialized, run:

```bash
git add src/vitrans/overlay.py
git commit -m "feat: add transparent overlay window"
```

If repository is not initialized, skip commit and note: `Skipped commit: not a git repository`.

## Task 8: App Orchestration and Hotkey

**Files:**
- Create: `src/vitrans/main.py`

- [ ] **Step 1: Implement main app**

Create `src/vitrans/main.py`:

```python
import sys
from collections.abc import Callable

from pynput import keyboard
from PyQt6.QtCore import QMetaObject, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from vitrans.capture import capture_rect
from vitrans.config import AppConfig, default_config_path, load_config, save_config
from vitrans.geometry import content_capture_rect, translate_capture_bbox_to_overlay
from vitrans.models import TranslatedBox
from vitrans.ocr import read_text
from vitrans.overlay import OverlayWindow, TOP_BAR_HEIGHT
from vitrans.translate import TranslationError, translate_texts


class ViTransApp:
    def __init__(self):
        self.config_path = default_config_path()
        self.config = load_config(self.config_path)
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setQuitOnLastWindowClosed(False)
        self.overlay = OverlayWindow(self.config, self.translate_selection, self.hide_overlay)
        self.tray = self._create_tray()
        self.hotkey_listener = keyboard.GlobalHotKeys({"<alt>+t": self.toggle_overlay_threadsafe})

    def _create_tray(self) -> QSystemTrayIcon:
        tray = QSystemTrayIcon(self.qt_app)
        tray.setToolTip("ViTrans")
        menu = QMenu()

        show_hide = QAction("Show/Hide")
        show_hide.triggered.connect(self.toggle_overlay)
        menu.addAction(show_hide)

        quit_action = QAction("Quit")
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)

        tray.setContextMenu(menu)
        tray.show()
        return tray

    def run(self) -> int:
        self.hotkey_listener.start()
        return self.qt_app.exec()

    def invoke_on_ui(self, callback: Callable[[], None]) -> None:
        QMetaObject.invokeMethod(self.overlay, callback, Qt.ConnectionType.QueuedConnection)

    def toggle_overlay_threadsafe(self) -> None:
        self.invoke_on_ui(self.toggle_overlay)

    def toggle_overlay(self) -> None:
        if self.overlay.isVisible():
            self.hide_overlay()
        else:
            self.overlay.show()
            self.overlay.raise_()
            self.overlay.activateWindow()

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
```

- [ ] **Step 2: Run import check**

Run:

```bash
python -c "from vitrans.main import ViTransApp; print(ViTransApp.__name__)"
```

Expected: prints `ViTransApp`.

- [ ] **Step 3: Commit**

If repository is initialized, run:

```bash
git add src/vitrans/main.py
git commit -m "feat: wire app hotkey and tray"
```

If repository is not initialized, skip commit and note: `Skipped commit: not a git repository`.

## Task 9: Run Instructions and Manual Validation

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README**

Create `README.md`:

```markdown
# ViTrans

Windows Python MVP for translating text inside a screen overlay.

## Setup

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
```

If imports from `src/` fail in your shell, run commands with:

```bash
PYTHONPATH=src python -m vitrans.main
```

## Run

```bash
PYTHONPATH=src python -m vitrans.main
```

First OCR run may download EasyOCR models.

## Use

- Press `Alt+T` to show or hide overlay.
- Move overlay by dragging top bar.
- Resize overlay from bottom-right grip.
- Put overlay around text in another app.
- Click `ViTrans`.
- Translated Vietnamese text appears over detected text.
- Click `X` to hide overlay.
- Use tray menu `Quit` to exit.

## Test

```bash
PYTHONPATH=src python -m pytest tests -v
```

## Manual validation checklist

- `Alt+T` toggles overlay.
- Overlay stays above other apps.
- Overlay moves and resizes.
- `X` hides overlay while app stays in tray.
- Tray `Show/Hide` works.
- Tray `Quit` exits app.
- Capture works over another app.
- English text inside overlay is OCR'd and translated to Vietnamese.
- Translation appears near original text positions with readable background blocks.
- Network translation failure shows an error instead of crashing.
```

- [ ] **Step 2: Run deterministic tests**

Run:

```bash
PYTHONPATH=src python -m pytest tests -v
```

Expected: all tests pass.

- [ ] **Step 3: Launch app manually**

Run:

```bash
PYTHONPATH=src python -m vitrans.main
```

Expected: app starts, tray icon appears, `Alt+T` toggles overlay.

- [ ] **Step 4: Manual translation test**

Open any app or browser page with English text. Press `Alt+T`, resize overlay around text, click `ViTrans`.

Expected: Vietnamese text appears over detected text. First run may pause while EasyOCR downloads models.

- [ ] **Step 5: Commit**

If repository is initialized, run:

```bash
git add README.md
git commit -m "docs: add run instructions"
```

If repository is not initialized, skip commit and note: `Skipped commit: not a git repository`.

## Self-Review

Spec coverage:

- Background app: Task 8 creates tray app and keeps Qt running after overlay hide.
- `Alt+T`: Task 8 registers global hotkey.
- Semi-transparent always-on-top resizable overlay: Task 7 implements PyQt6 window flags, translucent background, and size grip.
- Top controls: Task 7 adds Vietnamese selector, `ViTrans`, and `X`.
- Capture selected area: Task 4 and Task 8 capture content rect excluding top bar.
- OCR: Task 5 wraps EasyOCR.
- Auto-detect translation to Vietnamese: Task 6 uses googletrans destination `vi` without source language.
- Paint translation at same positions: Task 7 paints translated boxes; Task 8 maps OCR bboxes to overlay coordinates.
- Config persistence: Task 3 and Task 8 save/load geometry and language.
- Tests: Tasks 2 and 3 cover geometry and config; Task 9 covers manual validation.

Placeholder scan:

- No `TBD`, `TODO`, `implement later`, or unspecified test steps remain.

Type consistency:

- `Rect`, `OcrResult`, and `TranslatedBox` names match across tasks.
- `content_capture_rect` and `translate_capture_bbox_to_overlay` signatures match tests and orchestration.
- `AppConfig` fields match overlay and config tests.
