param(
  [switch]$Release
)

$ErrorActionPreference = "Stop"

# Ir a la raíz del repo (por si lo ejecutan desde scripts/)
Set-Location (Split-Path $PSScriptRoot -Parent)

# Activar venv si existe
if (Test-Path ".\venv\Scripts\Activate.ps1") {
  . .\venv\Scripts\Activate.ps1
}

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Limpiar builds previos
if (Test-Path ".\build") { Remove-Item ".\build" -Recurse -Force }
if (Test-Path ".\dist") { Remove-Item ".\dist" -Recurse -Force }

pyinstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name barcode_tool `
  --add-data "src\barcode_tool\resources\fonts\DejaVuSans.ttf;resources\fonts" `
  barcode_tool_gui.py

if (!(Test-Path ".\dist\barcode_tool.exe")) {
  throw "No se generó el ejecutable: dist\barcode_tool.exe"
}

Write-Host "EXE generado en: dist\barcode_tool.exe"

# Modo Release: crear el asset con nombre estándar para GitHub Releases
if ($Release) {
  Copy-Item ".\dist\barcode_tool.exe" -Destination ".\dist\barcode_tool_windows.exe" -Force
  Write-Host "Asset listo para GitHub Releases: dist\barcode_tool_windows.exe"
}
