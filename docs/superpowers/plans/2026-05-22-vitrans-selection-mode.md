# ViTrans Selection Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Change `Alt+T` from showing a saved overlay to opening a Windows-snipping-style rectangle picker that creates the overlay from the drag diagonal.

**Architecture:** Add a focused `SelectionWindow` for full-screen selection and keep translation overlay separate. `ViTransApp` owns the flow: when overlay is hidden, `Alt+T` starts selection; when selection completes, app sets overlay geometry and shows it.

**Tech Stack:** Python 3.12, PyQt6, existing ViTrans modules.

---

## File Structure

- `src/vitrans/selection.py`: full-screen selection overlay; emits selected `QRect` or cancel.
- `src/vitrans/main.py`: changes `toggle_overlay` behavior and handles selection result.
- `README.md`: updates usage instructions.

## Task 1: Add Selection Window

**Files:**
- Create: `src/vitrans/selection.py`

- [ ] **Step 1: Create `SelectionWindow`**

```python
from collections.abc import Callable

from PyQt6.QtCore import QPoint, QRect, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QWidget

MIN_SELECTION_WIDTH = 80
MIN_SELECTION_HEIGHT = 60


class SelectionWindow(QWidget):
    def __init__(self, on_selected: Callable[[QRect], None], on_cancelled: Callable[[], None]):
        super().__init__()
        self._on_selected = on_selected
        self._on_cancelled = on_cancelled
        self._start: QPoint | None = None
        self._current: QPoint | None = None
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMouseTracking(True)
        self.setGeometry(QApplication.primaryScreen().geometry())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start = event.globalPosition().toPoint()
            self._current = self._start
            self.update()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._start is not None:
            self._current = event.globalPosition().toPoint()
            self.update()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton or self._start is None:
            return
        self._current = event.globalPosition().toPoint()
        rect = self._selection_rect()
        self.close()
        if rect.width() >= MIN_SELECTION_WIDTH and rect.height() >= MIN_SELECTION_HEIGHT:
            self._on_selected(rect)
        else:
            self._on_cancelled()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            self._on_cancelled()
            event.accept()

    def _selection_rect(self) -> QRect:
        if self._start is None or self._current is None:
            return QRect()
        return QRect(self._start, self._current).normalized()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 70))
        rect = self._selection_rect()
        if rect.isNull():
            return
        painter.fillRect(rect, QColor(40, 120, 220, 35))
        painter.setPen(QPen(QColor(80, 180, 255), 2))
        painter.drawRect(rect.adjusted(0, 0, -1, -1))
```

- [ ] **Step 2: Run import check**

Run: `. .venv312/Scripts/activate && PYTHONPATH=src python -c "from vitrans.selection import SelectionWindow; print(SelectionWindow.__name__)"`
Expected: prints `SelectionWindow`.

## Task 2: Wire `Alt+T` Selection Flow

**Files:**
- Modify: `src/vitrans/main.py`

- [ ] **Step 1: Update imports and app state**

Add `from PyQt6.QtCore import QObject, QRect, pyqtSignal` and `from vitrans.selection import SelectionWindow`.

- [ ] **Step 2: Update toggle behavior**

When overlay visible, hide it. When selection window active, close it. Otherwise create and show `SelectionWindow`.

- [ ] **Step 3: Add selected/cancel handlers**

`_selection_selected(rect: QRect)` sets overlay geometry to `rect`, clears prior results, shows overlay, saves config. `_selection_cancelled()` clears selection reference.

- [ ] **Step 4: Run smoke check**

Run: `. .venv312/Scripts/activate && PYTHONPATH=src python -c "from vitrans.main import ViTransApp; print(ViTransApp.__name__)"`
Expected: prints `ViTransApp`.

## Task 3: Update README and Verify

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update Use section**

Explain `Alt+T` opens full-screen selection, drag to choose rectangle, release to show overlay.

- [ ] **Step 2: Run tests**

Run: `. .venv312/Scripts/activate && PYTHONPATH=src python -m pytest tests -v`
Expected: 6 passed.

- [ ] **Step 3: Manual validation**

Run app, press `Alt+T`, drag rectangle, release, verify overlay appears on selected rectangle.

## Self-Review

Spec coverage: selection window, drag diagonal, release-to-overlay, cancel path, tests/checks covered.
Placeholder scan: no placeholders.
Type consistency: `QRect` selection flows from `SelectionWindow` to `ViTransApp`.
