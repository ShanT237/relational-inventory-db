"""Componente visual para mostrar resultados de consultas en una tabla."""
import tkinter as tk
from tkinter import ttk

from vistas import estilos as e


class TablaResultados:

    def __init__(self, contenedor):
        self.contenedor = contenedor
        self.tabla = None

    def mostrar(self, columnas, filas):
        for widget in self.contenedor.winfo_children():
            widget.destroy()

        marco = e.tarjeta(self.contenedor)
        marco.pack(fill="both", expand=True)
        zona = tk.Frame(marco, bg=e.TARJETA)
        zona.pack(fill="both", expand=True, padx=1, pady=1)
        zona.columnconfigure(0, weight=1)
        zona.rowconfigure(0, weight=1)

        claves = [f"c{i}" for i in range(len(columnas))]
        tabla = ttk.Treeview(zona, columns=claves, show="headings")
        for clave, titulo in zip(claves, columnas):
            tabla.heading(clave, text=titulo)
            tabla.column(clave, width=150, minwidth=90, stretch=True)
        for fila in filas:
            tabla.insert(
                "", "end",
                values=[self._texto(valor) for valor in fila],
            )

        barra_vertical = ttk.Scrollbar(zona, orient="vertical", command=tabla.yview)
        barra_horizontal = ttk.Scrollbar(zona, orient="horizontal", command=tabla.xview)
        tabla.configure(yscrollcommand=barra_vertical.set,
                        xscrollcommand=barra_horizontal.set)
        tabla.grid(row=0, column=0, sticky="nsew")
        barra_vertical.grid(row=0, column=1, sticky="ns")
        barra_horizontal.grid(row=1, column=0, sticky="ew")
        self.tabla = tabla

    @staticmethod
    def _texto(valor):
        if valor is None:
            return "—"
        if hasattr(valor, "strftime"):
            return valor.strftime("%Y-%m-%d %H:%M:%S")
        return str(valor).replace("\n", " ")
