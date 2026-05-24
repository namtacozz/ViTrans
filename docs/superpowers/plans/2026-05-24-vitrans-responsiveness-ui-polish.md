# ViTrans Responsiveness and UI Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ViTrans start faster, allow small overlay boxes, keep UI responsive during translation, document project context, and clean up Settings UI.

**Architecture:** Delay OCR warm-up after Qt startup, run each overlay translation in a background job, guard OCR with a single lock, and update PyQt widgets through signals only. Overlay windows remain independent and small; Settings UI keeps existing controls but removes duplicate header content and tightens layout.

**Tech Stack:** Python 3.12, PyQt6 signals/threads, threading, EasyOCR, deep-translator, pytest, PyInstaller.

---

## File Structure

- `src/vitrans/main.py`: delayed OCR warm-up, background translation jobs, OCR lock, UI signal bridge.
- `src/vitrans/overlay.py`: lower minimum overlay size and icon sizing that does not force large boxes.
- `src/vitrans/settings.py`: remove custom title header, tighten layout, keep groups inside dialog.
- `CLAUDE.md`: project-specific context and commands for future sessions.
- `README.md`: update startup/concurrency/small overlay behavior.

## Task 1: Delay OCR Warm-Up After Startup

**Files:**
- Modify: `src/vitrans/main.py`

- [ ] **Step 1: Add delayed warm-up helper**

Replace direct warm-up thread start in `ViTransApp.__init__` with `QTimer.singleShot(3000, self._start_ocr_warmup)`.

Add import:

```python
from PyQt6.QtCore import QObject, QRect, QTimer, pyqtSignal
```

Add method:

```python
def _start_ocr_warmup(self) -> None:
    threading.Thread(target=warm_up_reader, daemon=True).start()
```

- [ ] **Step 2: Verify startup path imports**

Run:

```bash
PYTHONPATH=src ./.venv312/Scripts/python.exe -m pytest tests/test_hotkey.py tests/test_config.py -q
```

Expected: tests pass.

## Task 2: Allow Small Overlay Boxes

**Files:**
- Modify: `src/vitrans/overlay.py`

- [ ] **Step 1: Lower minimum size**

Change:

```python
self.setMinimumSize(QSize(240, 140))
```

to:

```python
self.setMinimumSize(QSize(32, 24))
```

- [ ] **Step 2: Prevent center icon from forcing layout size**

Keep `translate_button` fixed size at `32x32`; icon size `22x22`. Override `resizeEvent()` to hide icon when `self.width() < 40 or self.height() < 40`, unless translated boxes/status already exist. Show it again when box grows and no result exists.

- [ ] **Step 3: Verify resize math still obeys minimum**

Run:

```bash
PYTHONPATH=src ./.venv312/Scripts/python.exe -m pytest -q
```

Expected: tests pass.

## Task 3: Run Translation Jobs Without Blocking UI

**Files:**
- Modify: `src/vitrans/main.py`

- [ ] **Step 1: Extend UiBridge signals**

Change `UiBridge` to include:

```python
class UiBridge(QObject):
    toggle_requested = pyqtSignal()
    boxes_ready = pyqtSignal(object, list)
    status_ready = pyqtSignal(object, str)
```

Connect in `__init__`:

```python
self.bridge.boxes_ready.connect(lambda overlay, boxes: overlay.set_translated_boxes(boxes))
self.bridge.status_ready.connect(lambda overlay, message: overlay.set_status(message))
self.ocr_lock = threading.Lock()
```

- [ ] **Step 2: Make translate_overlay spawn a thread**

Change `translate_overlay(self, overlay)` to:

```python
def translate_overlay(self, overlay: OverlayWindow) -> None:
    threading.Thread(target=self._translate_overlay_job, args=(overlay,), daemon=True).start()
```

- [ ] **Step 3: Move current translation body to worker job**

Add `_translate_overlay_job(self, overlay: OverlayWindow)`. Inside it:
- capture image immediately for that overlay.
- guard `read_text(image)` with `with self.ocr_lock:`.
- run `translate_texts(...)` outside the lock.
- emit `boxes_ready` or `status_ready` instead of calling overlay methods directly.

