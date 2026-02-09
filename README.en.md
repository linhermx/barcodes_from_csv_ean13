# barcodes_from_csv_ean13

EAN-13 **barcode generator** in **PNG** format from a **CSV** file, developed in Python.

The system validates the check digit (checksum), generates images ready for **printing**, and names files using the **Clave** field as the main identifier.

Includes:
- **Windows (.exe)** application for non-technical users
- Graphical user interface (GUI)
- Automatic update system via launcher
- Command-line interface (CLI) for developers

---

## Features

- Generation of **valid EAN-13 barcodes**
- Automatic **checksum validation**
- **PNG** output with configurable size (default: **450 × 300 px**)
- Optimized for printing
- File names based on **Clave**
- CSV delimiter support: `,` and `|`
- Automatic filename collision handling (`_2`, `_3`, etc.)
- Compatible with Excel-generated CSV files (Windows)
- GUI for non-technical users
- Automatic update system

---

## Windows Usage (Recommended)

### Download

1. Go to **Releases**:  
   https://github.com/linhermx/barcodes_from_csv_ean13/releases
2. Download:  
   **`barcode_tool_launcher.exe`**

> No Python or dependencies required.

---

### First Run

1. Run `barcode_tool_launcher.exe`
2. The launcher:
   - Checks for a newer version
   - Asks whether you want to update
3. Accept, and the system updates automatically

After that, the main application opens.

---

### Using the Application

1. Select the **CSV file**
2. Select the **output folder**
3. Configure options
4. Click **Generate**

Generated structure:

- `barcodes/` → PNG barcode images
- `logs/` → execution and error logs

---

## CSV File Format

The CSV file must use **a single delimiter consistently**.

### Required Columns

| Column | Description |
|------|------------|
| Clave | Main identifier (used as filename) |
| Secuencial | Internal sequence |
| EAN-13 | Full 13-digit EAN-13 code |
| Descripción | Descriptive text |

### Example (`,` delimiter)

```
Clave,Secuencial,EAN-13,Descripción
TNF1041-1/8,105000000026,1050000000264,Test product
```

> ⚠️ Do not mix delimiters within the same file.

---

## Developer / Technical Usage (CLI)

### Requirements

- Python **3.10+**
- Windows

Main dependencies:
- `python-barcode`
- `Pillow`

---

### Installation

Using a virtual environment (`venv`) is recommended.

```bash
git clone https://github.com/linhermx/barcodes_from_csv_ean13.git
cd barcodes_from_csv_ean13

python -m venv venv
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

---

### Basic CLI Usage

```bash
python barcodes_from_csv_ean13.py \
  --csv examples/sample.csv \
  --outdir output \
  --delimiter ","
```

---

## CLI Parameters

| Parameter | Description |
|----------|------------|
| `--csv` | Path to the CSV file |
| `--outdir` | Output folder (default: `salida`) |
| `--delimiter` | CSV delimiter (`,`) |
| `--encoding` | CSV encoding (default: `utf-8-sig`) |
| `--width` | Final image width in pixels (default: 450) |
| `--height` | Final image height in pixels (default: 300) |
| `--overwrite` | Overwrite existing files |
| `--no-text` | Do not print the number below the barcode |

---

## Filename Convention

Example:

```
TNF1044-5/16 → TNF1044-5_16.png
```

Rules:
- `/` → `_`
- Invalid characters are removed
- `_2`, `_3`, etc. are added if a name collision occurs

---

## Printing Notes

- Default size: **450 × 300 px @ 300 DPI**
- Print at **100% scale**
- Functionally compliant with the EAN-13 standard

---

## Recommended Workflow

1. Prepare the CSV file
2. Run the application
3. Review generated barcodes
4. Check logs if errors occur
5. Print or integrate into your system
