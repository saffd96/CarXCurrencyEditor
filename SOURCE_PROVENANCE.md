# Source provenance

Verified locally on 2026-09-13 before publishing this repository.

Original bundle: `original-bundle-20260906-223555`.

| File | SHA-256 |
| --- | --- |
| Original `CarXCurrencyEditor_1.8.0.exe` | `37952c6f18a03ed89f1af98d4d2a472f5298323870242f6a582bfbac094c0d1b` |
| Published `carx_currency_editor.py` | `8a7196013ffaeec209bae54b61714479c905c33e97562a160aa1ad3c877e60bd` |

The original executable's PyInstaller archive contains a script entry named
`carx_currency_editor`. That entry was read with PyInstaller's CArchiveReader
and decoded with Python's marshal module, without executing the application.
The local source was compiled with CPython 3.14.3. After normalizing code-object
filenames recursively, the compiled source code object compared equal to the
original executable's code object, including its nested code objects.

Result: **the published application source matches the application bytecode
embedded in the specified original bundle**. The source was copied without edits.
Git attributes preserve its original bytes and line endings.

The original bundle includes `python314.dll`; saved build metadata records
CPython 3.14.3 x64. The archive is a directory bundle with `_internal` dependencies.
The existing working-directory spec contains later packaging optimizations and
is not presented as the original build recipe.

This check establishes application-code correspondence; it does not establish
byte-for-byte reproducibility of the entire executable or third-party runtime files.
The original executable and runtime binaries are not included in this source repository.

## Validation on 2026-09-13

- Built-in source self-test: passed.
- GUI smoke test: passed (languages, dropdown, fields, checkboxes, validation,
  and donation link callback with browser opening mocked).
- Clean virtual environment: CPython 3.14.3 x64, PyInstaller 6.21.0.
- Both README build commands completed successfully: onefile with UAC manifest
  and onedir with application-managed elevation.
- Application code extracted from both newly built executables matches the source.
- No live-game memory writes were performed during these checks.

Resolved build dependencies: altgraph 0.17.5, packaging 26.3,
pefile 2024.8.26, pyinstaller-hooks-contrib 2026.7, pywin32-ctypes 0.2.3,
setuptools 84.0.0. These describe this verification environment, not necessarily
all dependency versions used for the original binary.
