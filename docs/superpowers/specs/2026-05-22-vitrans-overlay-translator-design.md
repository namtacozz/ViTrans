# ViTrans Overlay Translator Design

## Goal

Build a Windows 10/11 Python MVP for live on-screen translation. App runs in background. `Alt+T` toggles a semi-transparent always-on-top overlay. User resizes overlay around screen text, clicks `ViTrans`, and app translates detected text to Vietnamese in place.

## Scope

MVP includes:

- Windows-only desktop app.
- Python script/virtualenv workflow, not packaged `.exe`.
- PyQt6 overlay UI.
- Local OCR with EasyOCR.
- Online translation with unofficial Google Translate via `googletrans`.
- Auto-detected source language.
- Vietnamese target language.
- Local config persistence for overlay position, size, and target language.

Out of scope for MVP:

- `.exe` packaging.
- macOS/Linux support.
- Paid translation APIs.
- Offline translation engine.
- Multi-target-language UX beyond stored target field.

## Architecture

### `main.py`

Entrypoint. Creates Qt app, loads config, creates overlay window, registers global hotkey, and starts system tray integration. Keeps app running after overlay closes.

### `overlay.py`

Owns PyQt6 overlay window. Window is frameless, always-on-top, semi-transparent, movable, and freely resizable. Top bar contains:

- target language selector/display set to `Vietnamese`
- `ViTrans` button
- `X` button

`X` hides overlay instead of quitting app. Overlay paints translated result boxes over original text locations.

### `capture.py`

Captures screen pixels inside overlay rectangle using MSS. Capture excludes top control bar, so OCR scans user-selected content area only.

### `ocr.py`

Wraps EasyOCR reader as a singleton. Returns recognized text, confidence, and bounding boxes relative to captured image.

### `translate.py`

Wraps `googletrans`. Uses source auto-detection and target code `vi`. Translates OCR text entries, with small retry behavior for transient network/library failures.

### `config.py`

Reads and writes JSON config for overlay geometry and target language.

### `models.py`

Defines dataclasses for OCR results and translated boxes. Shared shape keeps module boundaries clear.

## Data Flow

1. App starts.
2. Config loads.
3. Tray and hidden overlay initialize.
4. `Alt+T` shows or hides overlay.
5. User moves/resizes overlay around content.
6. User clicks `ViTrans`.
7. Overlay clears previous results and requests capture of content area.
8. OCR detects text boxes.
9. Low-confidence or empty text boxes are filtered.
10. Text is translated to Vietnamese.
11. Overlay maps image-space boxes back to overlay coordinates.
12. Overlay draws semi-transparent background blocks over original text and paints Vietnamese text in same positions.

## UI Behavior

- Overlay remains above other apps.
- Overlay background is transparent enough to see selected content underneath.
- Top bar remains readable and easy to click.
- Translated text blocks use semi-transparent fill to improve readability while preserving context.
- `Alt+T` toggles overlay visibility.
- Tray menu provides `Show/Hide` and `Quit`.
- `Quit` exits app and saves config.

## Error Handling

- OCR/model initialization or download failure shows short status message on overlay and does not crash app.
- Translation/network failure shows short status message on overlay and does not crash app.
- No detected text shows `No text found`.
- Low-confidence OCR entries are skipped.

## Testing

Automated tests:

- Config read/write defaults and persistence.
- Bounding-box coordinate transform from captured image to overlay coordinates.

Manual MVP validation:

- `Alt+T` toggles overlay.
- Overlay moves and resizes on Windows.
- `X` hides overlay while app stays in tray.
- Tray `Show/Hide` works.
- Tray `Quit` exits app.
- Capture works over another app.
- English text inside overlay is OCR'd and translated to Vietnamese.
- Translation appears at corresponding text positions with readable background blocks.
- Network translation failure shows an error instead of crashing.
