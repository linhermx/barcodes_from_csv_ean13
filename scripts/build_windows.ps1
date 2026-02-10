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
  --icon src\barcode_tool\resources\icon.ico `
  --name barcode_tool_windows `
  --add-data "src\barcode_tool\resources\fonts\DejaVuSans.ttf;resources\fonts" `
  barcode_tool_gui.py

if (!(Test-Path ".\dist\barcode_tool_windows.exe")) {
  throw "No se generó el ejecutable: dist\barcode_tool_windows.exe"
}

Write-Host "EXE generado en: dist\barcode_tool_windows.exe"

# Modo Release
if ($Release) {
  Copy-Item ".\dist\barcode_tool_windows.exe" -Destination ".\dist\barcode_tool.exe" -Force
  Write-Host "Alias listo: dist\barcode_tool.exe"
}