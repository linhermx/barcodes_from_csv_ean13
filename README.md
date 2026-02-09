# barcodes_from_csv_ean13

Generador de códigos de barras **EAN-13** en formato **PNG** a partir de un archivo **CSV**, desarrollado en Python.

El sistema valida el dígito de control (checksum), genera imágenes listas para **impresión** y nombra los archivos usando la **Clave** como identificador principal.

Incluye:
- Aplicación **Windows (.exe)** para usuarios no técnicos
- Interfaz gráfica (GUI)
- Actualización automática mediante launcher
- Uso por línea de comandos (CLI) para desarrolladores

---

## Características

- Generación de códigos de barras **EAN-13 válidos**
- Validación automática del **checksum**
- Salida en **PNG** con tamaño configurable (default: **450 × 300 px**)
- Optimizado para impresión
- Nombre de archivo basado en la **Clave**
- Soporte para delimitadores `,` y `|`
- Manejo de colisiones de nombre (`_2`, `_3`, etc.)
- Compatible con CSVs de Excel (Windows)
- GUI para usuarios no técnicos
- Sistema de actualización automática

---

## Uso en Windows (Recomendado)

### Descarga

1. Ir a **Releases**:
   https://github.com/linhermx/barcodes_from_csv_ean13/releases
2. Descargar:
   **`barcode_tool_launcher.exe`**

> No necesitas instalar Python ni dependencias.

---

### Primer uso

1. Ejecuta `barcode_tool_launcher.exe`
2. El launcher:
   - Revisa si hay una versión más reciente
   - Pregunta si deseas actualizar
3. Acepta y el sistema se actualiza automáticamente

Después se abre la aplicación principal.

---

### Uso de la aplicación

1. Selecciona el **archivo CSV**
2. Selecciona la **carpeta de salida**
3. Configura las opciones
4. Haz clic en **Generar**

Estructura generada:

- `barcodes/` → imágenes PNG
- `logs/` → logs de ejecución y errores

---

## Formato del archivo CSV

El CSV debe usar **un solo delimitador** en todo el archivo.

### Columnas requeridas

| Columna | Descripción |
|-------|------------|
| Clave | Identificador principal (nombre del archivo) |
| Secuencial | Secuencia interna |
| EAN-13 | Código completo de 13 dígitos |
| Descripción | Texto descriptivo |

### Ejemplo (delimitador `,`)

~~~
Clave,Secuencial,EAN-13,Descripción
TNF1041-1/8,105000000026,1050000000264,Producto de prueba
~~~

> ⚠️ No mezclar delimitadores dentro del mismo archivo.

---

## Uso técnico / desarrolladores (CLI)
### Requisitos

- Python **3.10+**
- Windows

Dependencias principales:
- `python-barcode`
- `Pillow`

---

### Instalación

Se recomienda usar un entorno virtual (`venv`).

```bash
git clone https://github.com/linhermx/barcodes_from_csv_ean13.git
cd barcodes_from_csv_ean13

python -m venv venv
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Uso básico por CLI

```bash
python barcodes_from_csv_ean13.py \
  --csv examples/sample.csv \
  --outdir salida \
  --delimiter ","
```

---

## Parámetros CLI

| Parámetro | Descripción
|---|---|
| `--csv` | Ruta del archivo CSV |
| `--outdir` | Carpeta de salida (default: `salida`) |
| `--delimiter` | Delimitador del CSV (`,`) |
| `--encoding` | Encoding del CSV (default: `utf-8-sig`) |
| `--width` | Ancho final de la imagen en píxeles (defautl: 450) |
| `--height` | Alto final de la imagen en píxeles (default: 300) |
| `--overwrite` | Sobreescribe archivos existentes |
| `--no-text` | No imprime el número debajo del código |

---

## Convención de nombres

Ejemplo:
~~~
TNF1044-5/16 →  TNF1044-5_16.png
~~~

Reglas:

- / → _
- Se eliminan caracteres inválidos
- Se agrega _2, _3 si hay colisión

---

## Notas de impresión
- Tamaño default: **450 x 300px @ 300 DPI**
- Imprimir al **100%**
- Cumple estándar EAN-13 funcional

---

## Flujo recomendado

1. Preparar CSV
2. Ejecutar la app
3. Revisar resultados
4. Ver logs si hay errores
5. Imprimir o integrar al sistema