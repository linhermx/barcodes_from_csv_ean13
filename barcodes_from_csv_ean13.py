import argparse
import csv
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Genera códigos de barras EAN-13 (PNG) desde un CSV. El nombre del archivo sale de 'Clave SAT'."
    )
    parser.add_argument("--csv", required=True, help="Ruta al archivo CSV")
    parser.add_argument("--outdir", default="salida", help="Carpeta de salida (default: salida)")
    parser.add_argument("--delimiter", default=None, help="Delimitador del CSV (ej: ',' o '|' ). Si se omite, se intenta detectar.")
    parser.add_argument("--encoding", default="utf-8-sig", help="Encoding (default: utf-8-sig)")
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
            # Por ahora solo contamos filas válidas de estructura
            generated += 1

    print(f"Listo. Filas leídas: {generated}")
    if errors:
        print("\nErrores:")
        for e in errors:
            print(e)


if __name__ == "__main__":
    main()
