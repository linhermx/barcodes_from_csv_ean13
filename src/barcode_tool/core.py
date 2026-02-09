from __future__ import annotations

import sys
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

from barcode import get_barcode_class
from barcode.writer import ImageWriter
from PIL import Image


WINDOWS_FORBIDDEN = '<>:"\\|?*'
REQUIRED_COLS = ["Clave", "Secuencial", "EAN-13", "Descripción"]


@dataclass
class RowError:
    line_no: int
    clave: str
    ean13: str
    message: str


@dataclass
class RunResult:
    generated: int
    errors: List[RowError]
    delimiter: str
    outdir: Path
    barcodes_dir: Path
    log_file: Path
    errors_csv: Path | None

def resource_path(relative: str) -> Path:
    """
    Devuelve la ruta absoluta a un recurso, compatible con PyInstaller.
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller extrae recursos a una carpeta temporal
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent
    return base / relative


def sanitize_filename(name: str) -> str:
    s = "" if name is None else str(name).strip()
    s = s.replace("/", "_")
    for ch in WINDOWS_FORBIDDEN:
        s = s.replace(ch, "")
    s = s.strip()
    if not s:
        s = "SIN_CLAVE"
    while s.endswith(".") or s.endswith(" "):
        s = s[:-1]
    return s


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    i = 2
    while True:
        candidate = path.with_name(f"{stem}_{i}{suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def clean_digits(value: str) -> str:
    s = "" if value is None else str(value).strip()
    return "".join(ch for ch in s if ch.isdigit())


def ean13_check_digit(code12: str) -> int:
    if len(code12) != 12 or not code12.isdigit():
        raise ValueError("Para checksum se requieren exactamente 12 dígitos")

    digits = [int(c) for c in code12]
    odd_sum = sum(digits[0::2])
    even_sum = sum(digits[1::2])
    total = odd_sum + (even_sum * 3)
    return (10 - (total % 10)) % 10


def validate_ean13(code13: str) -> str:
    if len(code13) != 13 or not code13.isdigit():
        raise ValueError(f"EAN-13 inválido: se esperaban 13 dígitos, llegó: '{code13}'")

    base12 = code13[:12]
    expected = ean13_check_digit(base12)
    actual = int(code13[-1])

    if expected != actual:
        raise ValueError(f"Checksum incorrecto: esperado {expected}, recibido {actual}")

    return base12


def resize_and_pad_to_exact(src_png: Path, dst_png: Path, width: int, height: int) -> None:
    with Image.open(src_png) as im:
        im = im.convert("RGB")
        im.thumbnail((width, height), Image.Resampling.LANCZOS)

        canvas = Image.new("RGB", (width, height), "white")
        x = (width - im.size[0]) // 2
        y = (height - im.size[1]) // 2
        canvas.paste(im, (x, y))

        canvas.save(dst_png, format="PNG", optimize=True)


def detect_delimiter(csv_path: Path, *, encoding: str) -> str:
    sample = csv_path.read_text(encoding=encoding, errors="ignore")[:2048]
    return "|" if sample.count("|") > sample.count(",") else ","


def generate_barcodes_from_csv(
    csv_path: Path,
    outdir: Path,
    *,
    delimiter: Optional[str] = None,
    encoding: str = "utf-8-sig",
    width: int = 450,
    height: int = 300,
    no_text: bool = False,
    overwrite: bool = False,
) -> RunResult:
    csv_path = Path(csv_path)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    barcodes_dir = outdir / "barcodes"
    logs_dir = outdir / "logs"

    barcodes_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    font_file = resource_path("resources/fonts/DejaVuSans.ttf")

    writer_options = {
        "dpi": 300,

        # Barras
        "module_width": 0.60,
        "module_height": 29.0,

        # Márgenes
        "quiet_zone": 0.9,

        # Texto
        "write_text": (not no_text),
        "font_size": 14,
        "text_distance": 5.5,

        "background": "white",
        "foreground": "black",
    }

    # Solo si queremos texto
    if not no_text:
        writer_options["font_path"] = str(font_file)                    

    EAN13 = get_barcode_class("ean13")

    if delimiter is None:
        delimiter = detect_delimiter(csv_path, encoding=encoding)

    generated = 0
    errors: List[RowError] = []

    with csv_path.open("r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)

        missing = [c for c in REQUIRED_COLS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(
                f"Faltan columnas: {missing}\nColumnas encontradas: {reader.fieldnames}"
            )

        for line_no, row in enumerate(reader, start=2):
            clave_raw = row.get("Clave", "")
            ean13_raw = row.get("EAN-13", "")

            try:
                clave = sanitize_filename(clave_raw)
                ean13_digits = clean_digits(ean13_raw)
                base12 = validate_ean13(ean13_digits)

                out_path = barcodes_dir / f"{clave}.png"
                if out_path.exists() and not overwrite:
                    out_path = unique_path(out_path)

                barcode_obj = EAN13(base12, writer=ImageWriter())

                tmp_base = barcodes_dir / f"__tmp__{ean13_digits}"
                barcode_obj.save(str(tmp_base), options=writer_options)
                tmp_png = Path(str(tmp_base) + ".png")

                resize_and_pad_to_exact(tmp_png, out_path, width, height)

                try:
                    tmp_png.unlink(missing_ok=True)
                except Exception:
                    pass

                generated += 1

            except Exception as e:
                errors.append(RowError(line_no, str(clave_raw), str(ean13_raw), str(e)))

    # ---- Guardar log de ejecución ----
    run_log = logs_dir / "run_log.txt"
    with run_log.open("w", encoding="utf-8") as lf:
        lf.write(f"CSV: {csv_path}\n")
        lf.write(f"Salida: {outdir}\n")
        lf.write(f"Delimitador: {delimiter}\n")
        lf.write(f"Generados: {generated}\n")
        lf.write(f"Errores: {len(errors)}\n\n")

        if errors:
            lf.write("Errores (line_no | Clave | EAN-13 | motivo):\n")
            for e in errors:
                lf.write(f"{e.line_no} | {e.clave} | {e.ean13} | {e.message}\n")

    errors_csv = outdir / "errors.csv"

    if errors:
        with errors_csv.open("w", encoding="utf-8", newline="") as ef:
            w = csv.writer(ef)
            w.writerow(["line_no", "Clave", "EAN-13", "motivo"])
            for e in errors:
                w.writerow([e.line_no, e.clave, e.ean13, e.message])
    else:
        if errors_csv.exists():
            try:
                errors_csv.unlink()
            except Exception:
                pass
    return RunResult(generated=generated, errors=errors, delimiter=delimiter, outdir=outdir, barcodes_dir=barcodes_dir, log_file=run_log, errors_csv=(errors_csv if errors else None))
