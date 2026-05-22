# ViTrans Windows App Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package ViTrans as a Windows app-style executable so tray/taskbar and Task Manager show ViTrans name/icon instead of Python.

**Architecture:** Keep existing Python source unchanged for development, add Windows app metadata and a PyInstaller one-folder build path. Runtime uses an AppUserModelID, icon resource, and bundled assets; build output is `dist/ViTrans/ViTrans.exe`.

**Tech Stack:** Python 3.12, PyQt6, PyInstaller, Pillow, Windows Shell AppUserModelID.

---

## File Structure

- `assets/logo.ico`: Windows icon generated from `assets/logo.png`.
- `src/vitrans/resources.py`: resolves resource paths for source and PyInstaller bundle.
- `src/vitrans/main.py`: sets AppUserModelID, app icon, and uses resource path for tray icon.
- `requirements.txt`: add `pyinstaller`.
- `scripts/build_windows.py`: builds one-folder Windows app via PyInstaller.
- `.gitignore`: ignores build outputs.
- `README.md`: adds build/run instructions.

## Task 1: Icon and Resource Helper

**Files:**
- Create: `assets/logo.ico`
- Create: `src/vitrans/resources.py`

- [ ] Generate ICO from PNG with Pillow:

```bash
. .venv312/Scripts/activate && python - <<'PY'
from PIL import Image
image = Image.open('assets/logo.png')
image.save('assets/logo.ico', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
PY
```

- [ ] Create resource helper:

```python
from pathlib import Path
import sys


def resource_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return base_path / relative_path
```

- [ ] Run import check:

```bash
. .venv312/Scripts/activate && PYTHONPATH=src python -c "from vitrans.resources import resource_path; print(resource_path('assets/logo.ico').name)"
```

Expected: `logo.ico`.

## Task 2: Windows App Identity

**Files:**
- Modify: `src/vitrans/main.py`

- [ ] Add Windows AppUserModelID helper using `ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ViTrans.App")` on Windows.
- [ ] Call it before creating `QApplication`.
- [ ] Set `QApplication` app name/display name/desktop file name to `ViTrans`.
- [ ] Set app icon and tray icon from `resource_path("assets/logo.ico")`.
- [ ] Run smoke check:

```bash
. .venv312/Scripts/activate && PYTHONPATH=src python -c "from vitrans.main import ViTransApp; print(ViTransApp.__name__)"
```

Expected: `ViTransApp`.

## Task 3: PyInstaller Build Script

**Files:**
- Modify: `requirements.txt`
- Create: `scripts/build_windows.py`
- Modify: `.gitignore`

- [ ] Add `pyinstaller==6.11.1` to `requirements.txt`.
- [ ] Create build script that runs:

```python
import subprocess
import sys


def main() -> int:
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "ViTrans",
        "--icon",
        "assets/logo.ico",
        "--add-data",
        "assets/logo.ico;assets",
        "--add-data",
        "assets/logo.png;assets",
        "--collect-all",
        "easyocr",
        "--collect-all",
        "torch",
        "--collect-all",
        "torchvision",
        "--paths",
        "src",
        "src/vitrans/main.py",
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] Add `dist/`, `build/`, and `*.spec` to `.gitignore`.
- [ ] Install updated dependencies:

```bash
. .venv312/Scripts/activate && python -m pip install -r requirements.txt
```

## Task 4: Docs and Verification

**Files:**
- Modify: `README.md`

- [ ] Add build instructions:

```bash
. .venv312/Scripts/activate
python scripts/build_windows.py
./dist/ViTrans/ViTrans.exe
```

- [ ] Run tests:

```bash
. .venv312/Scripts/activate && PYTHONPATH=src python -m pytest tests -v
```

Expected: all tests pass.

- [ ] Run import smoke check from Task 2.

- [ ] Attempt build:

```bash
. .venv312/Scripts/activate && python scripts/build_windows.py
```

Expected: `dist/ViTrans/ViTrans.exe` exists. If PyInstaller hits a dependency edge, keep code/build script and report exact blocker.

## Task 5: Commit and Push

**Files:**
- Commit all modified files.

- [ ] Check git status.
- [ ] Commit with message `Package ViTrans as Windows app`.
- [ ] Push to `origin/main`.

## Self-Review

Spec coverage: tray/taskbar icon via app icon and tray icon, Task Manager name via `ViTrans.exe`, official app-style packaging via PyInstaller one-folder build.
Placeholder scan: no placeholders.
Type consistency: resource path returns `Path`; main.py uses `QIcon(str(path))`.
