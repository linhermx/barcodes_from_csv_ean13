# barcodes_from_csv_ean13

Generador de códigos de barras **EAN-13** en formato **PNG** a partir de un archivo **CSV**, desarrollado en Python.  

El script valida el dígito de control (checksum), genera imágenes listas para **impresión** y nombra los archivos usando la **Clave** como identificador principal.

---

## Características

- Generación de códigos de barras **EAN-13 válidos**
- Validación automática del **checksum**
- Salida en **PNG** con dimensiones configurables (default: **450 × 300 px**)
- Optimizado para **impresión**
- Nombre de archivo basado en la **Clave** (sanitiza caracteres no válidos)
- Soporte para distintos delimitadores de CSV (``,``, `|`)
- Manejo de colisiones de nombre (`_2`, `_3`, etc.)
- Compatible con CSVs generados desde Excel (Windows)

---

## Requisitos

- Python **3.10+**
- Sistema operativo: Windows / macOS / Linux

Dependencias principales:
- `python-barcode`
- `Pillow`

---

## Instalación

Se recomienda usar un entorno virtual (`venv`).

```bash
git clone https://github.com/linhermx/barcodes_from_csv_ean13.git
cd barcodes_from_csv_ean13

python -m venv venv
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

---

## Formato del archivo CSV

El CSV debe usar un solo delimitador consistente en todo el archivo

### Columnas requeridas

| Columna | Descripción |
|---|---|
| Clave | Identificador principal (se usa para el nombre del archivo) |
| Secuencial | Secuencia interna para poder generar el EAN-13 |
| EAN-13 | Código EAN-13 completo (13 dígitos, incluye checksum) |
| Descripción | Texto descriptivo |

### Ejemplo (con delimitador ',')

~~~
Clave,Secuencial,EAN-13,Descripción
TNF1041-1/8,105000000026,1050000000264,Producto de prueba
~~~

>[!IMPORTANT]
>
> No mezclar delimitadores dentro del mismo archivo.

---

## Uso básico
```bash
python barcodes_from_csv_ean13.py \
  --csv examples/sample.csv \
  --outdir salida \
  --delimiter ","
```

Esto generará los archivos PNG en la carpeta `salida/`.

---

## Parámetros disponibles
| Parámetro | Descripción
|---|---|
| --csv | Ruta del archivo CSV |
| --outdir | Carpeta de salida (default: `salida`) |
| --delimiter | Delimitador del CSV (`,`) |
| --encoding | Encoding del CSV (default: `utf-8-sig`) |
| --width | Ancho final de la imagen en píxeles (defautl: 450) |
| --height | Alto final de la imagen en píxeles (default: 300) |
| --overwrite | Sobreescribe archivos existentes |
| --no-text | No imprime el número debajo del código |

---

## Conveción de nombres de archivo
Los archivos se generan usando la columna **Clave**:
~~~
TNF1044-5/16 →  TNF1044-5_16.png
~~~

- `/` se reemplaza por `_`
- Se eliminan caracteres no válidos para Windows
- Si el archivo existe y no se usa `--overwrite`, se agrega `_2`, `_3`, etc.

---

## Notas sobre impresión
- El tamaño por defecto (450 x 300 px a 300 DPI) está pensado para impresión.
- Se recomienda imprimir al 100% (sin "ajustar a página").
- Los códigos cumplen con el estándar EAN-13 a nivel funcional.

---

## Flujo de trabajo recomendado
1. Preparar el CSV con los encabezados correctos
2. Ejecutar el script
3. Revisar los códigos generados
4. Imprimir o integrar en el flujo de inventario