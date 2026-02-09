from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import requests


REPO = "linhermx/barcodes_from_csv_ean13"
LATEST_API = f"https://api.github.com/repos/{REPO}/releases/latest"

ASSET_NAME = "barcode_tool_windows.exe"   # <- nombre fijo del asset en Releases

APP_EXE_PREFIX = "barcode_tool_v"
APP_EXE_SUFFIX = ".exe"


def base_dir() -> Path:
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


def parse_version(tag: str) -> tuple[int, int, int] | None:
    # "v1.2.3" o "1.2.3"
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", tag.strip())
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def parse_version_from_name(name: str) -> tuple[int, int, int] | None:
    m = re.match(rf"^{re.escape(APP_EXE_PREFIX)}(\d+)\.(\d+)\.(\d+){re.escape(APP_EXE_SUFFIX)}$", name)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def find_installed_app(app_dir: Path) -> tuple[tuple[int, int, int], Path] | None:
    candidates: list[tuple[tuple[int, int, int], Path]] = []
    for p in app_dir.glob(f"{APP_EXE_PREFIX}*{APP_EXE_SUFFIX}"):
        v = parse_version_from_name(p.name)
        if v:
            candidates.append((v, p))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0]


def get_latest_release() -> tuple[tuple[int, int, int], str, str]:
    """
    Returns: (version_tuple, tag_name, asset_download_url)
    """
    r = requests.get(LATEST_API, timeout=20)
    r.raise_for_status()
    data = r.json()

    tag = data.get("tag_name", "")
    v = parse_version(tag)
    if not v:
        raise RuntimeError(f"Tag inválido en latest release: {tag!r}")

    assets = data.get("assets", []) or []
    asset = next((a for a in assets if a.get("name") == ASSET_NAME), None)
    if not asset:
        raise RuntimeError(
            f"No se encontró el asset '{ASSET_NAME}' en el latest release.\n"
            "Sube ese ejecutable como Asset en GitHub Releases."
        )

    url = asset.get("browser_download_url", "")
    if not url:
        raise RuntimeError("Asset sin browser_download_url")

    return v, tag, url


def download_file(url: str, dst: Path) -> None:
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with dst.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)


def run_app(exe_path: Path) -> None:
    subprocess.Popen([str(exe_path)], cwd=str(exe_path.parent))
    raise SystemExit(0)


def main() -> None:
    root = base_dir()
    dirs = ensure_dirs(root)

    tk_root = tk.Tk()
    tk_root.withdraw()

    installed = find_installed_app(dirs["app"])
    installed_version = installed[0] if installed else None
    installed_exe = installed[1] if installed else None

    # 1) Consultar latest
    try:
        latest_version, latest_tag, asset_url = get_latest_release()
    except Exception as e:
        # Si falla internet/API, seguimos con la instalada si existe
        if installed_exe:
            messagebox.showwarning("Actualización no disponible", f"No se pudo verificar update:\n{e}\n\nSe abrirá la versión instalada.")
            run_app(installed_exe)
        messagebox.showerror("No hay app instalada", f"No se pudo verificar update y no existe app instalada.\n\nDetalle:\n{e}")
        return

    # 2) Si no hay instalada, forzamos instalar
    needs_install = installed_exe is None
    needs_update = (installed_version is None) or (latest_version > installed_version)

    if needs_install or needs_update:
        msg = (
            f"Hay una versión disponible: {latest_tag}\n"
            f"Instalada: {'ninguna' if installed_version is None else 'v' + '.'.join(map(str, installed_version))}\n\n"
            "¿Deseas actualizar ahora?"
        )
        if needs_install or messagebox.askyesno("Actualización disponible", msg):
            tmp = dirs["downloads"] / ASSET_NAME
            try:
                download_file(asset_url, tmp)
                target = dirs["app"] / f"{APP_EXE_PREFIX}{latest_version[0]}.{latest_version[1]}.{latest_version[2]}{APP_EXE_SUFFIX}"
                shutil.move(str(tmp), str(target))
                installed_exe = target
            except Exception as e:
                if installed_exe:
                    messagebox.showwarning("Update falló", f"No se pudo actualizar:\n{e}\n\nSe abrirá la versión instalada.")
                else:
                    messagebox.showerror("Update falló", f"No se pudo descargar/instalar:\n{e}")
                    return

    # 3) Ejecutar
    if not installed_exe:
        messagebox.showerror("No se encontró la app", "No hay ejecutable para abrir.")
        return

    run_app(installed_exe)


if __name__ == "__main__":
    main()