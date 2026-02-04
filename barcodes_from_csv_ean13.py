import argparse
import csv
from pathlib import Path


WINDOWS_FORBIDDEN = '<>:"\\|?*'


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


def main():
    parser = argparse.ArgumentParser(
        description="Genera códigos de barras EAN-13 (PNG) desde un CSV. El nombre del archivo sale de 'Clave SAT'."
    )
    parser.add_argument("--csv", required=True, help="Ruta al archivo CSV")
    parser.add_argument("--outdir", default="salida", help="Carpeta de salida (default: salida)")
    parser.add_argument("--delimiter", default=None, help="Delimitador del CSV (ej: ',' o '|' ). Si se omite, se intenta detectar.")
    parser.add_argument("--encoding", default="utf-8-sig", help="Encoding (default: utf-8-sig)")
    parser.add_argument("--overwrite", action="store_true", help="Sobrescribir si el PNG ya existe (si no, crea _2, _3...)")

    args = parser.parse_args()

    csv_path = Path(args.csv)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    delimiter = args.delimiter
    if delimiter is None:
        sample = csv_path.read_text(encoding=args.encoding, errors="ignore")[:2048]
        delimiter = "|" if sample.count("|") > sample.count(",") else ","

    required_cols = ["Clave SAT", "Secuencial", "EAN-13", "Descripción"]

    generated = 0
    errors = []

    with csv_path.open("r", encoding=args.encoding, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)

        missing = [c for c in required_cols if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(
                f"Faltan columnas: {missing}\nColumnas encontradas: {reader.fieldnames}"
            )

        for line_no, row in enumerate(reader, start=2):
            clave_sat_raw = row.get("Clave SAT", "")
            ean13_raw = row.get("EAN-13", "")

            try:
                clave_sat = sanitize_filename(clave_sat_raw)
                ean13_digits = clean_digits(ean13_raw)
                _base12 = validate_ean13(ean13_digits)

                out_path = outdir / f"{clave_sat}.png"
                if out_path.exists() and not args.overwrite:
                    out_path = unique_path(out_path)

                generated += 1
            except Exception as e:
                errors.append((line_no, clave_sat_raw, ean13_raw, str(e)))


    print(f"Listo. Filas válidas: {generated}")
    if errors:
        print("\nErrores (línea CSV | Clave SAT | EAN-13 | motivo):")
        for ln, clave_sat, ean, msg in errors:
            print(f"- {ln} | {clave_sat} | {ean} | {msg}")



if __name__ == "__main__":
    main()
