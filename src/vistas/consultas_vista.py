"""Vista genérica: ejecuta una consulta y muestra sus filas en una tabla."""
from tkinter import messagebox, ttk

from vistas.tabla_resultados import TablaResultados


class ConsultasVista:

    def __init__(self, controlador, identificador, titulo):
        self.controlador = controlador
        self.identificador = identificador
        self.titulo = titulo

    def construir(self, contenedor):
        ttk.Label(contenedor, text=self.titulo, style="Pagina.TLabel").pack(anchor="w")
        ttk.Label(
            contenedor,
            text="Resultados de solo lectura disponibles para todos los roles.",
            style="Suave.TLabel",
        ).pack(anchor="w", pady=(4, 12))
        tabla_contenedor = ttk.Frame(contenedor)
        tabla_contenedor.pack(fill="both", expand=True)
        try:
            columnas, filas = self.controlador.ejecutar(self.identificador)
        except Exception as error:
            messagebox.showerror(
                "Consulta", f"No se pudo ejecutar la consulta:\n{error}",
                parent=contenedor.winfo_toplevel(),
            )
            return
        TablaResultados(tabla_contenedor).mostrar(columnas, filas)
        ttk.Label(
            contenedor, text=f"{len(filas)} registros", style="Suave.TLabel"
        ).pack(anchor="e", pady=(6, 0))
