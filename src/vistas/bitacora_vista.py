"""Vista administrativa con filtros para el historial de sesiones."""
import tkinter as tk
from tkinter import messagebox, ttk

from dominio.excepciones.regla_dominio_error import ReglaDominioError
from vistas.tabla_resultados import TablaResultados


class BitacoraVista:

    def __init__(self, controlador):
        self.controlador = controlador

    def construir(self, contenedor):
        ttk.Label(
            contenedor, text="Bitácora de entrada y salida", style="Pagina.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            contenedor,
            text="Las sesiones sin hora de salida aparecen como «Sesión abierta». "
                 "Las fechas usan el formato AAAA-MM-DD.",
            style="Suave.TLabel",
        ).pack(anchor="w", pady=(4, 12))

        filtros = ttk.Frame(contenedor)
        filtros.pack(fill="x", pady=(0, 12))
        ttk.Label(filtros, text="Usuario").pack(side="left")
        self.var_usuario = tk.StringVar(value="Todos")
        try:
            usuarios = self.controlador.listar_usuarios()
        except Exception as error:
            messagebox.showerror(
                "Bitácora", f"No se pudieron cargar los usuarios:\n{error}",
                parent=contenedor.winfo_toplevel(),
            )
            usuarios = []
        ttk.Combobox(
            filtros, textvariable=self.var_usuario, state="readonly",
            values=["Todos", *usuarios], width=22,
        ).pack(side="left", padx=(8, 18))

        ttk.Label(filtros, text="Desde").pack(side="left")
        self.var_desde = tk.StringVar()
        ttk.Entry(filtros, textvariable=self.var_desde, width=13).pack(
            side="left", padx=(8, 18))
        ttk.Label(filtros, text="Hasta").pack(side="left")
        self.var_hasta = tk.StringVar()
        ttk.Entry(filtros, textvariable=self.var_hasta, width=13).pack(
            side="left", padx=(8, 18))
        ttk.Button(filtros, text="Filtrar", command=self._filtrar).pack(side="left")

        self.tabla_contenedor = ttk.Frame(contenedor)
        self.tabla_contenedor.pack(fill="both", expand=True)
        self._filtrar()

    def _filtrar(self):
        nombre_usuario = self.var_usuario.get()
        if nombre_usuario == "Todos":
            nombre_usuario = None
        try:
            registros = self.controlador.listar(
                nombre_usuario, self.var_desde.get().strip(), self.var_hasta.get().strip())
        except ReglaDominioError as error:
            for widget in self.tabla_contenedor.winfo_children():
                widget.destroy()
            messagebox.showwarning(
                "Filtros de bitácora", str(error),
                parent=self.tabla_contenedor.winfo_toplevel(),
            )
            return
        except Exception as error:
            messagebox.showerror(
                "Bitácora", f"No se pudo cargar el historial:\n{error}",
                parent=self.tabla_contenedor.winfo_toplevel(),
            )
            return

        columnas = ["Usuario", "Nombre", "Rol", "Entrada", "Salida"]
        filas = [
            (fila["nombre_usuario"], fila["usuario"], fila["rol"],
             fila["entrada"], fila["salida"] or "Sesión abierta")
            for fila in registros
        ]
        TablaResultados(self.tabla_contenedor).mostrar(columnas, filas)
