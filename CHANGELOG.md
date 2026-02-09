# Changelog

All notable changes to this project will be documented in this file.

This project follows **Semantic Versioning** (`MAJOR.MINOR.PATCH`).

---

## [v1.2.0] - Launcher & Update System

### Added
- Windows **launcher executable** (`barcode_tool_launcher.exe`)
- Automatic update check against GitHub Releases
- User prompt to update when a newer version is available
- Separation between launcher and application executable
- App version displayed in GUI title

### Changed
- Distribution workflow to use launcher-based execution
- Improved end-user experience for non-technical users

---

## [v1.1.1] - Windows EXE Font Fix

### Fixed
- `cannot open resource` error when rendering barcode text in Windows EXE
- Font loading issues inside PyInstaller bundled executable

### Added
- Bundled **DejaVuSans.ttf** font into PyInstaller build
- Robust resource path resolution for packaged environments

---

## [v1.1.0] - GUI & Structured Output

### Added
- Minimal **Tkinter GUI** for non-technical users
- CSV file selector and output folder selector
- Organized output structure:
  - `barcodes/` for generated PNG files
  - `logs/` for execution logs and error reports
- `run_log.txt` execution summary
- `errors.csv` generated when row-level errors occur
- Option to open output folder after completion

### Changed
- Core barcode generation logic extracted into reusable module
- Improved error reporting and user feedback

---

## [v1.0.0] - Initial Release

### Added
- EAN-13 barcode generation from CSV
- Automatic checksum validation
- PNG output optimized for printing
- Configurable output size (default: 450×300 px)
- Filename generation based on `Clave` column
- Safe filename sanitization and collision handling
- CLI interface for developers
- Full project documentation

---