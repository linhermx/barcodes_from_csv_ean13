from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


APP_EXE_PREFIX = "barcode_tool_v"
APP_EXE_SUFFIX = ".exe"


def base_dir() -> Path:
    """
    Carpeta donde vive el launcher (dev o exe).
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def ensure_dirs(root: Path) -> dict[str, Path]:
    app_dir = root / "app"
    downloads_dir = root / "downloads"
    logs_dir = root / "logs"
    app_dir.mkdir(parents=True, exist_ok=True)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    return {"root": root, "app": app_dir, "downloads": downloads_dir, "logs": logs_dir}


def parse_version_from_name(name: str) -> tuple[int, int, int] | None:
    """
    barcode_tool_v1.2.3.exe -> (1,2,3)
    """
    m = re.match(rf"^{re.escape(APP_EXE_PREFIX)}(\d+)\.(\d+)\.(\d+){re.escape(APP_EXE_SUFFIX)}$", name)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def find_installed_app(app_dir: Path) -> Path | None:
    candidates: list[tuple[tuple[int, int, int], Path]] = []
    for p in app_dir.glob(f"{APP_EXE_PREFIX}*{APP_EXE_SUFFIX}"):
        v = parse_version_from_name(p.name)
        if v:
            candidates.append((v, p))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def run_app(exe_path: Path) -> None:
    # Ejecuta y cierra el launcher
    subprocess.Popen([str(exe_path)], cwd=str(exe_path.parent))
    raise SystemExit(0)


def main() -> None:
    root = base_dir()
    dirs = ensure_dirs(root)

    # Tk “invisible” para messagebox
    tk_root = tk.Tk()
    tk_root.withdraw()

    exe = find_installed_app(dirs["app"])
    if not exe:
        messagebox.showerror(
            "Aplicación no instalada",
            "No se encontró una versión instalada.\n\n"
            "Descarga el ejecutable desde GitHub Releases y colócalo en:\n"
            f"{dirs['app']}\n\n"
            "Ejemplo de nombre:\n"
            "barcode_tool_v1.1.1.exe"
        )
        return

    run_app(exe)


if __name__ == "__main__":
    main()