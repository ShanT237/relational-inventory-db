"""Vista: CRUD de categorías (Tkinter). No contiene SQL."""
import tkinter as tk
from tkinter import messagebox, ttk

from dominio.excepciones.regla_dominio_error import ReglaDominioError


class CategoriasVista:

    def __init__(self, padre, categoria_controlador):
        self.padre = padre
        self.controlador = categoria_controlador
        self.id_seleccionado = None   # None = se está creando una categoría nueva

    def mostrar(self):
        ventana = tk.Toplevel(self.padre)
        ventana.title("Categorías")
        ventana.geometry("700x470")
        ventana.transient(self.padre)
        ventana.grab_set()

        # --- Formulario ---
        formulario = ttk.LabelFrame(ventana, text="Datos de la categoría", padding=12)
        formulario.pack(fill="x", padx=12, pady=(12, 6))

        ttk.Label(formulario, text="Nombre:").grid(row=0, column=0, sticky="e", pady=4)
        entrada_nombre = ttk.Entry(formulario, width=40)
        entrada_nombre.grid(row=0, column=1, padx=8, sticky="w")

        ttk.Label(formulario, text="Descripción:").grid(row=1, column=0, sticky="e", pady=4)
        entrada_descripcion = ttk.Entry(formulario, width=40)
        entrada_descripcion.grid(row=1, column=1, padx=8, sticky="w")

        activa = tk.BooleanVar(value=True)
        ttk.Checkbutton(formulario, text="Activa", variable=activa).grid(
            row=2, column=1, padx=8, sticky="w", pady=4)

        # --- Tabla ---
        marco_tabla = ttk.Frame(ventana)
        marco_tabla.pack(fill="both", expand=True, padx=12, pady=6)

        tabla = ttk.Treeview(marco_tabla,
                             columns=("id", "nombre", "descripcion", "estado"),
                             show="headings", selectmode="browse")
        tabla.heading("id", text="Id")
        tabla.heading("nombre", text="Nombre")
        tabla.heading("descripcion", text="Descripción")
        tabla.heading("estado", text="Estado")
        tabla.column("id", width=40, anchor="center")
        tabla.column("nombre", width=160)
        tabla.column("descripcion", width=330)
        tabla.column("estado", width=80, anchor="center")
        barra = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        # --- Acciones ---
        def cargar_tabla():
            tabla.delete(*tabla.get_children())
            try:
                for c in self.controlador.listar():
                    tabla.insert("", "end", iid=str(c.id_categoria), values=(
                        c.id_categoria, c.nombre, c.descripcion or "",
                        "Activa" if c.estado else "Inactiva"))
            except Exception as error:
                messagebox.showerror("Error", f"No se pudieron cargar las categorías:\n{error}",
                                     parent=ventana)

        def limpiar():
            self.id_seleccionado = None
            entrada_nombre.delete(0, tk.END)
            entrada_descripcion.delete(0, tk.END)
            activa.set(True)
            tabla.selection_remove(tabla.selection())
            entrada_nombre.focus()

        def al_seleccionar(_evento=None):
            seleccion = tabla.selection()
            if not seleccion:
                return
            id_categoria, nombre, descripcion, estado = tabla.item(seleccion[0], "values")
            self.id_seleccionado = int(id_categoria)
            entrada_nombre.delete(0, tk.END)
            entrada_nombre.insert(0, nombre)
            entrada_descripcion.delete(0, tk.END)
            entrada_descripcion.insert(0, descripcion)
            activa.set(estado == "Activa")

        def guardar():
            try:
                if self.id_seleccionado is None:
                    self.controlador.crear(entrada_nombre.get(), entrada_descripcion.get(),
                                           activa.get())
                else:
                    self.controlador.modificar(self.id_seleccionado, entrada_nombre.get(),
                                               entrada_descripcion.get(), activa.get())
            except ReglaDominioError as error:
                messagebox.showwarning("Categorías", str(error), parent=ventana)
                return
            except Exception as error:
                messagebox.showerror("Error", f"No se pudo guardar:\n{error}", parent=ventana)
                return
            cargar_tabla()
            limpiar()

        def eliminar():
            if self.id_seleccionado is None:
                messagebox.showinfo("Categorías", "Selecciona una categoría de la tabla.",
                                    parent=ventana)
                return
            if not messagebox.askyesno("Eliminar", "¿Eliminar la categoría seleccionada?",
                                       parent=ventana):
                return
            try:
                self.controlador.eliminar(self.id_seleccionado)
            except ReglaDominioError as error:
                messagebox.showwarning("Categorías", str(error), parent=ventana)
                return
            except Exception as error:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{error}", parent=ventana)
                return
            cargar_tabla()
            limpiar()

        botones = ttk.Frame(ventana)
        botones.pack(pady=(0, 12))
        ttk.Button(botones, text="Nuevo", command=limpiar).pack(side="left", padx=4)
        ttk.Button(botones, text="Guardar", command=guardar).pack(side="left", padx=4)
        ttk.Button(botones, text="Eliminar", command=eliminar).pack(side="left", padx=4)
        ttk.Button(botones, text="Cerrar", command=ventana.destroy).pack(side="left", padx=4)

        tabla.bind("<<TreeviewSelect>>", al_seleccionar)
        cargar_tabla()
        entrada_nombre.focus()