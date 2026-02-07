import argparse
import sys
from pathlib import Path


# Importar desde /src sin configurar PYTHONPATH
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.exists() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from barcode_tool.core import generate_barcodes_from_csv


def main():
    parser = argparse.ArgumentParser(
        description="Genera códigos de barras EAN-13 (PNG) desde un CSV. El nombre del archivo sale de 'Clave'."
    )
    parser.add_argument("--csv", required=True, help="Ruta al archivo CSV")
    parser.add_argument("--outdir", default="salida", help="Carpeta de salida (default: salida)")
    parser.add_argument("--delimiter", default=None, help="Delimitador del CSV (ej: ',' o '|' ). Si se omite, se intenta detectar.")
    parser.add_argument("--encoding", default="utf-8-sig", help="Encoding (default: utf-8-sig)")
    parser.add_argument("--width", type=int, default=450, help="Ancho final en px (default: 450)")
    parser.add_argument("--height", type=int, default=300, help="Alto final en px (default: 300)")
    parser.add_argument("--no-text", action="store_true", help="No imprimir el número debajo del código")
    parser.add_argument("--overwrite", action="store_true", help="Sobrescribir si el PNG ya existe (si no, crea _2, _3...)")

    args = parser.parse_args()

    result = generate_barcodes_from_csv(
        csv_path=Path(args.csv),
        outdir=Path(args.outdir),
        delimiter=args.delimiter,
        encoding=args.encoding,
        width=args.width,
        height=args.height,
        no_text=args.no_text,
        overwrite=args.overwrite,
    )

    print(f"Listo. Filas válidas: {result.generated}")
    if result.errors:
        print("\nErrores (línea CSV | Clave | EAN-13 | motivo):")
        for e in result.errors:
            print(f"- {e.line_no} | {e.clave} | {e.ean13} | {e.message}")


if __name__ == "__main__":
    main()
