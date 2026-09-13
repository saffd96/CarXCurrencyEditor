# CarX Currency Editor 1.8.0 ? source for review

Full application source corresponding to the local release backup
`original-bundle-20260906-223555`, provided for Nexus Mods review.

## Files

- `carx_currency_editor.py`: complete application source, including the GUI,
  Russian/English translations, Windows process access, currency scanning and
  replacement, administrator elevation, and built-in self-test.
- `verify_bundle.py`: GUI smoke test helper; not required to build the application.
- `README_EN.txt` and `README_RU.txt`: usage instructions copied from the original bundle.
- `requirements-build.txt`: pinned build tool version.
- `SOURCE_PROVENANCE.md`: source-to-bundle verification and SHA-256 hashes.

The application uses the Python standard library, including Tkinter and ctypes.
No third-party application packages, external source files, game files, keys,
or downloaded assets are required to build it. PyInstaller is a build dependency.

## Build requirements

- 64-bit Windows.
- 64-bit CPython 3.10 or newer with Tcl/Tk and pip installed.
  **Python 3.14.3 x64 is the locally verified version** and matches the runtime
  version in the saved build metadata. Other Python versions have not been tested here.
- PyInstaller **6.21.0**.
- Internet access to install the build tools.

Install Python from https://www.python.org/downloads/windows/ and include Tcl/Tk
and pip. Download this repository using **Code > Download ZIP**, extract it,
and open PowerShell in the folder containing `carx_currency_editor.py`.

### 1. Prepare an isolated build environment

```powershell
python --version
python -c "import struct; assert struct.calcsize('P') == 8, '64-bit Python required'"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -c "import tkinter; print('Tk', tkinter.TkVersion)"
.\.venv\Scripts\python.exe -m PyInstaller --version
```

Activation is not required; every command explicitly uses the virtual environment.
If `python` is unavailable, install Python and enable its PATH option, then reopen
PowerShell. Building does not require administrator privileges.

### 2. Check the source without accessing the game

```powershell
.\.venv\Scripts\python.exe carx_currency_editor.py --self-test
```

Expected output: `self-test: OK`. This uses synthetic memory blocks and does not
connect to or modify a running game. Optional GUI checks (briefly opens a window):

```powershell
.\.venv\Scripts\python.exe verify_bundle.py
```

### 3. Build a single executable

This is the single-file command supplied in the moderation correspondence:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --uac-admin `
  --name CarXCurrencyEditor_1.8.0 `
  carx_currency_editor.py
```

Output: `dist\CarXCurrencyEditor_1.8.0.exe`.
The executable requests administrator rights when launched. `--windowed`
hides the console. The program itself also contains an elevation routine.

### 4. Alternative: directory bundle matching the original layout

The saved `original-bundle-20260906-223555` is a directory bundle containing
an executable and an `_internal` directory. Build the same packaging layout with:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller `
  --noconfirm `
  --clean `
  --onedir `
  --windowed `
  --name CarXCurrencyEditor_1.8.0 `
  carx_currency_editor.py
Copy-Item README_EN.txt, README_RU.txt dist\CarXCurrencyEditor_1.8.0\
```

Output: `dist\CarXCurrencyEditor_1.8.0\CarXCurrencyEditor_1.8.0.exe` plus
`_internal`. Distribute the **whole directory**. This variant uses the application's
own administrator elevation routine. The single-file and directory formats use
identical application source, but their executable hashes will differ.

The commands generate their own `.spec` files. A later size-optimized spec from
the working directory is deliberately not used for this original-bundle source.
Byte-for-byte reproduction of the original executable is not claimed: toolchain,
packaging settings, and dependency versions affect the executable.

## Application behavior relevant to review

The application targets the running `CarX Street.exe` process for offline game
version 1.8.0. It uses Windows process/memory APIs through ctypes to scan for
currency values, validate changed values, and write replacements selected by
the user. It requests administrator access for process access. It does not
patch game executables or directly edit save files; the game saves its state.

The GUI includes a donation button opening `https://dalink.to/saffd` in the
user's browser. Diagnostic logs are written to
`%LOCALAPPDATA%\CarXCurrencyEditor\editor.log`.
See the included usage instructions for the two-scan workflow.

## Build documentation

- [PyInstaller operating modes](https://pyinstaller.org/en/stable/operating-mode.html)
- [PyInstaller command options](https://pyinstaller.org/en/stable/usage.html)