- [ ] **Step 4: Ignore updates for closed overlays**

Before emitting success/status, check `if overlay not in self.overlays: return`.

- [ ] **Step 5: Verify UI-thread signal path imports**

Run:

```bash
PYTHONPATH=src ./.venv312/Scripts/python.exe -m pytest -q
```

Expected: tests pass.

## Task 4: Add Project CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Write project instructions**

Create `CLAUDE.md`:

```markdown
# ViTrans project context

ViTrans is a Windows desktop overlay translator. It uses PyQt6 for UI, EasyOCR for local OCR, deep-translator for Google Translate, pynput for global hotkeys, and PyInstaller for Windows packaging.

## Commands

Use Python 3.12 environment `.venv312`; `.venv` may point to Python 3.14 and cannot install pinned `torch==2.5.1`.

```bash
PYTHONPATH=src ./.venv312/Scripts/python.exe -m pytest -q
./.venv312/Scripts/python.exe scripts/build_windows.py
./dist/ViTrans/ViTrans.exe
```

## Current behavior

- Double-click tray icon opens Settings.
- Right-click tray icon is intentionally unused.
- `Alt+T` opens selection mode and creates a new overlay box; existing boxes stay visible.
- Each overlay box has a center app icon. Clicking it translates that box and hides the icon.
- Moving or resizing a box clears its translation and shows the icon again.
- Right-click an overlay box to choose source language, target language, or close only that box.
- OCR should run one job at a time; translation can run outside the OCR lock.

## Build notes

Build output lives at `dist/ViTrans/ViTrans.exe`. PyInstaller warnings about optional TensorBoard or SciPy hidden imports may appear; verify runtime behavior before changing dependency pins.
```
```

## Task 5: Clean Settings UI

**Files:**
- Modify: `src/vitrans/settings.py`

- [ ] **Step 1: Remove duplicate custom header**

Remove title bar widget code from `_build_ui()` that creates logo, `ViTrans`, and version labels. Keep native Windows title bar from `setWindowTitle()`.

- [ ] **Step 2: Tighten dialog geometry**

Change fixed size from `420x520` to `420x430`. Change main content margins to `16, 12, 16, 12`.

- [ ] **Step 3: Remove unused title stylesheet selectors**

Remove `QWidget#titleBar`, `QLabel#titleLabel`, and `QLabel#versionLabel` rules if unused.

- [ ] **Step 4: Verify settings imports**

Run:

```bash
PYTHONPATH=src ./.venv312/Scripts/python.exe -m pytest -q
```

Expected: tests pass.

## Task 6: Update README and Rebuild

**Files:**
- Modify: `README.md`
- Build output: `dist/ViTrans/ViTrans.exe`

- [ ] **Step 1: Update README**

Document:
- App starts UI before delayed OCR warm-up.
- OCR runs one job at a time; other overlay selection remains usable.
- Overlay boxes can be very small.

- [ ] **Step 2: Run all tests**

Run:

```bash
PYTHONPATH=src ./.venv312/Scripts/python.exe -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 3: Rebuild executable**

Run:

```bash
./.venv312/Scripts/python.exe scripts/build_windows.py
```

Expected: PyInstaller completes and writes `dist/ViTrans/ViTrans.exe`.

- [ ] **Step 4: Manual validation**

Run `dist/ViTrans/ViTrans.exe` and verify:
- Tray icon appears before OCR warm-up finishes.
- `Alt+T` can create new box while another box is translating.
- A one-word selection creates a small box and does not inflate.
- Center icon does not protrude from small boxes.
- Settings dialog has no custom top logo/version header and controls fit inside.

## Self-Review

- Spec coverage: startup delay, small overlays, non-blocking overlay creation, OCR queue, project CLAUDE.md, Settings UI cleanup all mapped to tasks.
- Placeholder scan: no TBD/TODO placeholders.
- Type consistency: `boxes_ready`, `status_ready`, `_translate_overlay_job`, `ocr_lock`, and overlay methods match planned usage.
