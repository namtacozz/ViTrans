# ViTrans Multi Overlay Controls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let users create multiple independent translation overlay boxes, each with center app icon translation trigger and right-click source/target/close controls.

**Architecture:** `ViTransApp` owns multiple `OverlayWindow` instances instead of one singleton overlay. Each `OverlayWindow` keeps per-box source/target state, shows center icon until translation runs, resets translation when moved/resized, and exposes right-click menu for source/target/close.

**Tech Stack:** Python 3.12, PyQt6, pynput, mss, EasyOCR, deep-translator, pytest, PyInstaller.

---

## File Structure

- `src/vitrans/overlay.py`: per-box UI state, icon button, right-click menu, move/resize reset behavior.
- `src/vitrans/main.py`: list of overlays, selection always creates new overlay, per-box translate/hide callbacks.
- `src/vitrans/geometry.py`: reuse existing `content_capture_rect()` and `translate_capture_bbox_to_overlay()` with top bar offset removed.
- `tests/test_geometry.py`: adjust/add tests for zero top-bar offset if needed.
- `README.md`: update usage/manual test checklist for multi-box overlays.

## Task 1: Convert OverlayWindow to Minimal Per-Box UI

**Files:**
- Modify: `src/vitrans/overlay.py`

- [ ] **Step 1: Replace top-bar controls with center icon button**

In `OverlayWindow._build_ui`, remove top bar, language combo, `ViTrans` button, and `X` button. Create one centered `QPushButton` with logo icon. Connect it to `self._on_translate`. Keep transparent content area. Add `self.translate_button` so later methods can hide/show it.

- [ ] **Step 2: Add per-box language state**

In `__init__`, set:

```python
self._source_language = config.source_language
self._target_language = config.target_language
```

Change `target_language()` to return `self._target_language`. Add `source_language()` returning `self._source_language`.

- [ ] **Step 3: Add right-click menu**

Add `contextMenuEvent()` creating a `QMenu` with:
- `Nguồn` submenu: auto/en/vi/ja/ko/zh-CN/fr/de
- `Đích` submenu: vi/en/ja/ko/zh-CN/fr/de
- separator
- `Tắt` action calling `self._on_hide`

When source or target changes, update state and call reset method.

- [ ] **Step 4: Reset output when box changes**

Add `_reset_translation_ui()`:

```python
self._status = ""
self._translated_boxes = []
self.translate_button.show()
self.update()
```

Call it after resize and after move completes. Do not call during every mouse move.

- [ ] **Step 5: Hide icon after translation starts/succeeds**

Add `mark_translating()` or hide button in translate callback path before OCR. `set_translated_boxes()` should hide icon. `set_status()` should show icon again only if user needs retry.

## Task 2: Manage Multiple Overlays in App

**Files:**
- Modify: `src/vitrans/main.py`

- [ ] **Step 1: Replace singleton overlay with list**

Change:

```python
self.overlay = OverlayWindow(...)
```

to:

```python
self.overlays: list[OverlayWindow] = []
```

- [ ] **Step 2: Make Alt+T always start selection**

Change `toggle_overlay()` so visible overlays do not hide. If selection is open, close it; otherwise start new selection.

- [ ] **Step 3: Create overlay per selection**

In `selection_selected()`, create new `OverlayWindow` for selected rect. Use closure callbacks:

```python
overlay = OverlayWindow(self.config, lambda: self.translate_overlay(overlay), lambda: self.hide_overlay(overlay))
```

Set geometry, append to `self.overlays`, show/raise.

- [ ] **Step 4: Change translation to accept overlay**

Rename `translate_selection()` to `translate_overlay(self, overlay: OverlayWindow)`. Use `overlay.overlay_rect()`, `overlay.source_language()`, and `overlay.target_language()`.

- [ ] **Step 5: Change hide to accept overlay**

`hide_overlay(self, overlay)` hides overlay and removes it from `self.overlays` if present.

- [ ] **Step 6: Save last geometry safely**

On quit, if overlays exist, save geometry from last overlay. If none exist, save existing app config unchanged.

## Task 3: Update Capture Geometry for No Top Bar

**Files:**
- Modify: `src/vitrans/main.py`
- Modify: `src/vitrans/overlay.py`

- [ ] **Step 1: Set content offset to zero**

Use:

```python
capture_area = content_capture_rect(overlay_rect, 0)
```

and:

```python
bbox=translate_capture_bbox_to_overlay(result.bbox, 0, 0)
```

- [ ] **Step 2: Update status text location**

In `paintEvent`, draw status from `QRect(12, 12, self.width() - 24, 60)` instead of using `TOP_BAR_HEIGHT`.

## Task 4: Update README Manual Behavior

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update use section**

Document:
- `Alt+T` creates a new selection/overlay box.
- Overlay is translucent rectangle.
- Center app icon starts translation and then hides.
- Resize/move clears current translation and shows icon again.
- Right-click overlay changes source/target or closes that box.
- Multiple boxes can exist at once.

## Task 5: Verify and Rebuild

**Files:**
- Build output: `dist/ViTrans/ViTrans.exe`

- [ ] **Step 1: Run tests**

Run:

```bash
PYTHONPATH=src ./.venv312/Scripts/python.exe -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Rebuild executable**

Run:

```bash
./.venv312/Scripts/python.exe scripts/build_windows.py
```

Expected: PyInstaller completes and writes `dist/ViTrans/ViTrans.exe`.

- [ ] **Step 3: Manual test**

Run `dist/ViTrans/ViTrans.exe` and verify:
- Double-click tray icon opens Settings.
- `Alt+T` creates first overlay.
- Center icon translates and hides.
- `Alt+T` creates second overlay without closing first.
- Right-click first overlay can change target and close only first overlay.
- Resize/move overlay clears result and shows icon again.

## Self-Review

- Spec coverage: multi overlays, center icon trigger, right-click source/target/close, resize reset, future style extension path covered.
- Placeholder scan: no TBD/TODO placeholders.
- Type consistency: `source_language()`, `target_language()`, `translate_overlay()`, `hide_overlay()` names consistent.
