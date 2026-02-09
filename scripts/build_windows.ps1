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
  barcode_tool_gui.py

Write-Host "EXE generado en: dist\barcode_tool.exe"
