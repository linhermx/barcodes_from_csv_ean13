from __future__ import annotations

import os
import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .core import generate_barcodes_from_csv


class BarcodeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de Códigos de Barras EAN-13")
        self.geometry("900x560")
        self.minsize(860, 540)

        self.csv_path = tk.StringVar(value="")
        self.out_dir = tk.StringVar(value="")
        self.overwrite_var = tk.BooleanVar(value=False)
        self.no_text_var = tk.BooleanVar(value=False)
        self.width_var = tk.IntVar(value=450)
        self.height_var = tk.IntVar(value=300)
        self.status_var = tk.StringVar(value="Listo.")
        self.last_output_dir: Path | None = None
        self.last_barcodes_dir: Path | None = None


        self._apply_style()
        self._build_ui()

    def _apply_style(self):
        style = ttk.Style(self)

        # Tema moderno nativo en Windows
        for theme in ("vista", "xpnative", "clam"):
            try:
                style.theme_use(theme)
                break
            except Exception:
                continue

        # Tipografía moderna (si existe)
        base_font = ("Segoe UI", 10)
        bold_font = ("Segoe UI", 10, "bold")

        style.configure("TLabel", font=base_font)
        style.configure("Title.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Hint.TLabel", foreground="#666666")
        style.configure("TButton", padding=(10, 6))
        style.configure("Primary.TButton", padding=(12, 7))
        style.configure("TCheckbutton", font=base_font)

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        root = ttk.Frame(self, padding=16)
        root.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)

        # ---------- Entrada ----------
        header_in = ttk.Label(root, text="Entrada", style="Title.TLabel")
        header_in.grid(row=0, column=0, sticky="w", pady=(0, 8))

        frm_in = ttk.Frame(root)
        frm_in.grid(row=1, column=0, sticky="ew")
        frm_in.columnconfigure(1, weight=1)

        ttk.Label(frm_in, text="Archivo CSV").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 8))
        ttk.Entry(frm_in, textvariable=self.csv_path).grid(row=0, column=1, sticky="ew", pady=(0, 8))
        ttk.Button(frm_in, text="Seleccionar…", command=self.pick_csv).grid(row=0, column=2, padx=(10, 0), pady=(0, 8))

        ttk.Label(frm_in, text="Carpeta de salida").grid(row=1, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(frm_in, textvariable=self.out_dir).grid(row=1, column=1, sticky="ew")
        ttk.Button(frm_in, text="Seleccionar…", command=self.pick_outdir).grid(row=1, column=2, padx=(10, 0))

        # Separador
        ttk.Separator(root).grid(row=2, column=0, sticky="ew", pady=14)

        # ---------- Opciones ----------
        header_opts = ttk.Label(root, text="Opciones", style="Title.TLabel")
        header_opts.grid(row=3, column=0, sticky="w", pady=(0, 8))

        frm_opts = ttk.Frame(root)
        frm_opts.grid(row=4, column=0, sticky="ew")
        frm_opts.columnconfigure(0, weight=1)

        left = ttk.Frame(frm_opts)
        left.grid(row=0, column=0, sticky="w")

        ttk.Checkbutton(left, text="Sobrescribir si existe", variable=self.overwrite_var).grid(row=0, column=0, sticky="w", padx=(0, 18))
        ttk.Checkbutton(left, text="No imprimir texto", variable=self.no_text_var).grid(row=0, column=1, sticky="w")

        size = ttk.Frame(frm_opts)
        size.grid(row=0, column=1, sticky="e")

        ttk.Label(size, text="Tamaño (px)").grid(row=0, column=0, sticky="e", padx=(0, 8))
        ttk.Entry(size, textvariable=self.width_var, width=7).grid(row=0, column=1, sticky="e")
        ttk.Label(size, text="×").grid(row=0, column=2, padx=8)
        ttk.Entry(size, textvariable=self.height_var, width=7).grid(row=0, column=3, sticky="e")
        ttk.Label(size, text="(ancho × alto)", style="Hint.TLabel").grid(row=0, column=4, padx=(10, 0))

        # Acción (botón alineado a la derecha)
        frm_actions = ttk.Frame(root)
        frm_actions.grid(row=5, column=0, sticky="ew", pady=(12, 6))
        frm_actions.columnconfigure(0, weight=1)

        # Botón secundario: abrir carpeta (deshabilitado al inicio)
        self.open_btn = ttk.Button(frm_actions, text="Abrir carpeta…", command=self.open_output, state="disabled")
        self.open_btn.grid(row=0, column=0, sticky="w")

        # Botón principal
        self.run_btn = ttk.Button(frm_actions, text="Generar", style="Primary.TButton", command=self.run)
        self.run_btn.grid(row=0, column=1, sticky="e")



        # ---------- Resultados ----------
        header_log = ttk.Label(root, text="Resultados", style="Title.TLabel")
        header_log.grid(row=6, column=0, sticky="w", pady=(10, 6))

        log_wrap = ttk.Frame(root)
        log_wrap.grid(row=7, column=0, sticky="nsew")
        log_wrap.columnconfigure(0, weight=1)
        log_wrap.rowconfigure(0, weight=1)

        self.log_box = tk.Text(
            log_wrap,
            wrap="word",
            height=12,
            borderwidth=1,
            relief="solid",
        )
        self.log_box.grid(row=0, column=0, sticky="nsew")
        self.log_box.configure(state="disabled")

        sb = ttk.Scrollbar(log_wrap, command=self.log_box.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.log_box.configure(yscrollcommand=sb.set)

        # Status bar
        ttk.Separator(root).grid(row=8, column=0, sticky="ew", pady=(10, 6))
        status = ttk.Label(root, textvariable=self.status_var, anchor="w", style="Hint.TLabel")
        status.grid(row=9, column=0, sticky="ew")

    def pick_csv(self):
        path = filedialog.askopenfilename(
            title="Selecciona el CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if path:
            self.csv_path.set(path)

    def pick_outdir(self):
        path = filedialog.askdirectory(title="Selecciona carpeta de salida")
        if path:
            self.out_dir.set(path)

    def _append_log(self, msg: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def open_output(self):
        # Abrimos la carpeta de barcodes si existe; si no, la raíz de salida
        target = self.last_barcodes_dir or self.last_output_dir
        if not target:
            return

        try:
            # Windows: abrir en Explorer
            os.startfile(str(target))  # type: ignore[attr-defined]
        except Exception:
            try:
                # Fallback (por si cambia el entorno)
                subprocess.run(["explorer", str(target)], check=False)
            except Exception as e:
                messagebox.showerror("No se pudo abrir la carpeta", str(e))

    def run(self):
        csv_p = self.csv_path.get().strip()
        out_d = self.out_dir.get().strip()

        if not csv_p:
            messagebox.showerror("Falta CSV", "Selecciona un archivo CSV.")
            return
        if not out_d:
            messagebox.showerror("Falta carpeta", "Selecciona una carpeta de salida.")
            return

        try:
            w = int(self.width_var.get())
            h = int(self.height_var.get())
            if w <= 0 or h <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Tamaño inválido", "El tamaño debe ser un número entero positivo.")
            return

        self.run_btn.configure(state="disabled")
        self.open_btn.configure(state="disabled")
        self.last_output_dir = None
        self.last_barcodes_dir = None

        self.status_var.set("Procesando…")
        self._append_log("== Iniciando generación ==")

        def task():
            try:
                result = generate_barcodes_from_csv(
                    csv_path=Path(csv_p),
                    outdir=Path(out_d),
                    width=w,
                    height=h,
                    overwrite=bool(self.overwrite_var.get()),
                    no_text=bool(self.no_text_var.get()),
                )
                self.after(0, lambda: self._on_success(result))
            except Exception as e:
                self.after(0, lambda: self._on_error(e))

        threading.Thread(target=task, daemon=True).start()

    def _on_success(self, result):
        self._append_log(f"Delimitador usado: {result.delimiter}")
        self._append_log(f"Generados: {result.generated}")

        # Guardar rutas para abrir carpeta
        self.last_output_dir = result.outdir
        self.last_barcodes_dir = getattr(result, "barcodes_dir", None)

        self._append_log(f"Salida: {result.outdir}")
        if getattr(result, "barcodes_dir", None):
            self._append_log(f"Barcodes: {result.barcodes_dir}")
        if getattr(result, "log_file", None):
            self._append_log(f"Log: {result.log_file}")
        if getattr(result, "errors_csv", None):
            self._append_log(f"Errors CSV: {result.errors_csv}")


        if result.errors:
            self._append_log(f"Errores: {len(result.errors)}")
            self._append_log("--- Detalle ---")
            for e in result.errors:
                self._append_log(f"L{e.line_no} | {e.clave} | {e.ean13} | {e.message}")
        else:
            self._append_log("Sin errores.")

        self.status_var.set("Listo.")
        self.run_btn.configure(state="normal")
        self.open_btn.configure(state="normal")

        messagebox.showinfo("Completado", f"Generados: {result.generated}\nErrores: {len(result.errors)}")

    def _on_error(self, e: Exception):
        self._append_log(f"[ERROR] {e}")
        self.status_var.set("Error.")
        self.run_btn.configure(state="normal")
        messagebox.showerror("Error", str(e))


def main():
    app = BarcodeApp()
    app.mainloop()
