$ErrorActionPreference = "Stop"

Set-Location (Split-Path $PSScriptRoot -Parent)

if (Test-Path ".\venv\Scripts\Activate.ps1") {
  . .\venv\Scripts\Activate.ps1
}

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Limpieza selectiva solo del launcher
if (Test-Path ".\dist\launcher") { Remove-Item ".\dist\launcher" -Recurse -Force }

pyinstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name barcode_tool_launcher `
  barcode_tool_launcher.py

Write-Host "Launcher EXE generado en: dist\barcode_tool_launcher.exe"